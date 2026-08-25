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

## Development

Requires Python 3.10+ and the [mongo-x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray) core package.

```bash
make unit-test   # run the unit tests
make lint        # ruff check + ruff format --check
make minify      # minify templates
```
