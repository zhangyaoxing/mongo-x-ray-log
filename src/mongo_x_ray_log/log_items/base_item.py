"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import html as html_mod
import logging
import os
from typing import Any, Optional

from bson import json_util

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray.utils import to_ejson
from mongo_x_ray.version import Version
from mongo_x_ray_log.rules.base_rule import BaseRule


def get_version(log_line):
    """
    Extract and parse the version information from a log line.
    """
    log_id = log_line.get("id", "")
    if log_id != 23403:
        return None
    attr = log_line.get("attr", {})
    build_info = attr.get("buildInfo", {})
    version = build_info.get("version", "Unknown")
    return Version.parse(version)


def colorize_severity(severity: SEVERITY) -> str:
    mapping = {
        SEVERITY.HIGH.name: "red",
        SEVERITY.MEDIUM.name: "orange",
        SEVERITY.LOW.name: "green",
        SEVERITY.INFO.name: "gray",
    }
    return mapping.get(severity.name, "black")


class BaseItem:
    _cache: Any = None

    def __init__(self, output_folder: str, config, **kwargs) -> None:
        self.config = config
        self._output_file = os.path.join(output_folder, f"{self.__class__.__name__}.json")
        self._logger = logging.getLogger(__name__)
        self._row_count: int = 0
        self._show_reset: bool = kwargs.get("show_reset", False)
        self._server_version: Optional[Version] = None
        self._hostname: Optional[str] = None
        self._test_result: list = []
        self._rules: dict[str, BaseRule] = {}
        if os.path.isfile(self._output_file):
            os.remove(self._output_file)

    def analyze(self, log_line) -> None:
        log_id = log_line.get("id", "")
        if log_id == 23403:  # Build Info
            self._server_version = get_version(log_line)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def finalize_analysis(self) -> None:
        self._write_output()

    def test_result_markdown(self, output) -> None:
        """Write the test results (issues found by the item's rules) to *output*."""
        if len(self._test_result) == 0:
            output.write("<b style='color: green;'>Pass.</b>\n\n")
            return

        output.write(
            '| <span data-sortable="false">\\#</span>{60px}'
            ' | <span data-sortable="true">Host</span>{180px}'
            ' | <span data-sortable="true">Severity</span>{120px}'
            ' | <span data-sortable="true">Category</span>{200px}'
            ' | <span data-sortable="false">Message</span>{*} |\n'
        )
        output.write("|:----------:|:----------:|:----------:|---------|---------|\n")
        for idx, item in enumerate(self._test_result):
            severity = item["severity"]
            severity_cell = (
                f'<span data-sort-value="{severity.value}">'
                f"<b style='color: {colorize_severity(severity)}'>"
                f" {severity.name} </b></span>"
            )
            category_cell = item["title"]
            risk = item.get("matched_risk")
            if risk:
                risk_id = html_mod.escape(str(risk.get("id", "")))
                risk_name = html_mod.escape(str(risk.get("name", ""))).replace("\r\n", "<br>").replace("\n", "<br>")
                risk_desc = (
                    html_mod.escape(str(risk.get("description", ""))).replace("\r\n", "<br>").replace("\n", "<br>")
                )
                category_cell += (
                    f' <span class="risk-badge">RISK-{risk_id}'
                    f'<span class="risk-tooltip">'
                    f'<span class="risk-name">{risk_name}</span>'
                    f"{risk_desc}"
                    f"</span></span>"
                )
            output.write(
                f"| **{idx + 1}** | `{item['host']}` | {severity_cell} | {category_cell} | {item['message']} |\n"
            )
        output.write("\n")

    def append_test_result(self, host: str, severity: SEVERITY, title: str, message: str) -> None:
        self._test_result.append({"host": host, "severity": severity, "title": title, "message": message})

    def append_test_results(self, items: list) -> None:
        for item in items:
            self.append_test_result(item["host"], item["severity"], item["title"], item["description"])

    def _load_records(self) -> list:
        """Load the analysed records from the output file."""
        with open(self._output_file, "r", encoding="utf-8") as f:
            return [json_util.loads(line) for line in f]

    def review_results_markdown(self, f) -> None:
        raise NotImplementedError("Subclasses should implement this method.")

    def _write_output(self) -> None:
        # Open file steam and write the cache to file
        # Even if the cache is None, we still write to indicate no data
        with open(self._output_file, "a", encoding="utf-8") as f:
            if self._cache is None:
                self._logger.debug("Cache is empty, nothing to write for %s", self.__class__.__name__)
                return
            if isinstance(self._cache, list):
                for item in self._cache:
                    f.write(to_ejson(item, indent=None))
                    f.write("\n")
                    self._row_count += 1
                self._logger.debug(
                    "Wrote %d records to %s for %s",
                    len(self._cache),
                    self._output_file,
                    self.__class__.__name__,
                )
            else:
                f.write(to_ejson(self._cache, indent=None))
                f.write("\n")
                self._row_count += 1
                self._logger.debug(
                    "Wrote 1 record to %s for %s",
                    self._output_file,
                    self.__class__.__name__,
                )
