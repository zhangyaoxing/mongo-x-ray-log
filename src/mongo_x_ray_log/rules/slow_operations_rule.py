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

DEFAULT_QUERY_TARGETING = 1000


class SlowOperationsRule(BaseRule):
    """Checks the aggregated top slow operations for common performance problems.

    Flags slow operations that:
    - use a collection scan (``planSummary`` is ``COLLSCAN``) — HIGH,
    - scan more than the configured threshold documents/keys per returned
      document (poor query targeting) — MEDIUM.
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._max_query_targeting = self._thresholds.get("query_targeting", DEFAULT_QUERY_TARGETING)
        self._max_query_targeting_obj = self._thresholds.get("query_targeting_obj", DEFAULT_QUERY_TARGETING)
        self._rule_desc.append("Checks if slow operations use collection scans (COLLSCAN).")
        self._rule_desc.append("Checks if the query targeting of slow operations is too high.")

    def apply(self, data: list, **kwargs) -> tuple:
        """Check the aggregated top slow operations for issues.

        Args:
            data (list): The top slow operation records, a list of dicts with
                ``ns``, ``query_hash``, ``plan_summary``, ``keys_examined``,
                ``docs_examined``, ``n_returned`` and ``count`` keys.
            extra_info (dict, optional): Additional information such as ``host``.

        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        test_results = []
        for record in data:
            ns = record.get("ns", "unknown")
            query_hash = record.get("query_hash", "N/A")
            plan_summary = record.get("plan_summary", "")
            # 1. Collection scans are a HIGH severity issue
            if plan_summary and plan_summary.startswith("COLLSCAN"):
                test_results.append(
                    {
                        "host": host,
                        "severity": SEVERITY.HIGH,
                        "title": "Collection Scan Detected",
                        "description": (
                            f"Slow operation `{query_hash}` on `{ns}` uses a collection scan "
                            f"(plan summary: `COLLSCAN`) instead of an index. "
                            "Consider adding an index to support the query."
                        ),
                    }
                )
            # 2. Poor query targeting is a MEDIUM severity issue
            n_returned = record.get("n_returned", 0)
            keys_examined = record.get("keys_examined", 0)
            docs_examined = record.get("docs_examined", 0)
            scanned_per_returned = round(keys_examined / n_returned, 2) if n_returned > 0 else keys_examined
            scannedobj_per_returned = round(docs_examined / n_returned, 2) if n_returned > 0 else docs_examined
            if scanned_per_returned >= self._max_query_targeting:
                test_results.append(
                    {
                        "host": host,
                        "severity": SEVERITY.MEDIUM,
                        "title": "Poor Query Targeting",
                        "description": (
                            f"Slow operation `{query_hash}` on `{ns}` has a scanned/returned ratio of "
                            f"`{scanned_per_returned}`, which is at or above the threshold "
                            f"`{self._max_query_targeting}`. Consider adding an index to support the query."
                        ),
                    }
                )
            if scannedobj_per_returned >= self._max_query_targeting_obj:
                test_results.append(
                    {
                        "host": host,
                        "severity": SEVERITY.MEDIUM,
                        "title": "Poor Query Targeting (Objects)",
                        "description": (
                            f"Slow operation `{query_hash}` on `{ns}` has a scanned objects/returned ratio of "
                            f"`{scannedobj_per_returned}`, which is at or above the threshold "
                            f"`{self._max_query_targeting_obj}`. Consider adding an index to support the query."
                        ),
                    }
                )
        return test_results, data


__all__ = ["SlowOperationsRule"]
