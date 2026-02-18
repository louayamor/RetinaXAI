import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

BASE_DIR = Path("backend-service")

dirs = [
    "logs",
    "logs/system",
    "logs/auth",

    "app",
    "app/api",
    "app/api/routes",

    "app/core",
    "app/db",
    "app/models",
    "app/schemas",
    "app/services",
    "app/services/ml_client",
    "app/services/llm_client",

    "app/auth",
    "app/auth/jwt",
    "app/auth/dependencies",

    "app/patients",
    "app/users",
    "app/reports",

    "tests",
    "migrations",
    "config",
]

for d in dirs:
    path = BASE_DIR / d
    path.mkdir(parents=True, exist_ok=True)
    logging.info(f"Ensured directory: {path}")

files = [
    "app/__init__.py",
    "app/main.py",

    "app/core/config.py",
    "app/core/security.py",

    "app/db/base.py",
    "app/db/session.py",

    "app/models/__init__.py",
    "app/models/user.py",
    "app/models/patient.py",
    "app/models/report.py",

    "app/schemas/__init__.py",
    "app/schemas/user_schema.py",
    "app/schemas/patient_schema.py",
    "app/schemas/report_schema.py",

    "app/auth/jwt_handler.py",
    "app/auth/dependencies.py",

    "app/api/routes/auth_routes.py",
    "app/api/routes/user_routes.py",
    "app/api/routes/patient_routes.py",
    "app/api/routes/report_routes.py",

    "app/services/ml_client/ml_service.py",
    "app/services/llm_client/llm_service.py",

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
