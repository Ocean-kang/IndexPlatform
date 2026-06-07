"""Data quality checks for daily price data."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from index_platform.data.schema import DAILY_PRICE_REQUIRED_FIELDS


@dataclass(frozen=True)
class QualityIssue:
    """One data quality issue found in a daily price table."""

    rule: str
    message: str
    rows: int


def check_daily_price_quality(data: pd.DataFrame) -> list[QualityIssue]:
    """Run required daily OHLC and completeness checks."""
    issues: list[QualityIssue] = []
    missing_fields = [field for field in DAILY_PRICE_REQUIRED_FIELDS if field not in data.columns]
    for field in missing_fields:
        issues.append(QualityIssue("missing_field", f"Missing required field: {field}", len(data)))

    available_required = [field for field in DAILY_PRICE_REQUIRED_FIELDS if field in data.columns]
    for field in available_required:
        count = int(data[field].isna().sum())
        if count:
            issues.append(QualityIssue("required_non_null", f"Required field has null values: {field}", count))

    if {"symbol", "date"}.issubset(data.columns):
        normalized_dates = pd.to_datetime(data["date"], errors="coerce").dt.normalize()
        duplicate_count = int(pd.DataFrame({"symbol": data["symbol"], "date": normalized_dates}).duplicated().sum())
        if duplicate_count:
            issues.append(QualityIssue("duplicate_date", "Duplicate symbol/date rows found.", duplicate_count))

    numeric = _numeric_columns(data)
    checks = [
        ("high_gte_low", "high must be greater than or equal to low.", _compare(numeric, "high", "low", "ge")),
        ("high_gte_open", "high must be greater than or equal to open.", _compare(numeric, "high", "open", "ge")),
        ("high_gte_close", "high must be greater than or equal to close.", _compare(numeric, "high", "close", "ge")),
        ("low_lte_open", "low must be less than or equal to open.", _compare(numeric, "low", "open", "le")),
        ("low_lte_close", "low must be less than or equal to close.", _compare(numeric, "low", "close", "le")),
        ("close_positive", "close must be positive.", _positive(numeric, "close")),
    ]
    for rule, message, passed in checks:
        if passed is None:
            continue
        failed = int((~passed.fillna(False)).sum())
        if failed:
            issues.append(QualityIssue(rule, message, failed))

    return issues


def summarize_data_status(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize row counts, date ranges, and issue counts by symbol."""
    if data.empty:
        return pd.DataFrame(columns=["symbol", "rows", "start_date", "end_date", "quality_issues"])

    working = data.copy()
    working["date"] = pd.to_datetime(working["date"]).dt.normalize()
    rows = []
    for symbol, group in working.groupby("symbol", sort=True):
        rows.append(
            {
                "symbol": symbol,
                "rows": len(group),
                "start_date": group["date"].min().date().isoformat(),
                "end_date": group["date"].max().date().isoformat(),
                "quality_issues": len(check_daily_price_quality(group)),
            }
        )
    return pd.DataFrame(rows)


def _numeric_columns(data: pd.DataFrame) -> dict[str, pd.Series]:
    columns: dict[str, pd.Series] = {}
    for field in ["open", "high", "low", "close"]:
        if field in data.columns:
            columns[field] = pd.to_numeric(data[field], errors="coerce")
    return columns


def _compare(columns: dict[str, pd.Series], left: str, right: str, operator: str) -> pd.Series | None:
    if left not in columns or right not in columns:
        return None
    if operator == "ge":
        return columns[left] >= columns[right]
    return columns[left] <= columns[right]


def _positive(columns: dict[str, pd.Series], field: str) -> pd.Series | None:
    if field not in columns:
        return None
    return columns[field] > 0
