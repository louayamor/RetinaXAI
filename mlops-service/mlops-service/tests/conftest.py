from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def sample_text() -> str:
    return """
    3D Macula Report    Triton    Print Date: 15/03/2026 11:10:55
    ID: 849x    Gender: Male    DOB: 01/01/1956    Age: 70
    OD(R)    Image Quality: 64    Analysis mode: Fine (2.0.7)
    Capture Date: 14/01/2026    Fixation: Macula
    Scan: 3D(7.0x7.0mm - 512x256)
    Average Thickness (um) 267.2
    Center Thickness (um) 241
    Total Volume (mm3) 7.55
    Comments: Dr Note: Vitreous = Normal, Vessels = Normal,
    Thickness = Normal, Central Retina = flat retina under SF6 gas,
    360 degree laser marks, without edema, mild NPDR, residual ERM
    """


@pytest.fixture
def dummy_image() -> np.ndarray:
    return np.zeros((1000, 1280, 3), dtype=np.uint8)


@pytest.fixture
def temp_input_dir(tmp_path: Path) -> Path:
    path = tmp_path / "input"
    path.mkdir()
    return path


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    path = tmp_path / "output"
    path.mkdir()
    return path


@pytest.fixture
def temp_images_dir(tmp_path: Path) -> Path:
    path = tmp_path / "images"
    path.mkdir()
    return path
