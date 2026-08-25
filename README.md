# mongo-x-ray-log

[![CI](https://github.com/zhangyaoxing/mongo-x-ray-log/actions/workflows/ci.yml/badge.svg)](https://github.com/zhangyaoxing/mongo-x-ray-log/actions/workflows/ci.yml)

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
```

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

## Development

Requires Python 3.10+ and the [mongo-x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray) core package.

```bash
make unit-test   # run the unit tests
make lint        # ruff check + ruff format --check
make minify      # minify templates
```
