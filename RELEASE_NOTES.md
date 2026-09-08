# mongo-x-ray-log Release Notes

**mongo-x-ray-log** is the MongoDB log analysis plugin for [x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray). It analyzes MongoDB log files and produces an interactive HTML/Markdown/PDF report on slow queries, connection/log rates, client metadata, replica-set state transitions, warnings/errors/fatal logs, and basic instance information.

All changes are part of the `2.0.0` line (the plugin was extracted from the core x-ray project).

## 2.0.0 — Main changes

### Added
- Standalone log analysis plugin (`x-ray log <path> [start] [end]`) with nine analysis items: Client Metadata, Connection Rate, Log Rate, Slow Rate, Top Slow Operations, Slow Operations Chart, Member State Trace, Warning/Error/Fatal Logs, and Basic Info.
- Slow query pattern analyzer, interactive HTML report (charts, outline, copy-table, sample viewers), unit tests plus Playwright browser tests for the report UI, and PDF output.
- AI-assisted analysis (GPT) for warning/error/fatal logs and risk-register matching for known issues.
- `x-ray log --version` support, PyPI/TestPyPI publishing via trusted publishing, CI (ruff + unit tests) and CodeQL.

### Changed
- Report restructured to mirror the healthcheck/gmd modules: **"1 Review Test Results"** (rule-based pass/fail issues) and **"2 Review Raw Results"** (data review), with cross links.
- Driver version compatibility rewritten as a rule producing test results, and all log item output now rendered through shared parsers (tables/charts/code) instead of per-item Markdown/JS.
- Risk register and AI client integrated as optional/shared components from the core, with graceful degradation when not installed.

### Fixed
- Driver compatibility check no longer flags internal drivers (`NetworkInterfaceTL`, `MongoDB Internal Client`); they are still shown in the results table.
- Removed unused code flagged by CodeQL.

### Documentation
- README rewritten with usage, CLI parameters, analysis items, and MongoDB 5.0+ compatibility notes.
