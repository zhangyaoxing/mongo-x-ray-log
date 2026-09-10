"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.rules.connection_rate_rule import ConnectionRateRule


def _bucket(created=0, ended=0, total=100, time="2026-09-04T10:00:00"):
    return {"time": time, "created": created, "ended": ended, "total": total, "byIp": {}}


def _titles(results):
    return [result["title"] for result in results]


def test_connection_rate_rule_no_issue_below_medium():
    rule = ConnectionRateRule({})
    data = [_bucket(created=40, ended=5, total=100)]
    test_results, parsed = rule.apply(data, extra_info={"host": "test-host"})
    assert parsed == data
    assert test_results == []


def test_connection_rate_rule_created_half_of_total_is_medium():
    rule = ConnectionRateRule({})
    data = [_bucket(created=50, ended=0, total=100)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert len(test_results) == 1
    issue = test_results[0]
    assert issue["severity"] == SEVERITY.MEDIUM
    assert issue["title"] == "High Connection Churn"
    assert "50 connections were created" in issue["description"]


def test_connection_rate_rule_ended_three_quarters_of_total_is_high():
    rule = ConnectionRateRule({})
    data = [_bucket(created=0, ended=75, total=100)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert len(test_results) == 1
    assert test_results[0]["severity"] == SEVERITY.HIGH
    assert "75 connections were ended" in test_results[0]["description"]


def test_connection_rate_rule_multiple_buckets():
    rule = ConnectionRateRule({})
    data = [
        _bucket(created=20, total=100, time="2026-09-04T10:00:00"),
        _bucket(created=60, total=100, time="2026-09-04T10:01:00"),
        _bucket(created=80, total=100, time="2026-09-04T10:02:00"),
    ]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    severities = [r["severity"] for r in test_results]
    assert severities == [SEVERITY.MEDIUM, SEVERITY.HIGH]


def test_connection_rate_rule_skips_buckets_without_total():
    rule = ConnectionRateRule({})
    data = [_bucket(created=50, total=0)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert test_results == []


def test_connection_rate_rule_custom_ratios_from_config():
    rule = ConnectionRateRule({"connection_rate_medium": 0.2, "connection_rate_high": 0.4})
    data = [_bucket(created=50, total=100)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert test_results[0]["severity"] == SEVERITY.HIGH
