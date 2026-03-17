import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
from box import ConfigBox
from box.exceptions import BoxValueError
from loguru import logger


def read_yaml(path: Path) -> ConfigBox:
    try:
        with open(path) as f:
            content = yaml.safe_load(f)
        if content is None:
            raise ValueError(f"yaml file is empty: {path}")
        logger.info(f"yaml loaded: {path}")
        return ConfigBox(content)
    except BoxValueError as e:
        raise ValueError(f"yaml file is invalid: {path}") from e


def save_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    logger.info(f"json saved: {path}")


def load_json(path: Path) -> ConfigBox:
    with open(path) as f:
        content = json.load(f)
    logger.info(f"json loaded: {path}")
    return ConfigBox(content)


def create_directories(paths: list[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"directory created: {path}")


def get_file_size(path: Path) -> str:
    size_bytes = path.stat().st_size
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    return f"{size_bytes / 1024 ** 3:.2f} GB"


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    logger.info(f"seed set: {seed}")