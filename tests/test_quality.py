"""
Tests for the Review Quality Analyzer and related new features.
"""
import unittest
from unittest.mock import MagicMock, patch

from models.review import Review
from analyzers.quality import (
    ReviewQualityAnalyzer,
    flesch_reading_ease,
    _count_syllables,
    ReviewQuality,
    QualityReport,
)
from analyzers.comparator import ProductComparator, ProductProfile, ComparisonReport
from utils.helpers import stars_str, format_number, clean_text, truncate


def _make_review(
    review_id=1,
    score=5,
    text="This is a great product. I really loved it.",
    summary="Great product",
    helpfulness_num=5,
    helpfulness_den=10,
    time_val=1349913600,
    product_id="B001",
    user_id="U001",
    profile_name="TestUser",
):
    """Helper to create a Review object for testing."""
    return Review(
        id=review_id,
        product_id=product_id,
        user_id=user_id,
        profile_name=profile_name,
        helpfulness_numerator=helpfulness_num,
        helpfulness_denominator=helpfulness_den,
        score=score,
        time=time_val,
        summary=summary,
        text=text,
    )


class TestCountSyllables(unittest.TestCase):
    def test_single_syllable(self):
        self.assertEqual(_count_syllables("cat"), 1)

    def test_multi_syllable(self):
        self.assertGreaterEqual(_count_syllables("beautiful"), 2)

    def test_empty_string(self):
        self.assertEqual(_count_syllables(""), 0)

    def test_silent_e(self):
        result = _count_syllables("like")
        self.assertEqual(result, 1)


class TestFleschReadingEase(unittest.TestCase):
    def test_simple_text(self):
        score = flesch_reading_ease("The cat sat on the mat. It was a good cat.")
        self.assertGreater(score, 50)

    def test_empty_text(self):
        score = flesch_reading_ease("")
        self.assertEqual(score, 50.0)

    def test_score_range(self):
        score = flesch_reading_ease(
            "This product is excellent. I would recommend it to everyone. "
            "The quality is superb. Great value for the price."
        )
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


class TestReviewQualityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ReviewQualityAnalyzer()

    def test_analyze_single_review(self):
        review = _make_review(
            text=(
                "This coffee is absolutely amazing. The flavor is rich and full-bodied. "
                "I have been drinking it every morning for the past 3 months and I am "
                "still impressed. It comes in a 12 oz bag which lasts me about 2 weeks. "
                "Highly recommended for anyone who loves a good cup of coffee."
            ),
        )
        result = self.analyzer.analyze_review(review)
        self.assertIsInstance(result, ReviewQuality)
        self.assertGreater(result.quality_score, 0)
        self.assertLessEqual(result.quality_score, 100)
        self.assertIn(result.quality_label, ("high", "medium", "low"))
        self.assertTrue(result.has_specific_details)  # has "12 oz"

    def test_analyze_short_review(self):
        review = _make_review(text="Bad.", helpfulness_num=0, helpfulness_den=0)
        result = self.analyzer.analyze_review(review)
        self.assertLess(result.word_count, 5)
        # Short reviews should have lower quality
        self.assertLess(result.quality_score, 70)

    def test_analyze_batch(self):
        reviews = [
            _make_review(review_id=1, text="Great product. Loved it. Five stars."),
            _make_review(review_id=2, text="Terrible. Would not buy again.", score=1),
            _make_review(
                review_id=3,
                text=(
                    "This 16 oz coffee is amazing. Rich flavor. "
                    "Great aroma. Best I have ever had in my life."
                ),
            ),
        ]
        report = self.analyzer.analyze_batch(reviews)
        self.assertIsInstance(report, QualityReport)
        self.assertEqual(report.total, 3)
        self.assertGreater(report.avg_quality, 0)

    def test_analyze_empty_batch(self):
        report = self.analyzer.analyze_batch([])
        self.assertEqual(report.total, 0)
        self.assertEqual(report.avg_quality, 0.0)

    def test_quality_label_thresholds(self):
        # High quality: detailed, readable, helpful review
        high_review = _make_review(
            text=(
                "I have been buying this product for years. The 24 oz container "
                "is perfect for my family. The taste is consistently excellent. "
                "My children love it. It dissolves easily in both hot and cold water. "
                "The price is very reasonable compared to similar products."
            ),
            helpfulness_num=9,
            helpfulness_den=10,
        )
        result = self.analyzer.analyze_review(high_review)
        self.assertEqual(result.quality_label, "high")


class TestProductComparator(unittest.TestCase):
    def test_build_profile_empty(self):
        db = MagicMock()
        comparator = ProductComparator(db)
        profile = comparator._build_profile("B_EMPTY", [])
        self.assertEqual(profile.total_reviews, 0)
        self.assertIsNone(profile.avg_score)

    @patch("analyzers.comparator.SentimentAnalyzer")
    def test_compare_returns_report(self, mock_sentiment_cls):
        from analyzers.sentiment import BatchSentimentReport
        mock_analyzer = mock_sentiment_cls.return_value
        mock_analyzer.analyze_batch.return_value = BatchSentimentReport(
            total=1, mismatches=0, avg_compound=0.5,
            score_vs_sentiment={5: 0.8}, mismatch_examples=[],
        )

        db = MagicMock()
        db.get_by_product.side_effect = [
            [_make_review(review_id=1, product_id="A", score=5)],
            [_make_review(review_id=2, product_id="B", score=3)],
        ]
        db.get_product_avg_score.side_effect = [5.0, 3.0]

        comparator = ProductComparator(db)
        report = comparator.compare("A", "B")
        self.assertIsInstance(report, ComparisonReport)
        self.assertEqual(report.product_a.product_id, "A")
        self.assertEqual(report.product_b.product_id, "B")
        self.assertEqual(report.winner_by_score, "A")


class TestHelpers(unittest.TestCase):
    def test_stars_str(self):
        self.assertEqual(stars_str(1), "★☆☆☆☆")
        self.assertEqual(stars_str(5), "★★★★★")
        self.assertEqual(stars_str(3), "★★★☆☆")

    def test_format_number_int(self):
        self.assertEqual(format_number(1000), "1,000")

    def test_format_number_float(self):
        self.assertEqual(format_number(3.14159), "3.14")

    def test_clean_text(self):
        self.assertEqual(clean_text("<b>Hello</b>"), "Hello")
        self.assertEqual(clean_text("a  b   c"), "a b c")

    def test_truncate(self):
        self.assertEqual(truncate("hello", 10), "hello")
        self.assertEqual(truncate("hello world extended", 10), "hello wor…")


class TestReviewModel(unittest.TestCase):
    def test_from_row(self):
        row = (1, "B001", "U001", "User1", 5, 10, 4, 1349913600, "Good", "Nice product")
        review = Review.from_row(row)
        self.assertEqual(review.id, 1)
        self.assertEqual(review.score, 4)
        self.assertEqual(review.product_id, "B001")

    def test_helpfulness_ratio(self):
        review = _make_review(helpfulness_num=7, helpfulness_den=10)
        self.assertAlmostEqual(review.helpfulness_ratio, 0.7)

    def test_helpfulness_ratio_zero_denom(self):
        review = _make_review(helpfulness_num=0, helpfulness_den=0)
        self.assertIsNone(review.helpfulness_ratio)

    def test_word_count(self):
        review = _make_review(text="one two three four five")
        self.assertEqual(review.word_count, 5)

    def test_is_positive(self):
        self.assertTrue(_make_review(score=5).is_positive)
        self.assertTrue(_make_review(score=4).is_positive)
        self.assertFalse(_make_review(score=3).is_positive)
        self.assertFalse(_make_review(score=1).is_positive)

    def test_date_str(self):
        review = _make_review(time_val=1349913600)
        self.assertRegex(review.date_str, r"\d{4}-\d{2}-\d{2}")


if __name__ == "__main__":
    unittest.main()
