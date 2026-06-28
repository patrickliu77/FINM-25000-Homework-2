"""Technical indicators used by the strategy backtests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def macd(close: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    line = ema(close, 12) - ema(close, 26)
    signal = line.ewm(span=9, adjust=False, min_periods=9).mean()
    hist = line - signal
    return line, signal, hist


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50)


def true_range(frame: pd.DataFrame) -> pd.Series:
    prev_close = frame["close"].shift(1)
    ranges = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - prev_close).abs(),
            (frame["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    return true_range(frame).ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def adx(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    high, low = frame["high"], frame["low"]
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=frame.index)
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=frame.index
    )
    tr = true_range(frame)
    plus_di = 100 * plus_dm.ewm(alpha=1 / window, adjust=False, min_periods=window).mean() / tr.ewm(
        alpha=1 / window, adjust=False, min_periods=window
    ).mean()
    minus_di = 100 * minus_dm.ewm(alpha=1 / window, adjust=False, min_periods=window).mean() / tr.ewm(
        alpha=1 / window, adjust=False, min_periods=window
    ).mean()
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0)
    return dx.ewm(alpha=1 / window, adjust=False, min_periods=window).mean().fillna(0)


def stochastic_oscillator(frame: pd.DataFrame, window: int = 14) -> tuple[pd.Series, pd.Series]:
    low_min = frame["low"].rolling(window, min_periods=window).min()
    high_max = frame["high"].rolling(window, min_periods=window).max()
    k = 100 * (frame["close"] - low_min) / (high_max - low_min).replace(0, np.nan)
    d = k.rolling(3, min_periods=3).mean()
    return k.fillna(50), d.fillna(50)


def williams_r(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    high_max = frame["high"].rolling(window, min_periods=window).max()
    low_min = frame["low"].rolling(window, min_periods=window).min()
    value = -100 * (high_max - frame["close"]) / (high_max - low_min).replace(0, np.nan)
    return value.fillna(-50)


def bollinger_bands(close: pd.Series, window: int = 20, num_std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = sma(close, window)
    sd = close.rolling(window=window, min_periods=window).std()
    upper = mid + num_std * sd
    lower = mid - num_std * sd
    return upper, mid, lower


def obv(frame: pd.DataFrame) -> pd.Series:
    direction = np.sign(frame["close"].diff()).fillna(0)
    return (direction * frame["volume"]).cumsum()


def chaikin_money_flow(frame: pd.DataFrame, window: int = 20) -> pd.Series:
    high_low = (frame["high"] - frame["low"]).replace(0, np.nan)
    multiplier = ((frame["close"] - frame["low"]) - (frame["high"] - frame["close"])) / high_low
    money_flow_volume = multiplier.fillna(0) * frame["volume"]
    return money_flow_volume.rolling(window, min_periods=window).sum() / frame["volume"].rolling(
        window, min_periods=window
    ).sum()


def add_indicators(prices: pd.DataFrame) -> pd.DataFrame:
    """Return OHLCV data with a broad set of technical indicator columns.

    This implements more than the six indicators required by the assignment
    while keeping conventional names for use by strategies and charts.
    """
    frame = prices.copy()
    close = frame["close"]

    frame["sma_20"] = sma(close, 20)
    frame["sma_50"] = sma(close, 50)
    frame["sma_200"] = sma(close, 200)
    frame["ema_20"] = ema(close, 20)
    frame["ema_50"] = ema(close, 50)
    frame["macd"], frame["macd_signal"], frame["macd_hist"] = macd(close)
    frame["adx_14"] = adx(frame, 14)
    frame["rsi_14"] = rsi(close, 14)
    frame["stoch_k"], frame["stoch_d"] = stochastic_oscillator(frame, 14)
    frame["williams_r"] = williams_r(frame, 14)
    frame["bb_upper"], frame["bb_mid"], frame["bb_lower"] = bollinger_bands(close, 20, 2.0)
    frame["atr_14"] = atr(frame, 14)
    frame["obv"] = obv(frame)
    frame["cmf_20"] = chaikin_money_flow(frame, 20).fillna(0)
    return frame
