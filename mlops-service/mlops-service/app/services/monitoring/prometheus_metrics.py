from prometheus_client import Counter, Gauge, Histogram, start_http_server
from loguru import logger


TRAINING_RUNS_TOTAL = Counter(
    "retinaxai_training_runs_total",
    "Total number of training runs triggered",
    ["pipeline"],
)

ACTIVE_TRAINING_JOBS = Gauge(
    "retinaxai_active_training_jobs",
    "Number of currently running training jobs",
)

BEST_VAL_ACCURACY = Gauge(
    "retinaxai_best_val_accuracy",
    "Best validation accuracy from last training run",
    ["pipeline"],
)

QUADRATIC_WEIGHTED_KAPPA = Gauge(
    "retinaxai_quadratic_weighted_kappa",
    "Quadratic weighted kappa from last evaluation run",
    ["pipeline", "split"],
)

EPOCH_TRAIN_LOSS = Histogram(
    "retinaxai_epoch_train_loss",
    "Training loss per epoch",
    ["pipeline"],
    buckets=[0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0],
)

INFERENCE_LATENCY = Histogram(
    "retinaxai_inference_latency_seconds",
    "Inference request latency in seconds",
    ["model"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
)

DRIFT_DETECTED = Gauge(
    "retinaxai_drift_detected",
    "Whether drift was detected (1) or not (0)",
    ["pipeline"],
)

DRIFT_PSI_SCORE = Gauge(
    "retinaxai_drift_psi_score",
    "Population Stability Index (PSI) for drift detection",
    ["pipeline", "feature"],
)

AUTOMATION_SCHEDULER_RUNNING = Gauge(
    "retinaxai_automation_scheduler_running",
    "Whether automation scheduler is running (1) or not (0)",
)

TRAINING_REJECTIONS_TOTAL = Counter(
    "retinaxai_training_rejections_total",
    "Total number of training job rejections due to capacity limits",
    ["pipeline", "reason"],
)

TRAINING_SLOTS_USED = Gauge(
    "retinaxai_training_slots_used",
    "Number of training slots currently used",
    ["pipeline"],
)


def start_metrics_server(port: int = 9101) -> None:
    try:
        start_http_server(port)
        logger.info(f"prometheus metrics server started on port {port}")
    except OSError as e:
        logger.warning(f"Could not start metrics server on port {port}: {e}")
