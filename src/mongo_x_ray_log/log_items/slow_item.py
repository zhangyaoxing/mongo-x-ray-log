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
from mongo_x_ray_log.parsers.slow_parser import SlowParser
from mongo_x_ray_log.query_analyzer import analyze_query_pattern
from mongo_x_ray_log.rules.slow_operations_rule import SlowOperationsRule


class SlowItem(BaseItem):
    """Analyse the slow operations from the log entries.

    Aggregates the top-N slowest query patterns (shown as a table with sample
    viewers and checked by the slow operations rules) and keeps every raw slow
    query line for the scatter charts (duration / scanned / scanned objects).
    """

    def __init__(self, output_folder: str, config):
        super().__init__(output_folder, config, show_reset=True)
        self._top_n = config.get("top", 10)
        self._patterns: dict = {}
        self._cache = None  # scratch buffer used to stream raw lines to the output file
        self.name = "Slow Operations"
        self.description = f"Identify the top `{self._top_n}` slowest operations and chart them over time."
        self._rules["slow_operations"] = SlowOperationsRule(config)

    def analyze(self, log_line):
        log_id = log_line.get("id", "")
        if log_id != 51803:  # Slow query
            return
        # Stream the raw log line to the output file for the scatter charts.
        self._cache = log_line
        self._write_output()
        self._cache = None

        # Aggregate the query patterns for the top-N table.
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
        slow_query = self._patterns.get(query_hash, None)
        if slow_query is None:
            slow_query = {}
            self._patterns[query_hash] = slow_query
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
        self._patterns = dict(
            sorted(self._patterns.items(), key=lambda item: item[1]["count"], reverse=True)[: self._top_n]
        )
        # Persist the aggregated top-N records (appended after the raw lines)
        # so they survive together with the chart data in the output file.
        self._cache = list(self._patterns.values())
        super().finalize_analysis()
        # Apply the rules to generate the test results (e.g. collection scans,
        # poor query targeting).
        for rule in self._rules.values():
            test_result, _ = rule.apply(self._cache, extra_info={"host": self._hostname or "unknown"})
            self.append_test_results(test_result)

    def review_results_markdown(self, f):
        records = self._load_records()
        parser = SlowParser()
        f.write(parser.markdown(records))
