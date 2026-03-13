"""
ReviewDatabase — thin wrapper around the SQLite reviews database.
"""
import sqlite3
from typing import List, Optional, Dict, Tuple

from models.review import Review
from config import DATABASE_PATH, TABLE_NAME


class ReviewDatabase:
    """Query interface for the Amazon Fine Food Reviews SQLite database."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self._path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    # ---- context manager ----------------------------------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Open the database connection."""
        self._conn = sqlite3.connect(self._path)

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected. Use `with ReviewDatabase() as db:` or call db.connect().")
        return self._conn

    # ---- core queries -------------------------------------------------------

    def count(self) -> int:
        """Total number of reviews."""
        cur = self.connection.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        return cur.fetchone()[0]

    def get_reviews(self, limit: int = 100, offset: int = 0) -> List[Review]:
        """Fetch reviews with pagination."""
        cur = self.connection.execute(
            f"SELECT * FROM {TABLE_NAME} LIMIT ? OFFSET ?", (limit, offset)
        )
        return [Review.from_row(row) for row in cur.fetchall()]

    def get_by_product(self, product_id: str, limit: int = 100) -> List[Review]:
        """Get reviews for a specific product."""
        cur = self.connection.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE ProductId = ? ORDER BY Time DESC LIMIT ?",
            (product_id, limit),
        )
        return [Review.from_row(row) for row in cur.fetchall()]

    def get_by_user(self, user_id: str, limit: int = 100) -> List[Review]:
        """Get reviews by a specific user."""
        cur = self.connection.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE UserId = ? ORDER BY Time DESC LIMIT ?",
            (user_id, limit),
        )
        return [Review.from_row(row) for row in cur.fetchall()]

    def search_text(self, query: str, limit: int = 20) -> List[Review]:
        """Full-text search across Summary and Text columns."""
        pattern = f"%{query}%"
        cur = self.connection.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE Summary LIKE ? OR Text LIKE ? LIMIT ?",
            (pattern, pattern, limit),
        )
        return [Review.from_row(row) for row in cur.fetchall()]

    # ---- aggregation queries ------------------------------------------------

    def get_score_distribution(self) -> Dict[int, int]:
        """Returns {score: count} mapping."""
        cur = self.connection.execute(
            f"SELECT Score, COUNT(*) FROM {TABLE_NAME} GROUP BY Score ORDER BY Score"
        )
        return {row[0]: row[1] for row in cur.fetchall()}

    def get_yearly_counts(self) -> Dict[str, int]:
        """Returns {year: count} for temporal trend analysis."""
        cur = self.connection.execute(
            f"SELECT strftime('%Y', datetime(Time,'unixepoch')) as year, COUNT(*) "
            f"FROM {TABLE_NAME} GROUP BY year ORDER BY year"
        )
        return {row[0]: row[1] for row in cur.fetchall()}

    def get_top_products(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Products with the most reviews."""
        cur = self.connection.execute(
            f"SELECT ProductId, COUNT(*) as cnt FROM {TABLE_NAME} "
            f"GROUP BY ProductId ORDER BY cnt DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()

    def get_top_reviewers(self, limit: int = 10) -> List[Tuple[str, str, int]]:
        """Users with the most reviews (returns UserId, ProfileName, count)."""
        cur = self.connection.execute(
            f"SELECT UserId, ProfileName, COUNT(*) as cnt FROM {TABLE_NAME} "
            f"GROUP BY UserId ORDER BY cnt DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()

    def get_product_avg_score(self, product_id: str) -> Optional[float]:
        """Average score for a given product."""
        cur = self.connection.execute(
            f"SELECT AVG(Score) FROM {TABLE_NAME} WHERE ProductId = ?",
            (product_id,),
        )
        result = cur.fetchone()
        return result[0] if result and result[0] is not None else None

    def get_unique_counts(self) -> Dict[str, int]:
        """Unique product and user counts."""
        cur = self.connection.execute(
            f"SELECT COUNT(DISTINCT ProductId), COUNT(DISTINCT UserId) FROM {TABLE_NAME}"
        )
        row = cur.fetchone()
        return {"products": row[0], "users": row[1]}

    def get_helpfulness_stats(self) -> Dict[str, float]:
        """Average helpfulness numerator and denominator."""
        cur = self.connection.execute(
            f"SELECT AVG(HelpfulnessNumerator), AVG(HelpfulnessDenominator), "
            f"AVG(LENGTH(Text)), AVG(LENGTH(Summary)) FROM {TABLE_NAME}"
        )
        row = cur.fetchone()
        return {
            "avg_helpful_num": round(row[0], 2),
            "avg_helpful_den": round(row[1], 2),
            "avg_text_len": round(row[2], 1),
            "avg_summary_len": round(row[3], 1),
        }

    def get_random_sample(self, n: int = 100) -> List[Review]:
        """Fetch a random sample of reviews."""
        cur = self.connection.execute(
            f"SELECT * FROM {TABLE_NAME} ORDER BY RANDOM() LIMIT ?", (n,)
        )
        return [Review.from_row(row) for row in cur.fetchall()]
