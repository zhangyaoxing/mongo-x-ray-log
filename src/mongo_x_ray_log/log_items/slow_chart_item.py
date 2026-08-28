"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_log.log_items.base_item import BaseItem
from mongo_x_ray_log.parsers.slow_chart_parser import SlowChartParser


class SlowChartItem(BaseItem):
    """Generate a scatter plot showing slow operations over time,
    with each point representing a slow query colored by namespace."""

    def __init__(self, output_folder, config):
        super().__init__(output_folder, config, show_reset=True)
        self.name = "Slow Operations Chart"
        self.description = "Generate a scatter plot showing slow operations over time, with each point representing a slow query colored by namespace."
        self._cache = None

    def analyze(self, log_line):
        log_id = log_line.get("id", "")
        if log_id != 51803:  # Slow query
            return
        self._cache = log_line
        self._write_output()
        self._cache = None

    def review_results_markdown(self, f):
        parser = SlowChartParser()
        f.write(parser.markdown(self._load_records()))
