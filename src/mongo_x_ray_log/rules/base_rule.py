"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseRule(ABC):
    """Base class for log analysis rules.

    A rule inspects analysed data and produces test results (issues) that are
    rendered in the "Review Test Results" section of the report. It mirrors
    the rule pattern used by the healthcheck and gmd modules.
    """

    def __init__(self, thresholds: Optional[dict] = None):
        self._thresholds: dict = thresholds or {}
        self._rule_desc: list[str] = []

    @abstractmethod
    def apply(self, data: Any, **kwargs) -> tuple:
        """Apply the rule to *data* and return ``(test_results, parsed_data)``."""
        raise NotImplementedError("Subclasses must implement the apply method")

    @property
    def description(self) -> list[str]:
        return self._rule_desc

    @property
    def description_md(self) -> str:
        return "\n".join(f"- {desc}" for desc in self._rule_desc)
