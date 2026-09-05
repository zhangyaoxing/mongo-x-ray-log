"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.rules.slow_rate_rule import SlowRateRule


def _bucket(total_slow_ms, count, time="2026-09-05T10:00:00"):
    return {"time": time, "total_slow_ms": total_slow_ms, "count": count, "byNs": {}}


def _titles(results):
    return [result["title"] for result in results]


def test_slow_rate_rule_no_issue_below_medium():
    rule = SlowRateRule({})
    data = [_bucket(total_slow_ms=100, count=2)]  # avg 50 ms
    test_results, parsed = rule.apply(data, extra_info={"host": "test-host"})
    assert parsed == data
    assert test_results == []


def test_slow_rate_rule_avg_over_100ms_is_medium():
    rule = SlowRateRule({})
    data = [_bucket(total_slow_ms=300, count=2)]  # avg 150 ms
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert len(test_results) == 1
    issue = test_results[0]
    assert issue["severity"] == SEVERITY.MEDIUM
    assert issue["title"] == "Significant Slow Queries"
    assert "150.00 ms" in issue["description"]


def test_slow_rate_rule_avg_over_500ms_is_high():
    rule = SlowRateRule({})
    data = [_bucket(total_slow_ms=2200, count=4)]  # avg 550 ms
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert len(test_results) == 1
    assert test_results[0]["severity"] == SEVERITY.HIGH


def test_slow_rate_rule_multiple_buckets():
    rule = SlowRateRule({})
    data = [
        _bucket(total_slow_ms=60, count=2, time="2026-09-05T10:00:00"),  # avg 30
        _bucket(total_slow_ms=300, count=2, time="2026-09-05T10:01:00"),  # avg 150 -> MEDIUM
        _bucket(total_slow_ms=1200, count=2, time="2026-09-05T10:02:00"),  # avg 600 -> HIGH
    ]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    severities = [r["severity"] for r in test_results]
    assert severities == [SEVERITY.MEDIUM, SEVERITY.HIGH]


def test_slow_rate_rule_skips_empty_buckets():
    rule = SlowRateRule({})
    data = [_bucket(total_slow_ms=0, count=0)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert test_results == []


def test_slow_rate_rule_custom_thresholds_from_config():
    rule = SlowRateRule({"slow_rate_medium": 50, "slow_rate_high": 200})
    data = [_bucket(total_slow_ms=500, count=2)]  # avg 250 -> HIGH with custom thresholds
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert test_results[0]["severity"] == SEVERITY.HIGH
