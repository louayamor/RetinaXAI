from __future__ import annotations

import json
from pathlib import Path

from app.entity.ocr_schema import ClinicalFindings, OCTReport, PatientInfo, RegionImage, ReportMetadata, RetinalThickness
from app.pipeline.ocr_pipeline import OCRPipeline


def test_ocr_pipeline_export_uses_configured_paths(monkeypatch, tmp_path):
    input_dir = tmp_path / "ocr_reports"
    output_dir = tmp_path / "output"
    images_dir = tmp_path / "images"
    regions_config = {"fundus": {"rel": [0.0, 0.0, 1.0, 1.0]}}

    class DummyConfig:
        pass

    DummyConfig.input_dir = input_dir
    DummyConfig.output_dir = output_dir
    DummyConfig.json_output = output_dir / "reports.json"
    DummyConfig.csv_output = output_dir / "reports.csv"
    DummyConfig.images_dir = images_dir
    DummyConfig.regions_config = regions_config

    report = OCTReport(
        source_file="scan.jpg",
        metadata=ReportMetadata(device="Triton"),
        patient=PatientInfo(patient_id="123"),
        thickness=RetinalThickness(center_thickness=241.0),
        clinical=ClinicalFindings(npdr_grade="mild"),
        images={"fundus": RegionImage(png_path="/tmp/fundus.png", base64_png="abc")},
        raw_text="raw text",
        extraction_warnings=[],
    )

    pipeline = OCRPipeline.__new__(OCRPipeline)
    pipeline.config = DummyConfig()

    captured: dict[str, object] = {}

    def fake_write_text(_self, data: str) -> None:
        captured["json"] = json.loads(data)

    def fake_to_csv(self, path: Path, index: bool = False) -> None:
        captured["csv_path"] = str(path)
        captured["csv_index"] = index

    monkeypatch.setattr("app.pipeline.ocr_pipeline.pd.DataFrame.to_csv", fake_to_csv)
    monkeypatch.setattr(Path, "write_text", fake_write_text, raising=False)

    pipeline._export([report])

    assert captured["json"][0]["source_file"] == "scan.jpg"
    assert captured["csv_path"] == str(DummyConfig.csv_output)
    assert captured["csv_index"] is False


def test_ocr_pipeline_skips_existing_report(monkeypatch, tmp_path):
    pipeline = OCRPipeline.__new__(OCRPipeline)
    pipeline.config = type(
        "Cfg",
        (),
        {
            "images_dir": tmp_path / "images",
            "input_dir": tmp_path / "input",
            "regions_config": {},
            "output_dir": tmp_path / "output",
            "json_output": tmp_path / "output" / "reports.json",
            "csv_output": tmp_path / "output" / "reports.csv",
        },
    )()

    report_dir = pipeline.config.images_dir / "patient" / "OD" / "scan"
    report_dir.mkdir(parents=True)
    (report_dir / "existing.png").write_text("x")

    assert pipeline._is_report_processed("patient", "OD", "scan") is True
    assert pipeline._is_report_processed("patient", "OS", "scan") is False
