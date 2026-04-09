from __future__ import annotations

from langchain_core.documents import Document

from app.rag.manifest_client import RagArtifact, RagArtifactId, RagArtifactType, RagSchemaVersion
from app.vectorstore.document_loader import normalize_artifact


def test_normalize_artifact_serializes_dict_payload():
    artifact = RagArtifact(
        schema_version=RagSchemaVersion.V1,
        artifact_id=RagArtifactId.CLINICAL_METRICS,
        artifact_type=RagArtifactType.JSON,
        source_path="/tmp/metrics.json",
        content_hash="abc",
        content_length=10,
        indexable=True,
        content={"accuracy": 0.9, "num_samples": 10},
    )

    docs = normalize_artifact(artifact)

    assert len(docs) == 1
    assert isinstance(docs[0], Document)
    assert "accuracy: 0.9" in docs[0].page_content
    assert docs[0].metadata["artifact_id"] == "clinical_metrics"
