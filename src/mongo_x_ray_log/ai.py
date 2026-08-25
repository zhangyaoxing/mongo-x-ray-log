"""AI analysis for the log plugin (warning / error / fatal log lines).

Uses the shared client in :mod:`mongo_x_ray.ai_client`.
"""

from __future__ import annotations

import logging

from mongo_x_ray.ai_client import complete

_logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = "You are a MongoDB expert. Analyze MongoDB log messages and tell me the reason in max 200 words."


def analyze_log_line_gpt(log_line: dict) -> str:
    """Analyze a MongoDB log line using the shared AI client."""
    result = complete(str(log_line), system=_SYSTEM_PROMPT)
    return (result or "").strip()
