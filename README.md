# IndexPlatform

IndexPlatform is a local-first index investment research platform.

The first phase focuses on research and backtesting only. It does not include
live trading, broker integrations, minute-level trading, machine learning
prediction, or production deployment.

## Current Progress

The repository currently includes:

- Task 001: project initialization
- Task 002: index registry
- Task 003: CSV data import
- Task 004: local Parquet storage
- Task 005: buy_hold backtest
- Task 006: performance metrics
- Task 007: basic CLI

## Available CLI

The CLI can be run through the installed `idx` entry point or directly with
`python -m index_platform.cli.main`.

```bash
python -m index_platform.cli.main --help
python -m index_platform.cli.main list-indices
python -m index_platform.cli.main data import path/to/prices.csv --data-dir data/parquet
python -m index_platform.cli.main data status --data-dir data/parquet
python -m index_platform.cli.main backtest run 000300.SH --data-dir data/parquet
python -m index_platform.cli.main report show path/to/metrics.json
```

## Data Scope

Daily price CSV files must include:

- `date`
- `symbol`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `amount`
- `currency`
- `source`

CSV data is normalized by the core data module, then can be saved to local
Parquet storage. The CLI calls the same core modules used by tests and future
interfaces.

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Show CLI help:

```bash
python -m index_platform.cli.main --help
```

## Current Limits

- Research and backtesting only
- Daily data only
- No live trading or broker API
- No real data source download adapters
- No dashboard yet
- No monitoring yet
- Only the first buy-and-hold strategy is implemented
