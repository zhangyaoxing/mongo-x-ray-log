"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.version import Version
from mongo_x_ray_log.rules.driver_compatibility_rule import (
    DriverCompatibilityRule,
    _parse_driver_matrix,
    load_driver_matrix,
)


def _cache_entry(driver_name, driver_version, app_name="myapp"):
    return {
        "doc": {
            "application": {"name": app_name},
            "driver": {"name": driver_name, "version": driver_version},
        },
        "ips": [{"ip": "10.0.0.1", "count": 1}],
    }


def test_driver_compatibility_rule_reports_incompatible_drivers():
    server_version = Version.parse("7.0.0")
    rule = DriverCompatibilityRule({})
    data = [
        _cache_entry("mongo-java-driver|sync", "3.12.10"),
        _cache_entry("PyMongo", "4.14.1", app_name="app2"),
        {
            "doc": {
                "driver": {"name": "NetworkInterfaceTL", "version": "5.0.31"},
            },
            "ips": [{"ip": "10.0.0.3", "count": 1}],
        },
    ]
    test_results, parsed = rule.apply(data, server_version=server_version, extra_info={"host": "test-host"})
    assert parsed == data
    assert len(test_results) == 1
    assert test_results[0]["host"] == "test-host"
    assert test_results[0]["title"] == "Incompatible Driver Version"
    assert "mongo-java-driver|sync 3.12.10" in test_results[0]["description"]
    assert "4.10" in test_results[0]["description"]


def test_driver_compatibility_rule_skips_when_server_version_unknown():
    rule = DriverCompatibilityRule({})
    data = [_cache_entry("mongo-java-driver|sync", "3.12.10")]
    test_results, _ = rule.apply(data, server_version=None, extra_info={"host": "test-host"})
    assert test_results == []


def test_driver_compatibility_rule_ignores_internal_drivers():
    server_version = Version.parse("7.0.0")
    rule = DriverCompatibilityRule({})
    data = [
        _cache_entry("NetworkInterfaceTL", "5.0.31"),
        _cache_entry("NetworkInterfaceTL-ReplNetwork", "7.0.37"),
        _cache_entry("MongoDB Internal Client", "7.0.2"),
    ]
    test_results, _ = rule.apply(data, server_version=server_version, extra_info={"host": "test-host"})
    assert test_results == []


def test_matrix_versions_may_be_written_as_strings():
    # The compatibility table is maintained by hand, where "1.15" is easier to
    # read than [1, 15].
    matrix = _parse_driver_matrix({"mongoc": "1.15", "mongo-java-driver": "100.0"})

    assert matrix["mongoc"] == Version.parse("1.15.0")
    assert matrix["mongo-java-driver"] == Version.parse("100.0.0")


def test_matrix_versions_may_still_be_written_as_arrays():
    matrix = _parse_driver_matrix({"mongoc": [1, 15], "mongo-java-driver": [100, 0]})

    assert matrix["mongoc"] == Version.parse("1.15.0")
    assert matrix["mongo-java-driver"] == Version.parse("100.0.0")


def test_matrix_sections_and_formats_can_be_mixed():
    matrix = _parse_driver_matrix({"mongoc": "1.15", "mongocxx": [3, 4]})

    assert matrix["mongoc"].version_array == [1, 15, 0, 0]
    assert matrix["mongocxx"].version_array == [3, 4, 0, 0]


def test_the_shipped_matrix_loads_for_a_known_server_version():
    # Whatever the format of the shipped file, loading it must not raise.
    matrix = load_driver_matrix(Version.parse("7.0.0"))

    assert matrix
    assert all(isinstance(version, Version) for version in matrix.values())
