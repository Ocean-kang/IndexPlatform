import pandas as pd

from index_platform.storage.parquet_store import load_price_data, save_price_data


def _price_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-01-03", "2024-01-02", "2024-01-02"],
            "symbol": ["000300.SH", "000300.SH", "SPX.US"],
            "open": [101, 100, 4000],
            "high": [103, 102, 4050],
            "low": [100, 99, 3990],
            "close": [102, 101, 4040],
            "volume": [1100, 1000, 2000],
            "amount": [112200, 101000, 8080000],
            "currency": ["CNY", "CNY", "USD"],
            "source": ["toy", "toy", "toy"],
        }
    )


def test_save_and_load_price_data(tmp_path) -> None:
    price_file = save_price_data(_price_data(), tmp_path / "parquet")

    loaded = load_price_data(tmp_path / "parquet")

    assert price_file.exists()
    assert loaded["symbol"].tolist() == ["000300.SH", "000300.SH", "SPX.US"]
    assert loaded["date"].tolist() == [
        pd.Timestamp("2024-01-02"),
        pd.Timestamp("2024-01-03"),
        pd.Timestamp("2024-01-02"),
    ]


def test_load_price_data_filters_symbol_and_dates(tmp_path) -> None:
    save_price_data(_price_data(), tmp_path)

    loaded = load_price_data(
        tmp_path,
        symbol="000300.SH",
        start_date="2024-01-03",
        end_date="2024-01-03",
    )

    assert len(loaded) == 1
    assert loaded.loc[0, "symbol"] == "000300.SH"
    assert loaded.loc[0, "date"] == pd.Timestamp("2024-01-03")


def test_save_price_data_replaces_existing_file(tmp_path) -> None:
    save_price_data(_price_data(), tmp_path)
    replacement = _price_data().iloc[[0]].copy()
    replacement.loc[:, "symbol"] = "HSI.HK"

    save_price_data(replacement, tmp_path)
    loaded = load_price_data(tmp_path)

    assert loaded["symbol"].tolist() == ["HSI.HK"]


def test_load_price_data_missing_file_raises(tmp_path) -> None:
    try:
        load_price_data(tmp_path)
    except FileNotFoundError as exc:
        assert "prices.parquet" in str(exc)
    else:
        raise AssertionError("Expected missing Parquet file to raise FileNotFoundError")

