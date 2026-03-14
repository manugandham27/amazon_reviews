"""
ReviewQualityAnalyzer — multi-metric review quality scoring.

Computes a composite quality score for each review based on:
  - Readability (Flesch Reading Ease)
  - Informativeness (word count, unique word ratio)
  - Helpfulness (community votes)
  - Specificity (presence of concrete details)
"""
import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from models.review import Review
from config import (
    QUALITY_LENGTH_IDEAL_MIN,
    QUALITY_LENGTH_IDEAL_MAX,
    QUALITY_WEIGHT_READABILITY,
    QUALITY_WEIGHT_INFORMATIVENESS,
    QUALITY_WEIGHT_HELPFULNESS,
    QUALITY_WEIGHT_SPECIFICITY,
)


# ── Readability helpers ──────────────────────────────────────────────────────

def _count_syllables(word: str) -> int:
    """Estimate syllable count using vowel-group heuristic."""
    word = word.lower().strip()
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # silent 'e' at end
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def flesch_reading_ease(text: str) -> float:
    """
    Compute the Flesch Reading Ease score.

    Score ranges:  90-100 very easy, 60-70 standard, 0-30 very difficult.
    Formula:  206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r"[a-zA-Z]+", text)

    if not words or not sentences:
        return 50.0  # neutral default

    total_syllables = sum(_count_syllables(w) for w in words)
    asl = len(words) / len(sentences)       # avg sentence length
    asw = total_syllables / len(words)       # avg syllables per word

    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return max(0.0, min(100.0, score))


# ── Quality dataclasses ──────────────────────────────────────────────────────

@dataclass
class ReviewQuality:
    """Quality metrics for a single review."""
    review_id: int
    score: int
    word_count: int
    unique_word_ratio: float
    flesch_score: float
    helpfulness_ratio: Optional[float]
    has_specific_details: bool
    quality_score: float           # composite 0-100
    quality_label: str             # "high", "medium", "low"


@dataclass
class QualityReport:
    """Aggregate quality report over a batch of reviews."""
    total: int = 0
    avg_quality: float = 0.0
    avg_readability: float = 0.0
    avg_word_count: float = 0.0
    avg_unique_ratio: float = 0.0
    high_quality_count: int = 0
    medium_quality_count: int = 0
    low_quality_count: int = 0
    quality_by_score: Dict[int, float] = field(default_factory=dict)
    examples_high: List[ReviewQuality] = field(default_factory=list)
    examples_low: List[ReviewQuality] = field(default_factory=list)


# ── Analyzer ─────────────────────────────────────────────────────────────────

class ReviewQualityAnalyzer:
    """Score review quality using multiple linguistic and structural metrics."""

    _DETAIL_PATTERNS = re.compile(
        r"\b(\d+\s*(oz|mg|lb|kg|pack|count|inch|cm|ml|cup|tbsp|tsp|cal|kcal))"
        r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        r"|\$\d+",
        re.IGNORECASE,
    )

    def analyze_review(self, review: Review) -> ReviewQuality:
        """Compute quality metrics for a single review."""
        text = review.text
        words = re.findall(r"[a-zA-Z]+", text.lower())
        word_count = len(words)
        unique_ratio = len(set(words)) / max(word_count, 1)

        # 1. Readability (0-100)
        readability = flesch_reading_ease(text)

        # 2. Informativeness (0-100)
        #    Reward reviews in the ideal length range; penalize extremes.
        if QUALITY_LENGTH_IDEAL_MIN <= word_count <= QUALITY_LENGTH_IDEAL_MAX:
            length_score = 100.0
        elif word_count < QUALITY_LENGTH_IDEAL_MIN:
            length_score = (word_count / QUALITY_LENGTH_IDEAL_MIN) * 100
        else:
            # diminishing returns beyond ideal max, but not penalized hard
            length_score = max(60.0, 100 - (word_count - QUALITY_LENGTH_IDEAL_MAX) * 0.05)
        informativeness = (length_score * 0.5) + (unique_ratio * 100 * 0.5)

        # 3. Helpfulness (0-100)
        hr = review.helpfulness_ratio
        helpfulness_score = (hr * 100) if hr is not None else 50.0

        # 4. Specificity (0-100)
        has_details = bool(self._DETAIL_PATTERNS.search(text))
        specificity = 80.0 if has_details else 40.0

        # Composite quality score (weighted)
        composite = (
            readability * QUALITY_WEIGHT_READABILITY
            + informativeness * QUALITY_WEIGHT_INFORMATIVENESS
            + helpfulness_score * QUALITY_WEIGHT_HELPFULNESS
            + specificity * QUALITY_WEIGHT_SPECIFICITY
        )
        composite = max(0.0, min(100.0, composite))

        if composite >= 70:
            label = "high"
        elif composite >= 40:
            label = "medium"
        else:
            label = "low"

        return ReviewQuality(
            review_id=review.id,
            score=review.score,
            word_count=word_count,
            unique_word_ratio=round(unique_ratio, 4),
            flesch_score=round(readability, 1),
            helpfulness_ratio=hr,
            has_specific_details=has_details,
            quality_score=round(composite, 1),
            quality_label=label,
        )

    def analyze_batch(self, reviews: List[Review]) -> QualityReport:
        """Analyze a list of reviews and produce an aggregate quality report."""
        results = [self.analyze_review(r) for r in reviews]
        if not results:
            return QualityReport()

        high = [r for r in results if r.quality_label == "high"]
        med = [r for r in results if r.quality_label == "medium"]
        low = [r for r in results if r.quality_label == "low"]

        # Per-star-rating average quality
        score_sums: Dict[int, List[float]] = {}
        for r in results:
            score_sums.setdefault(r.score, []).append(r.quality_score)
        quality_by_score = {
            s: round(sum(vals) / len(vals), 1)
            for s, vals in sorted(score_sums.items())
        }

        return QualityReport(
            total=len(results),
            avg_quality=round(sum(r.quality_score for r in results) / len(results), 1),
            avg_readability=round(sum(r.flesch_score for r in results) / len(results), 1),
            avg_word_count=round(sum(r.word_count for r in results) / len(results), 1),
            avg_unique_ratio=round(sum(r.unique_word_ratio for r in results) / len(results), 4),
            high_quality_count=len(high),
            medium_quality_count=len(med),
            low_quality_count=len(low),
            quality_by_score=quality_by_score,
            examples_high=sorted(high, key=lambda r: r.quality_score, reverse=True)[:5],
            examples_low=sorted(low, key=lambda r: r.quality_score)[:5],
        )
