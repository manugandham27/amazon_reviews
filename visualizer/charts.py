"""
ChartGenerator — matplotlib-based visualization for the reviews dataset.
"""
import os
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt

from config import OUTPUT_DIR, CHART_DPI, CHART_STYLE, COLOR_PALETTE


def _star_labels(scores):
    """Text labels for score axes that avoid unicode glyph issues."""
    return [f"{s}-Star" for s in scores]


class ChartGenerator:
    """Create and save publication-quality charts for review analytics."""

    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        try:
            plt.style.use(CHART_STYLE)
        except OSError:
            plt.style.use("ggplot")

    def _save(self, fig, filename: str):
        path = os.path.join(self.output_dir, filename)
        fig.savefig(path, dpi=CHART_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"  ✓ Saved  {path}")
        return path

    # ---- chart methods ------------------------------------------------------

    def plot_score_distribution(self, dist: Dict[int, int]) -> str:
        """Bar chart of 1-5 star rating counts."""
        fig, ax = plt.subplots(figsize=(8, 5))
        scores = sorted(dist.keys())
        counts = [dist[s] for s in scores]
        bars = ax.bar(
            _star_labels(scores),
            counts,
            color=COLOR_PALETTE,
            edgecolor="white",
            linewidth=1.2,
        )
        for bar, c in zip(bars, counts):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(counts) * 0.01,
                f"{c:,}",
                ha="center", va="bottom", fontsize=10, fontweight="bold",
            )
        ax.set_title("Score Distribution", fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel("Rating", fontsize=12)
        ax.set_ylabel("Number of Reviews", fontsize=12)
        ax.set_ylim(0, max(counts) * 1.12)
        fig.tight_layout()
        return self._save(fig, "score_distribution.png")

    def plot_yearly_trend(self, yearly: Dict[str, int]) -> str:
        """Line chart of reviews over time."""
        fig, ax = plt.subplots(figsize=(10, 5))
        years = sorted(yearly.keys())
        counts = [yearly[y] for y in years]
        ax.fill_between(years, counts, alpha=0.3, color="#3498db")
        ax.plot(years, counts, marker="o", color="#2980b9", linewidth=2.5, markersize=6)
        for i, (y, c) in enumerate(zip(years, counts)):
            if c > 10000 or i == 0 or i == len(years) - 1:
                ax.annotate(
                    f"{c:,}", (y, c),
                    textcoords="offset points", xytext=(0, 12),
                    ha="center", fontsize=8, fontweight="bold",
                )
        ax.set_title("Reviews per Year", fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Number of Reviews", fontsize=12)
        plt.xticks(rotation=45)
        fig.tight_layout()
        return self._save(fig, "yearly_trend.png")

    def plot_review_length_dist(self, length_data: Dict[int, Dict]) -> str:
        """Grouped bar chart showing average review length per score."""
        fig, ax = plt.subplots(figsize=(8, 5))
        scores = sorted(length_data.keys())
        avg_lens = [length_data[s]["avg_length"] for s in scores]
        ax.bar(
            _star_labels(scores),
            avg_lens,
            color=COLOR_PALETTE,
            edgecolor="white",
            linewidth=1.2,
        )
        for i, v in enumerate(avg_lens):
            ax.text(i, v + 5, f"{v:.0f}", ha="center", fontsize=10, fontweight="bold")
        ax.set_title("Average Review Length by Score", fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel("Rating", fontsize=12)
        ax.set_ylabel("Avg. Characters", fontsize=12)
        fig.tight_layout()
        return self._save(fig, "review_length_by_score.png")

    def plot_helpfulness_vs_score(self, helpfulness: Dict[int, Dict]) -> str:
        """Bar chart of helpfulness ratio per score bucket."""
        fig, ax = plt.subplots(figsize=(8, 5))
        scores = sorted(helpfulness.keys())
        ratios = [helpfulness[s]["avg_helpfulness_ratio"] for s in scores]
        ax.bar(
            _star_labels(scores),
            ratios,
            color=COLOR_PALETTE,
            edgecolor="white",
            linewidth=1.2,
        )
        for i, v in enumerate(ratios):
            ax.text(i, v + 0.005, f"{v:.1%}", ha="center", fontsize=10, fontweight="bold")
        ax.set_title("Avg Helpfulness Ratio by Score", fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel("Rating", fontsize=12)
        ax.set_ylabel("Helpfulness Ratio", fontsize=12)
        ax.set_ylim(0, max(ratios) * 1.15 if ratios else 1)
        fig.tight_layout()
        return self._save(fig, "helpfulness_by_score.png")

    def plot_sentiment_comparison(self, score_vs_sentiment: Dict[int, float]) -> str:
        """Compare average VADER compound score against star ratings."""
        fig, ax = plt.subplots(figsize=(8, 5))
        scores = sorted(score_vs_sentiment.keys())
        vader = [score_vs_sentiment[s] for s in scores]
        normalized = [(s - 3) / 2.0 for s in scores]

        x = range(len(scores))
        width = 0.35
        ax.bar(
            [i - width / 2 for i in x], normalized, width,
            label="Star Rating (normalized)", color="#3498db", alpha=0.8,
        )
        ax.bar(
            [i + width / 2 for i in x], vader, width,
            label="VADER Compound", color="#e74c3c", alpha=0.8,
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(_star_labels(scores))
        ax.set_title("Star Rating vs VADER Sentiment", fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel("Rating", fontsize=12)
        ax.set_ylabel("Sentiment Score (−1 to +1)", fontsize=12)
        ax.legend(fontsize=10)
        ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
        fig.tight_layout()
        return self._save(fig, "sentiment_comparison.png")

    def plot_quality_distribution(self, quality_by_score: Dict[int, float]) -> str:
        """Bar chart of average quality score per star rating."""
        fig, ax = plt.subplots(figsize=(8, 5))
        scores = sorted(quality_by_score.keys())
        qualities = [quality_by_score[s] for s in scores]
        bars = ax.bar(
            _star_labels(scores),
            qualities,
            color=COLOR_PALETTE,
            edgecolor="white",
            linewidth=1.2,
        )
        for bar, q in zip(bars, qualities):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{q:.1f}",
                ha="center", va="bottom", fontsize=10, fontweight="bold",
            )
        ax.set_title("Review Quality Score by Star Rating", fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel("Rating", fontsize=12)
        ax.set_ylabel("Quality Score (0–100)", fontsize=12)
        ax.set_ylim(0, 105)
        fig.tight_layout()
        return self._save(fig, "quality_by_score.png")
