import numpy as np
from pathlib import Path
from app.components.ocr.region_detector import extract_regions

REGIONS_CONFIG = Path(__file__).parent.parent.parent / "config" / "regions.yaml"


def test_extract_regions_keys(dummy_image):
    crops = extract_regions(dummy_image, REGIONS_CONFIG)
    expected = {
        "fundus_infrared", "oct_bscan_horizontal", "etdrs_heatmap",
        "shadowgram", "retinal_thickness_map", "oct_bscan_vertical",
        "ilm_osrpe_3d_map", "osrpe_surface_3d",
    }
    assert set(crops.keys()) == expected


def test_extract_regions_nonzero(dummy_image):
    crops = extract_regions(dummy_image, REGIONS_CONFIG)
    for name, crop in crops.items():
        assert crop.size > 0, f"Empty crop: {name}"


def test_extract_regions_are_numpy_arrays(dummy_image):
    crops = extract_regions(dummy_image, REGIONS_CONFIG)
    for name, crop in crops.items():
        assert isinstance(crop, np.ndarray), f"Not ndarray: {name}"