# FINM 25000 Homework 2: Strategy Backtesting Terminal

A Python and Streamlit application that downloads five years of daily OHLCV
data from Alpaca, computes a shelf of technical indicators, backtests several
algorithmic trading strategies, and compares them on a risk-adjusted basis.

## Current status

The Streamlit frontend is complete and runs end to end on a synthetic mock
service (`frontend/mock_backtest.py`) so the interface, charts, metric cards,
and comparison table can be built and demoed without the backend. Everything
shown is mock data for now.

Integration is a one-line import swap: when the backend module
`backtest_service.py` is ready (a class implementing the `BacktestService`
contract in `contract.py`), change the marked import in `app.py` and the same
UI renders live Alpaca results. Look for `BACKEND INTEGRATION POINT` in
`app.py`.

## Project structure

```
app.py                     Streamlit entry point and page orchestration
contract.py                Frontend <-> backend contract (shared data types)
frontend/mock_backtest.py  Synthetic BacktestService used until the backend lands
frontend/charts.py         Price, equity-curve, and drawdown chart builders
frontend/styles.py         Visual system (CSS) for the terminal interface
frontend/validation.py     Ticker input validation
.streamlit/config.toml     Local server configuration (port 8512)
requirements.txt           Python dependencies
backtest_service.py        Real Alpaca-backed service (added by the backend author)
```

## Run the frontend

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
streamlit run app.py
```

The project is configured to open at `http://localhost:8512`.

## Backend integration contract

Defined in `contract.py`. The backend ships a class implementing
`BacktestService`:

- `available_strategies() -> list[str]` -- strategy display names.
- `run_backtest(symbol, years=5) -> BacktestReport` -- loads history, runs
  Buy & Hold plus every strategy, and scores them.

`BacktestReport` carries the `prices` DataFrame (daily OHLCV), a `buy_hold`
result, and a `strategies` mapping. Each `StrategyResult` carries the equity
curve, daily returns, drawdown series, buy/sell `signals`, the `indicators`
to overlay on the price chart, the `trades` log, and a `Metrics` dict (Total
Return, CAGR, Volatility, Sharpe, Sortino, Maximum Drawdown, Win Rate).

The frontend only ever reads these objects, so as long as the backend returns
the same shapes, no frontend code changes.

## Strategies

- **Trend Following** -- MACD, ADX, and moving averages.
- **Mean Reversion** -- RSI and Bollinger Bands.
- **Custom** -- combines at least three indicators across two or more
  categories (trend, momentum, volatility, volume).

## Credentials

Copy `.env.example` to `.env` and add Alpaca paper API credentials locally.
The `.env` file is ignored by Git and must never be committed.
