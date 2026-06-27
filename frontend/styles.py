import streamlit as st


def inject_styles() -> None:
    """Apply the visual system for the strategy backtesting terminal."""
    st.markdown(
        """
        <style>
        :root {
            --ink: #0a0c0f;
            --panel: #11151a;
            --panel-raised: #161b21;
            --line: #29313a;
            --muted: #87919d;
            --paper: #edf1f3;
            --amber: #e5b454;
            --cyan: #63d2c6;
            --coral: #ef765f;
        }

        .stApp {
            background:
                radial-gradient(circle at 85% -10%, rgba(99, 210, 198, 0.08), transparent 25rem),
                var(--ink);
            color: var(--paper);
        }

        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: 1380px;
            padding: 2.4rem 2.5rem 4rem;
        }

        [data-testid="stHeader"] {
            display: none;
        }

        #MainMenu, [data-testid="stToolbar"], footer {
            visibility: hidden;
        }

        h1, h2, h3, p {
            color: var(--paper);
        }

        .terminal-header {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 2rem;
            margin-bottom: 1.6rem;
        }

        .brand-line {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 0.65rem;
        }

        .brand-mark {
            border: 1px solid var(--amber);
            color: var(--amber);
            font: 700 0.68rem/1 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.16em;
            padding: 0.45rem 0.55rem;
        }

        .brand-kicker, .section-kicker {
            color: var(--muted);
            font: 600 0.68rem/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .terminal-header h1.terminal-title {
            color: var(--paper);
            font-size: clamp(2rem, 4vw, 3.75rem) !important;
            font-weight: 550 !important;
            letter-spacing: -0.055em !important;
            line-height: 0.96 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .terminal-subtitle {
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.5;
            margin: 0;
            max-width: 26rem;
            text-align: right;
        }

        .st-key-command_bar {
            background: rgba(17, 21, 26, 0.92);
            border: 1px solid var(--line);
            border-left: 3px solid var(--amber);
            padding: 0.85rem 1rem 0.2rem;
            margin-bottom: 0.75rem;
        }

        .st-key-command_bar [data-testid="stWidgetLabel"] p {
            color: var(--muted);
            font: 600 0.65rem/1 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        .stTextInput input, [data-baseweb="select"] > div {
            background: #0c1014 !important;
            border-color: var(--line) !important;
            border-radius: 2px !important;
            color: var(--paper) !important;
        }

        .stTextInput input:focus {
            border-color: var(--amber) !important;
            box-shadow: 0 0 0 1px var(--amber) !important;
        }

        div.stButton > button,
        div.stButton > button[kind="primary"] {
            min-height: 2.55rem;
            border: 1px solid var(--amber) !important;
            border-radius: 2px !important;
            background: var(--amber) !important;
            color: #17130b !important;
            font: 700 0.72rem/1 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        div.stButton > button:hover,
        div.stButton > button[kind="primary"]:hover {
            border-color: #f3ca78 !important;
            background: #f3ca78 !important;
            color: #17130b !important;
        }

        .environment-note {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            color: var(--muted);
            font: 500 0.68rem/1.4 ui-monospace, SFMono-Regular, Menlo, monospace;
            margin: 0 0 2.2rem 0.2rem;
        }

        .environment-dot {
            width: 0.42rem;
            height: 0.42rem;
            border-radius: 50%;
            background: var(--amber);
            box-shadow: 0 0 0 3px rgba(229, 180, 84, 0.12);
        }

        .section-heading {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1rem;
            border-bottom: 1px solid var(--line);
            padding-bottom: 0.8rem;
            margin: 0.25rem 0 1rem;
        }

        .section-heading h2.section-title {
            color: var(--paper);
            font-size: 1.35rem !important;
            font-weight: 550 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.2 !important;
            margin: 0.35rem 0 0 !important;
            padding: 0 !important;
        }

        .status-block {
            text-align: right;
        }

        .status-line {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: var(--cyan);
            font: 650 0.66rem/1 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .status-line.offline {
            color: var(--coral);
        }

        .status-pulse {
            width: 0.45rem;
            height: 0.45rem;
            border-radius: 50%;
            background: currentColor;
        }

        .update-time {
            color: var(--muted);
            font: 500 0.62rem/1.3 ui-monospace, SFMono-Regular, Menlo, monospace;
            margin-top: 0.35rem;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1px;
            background: var(--line);
            border: 1px solid var(--line);
            margin-bottom: 2.4rem;
        }

        .metric-cell {
            background: var(--panel);
            min-height: 6.6rem;
            padding: 1.1rem 1.2rem;
        }

        .metric-label {
            color: var(--muted);
            font: 600 0.66rem/1 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .metric-value {
            color: var(--paper);
            font: 500 clamp(1.5rem, 3vw, 2.2rem)/1.05 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: -0.05em;
            margin-top: 1.1rem;
        }

        .metric-value.accent {
            color: var(--amber);
        }

        .metric-value.up {
            color: var(--cyan);
        }

        .metric-value.down {
            color: var(--coral);
        }

        .metric-unit {
            color: var(--muted);
            font-size: 0.7rem;
            letter-spacing: 0;
            margin-left: 0.25rem;
        }

        .period-chip {
            border: 1px solid var(--line);
            color: var(--muted);
            font: 600 0.64rem/1 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.08em;
            padding: 0.45rem 0.55rem;
            text-transform: uppercase;
        }

        [data-testid="stPlotlyChart"] {
            border: 1px solid var(--line);
            background: var(--panel);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
        }

        [data-testid="stExpander"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 2px;
        }

        [data-testid="stExpander"] summary p {
            color: var(--muted);
            font: 600 0.68rem/1 ui-monospace, SFMono-Regular, Menlo, monospace;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        @media (max-width: 760px) {
            [data-testid="stAppViewContainer"] > .main .block-container {
                padding: 1.4rem 1rem 3rem;
            }

            .terminal-header {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.8rem;
            }

            .terminal-subtitle {
                text-align: left;
            }

            .metric-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .section-heading {
                align-items: flex-start;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
