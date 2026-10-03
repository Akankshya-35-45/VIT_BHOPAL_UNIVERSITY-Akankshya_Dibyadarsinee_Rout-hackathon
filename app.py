import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))

import pandas as pd
import streamlit as st

from risk_engine import RiskEngine
from ingestion import collect_all
from stress_test import run_stress, portfolio_summary


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RiskPulse AI",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 RiskPulse AI — Financial Risk Intelligence Engine")

st.caption(
    "Hybrid NLP risk intelligence + event-driven portfolio stress testing "
    "| S&P Global & CRISIL Campus Hackathon 2026"
)


# ============================================================
# INITIALIZE ENGINE
# ============================================================

engine = RiskEngine()


# ============================================================
# DATA INGESTION
# ============================================================

@st.cache_data(ttl=300)
def get_records():
    return collect_all(use_live=True)


records = get_records()

if not records:
    st.warning(
        "No live records returned. Using the synthetic demo feed."
    )

    records = []


# ============================================================
# NLP RISK ANALYSIS
# ============================================================

signals = []

for record in records[:50]:

    signal = engine.analyze(
        text=record.get("text", ""),
        source=record.get("source", "unknown"),
        entity=record.get("entity", "Unknown")
    )

    signals.append(signal.__dict__)


signals_df = pd.DataFrame(signals)


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("⚙️ Risk Engine Controls")

threshold = st.sidebar.slider(
    "Stress-test trigger (Risk Score)",
    min_value=1,
    max_value=100,
    value=60
)


if not signals_df.empty:

    event_filter = st.sidebar.selectbox(
        "Event filter",
        ["All"]
        + sorted(
            signals_df["event_classification"]
            .unique()
            .tolist()
        )
    )

else:

    event_filter = "All"


refresh = st.sidebar.button("🔄 Refresh live feeds")


if refresh:

    st.cache_data.clear()
    st.rerun()


# ============================================================
# EXECUTIVE METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Signals Processed",
    len(signals_df)
)


c2.metric(
    "Average Risk Score",
    (
        f"{signals_df['risk_score'].mean():.1f}"
        if not signals_df.empty
        else "—"
    )
)


c3.metric(
    "High/Critical Signals",
    (
        int(
            (
                signals_df["risk_score"] >= 50
            ).sum()
        )
        if not signals_df.empty
        else 0
    )
)


c4.metric(
    "Entities Monitored",
    (
        signals_df["entity"].nunique()
        if not signals_df.empty
        else 0
    )
)


st.divider()


# ============================================================
# MODULE A
# ============================================================

st.subheader("1. 🧠 AI/NLP Risk Intelligence")


# ------------------------------------------------------------
# MANUAL ANALYSIS
# ------------------------------------------------------------

with st.expander("🧪 Analyze a headline / financial event manually"):

    manual_text = st.text_area(
        "Financial headline / event",
        "GlobalBank faces a credit downgrade after liquidity pressure emerges."
    )

    manual_entity = st.text_input(
        "Entity",
        "GlobalBank"
    )


    if st.button("🔍 Analyze Text"):

        manual = engine.analyze(
            manual_text,
            "Manual Input",
            manual_entity
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "Sentiment",
            manual.sentiment_label
        )

        m2.metric(
            "Event",
            manual.event_classification
        )

        m3.metric(
            "Risk Score",
            f"{manual.risk_score}/100"
        )

        m4.metric(
            "Risk Level",
            manual.risk_level
        )


        st.write("### Analysis Details")

        st.json(manual.__dict__)


# ============================================================
# SIGNAL TABLE
# ============================================================

if not signals_df.empty:

    show = signals_df.copy()


    if event_filter != "All":

        show = show[
            show["event_classification"] == event_filter
        ]


    columns = [
        "source",
        "entity",
        "sentiment_label",
        "sentiment_score",
        "event_classification",
        "event_confidence",
        "impact_score",
        "risk_score",
        "risk_level",
        "rationale",
        "text"
    ]


    st.dataframe(
        show[columns].sort_values(
            "risk_score",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    st.subheader("📈 Event Distribution")

    st.bar_chart(
        show["event_classification"].value_counts()
    )


    # --------------------------------------------------------
    # RISK LEVEL DISTRIBUTION
    # --------------------------------------------------------

    st.subheader("🚨 Risk-Level Distribution")

    st.bar_chart(
        show["risk_level"].value_counts()
    )


else:

    st.info(
        "No signals available."
    )


# ============================================================
# MODULE B
# ============================================================

st.divider()

st.subheader(
    "2. 📉 Module B — Strategic Portfolio Stress Testing"
)


# ============================================================
# LOAD PORTFOLIO
# ============================================================

portfolio_path = ROOT / "data" / "portfolio.csv"

portfolio = pd.read_csv(
    portfolio_path
)


# ============================================================
# STRESS SCENARIO
# ============================================================

event_options = [
    "Geopolitical",
    "Macroeconomic",
    "Credit Event",
    "Merger/Acquisition",
    "Regulatory",
    "Product Launch",
    "Earnings",
    "Other"
]


selected_event = st.selectbox(
    "Scenario Event",
    event_options
)


impact = st.slider(
    "Scenario Impact Score",
    min_value=1,
    max_value=10,
    value=8
)


triggered = impact > 7


if triggered:

    st.success(
        f"⚡ Stress Trigger ACTIVE — Impact Score = {impact}"
    )

else:

    st.info(
        f"Stress Trigger INACTIVE — Impact Score = {impact}"
    )


# ============================================================
# RUN STRESS TEST
# ============================================================

if st.button(
    "⚡ Run Stress Test",
    type="primary"
):

    if not triggered:

        st.warning(
            "Stress test requires an impact score greater than 7."
        )

        st.stop()


    stressed = run_stress(
        portfolio,
        selected_event,
        impact
    )


    summary = portfolio_summary(
        stressed
    )


    # --------------------------------------------------------
    # PORTFOLIO METRICS
    # --------------------------------------------------------

    a, b, c, d = st.columns(4)


    a.metric(
        "Portfolio Before",
        f"${summary['before']:,.0f}"
    )


    b.metric(
        "Portfolio After",
        f"${summary['after']:,.0f}"
    )


    c.metric(
        "Simulated P&L",
        f"${summary['pnl']:,.0f}"
    )


    d.metric(
        "Loss %",
        f"{summary['loss_pct']:.2f}%"
    )


    # --------------------------------------------------------
    # PORTFOLIO IMPACT
    # --------------------------------------------------------

    st.subheader(
        "📊 Portfolio Impact by Asset"
    )


    chart_data = stressed.set_index(
        "asset_id"
    )[[
        "market_value",
        "stressed_value"
    ]]


    st.bar_chart(
        chart_data
    )


    # --------------------------------------------------------
    # STRESS TEST DETAILS
    # --------------------------------------------------------

    st.subheader(
        "Stress-Test Results"
    )


    result_columns = [
        "asset_id",
        "asset_type",
        "market_value",
        "shock_pct",
        "stressed_value",
        "loss"
    ]


    st.dataframe(
        stressed[result_columns],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PROJECT DISCLAIMER
# ============================================================

st.divider()

st.caption(
    "RiskPulse AI is a hackathon prototype using synthetic/public data "
    "and scenario assumptions for demonstration. It is not investment advice."
)