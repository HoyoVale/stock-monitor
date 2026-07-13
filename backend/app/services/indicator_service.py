"""技术指标计算服务。

使用 pandas-ta 库计算 MACD、RSI、KDJ、Bollinger Bands、均线等指标。
计算结果缓存到 IndicatorCache 表中，加速重复查询。
"""

import asyncio
import logging
from datetime import date
from typing import Optional

import pandas as pd
import pandas_ta as ta
from sqlalchemy import select, delete as sa_delete, func
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.database import async_session
from app.models.indicator import IndicatorCache
from app.models.stock import DailyBar, Stock

logger = logging.getLogger(__name__)


class IndicatorService:
    """技术指标计算器。"""

    async def _run_in_executor(self, func, *args, **kwargs):
        """在线程池中运行同步的 pandas-ta 运算，避免阻塞事件循环。"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    # ------------------------------------------------------------------
    # 基础计算
    # ------------------------------------------------------------------

    def _to_series(self, close: pd.Series) -> pd.Series:
        """确保输入是 float Series，处理缺失值。"""
        return pd.to_numeric(close, errors="coerce").dropna()

    def _detect_cross(self, a: pd.Series, b: pd.Series) -> str:
        """检测序列 a 与序列 b 的最新交叉方向。

        返回 "golden_cross"（a 上穿 b）、"dead_cross"（a 下穿 b）或 "neutral"。
        """
        if len(a) < 2 or len(b) < 2:
            return "neutral"
        # 上穿: 前一根 a <= b, 当前 a > b
        if a.iloc[-2] <= b.iloc[-2] and a.iloc[-1] > b.iloc[-1]:
            return "golden_cross"
        # 下穿: 前一根 a >= b, 当前 a < b
        if a.iloc[-2] >= b.iloc[-2] and a.iloc[-1] < b.iloc[-1]:
            return "dead_cross"
        return "neutral"

    # ------------------------------------------------------------------
    # 指标计算 (同步方法)
    # ------------------------------------------------------------------

    def calc_macd(self, close: pd.Series, fast: int = 12, slow: int = 26,
                  signal: int = 9) -> dict:
        """计算 MACD 指标。

        Returns:
            dif: DIF 值序列
            dea: DEA (信号线) 序列
            histogram: MACD 柱序列
            signal: 最新交叉信号 "golden_cross"|"dead_cross"|"neutral"
            latest: {dif, dea, histogram} 最新值
        """
        s = self._to_series(close)
        if len(s) < slow + signal:
            return self._empty_indicator_result("macd")

        macd = ta.macd(s, fast=fast, slow=slow, signal=signal)
        if macd is None:
            return self._empty_indicator_result("macd")
        # pandas-ta 0.3.x 列名是 MACD_12_26_9 / MACDs_12_26_9 / MACDh_12_26_9
        col_dif = f"MACD_{fast}_{slow}_{signal}"
        col_sig = f"MACDs_{fast}_{slow}_{signal}"
        col_hist = f"MACDh_{fast}_{slow}_{signal}"

        dif = macd.get(col_dif, pd.Series(dtype=float))
        dea = macd.get(col_sig, pd.Series(dtype=float))
        hist = macd.get(col_hist, pd.Series(dtype=float))

        cross = self._detect_cross(dif, dea)

        def _last_or_none(s): return None if s.empty or pd.isna(s.iloc[-1]) else float(round(s.iloc[-1], 4))

        return {
            "dif": dif.tolist(),
            "dea": dea.tolist(),
            "histogram": hist.tolist(),
            "cross_signal": cross,
            "latest": {
                "dif": _last_or_none(dif),
                "dea": _last_or_none(dea),
                "histogram": _last_or_none(hist),
            },
        }

    def calc_rsi(self, close: pd.Series, period: int = 14) -> dict:
        """计算 RSI 指标。

        Returns:
            value: RSI 值序列
            latest: 最新 RSI 值
            signal: "oversold" (RSI<30) | "overbought" (RSI>70) | "neutral"
        """
        s = self._to_series(close)
        if len(s) < period:
            return {"value": [], "latest": None,
                    "signal": "neutral"}

        rsi = ta.rsi(s, length=period)
        if rsi is None:
            return {"value": [], "latest": None,
                    "signal": "neutral"}

        latest_val = None if rsi.empty or pd.isna(rsi.iloc[-1]) else float(round(rsi.iloc[-1], 2))
        if latest_val is None:
            sig = "neutral"
        elif latest_val < 30:
            sig = "oversold"
        elif latest_val > 70:
            sig = "overbought"
        else:
            sig = "neutral"

        return {"value": rsi.tolist(), "latest": latest_val,
                "signal": sig}

    def calc_kdj(self, high: pd.Series, low: pd.Series, close: pd.Series,
                 period: int = 9) -> dict:
        """计算 KDJ 指标。

        Returns:
            k, d, j: K/D/J 值序列
            cross_signal: K 与 D 交叉方向
            latest: {k, d, j} 最新值
        """
        h = self._to_series(high)
        l = self._to_series(low)
        c = self._to_series(close)
        if len(c) < period:
            return self._empty_indicator_result("kdj")

        # 计算 RSV
        lowest_low = l.rolling(window=period).min()
        highest_high = h.rolling(window=period).max()
        rsv = ((c - lowest_low) / (highest_high - lowest_low).replace(0, pd.NA)) * 100

        # 手动递推 K/D/J
        k = pd.Series(50.0, index=rsv.index)
        d = pd.Series(50.0, index=rsv.index)
        for i in range(period, len(rsv)):
            if pd.isna(rsv.iloc[i]):
                k.iloc[i] = k.iloc[i - 1]
                d.iloc[i] = d.iloc[i - 1]
            else:
                k.iloc[i] = 2 / 3 * k.iloc[i - 1] + 1 / 3 * rsv.iloc[i]
                d.iloc[i] = 2 / 3 * d.iloc[i - 1] + 1 / 3 * k.iloc[i]
        j = 3 * k - 2 * d

        cross = self._detect_cross(k, d)

        def _last_or_none(s): return None if s.empty or pd.isna(s.iloc[-1]) else float(round(s.iloc[-1], 2))

        return {
            "k": k.tolist(),
            "d": d.tolist(),
            "j": j.tolist(),
            "cross_signal": cross,
            "latest": {
                "k": _last_or_none(k),
                "d": _last_or_none(d),
                "j": _last_or_none(j),
            },
        }

    def calc_boll(self, close: pd.Series, period: int = 20, std: int = 2) -> dict:
        """计算 Bollinger Bands。

        Returns:
            upper, middle, lower: 上/中/下轨序列
            signal: 价格相对布林带位置
            latest: {upper, middle, lower} 最新值
        """
        s = self._to_series(close)
        if len(s) < period:
            return self._empty_indicator_result("boll")

        bbands = ta.bbands(s, length=period, std=std)
        if bbands is None:
            return self._empty_indicator_result("boll")
        # pandas-ta 列名: BBL_20_2.0 / BBM_20_2.0 / BBU_20_2.0
        col_lower = f"BBL_{period}_{float(std)}"
        col_mid = f"BBM_{period}_{float(std)}"
        col_upper = f"BBU_{period}_{float(std)}"

        upper = bbands.get(col_upper, pd.Series(dtype=float))
        middle = bbands.get(col_mid, pd.Series(dtype=float))
        lower = bbands.get(col_lower, pd.Series(dtype=float))

        # 判断价格位置
        if s.iloc[-1] >= upper.iloc[-1] if not upper.empty and not pd.isna(upper.iloc[-1]) else False:
            sig = "price_above_upper"
        elif s.iloc[-1] <= lower.iloc[-1] if not lower.empty and not pd.isna(lower.iloc[-1]) else False:
            sig = "price_below_lower"
        else:
            sig = "price_in_band"

        def _last_or_none(s): return None if s.empty or pd.isna(s.iloc[-1]) else float(round(s.iloc[-1], 4))

        return {
            "upper": upper.tolist(),
            "middle": middle.tolist(),
            "lower": lower.tolist(),
            "signal": sig,
            "latest": {
                "upper": _last_or_none(upper),
                "middle": _last_or_none(middle),
                "lower": _last_or_none(lower),
            },
        }

    def calc_sma(self, close: pd.Series, periods: list[int] = None) -> dict:
        """计算简单移动均线。

        Returns:
            {f"sma_{p}": [...] for p in periods}
        """
        if periods is None:
            periods = [5, 10, 20, 60]
        s = self._to_series(close)
        result = {}
        for p in periods:
            sma = s.rolling(window=p).mean()
            result[f"sma_{p}"] = sma.tolist()
        return result

    def calc_ema(self, close: pd.Series, periods: list[int] = None) -> dict:
        """计算指数移动均线。"""
        if periods is None:
            periods = [12, 26]
        s = self._to_series(close)
        result = {}
        for p in periods:
            ema = ta.ema(s, length=p)
            if ema is not None:
                result[f"ema_{p}"] = ema.tolist()
            else:
                result[f"ema_{p}"] = []
        return result

    def calc_volume_ma(self, volume: pd.Series, period: int = 20) -> list:
        """计算成交量移动均线。"""
        s = self._to_series(volume)
        if len(s) < period:
            return []
        vma = s.rolling(window=period).mean()
        return vma.tolist()

    # ------------------------------------------------------------------
    # 缓存查询
    # ------------------------------------------------------------------

    async def _get_cached_indicators(self, code: str) -> Optional[dict]:
        """从 IndicatorCache 表读取已缓存的指标结果。

        缓存有效性判断: 缓存行数与 daily_bars 行数一致则视为有效。
        不一致说明有新数据到达，需要重新计算。
        """
        async with async_session() as db:
            # 比较缓存行数与K线行数
            bar_count_result = await db.execute(
                select(func.count(DailyBar.id)).where(DailyBar.code == code)
            )
            bar_count = bar_count_result.scalar()
            if not bar_count:
                return None

            cache_count_result = await db.execute(
                select(func.count(IndicatorCache.id)).where(IndicatorCache.stock_code == code)
            )
            cache_count = cache_count_result.scalar()
            if cache_count != bar_count:
                return None

            # 从缓存中读取并重建返回值
            result = await db.execute(
                select(IndicatorCache)
                .where(IndicatorCache.stock_code == code)
                .order_by(IndicatorCache.date)
            )
            rows = result.scalars().all()
            if not rows:
                return None

            dates = [r.date for r in rows]
            n = len(rows)

            def _col(getter):
                return [getter(r) for r in rows]

            dif = _col(lambda r: r.macd_dif)
            dea = _col(lambda r: r.macd_dea)
            hist = _col(lambda r: r.macd_hist)
            rsi_vals = _col(lambda r: r.rsi_14)
            k_vals = _col(lambda r: r.kdj_k)
            d_vals = _col(lambda r: r.kdj_d)
            j_vals = _col(lambda r: r.kdj_j)
            upper_vals = _col(lambda r: r.boll_upper)
            middle_vals = _col(lambda r: r.boll_middle)
            lower_vals = _col(lambda r: r.boll_lower)
            sma5 = _col(lambda r: r.ma_5)
            sma10 = _col(lambda r: r.ma_10)
            sma20 = _col(lambda r: r.ma_20)
            sma60 = _col(lambda r: r.ma_60)
            vol_ma = _col(lambda r: r.volume_ma_20)

            logger.info(f"指标缓存命中: {code}, {n} 行")

            return {
                "code": code,
                "date": [d.isoformat() for d in dates],
                "bars_count": n,
                "cached": True,
                "macd": {
                    "dif": dif,
                    "dea": dea,
                    "histogram": hist,
                    "cross_signal": self._detect_cross_from_lists(dif, dea),
                    "latest": {"dif": dif[-1], "dea": dea[-1], "histogram": hist[-1]},
                },
                "rsi_14": {
                    "value": rsi_vals,
                    "latest": rsi_vals[-1],
                    "signal": self._rsi_signal(rsi_vals[-1]),
                },
                "kdj": {
                    "k": k_vals, "d": d_vals, "j": j_vals,
                    "cross_signal": self._detect_cross_from_lists(k_vals, d_vals),
                    "latest": {"k": k_vals[-1], "d": d_vals[-1], "j": j_vals[-1]},
                },
                "boll": {
                    "upper": upper_vals, "middle": middle_vals, "lower": lower_vals,
                    "signal": "price_in_band",
                    "latest": {"upper": upper_vals[-1], "middle": middle_vals[-1], "lower": lower_vals[-1]},
                },
                "sma": {"sma_5": sma5, "sma_10": sma10, "sma_20": sma20, "sma_60": sma60},
                "ema": {},
                "volume_ma_20": vol_ma,
            }

    @staticmethod
    def _detect_cross_from_lists(a: list, b: list) -> str:
        """从列表中检测交叉信号。"""
        if len(a) < 2 or len(b) < 2:
            return "neutral"
        a_prev, a_cur = a[-2], a[-1]
        b_prev, b_cur = b[-2], b[-1]
        if a_prev is None or a_cur is None or b_prev is None or b_cur is None:
            return "neutral"
        if a_prev <= b_prev and a_cur > b_cur:
            return "golden_cross"
        if a_prev >= b_prev and a_cur < b_cur:
            return "dead_cross"
        return "neutral"

    @staticmethod
    def _rsi_signal(val: Optional[float]) -> str:
        if val is None:
            return "neutral"
        if val < 30:
            return "oversold"
        if val > 70:
            return "overbought"
        return "neutral"

    # ------------------------------------------------------------------
    # 综合计算 (异步)
    # ------------------------------------------------------------------

    async def calc_all_indicators(self, code: str, force_refresh: bool = False) -> dict:
        """计算一只股票的全部技术指标。

        流程: 1) 检查缓存 → 2) 若未命中则读取 daily_bars → 3) 逐项计算 → 4) 写入 indicator_cache → 5) 返回汇总。

        Returns:
            {
                "code": str,
                "date": [str, ...],
                "bars_count": int,
                "macd": {...},
                "rsi_14": {...},
                "kdj": {...},
                "boll": {...},
                "sma": {...},
                "ema": {...},
                "volume_ma_20": [...],
            }
        """
        # 1. 先查缓存
        if not force_refresh:
            cached = await self._get_cached_indicators(code)
            if cached:
                return cached

        logger.info(f"指标缓存未命中: {code}，重新计算")

        # 2. 读取K线数据
        async with async_session() as db:
            result = await db.execute(
                select(DailyBar).where(DailyBar.code == code).order_by(DailyBar.date)
            )
            bars = result.scalars().all()

        if not bars:
            return {"code": code, "date": [], "bars_count": 0}

        # 3. 构造 DataFrame
        dates = [b.date for b in bars]
        close = pd.Series([b.close for b in bars], index=dates)
        high = pd.Series([b.high for b in bars], index=dates)
        low = pd.Series([b.low for b in bars], index=dates)
        volume = pd.Series([b.volume or 0 for b in bars], index=dates)

        # 4. 在线程池中并行计算（四个指标可以一起算）
        macd_fut = self._run_in_executor(self.calc_macd, close)
        rsi_fut = self._run_in_executor(self.calc_rsi, close, 14)
        kdj_fut = self._run_in_executor(self.calc_kdj, high, low, close, 9)
        boll_fut = self._run_in_executor(self.calc_boll, close, 20, 2)
        sma_fut = self._run_in_executor(self.calc_sma, close)
        ema_fut = self._run_in_executor(self.calc_ema, close)
        vol_fut = self._run_in_executor(self.calc_volume_ma, volume, 20)

        macd_r, rsi_r, kdj_r, boll_r, sma_r, ema_r, vol_r = await asyncio.gather(
            macd_fut, rsi_fut, kdj_fut, boll_fut, sma_fut, ema_fut, vol_fut
        )

        # 5. 写入缓存
        await self._cache_indicators(code, bars, macd_r, rsi_r, kdj_r, boll_r, sma_r, vol_r)

        return {
            "code": code,
            "date": [d.isoformat() for d in dates],
            "bars_count": len(bars),
            "cached": False,
            "macd": macd_r,
            "rsi_14": rsi_r,
            "kdj": kdj_r,
            "boll": boll_r,
            "sma": sma_r,
            "ema": ema_r,
            "volume_ma_20": vol_r,
        }

    async def _cache_indicators(self, code: str, bars, macd_r, rsi_r, kdj_r,
                                 boll_r, sma_r, vol_r):
        """将指标计算结果写入 IndicatorCache 表。"""
        if not bars:
            return
        # 提取最新值用于缓存（每行一条）
        dif_list = macd_r.get("dif", [])
        dea_list = macd_r.get("dea", [])
        hist_list = macd_r.get("histogram", [])
        rsi_list = rsi_r.get("value", [])
        k_list = kdj_r.get("k", [])
        d_list = kdj_r.get("d", [])
        j_list = kdj_r.get("j", [])
        upper_list = boll_r.get("upper", [])
        middle_list = boll_r.get("middle", [])
        lower_list = boll_r.get("lower", [])
        sma5_list = sma_r.get("sma_5", [])
        sma10_list = sma_r.get("sma_10", [])
        sma20_list = sma_r.get("sma_20", [])
        sma60_list = sma_r.get("sma_60", [])
        vol_ma_list = vol_r if isinstance(vol_r, list) else []

        def _get(lst, idx):
            if idx < len(lst) and lst[idx] is not None and not (isinstance(lst[idx], float) and pd.isna(lst[idx])):
                return lst[idx]
            return None

        async with async_session() as db:
            # 先删除旧缓存
            await db.execute(
                sa_delete(IndicatorCache).where(IndicatorCache.stock_code == code)
            )
            await db.flush()

            for i, bar in enumerate(bars):
                row = IndicatorCache(
                    stock_code=code,
                    date=bar.date,
                    macd_dif=_get(dif_list, i),
                    macd_dea=_get(dea_list, i),
                    macd_hist=_get(hist_list, i),
                    rsi_14=_get(rsi_list, i),
                    kdj_k=_get(k_list, i),
                    kdj_d=_get(d_list, i),
                    kdj_j=_get(j_list, i),
                    boll_upper=_get(upper_list, i),
                    boll_middle=_get(middle_list, i),
                    boll_lower=_get(lower_list, i),
                    ma_5=_get(sma5_list, i),
                    ma_10=_get(sma10_list, i),
                    ma_20=_get(sma20_list, i),
                    ma_60=_get(sma60_list, i),
                    volume_ma_20=_get(vol_ma_list, i),
                )
                db.add(row)
            await db.commit()

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def _empty_indicator_result(self, kind: str) -> dict:
        """返回空指标结果。"""
        if kind in ("macd",):
            return {
                "dif": [], "dea": [], "histogram": [],
                "cross_signal": "neutral",
                "latest": {"dif": None, "dea": None, "histogram": None},
            }
        if kind in ("kdj",):
            return {
                "k": [], "d": [], "j": [],
                "cross_signal": "neutral",
                "latest": {"k": None, "d": None, "j": None},
            }
        if kind in ("boll",):
            return {
                "upper": [], "middle": [], "lower": [],
                "signal": "neutral",
                "latest": {"upper": None, "middle": None, "lower": None},
            }
        return {}


# 单例
indicator_service = IndicatorService()
