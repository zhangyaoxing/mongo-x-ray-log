"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.version import Version
from mongo_x_ray_log.parsers.client_meta_parser import ClientMetaParser

DATA = [
    {
        "doc": {
            "application": {"name": "mlaunch v1.7.2"},
            "driver": {"name": "PyMongo|c", "version": "4.14.1"},
            "os": {"type": "Darwin", "name": "Darwin", "architecture": "arm64", "version": "15.7"},
            "platform": "CPython 3.11.12.final.0",
        },
        "ips": [
            {"ip": "192.168.0.2", "count": 2},
            {"ip": "192.168.0.3", "count": 1},
        ],
    },
    {
        "doc": {
            "driver": {"name": "NetworkInterfaceTL", "version": "5.0.14"},
            "os": {"type": "Darwin", "name": "Mac OS X", "architecture": "x86_64", "version": "24.6.0"},
        },
        "ips": [{"ip": "192.168.0.1", "count": 1}],
    },
    {
        "doc": {
            "application": {"name": "myapp"},
            "driver": {"name": "mongo-go-driver", "version": "v1.10.0"},
            "os": {"type": "Linux", "name": "Linux", "architecture": "x86_64", "version": "1"},
        },
        "ips": [{"ip": "10.0.0.1", "count": 1}],
    },
]


def test_client_meta_parser_output_structure():
    parser = ClientMetaParser()
    output = parser.parse(DATA, server_version=Version.parse("7.0.0"))
    assert len(output) == 3
    assert output[0]["type"] == "table"
    assert output[1]["type"] == "chart"
    assert output[2]["type"] == "chart"
    # Charts aggregate client counts by driver and by IP
    assert output[1]["data"] == {"PyMongo|c": 3, "NetworkInterfaceTL": 1, "mongo-go-driver": 1}
    assert output[2]["data"] == {"192.168.0.2": 2, "192.168.0.3": 1, "192.168.0.1": 1, "10.0.0.1": 1}


def test_client_meta_parser_marks_incompatible_drivers_red():
    parser = ClientMetaParser()
    output = parser.parse(DATA, server_version=Version.parse("7.0.0"))
    rows = output[0]["rows"]
    # Rows are sorted by application name, then driver name
    assert rows[0][0] == "mlaunch v1.7.2"
    myapp_row = next(row for row in rows if row[0] == "myapp")
    assert '<span style="color:red;">mongo-go-driver v1.10.0</span>' in myapp_row[1]
    # Compatible and internal drivers are not marked red
    for row in rows:
        if row[0] != "myapp":
            assert "color:red" not in row[1]


def test_client_meta_parser_markdown_renders_table_and_charts():
    parser = ClientMetaParser()
    md = parser.markdown(DATA, server_version=Version.parse("7.0.0"))
    assert "Client Metadata" in md
    assert "|NetworkInterfaceTL 5.0.14|" in md
    assert "Number of Clients By Driver" in md
    assert "Number of Clients By IP" in md
