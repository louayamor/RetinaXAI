from __future__ import annotations

import json

from app.core.config import settings
from app.llm.client import get_llm_client
from app.prompts.templates import REPORT_SYSTEM_PROMPT, REPORT_USER_PROMPT
from app.utils.helpers import dump_compact


class InferencePipeline:
    def __init__(self) -> None:
        provider = settings.llm_provider.value if hasattr(settings.llm_provider, "value") else str(settings.llm_provider)
        token = settings.github_token if provider == "github" else settings.llm_api_key
        base_url = settings.github_endpoint if provider == "github" else settings.llm_base_url

        client_kwargs = {"model": settings.llm_model}
        if provider == "github":
            client_kwargs["token"] = token or ""
            client_kwargs["endpoint"] = base_url or settings.github_endpoint
        elif provider == "ollama":
            client_kwargs["base_url"] = base_url or settings.ollama_base_url
        else:
            client_kwargs["token"] = token or ""
            client_kwargs["base_url"] = base_url or settings.llm_base_url or settings.github_endpoint

        self.client = get_llm_client(provider, **client_kwargs)

    def generate_report(self, payload: dict) -> dict[str, str]:
        model_name = str(payload.get("model") or settings.llm_model)
        user_prompt = REPORT_USER_PROMPT.format(
            patient=dump_compact(payload.get("patient") or {}),
            prediction=dump_compact(payload.get("prediction") or {}),
            cleaned_summary=str(payload.get("cleaned_summary") or ""),
            raw_ocr_text=str(payload.get("raw_ocr_text") or ""),
            report_type=str(payload.get("report_type") or "unknown"),
            language=str(payload.get("language") or "en"),
            tone=str(payload.get("tone") or "clinical"),
        )

        content = self.client.generate(user_prompt, REPORT_SYSTEM_PROMPT)
        parsed = None
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = None

        if isinstance(parsed, dict):
            report_content = str(parsed.get("content", content))
            summary = str(parsed.get("summary", report_content[:400]))
        else:
            report_content = content
            summary = content[:400]

        return {"content": report_content, "summary": summary, "model_used": model_name}
