"""
Operation state tracker for LLMOps service.
Tracks current operation: indexing, retrieval, generation.
"""

from threading import Lock
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

_operation_lock = Lock()
_current_operation: dict | None = None


@dataclass
class OperationState:
    state: Literal["idle", "indexing", "retrieving", "generating"]
    message: str
    progress: float | None = None
    started_at: str | None = None


def set_operation(state: str, message: str, progress: float | None = None):
    with _operation_lock:
        global _current_operation
        _current_operation = {
            "state": state,
            "message": message,
            "progress": progress,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }


def clear_operation():
    with _operation_lock:
        global _current_operation
        _current_operation = None


def get_operation() -> OperationState:
    with _operation_lock:
        if _current_operation is None:
            return OperationState(state="idle", message="Ready")
        return OperationState(**_current_operation)
