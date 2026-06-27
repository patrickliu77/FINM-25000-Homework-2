"""Chart builders for the strategy backtesting terminal.

Three figures are required by the assignment:

1. ``create_price_chart`` -- price with the indicators a strategy uses, plus
   buy/sell signal markers.
2. ``create_equity_curve_chart`` -- portfolio value over time for Buy & Hold
   and every strategy on a shared axis.
3. ``create_drawdown_chart`` -- drawdown over time for every strategy.

All three consume the dataclasses defined in ``contract.py`` so they work
identically against the mock service and the real backend.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from contract import BacktestReport, StrategyResult

# Shared palette, kept in sync with frontend/styles.py.
PANEL = "#11151a"
LINE = "#29313a"
MUTED = "#87919d"
PAPER = "#edf1f3"
AMBER = "#e5b454"
CYAN = "#63d2c6"
CORAL = "#ef765f"

# Distinct colors for the four series (Buy & Hold first, then the strategies).
SERIES_COLORS = [MUTED, CYAN, AMBER, CORAL]
# Muted overlay colors for indicator lines on the price chart.
INDICATOR_COLORS = ["#e5b454", "#63d2c6", "#9a8cff", "#ef765f", "#5aa9e6"]


def apply_dark_theme(figure: go.Figure, height: int = 520) -> go.Figure:
    """Apply the terminal's dark Plotly styling shared by every chart."""
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=18, t=18, b=12),
        hovermode="x unified",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(family="ui-monospace, SFMono-Regular, Menlo, monospace", color=MUTED, size=11),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=MUTED, size=10)
        ),
        hoverlabel=dict(bgcolor="#161b21", bordercolor=LINE, font_color=PAPER),
    )
    figure.update_xaxes(showgrid=False, linecolor=LINE, tickfont_color=MUTED, zeroline=False)
    figure.update_yaxes(
        gridcolor="#20272e", linecolor=LINE, tickfont_color=MUTED, zeroline=False, side="right"
    )
    return figure


def create_price_chart(prices: pd.DataFrame, result: StrategyResult) -> go.Figure:
    """Close price with the strategy's indicator overlays and buy/sell markers."""
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=prices.index,
            y=prices["close"],
            name="Close",
            line=dict(color=PAPER, width=1.4),
        )
    )

    for color, (label, series) in zip(INDICATOR_COLORS, result.indicators.items()):
        figure.add_trace(
            go.Scatter(x=series.index, y=series, name=label, line=dict(color=color, width=1))
        )

    signals = result.signals
    if not signals.empty:
        buys = signals[signals["side"] == "buy"]
        sells = signals[signals["side"] == "sell"]
        figure.add_trace(
            go.Scatter(
                x=buys.index,
                y=buys["price"],
                mode="markers",
                name="Buy",
                marker=dict(symbol="triangle-up", size=9, color=CYAN, line=dict(width=0)),
            )
        )
        figure.add_trace(
            go.Scatter(
                x=sells.index,
                y=sells["price"],
                mode="markers",
                name="Sell",
                marker=dict(symbol="triangle-down", size=9, color=CORAL, line=dict(width=0)),
            )
        )

    apply_dark_theme(figure, height=520)
    figure.update_yaxes(title_text="USD")
    return figure


def create_equity_curve_chart(report: BacktestReport) -> go.Figure:
    """Portfolio value over time for Buy & Hold and every strategy."""
    figure = go.Figure()
    series = [report.buy_hold, *report.strategies.values()]
    for color, result in zip(SERIES_COLORS, series):
        figure.add_trace(
            go.Scatter(
                x=result.equity.index,
                y=result.equity,
                name=result.name,
                line=dict(color=color, width=1.6 if result.name == "Buy & Hold" else 1.3),
            )
        )
    apply_dark_theme(figure, height=460)
    figure.update_yaxes(title_text="USD")
    return figure


def create_drawdown_chart(report: BacktestReport) -> go.Figure:
    """Drawdown over time for Buy & Hold and every strategy."""
    figure = go.Figure()
    series = [report.buy_hold, *report.strategies.values()]
    for color, result in zip(SERIES_COLORS, series):
        figure.add_trace(
            go.Scatter(
                x=result.drawdown.index,
                y=result.drawdown * 100,
                name=result.name,
                line=dict(color=color, width=1.2),
            )
        )
    apply_dark_theme(figure, height=360)
    figure.update_yaxes(title_text="%")
    return figure
