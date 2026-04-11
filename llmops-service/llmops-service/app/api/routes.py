"""
API Routes for LLMOps Service.

Includes synchronous and asynchronous report generation,
job status tracking, and RAG management.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import settings
from app.pipeline.indexing_pipeline import IndexingPipeline
from app.pipeline.inference_pipeline import InferencePipeline
from app.services.operation_state import get_operation
from app.services.job_manager import JobStatus, get_job_manager
from app.vectorstore.chroma_store import ChromaStore

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
    collection_name: str | None = None
    persist_directory: str | None = None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/generate")
async def generate(payload: GenerateRequest) -> dict[str, str]:
    """
    Synchronous report generation.

    Returns the report immediately. Use for quick generation.
    For long-running reports, use /generate/async instead.
    """
    try:
        pipeline = InferencePipeline()
        result = pipeline.generate_report(payload.model_dump())
        return {"response": json.dumps(result)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/generate/async")
async def generate_async(payload: GenerateRequest) -> dict[str, str]:
    """
    Asynchronous report generation.

    Submits a job and returns immediately with a job ID.
    Poll /jobs/{job_id} to check status.
    """
    job_manager = get_job_manager()
    job_id = await job_manager.submit(
        job_type="report_generation",
        payload=payload.model_dump(),
        max_retries=3,
    )
    return {"job_id": job_id, "status": "pending"}


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    job_type: str
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    result: dict | None = None
    error: str | None = None
    retry_count: int


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the status of an async report generation job.
    """
    job_manager = get_job_manager()
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatusResponse(
        job_id=job.id,
        status=job.status.value,
        job_type=job.job_type,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        result=job.result,
        error=job.error,
        retry_count=job.retry_count,
    )


@router.get("/jobs")
def list_jobs(
    status: str | None = Query(
        None, description="Filter by status: pending, running, completed, failed"
    ),
    limit: int = Query(100, ge=1, le=1000),
) -> dict:
    """
    List recent report generation jobs.
    """
    job_manager = get_job_manager()

    status_filter = None
    if status:
        try:
            status_filter = JobStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    jobs = job_manager.get_jobs(status=status_filter, limit=limit)

    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": j.id,
                "status": j.status.value,
                "job_type": j.job_type,
                "created_at": j.created_at.isoformat(),
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
    }


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str) -> dict:
    """
    Cancel a pending or running job.
    """
    job_manager = get_job_manager()
    result = await job_manager.cancel_job(job_id)

    if not result:
        raise HTTPException(status_code=400, detail=f"Job {job_id} cannot be cancelled")

    return {"job_id": job_id, "status": "cancelled"}


@router.post("/rag/reindex")
def rag_reindex() -> dict[str, object]:
    result = IndexingPipeline().run()
    return {"status": "ok", "result": result}


@router.get("/rag/status", response_model=RagStatusResponse)
def rag_status() -> RagStatusResponse:
    store = ChromaStore(
        settings.rag_chroma_persist_directory,
        settings.rag_chroma_collection_name,
        settings.rag_embedding_model,
    )
    state = store.read_state() or {}
    return RagStatusResponse(
        status="ok" if state else "idle",
        schema_version=str(state.get("schema_version"))
        if state.get("schema_version")
        else None,
        run_id=str(state.get("run_id")) if state.get("run_id") else None,
        artifact_count=int(state.get("artifact_count") or 0),
        collection_name=store.collection_name,
        persist_directory=str(store.persist_directory),
    )


@router.get("/operation/status")
def operation_status() -> dict:
    op = get_operation()
    return {
        "state": op.state,
        "message": op.message,
        "progress": op.progress,
        "started_at": op.started_at,
    }
