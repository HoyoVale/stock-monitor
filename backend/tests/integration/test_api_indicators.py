import pytest


@pytest.mark.asyncio
async def test_indicators_empty(client):
    response = await client.get("/api/indicators/600519")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_suggestions_empty(client):
    response = await client.get("/api/suggestions/600519?name=贵州茅台")
    assert response.status_code == 200
    data = response.json()
    assert "stock_code" in data
    assert "overall_score" in data
