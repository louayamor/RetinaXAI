from __future__ import annotations

from typing import Any

from langchain_core.documents import Document

from app.rag.manifest_client import RagArtifact
from app.utils.helpers import normalize_whitespace


def _serialize_content(content: Any) -> str:
    if isinstance(content, list):
        return "\n".join(str(item) for item in content)
    if isinstance(content, dict):
        return "\n".join(f"{key}: {value}" for key, value in content.items())
    return str(content)


def normalize_artifact(artifact: RagArtifact, run_id: str | None = None) -> list[Document]:
    content = _serialize_content(artifact.content)
    text = normalize_whitespace(content)
    metadata = {
        "schema_version": artifact.schema_version,
        "artifact_id": artifact.artifact_id.value,
        "artifact_type": artifact.artifact_type.value,
        "run_id": run_id,
        "source_path": artifact.source_path,
        "content_hash": artifact.content_hash,
        "content_length": artifact.content_length,
        "indexable": artifact.indexable,
    }
    return [Document(page_content=text, metadata=metadata)]
