import unittest

import numpy as np
import pandas as pd

from backtester import INITIAL_CAPITAL, build_strategy_result
from indicators import add_indicators
from strategies import generate_strategy_positions


def sample_prices(rows: int = 320) -> pd.DataFrame:
    index = pd.bdate_range("2021-01-01", periods=rows)
    base = 100 + np.linspace(0, 35, rows) + 4 * np.sin(np.linspace(0, 16, rows))
    close = pd.Series(base, index=index)
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + 1,
            "low": np.minimum(open_, close) - 1,
            "close": close,
            "volume": 1_000_000 + np.arange(rows) * 10,
        },
        index=index,
    )


class BackendTests(unittest.TestCase):
    def test_add_indicators_produces_required_categories(self):
        frame = add_indicators(sample_prices())
        for column in [
            "sma_50",
            "ema_20",
            "macd",
            "macd_signal",
            "adx_14",
            "rsi_14",
            "bb_upper",
            "atr_14",
            "obv",
            "cmf_20",
        ]:
            self.assertIn(column, frame.columns)

    def test_strategy_positions_are_long_only(self):
        frame = add_indicators(sample_prices())
        positions = generate_strategy_positions(frame)
        self.assertEqual(set(positions), {"Trend Following", "Mean Reversion", "Custom"})
        for position in positions.values():
            self.assertTrue(position.isin([0, 1]).all())
            self.assertEqual(len(position), len(frame))

    def test_backtest_result_contains_metrics_and_equity(self):
        frame = add_indicators(sample_prices())
        close = frame["close"]
        position = pd.Series(1, index=frame.index)
        result = build_strategy_result("Buy & Hold", close, position, {})
        self.assertAlmostEqual(result.equity.iloc[0], INITIAL_CAPITAL)
        self.assertIn("sharpe", result.metrics)
        self.assertIn("max_drawdown", result.metrics)
        self.assertGreaterEqual(result.metrics["win_rate"], 0)


if __name__ == "__main__":
    unittest.main()
