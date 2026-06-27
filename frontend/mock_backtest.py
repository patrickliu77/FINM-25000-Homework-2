"""Synthetic backtest service used while the Alpaca backend is being built.

``MockBacktestService`` implements the ``BacktestService`` contract end to end
on deterministic random data so the entire frontend (charts, metric cards, and
the comparison table) can be developed and demoed without the backend.

None of the numbers here are real. The backend's ``AlpacaBacktestService`` will
return the same objects computed from live Alpaca data and the real indicator
and backtest logic.
"""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from contract import BacktestReport, BacktestService, Metrics, StrategyResult

INITIAL_CAPITAL = 100_000.0
TRADING_DAYS = 252

STRATEGY_ORDER = ["Trend Following", "Mean Reversion", "Custom"]

_REFERENCE_PRICES = {
    "AAPL": 195.0,
    "MSFT": 445.0,
    "NVDA": 135.0,
    "TSLA": 220.0,
    "SPY": 600.0,
    "QQQ": 520.0,
}


# --------------------------------------------------------------------------- #
# Indicator helpers (mock-only; the backend owns the production versions).     #
# --------------------------------------------------------------------------- #
def _sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def _macd(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    macd = _ema(series, 12) - _ema(series, 26)
    signal = _ema(macd, 9)
    return macd, signal


def _bollinger(series: pd.Series, window: int = 20, k: float = 2.0):
    mid = _sma(series, window)
    sd = series.rolling(window).std()
    return mid + k * sd, mid, mid - k * sd


# --------------------------------------------------------------------------- #
# Backtest primitives                                                          #
# --------------------------------------------------------------------------- #
def _simulate(close: pd.Series, position: pd.Series) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """Long-only, all-in/all-out backtest of a 0/1 position series.

    Positions are shifted one bar so a signal formed at today's close is
    executed at the next bar -- no look-ahead. Returns the equity curve, the
    strategy's daily returns, and the round-trip trade log.
    """
    held = position.shift(1).fillna(0).clip(0, 1)
    market_return = close.pct_change().fillna(0)
    daily_return = market_return * held
    equity = INITIAL_CAPITAL * (1 + daily_return).cumprod()

    changes = held.diff().fillna(held)
    entries = list(close.index[changes > 0])
    exits = list(close.index[changes < 0])
    if len(exits) < len(entries):  # still holding at the end -> close on the last bar
        exits.append(close.index[-1])

    trades = pd.DataFrame(
        {
            "entry": entries,
            "exit": exits[: len(entries)],
            "return": [close.loc[x] / close.loc[e] - 1 for e, x in zip(entries, exits)],
        }
    )
    return equity, daily_return, trades


def _drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1


def _metrics(equity: pd.Series, daily_return: pd.Series, trades: pd.DataFrame, years: int) -> Metrics:
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1)
    cagr = float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)
    ann_return = float(daily_return.mean() * TRADING_DAYS)
    ann_vol = float(daily_return.std() * np.sqrt(TRADING_DAYS))
    downside = daily_return[daily_return < 0].std() * np.sqrt(TRADING_DAYS)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
    sortino = ann_return / float(downside) if downside and downside > 0 else 0.0
    win_rate = float((trades["return"] > 0).mean()) if len(trades) else 0.0
    return Metrics(
        total_return=total_return,
        cagr=cagr,
        volatility=ann_vol,
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown=float(_drawdown(equity).min()),
        win_rate=win_rate,
    )


def _signals_from_position(close: pd.Series, position: pd.Series) -> pd.DataFrame:
    """Buy/sell markers at the bars where the position turns on/off."""
    held = position.shift(1).fillna(0).clip(0, 1)
    changes = held.diff().fillna(held)
    rows = []
    for ts in close.index[changes > 0]:
        rows.append({"timestamp": ts, "price": float(close.loc[ts]), "side": "buy"})
    for ts in close.index[changes < 0]:
        rows.append({"timestamp": ts, "price": float(close.loc[ts]), "side": "sell"})
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=["price", "side"])
    return frame.set_index("timestamp").sort_index()


def _result(
    name: str, close: pd.Series, position: pd.Series, indicators: dict[str, pd.Series], years: int
) -> StrategyResult:
    equity, daily_return, trades = _simulate(close, position)
    return StrategyResult(
        name=name,
        equity=equity,
        returns=daily_return,
        drawdown=_drawdown(equity),
        signals=_signals_from_position(close, position),
        indicators=indicators,
        trades=trades,
        metrics=_metrics(equity, daily_return, trades, years),
    )


class MockBacktestService:
    """Deterministic synthetic implementation of the BacktestService contract."""

    def available_strategies(self) -> list[str]:
        return list(STRATEGY_ORDER)

    def run_backtest(self, symbol: str, years: int = 5) -> BacktestReport:
        prices = self._synthetic_prices(symbol, years)
        close = prices["close"]

        # Indicators (shared across the toy strategies).
        sma20, sma50 = _sma(close, 20), _sma(close, 50)
        ema20 = _ema(close, 20)
        rsi = _rsi(close)
        macd, macd_signal = _macd(close)
        upper, mid, lower = _bollinger(close)

        # --- Strategy 1: Trend Following (MACD cross confirmed by SMA50) ------
        trend_pos = ((macd > macd_signal) & (close > sma50)).astype(int)
        trend = _result(
            "Trend Following",
            close,
            trend_pos,
            {"SMA 20": sma20, "SMA 50": sma50, "EMA 20": ema20},
            years,
        )

        # --- Strategy 2: Mean Reversion (RSI + Bollinger band touches) --------
        mr_pos = self._mean_reversion_position(close, rsi, lower, upper)
        mean_rev = _result(
            "Mean Reversion",
            close,
            mr_pos,
            {"Boll Upper": upper, "Boll Mid": mid, "Boll Lower": lower},
            years,
        )

        # --- Strategy 3: Custom (trend + momentum + volatility filter) --------
        custom_pos = self._custom_position(close, sma50, macd, macd_signal, rsi, lower)
        custom = _result(
            "Custom",
            close,
            custom_pos,
            {"SMA 50": sma50, "Boll Lower": lower},
            years,
        )

        # --- Benchmark: Buy & Hold -------------------------------------------
        buy_hold = _result("Buy & Hold", close, pd.Series(1, index=close.index), {}, years)

        return BacktestReport(
            symbol=symbol,
            years=years,
            prices=prices,
            buy_hold=buy_hold,
            strategies={"Trend Following": trend, "Mean Reversion": mean_rev, "Custom": custom},
            using_mock=True,
        )

    # ------------------------------------------------------------------ #
    # Stateful strategy position builders                                #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _mean_reversion_position(close, rsi, lower, upper) -> pd.Series:
        pos, holding = [], False
        for i in range(len(close)):
            if not holding and (rsi.iloc[i] < 30 or close.iloc[i] < lower.iloc[i]):
                holding = True
            elif holding and (rsi.iloc[i] > 70 or close.iloc[i] > upper.iloc[i]):
                holding = False
            pos.append(1 if holding else 0)
        return pd.Series(pos, index=close.index)

    @staticmethod
    def _custom_position(close, sma50, macd, macd_signal, rsi, lower) -> pd.Series:
        pos, holding = [], False
        for i in range(len(close)):
            uptrend = close.iloc[i] > sma50.iloc[i] and macd.iloc[i] > macd_signal.iloc[i]
            momentum_ok = rsi.iloc[i] > 50
            if not holding and uptrend and momentum_ok:
                holding = True
            elif holding and (close.iloc[i] < sma50.iloc[i] or rsi.iloc[i] < 45):
                holding = False
            pos.append(1 if holding else 0)
        return pd.Series(pos, index=close.index)

    # ------------------------------------------------------------------ #
    # Synthetic OHLCV generator                                          #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _synthetic_prices(symbol: str, years: int) -> pd.DataFrame:
        seed = int.from_bytes(hashlib.sha256(symbol.encode()).digest()[:8], "big")
        rng = np.random.default_rng(seed)

        periods = TRADING_DAYS * years
        dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=periods)

        start_price = _REFERENCE_PRICES.get(symbol, 80.0 + seed % 240)
        drift = 0.08 / TRADING_DAYS
        vol = 0.22 / np.sqrt(TRADING_DAYS)
        log_returns = rng.normal(drift - 0.5 * vol**2, vol, periods)
        close = start_price * np.exp(np.cumsum(log_returns))

        open_ = np.empty(periods)
        open_[0] = start_price
        open_[1:] = close[:-1]
        wick = np.abs(rng.normal(0, vol, periods)) * close
        high = np.maximum(open_, close) + wick
        low = np.maximum(0.01, np.minimum(open_, close) - wick)
        volume = rng.integers(5_000_000, 60_000_000, periods).astype(float)

        return pd.DataFrame(
            {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
            index=dates,
        )


# Static type check: the mock satisfies the contract.
_service: BacktestService = MockBacktestService()
