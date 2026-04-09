from __future__ import annotations

from pathlib import Path
import fcntl

from langchain_core.documents import Document

from app.vectorstore.chroma_store import ChromaStore


def test_chroma_store_uses_configured_collection(tmp_path, monkeypatch):
    monkeypatch.setenv("RETINAXAI_BASE_DIR", str(tmp_path))
    store = ChromaStore()
    store.ensure_ready()

    assert store.persist_directory == tmp_path / "llmops-service" / "llmops-service" / "data" / "rag" / "chroma"
    assert store.collection_name == "retinaxai_rag"
    assert store.persist_directory.exists()
    spec = store.collection_spec()
    assert spec["collection_name"] == "retinaxai_rag"


def test_chroma_store_reset_collection_uses_same_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("RETINAXAI_BASE_DIR", str(tmp_path))
    store = ChromaStore()
    store.ensure_ready()

    created = []

    class DummyVectorStore:
        def add_documents(self, documents):
            created.append(("add", len(documents), documents[0].metadata["artifact_id"]))

    monkeypatch.setattr(store, "_make_vectorstore", lambda persist_directory: DummyVectorStore())
    store.upsert_documents([Document(page_content="hello", metadata={"artifact_id": "x", "content_hash": "y"})])

    assert created[0] == ("add", 1, "x")


def test_chroma_store_rebuild_lock_rejects_concurrent_rebuild(tmp_path, monkeypatch):
    monkeypatch.setenv("RETINAXAI_BASE_DIR", str(tmp_path))
    store = ChromaStore()
    store.ensure_ready()

    class DummyLockFile:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def fileno(self):
            return 1

    import app.vectorstore.chroma_store as cs

    monkeypatch.setattr(cs.Path, "open", lambda self, *args, **kwargs: DummyLockFile())

    def fake_flock(*args, **kwargs):
        raise BlockingIOError()

    monkeypatch.setattr(fcntl, "flock", fake_flock)

    try:
        with store.acquire_rebuild_lock():
            pass
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "already in progress" in str(exc)


def test_chroma_store_swap_directories_restores_active_on_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("RETINAXAI_BASE_DIR", str(tmp_path))
    store = ChromaStore()
    store.ensure_ready()

    active_dir = store.persist_directory
    staging_dir = store.staging_directory
    backup_dir = store.backup_directory

    active_dir.mkdir(parents=True, exist_ok=True)
    (active_dir / "keep.txt").write_text("keep", encoding="utf-8")
    staging_dir.mkdir(parents=True, exist_ok=True)
    (staging_dir / "new.txt").write_text("new", encoding="utf-8")

    calls = []

    def fake_replace(src, dst):
        calls.append((Path(src).name, Path(dst).name))
        if len(calls) == 2:
            raise OSError("swap failed")
        return None

    monkeypatch.setattr("app.vectorstore.chroma_store.os.replace", fake_replace)

    try:
        store._swap_directories(staging_dir)
        raise AssertionError("expected OSError")
    except OSError:
        pass

    assert active_dir.exists()
    assert (active_dir / "keep.txt").exists()
    assert not backup_dir.exists()


def test_chroma_store_rebuild_collection_atomically_writes_state_and_swaps(tmp_path, monkeypatch):
    monkeypatch.setenv("RETINAXAI_BASE_DIR", str(tmp_path))
    store = ChromaStore()
    store.ensure_ready()

    recorded = []

    class DummyStagingStore:
        def __init__(self, persist_directory, collection_name, embedding_model, embedding_function):
            self.persist_directory = Path(persist_directory)
            self.collection_name = collection_name
            self.embedding_model = embedding_model
            self.embedding_function = embedding_function

        def ensure_ready(self):
            self.persist_directory.mkdir(parents=True, exist_ok=True)

        def upsert_documents(self, chunks):
            recorded.append(("upsert", len(chunks), self.persist_directory.name))

        def write_state(self, state):
            recorded.append(("state", state["run_id"], self.persist_directory.name))

    monkeypatch.setattr("app.vectorstore.chroma_store.ChromaStore", DummyStagingStore)
    monkeypatch.setattr(store, "_swap_directories", lambda staging_directory: recorded.append(("swap", Path(staging_directory).name)))

    chunks = []
    state = {"run_id": "run-1"}
    store.rebuild_collection_atomically(chunks, state)

    assert recorded == [("upsert", 0, "chroma.staging"), ("state", "run-1", "chroma.staging"), ("swap", "chroma.staging")]
