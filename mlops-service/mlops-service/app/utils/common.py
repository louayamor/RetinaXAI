import yaml
from pathlib import Path
from box import ConfigBox
from loguru import logger


def read_yaml(path: Path) -> ConfigBox:
    with open(path) as f:
        content = yaml.safe_load(f)
    logger.debug(f"YAML loaded: {path}")
    return ConfigBox(content)


def create_directories(paths: list[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory created: {path}")