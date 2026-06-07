from pathlib import Path

import pandas as pd

from index_platform.data.csv_adapter import read_price_csv


def test_read_price_csv_normalizes_daily_price_data(tmp_path: Path) -> None:
    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(
        """date,symbol,open,high,low,close,volume,amount,currency,source
2024-01-02,000300.SH,100,105,99,104,1000,104000,CNY,toy
2024/01/03,000300.SH,104.5,106,103,105.5,1200,126600,CNY,toy
""",
        encoding="utf-8",
    )

    prices = read_price_csv(csv_file)

    assert list(prices.columns) == [
        "date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "currency",
        "source",
    ]
    assert prices["date"].tolist() == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")]
    assert pd.api.types.is_numeric_dtype(prices["close"])
    assert pd.api.types.is_numeric_dtype(prices["volume"])


def test_read_price_csv_missing_file_raises(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.csv"

    try:
        read_price_csv(missing_file)
    except FileNotFoundError as exc:
        assert str(missing_file) in str(exc)
    else:
        raise AssertionError("Expected missing CSV file to raise FileNotFoundError")

