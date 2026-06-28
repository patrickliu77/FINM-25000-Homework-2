"""Reusable long-only backtesting primitives and performance metrics."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from contract import Metrics, StrategyResult

INITIAL_CAPITAL = 100_000.0
TRADING_DAYS = 252


def run_long_only_backtest(
    close: pd.Series,
    position: pd.Series,
    initial_capital: float = INITIAL_CAPITAL,
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """Backtest a 0/1 long-only strategy with next-day execution.

    A signal formed at today's close is applied on the next trading day. That
    keeps the engine reusable and avoids look-ahead bias.
    """
    aligned_position = position.reindex(close.index).fillna(0).clip(0, 1)
    held = aligned_position.shift(1).fillna(0)
    market_return = close.pct_change().fillna(0)
    daily_return = market_return * held
    equity = initial_capital * (1 + daily_return).cumprod()

    trades = _trade_log(close, held)
    return equity, daily_return, trades


def drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1


def calculate_metrics(
    equity: pd.Series,
    daily_return: pd.Series,
    trades: pd.DataFrame,
) -> Metrics:
    """Calculate the assignment's required performance metrics."""
    elapsed_years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1 / TRADING_DAYS)
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1)
    cagr = float((equity.iloc[-1] / equity.iloc[0]) ** (1 / elapsed_years) - 1)
    volatility = float(daily_return.std(ddof=0) * np.sqrt(TRADING_DAYS))
    annualized_return = float(daily_return.mean() * TRADING_DAYS)
    downside_returns = daily_return[daily_return < 0]
    downside = float(downside_returns.std(ddof=0) * np.sqrt(TRADING_DAYS)) if len(downside_returns) else 0.0
    sharpe = annualized_return / volatility if volatility > 0 else 0.0
    sortino = annualized_return / downside if downside > 0 else 0.0
    win_rate = float((trades["return"] > 0).mean()) if len(trades) else 0.0

    return Metrics(
        total_return=_finite(total_return),
        cagr=_finite(cagr),
        volatility=_finite(volatility),
        sharpe=_finite(sharpe),
        sortino=_finite(sortino),
        max_drawdown=_finite(float(drawdown(equity).min())),
        win_rate=_finite(win_rate),
    )


def signals_from_position(close: pd.Series, position: pd.Series) -> pd.DataFrame:
    """Build buy/sell marker rows for the price chart."""
    held = position.reindex(close.index).fillna(0).clip(0, 1).shift(1).fillna(0)
    changes = held.diff().fillna(held)
    rows = []
    for timestamp in close.index[changes > 0]:
        rows.append({"timestamp": timestamp, "price": float(close.loc[timestamp]), "side": "buy"})
    for timestamp in close.index[changes < 0]:
        rows.append({"timestamp": timestamp, "price": float(close.loc[timestamp]), "side": "sell"})
    if not rows:
        return pd.DataFrame(columns=["price", "side"])
    return pd.DataFrame(rows).set_index("timestamp").sort_index()


def build_strategy_result(
    name: str,
    close: pd.Series,
    position: pd.Series,
    indicators: dict[str, pd.Series],
    initial_capital: float = INITIAL_CAPITAL,
) -> StrategyResult:
    equity, daily_return, trades = run_long_only_backtest(close, position, initial_capital)
    return StrategyResult(
        name=name,
        equity=equity,
        returns=daily_return,
        drawdown=drawdown(equity),
        signals=signals_from_position(close, position),
        indicators=indicators,
        trades=trades,
        metrics=calculate_metrics(equity, daily_return, trades),
    )


def _trade_log(close: pd.Series, held: pd.Series) -> pd.DataFrame:
    changes = held.diff().fillna(held)
    entries = list(close.index[changes > 0])
    exits = list(close.index[changes < 0])
    if len(exits) < len(entries):
        exits.append(close.index[-1])

    rows = []
    for entry, exit_ in zip(entries, exits):
        if exit_ < entry:
            continue
        rows.append(
            {
                "entry": entry,
                "exit": exit_,
                "entry_price": float(close.loc[entry]),
                "exit_price": float(close.loc[exit_]),
                "return": float(close.loc[exit_] / close.loc[entry] - 1),
            }
        )
    return pd.DataFrame(rows, columns=["entry", "exit", "entry_price", "exit_price", "return"])


def _finite(value: float) -> float:
    return float(value) if math.isfinite(value) else 0.0
