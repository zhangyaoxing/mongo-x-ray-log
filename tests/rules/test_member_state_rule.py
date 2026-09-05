"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.rules.member_state_rule import MemberStateRule


def _event(event_id, new_state=None):
    details = {}
    if new_state is not None:
        details["new_state"] = new_state
    return {"id": event_id, "details": details}


def test_member_state_rule_flags_abnormal_final_state():
    rule = MemberStateRule({})
    data = {
        "localhost:27018": [_event(21215, "STARTUP2"), _event(21358, "SECONDARY")],
        "localhost:27019": [_event(21215, "SECONDARY"), _event(21216, "DOWN")],
        "localhost:27017": [_event(21358, "PRIMARY")],
    }
    test_results, parsed = rule.apply(data, extra_info={"host": "test-host"})
    assert parsed == data
    assert len(test_results) == 1
    issue = test_results[0]
    assert issue["severity"] == SEVERITY.MEDIUM
    assert issue["title"] == "Abnormal Member State"
    assert "localhost:27019" in issue["description"]
    assert "DOWN" in issue["description"]


def test_member_state_rule_ignores_members_in_normal_states():
    rule = MemberStateRule({})
    data = {
        "a:27017": [_event(21358, "PRIMARY")],
        "b:27017": [_event(21215, "primary"), _event(21216, "SECONDARY")],  # case-insensitive
    }
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert test_results == []


def test_member_state_rule_skips_members_without_state_events():
    rule = MemberStateRule({})
    data = {
        "a:27017": [_event(21392)],  # NewConfig only
        "b:27017": [_event(-1)],  # LogEnd only
    }
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    assert test_results == []


def test_member_state_rule_uses_last_known_state():
    rule = MemberStateRule({})
    data = {
        # Member recovered to SECONDARY after an abnormal phase -> no issue
        "a:27017": [_event(21215, "RECOVERING"), _event(21216, "SECONDARY")],
        # Member ended in an abnormal state after being healthy -> issue
        "b:27017": [_event(21215, "PRIMARY"), _event(21216, "ROLLBACK")],
    }
    test_results, _ = rule.apply(data, extra_info={"host": "test-host"})
    titles = [r["title"] for r in test_results]
    assert titles == ["Abnormal Member State"]
    assert "b:27017" in test_results[0]["description"]
