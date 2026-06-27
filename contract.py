"""Frontend <-> backend contract for the strategy backtesting terminal.

This module is the single source of truth for the data shapes exchanged
between the two halves of the project. Both implementations import the types
from here:

* The frontend ships ``frontend/mock_backtest.MockBacktestService`` so the UI
  can be built and demoed against synthetic data.
* The backend ships ``backtest_service.AlpacaBacktestService`` (added by the
  backend author) which loads real Alpaca data, computes the indicators, runs
  the strategies, backtests them, and returns the exact same objects.

Because both satisfy the ``BacktestService`` protocol, integration is a
one-line import swap in ``app.py`` -- nothing else in the frontend changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypedDict

import pandas as pd


class Metrics(TypedDict):
    """Performance metrics for one equity curve.

    Fractions are expressed as decimals (0.42 == +42%); ratios are plain
    numbers. ``max_drawdown`` is negative or zero.
    """

    total_return: float
    cagr: float
    volatility: float  # annualized standard deviation of daily returns
    sharpe: float
    sortino: float
    max_drawdown: float
    win_rate: float  # fraction of round-trip trades that were profitable


@dataclass
class StrategyResult:
    """Everything the UI needs to draw and score a single strategy."""

    name: str
    equity: pd.Series  # date-indexed portfolio value in USD, starts at initial capital
    returns: pd.Series  # date-indexed daily returns of the strategy
    drawdown: pd.Series  # date-indexed drawdown (<= 0), peak-to-trough fraction
    signals: pd.DataFrame  # date index; columns: "price" (float), "side" ("buy"/"sell")
    indicators: dict[str, pd.Series]  # label -> date-indexed series to overlay on the price chart
    trades: pd.DataFrame  # round-trip trades; columns: "entry", "exit", "return"
    metrics: Metrics


@dataclass
class BacktestReport:
    """The full result of one backtest run, consumed by the frontend."""

    symbol: str
    years: int
    prices: pd.DataFrame  # date-indexed OHLCV: open, high, low, close, volume
    buy_hold: StrategyResult
    strategies: dict[str, StrategyResult]  # name -> result, in display order
    using_mock: bool = False  # True while served by the frontend mock


class BacktestService(Protocol):
    """Contract the backend must satisfy for the Streamlit UI."""

    def available_strategies(self) -> list[str]:
        """Strategy display names, e.g. ['Trend Following', 'Mean Reversion', 'Custom']."""
        ...

    def run_backtest(self, symbol: str, years: int = 5) -> BacktestReport:
        """Load history, run every strategy plus Buy & Hold, and score them."""
        ...
