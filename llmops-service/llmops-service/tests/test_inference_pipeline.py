from __future__ import annotations

import json
from typing import Any, cast

from app.core.config import LLMProvider
from app.llm.client import MockLLMClient
from app.pipeline.inference_pipeline import InferencePipeline


def test_inference_pipeline_uses_mock_client(monkeypatch):
    import app.pipeline.inference_pipeline as ip

    monkeypatch.setattr(ip.settings, "llm_provider", LLMProvider.MOCK)

    pipeline = cast(Any, InferencePipeline())
    assert isinstance(pipeline.client, MockLLMClient)


def test_generate_report_returns_required_keys(monkeypatch):
    from app.pipeline import inference_pipeline as ip
    from app.core.config import LLMProvider

    monkeypatch.setattr(ip.settings, "llm_provider", LLMProvider.MOCK)

    pipeline = cast(Any, InferencePipeline())
    result = pipeline.generate_report(
        {
            "patient": {"id": "P001", "age": 60},
            "prediction": {"grade": 1},
            "cleaned_summary": "No significant findings.",
            "raw_ocr_text": "",
            "report_type": "report",
            "language": "en",
            "tone": "clinical",
        }
    )

    assert "content" in result
    assert "summary" in result
    assert "model_used" in result


def test_generate_report_with_json_response(monkeypatch):
    import json
    from app.pipeline import inference_pipeline as ip
    from app.core.config import LLMProvider

    monkeypatch.setattr(ip.settings, "llm_provider", LLMProvider.MOCK)

    pipeline = cast(Any, InferencePipeline())

    def fake_generate(_prompt: str, _system_prompt=None) -> str:
        return json.dumps({"content": "Full report text.", "summary": "Short summary."})

    monkeypatch.setattr(pipeline.client, "generate", fake_generate)

    result = pipeline.generate_report({"report_type": "report"})
    assert result["content"] == "Full report text."
    assert result["summary"] == "Short summary."


def test_generate_report_with_plain_text_response(monkeypatch):
    from app.pipeline import inference_pipeline as ip
    from app.core.config import LLMProvider

    monkeypatch.setattr(ip.settings, "llm_provider", LLMProvider.MOCK)

    pipeline = InferencePipeline()

    plain_text = "This is a plain text report without JSON."

    def fake_generate(_prompt: str, _system_prompt=None) -> str:
        return plain_text

    monkeypatch.setattr(pipeline.client, "generate", fake_generate)

    result = pipeline.generate_report({"report_type": "report"})
    assert result["content"] == plain_text
    assert result["summary"] == plain_text[:400]
