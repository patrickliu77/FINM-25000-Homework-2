import pandas as pd
import streamlit as st

from contract import BacktestReport, StrategyResult
from frontend.charts import (
    create_drawdown_chart,
    create_equity_curve_chart,
    create_price_chart,
)
from frontend.styles import inject_styles
from frontend.validation import normalize_ticker

# --------------------------------------------------------------------------- #
# BACKEND INTEGRATION POINT                                                     #
# --------------------------------------------------------------------------- #
# The frontend is currently driven by synthetic data so it can be built and    #
# demoed without the backend. When the backend module `backtest_service.py`     #
# is ready (a class implementing the BacktestService contract in contract.py),  #
# swap the import below for:                                                     #
#                                                                               #
#     from backtest_service import AlpacaBacktestService as BacktestService     #
#                                                                               #
# Nothing else in this file needs to change -- both services return the same    #
# BacktestReport objects. See README "Backend integration contract".            #
# --------------------------------------------------------------------------- #
from frontend.mock_backtest import MockBacktestService as BacktestService

YEARS = 5

st.set_page_config(
    page_title="Strategy Backtesting Terminal",
    page_icon=":material/finance:",
    layout="wide",
)

inject_styles()


@st.cache_resource
def get_service() -> BacktestService:
    return BacktestService()


@st.cache_data(ttl=600, show_spinner=False)
def run_backtest(symbol: str, years: int) -> BacktestReport:
    return get_service().run_backtest(symbol, years)


def _pct(value: float) -> str:
    return f"{value * 100:,.1f}%"


def _ratio(value: float) -> str:
    return f"{value:,.2f}"


def metric_card(label: str, value: str, tone: str = "") -> str:
    tone_class = f" {tone}" if tone else ""
    return (
        '<div class="metric-cell">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value{tone_class}">{value}</div>'
        "</div>"
    )


def render_metric_cards(result: StrategyResult) -> None:
    m = result.metrics
    cards = [
        metric_card("Total Return", _pct(m["total_return"]), "up" if m["total_return"] >= 0 else "down"),
        metric_card("CAGR", _pct(m["cagr"]), "up" if m["cagr"] >= 0 else "down"),
        metric_card("Sharpe", _ratio(m["sharpe"]), "accent"),
        metric_card("Max Drawdown", _pct(m["max_drawdown"]), "down"),
    ]
    st.markdown(f'<div class="metric-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def comparison_table(report: BacktestReport) -> pd.DataFrame:
    rows = {}
    for result in [report.buy_hold, *report.strategies.values()]:
        m = result.metrics
        rows[result.name] = {
            "Total Return": _pct(m["total_return"]),
            "CAGR": _pct(m["cagr"]),
            "Volatility": _pct(m["volatility"]),
            "Sharpe": _ratio(m["sharpe"]),
            "Sortino": _ratio(m["sortino"]),
            "Max Drawdown": _pct(m["max_drawdown"]),
            "Win Rate": _pct(m["win_rate"]),
        }
    return pd.DataFrame(rows).T


# --------------------------------------------------------------------------- #
# Header                                                                        #
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <header class="terminal-header">
        <div>
            <div class="brand-line">
                <span class="brand-mark">BKT/02</span>
                <span class="brand-kicker">FINM 25000 / Strategy Backtesting</span>
            </div>
            <h1 class="terminal-title">Backtest terminal.</h1>
        </div>
        <p class="terminal-subtitle">
            Five years of daily bars, a shelf of technical indicators, and several
            strategies compared on a risk-adjusted basis.
        </p>
    </header>
    """,
    unsafe_allow_html=True,
)

service = get_service()

if "symbol" not in st.session_state:
    st.session_state.symbol = "AAPL"
if "strategy" not in st.session_state:
    st.session_state.strategy = service.available_strategies()[0]

with st.container(key="command_bar"):
    ticker_col, strategy_col, action_col = st.columns([2.2, 1.6, 1.2], vertical_alignment="bottom")
    ticker_input = ticker_col.text_input("Ticker symbol", value=st.session_state.symbol)
    strategy_choice = strategy_col.selectbox(
        "Price chart strategy",
        options=service.available_strategies(),
        index=service.available_strategies().index(st.session_state.strategy),
    )
    run_clicked = action_col.button("Run backtest", type="primary", width="stretch")

if run_clicked:
    try:
        st.session_state.symbol = normalize_ticker(ticker_input)
    except ValueError as error:
        st.error(str(error))
    st.session_state.strategy = strategy_choice

report = run_backtest(st.session_state.symbol, YEARS)

source_note = "Synthetic data / mock backend" if report.using_mock else "Live Alpaca data"
st.markdown(
    f"""
    <div class="environment-note">
        <span class="environment-dot"></span>
        {source_note} / {report.symbol} / {report.years}Y daily / $100,000 initial / long-only
    </div>
    """,
    unsafe_allow_html=True,
)

selected = report.strategies[st.session_state.strategy]

# --------------------------------------------------------------------------- #
# Selected-strategy metric cards                                               #
# --------------------------------------------------------------------------- #
render_metric_cards(selected)

# --------------------------------------------------------------------------- #
# Price chart with indicators and buy/sell signals                            #
# --------------------------------------------------------------------------- #
st.markdown(
    f"""
    <section class="section-heading">
        <div>
            <div class="section-kicker">Price &amp; signals</div>
            <h2 class="section-title">{report.symbol} / {selected.name}</h2>
        </div>
        <span class="period-chip">{report.years}Y / 1D</span>
    </section>
    """,
    unsafe_allow_html=True,
)
st.plotly_chart(create_price_chart(report.prices, selected), width="stretch")

# --------------------------------------------------------------------------- #
# Equity curve comparison                                                       #
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <section class="section-heading">
        <div>
            <div class="section-kicker">Equity curve</div>
            <h2 class="section-title">Portfolio value / Buy &amp; Hold vs strategies</h2>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)
st.plotly_chart(create_equity_curve_chart(report), width="stretch")

# --------------------------------------------------------------------------- #
# Drawdown comparison                                                           #
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <section class="section-heading">
        <div>
            <div class="section-kicker">Drawdown</div>
            <h2 class="section-title">Peak-to-trough decline by strategy</h2>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)
st.plotly_chart(create_drawdown_chart(report), width="stretch")

# --------------------------------------------------------------------------- #
# Performance comparison table                                                 #
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <section class="section-heading">
        <div>
            <div class="section-kicker">Performance</div>
            <h2 class="section-title">Risk-adjusted comparison</h2>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)
st.dataframe(comparison_table(report), width="stretch")

with st.expander("Inspect raw OHLCV rows"):
    st.dataframe(report.prices.tail(120), width="stretch")
