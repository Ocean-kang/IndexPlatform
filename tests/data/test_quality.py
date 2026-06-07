import pandas as pd

from index_platform.data.quality import check_daily_price_quality, summarize_data_status


def _valid_prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")],
            "symbol": ["AAA", "AAA"],
            "open": [10.0, 11.0],
            "high": [12.0, 12.0],
            "low": [9.0, 10.0],
            "close": [11.0, 11.5],
            "volume": [1000, 1000],
            "amount": [10000, 11000],
            "currency": ["CNY", "CNY"],
            "source": ["toy", "toy"],
        }
    )


def test_check_daily_price_quality_accepts_valid_data() -> None:
    assert check_daily_price_quality(_valid_prices()) == []


def test_check_daily_price_quality_finds_ohlc_errors() -> None:
    data = _valid_prices()
    data.loc[0, "high"] = 8.0
    data.loc[1, "low"] = 12.0
    data.loc[1, "close"] = 0.0

    rules = {issue.rule for issue in check_daily_price_quality(data)}

    assert "high_gte_low" in rules
    assert "high_gte_open" in rules
    assert "high_gte_close" in rules
    assert "low_lte_open" in rules
    assert "low_lte_close" in rules
    assert "close_positive" in rules


def test_check_daily_price_quality_finds_duplicate_dates_and_null_required_fields() -> None:
    data = _valid_prices()
    data.loc[1, "date"] = data.loc[0, "date"]
    data.loc[1, "source"] = None

    issues = check_daily_price_quality(data)
    issue_by_rule = {issue.rule: issue for issue in issues}

    assert issue_by_rule["duplicate_date"].rows == 1
    assert issue_by_rule["required_non_null"].rows == 1


def test_check_daily_price_quality_finds_missing_required_fields() -> None:
    data = _valid_prices().drop(columns=["amount"])

    issues = check_daily_price_quality(data)

    assert issues[0].rule == "missing_field"
    assert "amount" in issues[0].message


def test_summarize_data_status_by_symbol() -> None:
    data = pd.concat(
        [
            _valid_prices(),
            _valid_prices().assign(symbol="BBB", date=[pd.Timestamp("2024-01-04"), pd.Timestamp("2024-01-05")]),
        ],
        ignore_index=True,
    )

    summary = summarize_data_status(data)

    assert summary["symbol"].tolist() == ["AAA", "BBB"]
    assert summary["rows"].tolist() == [2, 2]
    assert summary.loc[0, "start_date"] == "2024-01-02"
    assert summary["quality_issues"].tolist() == [0, 0]
