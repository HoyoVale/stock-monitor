"""WebSocket endpoint for real-time quote streaming."""
import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.websocket import ws_manager

router = APIRouter()


@router.websocket("/ws/quotes")
async def websocket_quotes(websocket: WebSocket, codes: str = ""):
    """WebSocket endpoint for real-time stock quotes.

    Query params:
        codes: Comma-separated list of stock codes to subscribe to.
               If empty, all available quotes are pushed.
               Example: /ws/quotes?codes=000001,600000

    Message format (server -> client):
        {"type": "quote_update", "data": [{...}, ...]}
        {"type": "connected", "client_id": "..."}
        {"type": "error", "message": "..."}
    """
    client_id = await ws_manager.connect(websocket)
    code_list = [c.strip() for c in codes.split(",") if c.strip()]

    if code_list:
        ws_manager.subscribe(client_id, code_list)

    try:
        await websocket.send_json({"type": "connected", "client_id": client_id})

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
                # Send heartbeat to keep connection alive
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(client_id)
