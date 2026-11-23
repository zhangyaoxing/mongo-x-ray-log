"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.

Section-level AI analysis for the log report (issue #377).
"""

from io import StringIO

import pytest
from bson import json_util

import mongo_x_ray_log.ai as ai
from mongo_x_ray_log.log_items.connection_rate_item import ConnectionRateItem
from mongo_x_ray_log.log_items.log_rate_item import LogRateItem
from mongo_x_ray_log.log_items.slow_rate_item import SlowRateItem
from mongo_x_ray_log.log_items.wef_item import WEFItem
from tests.mocking import gen_mock_write_output

CONNECTION_LOGS = [
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.199+02:00"},"s":"I","c":"NETWORK","id":22943,"msg":"Connection accepted",'
        '"attr":{"remote":"127.0.0.1:51011","connectionCount":1}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.204+02:00"},"s":"I","c":"NETWORK","id":22944,"msg":"Connection ended",'
        '"attr":{"remote":"127.0.0.1:51011","connectionCount":0}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-26T00:02:01.718+02:00"},"s":"I","c":"NETWORK","id":22943,"msg":"Connection accepted",'
        '"attr":{"remote":"10.0.0.7:57335","connectionCount":20}}'
    ),
]

WEF_LOGS = [
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:49.656+02:00"},"s":"W","c":"ASIO","id":22601,'
        '"msg":"No TransportLayer configured during NetworkInterface startup"}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:49.659+02:00"},"s":"W","c":"ASIO","id":22601,'
        '"msg":"No TransportLayer configured during NetworkInterface startup"}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:52.000+02:00"},"s":"E","c":"NETWORK","id":22984,'
        '"msg":"Failed to connect to 10.0.0.9:27017"}'
    ),
]

SLOW_LOGS = [
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.199+02:00"},"s":"I","c":"COMMAND","id":51803,'
        '"msg":"Slow query","attr":{"ns":"shop.orders","durationMillis":1200}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:40:11.199+02:00"},"s":"I","c":"COMMAND","id":51803,'
        '"msg":"Slow query","attr":{"ns":"shop.orders","durationMillis":900}}'
    ),
]

INFO_LOGS = [
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.199+02:00"},"s":"I","c":"CONTROL","id":12345,"msg":"Repeated info log"}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:40:52.199+02:00"},"s":"I","c":"CONTROL","id":12345,"msg":"Repeated info log"}'
    ),
]


@pytest.fixture
def fake_client(monkeypatch):
    monkeypatch.setattr("mongo_x_ray.ai_client.get_client", lambda: (object(), "test-model"))


def test_items_run_their_own_ai_analysis(tmp_path, fake_client, monkeypatch):
    calls = []

    def fake(name):
        def analyzer(*_args):
            calls.append(name)
            return f"{name} verdict"

        return analyzer

    monkeypatch.setattr(ai, "analyze_connection_rate", fake("connection"))
    monkeypatch.setattr(ai, "analyze_log_rate", fake("log-rate"))
    monkeypatch.setattr(ai, "analyze_slow_rate", fake("slow-rate"))
    monkeypatch.setattr(ai, "analyze_wef", fake("wef"))

    connection = ConnectionRateItem(output_folder=str(tmp_path), config={"ai_analysis": True})
    _, connection._write_output = gen_mock_write_output(connection)
    for log in CONNECTION_LOGS:
        connection.analyze(log)
    connection.finalize_analysis()

    slow = SlowRateItem(output_folder=str(tmp_path), config={"ai_analysis": True})
    _, slow._write_output = gen_mock_write_output(slow)
    for log in SLOW_LOGS:
        slow.analyze(log)
    slow.finalize_analysis()

    wef = WEFItem(output_folder=str(tmp_path), config={"ai_analysis": True})
    _, wef._write_output = gen_mock_write_output(wef)
    for log in WEF_LOGS:
        wef.analyze(log)
    wef.finalize_analysis()

    log_rate = LogRateItem(output_folder=str(tmp_path), config={"ai_analysis": True})
    _, log_rate._write_output = gen_mock_write_output(log_rate)
    for log in INFO_LOGS:
        log_rate.analyze(log)
    log_rate.finalize_analysis()

    assert calls == ["connection", "slow-rate", "wef", "log-rate"]
    assert connection._ai_result == "connection verdict"
    assert slow._ai_result == "slow-rate verdict"
    assert wef._ai_result == "wef verdict"
    assert log_rate._ai_result == "log-rate verdict"


def test_ai_analysis_can_be_disabled_per_item(tmp_path, fake_client, monkeypatch):
    def fail(*_args):
        raise AssertionError("the analyzer must not run when ai_analysis is false")

    monkeypatch.setattr(ai, "analyze_connection_rate", fail)

    item = ConnectionRateItem(output_folder=str(tmp_path), config={"ai_analysis": False})
    _, item._write_output = gen_mock_write_output(item)
    for log in CONNECTION_LOGS:
        item.analyze(log)
    item.finalize_analysis()

    assert item._ai_result == ""


def test_ai_analysis_is_skipped_without_a_key(tmp_path, monkeypatch):
    monkeypatch.setattr("mongo_x_ray.ai_client.get_client", lambda: (None, "gpt-4o"))
    monkeypatch.setattr(ai, "analyze_connection_rate", lambda _records: pytest.fail("should not be called"))

    item = ConnectionRateItem(output_folder=str(tmp_path), config={"ai_analysis": True})
    _, item._write_output = gen_mock_write_output(item)
    for log in CONNECTION_LOGS:
        item.analyze(log)
    item.finalize_analysis()

    assert item._ai_result == ""


def test_ai_note_markdown_renders_the_verdict():
    item = ConnectionRateItem(output_folder="/tmp", config={"ai_analysis": True})
    output = StringIO()

    item.ai_note_markdown(output)
    assert output.getvalue() == ""

    item._ai_result = "Steady churn, nothing to act on."
    item.ai_note_markdown(output)
    note = output.getvalue()

    assert 'class="ai-label"' in note
    assert "AI Analysis" in note
    assert note.startswith("> ")
    assert "Steady churn, nothing to act on." in note


def test_analyzers_send_a_compact_summary(monkeypatch):
    prompts = []

    def fake_complete(prompt, system=None):
        prompts.append((prompt, system))
        return "  looks fine  "

    monkeypatch.setattr("mongo_x_ray.ai_client.complete", fake_complete)

    connection_prompt_result = ai.analyze_connection_rate(
        [
            {"created": 2, "ended": 1, "total": 2, "byIp": {"127.0.0.1": {"created": 2, "ended": 1}}},
            {"created": 1, "ended": 0, "total": 20, "byIp": {"10.0.0.7": {"created": 1, "ended": 0}}},
        ]
    )
    log_prompt_result = ai.analyze_log_rate(
        [{"id": 12345, "sample": {"msg": "Repeated info log"}, "buckets": [{"count": 1}, {"count": 4}]}]
    )
    slow_prompt_result = ai.analyze_slow_rate(
        [{"count": 2, "total_slow_ms": 2100, "byNs": {"shop.orders": {"count": 2, "total_slow_ms": 2100}}}]
    )
    wef_prompt_result = ai.analyze_wef(
        [{"id": 22601, "severity": "w", "timestamp": [1, 2], "msg": "No TransportLayer configured"}]
    )

    assert connection_prompt_result == "looks fine"
    assert log_prompt_result == "looks fine"
    assert slow_prompt_result == "looks fine"
    assert wef_prompt_result == "looks fine"

    prompts_text = "\n".join(prompt for prompt, _ in prompts)
    assert "Connections created per minute: peak 2" in prompts_text
    assert "[12345] total 5, peak 4/minute" in prompts_text
    assert "Slow queries per minute: peak 2" in prompts_text
    assert "shop.orders" in prompts_text
    assert "Per severity: W 2" in prompts_text
    for prompt, system in prompts:
        assert len(prompt) < 4000
        assert system and "MongoDB expert" in system


def test_empty_sections_do_not_call_the_ai(monkeypatch):
    def fail(*_args, **_kwargs):
        raise AssertionError("no AI call for an empty section")

    monkeypatch.setattr("mongo_x_ray.ai_client.complete", fail)

    assert ai.analyze_connection_rate([]) is None
    assert ai.analyze_log_rate([]) is None
    assert ai.analyze_slow_rate([]) is None
    assert ai.analyze_wef([]) is None


def test_wef_item_no_longer_runs_per_line_ai():
    # The old per-log-line analysis module is gone; the section analysis replaced it.
    assert not hasattr(ai, "analyze_log_line_gpt")

    item = WEFItem(output_folder="/tmp", config={"ai_analysis": True})
    _, item._write_output = gen_mock_write_output(item)
    for log in WEF_LOGS:
        item.analyze(log)
    item.finalize_analysis()

    assert all("ai_analysis" not in entry for entry in item._cache)
