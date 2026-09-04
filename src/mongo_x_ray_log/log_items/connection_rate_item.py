"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import math
from datetime import datetime

from mongo_x_ray_log.log_items.base_item import BaseItem
from mongo_x_ray_log.parsers.connection_rate_parser import ConnectionRateParser
from mongo_x_ray_log.rules.connection_rate_rule import ConnectionRateRule


class ConnectionRateItem(BaseItem):
    """
    Analyze connection rates from log entries.
    """

    def __init__(self, output_folder: str, config):
        super().__init__(output_folder, config, show_reset=True)
        self._cache = None
        self._records = []
        self.name = "Connection Rate"
        self.description = "Analyse the rate of connections created and ended over a specified time window."
        self._rules["connection_rate"] = ConnectionRateRule(config)

    def analyze(self, log_line):
        log_id = log_line.get("id", "")
        if log_id not in [22943, 22944]:  # Connection accepted/ended
            return
        if self._cache is None:
            self._cache = {}
        counter = "created" if log_id == 22943 else "ended"
        time = log_line.get("t")
        ts = math.floor(time.timestamp())
        time_min = datetime.fromtimestamp(ts - (ts % 60))

        if self._cache.get("time", None) != time_min:
            if self._cache != {}:
                self._write_output()
                self._records.append(self._cache)
            self._cache = {
                "time": time_min,
                "created": 0,
                "ended": 0,
                "total": 0,
                "byIp": {},
            }
        attr = log_line.get("attr", {})
        conn_count = attr.get("connectionCount", 1)
        ip = attr["remote"].split(":")[0] if "remote" in attr else "unknown"
        self._cache[counter] += 1
        self._cache["total"] = conn_count
        if ip not in self._cache["byIp"]:
            self._cache["byIp"][ip] = {"created": 0, "ended": 0}
        self._cache["byIp"][ip][counter] += 1

    def finalize_analysis(self):
        if self._cache:
            self._records.append(self._cache)
        super().finalize_analysis()
        # Apply the rules to the collected per-minute buckets to generate the
        # test results (e.g. high connection churn).
        for rule in self._rules.values():
            test_result, _ = rule.apply(self._records, extra_info={"host": self._hostname or "unknown"})
            self.append_test_results(test_result)

    def review_results_markdown(self, f):
        parser = ConnectionRateParser()
        f.write(parser.markdown(self._load_records()))
