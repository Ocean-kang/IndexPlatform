"""Simple transaction cost models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransactionCostModel:
    """Commission and slippage model based on absolute trade value."""

    commission_rate: float = 0.0
    slippage_rate: float = 0.0
    min_commission: float = 0.0

    def __post_init__(self) -> None:
        if self.commission_rate < 0:
            raise ValueError("commission_rate must not be negative.")
        if self.slippage_rate < 0:
            raise ValueError("slippage_rate must not be negative.")
        if self.min_commission < 0:
            raise ValueError("min_commission must not be negative.")

    def calculate(self, trade_value: float) -> float:
        """Calculate total transaction cost for one buy or sell trade."""
        absolute_value = abs(float(trade_value))
        if absolute_value == 0:
            return 0.0
        commission = max(absolute_value * self.commission_rate, self.min_commission)
        slippage = absolute_value * self.slippage_rate
        return float(commission + slippage)
