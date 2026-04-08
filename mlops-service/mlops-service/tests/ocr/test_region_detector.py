import numpy as np
from app.components.ocr.region_detector import extract_regions


def test_extract_regions_keys(dummy_image, regions_config):
    crops = extract_regions(dummy_image, regions_config)
    expected = {
        "fundus_infrared", "oct_bscan_horizontal", "etdrs_heatmap",
        "shadowgram", "retinal_thickness_map", "oct_bscan_vertical",
        "ilm_osrpe_3d_map", "osrpe_surface_3d",
    }
    assert set(crops.keys()) == expected


def test_extract_regions_nonzero(dummy_image, regions_config):
    crops = extract_regions(dummy_image, regions_config)
    for name, crop in crops.items():
        assert crop.size > 0, f"Empty crop: {name}"


def test_extract_regions_are_numpy_arrays(dummy_image, regions_config):
    crops = extract_regions(dummy_image, regions_config)
    for name, crop in crops.items():
        assert isinstance(crop, np.ndarray), f"Not ndarray: {name}"
