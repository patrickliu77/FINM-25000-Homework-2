"""Chart builders for the strategy backtesting terminal.

Three figures are required by the assignment:

1. ``create_price_chart`` -- price with the indicators a strategy uses, plus
   buy/sell signal markers.
2. ``create_equity_curve_chart`` -- portfolio value over time for Buy & Hold
   and each strategy on a shared axis.
3. ``create_drawdown_chart`` -- drawdown over time for every strategy.

The implementations land in Step 3 (frontend build). For now each function
documents the data it expects so the backend contract can be finalized first.
"""

import pandas as pd
import plotly.graph_objects as go


# Shared palette, kept in sync with frontend/styles.py.
PANEL = "#11151a"
LINE = "#29313a"
MUTED = "#87919d"
PAPER = "#edf1f3"
AMBER = "#e5b454"
CYAN = "#63d2c6"
CORAL = "#ef765f"

# Distinct colors for the four equity curves (Buy & Hold + three strategies).
SERIES_COLORS = [MUTED, CYAN, AMBER, CORAL]


def apply_dark_theme(figure: go.Figure, height: int = 520) -> go.Figure:
    """Apply the terminal's dark Plotly styling shared by every chart."""
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=18, t=18, b=12),
        hovermode="x unified",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(
            family="ui-monospace, SFMono-Regular, Menlo, monospace",
            color=MUTED,
            size=11,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(color=MUTED, size=10),
        ),
        hoverlabel=dict(bgcolor="#161b21", bordercolor=LINE, font_color=PAPER),
    )
    figure.update_xaxes(showgrid=False, linecolor=LINE, tickfont_color=MUTED, zeroline=False)
    figure.update_yaxes(
        gridcolor="#20272e", linecolor=LINE, tickfont_color=MUTED, zeroline=False, side="right"
    )
    return figure


def create_price_chart(prices: pd.DataFrame, signals: pd.DataFrame, indicators: dict) -> go.Figure:
    """Price line with overlaid indicators and buy/sell markers.

    Expected (draft -- finalize with the backend in Step 2):
        prices      DataFrame indexed by date with a ``close`` column.
        signals     DataFrame/Series of trade actions aligned to ``prices``.
        indicators  mapping of label -> Series to overlay (e.g. SMA, bands).
    """
    raise NotImplementedError("Implemented in Step 3 (frontend build).")


def create_equity_curve_chart(equity: pd.DataFrame) -> go.Figure:
    """Portfolio value over time for Buy & Hold and each strategy.

    Expected: ``equity`` is a DataFrame indexed by date with one column per
    series (e.g. ``Buy & Hold``, ``Trend Following``, ``Mean Reversion``,
    ``Custom``).
    """
    raise NotImplementedError("Implemented in Step 3 (frontend build).")


def create_drawdown_chart(drawdowns: pd.DataFrame) -> go.Figure:
    """Drawdown over time for every strategy, same column layout as equity."""
    raise NotImplementedError("Implemented in Step 3 (frontend build).")
