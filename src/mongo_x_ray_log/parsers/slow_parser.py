"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

import html as html_mod

from mongo_x_ray.shared import AI_ICON
from mongo_x_ray.utils import escape_markdown, format_json_md
from mongo_x_ray_log.parsers.base_parser import BaseParser


class SlowParser(BaseParser):
    """Render the slow operations: a top-N table with sample viewers and the
    scatter charts (duration / scanned / scanned objects) shown as tabs.

    The output file mixes two record kinds: the raw slow query lines (streamed
    during analysis, no top-level ``query_hash``) and the aggregated top-N
    records (written at finalize, with a top-level ``query_hash``).
    """

    def parse(self, data: list, **kwargs) -> list:
        top_n = [record for record in data if "query_hash" in record]
        raw_lines = [record for record in data if "query_hash" not in record]

        rows = []
        for i, line_json in enumerate(top_n):
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
                "Has Sort Stage": has_sort,
            }
            plan_summary = line_json.get("plan_summary", "N/A")
            plan_summary = f"`{escape_markdown(plan_summary if plan_summary != '' else 'N/A')}`"
            sort = query_pattern.get("sort", {})
            pattern_cell = f"Filter: <br><pre>{format_json_md(pattern)}</pre>"
            if sort:
                pattern_cell += f"<br>Sort: <br><pre>{format_json_md(sort)}</pre>"
            hash_cell = f"[{query_hash}](#{i})"
            ai_index = line_json.get("ai_index")
            if ai_index:
                # Markdown collapses raw newlines inside a table cell, so the
                # formatted command has to keep them as character references;
                # `.ai-index-command` renders with `white-space: pre`.
                tooltip = html_mod.escape(str(ai_index)).replace("\r\n", "\n").replace("\n", "&#10;")
                hash_cell += (
                    f' <span class="ai-index">{AI_ICON}'
                    f'<span class="ai-index-tooltip"><span class="ai-index-title">AI Recommended Index</span>'
                    f'<span class="ai-index-command">{tooltip}</span></span></span>'
                )
            rows.append(
                [
                    hash_cell,
                    f"`{op}` on `{ns}`",
                    pattern_cell,
                    f"<pre>{format_json_md(details)}</pre>",
                    f"{plan_summary}",
                ]
            )
        return [
            # Chart tabs block: the scatter charts first, fed with the raw log lines
            {"type": "chart", "data": raw_lines},
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
            # The shared sample code block comes last
            {"type": "code", "language": "json", "code": "// Click query hash to display sample query..."},
            # Wiring chart block: attaches click handlers to the table anchors
            {"type": "chart", "data": top_n},
        ]


__all__ = ["SlowParser"]
