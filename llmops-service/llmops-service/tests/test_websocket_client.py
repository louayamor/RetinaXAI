from __future__ import annotations

import json

import httpx
import pytest


@pytest.mark.asyncio
async def test_send_xai_event_emits_correct_event_name(respx_mock):
    """send_xai_event emits a fully-qualified event name (e.g. xai.prediction.started)."""
    route = respx_mock.post("http://localhost:8000/emit").mock(
        return_value=httpx.Response(200)
    )

    from app.services.websocket_client import send_xai_event

    await send_xai_event(
        event="xai.prediction",
        stage="prediction",
        status="started",
        progress=0,
        message="Generating prediction explanation...",
        prediction_id="pred-001",
    )

    assert route.called
    body = json.loads(route.calls[0].request.content)
    assert body["event"] == "xai.prediction.started"
    assert body["room"] == "xai:prediction"
    assert body["data"]["prediction_id"] == "pred-001"
    assert body["data"]["stage"] == "prediction"
    assert body["data"]["status"] == "started"


@pytest.mark.asyncio
async def test_send_xai_event_emits_correct_room_for_each_stage(respx_mock):
    """send_xai_event emits events to the correct xai:<stage> room."""
    from app.services.websocket_client import send_xai_event

    stages = ["prediction", "gradcam", "severity"]

    route = respx_mock.post("http://localhost:8000/emit").mock(
        return_value=httpx.Response(200)
    )

    for i, stage in enumerate(stages):
        await send_xai_event(
            event=f"xai.{stage}",
            stage=stage,
            status="completed",
            progress=100,
            message=f"{stage} done",
            prediction_id="pred-002",
        )

        body = json.loads(route.calls[i].request.content)
        assert body["room"] == f"xai:{stage}"
        assert body["event"] == f"xai.{stage}.completed"


@pytest.mark.asyncio
async def test_send_xai_event_includes_details_and_error(respx_mock):
    """send_xai_event includes optional details and error fields in the payload."""
    from app.services.websocket_client import send_xai_event

    route = respx_mock.post("http://localhost:8000/emit").mock(
        return_value=httpx.Response(200)
    )

    await send_xai_event(
        event="xai.gradcam",
        stage="gradcam",
        status="failed",
        progress=0,
        message="GradCAM error",
        prediction_id="pred-003",
        details={"left_regions": 3},
        error="model timeout",
    )

    assert route.called
    body = json.loads(route.calls[0].request.content)
    assert body["event"] == "xai.gradcam.failed"
    assert body["data"]["error"] == "model timeout"
    assert body["data"]["details"] == {"left_regions": 3}


@pytest.mark.asyncio
async def test_send_xai_event_does_not_raise_on_http_error(respx_mock):
    """send_xai_event swallows HTTP errors and does not raise."""
    from app.services.websocket_client import send_xai_event

    respx_mock.post("http://localhost:8000/emit").mock(
        return_value=httpx.Response(500)
    )

    # Should not raise even when the backend returns 500
    await send_xai_event(
        event="xai.severity",
        stage="severity",
        status="started",
        progress=0,
        message="Starting severity report",
        prediction_id="pred-004",
    )


@pytest.mark.asyncio
async def test_send_xai_event_does_not_raise_on_connection_error(respx_mock):
    """send_xai_event swallows connection errors and does not raise."""
    from app.services.websocket_client import send_xai_event

    respx_mock.post("http://localhost:8000/emit").mock(
        side_effect=httpx.ConnectError("connection refused")
    )

    await send_xai_event(
        event="xai.prediction",
        stage="prediction",
        status="started",
        progress=0,
        message="Starting prediction",
        prediction_id="pred-005",
    )


def test_websocket_client_singleton():
    """WebSocketClient.get_instance returns the same instance each time."""
    from app.services.websocket_client import WebSocketClient

    # Reset singleton for isolation
    WebSocketClient._instance = None

    a = WebSocketClient.get_instance()
    b = WebSocketClient.get_instance()
    assert a is b

    WebSocketClient._instance = None


@pytest.mark.asyncio
async def test_websocket_client_connect_sets_connected():
    """WebSocketClient.connect sets _connected to True."""
    from app.services.websocket_client import WebSocketClient

    client = WebSocketClient()
    result = await client.connect()
    assert result is True
    assert client.is_connected is True
    await client.disconnect()


@pytest.mark.asyncio
async def test_websocket_client_disconnect_closes_client():
    """WebSocketClient.disconnect closes the underlying httpx client."""
    from app.services.websocket_client import WebSocketClient

    client = WebSocketClient()
    await client.connect()
    assert client.is_connected is True
    await client.disconnect()
    assert client.is_connected is False
