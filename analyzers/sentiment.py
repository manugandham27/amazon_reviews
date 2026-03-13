"""
SentimentAnalyzer — VADER-based sentiment scoring + star-rating mismatch detection.
"""
from dataclasses import dataclass, field
from typing import List, Dict

from models.review import Review
from config import SENTIMENT_MISMATCH_DELTA

# Lazy-load NLTK VADER to avoid import-time downloads
_sia = None


def _get_analyzer():
    """Lazy-initialize the VADER SentimentIntensityAnalyzer."""
    global _sia
    if _sia is None:
        import nltk
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
        _sia = SentimentIntensityAnalyzer()
    return _sia


@dataclass
class SentimentResult:
    """Sentiment analysis result for a single review."""
    review_id: int
    score: int                    # original star rating (1-5)
    summary: str
    vader_compound: float         # VADER compound score (-1 to +1)
    vader_pos: float
    vader_neg: float
    vader_neu: float
    normalized_score: float       # star rating mapped to -1..+1
    is_mismatch: bool             # True if VADER disagrees with stars

    @property
    def vader_label(self) -> str:
        if self.vader_compound >= 0.05:
            return "positive"
        elif self.vader_compound <= -0.05:
            return "negative"
        return "neutral"

    @property
    def star_label(self) -> str:
        if self.score >= 4:
            return "positive"
        elif self.score <= 2:
            return "negative"
        return "neutral"


@dataclass
class BatchSentimentReport:
    """Aggregated report over a batch of reviews."""
    total: int = 0
    mismatches: int = 0
    avg_compound: float = 0.0
    score_vs_sentiment: Dict[int, float] = field(default_factory=dict)
    mismatch_examples: List[SentimentResult] = field(default_factory=list)


class SentimentAnalyzer:
    """Analyze review text sentiment using VADER and compare with star ratings."""

    @staticmethod
    def _normalize_score(score: int) -> float:
        """Map 1-5 star rating to -1..+1 range."""
        return (score - 3) / 2.0

    def analyze_review(self, review: Review) -> SentimentResult:
        """Run VADER on a single review and compare with its star rating."""
        sia = _get_analyzer()
        scores = sia.polarity_scores(review.text)
        norm = self._normalize_score(review.score)
        mismatch = abs(scores["compound"] - norm) > SENTIMENT_MISMATCH_DELTA

        return SentimentResult(
            review_id=review.id,
            score=review.score,
            summary=review.summary,
            vader_compound=round(scores["compound"], 4),
            vader_pos=round(scores["pos"], 4),
            vader_neg=round(scores["neg"], 4),
            vader_neu=round(scores["neu"], 4),
            normalized_score=round(norm, 4),
            is_mismatch=mismatch,
        )

    def analyze_batch(self, reviews: List[Review]) -> BatchSentimentReport:
        """Analyze a list of reviews and produce an aggregate report."""
        results = [self.analyze_review(r) for r in reviews]
        if not results:
            return BatchSentimentReport()

        mismatches = [r for r in results if r.is_mismatch]

        # Average VADER compound per star rating
        score_sums: Dict[int, List[float]] = {}
        for r in results:
            score_sums.setdefault(r.score, []).append(r.vader_compound)
        score_vs_sentiment = {
            s: round(sum(vals) / len(vals), 4) for s, vals in sorted(score_sums.items())
        }

        return BatchSentimentReport(
            total=len(results),
            mismatches=len(mismatches),
            avg_compound=round(sum(r.vader_compound for r in results) / len(results), 4),
            score_vs_sentiment=score_vs_sentiment,
            mismatch_examples=mismatches[:10],  # cap at 10 examples
        )
