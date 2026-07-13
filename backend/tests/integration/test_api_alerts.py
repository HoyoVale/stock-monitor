import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.alert import AlertRule


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_alerts_empty(client):
    response = await client.get("/api/alerts/rules")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_alert_rule(client):
    response = await client.post("/api/alerts/rules", json={
        "stock_code": "000001",
        "alert_type": "price_above",
        "threshold": 15.50,
        "enabled": True,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["stock_code"] == "000001"
    assert data["alert_type"] == "price_above"
    assert data["threshold"] == 15.50
    assert data["id"] > 0


@pytest.mark.asyncio
async def test_create_alert_invalid_type(client):
    response = await client.post("/api/alerts/rules", json={
        "stock_code": "000001",
        "alert_type": "invalid",
        "threshold": 10.0,
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_alert_rule(client):
    create = await client.post("/api/alerts/rules", json={
        "stock_code": "000002",
        "alert_type": "price_below",
        "threshold": 8.0,
    })
    rule_id = create.json()["id"]

    delete = await client.delete(f"/api/alerts/rules/{rule_id}")
    assert delete.status_code == 200
    assert delete.json() == {"ok": True}

    delete_again = await client.delete(f"/api/alerts/rules/{rule_id}")
    assert delete_again.status_code == 404


@pytest.mark.asyncio
async def test_toggle_alert_rule(client):
    create = await client.post("/api/alerts/rules", json={
        "stock_code": "000003",
        "alert_type": "price_above",
        "threshold": 20.0,
        "enabled": True,
    })
    rule_id = create.json()["id"]

    toggle_off = await client.patch(f"/api/alerts/rules/{rule_id}?enabled=false")
    assert toggle_off.status_code == 200

    rules = await client.get("/api/alerts/rules?enabled_only=true")
    rule_ids = [r["id"] for r in rules.json()]
    assert rule_id not in rule_ids


@pytest.mark.asyncio
async def test_list_alert_records(client):
    response = await client.get("/api/alerts/records")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_filter_by_stock_code(client):
    await client.post("/api/alerts/rules", json={
        "stock_code": "000001",
        "alert_type": "price_above",
        "threshold": 10.0,
    })
    await client.post("/api/alerts/rules", json={
        "stock_code": "000002",
        "alert_type": "price_below",
        "threshold": 5.0,
    })

    filtered = await client.get("/api/alerts/rules?stock_code=000001")
    assert filtered.status_code == 200
    data = filtered.json()
    assert len(data) == 1
    assert data[0]["stock_code"] == "000001"
