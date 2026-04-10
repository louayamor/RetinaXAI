from __future__ import annotations

import json

from app.core.config import settings
from app.llm.client import get_llm_client
from app.prompts.templates import REPORT_SYSTEM_PROMPT, REPORT_USER_PROMPT
from app.utils.helpers import dump_compact
from app.vectorstore.chroma_store import ChromaStore


class InferencePipeline:
    def __init__(self) -> None:
        provider = settings.llm_provider.value if hasattr(settings.llm_provider, "value") else str(settings.llm_provider)
        token = settings.github_token if provider == "github" else settings.llm_api_key
        base_url = settings.github_endpoint if provider == "github" else settings.llm_base_url

        client_kwargs: dict[str, str] = {"model": settings.llm_model}
        if provider == "github":
            client_kwargs["token"] = token if token is not None else ""
            client_kwargs["endpoint"] = base_url if base_url is not None else ""
        elif provider == "ollama":
            client_kwargs["base_url"] = base_url if base_url is not None else settings.ollama_base_url
        else:
            client_kwargs["token"] = token if token is not None else ""
            client_kwargs["base_url"] = base_url if base_url is not None else ""

        self.client = get_llm_client(provider, **client_kwargs)
        self.store = ChromaStore(
            settings.rag_chroma_persist_directory,
            settings.rag_chroma_collection_name,
            settings.rag_embedding_model,
        )

    def _build_retrieval_context(self, payload: dict) -> str:
        parts = [payload.get("cleaned_summary", ""), payload.get("raw_ocr_text", "")]
        query = "\n".join(part for part in parts if part)
        if not query.strip():
            return ""

        try:
            results = self.store.query(query, top_k=4)
        except Exception:
            return ""

        if not results:
            return ""

        if isinstance(results, tuple):
            documents = results[0] or []
        else:
            documents = results[0] if isinstance(results, list) and results else []

        snippets = []
        for item in documents[:4]:
            doc = item[0] if isinstance(item, tuple) else item
            text = getattr(doc, "page_content", str(doc)).strip()
            metadata = getattr(doc, "metadata", {}) or {}
            if text:
                snippets.append(f"[source: {metadata.get('artifact_id', 'unknown')}] {text}")

        return "\n".join(snippets)

    def generate_report(self, payload: dict) -> dict[str, str]:
        model_name = str(payload.get("model") or settings.llm_model)
        retrieved_context = self._build_retrieval_context(payload)
        user_prompt = REPORT_USER_PROMPT.format(
            patient=dump_compact(payload.get("patient", {})),
            prediction=dump_compact(payload.get("prediction", {})),
            cleaned_summary=payload.get("cleaned_summary", ""),
            raw_ocr_text=payload.get("raw_ocr_text", ""),
            report_type=payload.get("report_type", "unknown"),
            language=payload.get("language", "en"),
            tone=payload.get("tone", "clinical"),
            retrieved_context=retrieved_context,
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
