"""
StatisticsAnalyzer — descriptive analytics and insights from the reviews database.
"""
from typing import Dict, Any, List

from models.database import ReviewDatabase


class StatisticsAnalyzer:
    """Generate descriptive statistics and insights from the reviews database."""

    def __init__(self, db: ReviewDatabase):
        self.db = db

    def summary_stats(self) -> Dict[str, Any]:
        """High-level dataset summary."""
        total = self.db.count()
        uniques = self.db.get_unique_counts()
        helpfulness = self.db.get_helpfulness_stats()
        score_dist = self.db.get_score_distribution()

        total_reviews = sum(score_dist.values())
        weighted_avg = (
            sum(score * count for score, count in score_dist.items()) / total_reviews
            if total_reviews
            else 0
        )

        return {
            "total_reviews": total,
            "unique_products": uniques["products"],
            "unique_users": uniques["users"],
            "avg_score": round(weighted_avg, 2),
            "score_distribution": score_dist,
            "avg_text_length": helpfulness["avg_text_len"],
            "avg_summary_length": helpfulness["avg_summary_len"],
            "avg_helpfulness_numerator": helpfulness["avg_helpful_num"],
            "avg_helpfulness_denominator": helpfulness["avg_helpful_den"],
        }

    def temporal_trends(self) -> Dict[str, int]:
        """Year-over-year review counts."""
        return self.db.get_yearly_counts()

    def top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Most reviewed products with their average scores."""
        raw = self.db.get_top_products(limit)
        results = []
        for product_id, count in raw:
            avg = self.db.get_product_avg_score(product_id)
            results.append({
                "product_id": product_id,
                "review_count": count,
                "avg_score": round(avg, 2) if avg else None,
            })
        return results

    def top_reviewers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Most active reviewers."""
        raw = self.db.get_top_reviewers(limit)
        return [
            {"user_id": uid, "profile_name": name, "review_count": cnt}
            for uid, name, cnt in raw
        ]

    def helpfulness_analysis(self) -> Dict[str, Any]:
        """Helpful-vote analysis across score buckets."""
        conn = self.db.connection
        cur = conn.execute(
            "SELECT Score, "
            "  AVG(CASE WHEN HelpfulnessDenominator > 0 "
            "       THEN CAST(HelpfulnessNumerator AS FLOAT) / HelpfulnessDenominator "
            "       ELSE NULL END) as avg_ratio, "
            "  SUM(HelpfulnessDenominator) as total_votes "
            "FROM Reviews GROUP BY Score ORDER BY Score"
        )
        buckets = {}
        for row in cur.fetchall():
            buckets[row[0]] = {
                "avg_helpfulness_ratio": round(row[1], 4) if row[1] else 0,
                "total_votes": row[2],
            }
        return buckets

    def review_length_analysis(self) -> Dict[str, Any]:
        """Review length stats per score bucket."""
        conn = self.db.connection
        cur = conn.execute(
            "SELECT Score, "
            "  AVG(LENGTH(Text)) as avg_len, "
            "  MIN(LENGTH(Text)) as min_len, "
            "  MAX(LENGTH(Text)) as max_len "
            "FROM Reviews GROUP BY Score ORDER BY Score"
        )
        buckets = {}
        for row in cur.fetchall():
            buckets[row[0]] = {
                "avg_length": round(row[1], 1),
                "min_length": row[2],
                "max_length": row[3],
            }
        return buckets
