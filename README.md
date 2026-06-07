# IndexPlatform

IndexPlatform is a local-first index investment research and backtesting platform. The current phase focuses on daily data research, local storage, strategy backtests, reports, and a lightweight Streamlit dashboard.

This project is not a live trading system and does not provide investment advice.

## Current Capabilities

- Index registry from `configs/indices.yaml`, with market filtering.
- Daily price CSV import, schema normalization, and data-quality checks.
- Local Parquet storage and optional DuckDB querying for local analysis.
- A-share, Hong Kong, and US data-source adapter skeletons for AKShare and yfinance-compatible data.
- Buy-and-hold, moving-average timing, and momentum rotation strategies.
- Long-only daily backtests with basic transaction cost support.
- Backtest result storage, report generation, parameter sweep, and walk-forward helpers.
- Performance metrics: total return, annualized return, volatility, max drawdown, Sharpe, and Calmar.
- Streamlit dashboard pages for data status, index view, backtest results, strategy lab, and run monitor.
- Run-state and log files for local backtest monitoring.
- Lightweight prediction module with simple baseline predictors only.
- ETF mapping registry for research lookup only.

## Not Implemented

- Live trading, broker APIs, order placement, or account integration.
- Minute-level or intraday trading.
- Short selling, leverage, margin trading, futures, options, or financing.
- Production-grade machine learning, deep learning, model training systems, model persistence, or automated tuning.
- Cloud deployment, user accounts, permissions, or multi-user scheduling.
- Guaranteed data availability from third-party sources.

## Installation

Use Python 3.10 or newer.

```bash
python -m pip install -e ".[dev]"
```

Optional runtime adapters need their own libraries when used outside tests:

```bash
python -m pip install akshare yfinance
```

## Directory Structure

```text
index_platform/
  analysis/      index comparison helpers
  backtest/      backtest engines, costs, and runners
  calendar/      simple trading calendar helpers
  cli/           Typer CLI wrappers
  config/        YAML backtest config loader
  dashboard/     Streamlit pages
  data/          schemas, CSV import, validation, adapters
  fx/            local FX data helpers
  metrics/       performance metrics
  monitor/       run state and logs
  prediction/    lightweight baseline prediction interfaces
  research/      parameter sweep and walk-forward helpers
  storage/       Parquet and backtest result storage
  strategy/      strategy implementations
  universe/      index registry and ETF mapping

configs/
docs/
tests/
```

## Data Preparation

Daily price CSV files must include:

```text
date,symbol,open,high,low,close,volume,amount,currency,source
```

Import local data into Parquet storage:

```bash
python -m index_platform.cli.main data import examples/data/sample_index_prices.csv --data-dir data/parquet
```

Check local data status:

```bash
python -m index_platform.cli.main data status --data-dir data/parquet
```

## CLI Usage

```bash
python -m index_platform.cli.main --help
python -m index_platform.cli.main list-indices
python -m index_platform.cli.main list-indices --market CN
python -m index_platform.cli.main monitor status
```

If installed as an editable package, the `idx` entry point is also available.

## Backtest Examples

Run a single-symbol buy-and-hold backtest:

```bash
python -m index_platform.cli.main backtest run 000300.SH --data-dir data/parquet
```

Run a YAML-configured backtest and save results:

```bash
python -m index_platform.cli.main backtest run --config examples/configs/buy_hold_demo.yaml --data-dir data/parquet --output-dir outputs/backtests
```

Show a saved report:

```bash
python -m index_platform.cli.main report show --run-id <run_id> --runs-dir outputs/backtests
```

## Dashboard

Start the local dashboard:

```bash
streamlit run index_platform/dashboard/app.py
```

The dashboard reuses core storage, metrics, report, and backtest modules. It is a local research UI, not a trading terminal.

## Tests

Run the offline test suite:

```bash
pytest
```

Data-source adapter tests use mocked or toy DataFrames and do not make real network requests.

## Data Sources

- Local CSV is the primary reproducible input path.
- Parquet is the primary local storage format.
- AKShare and yfinance adapters are thin optional wrappers that standardize downloaded data into the DailyPrice schema.
- ETF mappings in `configs/etf_mapping.yaml` are research metadata only and do not imply tradability or order support.

## Current Limits

The platform is intended for research and educational backtesting with daily data. Results depend on input data quality and simplified assumptions. It does not promise returns, execute trades, connect to brokers, or replace professional financial advice.
