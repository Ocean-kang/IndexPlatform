import pandas as pd

from index_platform.analysis.index_compare import compare_indices, correlation_matrix, normalize_prices, risk_metrics, yearly_returns


def _prices() -> pd.DataFrame:
    rows = []
    for symbol, closes in {"AAA": [10, 11, 12, 13], "BBB": [20, 20, 22, 21]}.items():
        for date, close in zip(pd.date_range("2023-12-29", periods=4, freq="D"), closes):
            rows.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "open": close,
                    "high": close,
                    "low": close,
                    "close": close,
                    "volume": 1000,
                    "amount": 10000,
                    "currency": "CNY",
                    "source": "toy",
                }
            )
    return pd.DataFrame(rows)


def test_index_compare_supports_normalization_yearly_risk_and_correlation() -> None:
    prices = _prices()

    normalized = normalize_prices(prices)
    annual = yearly_returns(prices)
    risk = risk_metrics(prices)
    corr = correlation_matrix(prices)
    all_outputs = compare_indices(prices)

    assert normalized.iloc[0].to_dict() == {"AAA": 1.0, "BBB": 1.0}
    assert 2023 in annual.index
    assert {"total_return", "max_drawdown", "sharpe_ratio"}.issubset(risk.columns)
    assert list(corr.columns) == ["AAA", "BBB"]
    assert set(all_outputs) == {"normalized", "yearly_returns", "risk_metrics", "correlation"}
