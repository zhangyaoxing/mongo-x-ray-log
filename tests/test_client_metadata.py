"""
Copyright (c) 2025 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import io
import json

from bson import json_util
from mongo_x_ray.version import Version

from mongo_x_ray_log.log_items.client_meta_item import (
    COMPATIBILITY_MATRIX_JSON,
    ClientMetaItem,
    is_driver_compatible,
    parse_version_from_log,
)
from tests.mocking import gen_mock_write_output

LOGS = [
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.220+02:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn3","msg":"client metadata","attr":{"remote":"192.168.0.1:51013","client":"conn3","doc":{"driver":{"name":"NetworkInterfaceTL","version":"5.0.14"},"os":{"type":"Darwin","name":"Mac OS X","architecture":"x86_64","version":"24.6.0"}}}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.400+02:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn4","msg":"client metadata","attr":{"remote":"192.168.0.1:51014","client":"conn4","doc":{"driver":{"name":"NetworkInterfaceTL-ReplNetwork","version":"7.0.37"},"os":{"type":"Darwin","name":"Mac OS X","architecture":"x86_64","version":"24.6.0"}}}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.800+02:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn7","msg":"client metadata","attr":{"remote":"192.168.0.4:51040","client":"conn7","doc":{"driver":{"name":"MongoDB Internal Client","version":"7.0.2"},"os":{"type":"Darwin","name":"Mac OS X","architecture":"x86_64","version":"24.6.0"}}}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.993+02:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn5","msg":"client metadata","attr":{"remote":"192.168.0.2:51028","client":"conn5","doc":{"driver":{"name":"PyMongo|c","version":"4.14.1"},"os":{"type":"Darwin","name":"Darwin","architecture":"arm64","version":"15.7"},"platform":"CPython 3.11.12.final.0","application":{"name":"mlaunch v1.7.2"}}}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:51.998+02:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn6","msg":"client metadata","attr":{"remote":"192.168.0.2:51031","client":"conn6","doc":{"driver":{"name":"PyMongo|c","version":"4.14.1"},"os":{"type":"Darwin","name":"Darwin","architecture":"arm64","version":"15.7"},"platform":"CPython 3.11.12.final.0","application":{"name":"mlaunch v1.7.2"}}}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:39:52.000+02:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn8","msg":"client metadata","attr":{"remote":"192.168.0.3:51032","client":"conn8","doc":{"driver":{"name":"PyMongo|c","version":"4.14.1"},"os":{"type":"Darwin","name":"Darwin","architecture":"arm64","version":"15.7"},"platform":"CPython 3.11.12.final.0","application":{"name":"mlaunch v1.7.2"}}}}'
    ),
]


def test_client_metadata_item():
    item = ClientMetaItem(output_folder="/tmp", config={})
    output, item._write_output = gen_mock_write_output(item)
    for log in LOGS:
        item.analyze(log)
    item.finalize_analysis()

    assert len(output) == 4
    # Internal drivers are still collected so they show up in the results table
    assert output[0]["doc"]["driver"]["name"] == "NetworkInterfaceTL"
    assert output[0]["ips"][0]["ip"] == "192.168.0.1"
    assert output[0]["ips"][0]["count"] == 1
    assert output[1]["doc"]["driver"]["name"] == "NetworkInterfaceTL-ReplNetwork"
    assert output[1]["ips"][0]["ip"] == "192.168.0.1"
    assert output[1]["ips"][0]["count"] == 1
    assert output[2]["doc"]["driver"]["name"] == "MongoDB Internal Client"
    assert output[2]["ips"][0]["ip"] == "192.168.0.4"
    assert output[2]["ips"][0]["count"] == 1
    result = output[3]
    assert result["doc"]["driver"]["name"] == "PyMongo|c"
    assert result["ips"][0]["ip"] == "192.168.0.2"
    assert result["ips"][0]["count"] == 2
    assert result["ips"][1]["ip"] == "192.168.0.3"
    assert result["ips"][1]["count"] == 1


LOGS_2 = [
    {"name": "NetworkInterfaceTL", "version": "5.0.31"},
    {"name": "mongo-csharp-driver", "version": "2.21.0.0"},
    {"name": "mongo-java-driver|sync", "version": "3.12.10"},
    {"name": "mongoc / mongocxx", "version": "1.26.3 / 3.8.1"},
    {
        "name": "mongoc / ext-mongodb:PHP / PHPLIB/symfony-mongodb ",
        "version": "1.25.2 / 1.17.2 / 1.17.0/2.6.1 ",
    },
    {"name": "mongo-java-driver|mongo-scala-driver", "version": "unknown|2.3.0"},
    {"name": "mongo-go-driver", "version": "v1.12.0-cloud"},
]


def test_version_parser():
    target_drivers = [
        "NetworkInterfaceTL",
        "mongo-csharp-driver",
        "mongo-java-driver",
        "mongocxx",
        "ext-mongodb:PHP",
        "mongo-scala-driver",
        "mongo-go-driver",
    ]
    expected_versions = [
        "5.0.31",
        "2.21.0.0",
        "3.12.10",
        "3.8.1",
        "1.17.2",
        "2.3.0",
        "1.12.0",
    ]
    for log, target_driver, expected_version in zip(LOGS_2, target_drivers, expected_versions):
        parsed_version = parse_version_from_log(log["name"], log["version"], target_driver)
        assert parsed_version == Version.parse(expected_version), (
            f"Expected {expected_version}, got {parsed_version} for driver {target_driver}"
        )


def test_is_driver_compatible():
    # Assume server version is 7.0.0 for testing
    server_version = Version.parse("7.0.0")
    with COMPATIBILITY_MATRIX_JSON.open("r") as f:
        compatibility_matrix = json.load(f)
    matrix_70 = {k: Version(v) for k, v in compatibility_matrix.get("7.0", {}).items()}
    expected_compatibility = [True, True, False, True, True, False, True]
    for log, expected in zip(LOGS_2, expected_compatibility):
        is_compatible = is_driver_compatible(log["name"], log["version"], server_version, matrix_70)
        assert is_compatible == expected, (
            f"Expected compatibility {expected} for driver {log['name']}, got {is_compatible}"
        )
    # Internal drivers (whose name *contains* NetworkInterfaceTL, or is exactly
    # "MongoDB Internal Client") are ignored by the compatibility check, so they are
    # never flagged as incompatible.
    assert is_driver_compatible("NetworkInterfaceTL-ReplNetwork", "7.0.37", server_version, matrix_70) is True
    assert is_driver_compatible("MongoDB Internal Client", "7.0.2", server_version, matrix_70) is True


def test_internal_drivers_still_displayed_in_results_table(tmp_path):
    # Internal drivers are ignored by the compatibility check, but the results table must
    # still show them (not red, since they are never flagged as incompatible).
    item = ClientMetaItem(output_folder=str(tmp_path), config={})
    item._server_version = Version.parse("7.0.0")
    for log in LOGS:
        item.analyze(log)
    item.finalize_analysis()

    buf = io.StringIO()
    item.review_results_markdown(buf)
    md = buf.getvalue()

    # All internal drivers are still displayed as table rows
    assert "|NetworkInterfaceTL 5.0.14|" in md
    assert "|NetworkInterfaceTL-ReplNetwork 7.0.37|" in md
    assert "|MongoDB Internal Client 7.0.2|" in md
    # ... and they are not marked red as incompatible
    assert '<span style="color:red;">NetworkInterfaceTL' not in md
    assert '<span style="color:red;">MongoDB Internal Client' not in md
