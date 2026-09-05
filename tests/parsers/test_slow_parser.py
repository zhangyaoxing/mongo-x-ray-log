"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_log.parsers.slow_parser import SlowParser

RAW_LINE = {"id": 51803, "attr": {"ns": "test.c", "durationMillis": 10}}

AGGREGATED = {
    "query_hash": "ABC123",
    "ns": "test.c",
    "query_pattern": {"type": "find", "pattern": {}},
    "plan_summary": "IXSCAN",
    "keys_examined": 1,
    "docs_examined": 1,
    "n_returned": 1,
    "count": 1,
    "duration": 10,
}


def test_slow_parser_order_charts_then_table_then_code():
    parser = SlowParser()
    output = parser.parse([RAW_LINE, AGGREGATED])
    # Charts first, then the table, then the shared code block, then the wiring
    assert [block["type"] for block in output] == ["chart", "table", "code", "chart"]
    # The first chart carries the raw lines, the wiring chart the top-N records
    assert output[0]["data"] == [RAW_LINE]
    assert output[3]["data"] == [AGGREGATED]
    assert output[1]["rows"][0][0] == "[ABC123](#0)"


def test_slow_parser_markdown_order():
    parser = SlowParser()
    md = parser.markdown([RAW_LINE, AGGREGATED])
    chart_pos = md.find("// SlowParser")
    table_pos = md.find("Top Slow Operations")
    code_pos = md.find("// Click query hash to display sample query...")
    assert 0 <= chart_pos < table_pos < code_pos
