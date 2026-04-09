from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def configure_mlflow() -> None:
    if not settings.mlflow_tracking_uri:
        return

    try:
        import dagshub
        import mlflow
    except ModuleNotFoundError:
        return

    dagshub.init(
        repo_owner="louayamor",
        repo_name="retinaxai",
        mlflow=True,
    )
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)


configure_mlflow()
app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(router)
