# IndexPlatform

IndexPlatform is a local-first index investment research platform.

The first phase focuses on research and backtesting only. It does not include
live trading, broker integrations, or production deployment.

## Current Scope

Task 001 initializes the Python project foundation:

- Python package structure under `index_platform/`
- Minimal CLI entry point
- pytest configuration
- Basic import and CLI tests

No financial data model, index registry, storage, strategy, or backtest logic is
implemented yet.

## Commands

Run tests:

```bash
pytest
```

Show CLI help:

```bash
python -m index_platform.cli.main --help
```
