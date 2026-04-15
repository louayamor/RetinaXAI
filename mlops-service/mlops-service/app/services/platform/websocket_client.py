import asyncio
import os
from typing import Any

import httpx
from loguru import logger

BACKEND_WS_URL = os.environ.get("BACKEND_WS_URL", "ws://localhost:8000/ws")
BACKEND_API_KEY = os.environ.get("ML_SERVICE_API_KEY", "")


class WebSocketClient:
    _instance: "WebSocketClient | None" = None

    def __init__(self) -> None:
        self._base_url = BACKEND_WS_URL.replace("ws://", "http://").replace("/ws", "")

    @classmethod
    def get_instance(cls) -> "WebSocketClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=10.0)

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
        emit_url = f"{self._base_url}/emit"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    emit_url,
                    json={
                        "event": "training_stage",
                        "data": payload.get("data", {}),
                        "room": room,
                    },
                    headers={"X-API-Key": BACKEND_API_KEY} if BACKEND_API_KEY else {},
                )
                if response.status_code < 400:
                    logger.debug(
                        f"Sent training event: {stage} - {status} to room {room}"
                    )
                else:
                    logger.warning(
                        f"Failed to emit event: {response.status_code} {response.text}"
                    )
        except Exception as e:
            logger.warning(f"Failed to send training event: {e}")


_websocket_client: "WebSocketClient | None" = None


def get_websocket_client() -> "WebSocketClient":
    global _websocket_client
    if _websocket_client is None:
        _websocket_client = WebSocketClient.get_instance()
    return _websocket_client
