from __future__ import annotations

import pytest

from app.schemas.report_schema import ReportGenerateRequest


def test_shared_report_fixture_matches_schema(report_generate_payload) -> None:
    data = ReportGenerateRequest.model_validate(report_generate_payload)

    assert data.prediction_id is not None


def test_shared_llm_payload_has_required_fields(llm_report_payload) -> None:
    assert llm_report_payload["patient"]
    assert llm_report_payload["cleaned_summary"]
    assert llm_report_payload["raw_ocr_text"]


@pytest.mark.asyncio
async def test_api_client_fixture_available(api_client) -> None:
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
