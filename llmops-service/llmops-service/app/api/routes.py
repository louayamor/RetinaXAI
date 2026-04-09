from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.pipeline.indexing_pipeline import IndexingPipeline
from app.pipeline.inference_pipeline import InferencePipeline

router = APIRouter(prefix="/api", tags=["llmops"])


class GenerateRequest(BaseModel):
    model: str | None = None
    prompt: str | None = None
    stream: bool = False
    format: str | None = None
    patient: dict | None = None
    prediction: dict | None = None
    cleaned_summary: str = ""
    raw_ocr_text: str = ""
    report_type: str = Field(default="report")
    language: str = Field(default="en")
    tone: str = Field(default="clinical")


class RagStatusResponse(BaseModel):
    status: str
    schema_version: str | None = None
    run_id: str | None = None
    artifact_count: int = 0


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/generate")
async def generate(payload: GenerateRequest) -> dict[str, str]:
    try:
        pipeline = InferencePipeline()
        result = pipeline.generate_report(payload.model_dump())
        return {"response": json.dumps(result)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/rag/reindex")
def rag_reindex() -> dict[str, object]:
    result = IndexingPipeline().run()
    return {"status": "ok", "result": result}


@router.get("/rag/status", response_model=RagStatusResponse)
def rag_status() -> RagStatusResponse:
    result = IndexingPipeline().run()
    return RagStatusResponse(
        status="ok",
        schema_version=str(result.get("schema_version")) if result.get("schema_version") else None,
        run_id=str(result.get("run_id")) if result.get("run_id") else None,
        artifact_count=int(result.get("artifact_count") or 0),
    )
