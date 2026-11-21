"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

# `mongodb.html` is the optional MongoDB-styled report template (issue #372):
# the theme is inlined through {{ style }} - no remote stylesheet or font - and
# the chart/highlighting libraries stay on the CDNs used by `full.html`.
from pathlib import Path

from mongo_x_ray.utils import inject_assets

TEMPLATE_ROOT = Path(__file__).parent.parent / "src" / "mongo_x_ray_log" / "templates"
TEMPLATE = TEMPLATE_ROOT / "log" / "mongodb.html"


def _inject() -> str:
    return inject_assets(TEMPLATE.read_text(encoding="utf-8"), "log", template_root=TEMPLATE_ROOT, theme="mongodb")


def test_mongodb_template_inlines_the_theme():
    html = _inject()

    # Theme and shared styles are inlined; nothing is fetched as a stylesheet.
    assert "--lg-green-base" in html
    assert "--bgColor-muted" in html
    assert '<link rel="stylesheet"' not in html
    # Appended after the shared styles so the theme wins the cascade.
    assert html.index("--bgColor-muted") < html.index("--lg-green-base")


def test_mongodb_template_keeps_the_libraries_and_placeholders():
    html = _inject()

    assert "cdn.jsdelivr.net/npm/chart.js" in html
    assert "highlight.js" in html
    assert "chartjs-plugin-zoom" in html
    assert "hammerjs" in html
    assert "mongo-header" in html
    # Filled in by `inject_assets`; `{{ content }}` is filled in by the framework.
    assert "{{ style }}" not in html
    assert "{{ script }}" not in html
    assert "{{ pre_script }}" not in html
    assert "{{ content }}" in html
