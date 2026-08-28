"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import html as html_mod

from mongo_x_ray.utils import escape_markdown
from mongo_x_ray_log.parsers.base_parser import BaseParser


class WEFParser(BaseParser):
    """Render the warning/error/fatal log summary as an interactive table.

    The table rows link to the sample log lines; a chart block after the
    table wires up the click handlers (see the WEFParser_3 snippet).
    """

    def parse(self, data: list, **kwargs) -> list:
        rows = []
        for i, line_json in enumerate(data):
            log_id = line_json.get("id", "Unknown")
            severity = line_json.get("severity", "Unknown").upper()
            msg = line_json.get("msg", "")
            count = len(line_json.get("timestamp", []))
            risk_html = ""
            mr = line_json.get("matched_risk")
            if mr:
                rid = html_mod.escape(str(mr.get("id", "")))
                rname = html_mod.escape(str(mr.get("name", ""))).replace("\r\n", "<br>").replace("\n", "<br>")
                rdesc = (
                    html_mod.escape(str(mr.get("description", "")))
                    .replace("\r\n", "<br>")
                    .replace("\n", "<br>")
                    .replace("\r", "<br>")
                )
                risk_html = (
                    f'<span class="risk-badge">RISK-{rid}'
                    f'<span class="risk-tooltip">'
                    f'<span class="risk-name">{rname}</span>'
                    f"{rdesc}</span></span>"
                )
            rows.append((f"[{log_id}](#{i})", severity, escape_markdown(msg), count, risk_html))
        # Sort rows by the rendered text
        rows.sort(key=lambda row: str(row[0]).lower())
        return [
            {
                "type": "table",
                "caption": "Warning/Error/Fatal Logs",
                "header": [
                    {"width": "100px", "text": "Code", "align": "center"},
                    {"width": "100px", "text": "Severity", "align": "center"},
                    {"width": "*", "text": "Message", "align": "left"},
                    {"width": "100px", "text": "Count", "align": "center"},
                    {"width": "150px", "text": "Known Risks"},
                ],
                "rows": rows,
            },
            {"type": "code", "language": "json", "code": "// Click error code to review sample log line..."},
            {"type": "chart", "data": data},
        ]


__all__ = ["WEFParser"]
