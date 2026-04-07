from app.components.ocr.parser import parse_metadata, parse_patient, parse_thickness, parse_clinical


def test_parse_metadata(sample_text):
    meta = parse_metadata(sample_text)
    assert meta.device == "Triton"
    assert meta.eye == "OD"
    assert meta.image_quality == 64
    assert meta.capture_date == "14/01/2026"


def test_parse_patient(sample_text):
    patient = parse_patient(sample_text)
    assert patient.gender == "M"
    assert patient.age == 70
    assert patient.dob == "01/01/1956"


def test_parse_thickness(sample_text):
    thickness = parse_thickness(sample_text)
    assert thickness.average_thickness == 267.2
    assert thickness.center_thickness == 241.0
    assert thickness.total_volume_mm3 == 7.55


def test_parse_clinical(sample_text):
    clinical = parse_clinical(sample_text)
    assert clinical.vitreous == "Normal"
    assert not clinical.edema
    assert clinical.npdr_grade == "mild"
    assert clinical.erm_status == "residual"
    assert clinical.laser_marks
