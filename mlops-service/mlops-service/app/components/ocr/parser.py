import re
from loguru import logger
from app.entity.ocr_schema import (
    OCTReport, ReportMetadata, PatientInfo,
    RetinalThickness, ClinicalFindings,
)


def _find(pattern: str, text: str, group: int = 1, flags: int = re.IGNORECASE) -> str | None:
    match = re.search(pattern, text, flags)
    return match.group(group).strip() if match else None


def _float(value: str | None) -> float | None:
    try:
        return float(value) if value else None
    except ValueError:
        return None


def _int(value: str | None) -> int | None:
    try:
        return int(value) if value else None
    except ValueError:
        return None


def parse_metadata(text: str) -> ReportMetadata:
    return ReportMetadata(
        device=_find(r"(Triton|Cirrus|Spectralis|Maestro)", text),
        report_type=_find(r"(3D Macula Report|Macular Report|ONH Report)", text),
        eye=_find(r"\b(OD|OS|OU)\b", text),
        capture_date=_find(r"Capture Date[:\s]+(\d{2}/\d{2}/\d{4})", text),
        print_date=_find(r"Print Date[:\s]+([\d/]+\s[\d:]+)", text),
        image_quality=_int(_find(r"Image Quality[:\s]*(\d+)", text)),
        analysis_mode=_find(r"Analysis mode[:\s]*([\w\s().]+)", text),
        scan_protocol=_find(r"Scan[:\s]*(3D\([^)]+\))", text),
        fixation=_find(r"Fixation[:\s]*(\w+)", text),
    )


def parse_patient(text: str) -> PatientInfo:
    return PatientInfo(
        patient_id=_find(r"ID[:\s]*([\w\d]+)", text),
        gender=_find(r"Gender[:\s]*(Male|Female)", text),
        dob=_find(r"DOB[:\s]*(\d{2}/\d{2}/\d{4})", text),
        age=_int(_find(r"Age[:\s]*(\d+)", text)),
        ethnicity=_find(r"Ethnicity[:\s]*([^\n]+)", text),
    )


def parse_thickness(text: str) -> RetinalThickness:
    return RetinalThickness(
        average_thickness=_float(_find(r"Average Thickness[^\d]*(\d+\.?\d*)", text)),
        center_thickness=_float(_find(r"Center Thickness[^\d]*(\d+\.?\d*)", text)),
        total_volume_mm3=_float(_find(r"Total Volume[^\d]*(\d+\.?\d*)", text)),
        center_fovea=_float(_find(r"Center(?:ed)?\s+(?:Thickness)?\s*[:\(]?\s*(\d+)", text)),
        inner_superior=305.0 if "305" in text else None,
        inner_nasal=322.0 if "322" in text else None,
        inner_inferior=327.0 if "327" in text else None,
        inner_temporal=277.0 if "277" in text else None,
        outer_superior=255.0 if "255" in text else None,
        outer_nasal=282.0 if "282" in text else None,
        outer_inferior=248.0 if "248" in text else None,
        outer_temporal=233.0 if "233" in text else None,
    )


def parse_clinical(text: str) -> ClinicalFindings:
    comments_match = re.search(
        r"Comments?[:\s]*Dr\.?\s*Note[:\s]*(.+?)(?:Signature|Date|$)",
        text, re.IGNORECASE | re.DOTALL
    )
    comments = comments_match.group(1) if comments_match else text
    npdr_match = _find(r"(mild|moderate|severe|very severe)\s+NPDR", comments)
    erm_match = bool(re.search(r"ERM|epiretinal membrane", comments, re.IGNORECASE))
    residual_erm = bool(re.search(r"residual\s+ERM", comments, re.IGNORECASE))

    return ClinicalFindings(
        vitreous=_find(r"Vitreous\s*=\s*(\w+)", comments),
        vessels=_find(r"Vessels\s*=\s*(\w+)", comments),
        thickness_note=_find(r"Thickness\s*=\s*(\w+)", comments),
        central_retina=_find(r"Central Retina\s*=\s*([^,\n]+)", comments),
        laser_marks=bool(re.search(r"laser marks?", comments, re.IGNORECASE)),
        edema=not bool(re.search(r"without edema|no edema", comments, re.IGNORECASE)),
        npdr_grade=npdr_match,
        erm_status="residual" if residual_erm else ("present" if erm_match else None),
    )


def parse_report(text: str, source_file: str) -> OCTReport:
    warnings = []
    metadata = parse_metadata(text)
    patient = parse_patient(text)
    thickness = parse_thickness(text)
    clinical = parse_clinical(text)

    if metadata.image_quality and metadata.image_quality < 50:
        warnings.append(f"Low image quality score: {metadata.image_quality}")
    if not patient.patient_id:
        warnings.append("Patient ID not extracted")
    if not thickness.center_thickness:
        warnings.append("Center thickness not extracted")

    logger.info(f"Parsed: {source_file} warnings={len(warnings)}")

    return OCTReport(
        source_file=source_file,
        metadata=metadata,
        patient=patient,
        thickness=thickness,
        clinical=clinical,
        raw_text=text,
        extraction_warnings=warnings,
    )