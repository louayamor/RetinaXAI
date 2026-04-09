from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.api.rag_schemas import RagArtifactManifest, RagManifestResponse
from app.config.settings import Settings


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _artifact_from_json(artifact_id: str, path: Path, payload: Any) -> RagArtifactManifest:
    return RagArtifactManifest(
        artifact_id=artifact_id,
        artifact_type="json",
        source_path=str(path),
        content_hash=_hash_payload(payload),
        content_length=len(json.dumps(payload, ensure_ascii=True, default=str)),
        content=payload,
        indexable=True,
    )


def build_rag_manifest(settings: Settings) -> RagManifestResponse:
    artifacts: list[RagArtifactManifest] = []

    sources = [
        ("ocr_reports", Path(settings.ocr_output_dir) / "reports.json", "list"),
        ("clinical_metrics", settings.clinical_metrics_path, "json"),
        ("clinical_feature_importance", settings.clinical_feature_importance_path, "json"),
        ("imaging_metrics", settings.imaging_metrics_path, "json"),
    ]

    for artifact_id, path, _kind in sources:
        if not path.is_file():
            continue
        payload = _load_json(path)
        if artifact_id == "ocr_reports" and not isinstance(payload, list):
            continue
        artifacts.append(_artifact_from_json(artifact_id, path, payload))

    pipeline = "combined" if len(artifacts) == 4 else "partial"
    run_id = hashlib.sha1("|".join(a.content_hash for a in artifacts).encode("utf-8")).hexdigest()[:12] if artifacts else "none"
    return RagManifestResponse(
        run_id=run_id,
        pipeline=pipeline,
        generated_at=datetime.now(tz=UTC),
        artifact_count=len(artifacts),
        artifacts=artifacts,
    )
