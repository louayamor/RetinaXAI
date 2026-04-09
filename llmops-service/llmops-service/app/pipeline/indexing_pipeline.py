from __future__ import annotations

from app.core.config import settings
from app.rag.manifest_client import fetch_manifest


class IndexingPipeline:
    def run(self) -> dict[str, object]:
        manifest = fetch_manifest(settings.rag_manifest_url)
        return {
            "schema_version": manifest.schema_version,
            "run_id": manifest.run_id,
            "artifact_count": manifest.artifact_count,
            "pipeline": manifest.pipeline,
        }
