import asyncio
import os
from typing import Any

import httpx
from loguru import logger

BACKEND_WS_URL = os.environ.get("BACKEND_WS_URL", "ws://localhost:8000/ws")
BACKEND_API_KEY = os.environ.get("ML_SERVICE_API_KEY", "")


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
            payload = {"event": "subscribe", "data": {"room": "training:imaging"}}
            response = await self._client.post(
                self._url.replace("ws", "http") + "/subscribe",
                json=payload,
                headers={"X-API-Key": BACKEND_API_KEY} if BACKEND_API_KEY else {},
            )
            self._connected = response.status_code < 400
            logger.info(f"WebSocket client connected: {self._connected}")
            return self._connected
        except Exception as e:
            logger.warning(f"WebSocket connection failed: {e}")
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

    async def send_training_event(
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
        if not self._connected:
            await self.connect()

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

        try:
            if self._client:
                await self._client.post(
                    self._url.replace("ws", "http") + "/emit",
                    json={
                        "event": "training_stage",
                        "data": payload.get("data", {}),
                        "room": room,
                    },
                    headers={"X-API-Key": BACKEND_API_KEY} if BACKEND_API_KEY else {},
                )
                logger.debug(f"Sent training event: {stage} - {status} to room {room}")
        except Exception as e:
            logger.warning(f"Failed to send training event: {e}")


_websocket_client: WebSocketClient | None = None


def get_websocket_client() -> WebSocketClient:
    global _websocket_client
    if _websocket_client is None:
        _websocket_client = WebSocketClient.get_instance()
    return _websocket_client
