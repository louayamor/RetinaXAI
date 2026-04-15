import json
from datetime import datetime
from typing import Any
import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Body, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.db.session import get_db
from app.models.notification import Notification

router = APIRouter()


# Lazy load settings to avoid import errors
def _get_settings():
    try:
        return get_settings()
    except Exception:
        return None


settings = _get_settings()


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
async def emit_event(request: EmitRequest, db: AsyncSession = Depends(get_db)):
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

    # Persist notification to database
    # Also auto-create notifications for training and XAI events
    try:
        notif_data = request.data

        # Direct notification event
        if request.event == "notification":
            notification = Notification(
                id=uuid.UUID(notif_data.get("id", str(uuid.uuid4()))),
                type=notif_data.get("type", "general"),
                title=notif_data.get("title", ""),
                message=notif_data.get("message", ""),
                read=False,
            )
            db.add(notification)
            await db.commit()
            logger.info(f"Persisted notification: {notification.title}")

        # Auto-create notifications for training events
        elif request.event == "training_stage":
            stage = notif_data.get("stage", "")
            status = notif_data.get("status", "")
            message = notif_data.get("message", "")
            pipeline = notif_data.get("pipeline", "unknown")

            # Only create notifications for significant events
            if status in ("completed", "failed") or stage == "pipeline":
                title = f"Training {status.title()}"
                notif_type = "training_error" if status == "failed" else "training"

                notification = Notification(
                    id=uuid.UUID(str(uuid.uuid4())),
                    type=notif_type,
                    title=title,
                    message=f"[{pipeline.upper()}] {message}",
                    read=False,
                )
                db.add(notification)
                await db.commit()
                logger.info(f"Created training notification: {title}")

        # Auto-create notifications for XAI events
        elif request.event and request.event.startswith("xai."):
            stage = notif_data.get("stage", "")
            status = notif_data.get("status", "")
            message = notif_data.get("message", "")

            if status in ("completed", "failed"):
                title = f"XAI {status.title()}"
                notif_type = "error" if status == "failed" else "xai"

                notification = Notification(
                    id=uuid.UUID(str(uuid.uuid4())),
                    type=notif_type,
                    title=title,
                    message=f"[{stage}] {message}",
                    read=False,
                )
                db.add(notification)
                await db.commit()
                logger.info(f"Created XAI notification: {title}")

        # Auto-create notifications for llmops events
        elif request.event in ("llmops_operation", "rag_indexing", "report_generation"):
            status = notif_data.get("status", "")
            message = notif_data.get("message", "")

            if status == "completed":
                title = "LLM Operation Complete"
                notification = Notification(
                    id=uuid.UUID(str(uuid.uuid4())),
                    type="report",
                    title=title,
                    message=message,
                    read=False,
                )
                db.add(notification)
                await db.commit()
                logger.info(f"Created LLM ops notification: {title}")

    except Exception as e:
        logger.warning(f"Failed to process notification: {e}")

    return {
        "status": "ok",
        "delivered": sent_count,
        "total_connected": len(_connected_clients),
    }


@router.get("/ws/clients")
async def get_client_count():
    return {"connected": len(_connected_clients)}
