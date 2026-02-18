import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

BASE_DIR = Path("infra")

dirs = [
    "k8s",
    "nginx",
    "scripts"
]

for d in dirs:
    path = BASE_DIR / d
    path.mkdir(parents=True, exist_ok=True)
    logging.info(f"Ensured directory: {path}")

files = [
    "docker-compose.yml",
    ".env",

    "nginx/nginx.conf",

    "k8s/mlops-deployment.yaml",
    "k8s/llmops-deployment.yaml",
    "k8s/web-backend-deployment.yaml",
    "k8s/frontend-deployment.yaml",
    "k8s/services.yaml",
    "k8s/ingress.yaml",

    "scripts/setup_k8s.sh",
    "scripts/deploy.sh",
    
    "README.md"
]

for f in files:
    path = BASE_DIR / f
    if not path.exists():
        path.touch()
        logging.info(f"Created file: {path}")
    else:
        logging.info(f"File exists: {path}")
