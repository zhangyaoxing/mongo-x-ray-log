"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import io

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.log_items.summary_item import SummaryItem


class _FakeItem:
    def __init__(self, test_result):
        self._test_result = test_result


def _result(severity, title, matched_risk=None):
    result = {"host": "h1", "severity": severity, "title": title, "message": "msg"}
    if matched_risk:
        result["matched_risk"] = matched_risk
    return result


def test_summary_item_aggregates_severity_and_category():
    summary = SummaryItem(risk_available=False)
    items = [
        _FakeItem(
            [
                _result(SEVERITY.HIGH, "Collection Scan Detected"),
                _result(SEVERITY.MEDIUM, "Warning Logs Detected"),
            ]
        ),
        _FakeItem([_result(SEVERITY.HIGH, "Collection Scan Detected")]),
    ]
    summary.summarize(items)
    assert summary._summary_severity[SEVERITY.HIGH] == 2
    assert summary._summary_severity[SEVERITY.MEDIUM] == 1
    assert summary._summary_title == {"Collection Scan Detected": 2, "Warning Logs Detected": 1}


def test_summary_item_overview_renders_tables():
    summary = SummaryItem(risk_available=False)
    summary.summarize([_FakeItem([_result(SEVERITY.HIGH, "Collection Scan Detected")])])
    buf = io.StringIO()
    summary.overview(buf)
    md = buf.getvalue()
    assert "#### By Severity" in md
    assert "#### By Category" in md
    assert "Collection Scan Detected" in md
    assert "Known Risks" not in md


def test_summary_item_overview_renders_risk_badge():
    summary = SummaryItem(risk_available=True)
    summary.summarize(
        [
            _FakeItem(
                [
                    _result(
                        SEVERITY.MEDIUM,
                        "Incompatible Driver Version",
                        matched_risk={"id": 42, "name": "Risk Name", "description": "Risk description."},
                    )
                ]
            )
        ]
    )
    buf = io.StringIO()
    summary.overview(buf)
    md = buf.getvalue()
    assert "Known Risks" in md
    assert "RISK-42" in md
    assert "Risk Name" in md
