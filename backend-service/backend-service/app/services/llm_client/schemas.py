from pydantic import BaseModel


class LLMReportRequest(BaseModel):
    patient_age: int
    patient_gender: str
    model_name: str
    model_version: str
    prediction_output: dict
    confidence_score: float


class LLMReportResponse(BaseModel):
    content: str
    summary: str
    model_used: str