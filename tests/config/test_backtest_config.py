from pathlib import Path

import pytest

from index_platform.config import load_backtest_config


def test_load_backtest_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """strategy_name: moving_average
symbols: [000300.SH]
start_date: 2024-01-01
end_date: 2024-01-31
initial_nav: 1.0
benchmark: 000300.SH
rebalance_frequency: daily
transaction_cost:
  commission_rate: 0.001
execution_rule: next_close
strategy_params:
  window: 5
  execution_delay: 1
""",
        encoding="utf-8",
    )

    config = load_backtest_config(config_file)

    assert config.strategy_name == "moving_average"
    assert config.symbols == ["000300.SH"]
    assert config.transaction_cost["commission_rate"] == 0.001
    assert config.strategy_params["window"] == 5


def test_load_backtest_config_reports_missing_fields(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("strategy_name: buy_hold\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required fields"):
        load_backtest_config(config_file)
