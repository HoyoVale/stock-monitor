"""历史回测服务。

基于历史日K线，在每个交易日滚动计算技术指标，应用多因子加权评分引擎，
模拟买入/卖出决策，计算收益率、胜率、最大回撤、夏普比率等回测指标。
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy import select

from app.database import async_session
from app.models.stock import DailyBar
from app.services.indicator_service import IndicatorService

logger = logging.getLogger(__name__)

INDICATOR_WEIGHTS = {
    "MACD": 30, "RSI": 20, "KDJ": 20, "BOLL": 15, "MA_ARRANGE": 15,
}

SIGNAL_TO_SCORE = {
    "golden_cross": 1.0, "dead_cross": 0.0,
    "oversold": 1.0, "overbought": 0.0,
    "price_above_upper": 0.0, "price_below_lower": 1.0,
    "price_in_band": 0.5,
    "bullish": 1.0, "bearish": 0.0, "neutral": 0.5,
}


class BacktestService:
    """回测引擎。"""

    def __init__(self):
        self.indicator = IndicatorService()

    async def run(self, code: str, start: str, end: str, threshold: float = 60.0) -> dict:
        """执行回测。

        Args:
            code: 股票代码
            start: 开始日期 (YYYY-MM-DD)
            end: 结束日期 (YYYY-MM-DD)
            threshold: 买入信号阈值 (0-100)

        Returns:
            {
                "stock_code", "start_date", "end_date",
                "total_return": float, "annualized_return": float,
                "win_rate": float, "max_drawdown": float, "sharpe_ratio": float,
                "total_trades": int, "winning_trades": int, "losing_trades": int,
                "equity_curve": [{"date": str, "value": float}, ...],
                "daily_signals": [{"date": str, "score": float, "action": str}, ...],
            }
        """
        # 1. 读取日K数据
        async with async_session() as db:
            result = await db.execute(
                select(DailyBar)
                .where(DailyBar.code == code)
                .where(DailyBar.date >= date.fromisoformat(start))
                .where(DailyBar.date <= date.fromisoformat(end))
                .order_by(DailyBar.date)
            )
            bars = result.scalars().all()

        if len(bars) < 60:
            return {"error": f"数据不足: 需要至少 60 个交易日，当前 {len(bars)}"}

        # 2. 构造 DataFrame
        dates = [b.date for b in bars]
        closes = [b.close for b in bars]
        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        volumes = [b.volume or 0 for b in bars]

        # 3. 滚动窗口计算 (最小 60 根, 每 20 根算一次)
        window = 60
        step = 1  # 每个交易日都评估
        start_idx = window

        daily_scores = []
        daily_actions = []
        equity = []
        cash = 100000.0  # 初始资金 10 万
        shares = 0
        initial_price = closes[start_idx]

        for i in range(start_idx, len(bars)):
            window_closes = closes[max(0, i - window):i + 1]
            window_highs = highs[max(0, i - window):i + 1]
            window_lows = lows[max(0, i - window):i + 1]

            score = self._score_window(window_closes, window_highs, window_lows)
            daily_scores.append(score)

            current_price = closes[i]

            action = "hold"
            if score >= threshold and shares == 0:
                # 买入: 全仓
                if cash > 0 and current_price > 0:
                    shares = cash / current_price
                    cash = 0
                    action = "buy"
            elif score < threshold and shares > 0:
                # 卖出: 清仓
                cash = shares * current_price
                shares = 0
                action = "sell"

            daily_actions.append(action)

            # 权益 = 现金 + 持仓市值
            equity_value = cash + (shares * current_price)
            equity.append({"date": dates[i].isoformat(), "value": round(equity_value, 2)})

        # 4 计算回测指标
        equity_values = [e["value"] for e in equity]
        initial_equity = 100000.0
        final_equity = equity_values[-1] if equity_values else initial_equity
        total_return = (final_equity - initial_equity) / initial_equity * 100

        # 年化收益率
        trading_days = len(equity_values)
        years = trading_days / 252.0 if trading_days > 0 else 1
        annualized_return = ((final_equity / initial_equity) ** (1 / years) - 1) * 100 if years > 0 else 0

        # 日收益率
        daily_returns = []
        for j in range(1, len(equity_values)):
            ret = (equity_values[j] - equity_values[j - 1]) / equity_values[j - 1]
            daily_returns.append(ret)

        # 胜率
        trades = []  # 每笔交易收益率
        in_trade = False
        entry_price = 0
        for j in range(start_idx, len(bars)):
            idx = j - start_idx
            if idx >= len(daily_actions):
                break
            action = daily_actions[idx]
            if action == "buy":
                entry_price = closes[j]
                in_trade = True
            elif action == "sell" and in_trade and entry_price > 0:
                trade_return = (closes[j] - entry_price) / entry_price * 100
                trades.append(trade_return)
                in_trade = False

        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t > 0)
        losing_trades = sum(1 for t in trades if t < 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # 最大回撤
        peak = equity_values[0]
        max_dd = 0.0
        for v in equity_values[1:]:
            if v > peak:
                peak = v
            dd = (peak - v) / peak * 100
            if dd > max_dd:
                max_dd = dd

        # 夏普比率
        sharpe = 0.0
        if len(daily_returns) > 1 and np.std(daily_returns) > 0:
            avg_ret = np.mean(daily_returns)
            std_ret = np.std(daily_returns)
            sharpe = round((avg_ret / std_ret) * np.sqrt(252), 2)

        # 构造信号输出
        signals = []
        for j in range(start_idx, len(bars)):
            idx = j - start_idx
            if idx < len(daily_scores) and idx < len(daily_actions):
                signals.append({
                    "date": dates[j].isoformat(),
                    "score": round(daily_scores[idx], 1),
                    "action": daily_actions[idx],
                    "price": closes[j],
                })

        return {
            "stock_code": code,
            "start_date": start,
            "end_date": end,
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "win_rate": round(win_rate, 2),
            "max_drawdown": round(max_dd, 2),
            "sharpe_ratio": sharpe,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "equity_curve": equity,
            "daily_signals": signals,
        }

    def _score_window(self, closes: list, highs: list, lows: list) -> float:
        """对滑动窗口计算加权评分 (0-100)。

        使用与 suggestion_service 相同的指标和权重。
        不进行数据库缓存——回测是离线计算。
        """
        try:
            close_s = pd.Series(closes, dtype=float).dropna()
            high_s = pd.Series(highs, dtype=float).dropna()
            low_s = pd.Series(lows, dtype=float).dropna()

            if len(close_s) < 26:
                return 50

            # MACD
            macd = self.indicator.calc_macd(close_s)
            macd_signal = macd.get("cross_signal", "neutral")
            macd_score = SIGNAL_TO_SCORE.get(macd_signal, 0.5)

            # RSI
            rsi = self.indicator.calc_rsi(close_s, 14)
            rsi_signal = rsi.get("signal", "neutral")
            rsi_score = SIGNAL_TO_SCORE.get(rsi_signal, 0.5)

            # KDJ
            kdj = self.indicator.calc_kdj(high_s, low_s, close_s, 9)
            kdj_signal = kdj.get("cross_signal", "neutral")
            kdj_score = SIGNAL_TO_SCORE.get(kdj_signal, 0.5)

            # BOLL
            boll = self.indicator.calc_boll(close_s, 20, 2)
            boll_signal = boll.get("signal", "neutral")
            boll_score = SIGNAL_TO_SCORE.get(boll_signal, 0.5)

            # MA 排列
            ma_arrange = self._detect_ma_arrange(close_s)
            ma_score = SIGNAL_TO_SCORE.get(ma_arrange, 0.5)

            total_weight = sum(INDICATOR_WEIGHTS.values())
            weighted = (
                INDICATOR_WEIGHTS["MACD"] * macd_score
                + INDICATOR_WEIGHTS["RSI"] * rsi_score
                + INDICATOR_WEIGHTS["KDJ"] * kdj_score
                + INDICATOR_WEIGHTS["BOLL"] * boll_score
                + INDICATOR_WEIGHTS["MA_ARRANGE"] * ma_score
            )
            return (weighted / total_weight) * 100 if total_weight > 0 else 50

        except Exception as e:
            logger.debug(f"评分计算异常: {e}")
            return 50

    @staticmethod
    def _detect_ma_arrange(close: pd.Series) -> str:
        """检测均线排列。"""
        s = pd.to_numeric(close, errors="coerce").dropna()
        if len(s) < 60:
            return "neutral"
        ma5 = s.rolling(5).mean().iloc[-1]
        ma10 = s.rolling(10).mean().iloc[-1]
        ma20 = s.rolling(20).mean().iloc[-1]
        ma60 = s.rolling(60).mean().iloc[-1]
        if all(v > 0 for v in (ma5, ma10, ma20, ma60)):
            if ma5 > ma10 > ma20 > ma60:
                return "bullish"
            if ma5 < ma10 < ma20 < ma60:
                return "bearish"
        return "neutral"


# 单例
backtest_service = BacktestService()
