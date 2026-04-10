import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.prediction import Prediction, PredictionStatus
from app.mri_scans.repository import MRIScanRepository
from app.patients.repository import PatientRepository
from app.predictions.repository import PredictionRepository
from app.schemas.prediction_schema import PredictionRequest
from app.services.ml_client.ml_service import ml_client
from app.services.ml_client.schemas import MLPredictRequest


class PredictionService:
    def __init__(self, db: AsyncSession):
        self.repo = PredictionRepository(db)
        self.patient_repo = PatientRepository(db)
        self.mri_scan_repo = MRIScanRepository(db)

    async def run(self, data: PredictionRequest, requested_by: uuid.UUID) -> Prediction:
        patient = await self.patient_repo.get_by_id(data.patient_id)
        if not patient:
            raise NotFoundException("Patient", data.patient_id)  # type: ignore[reportArgumentType]

        scan = await self.mri_scan_repo.get_by_id(data.mri_scan_id)
        if not scan:
            raise NotFoundException("MRIScan", data.mri_scan_id)  # type: ignore[reportArgumentType]

        prediction = Prediction(
            patient_id=data.patient_id,
            mri_scan_id=data.mri_scan_id,
            requested_by=requested_by,
            model_name=data.model_name,
            model_version=data.model_version,
            input_payload=data.input_payload,
            status=PredictionStatus.PENDING,
        )
        prediction = await self.repo.create(prediction)

        try:
            ml_request = MLPredictRequest(
                model_name=data.model_name,
                model_version=data.model_version,
                patient_age=patient.age,
                patient_gender=patient.gender.value,
                left_scan_path=scan.left_scan_path,
                right_scan_path=scan.right_scan_path,
                features=data.input_payload,
            )
            ml_response = await ml_client.predict(ml_request)
            prediction.output_payload = ml_response.prediction
            prediction.confidence_score = ml_response.confidence_score
            prediction.status = PredictionStatus.SUCCESS
        except Exception as e:
            prediction.status = PredictionStatus.FAILED
            prediction.error_message = str(e)

        return await self.repo.update(prediction)

    async def get_by_id(self, prediction_id: uuid.UUID) -> Prediction:
        prediction = await self.repo.get_by_id(prediction_id)
        if not prediction:
            raise NotFoundException("Prediction", prediction_id)  # type: ignore[reportArgumentType]
        return prediction

    async def get_by_patient(
        self, patient_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> tuple[list[Prediction], int]:
        predictions = await self.repo.get_by_patient(patient_id, skip, limit)
        total = await self.repo.count_by_patient(patient_id)
        return predictions, total

    async def get_all(
        self, skip: int = 0, limit: int = 20
    ) -> tuple[list[Prediction], int]:
        predictions = await self.repo.get_all(skip, limit)
        total = await self.repo.count_all()
        return predictions, total