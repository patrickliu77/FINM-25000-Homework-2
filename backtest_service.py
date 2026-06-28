"""Production BacktestService implementation backed by Alpaca data."""

from __future__ import annotations

from contract import BacktestReport, BacktestService
from backtester import build_strategy_result
from data_loader import get_historical_data
from indicators import add_indicators
from strategies import STRATEGY_ORDER, generate_strategy_positions


class AlpacaBacktestService:
    """Load Alpaca history, compute indicators, run strategies, and score them."""

    def available_strategies(self) -> list[str]:
        return list(STRATEGY_ORDER)

    def run_backtest(self, symbol: str, years: int = 5) -> BacktestReport:
        symbol = symbol.upper().strip()
        prices = get_historical_data(symbol, years)
        frame = add_indicators(prices)
        close = frame["close"]
        positions = generate_strategy_positions(frame)

        buy_hold = build_strategy_result("Buy & Hold", close, frame["close"].notna().astype(int), {})
        trend = build_strategy_result(
            "Trend Following",
            close,
            positions["Trend Following"],
            {
                "SMA 50": frame["sma_50"],
                "SMA 200": frame["sma_200"],
                "MACD": frame["macd"],
            },
        )
        mean_reversion = build_strategy_result(
            "Mean Reversion",
            close,
            positions["Mean Reversion"],
            {
                "Boll Upper": frame["bb_upper"],
                "Boll Mid": frame["bb_mid"],
                "Boll Lower": frame["bb_lower"],
            },
        )
        custom = build_strategy_result(
            "Custom",
            close,
            positions["Custom"],
            {
                "EMA 20": frame["ema_20"],
                "SMA 50": frame["sma_50"],
                "Boll Mid": frame["bb_mid"],
            },
        )

        return BacktestReport(
            symbol=symbol,
            years=years,
            prices=prices,
            buy_hold=buy_hold,
            strategies={
                "Trend Following": trend,
                "Mean Reversion": mean_reversion,
                "Custom": custom,
            },
            using_mock=False,
        )


_service: BacktestService = AlpacaBacktestService()
