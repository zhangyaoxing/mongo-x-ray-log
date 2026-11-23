"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from types import SimpleNamespace

from mongo_x_ray_log.plugin import apply_cli_overrides


def test_config_values_are_kept_when_the_flags_are_absent():
    args = SimpleNamespace(rate=None, top=None)

    config = apply_cli_overrides({"sample_rate": 0.5, "item_config": {"SlowItem": {"top": 15}}}, args)

    # `--rate`/`--top` used to default to 1.0/10 and always overwrite the file.
    assert config["sample_rate"] == 0.5
    assert config["item_config"]["SlowItem"]["top"] == 15


def test_flags_override_the_config_when_given():
    args = SimpleNamespace(rate=0.1, top=3)

    config = apply_cli_overrides({"sample_rate": 0.5, "item_config": {"SlowItem": {"top": 15}}}, args)

    assert config["sample_rate"] == 0.1
    assert config["item_config"]["SlowItem"]["top"] == 3


def test_overrides_create_the_item_config_when_missing():
    args = SimpleNamespace(rate=None, top=20)

    config = apply_cli_overrides({}, args)

    assert config == {"item_config": {"SlowItem": {"top": 20}}}
