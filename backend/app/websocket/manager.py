import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import WebSocket

from app.services.stock_service import stock_service

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections for real-time quote streaming.

    Clients subscribe to specific stock codes, and the manager broadcasts
    updated quotes to all connected clients every configured interval.
    Tracks authenticated users and connection metrics.
    """

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._subscriptions: dict[str, set[str]] = {}  # client_id -> {codes}
        self._usernames: dict[str, str] = {}  # client_id -> username
        self._connect_times: dict[str, datetime] = {}  # client_id -> connect_time
        self._broadcast_task: Optional[asyncio.Task] = None
        self._counter: int = 0
        self._total_disconnects: int = 0
        self._disconnect_reasons: dict[str, int] = {}  # reason -> count

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    @property
    def max_connections(self) -> int:
        from app.api.ws import MAX_WS_CONNECTIONS
        return MAX_WS_CONNECTIONS

    async def connect(self, websocket: WebSocket, username: str = "anonymous") -> str:
        """Accept a new WebSocket connection and assign a client ID."""
        await websocket.accept()
        self._counter += 1
        client_id = f"client_{self._counter}"
        self._connections[client_id] = websocket
        self._subscriptions[client_id] = set()
        self._usernames[client_id] = username
        self._connect_times[client_id] = datetime.now(timezone.utc)

        if self._broadcast_task is None or self._broadcast_task.done():
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())

        return client_id

    def disconnect(self, client_id: str, reason: str = "unknown"):
        """Remove a client connection and log disconnect reason."""
        username = self._usernames.pop(client_id, "unknown")
        connect_time = self._connect_times.pop(client_id, None)
        duration_s = None
        if connect_time:
            duration_s = (datetime.now(timezone.utc) - connect_time).total_seconds()

        self._connections.pop(client_id, None)
        self._subscriptions.pop(client_id, None)
        self._total_disconnects += 1
        self._disconnect_reasons[reason] = self._disconnect_reasons.get(reason, 0) + 1

        logger.info(
            f"WS disconnect: {client_id} user={username} "
            f"reason={reason} "
            f"duration={duration_s:.0f}s" if duration_s else ""
        )

        if not self._connections and self._broadcast_task:
            self._broadcast_task.cancel()
            self._broadcast_task = None

    def subscribe(self, client_id: str, codes: list[str]):
        """Subscribe a client to specific stock codes."""
        if client_id in self._subscriptions:
            self._subscriptions[client_id] = set(codes)

    async def send_to_client(self, client_id: str, data: dict):
        """Send a JSON message to a specific client."""
        ws = self._connections.get(client_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(client_id, reason="send_error")

    async def broadcast_conn_count(self):
        """Send current connection count to all clients."""
        payload = {"type": "conn_count", "count": self.connection_count}
        for client_id, ws in list(self._connections.items()):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(client_id, reason="broadcast_error")

    async def broadcast_quote_update(self):
        """Fetch latest quotes and push to all subscribed clients."""
        try:
            all_quotes = await stock_service.get_realtime_quotes()
        except Exception:
            all_quotes = []

        quote_map = {q["code"]: q for q in all_quotes}

        for client_id, codes in list(self._subscriptions.items()):
            ws = self._connections.get(client_id)
            if ws is None:
                continue

            client_quotes = []
            for code in codes:
                if code in quote_map:
                    client_quotes.append(quote_map[code])
                elif all_quotes:
                    for q in all_quotes:
                        if q["code"] == code:
                            client_quotes.append(q)
                            break

            if client_quotes:
                try:
                    await ws.send_json({"type": "quote_update", "data": client_quotes})
                except Exception:
                    self.disconnect(client_id, reason="send_error")

    async def broadcast_index_update(self):
        """Push index quotes to all index subscribers."""
        try:
            indices = await stock_service.get_index_quotes()
        except Exception:
            return

        payload = {"type": "index_update", "data": indices}
        for client_id, ws in list(self._connections.items()):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(client_id, reason="send_error")

    async def _broadcast_loop(self):
        """Background task: broadcast quotes every configured interval."""
        from app.config import REFRESH_INTERVAL
        interval = max(REFRESH_INTERVAL, 5)
        while True:
            try:
                await asyncio.sleep(interval)
                if self._connections:
                    await self.broadcast_quote_update()
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5)


ws_manager = WebSocketManager()
