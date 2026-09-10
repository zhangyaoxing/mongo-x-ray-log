"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.rules.severity_log_rule import SeverityLogRule


def _entry(severity):
    return {"id": 1, "severity": severity, "timestamp": ["2026-09-08T00:00:00"], "msg": "msg"}


def test_severity_log_rule_flags_warning_as_medium():
    rule = SeverityLogRule({})
    data = [_entry("w"), _entry("e")]
    test_results, parsed = rule.apply(data, extra_info={"host": "test-host"})
    assert parsed == data
    assert len(test_results) == 1
    issue = test_results[0]
    assert issue["severity"] == SEVERITY.MEDIUM
    assert issue["title"] == "Warning Logs Detected"
    assert "`1` warning log entry" in issue["description"]


def test_severity_log_rule_flags_fatal_as_high():
    rule = SeverityLogRule({})
    data = [_entry("f"), _entry("e")]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert len(test_results) == 1
    issue = test_results[0]
    assert issue["severity"] == SEVERITY.HIGH
    assert issue["title"] == "Fatal Logs Detected"
    assert "`1` fatal log entry" in issue["description"]


def test_severity_log_rule_reports_both_severities():
    rule = SeverityLogRule({})
    data = [_entry("w"), _entry("w"), _entry("f")]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    titles = [r["title"] for r in test_results]
    severities = [r["severity"] for r in test_results]
    assert titles == ["Warning Logs Detected", "Fatal Logs Detected"]
    assert severities == [SEVERITY.MEDIUM, SEVERITY.HIGH]
    assert "`2` warning log entries" in test_results[0]["description"]


def test_severity_log_rule_no_issue_without_warnings_or_fatals():
    rule = SeverityLogRule({})
    data = [_entry("e")]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert test_results == []
