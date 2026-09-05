"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.utils import escape_markdown, format_json_md
from mongo_x_ray_log.parsers.base_parser import BaseParser


class TopSlowParser(BaseParser):
    """Render the top slow operations as an interactive table.

    The table rows link to the sample log lines; a chart block after the
    table wires up the click handlers (see the TopSlowParser_3 snippet).
    """

    def parse(self, data: list, **kwargs) -> list:
        rows = []
        for i, line_json in enumerate(data):
            query_hash = line_json.get("query_hash", "N/A")
            ns = line_json.get("ns", "N/A")
            query_pattern = line_json.get("query_pattern") or {}
            op = query_pattern.get("type", "UNKNOWN")
            pattern = query_pattern.get("pattern", {})
            duration = line_json.get("duration", 0)
            count = line_json.get("count", 0)
            avg_duration = round(duration / count, 2) if count > 0 else 0
            n_returned = line_json.get("n_returned", 0)
            keys_examined = line_json.get("keys_examined", 0)
            docs_examined = line_json.get("docs_examined", 0)
            has_sort = "Yes" if line_json.get("has_sort", False) else "No"
            scanned_per_returned = round(keys_examined / n_returned, 2) if n_returned > 0 else keys_examined
            scannedobj_per_returned = round(docs_examined / n_returned, 2) if n_returned > 0 else docs_examined
            details = {
                "Total Duration (ms)": duration,
                "Count": count,
                "Avg Duration (ms)": avg_duration,
                "Targeting": scanned_per_returned,
                "Targeting (Obj)": scannedobj_per_returned,
                "Has Sort": has_sort,
            }
            plan_summary = line_json.get("plan_summary", "N/A")
            plan_summary = escape_markdown(plan_summary if plan_summary != "" else "N/A")
            rows.append(
                [
                    f"[{query_hash}](#{i})",
                    f"`{op}` on `{ns}`",
                    f"<pre>{format_json_md(pattern)}</pre>",
                    f"<pre>{format_json_md(details)}</pre>",
                    f"{plan_summary}",
                ]
            )
        return [
            {
                "type": "table",
                "caption": "Top Slow Operations",
                "header": [
                    {"width": "120px", "text": "Query Hash"},
                    {"width": "200px", "text": "Op"},
                    {"width": "*", "text": "Pattern", "align": "left"},
                    {"width": "*", "text": "Details", "align": "left"},
                    {"width": "200px", "text": "Plan Summary", "align": "left"},
                ],
                "rows": rows,
            },
            {"type": "code", "language": "json", "code": "// Click query hash to display sample query..."},
            {"type": "chart", "data": data},
        ]


__all__ = ["TopSlowParser"]
