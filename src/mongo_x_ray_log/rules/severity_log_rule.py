"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from typing import Optional

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.rules.base_rule import BaseRule


class SeverityLogRule(BaseRule):
    """Checks the W/E/F log entries for warning- and fatal-severity messages."""

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._rule_desc.append("Checks if there are any warning-level log messages.")
        self._rule_desc.append("Checks if there are any fatal-level log messages.")

    def apply(self, data: list, **kwargs) -> tuple:
        """Raise an issue when warning or fatal log entries are present.

        Args:
            data (list): The W/E/F log entries, a list of dicts with a
                ``severity`` key (``w`` / ``e`` / ``f``).
            extra_info (dict, optional): Additional information such as ``host``.

        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        warnings = [entry for entry in data if (entry.get("severity", "") or "").lower() == "w"]
        fatals = [entry for entry in data if (entry.get("severity", "") or "").lower() == "f"]
        test_results = []
        if warnings:
            test_results.append(
                {
                    "host": host,
                    "severity": SEVERITY.MEDIUM,
                    "title": "Warning Logs Detected",
                    "description": (
                        f"The log contains `{len(warnings)}` warning log entr{'y' if len(warnings) == 1 else 'ies'}. "
                        "Review the Warning/Error/Fatal Logs section for details."
                    ),
                }
            )
        if fatals:
            test_results.append(
                {
                    "host": host,
                    "severity": SEVERITY.HIGH,
                    "title": "Fatal Logs Detected",
                    "description": (
                        f"The log contains `{len(fatals)}` fatal log entr{'y' if len(fatals) == 1 else 'ies'}. "
                        "Review the Warning/Error/Fatal Logs section for details."
                    ),
                }
            )
        return test_results, data


__all__ = ["SeverityLogRule"]
