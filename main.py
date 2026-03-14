#!/usr/bin/env python3
"""
Amazon Fine Food Reviews Analyzer — CLI Entry Point
====================================================

Usage:
    python main.py stats              Show summary statistics
    python main.py sentiment          Run sentiment analysis on a sample
    python main.py search  --query Q  Search reviews by keyword
    python main.py product --id PID   Analyze a specific product
    python main.py visualize          Generate all charts
    python main.py quality            Analyze review quality metrics
    python main.py compare --products PID1 PID2   Compare two products
    python main.py export  --output FILE          Export analysis to JSON
"""
import argparse
import json
import sys

from config import DEFAULT_SAMPLE_SIZE, DEFAULT_SEARCH_LIMIT
from models.database import ReviewDatabase
from analyzers.sentiment import SentimentAnalyzer
from analyzers.statistics import StatisticsAnalyzer
from analyzers.quality import ReviewQualityAnalyzer
from analyzers.comparator import ProductComparator
from visualizer.charts import ChartGenerator
from utils.helpers import (
    header, success, warn, error,
    format_number, print_table, stars_str,
)


# ═══════════════════════════════════════════════════════════════════════════
#  Subcommand handlers
# ═══════════════════════════════════════════════════════════════════════════

def cmd_stats(args):
    """Print comprehensive summary statistics."""
    with ReviewDatabase() as db:
        stats_analyzer = StatisticsAnalyzer(db)

        # ── Summary ──
        print(header("📊  Dataset Summary"))
        s = stats_analyzer.summary_stats()
        print(f"  Total Reviews       : {format_number(s['total_reviews'])}")
        print(f"  Unique Products     : {format_number(s['unique_products'])}")
        print(f"  Unique Users        : {format_number(s['unique_users'])}")
        print(f"  Average Score       : {s['avg_score']} / 5.0")
        print(f"  Avg Review Length   : {format_number(s['avg_text_length'])} chars")
        print(f"  Avg Summary Length  : {format_number(s['avg_summary_length'])} chars")
        print(f"  Avg Helpfulness ↑   : {s['avg_helpfulness_numerator']}")
        print(f"  Avg Helpfulness tot : {s['avg_helpfulness_denominator']}")

        # ── Score Distribution ──
        print(header("⭐  Score Distribution"))
        dist = s["score_distribution"]
        total = sum(dist.values())
        for score in sorted(dist):
            pct = dist[score] / total * 100
            bar = "█" * int(pct / 2)
            print(f"  {stars_str(score)}  {format_number(dist[score]).rjust(8)}  ({pct:5.1f}%)  {bar}")

        # ── Temporal Trends ──
        print(header("📈  Reviews per Year"))
        trends = stats_analyzer.temporal_trends()
        print_table(
            ["Year", "Reviews"],
            [[y, format_number(c)] for y, c in sorted(trends.items())],
        )

        # ── Top Products ──
        print(header("🏆  Top 10 Most Reviewed Products"))
        products = stats_analyzer.top_products(10)
        print_table(
            ["Product ID", "Reviews", "Avg Score"],
            [[p["product_id"], format_number(p["review_count"]),
              f"{p['avg_score']:.2f}" if p["avg_score"] else "N/A"]
             for p in products],
        )

        # ── Top Reviewers ──
        print(header("👤  Top 10 Most Active Reviewers"))
        reviewers = stats_analyzer.top_reviewers(10)
        print_table(
            ["User ID", "Profile Name", "Reviews"],
            [[r["user_id"], r["profile_name"], format_number(r["review_count"])]
             for r in reviewers],
        )

        # ── Helpfulness by Score ──
        print(header("👍  Helpfulness Analysis by Score"))
        help_data = stats_analyzer.helpfulness_analysis()
        print_table(
            ["Rating", "Avg Helpfulness Ratio", "Total Votes"],
            [[stars_str(s), f"{d['avg_helpfulness_ratio']:.1%}",
              format_number(d["total_votes"])]
             for s, d in sorted(help_data.items())],
        )

        # ── Review Length by Score ──
        print(header("📝  Review Length by Score"))
        len_data = stats_analyzer.review_length_analysis()
        print_table(
            ["Rating", "Avg Length", "Min", "Max"],
            [[stars_str(s), f"{d['avg_length']:.0f}",
              format_number(d["min_length"]), format_number(d["max_length"])]
             for s, d in sorted(len_data.items())],
        )

        print(f"\n{success('Statistics complete.')}\n")


def cmd_sentiment(args):
    """Run VADER sentiment analysis on a random sample."""
    sample_size = args.sample_size
    print(header(f"🧠  Sentiment Analysis (sample = {sample_size})"))

    with ReviewDatabase() as db:
        print("  Fetching random sample …")
        reviews = db.get_random_sample(sample_size)

    print("  Running VADER analysis …")
    analyzer = SentimentAnalyzer()
    report = analyzer.analyze_batch(reviews)

    print(f"\n  Analyzed            : {report.total} reviews")
    print(f"  Avg VADER compound  : {report.avg_compound:+.4f}")
    print(f"  Mismatches found    : {report.mismatches}  "
          f"({report.mismatches / report.total * 100:.1f}%)")

    # Score vs Sentiment table
    print(header("Star Rating → Avg VADER Compound"))
    print_table(
        ["Rating", "Normalized Stars", "VADER Compound", "Match?"],
        [
            [stars_str(s),
             f"{(s - 3) / 2.0:+.2f}",
             f"{v:+.4f}",
             success("yes") if abs(v - (s - 3) / 2.0) < 0.4 else warn("drift")]
            for s, v in sorted(report.score_vs_sentiment.items())
        ],
    )

    # Mismatch examples
    if report.mismatch_examples:
        print(header("⚠  Mismatch Examples (text sentiment ≠ star rating)"))
        for m in report.mismatch_examples[:5]:
            print(f"  ID {m.review_id}:  {stars_str(m.score)}  VADER={m.vader_compound:+.4f}  "
                  f"({m.vader_label} vs {m.star_label})")
            print(f"    \"{m.summary}\"")
            print()

    print(success("Sentiment analysis complete."))


def cmd_search(args):
    """Search reviews by keyword."""
    query = args.query
    limit = args.limit
    print(header(f"🔍  Search: \"{query}\"  (limit {limit})"))

    with ReviewDatabase() as db:
        results = db.search_text(query, limit)

    if not results:
        print(warn(f"  No reviews matched \"{query}\"."))
        return

    print(f"  Found {len(results)} result(s):\n")
    for r in results:
        print(f"  {stars_str(r.score)}  [{r.date_str}]  {r.summary}")
        excerpt = r.text[:120].replace("\n", " ")
        print(f"    {excerpt}…" if len(r.text) > 120 else f"    {r.text}")
        print(f"    Product: {r.product_id}   User: {r.profile_name}")
        if r.helpfulness_ratio is not None:
            print(f"    Helpful: {r.helpfulness_numerator}/{r.helpfulness_denominator} "
                  f"({r.helpfulness_ratio:.0%})")
        print()

    print(success(f"Search complete — {len(results)} results."))


def cmd_product(args):
    """Analyze a specific product."""
    pid = args.id
    print(header(f"📦  Product Analysis: {pid}"))

    with ReviewDatabase() as db:
        reviews = db.get_by_product(pid, limit=200)
        avg_score = db.get_product_avg_score(pid)

    if not reviews:
        print(error(f"  No reviews found for product \"{pid}\"."))
        return

    print(f"  Total reviews : {len(reviews)}")
    print(f"  Average score : {avg_score:.2f} / 5.0" if avg_score else "  Average score : N/A")

    # Score breakdown
    score_counts = {}
    for r in reviews:
        score_counts[r.score] = score_counts.get(r.score, 0) + 1

    print(header("Score Breakdown"))
    for s in sorted(score_counts):
        pct = score_counts[s] / len(reviews) * 100
        bar = "█" * int(pct / 2)
        print(f"  {stars_str(s)}  {str(score_counts[s]).rjust(4)}  ({pct:5.1f}%)  {bar}")

    # Latest reviews
    print(header("Latest Reviews"))
    for r in reviews[:5]:
        print(f"  {stars_str(r.score)}  [{r.date_str}]  {r.summary}")
        print(f"    {r.text[:150].replace(chr(10), ' ')}…" if len(r.text) > 150 else f"    {r.text}")
        print()

    # Sentiment on this product
    print(header("Sentiment Analysis"))
    analyzer = SentimentAnalyzer()
    report = analyzer.analyze_batch(reviews[:50])
    print(f"  Avg VADER compound : {report.avg_compound:+.4f}")
    print(f"  Mismatches         : {report.mismatches}/{report.total}")

    print(f"\n{success('Product analysis complete.')}\n")


def cmd_visualize(args):
    """Generate all charts and save to output/ directory."""
    print(header("📉  Generating Charts"))

    with ReviewDatabase() as db:
        stats = StatisticsAnalyzer(db)

        charts = ChartGenerator()

        # 1. Score distribution
        dist = db.get_score_distribution()
        charts.plot_score_distribution(dist)

        # 2. Yearly trend
        yearly = db.get_yearly_counts()
        charts.plot_yearly_trend(yearly)

        # 3. Review length by score
        len_data = stats.review_length_analysis()
        charts.plot_review_length_dist(len_data)

        # 4. Helpfulness by score
        help_data = stats.helpfulness_analysis()
        charts.plot_helpfulness_vs_score(help_data)

        # 5. Sentiment comparison (needs VADER on a sample)
        print("  Running VADER on 200 reviews for sentiment chart …")
        sample = db.get_random_sample(200)

    analyzer = SentimentAnalyzer()
    report = analyzer.analyze_batch(sample)
    charts.plot_sentiment_comparison(report.score_vs_sentiment)

    # 6. Quality by score (reuse the same sample)
    quality_analyzer = ReviewQualityAnalyzer()
    quality_report = quality_analyzer.analyze_batch(sample)
    charts.plot_quality_distribution(quality_report.quality_by_score)

    print(f"\n{success('All charts saved to output/ directory.')}\n")


def cmd_quality(args):
    """Analyze review quality using readability, informativeness, and helpfulness metrics."""
    sample_size = args.sample_size
    print(header(f"📐  Review Quality Analysis (sample = {sample_size})"))

    with ReviewDatabase() as db:
        print("  Fetching random sample …")
        reviews = db.get_random_sample(sample_size)

    print("  Computing quality metrics …")
    analyzer = ReviewQualityAnalyzer()
    report = analyzer.analyze_batch(reviews)

    print(f"\n  Analyzed              : {report.total} reviews")
    print(f"  Avg Quality Score     : {report.avg_quality:.1f} / 100")
    print(f"  Avg Readability (FRE) : {report.avg_readability:.1f}")
    print(f"  Avg Word Count        : {report.avg_word_count:.0f}")
    print(f"  Avg Unique Word Ratio : {report.avg_unique_ratio:.2%}")
    print()
    print(f"  🟢 High quality  : {report.high_quality_count}  ({report.high_quality_count / report.total * 100:.1f}%)")
    print(f"  🟡 Medium quality: {report.medium_quality_count}  ({report.medium_quality_count / report.total * 100:.1f}%)")
    print(f"  🔴 Low quality   : {report.low_quality_count}  ({report.low_quality_count / report.total * 100:.1f}%)")

    # Quality by star rating
    print(header("Quality Score by Star Rating"))
    print_table(
        ["Rating", "Avg Quality"],
        [[stars_str(s), f"{q:.1f}"] for s, q in sorted(report.quality_by_score.items())],
    )

    # High quality examples
    if report.examples_high:
        print(header("🏆  Highest Quality Reviews"))
        for rq in report.examples_high[:3]:
            print(f"  ID {rq.review_id}:  {stars_str(rq.score)}  Quality={rq.quality_score:.1f}  "
                  f"Readability={rq.flesch_score:.0f}  Words={rq.word_count}")

    # Low quality examples
    if report.examples_low:
        print(header("⚠  Lowest Quality Reviews"))
        for rq in report.examples_low[:3]:
            print(f"  ID {rq.review_id}:  {stars_str(rq.score)}  Quality={rq.quality_score:.1f}  "
                  f"Readability={rq.flesch_score:.0f}  Words={rq.word_count}")

    print(f"\n{success('Quality analysis complete.')}\n")


def cmd_compare(args):
    """Compare two products side-by-side."""
    pid_a, pid_b = args.products
    print(header(f"⚖  Product Comparison: {pid_a} vs {pid_b}"))

    with ReviewDatabase() as db:
        comparator = ProductComparator(db)
        report = comparator.compare(pid_a, pid_b)

    pa, pb = report.product_a, report.product_b

    if pa.total_reviews == 0 and pb.total_reviews == 0:
        print(error("  No reviews found for either product."))
        return

    # Side-by-side table
    print(header("📊  Head-to-Head Comparison"))
    print_table(
        ["Metric", pa.product_id, pb.product_id],
        [
            ["Total Reviews", format_number(pa.total_reviews), format_number(pb.total_reviews)],
            ["Avg Score", f"{pa.avg_score:.2f}" if pa.avg_score else "N/A",
             f"{pb.avg_score:.2f}" if pb.avg_score else "N/A"],
            ["VADER Compound", f"{pa.avg_vader_compound:+.4f}" if pa.avg_vader_compound is not None else "N/A",
             f"{pb.avg_vader_compound:+.4f}" if pb.avg_vader_compound is not None else "N/A"],
            ["Mismatch %", f"{pa.mismatch_pct:.1f}%" if pa.mismatch_pct is not None else "N/A",
             f"{pb.mismatch_pct:.1f}%" if pb.mismatch_pct is not None else "N/A"],
            ["Avg Word Count", f"{pa.avg_word_count:.0f}", f"{pb.avg_word_count:.0f}"],
            ["Avg Helpfulness", f"{pa.avg_helpfulness:.1%}" if pa.avg_helpfulness is not None else "N/A",
             f"{pb.avg_helpfulness:.1%}" if pb.avg_helpfulness is not None else "N/A"],
            ["First Review", pa.earliest_review or "N/A", pb.earliest_review or "N/A"],
            ["Last Review", pa.latest_review or "N/A", pb.latest_review or "N/A"],
        ],
    )

    # Score distributions
    for profile in (pa, pb):
        if profile.score_distribution:
            print(header(f"Score Breakdown — {profile.product_id}"))
            total = sum(profile.score_distribution.values())
            for s in sorted(profile.score_distribution):
                cnt = profile.score_distribution[s]
                pct = cnt / total * 100
                bar = "█" * int(pct / 2)
                print(f"  {stars_str(s)}  {str(cnt).rjust(4)}  ({pct:5.1f}%)  {bar}")

    # Winners
    print(header("🏅  Winners"))
    print(f"  By Avg Score     : {report.winner_by_score}")
    print(f"  By Review Volume : {report.winner_by_volume}")
    if report.winner_by_sentiment:
        print(f"  By Sentiment     : {report.winner_by_sentiment}")

    print(f"\n{success('Product comparison complete.')}\n")


def cmd_export(args):
    """Export analysis results to a JSON file."""
    output_path = args.output
    print(header(f"💾  Exporting Analysis to {output_path}"))

    with ReviewDatabase() as db:
        stats_analyzer = StatisticsAnalyzer(db)

        print("  Gathering summary statistics …")
        summary = stats_analyzer.summary_stats()

        print("  Gathering temporal trends …")
        trends = stats_analyzer.temporal_trends()

        print("  Gathering top products …")
        top_prods = stats_analyzer.top_products(10)

        print("  Gathering top reviewers …")
        top_revs = stats_analyzer.top_reviewers(10)

        print("  Gathering helpfulness data …")
        helpfulness = stats_analyzer.helpfulness_analysis()

        print("  Gathering review length data …")
        length_data = stats_analyzer.review_length_analysis()

        print("  Running sentiment analysis on sample …")
        sample = db.get_random_sample(100)

    analyzer = SentimentAnalyzer()
    sentiment_report = analyzer.analyze_batch(sample)

    quality_analyzer = ReviewQualityAnalyzer()
    quality_report = quality_analyzer.analyze_batch(sample)

    # Build export structure
    export_data = {
        "summary": {
            "total_reviews": summary["total_reviews"],
            "unique_products": summary["unique_products"],
            "unique_users": summary["unique_users"],
            "avg_score": summary["avg_score"],
            "avg_text_length": summary["avg_text_length"],
            "avg_summary_length": summary["avg_summary_length"],
        },
        "score_distribution": {str(k): v for k, v in summary["score_distribution"].items()},
        "temporal_trends": trends,
        "top_products": top_prods,
        "top_reviewers": top_revs,
        "helpfulness_by_score": {
            str(k): v for k, v in helpfulness.items()
        },
        "review_length_by_score": {
            str(k): v for k, v in length_data.items()
        },
        "sentiment_analysis": {
            "sample_size": sentiment_report.total,
            "avg_compound": sentiment_report.avg_compound,
            "mismatches": sentiment_report.mismatches,
            "mismatch_pct": round(
                sentiment_report.mismatches / sentiment_report.total * 100, 1
            ) if sentiment_report.total else 0,
            "score_vs_sentiment": {
                str(k): v for k, v in sentiment_report.score_vs_sentiment.items()
            },
        },
        "quality_analysis": {
            "sample_size": quality_report.total,
            "avg_quality": quality_report.avg_quality,
            "avg_readability": quality_report.avg_readability,
            "high_quality_pct": round(
                quality_report.high_quality_count / quality_report.total * 100, 1
            ) if quality_report.total else 0,
            "medium_quality_pct": round(
                quality_report.medium_quality_count / quality_report.total * 100, 1
            ) if quality_report.total else 0,
            "low_quality_pct": round(
                quality_report.low_quality_count / quality_report.total * 100, 1
            ) if quality_report.total else 0,
            "quality_by_score": {
                str(k): v for k, v in quality_report.quality_by_score.items()
            },
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"\n{success(f'Exported to {output_path}')}\n")


# ═══════════════════════════════════════════════════════════════════════════
#  CLI entry point
# ═══════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="review-analyzer",
        description="Amazon Fine Food Reviews Analysis Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # stats
    sub.add_parser("stats", help="Show comprehensive summary statistics")

    # sentiment
    p_sent = sub.add_parser("sentiment", help="Run sentiment analysis on a sample")
    p_sent.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE,
                        help=f"Number of reviews to sample (default: {DEFAULT_SAMPLE_SIZE})")

    # search
    p_search = sub.add_parser("search", help="Search reviews by keyword")
    p_search.add_argument("--query", "-q", required=True, help="Search keyword")
    p_search.add_argument("--limit", "-l", type=int, default=DEFAULT_SEARCH_LIMIT,
                          help=f"Max results (default: {DEFAULT_SEARCH_LIMIT})")

    # product
    p_prod = sub.add_parser("product", help="Analyze a specific product")
    p_prod.add_argument("--id", required=True, help="Product ID (e.g. B007JFMH8M)")

    # visualize
    sub.add_parser("visualize", help="Generate all charts (saved to output/)")

    # quality
    p_qual = sub.add_parser("quality", help="Analyze review quality metrics")
    p_qual.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE,
                        help=f"Number of reviews to sample (default: {DEFAULT_SAMPLE_SIZE})")

    # compare
    p_cmp = sub.add_parser("compare", help="Compare two products side-by-side")
    p_cmp.add_argument("--products", nargs=2, required=True, metavar="PID",
                       help="Two product IDs to compare (e.g. B007JFMH8M B000LKTHJK)")

    # export
    p_exp = sub.add_parser("export", help="Export analysis results to JSON")
    p_exp.add_argument("--output", "-o", default="analysis_export.json",
                       help="Output file path (default: analysis_export.json)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "stats": cmd_stats,
        "sentiment": cmd_sentiment,
        "search": cmd_search,
        "product": cmd_product,
        "visualize": cmd_visualize,
        "quality": cmd_quality,
        "compare": cmd_compare,
        "export": cmd_export,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print(f"\n{warn('Interrupted.')}")
        sys.exit(1)
    except Exception as e:
        print(error(f"Error: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
