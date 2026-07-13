"""POST /api/predictions/{code} 集成测试。"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.prediction_service import prediction_service


@pytest.fixture(autouse=True)
def clear_cache():
    """每个测试前清除缓存。"""
    prediction_service.invalidate_cache()
    yield
    prediction_service.invalidate_cache()


class TestPredictionsAPI:
    """预测 API 集成测试。

    注意: 预测需要真实 K 线数据，这里测试 API 契约和错误处理。
    """

    @pytest.mark.asyncio
    async def test_missing_stock_returns_400(self):
        """不存在的股票应返回 400。"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/predictions/999999", json={"days": 7}
            )
            assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_invalid_days_range(self):
        """预测天数超出范围应返回错误。"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # days=0: Pydantic 校验 (ge=1) 应拒绝
            resp = await client.post(
                "/api/predictions/600519", json={"days": 0}
            )
            assert resp.status_code in (400, 422)

            resp2 = await client.post(
                "/api/predictions/600519", json={"days": 31}
            )
            assert resp2.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_valid_request_returns_prediction_format(self):
        """有效请求应返回预测结果。

        这个测试依赖真实 akshare 数据，在 CI 环境可能失败。
        这里验证响应格式契约。
        """
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/predictions/600519", json={"days": 5}
            )
            if resp.status_code == 200:
                data = resp.json()
                assert "stock_code" in data
                assert "last_price" in data
                assert "trend" in data
                assert "predictions" in data
                assert "metrics" in data
                assert "cache_hit" in data
                assert len(data["predictions"]) == 5
                for p in data["predictions"]:
                    assert "date" in p
                    assert "price" in p
                    assert "lower" in p
                    assert "upper" in p
                    assert p["lower"] <= p["price"] <= p["upper"]
                assert 0 <= data["metrics"]["direction_accuracy_pct"] <= 100
            else:
                # 数据源不可用时应返回有意义的错误
                data = resp.json()
                assert "detail" in data

    @pytest.mark.asyncio
    async def test_default_days_is_7(self):
        """未传 days 参数时默认使用 7 天。"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/predictions/600519")
            if resp.status_code == 200:
                data = resp.json()
                assert len(data["predictions"]) == 7
            else:
                assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_cache_hit_flag_present(self):
        """响应应包含 cache_hit 标志。"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/predictions/600519", json={"days": 3}
            )
            if resp.status_code == 200:
                data = resp.json()
                assert "cache_hit" in data
                assert isinstance(data["cache_hit"], bool)
