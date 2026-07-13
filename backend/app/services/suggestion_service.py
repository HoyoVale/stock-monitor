import asyncio
import logging
from datetime import datetime

from app.database import async_session
from app.services.indicator_service import IndicatorService

logger = logging.getLogger(__name__)

INDICATOR_WEIGHTS = {
    "MACD": 30,
    "RSI": 20,
    "KDJ": 20,
    "BOLL": 15,
    "MA_ARRANGE": 15,
}

SIGNAL_TO_JUDGMENT = {
    "golden_cross": "买入",
    "dead_cross": "卖出",
    "oversold": "买入",
    "overbought": "卖出",
    "price_above_upper": "卖出",
    "price_below_lower": "买入",
    "price_in_band": "观望",
    "bullish": "买入",
    "bearish": "卖出",
    "neutral": "观望",
}

SIGNAL_TO_WEIGHT = {
    "golden_cross": 1.0,
    "dead_cross": 0.0,
    "oversold": 1.0,
    "overbought": 0.0,
    "price_above_upper": 0.0,
    "price_below_lower": 1.0,
    "price_in_band": 0.5,
    "bullish": 1.0,
    "bearish": 0.0,
    "neutral": 0.5,
}

RATING_THRESHOLDS = [
    (80, "★★★★★", "强烈买入", "积极买入"),
    (60, "★★★★☆", "买入", "适当建仓或加仓"),
    (40, "★★★☆☆", "观望", "持有不动，等待信号"),
    (20, "★★☆☆☆", "卖出", "减仓，控制风险"),
    (0, "★☆☆☆☆", "强烈卖出", "清仓或做空"),
]


class SuggestionService:
    def __init__(self):
        self.indicator_service = IndicatorService()

    async def analyze(self, stock_code: str, stock_name: str) -> dict:
        raw = await self.indicator_service.calc_all_indicators(stock_code)
        if not raw or raw.get("bars_count", 0) == 0:
            return self._empty_result(stock_code, stock_name)

        indicators = self._normalize_indicators(raw)

        indicator_results = []
        total_weight = 0
        weighted_score = 0

        for ind in indicators:
            name = ind["name"]
            weight = INDICATOR_WEIGHTS.get(name, 0)
            signal = ind.get("signal", "neutral")
            judgment = SIGNAL_TO_JUDGMENT.get(signal, "观望")
            sw = SIGNAL_TO_WEIGHT.get(signal, 0.5)

            indicator_results.append({
                "name": name,
                "weight": weight,
                "raw_value": ind.get("values", {}),
                "signal": signal,
                "judgment": judgment,
                "score_contribution": weight * sw,
                "explanation": self._build_explanation(name, ind, signal),
            })

            total_weight += weight
            weighted_score += weight * sw

        overall_score = round((weighted_score / total_weight) * 100, 1) if total_weight > 0 else 0
        rating = self._get_rating(overall_score)

        now = datetime.now().isoformat()
        trend = self._determine_trend(indicator_results)

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "overall_score": overall_score,
            "rating": rating["stars"],
            "rating_label": rating["label"],
            "rating_advice": rating["advice"],
            "trend": trend,
            "summary": self._build_summary(overall_score, rating, trend),
            "data_source": {
                "realtime": "akshare: stock_zh_a_spot()",
                "kline": "akshare: stock_zh_a_hist() (近120交易日)",
                "indicators": "pandas-ta via IndicatorService",
                "generated_at": now,
            },
            "indicators": indicator_results,
            "risk_tips": self._build_risk_tips(indicator_results, indicators),
            "position_suggestion": self._position_suggestion(overall_score),
            "timestamp": now,
        }

    def _normalize_indicators(self, raw: dict) -> list:
        result = []
        if "macd" in raw and raw["macd"]:
            m = raw["macd"]
            result.append({"name": "MACD", "signal": m.get("signal", "neutral"),
                "values": {"dif": m.get("latest", {}).get("dif", 0), "dea": m.get("latest", {}).get("dea", 0), "hist": m.get("latest", {}).get("histogram", 0)}})
        if "rsi_14" in raw and raw["rsi_14"]:
            r = raw["rsi_14"]
            result.append({"name": "RSI", "signal": r.get("signal", "neutral"),
                "values": {"value": r.get("latest") or 0}})
        if "kdj" in raw and raw["kdj"]:
            kd = raw["kdj"]
            result.append({"name": "KDJ", "signal": kd.get("signal", "neutral"),
                "values": {"k": kd.get("latest", {}).get("k", 0), "d": kd.get("latest", {}).get("d", 0), "j": kd.get("latest", {}).get("j", 0)}})
        if "boll" in raw and raw["boll"]:
            b = raw["boll"]
            result.append({"name": "BOLL", "signal": b.get("signal", "neutral"),
                "values": {"upper": b.get("latest", {}).get("upper", 0), "middle": b.get("latest", {}).get("middle", 0), "lower": b.get("latest", {}).get("lower", 0)}})
        if "sma" in raw and raw["sma"]:
            sma = raw["sma"]
            ma = sma.get("latest", {})
            ma5 = ma.get("ma5") or 0
            ma10 = ma.get("ma10") or 0
            ma20 = ma.get("ma20") or 0
            ma60 = ma.get("ma60") or 0
            sig = "neutral"
            if ma5 > ma10 > ma20 > ma60 and all(v > 0 for v in (ma5, ma10, ma20, ma60)):
                sig = "bullish"
            elif ma5 < ma10 < ma20 < ma60:
                sig = "bearish"
            result.append({"name": "MA_ARRANGE", "signal": sig,
                "values": {"ma5": ma5, "ma10": ma10, "ma20": ma20, "ma60": ma60}})
        return result

    def _build_explanation(self, name: str, ind: dict, signal: str) -> str:
        values = ind.get("values", {})
        if name == "MACD":
            dif = values.get("dif", 0)
            dea = values.get("dea", 0)
            hist = values.get("hist", 0)
            if signal == "golden_cross":
                return f"DIF({dif:.2f}) 上穿 DEA({dea:.2f})，金叉确认"
            elif signal == "dead_cross":
                return f"DIF({dif:.2f}) 下穿 DEA({dea:.2f})，死叉确认"
            return f"DIF({dif:.2f})/DEA({dea:.2f})/MACDh({hist:.2f})，无交叉信号"
        elif name == "RSI":
            val = values.get("value", 0)
            if signal == "oversold":
                return f"RSI={val:.1f}<30，超卖区间可博反弹"
            elif signal == "overbought":
                return f"RSI={val:.1f}>70，超买区间注意回落风险"
            return f"RSI={val:.1f}，30~70区间运行正常"
        elif name == "KDJ":
            k = values.get("k", 0)
            d = values.get("d", 0)
            j = values.get("j", 0)
            if signal == "golden_cross":
                return f"K({k:.1f}) 上穿 D({d:.1f})，金叉买入信号"
            elif signal == "dead_cross":
                return f"K({k:.1f}) 下穿 D({d:.1f})，死叉卖出信号"
            return f"K({k:.1f})/D({d:.1f})/J({j:.1f})，无明确交叉"
        elif name == "BOLL":
            upper = values.get("upper", 0)
            middle = values.get("middle", 0)
            lower = values.get("lower", 0)
            if signal == "price_below_lower":
                return f"价格触及下轨({lower:.2f})，支撑位可买入"
            elif signal == "price_above_upper":
                return f"价格触及上轨({upper:.2f})，压力位宜卖出"
            return f"价格在中上轨运行，布林带收窄"
        elif name == "MA_ARRANGE":
            if signal == "bullish":
                return "MA5>MA10>MA20>MA60 多头排列，趋势向上"
            elif signal == "bearish":
                return "MA5<MA10<MA20<MA60 空头排列，趋势向下"
            return "均线纠缠，方向不明"
        return "无信号"

    def _get_rating(self, score: float) -> dict:
        for threshold, stars, label, advice in RATING_THRESHOLDS:
            if score >= threshold:
                return {"stars": stars, "label": label, "advice": advice}
        return {"stars": "★☆☆☆☆", "label": "强烈卖出", "advice": "清仓或做空"}

    def _determine_trend(self, results: list) -> str:
        buy_count = sum(1 for r in r["judgment"] == "买入")
        sell_count = sum(1 for r in r["judgment"] == "卖出")
        if buy_count >= 3:
            return "偏多"
        elif sell_count >= 3:
            return "偏空"
        return "震荡"

    def _build_summary(self, score: float, rating: dict, trend: str) -> str:
        if score >= 80:
            return f"多个指标同时看多，技术面强势，{rating['advice']}"
        elif score >= 60:
            return f"技术面总体偏{trend}，多数信号支持做多，{rating['advice']}"
        elif score >= 40:
            return f"信号分歧，趋势{trend}，{rating['advice']}"
        elif score >= 20:
            return f"空头信号占优，{rating['advice']}"
        return f"全面空头，{rating['advice']}"

    def _build_risk_tips(self, results: list, indicators: list) -> str:
        tips = []
        for r in results:
            if r["name"] == "RSI" and r["signal"] == "overbought":
                tips.append("RSI超买，短期有技术回调压力")
            if r["name"] == "BOLL" and r["signal"] == "price_above_upper":
                tips.append("价格突破布林上轨，追高风险大")
        if not tips:
            tips.append("注意控制仓位，设置合理止损")
        return "；".join(tips)

    def _position_suggestion(self, score: float) -> str:
        if score >= 80:
            return "50%~70%"
        elif score >= 60:
            return "30%~50%"
        elif score >= 40:
            return "10%~30%"
        return "0%~10%"

    def _empty_result(self, code: str, name: str) -> dict:
        now = datetime.now().isoformat()
        return {
            "stock_code": code,
            "stock_name": name,
            "overall_score": 0,
            "rating": "暂无数据",
            "rating_label": "暂无数据",
            "rating_advice": "请先拉取该股票的日K线数据",
            "trend": "未知",
            "summary": "暂无足够K线数据计算指标",
            "data_source": {},
            "indicators": [],
            "risk_tips": "无数据无法评估风险",
            "position_suggestion": "0%",
            "timestamp": now,
        }

    async def analyze_async(self, stock_code: str, stock_name: str) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: asyncio.run(self.analyze(stock_code, stock_name)))


suggestion_service = SuggestionService()
