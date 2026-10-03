# 5–7 minute demo script

1. **0:00–0:30 — Problem**
   “Financial risk often appears first as unstructured language. RiskPulse AI converts that language into structured risk signals and demonstrates how those signals can drive a portfolio stress test.”

2. **0:30–1:15 — Architecture**
   Show `docs/architecture.png`. Explain GDELT/NewsAPI → NLP engine → risk signal → Module B.

3. **1:15–2:30 — Live ingestion**
   Run `streamlit run app.py`. Point to the signal table. Show source, sentiment, event class and impact score. Click Refresh if needed.

4. **2:30–4:00 — Stress test**
   Choose “Geopolitical”, impact 8. Click Run Stress Test. Explain that the trigger is Impact > threshold and the shocks are synthetic, transparent assumptions.

5. **4:00–4:45 — API**
   Show:
   `uvicorn src.api:app --reload`
   and explain `/analyze` returns the same machine-readable fields.

6. **4:45–5:30 — Domain impact**
   Explain traceability and downstream use.

7. **5:30–6:00 — Limitations**
   Be explicit: hybrid MVP today; production path is trained financial NLP + streaming + calibrated scenarios.
