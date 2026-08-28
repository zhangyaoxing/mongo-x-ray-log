"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import json
from importlib.resources import files
from re import search, split
from typing import Optional

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray.utils import get_script_path
from mongo_x_ray.version import Version
from mongo_x_ray_log.rules.base_rule import BaseRule

COMPATIBILITY_MATRIX_JSON = files("mongo_x_ray") / "compatibility_matrix.json"

# Internal drivers used by MongoDB itself, not by user-facing drivers, so they are
# not in the compatibility matrix. They are ignored by the compatibility check but
# are still displayed in the results table.
INTERNAL_DRIVER_NAMES = ("NetworkInterfaceTL", "MongoDB Internal Client")

COMPATIBILITY_MATRIX_URL = "https://www.mongodb.com/docs/drivers/compatibility/"


def load_driver_matrix(server_version: Optional[Version]) -> dict[str, Version]:
    """Load the minimum compatible driver versions for the given server version.

    Args:
        server_version: The MongoDB server version detected from the log.

    Returns:
        dict: Mapping of driver name to its minimum compatible version. Empty
            when the server version cannot be determined.
    """
    matrix_path = get_script_path(COMPATIBILITY_MATRIX_JSON)
    with open(matrix_path, "r", encoding="utf-8") as f:
        compatibility_matrix = json.load(f)
    server_compatible_version = server_version.to_compatibility_str() if server_version else "Unknown"
    driver_matrix = compatibility_matrix.get(server_compatible_version, {})
    return {k: Version(v) for k, v in driver_matrix.items()}


def _is_internal_driver(log_driver_name: str) -> bool:
    """Return True for drivers used internally by MongoDB itself."""
    return "NetworkInterfaceTL" in log_driver_name or log_driver_name == "MongoDB Internal Client"


def _find_driver_in_matrix(log_driver_name: str, matrix) -> tuple:
    """Find the driver in the compatibility matrix that matches *log_driver_name*.

    Some drivers use other drivers internally (e.g. PHP uses the C driver, Scala
    uses the Java driver). The sequence matters, so the last match wins.

    Returns:
        tuple: (driver_name, min_version). Both None when there is no match.
    """
    driver_name = None
    min_version = None
    for k, v in matrix.items():
        if k in log_driver_name:
            driver_name = k
            min_version = v
    return driver_name, min_version


def check_driver_compatibility(
    log_driver_name: str, log_driver_version: str, server_version: Optional[Version], matrix
) -> tuple:
    """Check whether a driver is compatible with the given MongoDB server version.

    Args:
        log_driver_name: The driver name reported in the log.
        log_driver_version: The driver version reported in the log.
        server_version: The MongoDB server version, or None if it cannot be determined.
        matrix: The compatibility matrix (driver name -> minimum compatible version).

    Returns:
        tuple: (is_compatible: bool, min_version: Optional[Version]).
    """
    if _is_internal_driver(log_driver_name):
        return True, None
    if not server_version or log_driver_version == "Unknown":
        # Can't determine the server version or the driver version, assume compatible.
        return True, None
    try:
        driver_name, min_version = _find_driver_in_matrix(log_driver_name, matrix)
        if driver_name is None or min_version is None:
            return True, None
        driver_ver = parse_version_from_log(log_driver_name, log_driver_version, driver_name)
        return (not driver_ver or driver_ver >= min_version), min_version
    except Exception:
        return True, None


def is_driver_compatible(log_driver_name: str, log_driver_version: str, server_version: Version, matrix) -> bool:
    """Return True if the driver is compatible with the given MongoDB server version."""
    compatible, _ = check_driver_compatibility(log_driver_name, log_driver_version, server_version, matrix)
    return compatible


def parse_version_from_log(driver_name: str, driver_version: str, target_driver_name: str) -> Optional[Version]:
    """Parse driver version from log line"""
    # Driver version from the log can have different forms. Some examples are:
    #  - {"name":"mongo-csharp-driver","version":"2.21.0.0"}
    #  - {"name":"mongo-java-driver|sync","version":"3.12.10"}
    #  - {"name":"mongoc / mongocxx","version":"1.26.3 / 3.8.1"}
    #  - {"name":"mongoc / ext-mongodb:PHP / PHPLIB/symfony-mongodb ","version":"1.25.2 / 1.17.2 / 1.17.0/2.6.1 "}
    #  - {"name":"mongo-java-driver|mongo-scala-driver","version":"unknown|2.3.0"}
    #  - {"name":"mongo-go-driver","version":"v1.12.0-cloud"}
    # We need to extract the relevant part for comparison.
    # Some drivers are internal only, e.g., NetworkInterfaceTL, we skip those.
    #  - {"name":"NetworkInterfaceTL","version":"5.0.31"}
    name_parts = [part.strip(" ") for part in split("[|/]", driver_name)]
    version_parts = [part.strip(" ") for part in split("[|/]", driver_version)]
    for name_part, version_part in zip(name_parts, version_parts):
        if name_part == target_driver_name:
            version = search(r"\d+(\.\d+)*", version_part.strip())
            return Version.parse(version.group(0) if version else None)
    # Because | is used both as delimiter and in driver names, we need to do one more check
    # Drivers like mongo-java-driver|sync will go here if not matched above
    if target_driver_name == driver_name:
        version = search(r"\d+(\.\d+)*", driver_version.strip())
        return Version.parse(version.group(0) if version else None)

    return None


class DriverCompatibilityRule(BaseRule):
    """Checks that the client drivers are compatible with the MongoDB server version."""

    def __init__(self, config=None):
        super().__init__(config)
        self._rule_desc.append("Checks if the client drivers are compatible with the MongoDB server version.")

    def apply(self, data: list, **kwargs) -> tuple:
        """Check the driver compatibility of all collected client metadata.

        Args:
            data (list): The collected client metadata cache, a list of
                ``{"doc": {...}, "ips": [...]}`` dicts.
            server_version (Version, optional): The MongoDB server version detected
                from the log, passed as a kwarg.
            extra_info (dict, optional): Additional information such as ``host``.

        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        server_version = kwargs.get("server_version")
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        test_results = []
        if not server_version:
            # Without the server version, compatibility cannot be determined.
            return test_results, data
        matrix = load_driver_matrix(server_version)
        for entry in data:
            doc = entry.get("doc", {})
            driver = doc.get("driver", {})
            driver_name = driver.get("name", "Unknown")
            driver_version = driver.get("version", "Unknown")
            compatible, min_version = check_driver_compatibility(driver_name, driver_version, server_version, matrix)
            if compatible:
                continue
            application = doc.get("application", {}).get("name", "Unknown")
            test_results.append(
                {
                    "host": host,
                    "severity": SEVERITY.MEDIUM,
                    "title": "Incompatible Driver Version",
                    "description": (
                        f"Driver `{driver_name} {driver_version}` (application `{application}`) does not "
                        f"support MongoDB `{server_version}`. The minimum compatible version is "
                        f"`{min_version}`. Reference: [Compatibility Matrix]({COMPATIBILITY_MATRIX_URL})."
                    ),
                }
            )
        return test_results, data
