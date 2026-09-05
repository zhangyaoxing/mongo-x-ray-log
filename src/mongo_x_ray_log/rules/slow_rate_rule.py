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

DEFAULT_MEDIUM_MS = 100
DEFAULT_HIGH_MS = 500


class SlowRateRule(BaseRule):
    """Checks the per-minute slow query rate for significant slow queries.

    When the average duration of the slow queries in a minute is more than the
    configured thresholds, an issue is raised: MEDIUM above
    ``slow_rate_medium`` ms, HIGH above ``slow_rate_high`` ms.
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._medium_ms = self._thresholds.get("slow_rate_medium", DEFAULT_MEDIUM_MS)
        self._high_ms = self._thresholds.get("slow_rate_high", DEFAULT_HIGH_MS)
        self._rule_desc.append("Checks if the average slow query duration per minute is too high.")

    def apply(self, data: list, **kwargs) -> tuple:
        """Check the per-minute slow rate buckets.

        Args:
            data (list): The slow rate buckets, a list of dicts with ``time``,
                ``total_slow_ms`` and ``count`` keys.
            extra_info (dict, optional): Additional information such as ``host``.

        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        test_results = []
        for bucket in data:
            count = bucket.get("count", 0)
            if count <= 0:
                continue
            avg_ms = bucket.get("total_slow_ms", 0) / count
            if avg_ms > self._high_ms:
                severity = SEVERITY.HIGH
                wording = f"more than the critical threshold `{self._high_ms} ms`"
            elif avg_ms > self._medium_ms:
                severity = SEVERITY.MEDIUM
                wording = f"more than the threshold `{self._medium_ms} ms`"
            else:
                continue
            test_results.append(
                {
                    "host": host,
                    "severity": severity,
                    "title": "Significant Slow Queries",
                    "description": (
                        f"At {bucket.get('time', 'unknown')}, the average slow query duration is "
                        f"`{avg_ms:.2f} ms` over `{count}` slow queries, which is {wording}."
                    ),
                }
            )
        return test_results, data


__all__ = ["SlowRateRule"]
