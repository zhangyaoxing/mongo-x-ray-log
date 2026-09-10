"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.rules.slow_operations_rule import SlowOperationsRule


def _record(
    query_hash="ABC123",
    ns="test.pizzas",
    plan_summary="IXSCAN { size: 1 }",
    keys_examined=0,
    docs_examined=0,
    n_returned=0,
    count=1,
):
    return {
        "query_hash": query_hash,
        "ns": ns,
        "plan_summary": plan_summary,
        "keys_examined": keys_examined,
        "docs_examined": docs_examined,
        "n_returned": n_returned,
        "count": count,
    }


def _titles(test_results):
    return [result["title"] for result in test_results]


def test_slow_operations_rule_no_issues_for_indexed_queries():
    rule = SlowOperationsRule({})
    data = [
        _record(plan_summary="IXSCAN { size: 1 }", keys_examined=10, n_returned=10, docs_examined=10),
        _record(query_hash="DEF456", plan_summary="", keys_examined=1, n_returned=100),
    ]
    test_results, parsed = rule.apply(data, extra_info={"host": "test-host"})
    assert parsed == data
    assert test_results == []


def test_slow_operations_rule_flags_collection_scan_as_high():
    rule = SlowOperationsRule({})
    data = [_record(plan_summary="COLLSCAN", keys_examined=5, n_returned=5)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    collscan_issues = [r for r in test_results if r["title"] == "Collection Scan Detected"]
    assert len(collscan_issues) == 1
    assert collscan_issues[0]["severity"] == SEVERITY.HIGH
    assert collscan_issues[0]["host"] == "test-host"
    assert "test.pizzas" in collscan_issues[0]["description"]


def test_slow_operations_rule_flags_poor_query_targeting_as_medium():
    rule = SlowOperationsRule({})
    # 5000 keys examined for 1 returned document >= threshold 1000
    data = [_record(plan_summary="IXSCAN { type: 1 }", keys_examined=5000, n_returned=1, docs_examined=2)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert _titles(test_results) == ["Poor Query Targeting"]
    issue = test_results[0]
    assert issue["severity"] == SEVERITY.MEDIUM
    assert "5000.0" in issue["description"] or "5000" in issue["description"]


def test_slow_operations_rule_flags_scanned_objects_targeting():
    rule = SlowOperationsRule({})
    # 2000 objects examined for 1 returned document >= threshold 1000
    data = [_record(plan_summary="COLLSCAN", keys_examined=5000, n_returned=1, docs_examined=2000)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    titles = _titles(test_results)
    assert titles.count("Collection Scan Detected") == 1
    assert titles.count("Poor Query Targeting") == 1
    assert titles.count("Poor Query Targeting (Objects)") == 1


def test_slow_operations_rule_custom_threshold_from_config():
    # Lower thresholds configured via config.json
    rule = SlowOperationsRule({"query_targeting": 10, "query_targeting_obj": 10})
    data = [_record(plan_summary="IXSCAN { x: 1 }", keys_examined=500, n_returned=10, docs_examined=500)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert _titles(test_results) == ["Poor Query Targeting", "Poor Query Targeting (Objects)"]


def test_slow_operations_rule_escalates_targeting_over_5000_to_high():
    rule = SlowOperationsRule({})
    # 6000 keys examined for 1 returned document > high threshold 5000
    data = [_record(plan_summary="IXSCAN { type: 1 }", keys_examined=6000, n_returned=1, docs_examined=2)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert _titles(test_results) == ["Poor Query Targeting"]
    issue = test_results[0]
    assert issue["severity"] == SEVERITY.HIGH
    assert "critical threshold" in issue["description"]


def test_slow_operations_rule_targeting_at_5000_stays_medium():
    rule = SlowOperationsRule({})
    # Exactly 5000 keys examined for 1 returned document: MEDIUM, not HIGH
    data = [_record(plan_summary="IXSCAN { type: 1 }", keys_examined=5000, n_returned=1, docs_examined=2)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert len(test_results) == 1
    assert test_results[0]["severity"] == SEVERITY.MEDIUM


def test_slow_operations_rule_escalates_scanned_objects_over_5000_to_high():
    rule = SlowOperationsRule({})
    # 8000 objects examined for 1 returned document > high threshold 5000
    data = [_record(plan_summary="IXSCAN { type: 1 }", keys_examined=10, n_returned=1, docs_examined=8000)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert _titles(test_results) == ["Poor Query Targeting (Objects)"]
    assert test_results[0]["severity"] == SEVERITY.HIGH


def test_slow_operations_rule_custom_high_threshold_from_config():
    # A lower critical threshold configured via config.json
    rule = SlowOperationsRule({"query_targeting_high": 500})
    data = [_record(plan_summary="IXSCAN { x: 1 }", keys_examined=1000, n_returned=1, docs_examined=1)]
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert _titles(test_results) == ["Poor Query Targeting"]
    assert test_results[0]["severity"] == SEVERITY.HIGH
