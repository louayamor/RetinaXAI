from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PipelineType(str, Enum):
    both = "both"
    imaging = "imaging"
    clinical = "clinical"


class TrainRequest(BaseModel):
    pipeline: PipelineType = PipelineType.both


class TrainResponse(BaseModel):
    job_id: str
    pipeline: str
    status: str
    message: str


class StatusResponse(BaseModel):
    job_id: Optional[str]
    pipeline: Optional[str]
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error: Optional[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ImagingMetrics(BaseModel):
    accuracy: Optional[float]
    quadratic_weighted_kappa: Optional[float]
    roc_auc_macro: Optional[float]
    num_samples: Optional[int]


class ClinicalMetrics(BaseModel):
    accuracy: Optional[float]
    quadratic_weighted_kappa: Optional[float]
    roc_auc_macro: Optional[float]
    num_samples: Optional[int]


class MetricsResponse(BaseModel):
    imaging: Optional[ImagingMetrics]
    clinical: Optional[ClinicalMetrics]


class ClinicalFeatures(BaseModel):
    patient_age: Optional[float] = None
    patient_gender: Optional[str] = None
    meta_eye: Optional[str] = None
    thickness_center_fovea: Optional[float] = None
    thickness_average_thickness: Optional[float] = None
    thickness_total_volume_mm3: Optional[float] = None
    thickness_inner_superior: Optional[float] = None
    thickness_inner_nasal: Optional[float] = None
    thickness_inner_inferior: Optional[float] = None
    thickness_inner_temporal: Optional[float] = None
    thickness_outer_superior: Optional[float] = None
    thickness_outer_nasal: Optional[float] = None
    thickness_outer_inferior: Optional[float] = None
    thickness_outer_temporal: Optional[float] = None
    clinical_edema: Optional[str] = None
    clinical_erm_status: Optional[str] = None
    meta_image_quality: Optional[str] = None


class MLPredictHttpRequest(BaseModel):
    model_name: str
    model_version: str
    patient_age: int
    patient_gender: str
    left_scan_path: Optional[str] = None
    right_scan_path: Optional[str] = None
    left_scan: str
    right_scan: str
    features: dict


class PredictResponse(BaseModel):
    prediction: dict = Field(
        description="Primary imaging prediction with clinical metadata"
    )
    confidence_score: float = Field(
        description="Confidence score from imaging model (0-1)"
    )
    model_name: str = Field(description="Model used for primary prediction")
    model_version: str = Field(description="Model version")
    gradcam_left: Optional[str] = Field(
        None, description="GradCAM heatmap for left eye (base64 PNG)"
    )
    gradcam_right: Optional[str] = Field(
        None, description="GradCAM heatmap for right eye (base64 PNG)"
    )
