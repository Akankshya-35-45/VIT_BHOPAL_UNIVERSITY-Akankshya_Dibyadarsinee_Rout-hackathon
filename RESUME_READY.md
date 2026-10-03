# Resume-ready description

## Project title
**RiskPulse AI — Financial Risk Intelligence & Portfolio Stress Testing**

## One-line version
Built a hybrid NLP risk engine that converts financial news/social text into sentiment, event and impact signals and feeds high-impact events into an event-driven portfolio stress-testing dashboard.

## 2-bullet resume version
- Built a Python NLP risk engine using VADER sentiment analysis and domain-specific event classification to transform unstructured financial news/social text into machine-readable sentiment, event type and 1–10 impact signals.
- Developed a Streamlit strategic portfolio stress-testing module with synthetic equities, bonds, loans and derivatives; exposed the risk engine through FastAPI and integrated live GDELT ingestion with reproducible synthetic data.

## Skills / keywords
Python, NLP, Sentiment Analysis, Financial Risk Analytics, Event Classification, Streamlit, FastAPI, Pandas, REST API, Data Ingestion, GDELT, NewsAPI, Portfolio Stress Testing, Data Visualization, Git/GitHub

## Interview explanation
**Problem:** Financial risk signals often appear first in unstructured text.

**Solution:** Normalize multiple text feeds, score sentiment, classify event type, estimate prototype impact, and pass high-impact signals to a portfolio stress-test engine.

**Why it is interesting:** The project demonstrates the full path from unstructured information to a downstream financial-risk workflow rather than stopping at sentiment classification.

**Honest limitation:** The current impact/event layer is a transparent hybrid MVP. A production system would use a calibrated financial event model, entity linking, confidence scores, historical scenario calibration, streaming infrastructure and model monitoring.
