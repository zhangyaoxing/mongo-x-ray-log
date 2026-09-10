"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_log.log_items.client_meta_item import ClientMetaItem
from mongo_x_ray_log.log_items.log_rate_item import LogRateItem
from mongo_x_ray_log.log_items.slow_rate_item import SlowRateItem


def test_item_description_lists_rule_checks():
    item = SlowRateItem(output_folder="/tmp", config={})
    assert item.description.startswith("Analyse the rate of slow queries.")
    assert "- Checks if the average slow query duration per minute is too high." in item.description


def test_item_description_includes_multiple_rules():
    item = ClientMetaItem(output_folder="/tmp", config={})
    assert "- Checks if the client drivers are compatible with the MongoDB server version." in item.description


def test_item_description_without_rules_stays_plain():
    item = LogRateItem(output_folder="/tmp", config={})
    assert "Checks if" not in item.description
