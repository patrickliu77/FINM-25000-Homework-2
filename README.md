# FINM 25000 Homework 2: Strategy Backtesting Terminal

A Python and Streamlit application that downloads five years of daily OHLCV
data from Alpaca, computes a shelf of technical indicators, backtests several
algorithmic trading strategies, and compares them on a risk-adjusted basis.

## Current status

Project scaffold. The Streamlit frontend (visual system, layout, charts, and
the performance table) is being built against the backend contract below. The
historical data loader, technical indicators, strategy signals, backtesting
engine, and performance metrics live in the backend modules.

## Project structure

```
app.py                   Streamlit entry point and page orchestration
frontend/styles.py       Visual system (CSS) for the terminal interface
frontend/charts.py       Price, equity-curve, and drawdown chart builders
frontend/validation.py   Ticker input validation
.streamlit/config.toml   Local server configuration (port 8512)
requirements.txt         Python dependencies
```

Backend modules (data loader, indicators, strategies, backtest engine, and
metrics) are added by the backend author against the contract below.

## Run the frontend

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```

The project is configured to open at `http://localhost:8512`.

## Backend integration contract (draft)

To be finalized between the frontend and backend authors. The frontend expects
the backend to provide:

- `load_history(symbol, years=5)` -> a pandas DataFrame of daily OHLCV bars
  indexed by date with `open`, `high`, `low`, `close`, and `volume` columns.
- `run_backtest(prices, strategy)` -> per-strategy results containing the
  portfolio value series (equity curve), daily returns, and the list of trades.
- `performance_metrics(results)` -> Total Return, CAGR, Volatility, Sharpe,
  Sortino, Maximum Drawdown, and Win Rate.

## Strategies

- **Trend Following** -- MACD, ADX, and moving averages.
- **Mean Reversion** -- RSI and Bollinger Bands.
- **Custom** -- combines at least three indicators across two or more
  categories (trend, momentum, volatility, volume).

## Credentials

Copy `.env.example` to `.env` and add Alpaca paper API credentials locally.
The `.env` file is ignored by Git and must never be committed.
