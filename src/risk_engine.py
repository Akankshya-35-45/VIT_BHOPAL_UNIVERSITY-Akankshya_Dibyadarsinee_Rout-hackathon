import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ============================================================
# EVENT TAXONOMY
# ============================================================

EVENT_KEYWORDS = {
    "Geopolitical": [
        "war",
        "sanction",
        "sanctions",
        "conflict",
        "tariff",
        "tariffs",
        "missile",
        "border",
        "geopolitical",
        "trade war",
        "military",
        "escalation",
    ],

    "Macroeconomic": [
        "inflation",
        "interest rate",
        "interest rates",
        "rate hike",
        "rate hike",
        "recession",
        "gdp",
        "unemployment",
        "central bank",
        "monetary policy",
        "economic slowdown",
    ],

    "Credit Event": [
        "default",
        "downgrade",
        "credit",
        "bankruptcy",
        "liquidity",
        "debt restructuring",
        "credit rating",
        "rating downgrade",
        "insolvency",
        "debt crisis",
    ],

    "Merger/Acquisition": [
        "merger",
        "acquire",
        "acquires",
        "acquisition",
        "takeover",
        "buyout",
        "merging",
    ],

    "Product Launch": [
        "launch",
        "new product",
        "release",
        "unveil",
        "new model",
        "product launch",
        "rollout",
    ],

    "Regulatory": [
        "regulator",
        "regulation",
        "regulatory",
        "antitrust",
        "fine",
        "lawsuit",
        "compliance",
        "investigation",
        "penalty",
        "legal action",
    ],

    "Earnings": [
        "earnings",
        "revenue",
        "profit",
        "loss",
        "guidance",
        "quarterly results",
        "quarterly earnings",
        "net income",
        "operating profit",
        "earnings report",
    ],
}


# ============================================================
# HIGH-IMPACT TERMS
# ============================================================

HIGH_IMPACT_TERMS = {
    "default": 4,
    "bankruptcy": 5,
    "war": 5,
    "sanction": 4,
    "sanctions": 4,
    "recession": 4,
    "takeover": 3,
    "acquisition": 3,
    "antitrust": 3,
    "downgrade": 3,
    "rate hike": 3,
    "interest rate": 2,
    "inflation": 2,
    "lawsuit": 2,
    "guidance": 2,
    "liquidity": 2,
    "insolvency": 5,
    "debt crisis": 4,
    "military": 3,
    "escalation": 3,
}


# ============================================================
# EVENT-SPECIFIC BASE RISK
# ============================================================

EVENT_BASE_RISK = {
    "Geopolitical": 5,
    "Macroeconomic": 5,
    "Credit Event": 5,
    "Regulatory": 4,
    "Merger/Acquisition": 3,
    "Earnings": 3,
    "Product Launch": 2,
    "Other": 1,
}


# ============================================================
# RISK SIGNAL DATA MODEL
# ============================================================

@dataclass
class RiskSignal:
    source: str
    entity: str
    text: str

    sentiment_score: float
    sentiment_label: str

    event_classification: str
    event_confidence: float

    impact_score: int
    risk_score: int
    risk_level: str

    matched_keywords: List[str]

    rationale: str


# ============================================================
# RISK ENGINE
# ============================================================

class RiskEngine:

    def __init__(self):
        """
        Initialize the NLP sentiment analyzer.
        """

        self.sentiment = SentimentIntensityAnalyzer()

    # ========================================================
    # TEXT NORMALIZATION
    # ========================================================

    def _normalize_text(self, text: str) -> str:
        """
        Normalize incoming text before analysis.

        This makes matching more reliable and prevents
        unnecessary differences caused by capitalization
        or extra whitespace.
        """

        if not text:
            return ""

        text = str(text).strip().lower()

        # Normalize multiple spaces.
        text = re.sub(r"\s+", " ", text)

        return text

    # ========================================================
    # SAFE KEYWORD MATCHING
    # ========================================================

    def _keyword_matches(
        self,
        text: str,
        keywords: List[str]
    ) -> List[str]:
        """
        Detect keywords as complete words or phrases.

        Example:

        "war" will match:
            "A new war has started."

        but will not incorrectly match:
            "software"

        This is safer than simple substring matching.
        """

        text_lower = self._normalize_text(text)

        matches = []

        for keyword in keywords:

            keyword_lower = keyword.lower().strip()

            if not keyword_lower:
                continue

            pattern = r"\b" + re.escape(keyword_lower) + r"\b"

            if re.search(pattern, text_lower):

                matches.append(keyword)

        return matches

    # ========================================================
    # SENTIMENT ANALYSIS
    # ========================================================

    def _sentiment(
        self,
        text: str
    ) -> Tuple[float, str]:
        """
        Calculate VADER compound sentiment score.

        Score range:
            -1 → strongly negative
             0 → neutral
            +1 → strongly positive
        """

        if not text:
            return 0.0, "Neutral"

        score = self.sentiment.polarity_scores(text)["compound"]

        if score >= 0.05:

            label = "Positive"

        elif score <= -0.05:

            label = "Negative"

        else:

            label = "Neutral"

        return round(float(score), 4), label

    # ========================================================
    # EVENT CLASSIFICATION
    # ========================================================

    def _event(
        self,
        text: str
    ) -> Tuple[str, float, List[str]]:
        """
        Classify the financial event using the event taxonomy.

        Returns:

        event
        confidence
        matched keywords
        """

        text_lower = self._normalize_text(text)

        if not text_lower:

            return "Other", 0.0, []

        scores = {}

        matched_by_event = {}

        # ----------------------------------------------------
        # Count matching keywords for every event.
        # ----------------------------------------------------

        for event, keywords in EVENT_KEYWORDS.items():

            matches = self._keyword_matches(
                text_lower,
                keywords
            )

            matched_by_event[event] = matches

            scores[event] = len(matches)

        # ----------------------------------------------------
        # Find the event with the highest number of matches.
        # ----------------------------------------------------

        best_event = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_event]

        total_matches = sum(scores.values())

        # ----------------------------------------------------
        # No event detected.
        # ----------------------------------------------------

        if best_score == 0:

            return "Other", 0.0, []

        # ----------------------------------------------------
        # Confidence calculation.
        #
        # Example:
        #
        # Geopolitical = 2 matches
        # Credit Event = 1 match
        #
        # Confidence = 2 / 3 = 66.7%
        # ----------------------------------------------------

        confidence = best_score / max(
            total_matches,
            1
        )

        matched_keywords = matched_by_event[best_event]

        return (
            best_event,
            round(confidence, 4),
            matched_keywords
        )

    # ========================================================
    # IMPACT SCORE
    # ========================================================

    def _impact(
        self,
        text: str,
        event: str,
        sentiment: float
    ) -> Tuple[int, List[str]]:
        """
        Calculate event impact on a 1–10 scale.

        The score considers:

        1. Event base risk
        2. High-impact financial keywords
        3. Sentiment strength
        """

        text_lower = self._normalize_text(text)

        # ----------------------------------------------------
        # Start with event-specific base risk.
        # ----------------------------------------------------

        score = EVENT_BASE_RISK.get(
            event,
            1
        )

        matched_terms = []

        # ----------------------------------------------------
        # Add risk contribution from high-impact terms.
        # ----------------------------------------------------

        for keyword, weight in HIGH_IMPACT_TERMS.items():

            pattern = r"\b" + re.escape(
                keyword.lower()
            ) + r"\b"

            if re.search(
                pattern,
                text_lower
            ):

                score += weight

                matched_terms.append(keyword)

        # ----------------------------------------------------
        # Strong sentiment increases impact slightly.
        # ----------------------------------------------------

        if abs(sentiment) > 0.65:

            score += 1

        # ----------------------------------------------------
        # Keep score between 1 and 10.
        # ----------------------------------------------------

        score = max(
            1,
            min(
                10,
                int(score)
            )
        )

        return score, matched_terms

    # ========================================================
    # OVERALL RISK SCORE
    # ========================================================

    def _risk_score(
        self,
        impact_score: int,
        event_confidence: float,
        sentiment: float
    ) -> int:
        """
        Calculate normalized overall risk score from 0–100.

        Components:

        Impact:
            Maximum contribution = 70

        Event confidence:
            Maximum contribution = 20

        Negative sentiment:
            Maximum contribution = 10
        """

        # ----------------------------------------------------
        # Impact component
        # ----------------------------------------------------

        impact_component = impact_score * 7

        # ----------------------------------------------------
        # Event confidence component
        # ----------------------------------------------------

        confidence_component = (
            event_confidence * 20
        )

        # ----------------------------------------------------
        # Negative sentiment component
        # ----------------------------------------------------

        sentiment_component = (
            max(
                0,
                -sentiment
            ) * 10
        )

        # ----------------------------------------------------
        # Final score
        # ----------------------------------------------------

        score = (
            impact_component
            + confidence_component
            + sentiment_component
        )

        return max(
            0,
            min(
                100,
                round(score)
            )
        )

    # ========================================================
    # RISK LEVEL
    # ========================================================

    def _risk_level(
        self,
        risk_score: int
    ) -> str:
        """
        Convert numerical risk score into
        an interpretable risk category.
        """

        if risk_score >= 75:

            return "Critical"

        if risk_score >= 50:

            return "High"

        if risk_score >= 25:

            return "Medium"

        return "Low"

    # ========================================================
    # RISK RATIONALE
    # ========================================================

    def _generate_rationale(
        self,
        event: str,
        confidence: float,
        sentiment_label: str,
        impact_score: int,
        risk_score: int,
        matched_keywords: List[str]
    ) -> str:
        """
        Generate a human-readable explanation
        for the calculated risk.
        """

        if matched_keywords:

            keyword_text = ", ".join(
                matched_keywords
            )

            rationale = (
                f"{event} event detected with "
                f"{confidence:.0%} classification confidence. "
                f"Impact score={impact_score}/10. "
                f"Risk score={risk_score}/100. "
                f"Key risk indicators: "
                f"{keyword_text}. "
                f"Sentiment={sentiment_label.lower()}."
            )

        else:

            rationale = (
                f"{event} event detected with "
                f"{confidence:.0%} classification confidence. "
                f"Impact score={impact_score}/10. "
                f"Risk score={risk_score}/100. "
                f"No major high-impact keywords detected. "
                f"Sentiment={sentiment_label.lower()}."
            )

        return rationale

    # ========================================================
    # MAIN ANALYSIS FUNCTION
    # ========================================================

    def analyze(
        self,
        text: str,
        source: str = "unknown",
        entity: str = "Unknown"
    ) -> RiskSignal:
        """
        Run the complete risk-analysis pipeline.

        Pipeline:

        Text
          ↓
        Sentiment Analysis
          ↓
        Event Classification
          ↓
        Event Confidence
          ↓
        Impact Score
          ↓
        Overall Risk Score
          ↓
        Risk Level
          ↓
        Explainable Rationale
        """

        # ----------------------------------------------------
        # Validate input.
        # ----------------------------------------------------

        text = str(text).strip()

        if not text:

            return RiskSignal(
                source=source,
                entity=entity,
                text=text,
                sentiment_score=0.0,
                sentiment_label="Neutral",
                event_classification="Other",
                event_confidence=0.0,
                impact_score=1,
                risk_score=0,
                risk_level="Low",
                matched_keywords=[],
                rationale=(
                    "No text was provided for risk analysis."
                ),
            )

        # ----------------------------------------------------
        # 1. Sentiment
        # ----------------------------------------------------

        sentiment, sentiment_label = self._sentiment(
            text
        )

        # ----------------------------------------------------
        # 2. Event classification
        # ----------------------------------------------------

        event, event_confidence, event_keywords = self._event(
            text
        )

        # ----------------------------------------------------
        # 3. Impact score
        # ----------------------------------------------------

        impact, impact_keywords = self._impact(
            text,
            event,
            sentiment
        )

        # ----------------------------------------------------
        # 4. Combine detected keywords
        # ----------------------------------------------------

        matched_keywords = list(
            dict.fromkeys(
                event_keywords + impact_keywords
            )
        )

        # ----------------------------------------------------
        # 5. Overall risk score
        # ----------------------------------------------------

        risk_score = self._risk_score(
            impact,
            event_confidence,
            sentiment
        )

        # ----------------------------------------------------
        # 6. Risk level
        # ----------------------------------------------------

        risk_level = self._risk_level(
            risk_score
        )

        # ----------------------------------------------------
        # 7. Explainable rationale
        # ----------------------------------------------------

        rationale = self._generate_rationale(
            event=event,
            confidence=event_confidence,
            sentiment_label=sentiment_label,
            impact_score=impact,
            risk_score=risk_score,
            matched_keywords=matched_keywords,
        )

        # ----------------------------------------------------
        # 8. Return structured risk signal
        # ----------------------------------------------------

        return RiskSignal(
            source=source,
            entity=entity,
            text=text,
            sentiment_score=sentiment,
            sentiment_label=sentiment_label,
            event_classification=event,
            event_confidence=event_confidence,
            impact_score=impact,
            risk_score=risk_score,
            risk_level=risk_level,
            matched_keywords=matched_keywords,
            rationale=rationale,
        )

    # ========================================================
    # BATCH ANALYSIS
    # ========================================================

    def analyze_many(
        self,
        records: List[Dict]
    ) -> List[Dict]:
        """
        Analyze multiple financial records.
        """

        results = []

        for record in records:

            signal = self.analyze(
                text=record.get(
                    "text",
                    ""
                ),
                source=record.get(
                    "source",
                    "unknown"
                ),
                entity=record.get(
                    "entity",
                    "Unknown"
                ),
            )

            results.append(
                asdict(signal)
            )

        return results