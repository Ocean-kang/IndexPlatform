from pathlib import Path

import pandas as pd
import pytest

from index_platform.fx import convert_amount, load_fx_data, read_fx_csv, save_fx_data


def _fx_rates() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-02"],
            "base_currency": ["USD", "HKD"],
            "quote_currency": ["CNY", "CNY"],
            "rate": [7.1, 0.91],
            "source": ["toy", "toy"],
        }
    )


def test_read_fx_csv_normalizes_fields(tmp_path: Path) -> None:
    csv_file = tmp_path / "fx.csv"
    _fx_rates().to_csv(csv_file, index=False)

    rates = read_fx_csv(csv_file)

    assert list(rates.columns) == ["date", "base_currency", "quote_currency", "rate", "source"]
    assert rates["date"].iloc[0] == pd.Timestamp("2024-01-02")


def test_save_and_load_fx_data(tmp_path: Path) -> None:
    save_fx_data(_fx_rates(), tmp_path)

    loaded = load_fx_data(tmp_path)

    assert len(loaded) == 2
    assert loaded.iloc[0]["base_currency"] == "HKD"


def test_convert_amount_direct_inverse_and_missing_rate() -> None:
    rates = _fx_rates()

    assert convert_amount(10, "USD", "CNY", "2024-01-02", rates) == pytest.approx(71)
    assert convert_amount(7.1, "CNY", "USD", "2024-01-02", rates) == pytest.approx(1)
    assert convert_amount(5, "USD", "USD", "2024-01-02", rates) == 5
    with pytest.raises(ValueError, match="Missing FX rate"):
        convert_amount(1, "EUR", "CNY", "2024-01-02", rates)
