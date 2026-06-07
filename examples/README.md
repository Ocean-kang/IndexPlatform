# Examples

These examples use small synthetic daily price data. They are intended only to verify the local workflow.

## Import Data

```bash
python -m index_platform.cli.main data import examples/data/sample_index_prices.csv --data-dir data/parquet
python -m index_platform.cli.main data status --data-dir data/parquet
```

## Run Backtests

```bash
python -m index_platform.cli.main backtest run --config examples/configs/buy_hold_demo.yaml --data-dir data/parquet --output-dir outputs/backtests
python -m index_platform.cli.main backtest run --config examples/configs/moving_average_demo.yaml --data-dir data/parquet --output-dir outputs/backtests
python -m index_platform.cli.main backtest run --config examples/configs/momentum_demo.yaml --data-dir data/parquet --output-dir outputs/backtests
```

Each command prints a `Run ID`. Use it to show a report:

```bash
python -m index_platform.cli.main report show --run-id <run_id> --runs-dir outputs/backtests
```

The examples do not download data and do not place trades.
