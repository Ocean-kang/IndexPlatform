"""Analysis helpers for comparing index performance."""

from index_platform.analysis.index_compare import (
    compare_indices,
    correlation_matrix,
    normalize_prices,
    risk_metrics,
    yearly_returns,
)

__all__ = [
    "compare_indices",
    "correlation_matrix",
    "normalize_prices",
    "risk_metrics",
    "yearly_returns",
]
