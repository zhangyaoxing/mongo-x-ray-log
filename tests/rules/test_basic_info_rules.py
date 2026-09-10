"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from bson import json_util

from mongo_x_ray_log.log_items.info_item import InfoItem


def _cmd_opts_line(options_json):
    return json_util.loads(
        '{"t":{"$date":"2026-07-03T00:00:00.000Z"},"s":"I","c":"CONTROL","id":21951,'
        f'"ctx":"initandlisten","msg":"Options set by command line","attr":{{"options":{options_json}}}}}'
    )


def _titles(results):
    return [result["title"] for result in results]


def test_info_item_runs_security_checks_on_command_line_options(tmp_path):
    item = InfoItem(output_folder=str(tmp_path), config={})
    item._hostname = "test-host"
    line = _cmd_opts_line('{"net":{"bindIp":"0.0.0.0","port":27017},"security":{"authorization":"disabled"}}')
    item.analyze(line)
    item.finalize_analysis()

    titles = _titles(item._test_result)
    # The healthcheck SecurityRule checks are applied to the log options
    assert "Authorization Disabled" in titles
    assert "Unrestricted Bind IP" in titles
    assert "Default Port Used" in titles


def test_info_item_no_issues_when_options_only_point_at_config_file(tmp_path):
    # When only a config file path is echoed, the effective options are unknown
    item = InfoItem(output_folder=str(tmp_path), config={})
    item.analyze(_cmd_opts_line('{"config":"/etc/mongod.conf"}'))
    item.finalize_analysis()
    assert item._test_result == []


def test_info_item_no_issues_without_command_line_options(tmp_path):
    item = InfoItem(output_folder=str(tmp_path), config={})
    item.finalize_analysis()
    assert item._test_result == []
