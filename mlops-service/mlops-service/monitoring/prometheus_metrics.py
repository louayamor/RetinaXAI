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


def start_metrics_server(port: int = 9090) -> None:
    start_http_server(port)
    logger.info(f"prometheus metrics server started on port {port}")