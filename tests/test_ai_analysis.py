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
from mongo_x_ray_log.log_items.slow_item import SlowItem
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


def test_ai_note_is_rendered_in_the_raw_results_section(monkeypatch):
    """The verdict sits with the charts, not with the findings table."""
    from datetime import datetime, timezone
    from typing import TextIO

    import mongo_x_ray_log.framework as framework_module
    from mongo_x_ray_log.framework import Framework

    class FakeSummary:
        def __init__(self, **_kwargs):
            pass

        def summarize(self, _items):
            pass

        def overview(self, output: TextIO) -> None:
            output.write("SUMMARY\n\n")

    class FakeItem:
        name = "Fake Item"
        description = "Fake description."
        _test_result: list = []
        _show_reset = False
        _ai_result = "Verdict about the charts."

        def test_result_markdown(self, output: TextIO) -> None:
            output.write("FINDINGS\n\n")

        def review_results_markdown(self, output: TextIO) -> None:
            output.write("CHARTS\n\n")

        def ai_note_markdown(self, output: TextIO) -> None:
            if self._ai_result:
                output.write(f"AI-NOTE: {self._ai_result}\n\n")

    monkeypatch.setattr(framework_module, "SummaryItem", FakeSummary)

    framework = Framework(file_path="mongodb.log", config={})
    framework._items = [FakeItem()]
    framework._log_start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    framework._log_end = datetime(2025, 1, 2, tzinfo=timezone.utc)

    output = StringIO()
    framework._render_markdown(output)
    report = output.getvalue()

    assert report.count("AI-NOTE: Verdict about the charts.") == 1
    # not in the findings section ...
    assert report.index("FINDINGS") < report.index("## 2 Review Raw Results")
    # ... but after the raw-results heading and after the item's charts
    assert report.index("## 2 Review Raw Results") < report.index("CHARTS")
    assert report.index("CHARTS") < report.index("AI-NOTE: Verdict about the charts.")


def test_index_recommendation_is_parsed_from_json(monkeypatch):
    assert ai._parse_index_recommendation('{"recommended_index": "db.a.createIndex({x: 1})"}') == (
        "db.a.createIndex({x: 1})"
    )
    assert ai._parse_index_recommendation('```json\n{"recommended_index": "db.a.createIndex({x: 1})"}\n```') == (
        "db.a.createIndex({x: 1})"
    )
    assert ai._parse_index_recommendation('{"recommended_index": ""}') is None
    assert ai._parse_index_recommendation("no idea") is None
    # a model that answers in prose still gets picked up
    assert ai._parse_index_recommendation('Sure: {"recommended_index": "db.b.createIndex({y: -1})"}') == (
        "db.b.createIndex({y: -1})"
    )


def test_index_recommendation_prompt_carries_the_table_json(monkeypatch):
    prompts = []

    def fake_complete(prompt, system=None):
        prompts.append((prompt, system))
        return '{"recommended_index": "db.Restaurant.pizzas.createIndex({size: 1})"}'

    monkeypatch.setattr("mongo_x_ray.ai_client.complete", fake_complete)

    record = {
        "query_hash": "904CC0B3",
        "ns": "Restaurant.pizzas",
        "query_pattern": {"type": "find", "pattern": {"size": {"$in": ["small"]}}, "sort": {"price": -1}},
        "plan_summary": "COLLSCAN",
        "has_sort": True,
        "count": 3,
        "duration": 120,
        "keys_examined": 0,
        "docs_examined": 1,
        "n_returned": 1,
    }

    # the recommendation comes back pretty printed
    assert ai.recommend_index(record) == "db.Restaurant.pizzas.createIndex({\n  size: 1\n})"
    prompt, system = prompts[0]
    assert "Restaurant.pizzas" in prompt
    assert "COLLSCAN" in prompt
    assert '"size"' in prompt
    assert '"price"' in prompt
    assert "recommended_index" in system


def test_slow_item_keeps_the_index_recommendation(tmp_path, monkeypatch):
    monkeypatch.setattr("mongo_x_ray.ai_client.get_client", lambda: (object(), "test-model"))
    monkeypatch.setattr(ai, "recommend_index", lambda record: f"db.x.createIndex({{ {record['ns']}: 1 }})")

    item = SlowItem(output_folder=str(tmp_path), config={"ai_analysis": True})
    for log in SLOW_LOGS:
        item.analyze(log)
    item.finalize_analysis()

    assert item._cache
    assert all(record["ai_index"].startswith("db.x.createIndex(") for record in item._cache)

    # The parser reads the records back from the output file, so the
    # recommendations have to be stored before that file is written.
    aggregated = [record for record in item._load_records() if "query_hash" in record]
    assert aggregated
    assert all(record.get("ai_index", "").startswith("db.x.createIndex(") for record in aggregated)


def test_slow_parser_renders_the_index_hint_after_the_hash():
    from mongo_x_ray_log.parsers.slow_parser import SlowParser

    record = {
        "query_hash": "904CC0B3",
        "ns": "Restaurant.pizzas",
        "query_pattern": {"type": "find", "pattern": {"size": "small"}},
        "plan_summary": "COLLSCAN",
        "count": 2,
        "duration": 40,
        "keys_examined": 0,
        "docs_examined": 1,
        "n_returned": 1,
        "ai_index": "db.Restaurant.pizzas.createIndex({size: 1})",
    }

    markup = SlowParser().markdown([record])

    assert 'class="ai-index"' in markup
    assert "AI Recommended Index" in markup
    assert "db.Restaurant.pizzas.createIndex({size: 1})" in markup
    # the badge follows the query hash link in the first cell
    assert markup.index("[904CC0B3](#0)") < markup.index('class="ai-index"')

    without = dict(record)
    without.pop("ai_index")
    assert 'class="ai-index"' not in SlowParser().markdown([without])


def test_index_recommendation_is_pretty_printed():
    formatted = ai.format_index_recommendation("db.Restaurant.pizzas.createIndex({ size: 1, price: -1 })")

    assert formatted == "db.Restaurant.pizzas.createIndex({\n  size: 1,\n  price: -1\n})"

    with_options = ai.format_index_recommendation(
        'db.pizzas.createIndex({ size: 1 }, { partialFilterExpression: { size: "small" } })'
    )
    assert with_options.startswith("db.pizzas.createIndex({\n  size: 1\n}, {")
    assert '    size: "small"\n' in with_options

    # already formatted input is left alone
    assert ai.format_index_recommendation("db.a.createIndex({\n  a: 1\n})") == "db.a.createIndex({\n  a: 1\n})"


def test_bare_key_pattern_is_wrapped_in_create_index(monkeypatch):
    monkeypatch.setattr(
        "mongo_x_ray.ai_client.complete",
        lambda prompt, system=None: '{"recommended_index": "{ size: 1, price: -1 }"}',
    )

    recommendation = ai.recommend_index({"ns": "Restaurant.pizzas", "query_pattern": {"pattern": {"size": "small"}}})

    assert recommendation == "db.pizzas.createIndex({\n  size: 1,\n  price: -1\n})"


def test_sample_viewer_shows_the_ai_block_only_when_present():
    from pathlib import Path

    import mongo_x_ray_log

    snippet = Path(mongo_x_ray_log.__file__).parent / "templates" / "log" / "snippets" / "SlowParser_3.raw.js"
    js = snippet.read_text(encoding="utf-8")

    assert "// AI Recommended Index" in js
    assert "// Query Sample" in js
    # the AI block is optional, so the viewer still works without a key
    assert "if (row.ai_index)" in js


def test_sample_viewers_use_javascript_highlighting():
    from mongo_x_ray_log.parsers.slow_parser import SlowParser
    from mongo_x_ray_log.parsers.wef_parser import WEFParser

    record = {
        "query_hash": "904CC0B3",
        "ns": "Restaurant.pizzas",
        "query_pattern": {"type": "find", "pattern": {"size": "small"}},
        "plan_summary": "COLLSCAN",
        "count": 2,
        "duration": 40,
        "keys_examined": 0,
        "docs_examined": 1,
        "n_returned": 1,
    }

    slow_markup = SlowParser().markdown([record])
    assert "```javascript" in slow_markup
    assert "```json" not in slow_markup

    wef_markup = WEFParser().markdown([{"id": 22601, "severity": "w", "msg": "warn", "timestamp": [1], "sample": {}}])
    assert "```javascript" in wef_markup
