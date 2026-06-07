from pathlib import Path

import pandas as pd

from index_platform.storage.backtest_store import generate_run_id, load_backtest_result, save_backtest_result


def test_generate_run_id_is_unique() -> None:
    first = generate_run_id()
    second = generate_run_id()

    assert first != second
    assert first.startswith("bt_")


def test_save_and_load_backtest_result(tmp_path: Path) -> None:
    nav = pd.DataFrame({"date": pd.date_range("2024-01-02", periods=2), "nav": [1.0, 1.1]})
    positions = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-02", periods=2),
            "symbol": ["AAA", "AAA"],
            "market_value": [1.0, 1.1],
            "weight": [1.0, 1.0],
        }
    )
    orders = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-01-02")],
            "symbol": ["AAA"],
            "trade_value": [1.0],
            "price": [100.0],
            "quantity": [0.01],
            "cost": [0.0],
        }
    )
    metrics = {"total_return": 0.1}

    run_id = save_backtest_result(
        tmp_path,
        config={"strategy": "buy_hold", "symbols": ["AAA"]},
        nav=nav,
        positions=positions,
        orders=orders,
        metrics=metrics,
        run_id="test_run",
    )
    loaded = load_backtest_result(tmp_path, run_id)

    assert run_id == "test_run"
    assert (tmp_path / "test_run" / "config.yaml").exists()
    assert (tmp_path / "test_run" / "nav.parquet").exists()
    assert (tmp_path / "test_run" / "positions.parquet").exists()
    assert (tmp_path / "test_run" / "orders.parquet").exists()
    assert (tmp_path / "test_run" / "metrics.json").exists()
    assert loaded["metrics"] == metrics
    assert loaded["nav"]["nav"].tolist() == [1.0, 1.1]
    assert "strategy: buy_hold" in loaded["config_text"]


def test_save_backtest_result_creates_empty_orders_table(tmp_path: Path) -> None:
    run_id = save_backtest_result(
        tmp_path,
        config={"strategy": "empty"},
        nav=pd.DataFrame({"date": [pd.Timestamp("2024-01-02")], "nav": [1.0]}),
        positions=pd.DataFrame({"date": [pd.Timestamp("2024-01-02")], "symbol": ["AAA"]}),
        orders=None,
        metrics={"total_return": 0.0},
        run_id="empty_orders",
    )
    loaded = load_backtest_result(tmp_path, run_id)

    assert list(loaded["orders"].columns) == ["date", "symbol", "trade_value", "price", "quantity", "cost"]
    assert loaded["orders"].empty
