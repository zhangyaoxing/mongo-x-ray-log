"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_log import ai as _ai
from mongo_x_ray_log.log_items.base_item import BaseItem
from mongo_x_ray_log.parsers.wef_parser import WEFParser
from mongo_x_ray_log.rules.severity_log_rule import SeverityLogRule


class WEFItem(BaseItem):
    def __init__(self, output_folder, config):
        super().__init__(output_folder, config)
        self._cache = {}
        self.name = "Warning/Error/Fatal Logs"
        self.description = "Visualize warning, error, and fatal log messages."
        self._rules["severity_log"] = SeverityLogRule(config)

    def analyze(self, log_line):
        severity = log_line.get("s", "").lower()
        if severity not in ["w", "e", "f"]:
            return
        timestamp = log_line.get("t", "")
        msg = log_line.get("msg", "")
        log_id = log_line.get("id", "")
        if log_id not in self._cache:
            self._cache[log_id] = {
                "id": log_id,
                "severity": severity,
                "timestamp": [timestamp],
                "msg": msg,
                "sample": log_line,
            }
        else:
            self._cache[log_id]["timestamp"].append(timestamp)

    def finalize_analysis(self):
        self._cache = list(self._cache.values())

        self._match_risks()
        super().finalize_analysis()
        self._run_ai_analysis(lambda: _ai.analyze_wef(self._cache))
        # Apply the rules to generate the test results (e.g. warning logs present).
        for rule in self._rules.values():
            test_result, _ = rule.apply(self._cache, extra_info={"host": self._hostname or "unknown"})
            self.append_test_results(test_result)

    def _match_risks(self) -> None:
        """Enrich cache entries with matched risk info via vector search."""
        try:
            from mongo_x_ray_risk import match_risk
        except ImportError:
            return
        for entry in self._cache:
            msg = entry.get("msg", "")
            if not msg:
                continue
            risk = match_risk(msg)
            if risk:
                entry["matched_risk"] = risk

    def review_results_markdown(self, f):
        parser = WEFParser()
        f.write(parser.markdown(self._load_records()))
