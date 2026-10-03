import sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))

import pandas as pd
import streamlit as st
from risk_engine import RiskEngine
from ingestion import collect_all
from stress_test import run_stress, portfolio_summary

st.set_page_config(page_title="RiskPulse AI", page_icon="📊", layout="wide")
st.title("📊 RiskPulse AI — Financial Risk Intelligence Engine")
st.caption("Hybrid NLP risk signals + event-driven portfolio stress testing | S&P Global & CRISIL Campus Hackathon 2026")

engine = RiskEngine()

@st.cache_data(ttl=300)
def get_records():
    return collect_all(use_live=True)

records = get_records()
if not records:
    st.warning("No live records returned. Use the demo social feed in data/social_posts.csv.")
    records = []

signals = []
for r in records[:50]:
    signals.append(engine.analyze(r.get("text",""), r.get("source","unknown"), r.get("entity","Unknown")).__dict__)
signals_df = pd.DataFrame(signals)

# Sidebar
st.sidebar.header("Risk Engine Controls")
threshold = st.sidebar.slider("Stress-test trigger (Impact Score)", 1, 10, 7)
event_filter = st.sidebar.selectbox("Event filter", ["All"] + sorted(signals_df["event_classification"].unique().tolist()) if not signals_df.empty else ["All"])
refresh = st.sidebar.button("🔄 Refresh live feeds")

if refresh:
    st.cache_data.clear()
    st.rerun()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Signals processed", len(signals_df))
c2.metric("Avg. sentiment", f"{signals_df.sentiment_score.mean():.2f}" if not signals_df.empty else "—")
c3.metric("High-impact signals", int((signals_df.impact_score >= threshold).sum()) if not signals_df.empty else 0)
c4.metric("Sources", signals_df.source.nunique() if not signals_df.empty else 0)

st.divider()
st.subheader("1. AI/NLP Risk Signals")

with st.expander("🧪 Analyze a headline / post manually"):
    manual_text = st.text_area("Paste unstructured financial text", "GlobalBank faces a credit downgrade after liquidity pressure emerges.")
    manual_entity = st.text_input("Entity", "GlobalBank")
    if st.button("Analyze text"):
        manual = engine.analyze(manual_text, "Manual Input", manual_entity).__dict__
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Sentiment", manual["sentiment_label"])
        m2.metric("Score", manual["sentiment_score"])
        m3.metric("Event", manual["event_classification"])
        m4.metric("Impact", f'{manual["impact_score"]}/10')
        st.json(manual)


if not signals_df.empty:
    show = signals_df.copy()
    if event_filter != "All":
        show = show[show.event_classification == event_filter]
    cols = ["source","entity","sentiment_label","sentiment_score","event_classification","impact_score","text"]
    st.dataframe(show[cols].sort_values("impact_score", ascending=False), use_container_width=True, hide_index=True)

    st.subheader("Risk Distribution")
    st.bar_chart(show["event_classification"].value_counts())
else:
    st.info("No signals available.")

st.divider()
st.subheader("2. Module B — Strategic Portfolio Stress Testing")

portfolio = pd.read_csv(ROOT / "data" / "portfolio.csv")
event_options = ["Geopolitical","Macroeconomic","Credit Event","Merger/Acquisition","Regulatory","Product Launch","Earnings","Other"]
selected_event = st.selectbox("Scenario event", event_options)
impact = st.slider("Scenario impact score", 1, 10, 8)

triggered = impact > threshold
st.write(f"**Stress trigger:** {'ACTIVE' if triggered else 'INACTIVE'}  |  Rule: Impact Score > {threshold}")

if st.button("⚡ Run Stress Test", type="primary"):
    if not triggered:
        st.warning(f"Stress test not triggered: impact score must be greater than {threshold}.")
        st.stop()
    stressed = run_stress(portfolio, selected_event, impact)
    summary = portfolio_summary(stressed)
    a,b,c = st.columns(3)
    a.metric("Portfolio before", f"${summary['before']:,.0f}")
    b.metric("Portfolio after", f"${summary['after']:,.0f}")
    c.metric("Simulated P&L", f"${summary['pnl']:,.0f}", f"{summary['loss_pct']:.2f}%")
    st.bar_chart(stressed.set_index("asset_id")[["market_value","stressed_value"]])
    st.dataframe(stressed[["asset_id","asset_type","market_value","shock_pct","stressed_value","loss"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("Prototype note: stress shocks are synthetic scenario assumptions for hackathon demonstration, not investment advice.")