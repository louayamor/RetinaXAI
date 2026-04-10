from __future__ import annotations

from app.rag.manifest_client import RagArtifact, RagArtifactId, RagArtifactType, RagSchemaVersion
from app.vectorstore.document_loader import chunk_documents, normalize_artifact


def test_chunk_documents_preserve_metadata_and_ids():
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
    chunks = chunk_documents(docs, chunk_size=8, chunk_overlap=2)

    assert chunks
    assert chunks[0].id is not None and chunks[0].id.startswith("clinical_metrics:abc:0")
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[0].metadata["run_id"] is None
