import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

GRADE_LABELS = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnprocessableEntityException,
)
from app.models.prediction import PredictionStatus
from app.models.report import Report, ReportStatus
from app.patients.repository import PatientRepository
from app.predictions.repository import PredictionRepository
from app.reports.repository import ReportRepository
from app.schemas.report_schema import ReportGenerateRequest
from app.services.llm_client.llm_service import llm_client
from app.services.llm_client.schemas import LLMReportRequest


class ReportService:
    def __init__(self, db: AsyncSession):
        self.repo = ReportRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.patient_repo = PatientRepository(db)
        self.db = db

    async def generate(
        self, data: ReportGenerateRequest, generated_by: uuid.UUID
    ) -> Report:
        prediction = await self.prediction_repo.get_by_id(data.prediction_id)
        if not prediction:
            raise NotFoundException("Prediction", data.prediction_id)  # type: ignore[reportArgumentType]

        if prediction.status != PredictionStatus.SUCCESS:
            raise UnprocessableEntityException(
                "Cannot generate a report for a prediction that did not succeed."
            )

        existing = await self.repo.get_by_prediction_id(data.prediction_id)
        if existing:
            if existing.status == ReportStatus.FAILED:
                await self.db.delete(existing)
                await self.db.flush()
            else:
                raise ConflictException("A report for this prediction already exists.")

        patient = await self.patient_repo.get_by_id(prediction.patient_id)
        if not patient:
            raise NotFoundException("Patient", prediction.patient_id)  # type: ignore[reportArgumentType]

        report = Report(
            patient_id=prediction.patient_id,
            prediction_id=data.prediction_id,
            generated_by=generated_by,
            llm_model=settings.LLM_MODEL,
            status=ReportStatus.GENERATING,
        )
        report = await self.repo.create(report)

        try:
            cleaned_summary = ""
            output_payload = prediction.output_payload or {}

            cleaned_summary = str(
                output_payload.get("summary")
                or output_payload.get("description")
                or output_payload.get("dr_grade", "")
            )

            combined_grade = output_payload.get("combined_grade")
            predicted_class = output_payload.get("predicted_class")
            grade_text = (
                GRADE_LABELS[combined_grade]
                if combined_grade is not None
                else predicted_class or "Unknown"
            )

            prediction_summary = {
                "id": str(prediction.id),
                "model_name": prediction.model_name,
                "model_version": prediction.model_version,
                "confidence_score": prediction.confidence_score,
                "status": prediction.status.value,
                "dr_grade": grade_text,
                "severity": output_payload.get("overall_severity", "unknown"),
            }

            llm_request = LLMReportRequest(
                patient={
                    "id": str(patient.id),
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "age": patient.age,
                    "gender": patient.gender.value,
                    "medical_record_number": patient.medical_record_number,
                },
                prediction=prediction_summary,
                cleaned_summary=cleaned_summary,
                raw_ocr_text="",
                report_type="prediction",
                model_name=prediction.model_name,
                model_version=prediction.model_version,
                prediction_output=prediction_summary,
                confidence_score=prediction.confidence_score
                if prediction.confidence_score is not None
                else 0.0,
            )
            llm_response = await llm_client.generate_report(llm_request)
            report.content = llm_response.content
            report.summary = llm_response.summary
            report.llm_model = llm_response.model_used
            report.status = ReportStatus.COMPLETED
        except Exception as e:
            report.status = ReportStatus.FAILED
            report.error_message = str(e)

        return await self.repo.update(report)

    async def get_by_id(self, report_id: uuid.UUID) -> Report:
        report = await self.repo.get_by_id(report_id)
        if not report:
            raise NotFoundException("Report", report_id)  # type: ignore[reportArgumentType]
        return report

    async def get_by_patient(
        self, patient_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> tuple[list[Report], int]:
        reports = await self.repo.get_by_patient(patient_id, skip, limit)
        total = await self.repo.count_by_patient(patient_id)
        return reports, total

    async def get_all(self, skip: int = 0, limit: int = 20) -> tuple[list[Report], int]:
        reports = await self.repo.get_all(skip, limit)
        total = await self.repo.count_all()
        return reports, total
