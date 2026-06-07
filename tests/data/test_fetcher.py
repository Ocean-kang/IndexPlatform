from pathlib import Path

import pandas as pd

from index_platform.data.fetcher import fetch_price_data
from index_platform.storage import load_price_data, save_price_data


def _write_registry(path: Path) -> None:
    path.write_text(
        """indices:
  - symbol: 000300.SH
    name: CSI 300
    market: CN
    currency: CNY
    source: local
  - symbol: SPX.US
    name: S&P 500
    market: US
    currency: USD
    source: local
  - symbol: HSI.HK
    name: Hang Seng Index
    market: HK
    currency: HKD
    source: local
""",
        encoding="utf-8",
    )


def _price_frame(symbol: str, close: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03"],
            "symbol": [symbol, symbol],
            "open": [close, close + 1],
            "high": [close, close + 1],
            "low": [close, close + 1],
            "close": [close, close + 1],
            "volume": [1000, 1100],
            "amount": [10000, 12000],
            "currency": ["SRC", "SRC"],
            "source": ["mock", "mock"],
        }
    )


class _MockAdapter:
    def __init__(self, market: str, calls: list[tuple[str, str]]) -> None:
        self.market = market
        self.calls = calls

    def fetch_daily(self, symbol: str, start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
        self.calls.append((self.market, symbol))
        return _price_frame(symbol)


class _FailingAdapter(_MockAdapter):
    def fetch_daily(self, symbol: str, start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
        self.calls.append((self.market, symbol))
        if symbol == "^GSPC":
            raise RuntimeError("mock source unavailable")
        return _price_frame(symbol)


def test_fetch_single_symbol_downloads_and_saves_with_symbol_mapping(tmp_path: Path) -> None:
    registry = tmp_path / "indices.yaml"
    data_dir = tmp_path / "parquet"
    calls: list[tuple[str, str]] = []
    _write_registry(registry)

    result = fetch_price_data(
        symbol="000300.SH",
        start_date="2024-01-01",
        end_date="2024-01-31",
        data_dir=data_dir,
        registry=registry,
        adapter_factory=lambda market: _MockAdapter(market, calls),
    )

    prices = load_price_data(data_dir)
    assert result.success_symbols == ["000300.SH"]
    assert result.failures == []
    assert calls == [("CN", "sh000300")]
    assert prices["symbol"].tolist() == ["000300.SH", "000300.SH"]
    assert prices["currency"].tolist() == ["CNY", "CNY"]


def test_fetch_market_downloads_all_registered_market_symbols(tmp_path: Path) -> None:
    registry = tmp_path / "indices.yaml"
    data_dir = tmp_path / "parquet"
    calls: list[tuple[str, str]] = []
    _write_registry(registry)

    result = fetch_price_data(
        market="US",
        data_dir=data_dir,
        registry=registry,
        adapter_factory=lambda market: _MockAdapter(market, calls),
    )

    prices = load_price_data(data_dir)
    assert result.success_symbols == ["SPX.US"]
    assert calls == [("US", "^GSPC")]
    assert prices["symbol"].unique().tolist() == ["SPX.US"]


def test_fetch_all_downloads_every_registered_symbol(tmp_path: Path) -> None:
    registry = tmp_path / "indices.yaml"
    data_dir = tmp_path / "parquet"
    calls: list[tuple[str, str]] = []
    _write_registry(registry)

    result = fetch_price_data(
        fetch_all=True,
        data_dir=data_dir,
        registry=registry,
        adapter_factory=lambda market: _MockAdapter(market, calls),
    )

    prices = load_price_data(data_dir)
    assert result.success_symbols == ["000300.SH", "SPX.US", "HSI.HK"]
    assert calls == [("CN", "sh000300"), ("US", "^GSPC"), ("HK", "HSI.HK")]
    assert sorted(prices["symbol"].unique()) == ["000300.SH", "HSI.HK", "SPX.US"]


def test_fetch_merges_existing_prices_and_new_rows_win_on_duplicates(tmp_path: Path) -> None:
    registry = tmp_path / "indices.yaml"
    data_dir = tmp_path / "parquet"
    _write_registry(registry)
    save_price_data(_price_frame("000300.SH", close=10.0), data_dir)

    fetch_price_data(
        symbol="000300.SH",
        data_dir=data_dir,
        registry=registry,
        adapter_factory=lambda market: _MockAdapter(market, []),
    )

    prices = load_price_data(data_dir, symbol="000300.SH")
    assert len(prices) == 2
    assert prices["close"].tolist() == [100.0, 101.0]
    assert prices["source"].tolist() == ["mock", "mock"]


def test_fetch_partial_failure_still_saves_successful_symbols(tmp_path: Path) -> None:
    registry = tmp_path / "indices.yaml"
    data_dir = tmp_path / "parquet"
    calls: list[tuple[str, str]] = []
    _write_registry(registry)

    result = fetch_price_data(
        fetch_all=True,
        data_dir=data_dir,
        registry=registry,
        adapter_factory=lambda market: _FailingAdapter(market, calls),
    )

    prices = load_price_data(data_dir)
    assert result.success_symbols == ["000300.SH", "HSI.HK"]
    assert [failure.symbol for failure in result.failures] == ["SPX.US"]
    assert "mock source unavailable" in result.failures[0].reason
    assert sorted(prices["symbol"].unique()) == ["000300.SH", "HSI.HK"]
