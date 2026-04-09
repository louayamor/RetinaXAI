from __future__ import annotations


def test_llmops_settings_include_rag_and_mlflow_defaults(monkeypatch):
    monkeypatch.setenv("RAG_MANIFEST_URL", "http://example.com/api/rag/manifest")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://dagshub.com/example/repo.mlflow")
    monkeypatch.setenv("MLFLOW_EXPERIMENT_NAME", "llmops-test")
    monkeypatch.setenv("GITHUB_ACCESS_TOKEN", "token")

    from app.core.config import Settings

    settings = Settings()

    assert settings.rag_manifest_url == "http://example.com/api/rag/manifest"
    assert settings.mlflow_tracking_uri == "https://dagshub.com/example/repo.mlflow"
    assert settings.mlflow_experiment_name == "llmops-test"
    assert settings.github_token == "token"
