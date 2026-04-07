import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s'
)

BASE_DIR = Path("llmops-service")

dirs = [
    "data",
    "data/cache",
    "app",
    "app/api",
    "app/core",
    "app/pipeline",
    "app/prompts",
    "app/vectorstore",
    "app/utils",
    "config",
    "tests",
]

for d in dirs:
    path = BASE_DIR / d
    path.mkdir(parents=True, exist_ok=True)
    logging.info(f"Ensured directory: {path}")

files = [
    "app/__init__.py",
    "app/main.py",

    "app/api/__init__.py",
    "app/api/routes.py",

    "app/core/__init__.py",
    "app/core/config.py",

    "app/pipeline/__init__.py",
    "app/pipeline/inference_pipeline.py",
    "app/pipeline/indexing_pipeline.py",

    "app/prompts/__init__.py",
    "app/prompts/templates.py",

    "app/vectorstore/__init__.py",
    "app/vectorstore/faiss_store.py",

    "app/utils/__init__.py",
    "app/utils/logger.py",
    "app/utils/helpers.py",

    "config/config.yaml",
    "config/params.yaml",

    "Dockerfile",
    "requirements.txt",
    "README.md",
]

for f in files:
    path = BASE_DIR / f
    if not path.exists():
        path.touch()
        logging.info(f"Created file: {path}")
    else:
        logging.info(f"File exists: {path}")
