# mongo-x-ray-log Release Notes

**mongo-x-ray-log** is the MongoDB log analysis plugin for [x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray). It analyzes MongoDB log files and produces an interactive HTML/Markdown/PDF report on slow queries, connection/log rates, client metadata, replica-set state transitions, warnings/errors/fatal logs, and basic instance information.

## 2.1.0 — Main changes

### Added
- **Summary item** with an overview (severity and category counts) plus a risk scan of the report's findings.
- **New rules**: slow rate rules for `SlowRateItem`, connection rate and basic info rules, slow operations rules on the top slow operations item, and member state rules for the member state trace.
- **Warning/error/fatal severities**: warning logs raise a `MEDIUM` issue, fatal logs a `HIGH` issue.
- **Query targeting escalation**: extremely poor query targeting is escalated to `HIGH` severity.
- **Checks description**: each item now states in the report what its rules check.
- **Slow operations patterns**: the pattern column shows the query sort ("Has Sort Stage"), and `getMore` slow queries derive their pattern from the originating command (falling back to an empty pattern when none is found).

### Changed
- **Merged items**: Top Slow Operations and Slow Operations Chart are now a single `SlowItem`; the charts are rendered before the table and code block.
- **Copyable values**: important table cells are wrapped in backticks so the new report copy icons can copy them with one click.
- **Slow operation aggregation key** is namespace-qualified and includes the command type.
- **Risk register**: test results are matched against the known risks, with a message logged before each vector search.
- **Report copy support** (core-side): inline code, code blocks and table `<pre>` blocks now have copy icons, and table `<pre>` blocks are outlined.

### Fixed
- Test results report the resolved hostname instead of `unknown`.
- Member State Trace chart is sized (55px per member) so the state bars are visible.
- Chart reset buttons now actually reset the zoom.
- Code columns in the top slow operations table are left-aligned.

### Documentation
- README gained the PyPI badge.

### Dependencies
- Requires `mongo-x-ray-hc>=2.1.0`: the healthcheck plugin owns the shared issue catalog (`mongo_x_ray_hc.issues`) and hc 2.0.0 imports `mongo_x_ray.issues`, which core 2.1.0 no longer ships.

### Development
- **CI now runs on pull requests** as well as on pushes to `main`, so a dependency bump is linted and tested before it can land.
- **Dependabot** is enabled for `pip` and GitHub Actions (weekly). Patch and minor updates merge automatically once every check is green, as do major updates of the CI actions and the build/lint/test tooling; a major update of a runtime dependency (`mongo-x-ray`, `mongo-x-ray-hc`) is left for review, and a failing or missing check leaves the pull request open instead of merging.
- **Tooling bumped**: `setuptools` 83.0.0 → 84.0.0, `actions/checkout` v4 → v7, `actions/setup-python` v5 → v7.

## 2.0.0

The plugin was extracted from the core x-ray project as a standalone package (`x-ray log <path> [start] [end]`), with nine analysis items, shared parsers and report rendering, AI-assisted analysis for W/E/F logs, risk-register matching, PyPI/TestPyPI publishing, CI and CodeQL.
