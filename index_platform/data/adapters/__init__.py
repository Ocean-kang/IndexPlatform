"""External daily price data adapters."""

from index_platform.data.adapters.akshare_adapter import AkShareIndexAdapter
from index_platform.data.adapters.hk_adapter import HongKongIndexAdapter
from index_platform.data.adapters.yfinance_adapter import YFinanceAdapter

__all__ = [
    "AkShareIndexAdapter",
    "HongKongIndexAdapter",
    "YFinanceAdapter",
]
