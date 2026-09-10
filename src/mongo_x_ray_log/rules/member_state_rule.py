"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from typing import Optional

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_log.rules.base_rule import BaseRule

# Replica set states that carry the replica set data plane (any other state is
# considered abnormal).
NORMAL_STATES = ("PRIMARY", "SECONDARY")
# Events whose details carry the member state (mirrors the state trace chart).
STATE_EVENT_IDS = (20722, 21215, 21216, 21358)


class MemberStateRule(BaseRule):
    """Checks that every replica set member ends the analysed period in a normal state.

    A member is reported as abnormal when its last known state (from the member
    state change events) is anything other than PRIMARY or SECONDARY.
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._rule_desc.append("Checks if any replica set member is running in an abnormal state.")

    def apply(self, data: dict, **kwargs) -> tuple:
        """Check the member state trace events for abnormal member states.

        Args:
            data (dict): The member state trace cache, a dict of
                ``{host: [events]}`` where each event has ``id`` and ``details``
                (with an optional ``new_state``).
            extra_info (dict, optional): Additional information such as ``host``.

        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        test_results = []
        for member, events in (data or {}).items():
            state = None
            for event in events:
                if event.get("id") not in STATE_EVENT_IDS:
                    continue
                new_state = (event.get("details") or {}).get("new_state")
                if new_state:
                    state = str(new_state).upper()
            if not state or state in NORMAL_STATES:
                continue
            test_results.append(
                {
                    "host": host,
                    "severity": SEVERITY.MEDIUM,
                    "title": "Abnormal Member State",
                    "description": (
                        f"Member `{member}` is running in an abnormal state `{state}`; expected PRIMARY or SECONDARY."
                    ),
                }
            )
        return test_results, data


__all__ = ["MemberStateRule"]
