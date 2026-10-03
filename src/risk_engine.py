import re
from dataclasses import dataclass, asdict
from typing import Dict, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

EVENT_KEYWORDS = {
    "Geopolitical": ["war", "sanction", "conflict", "tariff", "missile", "border", "geopolitical"],
    "Macroeconomic": ["inflation", "interest rate", "rate hike", "recession", "gdp", "unemployment", "central bank"],
    "Credit Event": ["default", "downgrade", "credit", "bankruptcy", "liquidity", "debt restructuring"],
    "Merger/Acquisition": ["merger", "acquire", "acquisition", "takeover", "buyout"],
    "Product Launch": ["launch", "new product", "release", "unveil", "new model"],
    "Regulatory": ["regulator", "regulation", "antitrust", "fine", "lawsuit", "compliance"],
    "Earnings": ["earnings", "revenue", "profit", "loss", "guidance", "quarterly results"],
}

HIGH_IMPACT_TERMS = {
    "default": 4, "bankruptcy": 5, "war": 5, "sanction": 4, "recession": 4,
    "takeover": 3, "acquisition": 3, "antitrust": 3, "downgrade": 3,
    "rate hike": 3, "inflation": 2, "lawsuit": 2, "guidance": 2
}

@dataclass
class RiskSignal:
    source: str
    entity: str
    text: str
    sentiment_score: float
    sentiment_label: str
    event_classification: str
    impact_score: int
    rationale: str

class RiskEngine:
    def __init__(self):
        self.sentiment = SentimentIntensityAnalyzer()

    def _sentiment(self, text: str):
        score = self.sentiment.polarity_scores(text)["compound"]
        label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
        return round(float(score), 4), label

    def _event(self, text: str):
        t = text.lower()
        scores = {event: sum(1 for kw in kws if kw in t) for event, kws in EVENT_KEYWORDS.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] else "Other"

    def _impact(self, text: str, event: str, sentiment: float):
        t = text.lower()
        score = 2
        score += min(4, sum(v for k, v in HIGH_IMPACT_TERMS.items() if k in t))
        if event in {"Geopolitical", "Credit Event", "Macroeconomic"}:
            score += 1
        if abs(sentiment) > 0.65:
            score += 1
        return max(1, min(10, int(score)))

    def analyze(self, text: str, source="unknown", entity="Unknown") -> RiskSignal:
        sentiment, label = self._sentiment(text)
        event = self._event(text)
        impact = self._impact(text, event, sentiment)
        rationale = f"{event} event; sentiment={label.lower()}; severity driven by event keywords and polarity."
        return RiskSignal(source, entity, text, sentiment, label, event, impact, rationale)

    def analyze_many(self, records: List[Dict]) -> List[Dict]:
        return [asdict(self.analyze(r["text"], r.get("source","unknown"), r.get("entity","Unknown"))) for r in records]