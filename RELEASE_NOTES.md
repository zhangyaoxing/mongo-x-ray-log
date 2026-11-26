# mongo-x-ray-log Release Notes

## 2.1.4

Version alignment with x-ray 2.1.4 — the first published build of the 2.1.3 changes.

`mongo-x-ray==2.1.3` reached PyPI without the MongoDB theme stylesheet, so its reports rendered unstyled and the 2.1.3 plugin packages were never published; 2.1.4 fixes the core packaging and these plugins require `mongo-x-ray>=2.1.4`.


## 2.1.3

### Added
- **AI analysis for four sections**: Connection Rate (normal churn or a leak?), Log Rate Analysis (are the repeated INFO logs a problem?), Slow Rate (does the rate look normal?) and Warning/Error/Fatal Logs (which messages are worth noticing?). Each sends a compact statistics summary — never the raw log — and shows the verdict as an "AI Analysis" note at the end of the matching `2 Review …` section, next to the charts.
- **AI index recommendation for slow operations**: every row of the Top Slow Operations table is sent to the model (namespace, filter, sort, plan summary, counts) asking for an index that would make it cheaper. A Sparkle badge appears after the query hash when there is one; hovering shows the formatted `createIndex` command, and the query sample viewer shows it above the sample:
  ```
  // AI Recommended Index
  db.pizzas.createIndex({
    size: 1,
    price: -1
  })

  // Query Sample
  { ... }
  ```
- **Copy button on every AI note** (the note only, not the title).
- **MongoDB report template** (`log/mongodb.html`): dark report in the design system, no remote stylesheet or webfont.
- **Severity badges** in the findings table and the "By Severity" summary.

### Changed
- The AI analysis runs whenever an API key is configured, in any `ENV`; `"ai_analysis": false` disables it (per item or for the module) and `"ai_analysis": true` opts a test run in. The old `WEFItem.ai_support` switch and its per-log-line analysis are gone.
- The report outline has a proper header row (the collapse toggle no longer covers the title) and the outline highlight/jump were fixed upstream.
- Requires `mongo-x-ray>=2.1.4` for the shared AI/badge helpers and the report stylesheets.

### Fixed
- **`item_config.SlowItem.top` / `sample_rate` are honoured**: `--top` and `-r/--rate` used to default to `10` and `1.0` and always overwrite the config file, so editing the config had no effect. They now only override it when passed.
- **The query/error sample viewers are highlighted as JavaScript**, matching their `//` comments and mongosh commands, instead of JSON.

## 2.1.2

### Fixed
- **The driver compatibility matrix accepts string versions**: `load_driver_matrix` passed every matrix entry to `Version(...)`, which only accepts a version array, so a matrix written the readable way (`"mongoc": "1.15"`) raised `ValueError: Invalid version array` and took the driver compatibility check and the client metadata table down with it. Entries are normalized now, so version strings, arrays and a mix of both all work.

## 2.1.1

Dependency and automation release — the plugin's own behaviour is unchanged.

### Dependencies
- Build: `setuptools` 84.0.0 → 84.2.1 ([`GHSA-xmj3-9gf7-h52w`](https://github.com/advisories/GHSA-xmj3-9gf7-h52w), low — Windows path escape via `namespace_packages.txt` during a legacy wheel install).

### Automation
- **Dependabot auto-merge repaired**: the workflow counted its own in-progress `auto-merge` check when waiting for "every check to pass", so it always timed out and updates stayed open. It now ignores its own check, retries a merge that lost a race with a sibling update, requests a rebase when the branch conflicts, and tolerates branches modified by hand.
- Repository labels `dependencies`, `python` and `github-actions` added, so Dependabot can tag its pull requests.

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
