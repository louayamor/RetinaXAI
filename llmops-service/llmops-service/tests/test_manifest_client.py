from __future__ import annotations

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
    result = ip.IndexingPipeline().run()

    assert result["schema_version"] == RagSchemaVersion.V1
    assert result["run_id"] == "run-123"
    assert result["artifact_count"] == 4
