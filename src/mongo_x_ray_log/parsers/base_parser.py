"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.

Log analysis parser base — subclass of the shared core parser.
"""

import os

from mongo_x_ray.parsers.base_parser import BaseParser as CoreBaseParser


class BaseParser(CoreBaseParser):
    """Render log analysis results using the common table/chart format."""

    TEMPLATE_FOLDER = os.path.join("templates", "log", "snippets")
    TEMPLATE_PACKAGE = "mongo_x_ray_log"


__all__ = ["BaseParser"]
