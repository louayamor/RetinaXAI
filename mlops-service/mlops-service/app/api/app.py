from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import (
    health,
    train,
    status,
    metrics,
    predict,
    rag,
    models,
    drift,
)  # reports temporarily disabled
from app.api.dependencies import get_settings
from monitoring.prometheus_metrics import start_metrics_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"starting {settings.app_name} v{settings.app_version}")
    logger.info(f"environment: {settings.app_env}")
    start_metrics_server(port=settings.prometheus_metrics_port)
    yield
    logger.info("shutting down mlops service")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])  # type: ignore[arg-type]
    app.include_router(train.router, tags=["training"])  # type: ignore[arg-type]
    app.include_router(status.router, tags=["status"])  # type: ignore[arg-type]
    app.include_router(metrics.router, tags=["metrics"])  # type: ignore[arg-type]
    app.include_router(predict.router, tags=["predict"])  # type: ignore[arg-type]
    app.include_router(rag.router, tags=["rag"])  # type: ignore[arg-type]
    app.include_router(models.router, tags=["models"])  # type: ignore[arg-type]
    app.include_router(drift.router, tags=["drift"])  # type: ignore[arg-type]
    # app.include_router(reports.router, tags=["monitoring"]) # temporarily disabled (evidently dep conflict)

    return app


app = create_app()
