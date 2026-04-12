import os
from collections.abc import Callable
from typing import Any

import redis.asyncio as aioredis
from app.core.config import get_settings
from loguru import logger
from python_socketio import AsyncManager, AsyncServer
from python_socketio.asyncio_async_manager import AsyncioAsyncManager
from python_socketio.namespace import AsyncNamespace


class WebSocketNamespace(AsyncNamespace):
    async def on_connect(self, sid: str, environ: dict[str, Any]) -> None:
        logger.info(f"Client connected: sid={sid}")
        await self.emit(
            "connected", {"sid": sid, "message": "Connected to RetinaXAI WebSocket"}
        )

    async def on_disconnect(self, sid: str) -> None:
        logger.info(f"Client disconnected: sid={sid}")

    async def on_subscribe(self, sid: str, data: dict[str, Any]) -> None:
        room = data.get("room")
        if room:
            await self.enter_room(sid, room)
            logger.info(f"Client {sid} subscribed to room: {room}")

    async def on_unsubscribe(self, sid: str, data: dict[str, Any]) -> None:
        room = data.get("room")
        if room:
            await self.leave_room(sid, room)
            logger.info(f"Client {sid} unsubscribed from room: {room}")


class SocketManager:
    _instance: "SocketManager | None" = None
    _server: AsyncServer | None = None
    _redis: aioredis.Redis | None = None

    def __init__(self) -> None:
        self.settings = get_settings()
        self._namespace = WebSocketNamespace("/")

    @classmethod
    def get_instance(cls) -> "SocketManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        redis_url = self.settings.REDIS_URL
        logger.info(f"Initializing SocketManager with Redis: {redis_url}")

        try:
            self._redis = aioredis.from_url(
                redis_url, encoding="utf-8", decode_responses=True
            )
            await self._redis.ping()
            logger.info("Redis connection verified")
        except Exception as e:
            logger.warning(f"Redis not available, falling back to in-memory: {e}")
            self._redis = None

        self._server = AsyncServer(
            async_mode="asyncio",
            cors_allowed_origins="*",
            manager=AsyncioAsyncManager() if not self._redis else None,
        )
        self._server.on("connect", self._namespace.on_connect)
        self._server.on("disconnect", self._namespace.on_disconnect)
        self._server.on("subscribe", self._namespace.on_subscribe)
        self._server.on("unsubscribe", self._namespace.on_unsubscribe)

        logger.info("SocketManager initialized")

    @property
    def server(self) -> AsyncServer:
        if self._server is None:
            raise RuntimeError(
                "SocketManager not initialized. Call initialize() first."
            )
        return self._server

    async def emit_to_room(self, room: str, event: str, data: dict[str, Any]) -> None:
        if self._server:
            await self._server.emit(event, data, room=room)
            logger.debug(f"Emitted {event} to room {room}: {data}")

    async def emit_to_all(self, event: str, data: dict[str, Any]) -> None:
        if self._server:
            await self._server.emit(event, data)
            logger.debug(f"Emitted {event} to all: {data}")

    async def emit_training_event(
        self,
        job_id: str,
        pipeline: str,
        stage: str,
        status: str,
        progress: int,
        message: str | None = None,
        metrics: dict[str, float] | None = None,
        error: str | None = None,
    ) -> None:
        payload = {
            "event": "training_stage",
            "data": {
                "job_id": job_id,
                "pipeline": pipeline,
                "stage": stage,
                "status": status,
                "progress": progress,
                "message": message,
                "metrics": metrics,
                "error": error,
            },
        }
        room = f"training:{pipeline}"
        await self.emit_to_room(room, "training_stage", payload)
        await self.emit_to_room(f"job:{job_id}", "training_stage", payload)
        logger.info(f"Emitted training event: {stage} - {status} ({progress}%)")

    async def emit_llmops_event(
        self,
        event_type: str,
        status: str,
        progress: int,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "event": event_type,
            "data": {
                "status": status,
                "progress": progress,
                "message": message,
                "details": details or {},
            },
        }
        await self.emit_to_all(event_type, payload)
        logger.info(f"Emitted LLM ops event: {event_type} - {status}")

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")
        self._server = None
        SocketManager._instance = None


def get_socket_manager() -> SocketManager:
    return SocketManager.get_instance()
