"""Trading signal rules for the required strategies."""

from __future__ import annotations

import pandas as pd

STRATEGY_ORDER = ["Trend Following", "Mean Reversion", "Custom"]


def _stateful_position(
    frame: pd.DataFrame,
    enter: pd.Series,
    exit_: pd.Series,
) -> pd.Series:
    """Convert entry/exit conditions into a long-only 0/1 position series."""
    position: list[int] = []
    holding = False
    for timestamp in frame.index:
        if not holding and bool(enter.loc[timestamp]):
            holding = True
        elif holding and bool(exit_.loc[timestamp]):
            holding = False
        position.append(1 if holding else 0)
    return pd.Series(position, index=frame.index, name="position")


def trend_following_signals(frame: pd.DataFrame) -> pd.Series:
    """Strategy 1: MACD trend following confirmed by ADX and moving averages."""
    enter = (frame["macd"] > frame["macd_signal"]) & (frame["adx_14"] > 25) & (
        frame["close"] > frame["sma_50"]
    )
    exit_ = (frame["macd"] < frame["macd_signal"]) | (frame["close"] < frame["sma_50"])
    return _stateful_position(frame, enter.fillna(False), exit_.fillna(False))


def mean_reversion_signals(frame: pd.DataFrame) -> pd.Series:
    """Strategy 2: buy oversold RSI/Bollinger breaks, exit overbought rebounds."""
    enter = (frame["rsi_14"] < 30) & (frame["close"] < frame["bb_lower"])
    exit_ = (frame["rsi_14"] > 70) | (frame["close"] > frame["bb_upper"])
    return _stateful_position(frame, enter.fillna(False), exit_.fillna(False))


def custom_strategy_signals(frame: pd.DataFrame) -> pd.Series:
    """Strategy 3: trend + momentum + volatility + volume confirmation.

    Categories used:
    - Trend: EMA/SMA and MACD
    - Momentum: RSI
    - Volatility: Bollinger midline and ATR regime
    - Volume: Chaikin Money Flow
    """
    atr_pct = frame["atr_14"] / frame["close"]
    normal_volatility = atr_pct < atr_pct.rolling(60, min_periods=20).quantile(0.8)
    enter = (
        (frame["ema_20"] > frame["sma_50"])
        & (frame["macd"] > frame["macd_signal"])
        & frame["rsi_14"].between(45, 70)
        & (frame["close"] > frame["bb_mid"])
        & (frame["cmf_20"] > 0)
        & normal_volatility
    )
    exit_ = (
        (frame["ema_20"] < frame["sma_50"])
        | (frame["macd"] < frame["macd_signal"])
        | (frame["rsi_14"] < 40)
        | (frame["cmf_20"] < -0.05)
    )
    return _stateful_position(frame, enter.fillna(False), exit_.fillna(False))


def generate_strategy_positions(frame: pd.DataFrame) -> dict[str, pd.Series]:
    """Return every required strategy as long-only 0/1 position series."""
    return {
        "Trend Following": trend_following_signals(frame),
        "Mean Reversion": mean_reversion_signals(frame),
        "Custom": custom_strategy_signals(frame),
    }
