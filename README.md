# FINM 25000 Homework 2: Strategy Backtesting Terminal

Streamlit app and backend engine for testing technical-indicator trading
strategies with Alpaca historical market data.

## What It Does

- Authenticates to Alpaca's paper-trading API.
- Downloads 5 years of daily OHLCV bars for a user-selected ticker.
- Computes technical indicators across trend, momentum, volatility, and volume.
- Backtests Buy & Hold, Trend Following, Mean Reversion, and Custom strategies.
- Calculates Total Return, CAGR, Volatility, Sharpe, Sortino, Max Drawdown, and Win Rate.
- Displays price/signals, equity curves, drawdowns, and a comparison table.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Alpaca paper credentials to `.env`:

```bash
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
```

`.env` is ignored by Git and should not be committed.

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8512`.

If credentials are missing, the dashboard falls back to clearly labeled
synthetic demo data so the UI can still be reviewed. With `.env` configured, it
uses the real Alpaca backend.

## Generate Charts And PDF Report

For final Alpaca-based artifacts:

```bash
python generate_submission_artifacts.py --symbol AAPL
```

For structure/testing without credentials:

```bash
python generate_submission_artifacts.py --symbol AAPL --allow-mock
```

This writes:

- `charts/aapl_trend_price_signals.html`
- `charts/aapl_equity_curves.html`
- `charts/aapl_drawdowns.html`
- `reports/final_report.pdf`

## Project Structure

```text
app.py                              Streamlit dashboard
backtest_service.py                 Production service satisfying contract.py
data_loader.py                      Alpaca auth and historical OHLCV retrieval
indicators.py                       SMA, EMA, MACD, ADX, RSI, Bollinger, ATR, OBV, CMF, etc.
strategies.py                       Trend, mean-reversion, and custom signal rules
backtester.py                       Long-only reusable backtest engine and metrics
generate_submission_artifacts.py    Chart/PDF artifact generator
contract.py                         Frontend/backend dataclasses and protocol
frontend/                           UI charts, styling, validation, mock service
tests/                              Unit tests for backend logic and Alpaca auth wiring
charts/                             Exported chart files
reports/final_report.pdf            Final report PDF
```

## Strategies

- **Trend Following**: buy when MACD > signal, ADX > 25, and price > SMA50;
  sell when MACD < signal or price < SMA50.
- **Mean Reversion**: buy when RSI < 30 and price is below the lower Bollinger
  Band; sell when RSI > 70 or price is above the upper Bollinger Band.
- **Custom**: combines EMA/SMA trend, MACD, RSI, Bollinger midline, ATR regime,
  and Chaikin Money Flow.

## Tests

```bash
python -m unittest discover -s tests -v
```
