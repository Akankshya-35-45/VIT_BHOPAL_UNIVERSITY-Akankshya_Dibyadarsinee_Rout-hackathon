# RiskPulse AI - S&P Global & CRISIL Campus Hackathon 2026

**Candidate Name:** Akankshya Dibyadarsinee Rout  
**College / Campus:** VIT Bhopal University  
**Project:** AI/NLP Financial Risk Intelligence Engine + Strategic Portfolio Stress Testing

## 1. Project Overview / Problem Statement & Approach

Financial risk can emerge first as unstructured language: breaking news, market commentary and social-media discussion. RiskPulse AI converts these text streams into structured signals that a downstream portfolio application can consume.

The prototype uses a hybrid NLP pipeline. It ingests live GDELT news, optionally ingests NewsAPI articles when `NEWSAPI_KEY` is configured, and combines them with a synthetic social-media feed included in `/data`. Each text item receives a sentiment score, sentiment label, event classification and 1–10 impact score.

The downstream application is **Module B: Strategic Portfolio Stress Testing**. When an event exceeds a configurable impact threshold, the engine applies transparent synthetic shocks to a portfolio containing equities, bonds, loans and derivatives. The dashboard shows portfolio value before/after the scenario and asset-level losses.

## 2. Architecture & Tech Stack

**Flow**

`GDELT / NewsAPI / Social Feed → Normalization → NLP Risk Engine → Risk Signals → Stress-Test Trigger → Scenario Shocks → Dashboard`

Tech stack:
- Python 3.11+
- Streamlit dashboard
- FastAPI risk endpoint
- Pandas
- VADER sentiment analysis
- Hybrid keyword event classification + impact scoring
- GDELT live news API
- Optional NewsAPI
- Synthetic portfolio + social-media demo data

### API

Run:
```bash
uvicorn src.api:app --reload
```

Then POST JSON to `/analyze`:
```json
{
  "text": "Bank announces a major credit downgrade after liquidity pressure.",
  "source": "demo",
  "entity": "GlobalBank"
}
```

## 3. Dataset Used

- **GDELT:** live public news source for the prototype. The DOC 2.0 API supports article-list JSON output and time-windowed searches.
- **NewsAPI:** optional second live news source; requires an API key.
- **Social feed:** synthetic, non-proprietary records in `data/social_posts.csv`.
- **Portfolio:** synthetic wholesale-banking-style asset mix in `data/portfolio.csv`.

No confidential S&P Global or CRISIL data is used.

## 4. Quickstart & Installation

Runtime: Python 3.11+.

```bash
git clone <YOUR_PUBLIC_REPO_URL>
cd spglobal-crisil-risk-engine

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Optional live NewsAPI:
```bash
copy .env.example .env
# add NEWSAPI_KEY=...
```

The dashboard still works with GDELT + synthetic social feed if NewsAPI is not configured.

## 5. Key Results & Domain Impact

The prototype demonstrates:
1. Multi-source unstructured-data ingestion.
2. Machine-readable risk signals: sentiment, event class and impact.
3. A configurable high-impact event trigger.
4. Event-specific portfolio shocks.
5. Before/after portfolio valuation and asset-level loss visualization.
6. API access for downstream applications.

The scenario model is deliberately transparent for hackathon evaluation: shocks are synthetic assumptions, not investment recommendations.

## 6. Repository Structure

```text
spglobal-crisil-risk-engine/
├── README.md
├── requirements.txt
├── LICENSE
├── .env.example
├── app.py
├── src/
│   ├── risk_engine.py
│   ├── ingestion.py
│   ├── stress_test.py
│   └── api.py
├── data/
│   ├── social_posts.csv
│   └── portfolio.csv
└── docs/
    ├── presentation.pptx
    └── architecture.png
```

## 7. Limitations & Next Steps

- The MVP uses transparent hybrid NLP rather than a large financial language model.
- Social-media records are synthetic for reproducibility.
- Stress shocks are illustrative assumptions.
- Next step: replace keyword event classification with a fine-tuned FinBERT/financial event classifier, add entity recognition, confidence calibration, event deduplication, streaming queues and model monitoring.

## Demo

Add the final unlisted YouTube demo URL here before submission.

## Academic / AI Use

AI assistance was used during development; all implementation choices, testing and final submission should be reviewed by the candidate before submission.

## 8. Resume-Ready Project Summary

**RiskPulse AI — Financial Risk Intelligence & Portfolio Stress Testing:** Built a hybrid NLP risk engine using VADER sentiment analysis and domain event classification to convert unstructured financial text into sentiment, event and impact signals; developed a Streamlit event-driven portfolio stress-testing workflow and exposed the engine through FastAPI.

## 9. Reproducibility

The repository contains all synthetic data required for the demo. Live GDELT ingestion is attempted at runtime; if live retrieval is unavailable, the synthetic social feed keeps the prototype reproducible. NewsAPI is optional and requires `NEWSAPI_KEY`.
