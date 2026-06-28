"""Alpaca historical data access for the backtesting engine."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

import pandas as pd
from dotenv import load_dotenv


class AlpacaConfigurationError(RuntimeError):
    """Raised when Alpaca credentials are missing or incomplete."""


def _alpaca_credentials() -> tuple[str, str]:
    """Load Alpaca credentials from local environment variables.

    The course instructions call for environment-variable based credentials.
    We support both the names used in this repo and Alpaca's common APCA names.
    """
    load_dotenv()
    api_key = os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY")
    if not api_key or not secret_key:
        raise AlpacaConfigurationError(
            "Missing Alpaca credentials. Copy .env.example to .env and set "
            "ALPACA_API_KEY and ALPACA_SECRET_KEY."
        )
    return api_key, secret_key


def authenticate_paper_account():
    """Authenticate against Alpaca's paper-trading API and return the account.

    The assignment explicitly asks for paper-trading API authentication. Market
    data is fetched through the historical data client, but this call confirms
    the credentials are valid for the paper account before any backtest runs.
    """
    from alpaca.trading.client import TradingClient

    api_key, secret_key = _alpaca_credentials()
    trading_client = TradingClient(api_key, secret_key, paper=True)
    return trading_client.get_account()


def get_historical_data(symbol: str, years: int = 5, feed: str = "iex") -> pd.DataFrame:
    """Download daily OHLCV bars from Alpaca as a clean Pandas DataFrame.

    Parameters
    ----------
    symbol:
        US equity ticker, e.g. ``AAPL`` or ``SPY``.
    years:
        Number of calendar years to request. The assignment requires at least
        five years of daily OHLCV data.
    feed:
        Alpaca market-data feed. ``iex`` works for most free paper accounts;
        set ``sip`` locally if your account has SIP access.
    """
    from alpaca.data.enums import DataFeed
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame

    symbol = symbol.upper().strip()
    api_key, secret_key = _alpaca_credentials()

    end = datetime.now(UTC)
    start = end - timedelta(days=int(years * 365.25) + 14)

    # Paper auth is separate from data retrieval, but doing it here keeps the
    # backend honest about the assignment's authentication requirement.
    authenticate_paper_account()

    client = StockHistoricalDataClient(api_key, secret_key)
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed(feed),
    )
    bars = client.get_stock_bars(request)
    frame = bars.df

    if frame.empty:
        raise ValueError(f"No historical daily bars returned for {symbol}.")

    if isinstance(frame.index, pd.MultiIndex):
        frame = frame.xs(symbol, level=0)

    frame = frame.rename(columns=str.lower)
    required = ["open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Alpaca response for {symbol} is missing columns: {missing}")

    clean = frame[required].copy()
    clean.index = pd.to_datetime(clean.index)
    if clean.index.tz is not None:
        clean.index = clean.index.tz_convert(None)
    clean = clean.sort_index()

    # Keep the most recent five-year window while preserving all daily rows
    # returned by Alpaca inside that window.
    earliest = pd.Timestamp(end.replace(tzinfo=None)) - pd.DateOffset(years=years)
    clean = clean.loc[clean.index >= earliest]
    if len(clean) < 252 * min(years, 1):
        raise ValueError(f"Not enough historical data returned for {symbol}.")
    return clean
