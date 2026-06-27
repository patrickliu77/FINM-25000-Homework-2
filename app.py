import streamlit as st

from frontend.styles import inject_styles

st.set_page_config(
    page_title="Strategy Backtesting Terminal",
    page_icon=":material/finance:",
    layout="wide",
)

inject_styles()

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

st.markdown(
    """
    <div class="environment-note">
        <span class="environment-dot"></span>
        Scaffold / interface under construction / backend contract pending
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Project scaffold. The command bar, indicator overlays, equity-curve and "
    "drawdown charts, and the performance table are built in Step 3 once the "
    "backend contract is finalized."
)
