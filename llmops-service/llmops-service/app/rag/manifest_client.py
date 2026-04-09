from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

import httpx


class RagSchemaVersion(StrEnum):
    V1 = "1.0"


class RagPipeline(StrEnum):
    CLINICAL = "clinical"
    IMAGING = "imaging"
    OCR = "ocr"
    COMBINED = "combined"
    PARTIAL = "partial"


class RagArtifactId(StrEnum):
    OCR_REPORTS = "ocr_reports"
    CLINICAL_METRICS = "clinical_metrics"
    CLINICAL_FEATURE_IMPORTANCE = "clinical_feature_importance"
    IMAGING_METRICS = "imaging_metrics"


class RagArtifactType(StrEnum):
    JSON = "json"


@dataclass(frozen=True)
class RagArtifact:
    schema_version: str
    artifact_id: RagArtifactId
    artifact_type: RagArtifactType
    source_path: str
    content_hash: str
    content_length: int
    indexable: bool
    content: Any | None = None


@dataclass(frozen=True)
class RagManifest:
    schema_version: str
    run_id: str
    pipeline: RagPipeline
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
        schema_version=RagSchemaVersion(payload["schema_version"]),
        run_id=payload["run_id"],
        pipeline=RagPipeline(payload["pipeline"]),
        generated_at=datetime.fromisoformat(generated_at.replace("Z", "+00:00")) if isinstance(generated_at, str) else generated_at,
        artifact_count=payload["artifact_count"],
        artifacts=artifacts,
    )
