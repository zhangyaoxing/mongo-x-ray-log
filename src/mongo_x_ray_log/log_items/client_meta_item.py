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
from mongo_x_ray_log.parsers.client_meta_parser import ClientMetaParser
from mongo_x_ray_log.rules.driver_compatibility_rule import DriverCompatibilityRule


class ClientMetaItem(BaseItem):
    """Client Metadata Log Item checks for client metadata in the log."""

    def __init__(self, output_folder: str, config):
        super().__init__(output_folder, config)
        self._cache = {}
        self.name = "Client Metadata"
        self.description = "Visualize client metadata."
        self._rules["driver_compatibility"] = DriverCompatibilityRule(config)

    def analyze(self, log_line):
        super().analyze(log_line)
        log_id = log_line.get("id", "")
        if log_id != 51800:  # Client metadata
            return
        attr = log_line.get("attr", {})
        ip = attr["remote"].split(":")[0]
        doc = {
            "application": attr["doc"].get("application", {}),
            "driver": attr["doc"].get("driver", {}),
            "os": attr["doc"].get("os", {}),
            "platform": attr["doc"].get("platform", ""),
        }
        # Exclude automation agent connections — they dominate the chart.
        # Internal drivers (e.g. NetworkInterfaceTL, MongoDB Internal Client) are still collected
        # here so they appear in the results table; they are just ignored by the
        # compatibility check (see DriverCompatibilityRule).
        app_name = doc["application"].get("name", "").lower()
        if "automation" in app_name:
            return
        doc_hash = json_hash(doc)
        if doc_hash not in self._cache:
            self._cache[doc_hash] = {"doc": doc}
        if "ips" not in self._cache[doc_hash]:
            self._cache[doc_hash]["ips"] = {}
        self._cache[doc_hash]["ips"][ip] = self._cache[doc_hash]["ips"].get(ip, 0) + 1

    def finalize_analysis(self):
        cache = []
        for v in self._cache.values():
            doc = v["doc"]
            ips = [{"ip": ip, "count": count} for ip, count in v.get("ips", {}).items()]
            cache.append({"doc": doc, "ips": ips})
        self._cache = cache
        super().finalize_analysis()
        # Apply the rules to generate the test results (e.g. driver version incompatibility).
        for rule in self._rules.values():
            test_result, _ = rule.apply(
                cache, server_version=self._server_version, extra_info={"host": self._hostname or "unknown"}
            )
            self.append_test_results(test_result)

    def review_results_markdown(self, f):
        parser = ClientMetaParser()
        f.write(parser.markdown(self._cache, server_version=self._server_version))
