"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import to_json
from mongo_x_ray_log.parsers.base_parser import BaseParser


class InfoParser(BaseParser):
    """Render the basic instance information as key/value tables and code blocks."""

    def parse(self, data: dict, **kwargs) -> list:
        output_list: list[dict] = []

        process = data.get("process", None)
        build_info = data.get("build_info", None)
        fcv = data.get("fcv", None)
        if build_info or process:
            rows = []
            version = build_info.get("version", "Unknown") if build_info else "Unknown"
            if build_info and "enterprise" in build_info.get("modules", []):
                version += "-ent"
            rows.append(["MongoDB Version", version])
            if fcv:
                rows.append(["Feature Compatibility Version", fcv])
            if process:
                rows.append(["PID", process.get("pid", "Unknown")])
                rows.append(["Host", process.get("host", "Unknown")])
                rows.append(["Port", process.get("port", "Unknown")])
            output_list.append(
                {
                    "type": "table",
                    "caption": "Process Info",
                    "header": [{"width": "250px", "text": "Key"}, {"width": "*", "text": "Value", "align": "left"}],
                    "rows": rows,
                }
            )

        cert_info = data.get("cert_info", None)
        if cert_info:
            rows = [
                ["Key File", cert_info.get("keyFile", "Unknown")],
                ["Type", cert_info.get("type", "Unknown")],
                ["Subject", cert_info.get("subject", "Unknown")],
                ["Issuer", cert_info.get("issuer", "Unknown")],
                ["Valid From", cert_info.get("notValidBefore", "Unknown")],
                ["Valid To", cert_info.get("notValidAfter", "Unknown")],
            ]
            output_list.append(
                {
                    "type": "table",
                    "caption": "Certificate Info",
                    "header": [{"width": "250px", "text": "Key"}, {"width": "*", "text": "Value", "align": "left"}],
                    "rows": rows,
                }
            )

        guest_os = data.get("os", None)
        if guest_os:
            output_list.append(
                {
                    "type": "table",
                    "caption": "Operating System",
                    "header": [{"width": "250px", "text": "Key"}, {"width": "*", "text": "Value", "align": "left"}],
                    "rows": [
                        ["Name", guest_os.get("name", "Unknown")],
                        ["Version", guest_os.get("version", "Unknown")],
                    ],
                }
            )

        replica_set = data.get("replica_set", {})
        rs_config = replica_set.get("config", None)
        if replica_set:
            rows = []
            for member in rs_config.get("members", []):
                rows.append(
                    [
                        member.get("_id", "Unknown"),
                        member.get("host", "Unknown"),
                        member.get("arbiterOnly", False),
                        member.get("priority", 0),
                        member.get("votes", 0),
                        member.get("hidden", False),
                        member.get("secondaryDelaySecs", 0),
                    ]
                )
            output_list.append(
                {
                    "type": "table",
                    "caption": f"Replica Set Config ({rs_config.get('_id', 'Unknown')})",
                    "notes": f"Member state: `{replica_set.get('memberState', 'Unknown')}`",
                    "header": [
                        {"width": "80px", "text": "Member"},
                        {"width": "*", "text": "Host"},
                        {"width": "80px", "text": "Arbiter"},
                        {"width": "80px", "text": "Priority"},
                        {"width": "80px", "text": "Votes"},
                        {"width": "80px", "text": "Hidden"},
                        {"width": "80px", "text": "Delay"},
                    ],
                    "rows": rows,
                }
            )
            if rs_config is not None:
                output_list.append(
                    {
                        "type": "code",
                        "language": "json",
                        "code": to_json(rs_config, indent=4),
                    }
                )

        command_line_options = data.get("command_line_options", None)
        if command_line_options:
            output_list.append(
                {
                    "type": "code",
                    "language": "json",
                    "caption": "Command Line Options",
                    "code": to_json(command_line_options, indent=4),
                }
            )

        return output_list


__all__ = ["InfoParser"]
