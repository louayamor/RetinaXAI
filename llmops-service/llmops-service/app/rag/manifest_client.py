from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx


@dataclass(frozen=True)
class RagArtifact:
    schema_version: str
    artifact_id: str
    artifact_type: str
    source_path: str
    content_hash: str
    content_length: int
    indexable: bool
    content: Any | None = None


@dataclass(frozen=True)
class RagManifest:
    schema_version: str
    run_id: str
    pipeline: str
    generated_at: datetime
    artifact_count: int
    artifacts: list[RagArtifact]


def fetch_manifest(url: str, timeout: float = 30.0) -> RagManifest:
    response = httpx.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    artifacts = [RagArtifact(**artifact) for artifact in payload.get("artifacts", [])]
    generated_at = payload.get("generated_at")
    return RagManifest(
        schema_version=payload["schema_version"],
        run_id=payload["run_id"],
        pipeline=payload["pipeline"],
        generated_at=datetime.fromisoformat(generated_at.replace("Z", "+00:00")) if isinstance(generated_at, str) else generated_at,
        artifact_count=payload["artifact_count"],
        artifacts=artifacts,
    )
