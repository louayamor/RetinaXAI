from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import TypedDict

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.rag.manifest_client import fetch_manifest
from app.vectorstore.chroma_store import ChromaStore
from app.vectorstore.document_loader import normalize_artifact


class PipelineResult(TypedDict):
    schema_version: str
    run_id: str
    artifact_count: int
    pipeline: str
    document_count: int
    chunk_count: int


class IndexingPipeline:
    def run(self) -> PipelineResult:
        start_time = time.time()

        manifest = fetch_manifest(settings.rag_manifest_url)
        store = ChromaStore(
            settings.rag_chroma_persist_directory,
            settings.rag_chroma_collection_name,
            settings.rag_embedding_model,
        )
        store.ensure_ready()
        store.upsert_documents([])

        documents = []
        for artifact in manifest.artifacts:
            if not artifact.indexable:
                continue
            documents.extend(normalize_artifact(artifact, run_id=manifest.run_id))

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(documents)
        state = {
            "schema_version": manifest.schema_version,
            "run_id": manifest.run_id,
            "artifact_count": manifest.artifact_count,
            "pipeline": manifest.pipeline,
            "document_count": len(documents),
            "chunk_count": len(chunks),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if hasattr(store, "rebuild_collection_atomically"):
            store.rebuild_collection_atomically(chunks, state)
        else:
            store.upsert_documents(chunks)
            if hasattr(store, "write_state"):
                store.write_state(state)

        elapsed_time = time.time() - start_time

        self._log_to_mlflow(
            manifest=manifest,
            document_count=len(documents),
            chunk_count=len(chunks),
            elapsed_time=elapsed_time,
            run_index=len(chunks) % 1000,
        )

        return {
            "schema_version": manifest.schema_version,
            "run_id": manifest.run_id,
            "artifact_count": manifest.artifact_count,
            "pipeline": manifest.pipeline,
            "document_count": len(documents),
            "chunk_count": len(chunks),
        }

    def _log_to_mlflow(
        self,
        manifest,
        document_count: int,
        chunk_count: int,
        elapsed_time: float,
        run_index: int = 0,
    ) -> None:
        try:
            import mlflow

            if not settings.mlflow_tracking_uri:
                return

            with mlflow.start_run(run_name=f"llmops_indexing_{manifest.run_id}_{run_index:03d}"):
                mlflow.log_params({
                    "run_id": manifest.run_id,
                    "pipeline": manifest.pipeline,
                    "schema_version": manifest.schema_version,
                })
                mlflow.log_metrics({
                    "artifact_count": manifest.artifact_count,
                    "document_count": document_count,
                    "chunk_count": chunk_count,
                    "indexing_duration_seconds": elapsed_time,
                    "embedding_model": settings.rag_embedding_model,
                    "chunk_size": settings.rag_chunk_size,
                    "chunk_overlap": settings.rag_chunk_overlap,
                })
        except Exception:
            pass
