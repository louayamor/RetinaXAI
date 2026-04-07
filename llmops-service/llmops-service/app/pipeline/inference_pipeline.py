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
            client_kwargs["token"] = token
            client_kwargs["endpoint"] = base_url
        elif provider == "ollama":
            client_kwargs["base_url"] = base_url or settings.ollama_base_url
        else:
            client_kwargs["token"] = token
            client_kwargs["base_url"] = base_url

        self.client = get_llm_client(provider, **client_kwargs)

    def generate_report(self, payload: dict) -> dict[str, str]:
        model_name = str(payload.get("model") or settings.llm_model)
        user_prompt = REPORT_USER_PROMPT.format(
            patient=dump_compact(payload.get("patient", {})),
            prediction=dump_compact(payload.get("prediction", {})),
            cleaned_summary=payload.get("cleaned_summary", ""),
            raw_ocr_text=payload.get("raw_ocr_text", ""),
            report_type=payload.get("report_type", "unknown"),
            language=payload.get("language", "en"),
            tone=payload.get("tone", "clinical"),
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
