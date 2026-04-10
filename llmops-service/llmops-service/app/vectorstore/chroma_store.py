from __future__ import annotations

import json
import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


class ChromaStore:
    def __init__(
        self,
        persist_directory: str | Path | None = None,
        collection_name: str | None = None,
        embedding_model: str | None = None,
        embedding_function: Any | None = None,
    ) -> None:
        base_dir = Path(os.environ.get("RETINAXAI_BASE_DIR", "/home/louay/RetinaXAI"))
        self.persist_directory = Path(
            persist_directory or base_dir / "llmops-service" / "llmops-service" / "data" / "rag" / "chroma"
        )
        self.collection_name = collection_name or "retinaxai_rag"
        self.embedding_model = embedding_model or "sentence-transformers/all-MiniLM-L6-v2"
        self.embedding_function = embedding_function or HuggingFaceEmbeddings(model_name=self.embedding_model)

    @property
    def state_path(self) -> Path:
        return self.persist_directory / "index_state.json"

    @property
    def lock_path(self) -> Path:
        return self.persist_directory / "index.lock"

    @property
    def staging_directory(self) -> Path:
        return self.persist_directory.with_name(f"{self.persist_directory.name}.staging")

    @property
    def backup_directory(self) -> Path:
        return self.persist_directory.with_name(f"{self.persist_directory.name}.previous")

    def ensure_ready(self) -> None:
        self.persist_directory.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def acquire_rebuild_lock(self):
        self.ensure_ready()
        with self.lock_path.open("a+", encoding="utf-8") as lock_file:
            try:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RuntimeError("RAG index rebuild already in progress") from exc

            try:
                yield
            finally:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def collection_spec(self) -> dict[str, str]:
        return {
            "persist_directory": str(self.persist_directory),
            "collection_name": self.collection_name,
        }

    def _remove_path(self, path: Path) -> None:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    def _swap_directories(self, staging_directory: Path) -> None:
        import os as _os

        active_directory = self.persist_directory
        backup_directory = self.backup_directory

        if backup_directory.exists():
            self._remove_path(backup_directory)

        active_existed = active_directory.exists()
        if active_existed:
            _os.replace(active_directory, backup_directory)

        try:
            _os.replace(staging_directory, active_directory)
        except Exception:
            if active_existed and backup_directory.exists():
                if active_directory.exists():
                    self._remove_path(active_directory)
                _os.replace(backup_directory, active_directory)
            raise
        else:
            if backup_directory.exists():
                self._remove_path(backup_directory)

    def _make_vectorstore(self, persist_directory: Path) -> Chroma:
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
            persist_directory=str(persist_directory),
        )

    def upsert_documents(self, documents: list[Document]) -> None:
        if not documents:
            return

        vectorstore = self._make_vectorstore(self.persist_directory)
        vectorstore.add_documents(documents)

    def query(self, text: str, top_k: int = 4) -> list[tuple[Any, float]]:
        vectorstore = self._make_vectorstore(self.persist_directory)
        return vectorstore.similarity_search_with_score(text, k=top_k)

    def rebuild_collection_atomically(self, documents: list[Document], state: dict[str, Any]) -> None:
        self.ensure_ready()

        with self.acquire_rebuild_lock():
            staging_directory = self.staging_directory
            backup_directory = self.backup_directory

            if staging_directory.exists():
                self._remove_path(staging_directory)
            if backup_directory.exists():
                self._remove_path(backup_directory)

            staging_store = ChromaStore(
                staging_directory,
                self.collection_name,
                self.embedding_model,
                self.embedding_function,
            )
            staging_store.ensure_ready()
            staging_store.upsert_documents(documents)
            staging_store.write_state(state)

            self._swap_directories(staging_directory)

    def write_state(self, state: dict[str, Any]) -> None:
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(state, ensure_ascii=True, sort_keys=True, default=str, indent=2)
        self.state_path.write_text(payload, encoding="utf-8")

    def read_state(self) -> dict[str, Any] | None:
        if not self.state_path.is_file():
            return None

        return json.loads(self.state_path.read_text(encoding="utf-8"))
