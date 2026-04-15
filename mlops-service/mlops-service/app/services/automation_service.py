import threading
import time
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from app.services.training_service import create_job, run_pipeline_task
from app.services.drift_detection import DriftDetectionService, DriftStatus
from monitoring.prometheus_metrics import AUTOMATION_SCHEDULER_RUNNING


class AutomationService:
    def __init__(self, artifacts_root, reports_dir):
        self._lock = threading.Lock()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_run: dict[str, str] = {}
        self._artifacts_root = artifacts_root
        self._reports_dir = reports_dir
        self._drift_service = DriftDetectionService(
            artifacts_root=artifacts_root,
            reports_dir=reports_dir,
        )

    def start_scheduler(self, interval_hours: int = 24) -> None:
        with self._lock:
            if self._running:
                logger.info("Automation scheduler already running")
                return
            self._running = True
            self._scheduler_thread = threading.Thread(
                target=self._run_loop,
                args=(interval_hours,),
                daemon=True,
            )
            self._scheduler_thread.start()
            AUTOMATION_SCHEDULER_RUNNING.set(1)
            logger.info(f"Automation scheduler started: interval={interval_hours}h")

    def stop_scheduler(self) -> None:
        with self._lock:
            self._running = False
            AUTOMATION_SCHEDULER_RUNNING.set(0)
            logger.info("Automation scheduler stopped")

    def _run_loop(self, interval_hours: int) -> None:
        while self._running:
            try:
                self._run_scheduled_jobs()
            except Exception as e:
                logger.warning(f"Automation scheduler error: {e}")
            time.sleep(interval_hours * 3600)

    def _run_scheduled_jobs(self) -> None:
        now = datetime.utcnow()
        last_run_time = self._last_run.get("scheduled")
        if last_run_time:
            last_run = datetime.fromisoformat(last_run_time)
            if now - last_run < timedelta(hours=23):
                return

        logger.info("Running scheduled retraining job")
        job_id = create_job("both")
        threading.Thread(
            target=run_pipeline_task,
            args=(job_id, "both"),
            daemon=True,
        ).start()
        self._last_run["scheduled"] = now.isoformat()

    def trigger_drift_retraining(
        self,
        reference_csv,
        current_csv,
        pipeline: str = "both",
        psi_threshold: float = 0.3,
    ) -> dict:
        report = self._drift_service.check_drift(
            reference_csv=reference_csv,
            current_csv=current_csv,
            pipeline=pipeline,
        )

        if (
            report.status == DriftStatus.DRIFT_DETECTED
            and report.overall_psi >= psi_threshold
        ):
            logger.info(
                f"Drift detected (psi={report.overall_psi:.4f}), triggering retraining"
            )
            job_id = create_job(pipeline)
            threading.Thread(
                target=run_pipeline_task,
                args=(job_id, pipeline),
                daemon=True,
            ).start()
            return {
                "status": "retraining_triggered",
                "job_id": job_id,
                "psi": report.overall_psi,
            }

        return {
            "status": "no_retraining",
            "psi": report.overall_psi,
        }


_automation_service: Optional[AutomationService] = None


def get_automation_service(artifacts_root, reports_dir) -> AutomationService:
    global _automation_service
    if _automation_service is None:
        _automation_service = AutomationService(artifacts_root, reports_dir)
    return _automation_service
