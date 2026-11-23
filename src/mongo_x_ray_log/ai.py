"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.

Section-level AI analysis for the log plugin.

Each report section that carries a pattern worth a second look has an analyzer
here: connection churn, the rate of repeated INFO logs, the slow query rate and
the warning/error/fatal logs. They all summarise the section's statistics first
(a few hundred characters, never the raw log) and ask the shared client in
:mod:`mongo_x_ray.ai_client` for a short verdict, which the item renders as an
"AI Analysis" note at the end of the section.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Optional

_MAX_MESSAGE_CHARS = 180
_MAX_ROWS = 10

_SYSTEM_PROMPT = (
    "You are a MongoDB expert reviewing an analysis report. "
    "Answer in at most three short sentences of plain text: say whether the pattern looks healthy "
    "or suspicious, and what to check next. No markdown, no lists."
)


def _complete(prompt: str) -> Optional[str]:
    """Send a prompt through the shared client and return the text, if any."""
    from mongo_x_ray.ai_client import complete

    result = complete(prompt, system=_SYSTEM_PROMPT)
    text = (result or "").strip()
    return text or None


def _truncate(text: Any, limit: int = _MAX_MESSAGE_CHARS) -> str:
    msg = " ".join(str(text or "").split())
    return msg if len(msg) <= limit else msg[: limit - 1] + "\u2026"


def analyze_connection_rate(records: list[dict]) -> Optional[str]:
    """Analyse per-minute connection churn (created vs ended)."""
    if not records:
        return None

    created = [int(r.get("created", 0)) for r in records]
    ended = [int(r.get("ended", 0)) for r in records]
    open_connections = [int(r.get("total", 0)) for r in records]

    clients: Counter = Counter()
    for record in records:
        for ip, counts in (record.get("byIp") or {}).items():
            clients[ip] += int(counts.get("created", 0))

    lines = [
        f"Minutes observed: {len(records)}",
        f"Connections created per minute: peak {max(created)}, average {sum(created) / len(created):.1f}",
        f"Connections ended per minute: peak {max(ended)}, average {sum(ended) / len(ended):.1f}",
        f"Open connections: peak {max(open_connections)}",
    ]
    if clients:
        top = ", ".join(f"{ip} ({count})" for ip, count in clients.most_common(5))
        lines.append(f"Top clients by connections created: {top}")

    prompt = (
        "MongoDB connection rate analysis. Judge whether this is a normal pattern "
        "(steady churn, no connection leak) or something to investigate.\n" + "\n".join(lines)
    )
    return _complete(prompt)


def analyze_log_rate(records: list[dict]) -> Optional[str]:
    """Analyse the INFO log ids that keep showing up."""
    rows = []
    for entry in records:
        buckets = entry.get("buckets") or []
        total = sum(int(b.get("count", 0)) for b in buckets)
        peak = max((int(b.get("count", 0)) for b in buckets), default=0)
        sample = entry.get("sample") or {}
        rows.append((total, peak, len(buckets), entry.get("id"), _truncate(sample.get("msg", ""))))
    if not rows:
        return None
    rows.sort(reverse=True)

    lines = [f"Log ids with repeated INFO logs: {len(rows)}"]
    for total, peak, minutes, log_id, msg in rows[:_MAX_ROWS]:
        lines.append(f"- [{log_id}] total {total}, peak {peak}/minute, over {minutes} minute(s): {msg}")

    prompt = (
        "MongoDB log rate analysis (INFO logs only, warning/error/fatal are reported elsewhere). "
        "Judge whether these repeated logs look like a healthy pattern or an ongoing problem.\n" + "\n".join(lines)
    )
    return _complete(prompt)


def analyze_slow_rate(records: list[dict]) -> Optional[str]:
    """Analyse the slow query rate and the namespaces behind it."""
    if not records:
        return None

    counts = [int(r.get("count", 0)) for r in records]
    slow_ms = [int(r.get("total_slow_ms", 0)) for r in records]
    namespaces: Counter = Counter()
    for record in records:
        for namespace, values in (record.get("byNs") or {}).items():
            namespaces[namespace] += int(values.get("count", 0))

    lines = [
        f"Minutes observed: {len(records)}",
        f"Slow queries per minute: peak {max(counts)}, average {sum(counts) / len(counts):.1f}",
        f"Slow time per minute: peak {max(slow_ms)} ms, average {sum(slow_ms) / len(slow_ms):.1f} ms",
    ]
    if namespaces:
        top = ", ".join(f"{ns} ({count})" for ns, count in namespaces.most_common(5))
        lines.append(f"Top namespaces by slow queries: {top}")

    prompt = (
        "MongoDB slow query rate analysis. Judge whether this rate and distribution look normal "
        "or indicate a query problem that needs attention.\n" + "\n".join(lines)
    )
    return _complete(prompt)


def analyze_wef(entries: list[dict]) -> Optional[str]:
    """Analyse the warning/error/fatal log messages."""
    if not entries:
        return None

    per_severity: Counter = Counter()
    total = 0
    rows = []
    for entry in entries:
        severity = str(entry.get("severity", "")).upper() or "UNKNOWN"
        occurrences = len(entry.get("timestamp") or [])
        total += occurrences
        per_severity[severity] += occurrences
        rows.append((occurrences, severity, entry.get("id"), _truncate(entry.get("msg", ""))))
    rows.sort(reverse=True)

    lines = [
        f"Distinct warning/error/fatal codes: {len(rows)}, occurrences: {total}",
        "Per severity: " + ", ".join(f"{sev} {count}" for sev, count in per_severity.most_common()),
    ]
    for occurrences, severity, log_id, msg in rows[:_MAX_ROWS]:
        lines.append(f"- [{log_id}] {severity} x{occurrences}: {msg}")

    prompt = (
        "MongoDB warning/error/fatal log analysis. Judge which of these are worth noticing for a "
        "healthy deployment and which are routine noise.\n" + "\n".join(lines)
    )
    return _complete(prompt)
