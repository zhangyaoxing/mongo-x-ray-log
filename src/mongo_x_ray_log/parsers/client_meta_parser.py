"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from typing import Optional

from mongo_x_ray.utils import escape_markdown, tooltip_html, truncate_content
from mongo_x_ray.version import Version
from mongo_x_ray_log.parsers.base_parser import BaseParser
from mongo_x_ray_log.rules.driver_compatibility_rule import (
    COMPATIBILITY_MATRIX_URL,
    is_driver_compatible,
    load_driver_matrix,
)


class ClientMetaParser(BaseParser):
    """Render the collected client metadata (driver, OS, platform, IPs) as tables and charts."""

    def parse(self, data: list, **kwargs) -> list:
        """Parse the collected client metadata into a table and two pie charts.

        Args:
            data (list): The client metadata cache, a list of ``{"doc": {...}, "ips": [...]}`` dicts.
            server_version (Version, optional): The MongoDB server version detected from the log.

        Returns:
            list: The parsed list of table/chart items.
        """
        server_version: Optional[Version] = kwargs.get("server_version")
        driver_matrix = load_driver_matrix(server_version)

        rows: list[list] = []
        driver_count: dict[str, int] = {}
        ip_count: dict[str, int] = {}
        for entry in data:
            doc = entry.get("doc", {})
            full_app = doc.get("application", {}).get("name", "Unknown")
            trunc_app = truncate_content(full_app)
            app_html = (
                tooltip_html(escape_markdown(full_app), escape_markdown(trunc_app))
                if full_app != trunc_app
                else escape_markdown(full_app)
            )
            driver = doc.get("driver", {})
            driver_name = driver.get("name", "Unknown")
            driver_version = driver.get("version", "Unknown")
            full_driver = escape_markdown(f"{driver_name} {driver_version}")
            is_compatible = server_version is None or is_driver_compatible(
                driver_name,
                driver_version,
                server_version,
                driver_matrix,
            )
            if not is_compatible:
                full_driver = f'<span style="color:red;">{full_driver}</span>'
            os = doc.get("os", {})
            os_type = os.get("type", "Unknown")
            os_name = os.get("name", "Unknown")
            os_arch = os.get("architecture", "Unknown")
            os_version = os.get("version", "Unknown")
            os_str = escape_markdown(
                f"{os_name if os_name != 'Unknown' else os_type} {os_arch} {os_version if os_version != 'Unknown' else ''}"
            )
            platform = escape_markdown(doc.get("platform", "Unknown"))
            ips = [f"{ip['ip']} ({ip['count']} times)" for ip in entry.get("ips", [])]
            ips_html = tooltip_html(", ".join(ips), f"{ips[0]} {'...' if len(ips) > 1 else ''}") if ips else "-"
            rows.append([app_html, full_driver, os_str, platform, ips_html])

            driver_count[driver_name] = driver_count.get(driver_name, 0) + sum(
                ip.get("count", 0) for ip in entry.get("ips", [])
            )
            for ip in entry.get("ips", []):
                ip_count[ip["ip"]] = ip_count.get(ip["ip"], 0) + ip.get("count", 0)

        # Sort by Application name, then driver name
        rows.sort(key=lambda row: (row[0].lower(), row[1].lower()))

        notes = ""
        if server_version:
            notes = (
                f'**Drivers that don\'t support current MongoDB <span style="color: red;">{server_version}</span> '
                f'are marked <span style="color:red;">RED</span>. Reference: '
                f"[Compatibility Matrix]({COMPATIBILITY_MATRIX_URL})**"
            )
        else:
            notes = (
                '**<span style="color: red;">Unable to determine server version to mark incompatible drivers. '
                "Log may be truncated by user.</span>**"
            )

        return [
            {
                "type": "table",
                "caption": "Client Metadata",
                "notes": notes,
                "header": [
                    {"width": "200px", "text": "Application"},
                    {"width": "200px", "text": "Driver"},
                    {"width": "200px", "text": "OS"},
                    {"width": "200px", "text": "Platform"},
                    {"width": "*", "text": "Client IPs"},
                ],
                "rows": rows,
            },
            {"type": "chart", "data": driver_count},
            {"type": "chart", "data": ip_count},
        ]


__all__ = ["ClientMetaParser"]
