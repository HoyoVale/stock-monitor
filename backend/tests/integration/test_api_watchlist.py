import pytest


@pytest.mark.asyncio
async def test_add_watchlist(client):
    response = await client.post("/api/watchlist", json={"code": "600519", "name": "贵州茅台"})
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "600519"
    assert data["name"] == "贵州茅台"


@pytest.mark.asyncio
async def test_list_watchlist(client):
    await client.post("/api/watchlist", json={"code": "000001", "name": "平安银行"})
    response = await client.get("/api/watchlist")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_delete_watchlist(client):
    resp = await client.post("/api/watchlist", json={"code": "300750", "name": "宁德时代"})
    item_id = resp.json()["id"]
    response = await client.delete(f"/api/watchlist/{item_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_duplicate_watchlist(client):
    await client.post("/api/watchlist", json={"code": "600519", "name": "贵州茅台"})
    response = await client.post("/api/watchlist", json={"code": "600519", "name": "贵州茅台"})
    assert response.status_code == 400
