"""WebSocket endpoint for real-time quote streaming with JWT auth."""
import asyncio
import json
import logging
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.auth import decode_access_token
from app.websocket import ws_manager

logger = logging.getLogger(__name__)

MAX_WS_CONNECTIONS = int(os.getenv("MAX_WS_CONNECTIONS", "50"))

router = APIRouter()


@router.websocket("/ws/quotes")
async def websocket_quotes(
    websocket: WebSocket,
    codes: str = "",
    token: str = Query(default="", description="JWT access token for authentication"),
):
    """WebSocket endpoint for real-time stock quotes.

    Query params:
        token: JWT access token (required). Pass as /ws/quotes?token=xxx
        codes: Comma-separated list of stock codes to subscribe to.
               If empty, all available quotes are pushed.
               Example: /ws/quotes?token=xxx&codes=000001,600000

    Message format (server -> client):
        {"type": "connected", "client_id": "..."}
        {"type": "error", "message": "...", "code": 4008}
        {"type": "quote_update", "data": [{...}, ...]}
        {"type": "conn_count", "count": N}
    """
    # Authenticate via JWT token
    if not token:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "message": "Authentication required. Pass token as query param: ?token=xxx",
            "code": 4008,
        })
        await websocket.close(code=4008, reason="auth_required")
        return

    payload = decode_access_token(token)
    if payload is None:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "message": "Invalid or expired token",
            "code": 4008,
        })
        await websocket.close(code=4008, reason="auth_invalid")
        return

    username = payload.get("sub", "unknown")

    # Enforce connection limit
    if ws_manager.connection_count >= MAX_WS_CONNECTIONS:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "message": f"Max connections ({MAX_WS_CONNECTIONS}) reached. Please try again later.",
            "code": 4009,
        })
        await websocket.close(code=4009, reason="max_connections")
        logger.warning(f"WebSocket connection rejected: max connections ({MAX_WS_CONNECTIONS})")
        return

    client_id = await ws_manager.connect(websocket, username=username)
    code_list = [c.strip() for c in codes.split(",") if c.strip()]

    if code_list:
        ws_manager.subscribe(client_id, code_list)

    logger.info(f"WebSocket connected: {client_id} (user={username}, total={ws_manager.connection_count})")

    try:
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "user": username,
            "conn_count": ws_manager.connection_count,
        })

        # Broadcast updated connection count
        await ws_manager.broadcast_conn_count()

        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                data = json.loads(raw)
                msg_type = data.get("type", "")

                if msg_type == "subscribe":
                    new_codes = data.get("codes", [])
                    if new_codes:
                        ws_manager.subscribe(client_id, new_codes)
                        await websocket.send_json({
                            "type": "subscribed",
                            "codes": new_codes,
                        })

                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "unsubscribe":
                    ws_manager.subscribe(client_id, [])
                    await websocket.send_json({"type": "unsubscribed"})

            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    finally:
        disconnect_reason = "client_closed"
        ws_manager.disconnect(client_id, reason=disconnect_reason)
        logger.info(f"WebSocket disconnected: {client_id} (user={username}, total={ws_manager.connection_count})")
        await ws_manager.broadcast_conn_count()
