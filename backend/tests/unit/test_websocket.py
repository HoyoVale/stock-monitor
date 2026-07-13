"""Tests for WebSocket manager and endpoint."""
import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.websocket.manager import WebSocketManager


class TestWebSocketManager:
    """Test the WebSocket connection manager."""

    @pytest.fixture
    def manager(self):
        mgr = WebSocketManager()
        yield mgr
        # Clean up broadcast task
        if mgr._broadcast_task and not mgr._broadcast_task.done():
            mgr._broadcast_task.cancel()

    @pytest.fixture
    def mock_websocket(self):
        ws = MagicMock()
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_text = AsyncMock()
        ws.close = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_assigns_client_id(self, manager, mock_websocket):
        client_id = await manager.connect(mock_websocket)
        assert client_id.startswith("client_")
        assert client_id in manager._connections
        assert client_id in manager._subscriptions

    @pytest.mark.asyncio
    async def test_connect_accepts_websocket(self, manager, mock_websocket):
        await manager.connect(mock_websocket)
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_removes_client(self, manager, mock_websocket):
        client_id = await manager.connect(mock_websocket)
        manager.disconnect(client_id)
        assert client_id not in manager._connections
        assert client_id not in manager._subscriptions

    @pytest.mark.asyncio
    async def test_subscribe_sets_codes(self, manager, mock_websocket):
        client_id = await manager.connect(mock_websocket)
        manager.subscribe(client_id, ["000001", "600000"])
        assert manager._subscriptions[client_id] == {"000001", "600000"}

    @pytest.mark.asyncio
    async def test_disconnect_unknown_client_no_error(self, manager):
        manager.disconnect("nonexistent")
        # Should not raise

    @pytest.mark.asyncio
    async def test_send_to_client(self, manager, mock_websocket):
        client_id = await manager.connect(mock_websocket)
        await manager.send_to_client(client_id, {"type": "test"})
        mock_websocket.send_json.assert_called_with({"type": "test"})

    @pytest.mark.asyncio
    async def test_send_to_disconnected_client(self, manager):
        # Should not raise
        await manager.send_to_client("nonexistent", {"type": "test"})

    @pytest.mark.asyncio
    async def test_broadcast_quote_update(self, manager, mock_websocket):
        client_id = await manager.connect(mock_websocket)
        manager.subscribe(client_id, ["000001"])

        mock_quotes = [{"code": "000001", "name": "平安银行", "price": 10.0}]

        with patch.object(manager, "_connections", {client_id: mock_websocket}):
            with patch("app.websocket.manager.stock_service.get_realtime_quotes",
                       AsyncMock(return_value=mock_quotes)):
                await manager.broadcast_quote_update()

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "quote_update"
        assert len(call_args["data"]) == 1

    @pytest.mark.asyncio
    async def test_broadcast_handles_service_error(self, manager, mock_websocket):
        client_id = await manager.connect(mock_websocket)

        with patch("app.websocket.manager.stock_service.get_realtime_quotes",
                   AsyncMock(side_effect=RuntimeError("down"))):
            # Should not raise
            await manager.broadcast_quote_update()

    @pytest.mark.asyncio
    async def test_multiple_clients(self, manager):
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = MagicMock()
        ws2.accept = AsyncMock()
        ws2.send_json = AsyncMock()

        cid1 = await manager.connect(ws1)
        cid2 = await manager.connect(ws2)

        assert cid1 != cid2
        assert len(manager._connections) == 2

        manager.disconnect(cid1)
        assert len(manager._connections) == 1
        assert cid1 not in manager._connections
        assert cid2 in manager._connections
