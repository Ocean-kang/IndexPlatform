import pandas as pd

from index_platform.data.validators import normalize_daily_price_data, validate_required_fields


def test_validate_required_fields_reports_missing_columns() -> None:
    data = pd.DataFrame({"date": ["2024-01-02"], "symbol": ["000300.SH"]})

    try:
        validate_required_fields(data)
    except ValueError as exc:
        message = str(exc)
        assert "open" in message
        assert "source" in message
    else:
        raise AssertionError("Expected missing required fields to raise ValueError")


def test_normalize_daily_price_data_converts_date_and_numeric_fields() -> None:
    data = pd.DataFrame(
        {
            "date": ["2024-01-02"],
            "symbol": ["000300.SH"],
            "open": ["100.1"],
            "high": ["101.2"],
            "low": ["99.3"],
            "close": ["100.8"],
            "volume": ["1000"],
            "amount": ["100800.5"],
            "currency": ["CNY"],
            "source": ["toy"],
        }
    )

    normalized = normalize_daily_price_data(data)

    assert normalized.loc[0, "date"] == pd.Timestamp("2024-01-02")
    assert normalized.loc[0, "close"] == 100.8
    assert pd.api.types.is_numeric_dtype(normalized["amount"])

