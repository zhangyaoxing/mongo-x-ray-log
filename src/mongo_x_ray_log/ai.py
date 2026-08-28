"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.

AI analysis for the log plugin (warning / error / fatal log lines).

Uses the shared client in :mod:`mongo_x_ray.ai_client`.
"""

from __future__ import annotations

from mongo_x_ray.ai_client import complete

_SYSTEM_PROMPT = "You are a MongoDB expert. Analyze MongoDB log messages and tell me the reason in max 200 words."


def analyze_log_line_gpt(log_line: dict) -> str:
    """Analyze a MongoDB log line using the shared AI client."""
    result = complete(str(log_line), system=_SYSTEM_PROMPT)
    return (result or "").strip()
