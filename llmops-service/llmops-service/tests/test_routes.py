from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_endpoint_with_mock(monkeypatch):
    import app.api.routes as routes_module

    class MockPipeline:
        def generate_report(self, payload: dict) -> dict:
            return {
                "content": "Mock clinical report.",
                "summary": "Mock summary.",
                "model_used": "mock-model",
            }

    monkeypatch.setattr(routes_module, "InferencePipeline", MockPipeline)

    payload = {
        "patient": {"id": "P001", "age": 55},
        "prediction": {"grade": 2},
        "report_type": "report",
        "language": "en",
        "tone": "clinical",
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    parsed = json.loads(body["response"])
    assert parsed["content"] == "Mock clinical report."
    assert parsed["summary"] == "Mock summary."


def test_generate_endpoint_returns_503_on_error(monkeypatch):
    import app.api.routes as routes_module

    class BrokenPipeline:
        def generate_report(self, payload: dict) -> dict:
            raise RuntimeError("LLM unavailable")

    monkeypatch.setattr(routes_module, "InferencePipeline", BrokenPipeline)

    response = client.post("/api/generate", json={})
    assert response.status_code == 503


def test_rag_endpoints_use_indexing_pipeline(monkeypatch):
    import app.api.routes as routes_module

    class MockIndexingPipeline:
        def run(self) -> dict:
            return {"schema_version": "1.0", "run_id": "run-1", "artifact_count": 4}

    monkeypatch.setattr(routes_module, "IndexingPipeline", MockIndexingPipeline)

    response = client.post("/api/rag/reindex")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["result"]["run_id"] == "run-1"

    status_response = client.get("/api/rag/status")
    assert status_response.status_code == 200
    assert status_response.json()["artifact_count"] == 4
