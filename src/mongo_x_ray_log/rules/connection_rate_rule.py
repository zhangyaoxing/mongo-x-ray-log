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

DEFAULT_MEDIUM_RATIO = 0.5
DEFAULT_HIGH_RATIO = 0.75


class ConnectionRateRule(BaseRule):
    """Checks the connection rate buckets for connection churn.

    When, within one minute, the number of connections created (or ended) reaches
    a large fraction of the server's current total connections, the pool is
    churning: MEDIUM at/above the ``connection_rate_medium`` ratio, HIGH at/above
    the ``connection_rate_high`` ratio.
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._medium_ratio = self._thresholds.get("connection_rate_medium", DEFAULT_MEDIUM_RATIO)
        self._high_ratio = self._thresholds.get("connection_rate_high", DEFAULT_HIGH_RATIO)
        self._rule_desc.append("Checks if connections are churning faster than the configured ratio.")

    def apply(self, data: list, **kwargs) -> tuple:
        """Check the per-minute connection rate buckets for churn.

        Args:
            data (list): The connection rate buckets, a list of dicts with
                ``time``, ``created``, ``ended`` and ``total`` keys.
            extra_info (dict, optional): Additional information such as ``host``.

        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        test_results = []
        for bucket in data:
            total = bucket.get("total", 0)
            if total <= 0:
                continue
            created = bucket.get("created", 0)
            ended = bucket.get("ended", 0)
            created_ratio = created / total
            ended_ratio = ended / total
            ratio = max(created_ratio, ended_ratio)
            if ratio >= self._high_ratio:
                severity = SEVERITY.HIGH
                wording = f"at or above the critical ratio `{self._high_ratio:.0%}`"
            elif ratio >= self._medium_ratio:
                severity = SEVERITY.MEDIUM
                wording = f"at or above the ratio `{self._medium_ratio:.0%}`"
            else:
                continue
            if created_ratio >= ended_ratio:
                action = f"{created} connections were created"
                action_ratio = f"{created_ratio:.0%}"
            else:
                action = f"{ended} connections were ended"
                action_ratio = f"{ended_ratio:.0%}"
            test_results.append(
                {
                    "host": host,
                    "severity": severity,
                    "title": "High Connection Churn",
                    "description": (
                        f"In one minute, {action} out of `{total}` total connections "
                        f"({action_ratio} of the current total), which is {wording}. "
                        "This may indicate a client repeatedly opening and closing connections."
                    ),
                }
            )
        return test_results, data


__all__ = ["ConnectionRateRule"]
