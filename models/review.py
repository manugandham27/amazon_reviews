"""
Review dataclass — represents a single Amazon Fine Food review.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Review:
    """A single product review from the Amazon Fine Food Reviews dataset."""

    id: int
    product_id: str
    user_id: str
    profile_name: str
    helpfulness_numerator: int
    helpfulness_denominator: int
    score: int
    time: int  # unix timestamp
    summary: str
    text: str

    # ---- computed properties ------------------------------------------------

    @property
    def date(self) -> datetime:
        """Human-readable datetime of the review."""
        return datetime.utcfromtimestamp(self.time)

    @property
    def date_str(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @property
    def is_positive(self) -> bool:
        """Score >= 4 is considered positive."""
        from config import POSITIVE_THRESHOLD
        return self.score >= POSITIVE_THRESHOLD

    @property
    def helpfulness_ratio(self) -> Optional[float]:
        """Fraction of people who found the review helpful (None if no votes)."""
        if self.helpfulness_denominator == 0:
            return None
        return self.helpfulness_numerator / self.helpfulness_denominator

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    # ---- factories ----------------------------------------------------------

    @classmethod
    def from_row(cls, row: tuple) -> "Review":
        """Create a Review from a database row tuple."""
        return cls(
            id=row[0],
            product_id=row[1],
            user_id=row[2],
            profile_name=row[3],
            helpfulness_numerator=row[4],
            helpfulness_denominator=row[5],
            score=row[6],
            time=row[7],
            summary=row[8],
            text=row[9],
        )

    # ---- display ------------------------------------------------------------

    def short_str(self, max_text: int = 80) -> str:
        """One-line summary suitable for console display."""
        stars = "★" * self.score + "☆" * (5 - self.score)
        excerpt = (self.text[:max_text] + "…") if len(self.text) > max_text else self.text
        return f"[{self.date_str}] {stars}  {self.summary}  —  {excerpt}"

    def __str__(self) -> str:
        return self.short_str()
