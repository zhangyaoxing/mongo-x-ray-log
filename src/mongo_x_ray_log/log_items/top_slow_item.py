"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.utils import json_hash
from mongo_x_ray_log.log_items.base_item import BaseItem
from mongo_x_ray_log.parsers.top_slow_parser import TopSlowParser
from mongo_x_ray_log.query_analyzer import analyze_query_pattern
from mongo_x_ray_log.rules.slow_operations_rule import SlowOperationsRule


class TopSlowItem(BaseItem):
    """
    Identify the top N slowest operations from the log entries.
    """

    def __init__(self, output_folder: str, config):
        super().__init__(output_folder, config)
        self._top_n = config.get("top", 10)
        self.name = "Top Slow Operations"
        self.description = f"Identify the top `{self._top_n}` slowest operations from the log entries."
        self._cache = {}
        self._rules["slow_operations"] = SlowOperationsRule(config)

    def analyze(self, log_line):
        log_id = log_line.get("id", "")
        if log_id != 51803:  # Slow query
            return
        attr = log_line.get("attr", {})
        ns = attr.get("ns", "")
        # Skip system namespaces and system.* collections
        if ns.startswith("admin.") or ns.startswith("local.") or ns.startswith("config.") or ".system." in ns:
            return
        duration = attr.get("durationMillis", 0)
        has_sort = attr.get("hasSortStage", False)
        query_hash = attr.get("queryHash", "")
        n_returned = attr.get("nreturned", 0)
        keys_examined = attr.get("keysExamined", 0)
        docs_examined = attr.get("docsExamined", 0)
        plan_summary = attr.get("planSummary", "")
        query_pattern = analyze_query_pattern(log_line)
        if query_pattern is None:
            return
        if query_hash == "":
            # Some command doesn't have queryHash, e.g., getMore
            # If so, we generate one based on the query shape and sort
            query_hash = json_hash(query_pattern, 4)
            # query_hash = query_pattern.get("hash", "N/A") if query_pattern else "N/A"
        slow_query = self._cache.get(query_hash, None)
        if slow_query is None:
            slow_query = {}
            self._cache[query_hash] = slow_query
        slow_query.update(
            {
                "query_hash": query_hash,
                "ns": ns,
                "query_pattern": query_pattern,
                "duration": slow_query.get("duration", 0) + duration,
                "n_returned": slow_query.get("n_returned", 0) + n_returned,
                "keys_examined": slow_query.get("keys_examined", 0) + keys_examined,
                "docs_examined": slow_query.get("docs_examined", 0) + docs_examined,
                "plan_summary": (plan_summary if "plan_summary" not in slow_query else slow_query["plan_summary"]),
                "has_sort": has_sort or slow_query.get("has_sort", False),
                "count": slow_query.get("count", 0) + 1,
                "sample": (log_line if "sample" not in slow_query else slow_query["sample"]),
            }
        )

    def finalize_analysis(self):
        self._cache = list(sorted(self._cache.values(), key=lambda item: item["count"], reverse=True)[: self._top_n])
        # self._cache = list(sorted(self._cache.values(), key=lambda item: item["duration"], reverse=True)[:self._top_n])
        super().finalize_analysis()
        # Apply the rules to generate the test results (e.g. collection scans, poor query targeting).
        for rule in self._rules.values():
            test_result, _ = rule.apply(self._cache, extra_info={"host": self._hostname or "unknown"})
            self.append_test_results(test_result)

    def review_results_markdown(self, f):
        parser = TopSlowParser()
        f.write(parser.markdown(self._load_records()))
