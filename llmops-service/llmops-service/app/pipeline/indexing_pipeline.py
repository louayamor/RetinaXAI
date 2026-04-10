from __future__ import annotations

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

        return {
            "schema_version": manifest.schema_version,
            "run_id": manifest.run_id,
            "artifact_count": manifest.artifact_count,
            "pipeline": manifest.pipeline,
            "document_count": len(documents),
            "chunk_count": len(chunks),
        }
