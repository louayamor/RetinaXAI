from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RagArtifactManifest(BaseModel):
    schema_version: str = Field(default="1.0")
    artifact_id: str
    artifact_type: str
    source_path: str
    content_hash: str
    content_length: int
    indexable: bool = True
    content: Any | None = None


class RagManifestResponse(BaseModel):
    schema_version: str = Field(default="1.0")
    run_id: str
    pipeline: str
    generated_at: datetime
    artifact_count: int
    artifacts: list[RagArtifactManifest]
