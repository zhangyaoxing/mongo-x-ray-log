"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import io
import sys
from datetime import datetime, timezone
from types import ModuleType

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.framework import Framework
from mongo_x_ray_log.log_items.base_item import BaseItem


def _make_item():
    item = BaseItem(output_folder="/tmp", config={})
    item.name = "Test Item"
    item.description = "Test description."
    item._test_result = [
        {
            "host": "host1",
            "severity": SEVERITY.MEDIUM,
            "title": "Incompatible Driver Version",
            "message": "Driver `x 1.0` is not compatible.",
        }
    ]
    return item


def _inject_fake_risk_module(has_risks=True):
    """Inject a fake mongo_x_ray_risk module and return the enrich call log."""
    calls = []

    def enrich(test_results):
        calls.append(test_results)
        for result in test_results:
            result["matched_risk"] = {"id": 42, "name": "Test Risk", "description": "Risk description."}
        return len(test_results)

    fake = ModuleType("mongo_x_ray_risk")
    fake.has_risks = lambda: has_risks
    fake.enrich_test_results = enrich
    sys.modules["mongo_x_ray_risk"] = fake
    return calls


def _render_framework(item):
    fw = Framework("/tmp/test.log", {})
    fw._log_start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    fw._log_end = datetime(2026, 9, 1, 1, tzinfo=timezone.utc)
    fw._items = [item]
    buf = io.StringIO()
    fw._render_markdown(buf)
    return buf.getvalue()


def test_test_result_markdown_renders_risk_badge():
    item = _make_item()
    item._test_result[0]["matched_risk"] = {"id": 7, "name": "Known Risk", "description": "Risk description."}
    buf = io.StringIO()
    item.test_result_markdown(buf)
    md = buf.getvalue()
    assert 'class="risk-badge"' in md
    assert "RISK-7" in md
    assert "Known Risk" in md


def test_test_result_markdown_without_risk_badge():
    item = _make_item()
    buf = io.StringIO()
    item.test_result_markdown(buf)
    assert 'class="risk-badge"' not in buf.getvalue()


def test_framework_enriches_test_results_with_risks(monkeypatch):
    calls = _inject_fake_risk_module(has_risks=True)
    item = _make_item()
    md = _render_framework(item)
    assert calls == [item._test_result]
    # The badge appears in the rendered test results
    assert 'class="risk-badge"' in md
    assert "RISK-42" in md


def test_framework_skips_enrichment_when_no_risks(monkeypatch):
    calls = _inject_fake_risk_module(has_risks=False)
    item = _make_item()
    md = _render_framework(item)
    assert calls == []
    assert 'class="risk-badge"' not in md


def test_framework_degrades_when_risk_module_missing(monkeypatch):
    monkeypatch.delitem(sys.modules, "mongo_x_ray_risk", raising=False)
    item = _make_item()
    md = _render_framework(item)
    # Report still renders without the risk register
    assert "Incompatible Driver Version" in md
