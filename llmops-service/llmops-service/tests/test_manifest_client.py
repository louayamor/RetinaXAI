from __future__ import annotations

from datetime import datetime, timezone

from app.rag.manifest_client import RagArtifact, RagManifest
from app.rag.manifest_client import RagArtifactId, RagArtifactType, RagPipeline, RagSchemaVersion


def test_indexing_pipeline_fetches_manifest(monkeypatch):
    from app.pipeline import indexing_pipeline as ip

    manifest = RagManifest(
        schema_version=RagSchemaVersion.V1,
        run_id="run-123",
        pipeline=RagPipeline.COMBINED,
        generated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        artifact_count=4,
        artifacts=[
            RagArtifact(
                schema_version=RagSchemaVersion.V1,
                artifact_id=RagArtifactId.OCR_REPORTS,
                artifact_type=RagArtifactType.JSON,
                source_path="/tmp/reports.json",
                content_hash="abc",
                content_length=10,
                indexable=True,
                content=[{"x": 1}],
            )
        ],
    )

    monkeypatch.setattr(ip, "fetch_manifest", lambda url: manifest)
    class DummyStore:
        def __init__(self, *args, **kwargs):
            self.persist_directory = None

        def ensure_ready(self):
            return None

        def reset_collection(self):
            return None

        def upsert_documents(self, chunks):
            self.chunks = chunks

    monkeypatch.setattr(ip, "ChromaStore", DummyStore)
    result = ip.IndexingPipeline().run()

    assert result["schema_version"] == RagSchemaVersion.V1
    assert result["run_id"] == "run-123"
    assert result["artifact_count"] == 4
    assert result["document_count"] == 1
    assert result["chunk_count"] >= 1


def test_fetch_manifest_rejects_malformed_payload(monkeypatch):
    from app.rag import manifest_client as mc

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "schema_version": "1.0",
                "run_id": "run-1",
                "pipeline": "combined",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "artifact_count": 2,
                "artifacts": [],
                "unexpected": True,
            }

    monkeypatch.setattr(mc.httpx, "get", lambda *args, **kwargs: DummyResponse())

    try:
        mc.fetch_manifest("http://example.com")
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Invalid RAG manifest payload" in str(exc)
