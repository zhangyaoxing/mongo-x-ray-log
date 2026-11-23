# mongo-x-ray-log

[![CI](https://github.com/zhangyaoxing/mongo-x-ray-log/actions/workflows/ci.yml/badge.svg)](https://github.com/zhangyaoxing/mongo-x-ray-log/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mongo-x-ray-log.svg)](https://pypi.org/project/mongo-x-ray-log/)

MongoDB log analysis plugin for [x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray).

## Install

```bash
pip install mongo-x-ray mongo-x-ray-log
```

## Usage

```bash
x-ray log /var/log/mongodb/mongod.log
x-ray log /var/log/mongodb/ 2026-07-20T08:00:00Z 2026-07-20T10:00:00Z
x-ray log /path/to/mongod.log -f html -o /path/to/output/
# Analyze a random 10% of a large log
x-ray log -r 0.1 mongodb.log
# Discover log folders recursively
x-ray log --discover /var/log/
```

## Compatibility

Supports MongoDB 5.0 and above on all topologies:

| Replica Set | Sharded Cluster | Standalone |
| :---------: | :-------------: | :--------: |
| ✅ | ✅ | ✅ |

## Parameters

```bash
x-ray log [-h] [-s CHECKSET] [-o OUTPUT] [-f {markdown,html,pdf}] [--no-browser]
          [-r RATE] [--top TOP] [--discover] log_file [start_time] [end_time]
```

| Argument | Description | Default |
| --- | --- | --- |
| `log_file` | Path to the MongoDB log file, or a folder of log files to analyze. | required |
| `start_time` | Inclusive UTC start time in ISO-8601 format. | first log line |
| `end_time` | Inclusive UTC end time in ISO-8601 format. | last log line |
| `-s, --checkset` | Checkset to run. | `default` |
| `-o, --output` | Output folder path. | `output/` |
| `-f, --format` | Output format: `markdown`, `html` or `pdf` (PDF also keeps Markdown and HTML). | `html` |
| `--no-browser` | Do not open the generated report in the browser. | `false` |
| `-r, --rate` | Log sampling rate, e.g. `1` for all logs, `0.1` for 10% of logs. | `1` |
| `--top` | Top N slow queries to list. | `10` |
| `--discover` | Recursively search the given path for folders containing log files. | `false` |

## Analysis Items

| Item | Purpose |
| --- | --- |
| `InfoItem` | Basic information about the MongoDB instance. |
| `ClientMetaItem` | Visualize client metadata (application, driver, OS, client IPs). |
| `ConnectionRateItem` | Analyze the rate of connections created and ended over a time window. |
| `LogRateItem` | Show the rate at which different log messages (grouped by log ID) appear over time. |
| `SlowItem` | Identify the top N slowest operations (table with sample viewers) and chart them over time as tabs (duration / scanned / scanned objects). |
| `SlowRateItem` | Analyze the rate of slow queries. |
| `StateTraceItem` | Visualize replica set member state changes over time. |
| `WEFItem` | Visualize warning, error and fatal log messages. |

## AI Analysis (Optional)

Four sections can carry an AI verdict, rendered as an "AI Analysis" note at the
end of each section in the report:

| Section | What the model is asked |
| --- | --- |
| Connection Rate | Whether the connection churn is a normal pattern or a connection leak. |
| Log Rate Analysis | Whether the repeated INFO logs look like a healthy pattern or an ongoing problem. |
| Slow Rate | Whether the slow query rate and its namespaces look normal. |
| Warning/Error/Fatal Logs | Which of the warning/error/fatal messages are worth noticing. |

Each prompt is a compact summary of that section's statistics (never the raw
log), so the calls are cheap and the answers short.

**Configuration** — the analysis runs whenever an API key is configured, in any
`ENV`. Set the environment variables (the repository's `.env` is read
automatically):

| Variable | Required | Default | Description |
| --- | :---: | --- | --- |
| `OPENAI_API_KEY` | Yes | — | API key for the AI service. |
| `OPENAI_BASE_URL` | No | OpenAI default | Compatible API endpoint (e.g. DeepSeek). |
| `AI_MODEL` | No | `gpt-4o` | Model name to use. |

To turn it off even when a key is configured, disable it in the config file:

```json
{
    "log": {
        "item_config": { "ai_analysis": false }
    }
}
```

Or per item, e.g. `"item_config": { "WEFItem": { "ai_analysis": false } }`.

## Development

Requires Python 3.10+, MongoDB 5.0 or later, and the [mongo-x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray) core package.

```bash
make unit-test   # run the unit tests
make lint        # ruff check + ruff format --check
make minify      # minify templates
```
