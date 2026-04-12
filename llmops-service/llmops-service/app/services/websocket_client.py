import asyncio
import os
from typing import Any

import httpx
from loguru import logger

BACKEND_WS_URL = os.environ.get("BACKEND_WS_URL", "ws://localhost:8000/ws")
BACKEND_API_KEY = os.environ.get("BACKEND_API_KEY", "")


class WebSocketClient:
    _instance: "WebSocketClient | None" = None
    _connected: bool = False

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._url = BACKEND_WS_URL

    @classmethod
    def get_instance(cls) -> "WebSocketClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def connect(self) -> bool:
        if self._connected:
            return True

        try:
            self._client = httpx.AsyncClient(timeout=5.0)
            self._connected = True
            logger.info("LLMOps WebSocket client initialized")
            return True
        except Exception as e:
            logger.warning(f"WebSocket client init failed: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def send_llmops_event(
        self,
        event_type: str,
        status: str,
        progress: int,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        if not self._connected:
            await self.connect()

        payload = {
            "event": event_type,
            "data": {
                "status": status,
                "progress": progress,
                "message": message,
                "details": details or {},
            },
        }

        room = "llmops" if event_type in ("rag_indexing", "report_generation") else None

        try:
            if self._client:
                emit_payload = {"event": event_type, "data": payload.get("data", {})}
                if room:
                    emit_payload["room"] = room
                await self._client.post(
                    self._url.replace("ws", "http") + "/emit",
                    json=emit_payload,
                    headers={"X-API-Key": BACKEND_API_KEY} if BACKEND_API_KEY else {},
                )
                logger.debug(
                    f"Sent LLM ops event: {event_type} - {status} to room {room or 'broadcast'}"
                )
        except Exception as e:
            logger.warning(f"Failed to send LLM ops event: {e}")


_websocket_client: WebSocketClient | None = None


def get_websocket_client() -> WebSocketClient:
    global _websocket_client
    if _websocket_client is None:
        _websocket_client = WebSocketClient.get_instance()
    return _websocket_client
