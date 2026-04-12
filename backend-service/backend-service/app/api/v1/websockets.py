import json
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Body, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


class EmitRequest(BaseModel):
    event: str
    data: dict[str, Any]
    room: str | None = None


_redis: aioredis.Redis | None = None
_connected_clients: list[WebSocket] = []
_client_rooms: dict[WebSocket, set[str]] = {}


async def get_redis() -> aioredis.Redis | None:
    global _redis
    if _redis is None:
        try:
            _redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await _redis.ping()
            logger.info("WebSocket Redis connection established")
        except Exception as e:
            logger.warning(f"Redis not available for WebSocket: {e}")
            _redis = None
    return _redis


def _get_clients_in_room(room: str) -> list[WebSocket]:
    """Get all WebSocket clients subscribed to a specific room."""
    return [client for client, rooms in _client_rooms.items() if room in rooms]


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _connected_clients.append(websocket)
    _client_rooms[websocket] = set()
    logger.info(f"Client connected. Total clients: {len(_connected_clients)}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")

            try:
                message = json.loads(data) if isinstance(data, str) else data
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"event": "error", "data": {"message": "Invalid JSON"}}
                )
                continue

            event = message.get("event")
            payload = message.get("data", {})

            if event == "subscribe":
                room = payload.get("room")
                if room:
                    _client_rooms[websocket].add(room)
                    await websocket.send_json(
                        {"event": "subscribed", "data": {"room": room}}
                    )
                    logger.info(
                        f"Client subscribed to room: {room}, total rooms: {len(_client_rooms[websocket])}"
                    )

            elif event == "unsubscribe":
                room = payload.get("room")
                if room:
                    _client_rooms[websocket].discard(room)
                    await websocket.send_json(
                        {"event": "unsubscribed", "data": {"room": room}}
                    )

            elif event == "ping":
                await websocket.send_json(
                    {"event": "pong", "data": {"timestamp": payload.get("timestamp")}}
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        if websocket in _connected_clients:
            _connected_clients.remove(websocket)
        _client_rooms.pop(websocket, None)
        logger.info(f"Client removed. Total clients: {len(_connected_clients)}")


@router.post("/emit")
async def emit_event(request: EmitRequest):
    message = {
        "event": request.event,
        "data": request.data,
    }

    redis = await get_redis()

    # Determine target clients based on room
    if request.room:
        # Send to clients in specific room
        target_clients = _get_clients_in_room(request.room)
        logger.info(f"Room {request.room}: targeting {len(target_clients)} clients")

        # Also publish to Redis for multi-instance support
        if redis:
            channel = f"ws:{request.room}"
            await redis.publish(channel, json.dumps(message))
    else:
        # Broadcast to all connected clients
        target_clients = _connected_clients
        logger.info(f"Broadcast: targeting {len(target_clients)} clients")

        if redis:
            channel = "ws:broadcast"
            await redis.publish(channel, json.dumps(message))

    sent_count = 0
    for client in target_clients:
        try:
            await client.send_json(message)
            sent_count += 1
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")

    logger.debug(f"Emitted {request.event} to {sent_count} clients")
    return {
        "status": "ok",
        "delivered": sent_count,
        "total_connected": len(_connected_clients),
    }


@router.get("/ws/clients")
async def get_client_count():
    return {"connected": len(_connected_clients)}
