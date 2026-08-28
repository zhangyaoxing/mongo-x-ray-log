"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from random import randint

from mongo_x_ray.utils import bold, env, green, yellow
from mongo_x_ray_log.log_items.base_item import BaseItem
from mongo_x_ray_log.parsers.wef_parser import WEFParser


class WEFItem(BaseItem):
    def __init__(self, output_folder, config):
        super().__init__(output_folder, config)
        self._cache = {}
        self.name = "Warning/Error/Fatal Logs"
        self.description = "Visualize warning, error, and fatal log messages."
        self._ai_support = self.config.get("ai_support", False)

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
        cache = self._cache

        if self._ai_support == "gpt":
            try:
                from mongo_x_ray.ai_client import GPT_MODEL
                from mongo_x_ray_log.ai import analyze_log_line_gpt

                if env == "development":
                    cache = [self._cache[randint(0, len(self._cache) - 1)]] if len(self._cache) > 0 else []
                    self._logger.info(yellow("Running in development mode. Only process ONE random log entry with AI."))
                    self._logger.info(yellow(f"Log ID: {cache[0]['id']}"))
                self._logger.info(
                    "Using GPT model (%s) for W/E/F log analysis. This can take a few minutes...",
                    green(bold(GPT_MODEL)),
                )
                for item in cache:
                    item["ai_analysis"] = analyze_log_line_gpt(item["sample"])
                    self._logger.debug("AI analyzed log: %s", item["id"])

            except ImportError as e:
                self._logger.error("OpenAI support enabled but the OpenAI library is not available: %s", e)
                self._logger.error("Please install the OpenAI dependency or disable AI support in config.json")
                self._ai_support = False

        self._match_risks()
        super().finalize_analysis()

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
