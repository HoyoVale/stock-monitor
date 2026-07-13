"""E2E smoke tests — validate real akshare data flows end-to-end.

These tests run against the live FastAPI app and hit real akshare data.
They are designed to fail gracefully when data sources are unavailable,
rather than falsely passing with empty responses.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as ac:
        yield ac


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_indices_nonempty(client):
    """大盘指数 API 返回非空数据"""
    response = await client.get("/api/indices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1, "大盘指数至少应有1条数据"
    for idx in data:
        assert "code" in idx
        assert "name" in idx
        assert "price" in idx
        assert "change_pct" in idx


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_stock_search_returns_results(client):
    """股票搜索返回结果"""
    response = await client.get("/api/stocks?search=平安")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1, "搜索'平安'应有结果"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_stock_quote_valid_fields(client):
    """个股行情返回完整字段"""
    response = await client.get("/api/stocks/000001/quotes")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert "price" in data
    assert "open" in data
    assert "high" in data
    assert "low" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_stock_bars_has_data(client):
    """个股K线返回历史数据"""
    response = await client.get("/api/stocks/000001/bars?start=2026-06-01&end=2026-07-13")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10, "应至少有10个交易日数据"
    bar = data[0]
    assert "date" in bar
    assert "close" in bar
    assert "volume" in bar


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_indicators_complete(client):
    """技术指标计算返回完整结果"""
    response = await client.get("/api/indicators/000001")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data.get("bars_count", 0) >= 10, "需要足够数据计算技术指标"
    assert "macd" in data
    assert "rsi_14" in data
    assert "kdj" in data
    assert "boll" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_suggestion_score_in_range(client):
    """决策建议评分在 0-100 范围"""
    response = await client.get("/api/suggestions/000001")
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert 0 <= data["overall_score"] <= 100
    assert "rating" in data
    assert "rating_cn" in data
    assert "summary" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_health_endpoint(client):
    """健康检查端点可用"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
