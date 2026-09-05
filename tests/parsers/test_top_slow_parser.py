"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_log.parsers.top_slow_parser import TopSlowParser


def _record():
    return {
        "query_hash": "ABC123",
        "ns": "test.pizzas",
        "query_pattern": {"type": "find", "pattern": {"size": {"$in": 1}}},
        "duration": 100,
        "count": 2,
        "n_returned": 1,
        "keys_examined": 10,
        "docs_examined": 10,
        "plan_summary": "COLLSCAN",
    }


def test_top_slow_parser_code_columns_left_aligned():
    parser = TopSlowParser()
    output = parser.parse([_record()])
    header = output[0]["header"]
    columns = {h["text"]: h.get("align", "center") for h in header}
    # The Pattern and Details code blocks must be left-aligned, not centered
    assert columns["Pattern"] == "left"
    assert columns["Details"] == "left"


def test_top_slow_parser_table_shape():
    parser = TopSlowParser()
    output = parser.parse([_record()])
    assert output[0]["type"] == "table"
    row = output[0]["rows"][0]
    assert "<pre>" in row[2] and "<pre>" in row[3]
