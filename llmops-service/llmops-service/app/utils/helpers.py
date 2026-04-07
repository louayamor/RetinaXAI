from __future__ import annotations

import json
from typing import Any


def dump_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), default=str)


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())
