"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import html as html_mod

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.log_items.base_item import colorize_severity


class SummaryItem:
    """Summarize the test results across all log items (like the other plugins)."""

    def __init__(self, risk_available: bool = True) -> None:
        # Whether the risk register was detected; controls the Known Risks
        # column of the By Category summary table.
        self._risk_available = risk_available
        self._summary_severity: dict[SEVERITY, int] = {
            SEVERITY.HIGH: 0,
            SEVERITY.MEDIUM: 0,
            SEVERITY.LOW: 0,
            SEVERITY.INFO: 0,
        }
        self._summary_title: dict[str, int] = {}
        self._title_risk: dict[str, dict] = {}

    def summarize(self, items) -> None:
        for item in items:
            for result in item._test_result:
                severity = result.get("severity", SEVERITY.INFO)
                self._summary_severity[severity] = self._summary_severity.get(severity, 0) + 1
                title = result.get("title", "Untitled")
                self._summary_title[title] = self._summary_title.get(title, 0) + 1
                matched_risk = result.get("matched_risk")
                if matched_risk:
                    self._title_risk[title] = matched_risk

    def overview(self, output) -> None:
        def format_header(severity: SEVERITY):
            return f"<b style='color: {colorize_severity(severity)}'>{severity.name}</b>"

        output.write("#### By Severity\n\n")
        output.write(
            f"|{format_header(SEVERITY.HIGH)}{{200}}|{format_header(SEVERITY.MEDIUM)}{{200}}|"
            f"{format_header(SEVERITY.LOW)}{{200}}|{format_header(SEVERITY.INFO)}{{200}}|\n"
        )
        output.write("|:---:|:---:|:---:|:---:|\n")
        output.write(
            f"|{self._summary_severity[SEVERITY.HIGH]}|{self._summary_severity[SEVERITY.MEDIUM]}|"
            f"{self._summary_severity[SEVERITY.LOW]}|{self._summary_severity[SEVERITY.INFO]}|\n\n"
        )
        output.write("#### By Category\n\n")
        # The Known Risks column only makes sense when a risk register was
        # detected, so it is omitted from the summary table otherwise.
        if self._risk_available:
            output.write(
                '| <span data-sortable="true">Category</span>{400} '
                '| <span data-sortable="true">Count</span>{100} '
                '| <span data-sortable="false">Known Risks</span>{150} |\n'
            )
            output.write("|---:|:---:|:---|\n")
        else:
            output.write(
                '| <span data-sortable="true">Category</span>{400} | <span data-sortable="true">Count</span>{100} |\n'
            )
            output.write("|---:|:---:|\n")
        for title, count in self._summary_title.items():
            risk_html = ""
            matched_risk = self._title_risk.get(title)
            if matched_risk:
                rid = html_mod.escape(str(matched_risk.get("id", "")))
                rname = html_mod.escape(str(matched_risk.get("name", ""))).replace("\r\n", "<br>").replace("\n", "<br>")
                rdesc = (
                    html_mod.escape(str(matched_risk.get("description", "")))
                    .replace("\r\n", "<br>")
                    .replace("\n", "<br>")
                )
                risk_html = (
                    f'<span class="risk-badge">RISK-{rid}'
                    f'<span class="risk-tooltip">'
                    f'<span class="risk-name">{rname}</span>'
                    f"{rdesc}</span></span>"
                )
            if self._risk_available:
                output.write(f'|{title}|<span data-sort-value="{count}"><strong>{count}</strong></span>|{risk_html}|\n')
            else:
                output.write(f'|{title}|<span data-sort-value="{count}"><strong>{count}</strong></span>|\n')
        output.write("\n")


__all__ = ["SummaryItem"]
