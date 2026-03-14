"""
ProductComparator — side-by-side comparison of two products.

Gathers score distribution, sentiment, helpfulness, review volume,
and temporal activity for two products and produces a structured report.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.database import ReviewDatabase
from models.review import Review
from analyzers.sentiment import SentimentAnalyzer


@dataclass
class ProductProfile:
    """Aggregated profile for a single product."""
    product_id: str
    total_reviews: int
    avg_score: Optional[float]
    score_distribution: Dict[int, int]
    avg_vader_compound: Optional[float]
    mismatch_pct: Optional[float]
    avg_word_count: float
    avg_helpfulness: Optional[float]
    earliest_review: Optional[str]       # date string
    latest_review: Optional[str]         # date string


@dataclass
class ComparisonReport:
    """Side-by-side comparison of two products."""
    product_a: ProductProfile
    product_b: ProductProfile
    winner_by_score: str                 # product_id with higher avg score
    winner_by_volume: str                # product_id with more reviews
    winner_by_sentiment: Optional[str]   # product_id with higher VADER compound


class ProductComparator:
    """Compare two products across multiple dimensions."""

    def __init__(self, db: ReviewDatabase):
        self.db = db
        self._sentiment = SentimentAnalyzer()

    def _build_profile(self, product_id: str, reviews: List[Review]) -> ProductProfile:
        """Build an aggregated profile from a product's reviews."""
        if not reviews:
            return ProductProfile(
                product_id=product_id, total_reviews=0, avg_score=None,
                score_distribution={}, avg_vader_compound=None,
                mismatch_pct=None, avg_word_count=0, avg_helpfulness=None,
                earliest_review=None, latest_review=None,
            )

        avg_score = self.db.get_product_avg_score(product_id)

        # Score distribution
        dist: Dict[int, int] = {}
        for r in reviews:
            dist[r.score] = dist.get(r.score, 0) + 1

        # Sentiment (sample up to 100)
        sample = reviews[:100]
        report = self._sentiment.analyze_batch(sample)
        avg_vader = report.avg_compound if report.total else None
        mismatch_pct = (
            (report.mismatches / report.total * 100) if report.total else None
        )

        # Word count & helpfulness
        wc = sum(r.word_count for r in reviews) / len(reviews)
        help_ratios = [r.helpfulness_ratio for r in reviews if r.helpfulness_ratio is not None]
        avg_help = sum(help_ratios) / len(help_ratios) if help_ratios else None

        # Temporal range
        sorted_by_time = sorted(reviews, key=lambda r: r.time)
        earliest = sorted_by_time[0].date_str
        latest = sorted_by_time[-1].date_str

        return ProductProfile(
            product_id=product_id,
            total_reviews=len(reviews),
            avg_score=round(avg_score, 2) if avg_score else None,
            score_distribution=dict(sorted(dist.items())),
            avg_vader_compound=round(avg_vader, 4) if avg_vader is not None else None,
            mismatch_pct=round(mismatch_pct, 1) if mismatch_pct is not None else None,
            avg_word_count=round(wc, 1),
            avg_helpfulness=round(avg_help, 4) if avg_help is not None else None,
            earliest_review=earliest,
            latest_review=latest,
        )

    def compare(self, product_id_a: str, product_id_b: str) -> ComparisonReport:
        """Run a full comparison between two products."""
        reviews_a = self.db.get_by_product(product_id_a, limit=500)
        reviews_b = self.db.get_by_product(product_id_b, limit=500)

        profile_a = self._build_profile(product_id_a, reviews_a)
        profile_b = self._build_profile(product_id_b, reviews_b)

        # Determine winners
        score_a = profile_a.avg_score or 0
        score_b = profile_b.avg_score or 0
        winner_score = product_id_a if score_a >= score_b else product_id_b

        winner_volume = product_id_a if profile_a.total_reviews >= profile_b.total_reviews else product_id_b

        vader_a = profile_a.avg_vader_compound
        vader_b = profile_b.avg_vader_compound
        if vader_a is not None and vader_b is not None:
            winner_sentiment = product_id_a if vader_a >= vader_b else product_id_b
        else:
            winner_sentiment = None

        return ComparisonReport(
            product_a=profile_a,
            product_b=profile_b,
            winner_by_score=winner_score,
            winner_by_volume=winner_volume,
            winner_by_sentiment=winner_sentiment,
        )
