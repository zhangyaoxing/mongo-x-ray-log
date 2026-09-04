"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_hc.rules.security_rule import SecurityRule
from mongo_x_ray_hc.rules.tls_protocol_rule import TlsProtocolRule
from mongo_x_ray_log.log_items.base_item import BaseItem
from mongo_x_ray_log.parsers.info_parser import InfoParser


class InfoItem(BaseItem):
    def __init__(self, output_folder, config):
        super().__init__(output_folder, config)
        self.name = "Basic Info"
        self.description = "Basic information about the instance."
        self._cache = {}
        # Reuse the healthcheck rules that inspect the server command line options
        # (the same rules the GMD module runs on getCmdLineOpts).
        self._rules["security"] = SecurityRule(config)
        self._rules["tls_protocol"] = TlsProtocolRule(config)

        self._ids = [
            20721,  # Process Details
            20722,  # Node is a member of a replica set
            5853300,  # current featureCompatibilityVersion value
            23403,  # Build Info
            51765,  # Operating System
            21951,  # Options set by command line
            4913010,  # Certificate information
            4615611,  # MongoDB starting
        ]

    def analyze(self, log_line):
        log_id = log_line.get("id", "")
        index = self._ids.index(log_id) if log_id in self._ids else -1
        attr = log_line.get("attr", {})
        if index in [0, 7]:
            # Process Details
            self._process_details(attr)
        elif index == 1:
            # Node is a member of a replica set
            self._process_replica_set(attr)
        elif index == 2:
            # current featureCompatibilityVersion value
            self._process_feature_compatibility(attr)
        elif index == 3:
            # Build Info
            self._process_build_info(attr)
        elif index == 4:
            # Operating System
            self._process_operating_system(attr)
        elif index == 5:
            # Options set by command line
            self._process_command_line_options(attr)
        elif index == 6:
            # Certificate information
            self._process_certificate_info(attr)

    def _process_details(self, attr):
        self._cache["process"] = {
            "pid": attr.get("pid", "Unknown"),
            "host": attr.get("host", "Unknown"),
            "port": attr.get("port", "Unknown"),
        }

    def _process_replica_set(self, attr):
        self._cache["replica_set"] = attr

    def _process_feature_compatibility(self, attr):
        self._cache["fcv"] = attr.get("featureCompatibilityVersion", "Unknown")

    def _process_build_info(self, attr):
        build_info = attr.get("buildInfo", {})
        self._cache["build_info"] = {
            "version": build_info.get("version", "Unknown"),
            "modules": build_info.get("modules", []),
            "environment": build_info.get("environment", {}),
        }

    def _process_operating_system(self, attr):
        os_info = attr.get("os", {})
        self._cache["os"] = {
            "name": os_info.get("name", "Unknown"),
            "version": os_info.get("version", "Unknown"),
        }

    def _process_command_line_options(self, attr):
        options = attr.get("options", {})
        self._cache["command_line_options"] = options

    def _process_certificate_info(self, attr):
        cert_info = attr
        self._cache["cert_info"] = cert_info

    def finalize_analysis(self):
        super().finalize_analysis()
        # The command line options echoed in the log are the config sections passed
        # on the command line (equivalent to getCmdLineOpts().parsed). Run the same
        # security checks the GMD module runs on getCmdLineOpts, skipping when the
        # options are missing or only point at a config file (their effective values
        # are then unknown).
        options = self._cache.get("command_line_options", {})
        if not options or set(options) == {"config"}:
            return
        cmd_line_opts = {"parsed": options}
        for rule in self._rules.values():
            test_result, _ = rule.apply(cmd_line_opts, extra_info={"host": self._hostname or "unknown"})
            self.append_test_results(test_result)

    def review_results_markdown(self, f):
        parser = InfoParser()
        f.write(parser.markdown(self._cache))
