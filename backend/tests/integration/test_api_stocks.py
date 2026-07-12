import pytest


@pytest.mark.asyncio
async def test_list_stocks_empty(client):
    response = await client.get("/api/stocks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_stock_quote_not_found(client):
    response = await client.get("/api/stocks/999999/quotes")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_indices_empty(client):
    response = await client.get("/api/indices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
