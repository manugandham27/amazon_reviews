# 🛒 Amazon Fine Food Reviews Analyzer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![NLTK](https://img.shields.io/badge/NLP-VADER-orange)](https://www.nltk.org/)
[![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-blue)](https://matplotlib.org/)
[![Tests](https://img.shields.io/badge/Tests-25%20passing-brightgreen)](#-testing)

> A modular Python CLI toolkit for analyzing **568,454 Amazon Fine Food Reviews** with VADER sentiment analysis, multi-metric review quality scoring, product comparison, statistical insights, data export, and publication-quality chart visualizations.

---

## ✨ Features

| Command | Description |
|---------|-------------|
| `stats` | Comprehensive summary — score distribution, temporal trends, top products/reviewers, helpfulness analysis, review length stats |
| `sentiment` | VADER-based NLP sentiment scoring on random samples with star-rating mismatch detection |
| `search` | Full-text keyword search across review summaries and body text |
| `product` | Deep-dive into any product by ID — score breakdown, latest reviews, sentiment |
| `visualize` | Generate 6 publication-quality charts saved as PNGs |
| `quality` | **🆕** Multi-metric review quality scoring — Flesch readability, informativeness, helpfulness, and specificity |
| `compare` | **🆕** Side-by-side comparison of two products across score, sentiment, helpfulness, and volume |
| `export` | **🆕** Export full analysis results (stats, sentiment, quality) to a structured JSON file |

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [Summary Statistics](#summary-statistics)
  - [Sentiment Analysis](#sentiment-analysis)
  - [Search Reviews](#search-reviews)
  - [Product Analysis](#product-analysis)
  - [Generate Charts](#generate-charts)
  - [Review Quality Analysis](#review-quality-analysis-)
  - [Product Comparison](#product-comparison-)
  - [Export to JSON](#export-to-json-)
- [What's Novel](#-whats-novel)
- [Project Architecture](#-project-architecture)
- [Dataset Overview](#-dataset-overview)
- [Database Schema](#-database-schema)
- [Analysis Methodology](#-analysis-methodology)
- [Sample Output](#-sample-output)
- [Charts Generated](#-charts-generated)
- [Configuration](#%EF%B8%8F-configuration)
- [Testing](#-testing)
- [Dependencies](#-dependencies)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/manugandham27/amazon_reviews.git
cd amazon_reviews
```

### 2. Set Up Virtual Environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data (first run only)

```bash
python -c "import nltk; nltk.download('vader_lexicon')"
```

### 5. Get the Dataset

Download the **Amazon Fine Food Reviews** dataset from [Kaggle](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) and place `database.sqlite` in the project root.

### 6. Run

```bash
python main.py stats
```

---

## 💻 Usage

### Summary Statistics

```bash
python main.py stats
```

Prints a comprehensive overview: total reviews, unique products/users, score distribution with bar charts, yearly trends, top 10 products, top 10 reviewers, helpfulness analysis per score, and review length analysis.

### Sentiment Analysis

```bash
python main.py sentiment                    # default: 100 samples
python main.py sentiment --sample-size 500  # larger sample
```

Runs VADER (Valence Aware Dictionary and sEntiment Reasoner) on a random sample of reviews and compares the NLP polarity score against the star rating. Reports:
- Average VADER compound score
- Per-star VADER averages vs normalized star ratings
- Mismatch count and percentage
- Example mismatches (e.g., positive text with 1-star rating)

### Search Reviews

```bash
python main.py search --query "chocolate"              # default 20 results
python main.py search --query "dog food" --limit 50    # custom limit
python main.py search -q "organic coffee" -l 10        # short flags
```

Full-text search across both the `Summary` and `Text` columns. Each result shows the star rating, date, summary, excerpt, product ID, user profile, and helpfulness votes.

### Product Analysis

```bash
python main.py product --id B007JFMH8M
```

Deep-dive into a specific product:
- Total reviews and average score
- Score breakdown with percentage bars
- 5 most recent reviews with excerpts
- VADER sentiment analysis on the product's reviews

### Generate Charts

```bash
python main.py visualize
```

Generates 6 charts saved to the `output/` directory (see [Charts Generated](#-charts-generated) below).

### Review Quality Analysis 🆕

```bash
python main.py quality                      # default: 100 samples
python main.py quality --sample-size 500    # larger sample
```

Runs a **multi-metric quality analysis** on a random sample of reviews. Each review is scored on four dimensions:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| **Readability** | 25% | Flesch Reading Ease score — how accessible the text is |
| **Informativeness** | 30% | Word count (ideal range) + vocabulary diversity (unique word ratio) |
| **Helpfulness** | 25% | Community helpfulness vote ratio |
| **Specificity** | 20% | Presence of concrete details (quantities, measurements, prices) |

Reviews are classified as **High** (≥ 70), **Medium** (40–69), or **Low** (< 40) quality. The report shows:
- Aggregate quality statistics
- Quality distribution across star ratings
- Examples of highest- and lowest-quality reviews

### Product Comparison 🆕

```bash
python main.py compare --products B007JFMH8M B000LKTHJK
```

Generates a **head-to-head comparison** of two products across multiple dimensions:

- Total reviews and average score
- VADER sentiment compound score
- Sentiment–rating mismatch percentage
- Average review word count and helpfulness ratio
- Review timeline (earliest → latest)
- Score breakdown for each product
- Overall winners (by score, volume, and sentiment)

### Export to JSON 🆕

```bash
python main.py export                                # default: analysis_export.json
python main.py export --output my_analysis.json      # custom file path
```

Exports a complete analysis snapshot to a structured JSON file containing:
- Summary statistics (total reviews, unique products/users, average score)
- Score distribution
- Temporal trends (reviews per year)
- Top 10 products and reviewers
- Helpfulness and review length data by score
- Sentiment analysis results (VADER compound, mismatches, per-star averages)
- Quality analysis results (readability, quality distribution, per-star quality scores)

---

## 🔬 What's Novel

This project goes beyond typical review analysis tools with several unique capabilities:

### 1. Composite Review Quality Scoring

Unlike tools that only measure sentiment or word count, this analyzer combines **four orthogonal quality dimensions** into a single composite score:

```
Quality = 0.25 × Readability + 0.30 × Informativeness + 0.25 × Helpfulness + 0.20 × Specificity
```

- **Readability** uses the Flesch Reading Ease formula (`206.835 − 1.015 × ASL − 84.6 × ASW`), a well-established psycholinguistic metric
- **Informativeness** rewards reviews in an ideal word-count range (30–300 words) and penalizes both extremely short and extremely long reviews, combined with vocabulary diversity
- **Specificity** detects concrete details like measurements (`12 oz`, `$4.99`, `3 tbsp`) using pattern matching — a proxy for actionable product information

### 2. Sentiment–Rating Mismatch Detection

The system detects reviews where the **text sentiment disagrees with the star rating** by comparing VADER compound scores against normalized star values. This catches:
- **Sarcasm**: positive text with low star ratings
- **Rating errors**: negative text with high star ratings
- **Complex opinions**: mixed-sentiment reviews that defy simple scoring

The configurable mismatch threshold (`SENTIMENT_MISMATCH_DELTA = 0.4`) allows tuning sensitivity for different use cases.

### 3. Multi-Dimensional Product Comparison

The `compare` command enables structured comparison of two products across **8 dimensions simultaneously**, providing a holistic view that goes beyond simple average-score comparison. It combines quantitative metrics (scores, volumes) with qualitative NLP insights (sentiment, mismatches).

### 4. Structured Data Export

The JSON export creates a complete, machine-readable analysis snapshot that can be consumed by:
- Downstream data pipelines
- Dashboard tools (Grafana, Metabase)
- Jupyter notebooks for further analysis
- Automated reporting systems

### 5. Modular, Extensible Architecture

The clean separation of concerns (models → analyzers → visualizer → CLI) makes it straightforward to add new analysis modules without modifying existing code. Each analyzer operates independently and can be used as a library.

---

## 🏗 Project Architecture

```
amazon_reviews/
│
├── main.py                        # CLI entry point — argparse with 8 subcommands
├── config.py                      # Centralized paths, thresholds, weights, constants
├── requirements.txt               # Python dependencies
│
├── models/                        # Data layer
│   ├── __init__.py
│   ├── review.py                  # Review dataclass with computed properties
│   └── database.py                # ReviewDatabase — SQLite query interface
│
├── analyzers/                     # Analysis layer
│   ├── __init__.py
│   ├── sentiment.py               # SentimentAnalyzer — VADER + mismatch detection
│   ├── statistics.py              # StatisticsAnalyzer — descriptive analytics
│   ├── quality.py                 # ReviewQualityAnalyzer — composite quality scoring
│   └── comparator.py              # ProductComparator — side-by-side comparison
│
├── visualizer/                    # Presentation layer
│   ├── __init__.py
│   └── charts.py                  # ChartGenerator — matplotlib chart factory (6 types)
│
├── utils/                         # Shared utilities
│   ├── __init__.py
│   └── helpers.py                 # Text cleaning, console formatting, table printer
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_quality.py            # Unit tests for quality, comparator, helpers, models
│
└── output/                        # Generated charts (auto-created)
    ├── score_distribution.png
    ├── yearly_trend.png
    ├── review_length_by_score.png
    ├── helpfulness_by_score.png
    ├── sentiment_comparison.png
    └── quality_by_score.png
```

### Key Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `Review` | `models/review.py` | Dataclass for a single review with computed properties (`is_positive`, `helpfulness_ratio`, `word_count`, `date`) |
| `ReviewDatabase` | `models/database.py` | SQLite wrapper with context manager — queries, aggregations, random sampling |
| `SentimentAnalyzer` | `analyzers/sentiment.py` | VADER sentiment scoring, batch analysis, star-rating mismatch reports |
| `StatisticsAnalyzer` | `analyzers/statistics.py` | Descriptive stats — summaries, temporal trends, helpfulness/length analysis |
| `ReviewQualityAnalyzer` | `analyzers/quality.py` | **🆕** Composite quality scoring with readability, informativeness, helpfulness, specificity |
| `ProductComparator` | `analyzers/comparator.py` | **🆕** Multi-dimensional product comparison across 8 metrics |
| `ChartGenerator` | `visualizer/charts.py` | Matplotlib chart factory — 6 chart types saved as PNGs |

### Data Flow

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────────┐     ┌───────────────┐
│  SQLite DB   │────▶│  ReviewDatabase  │────▶│  Analyzers           │────▶│  CLI Output   │
│ (568K rows)  │     │  (query layer)   │     │  • SentimentAnalyzer │     │  • Console    │
│              │     │                  │     │  • StatisticsAnalyzer│     │  • Charts     │
│              │     │                  │     │  • QualityAnalyzer   │     │  • JSON       │
│              │     │                  │     │  • ProductComparator │     │               │
└──────────────┘     └─────────────────┘     └──────────────────────┘     └───────────────┘
```

---

## 📊 Dataset Overview

The [Amazon Fine Food Reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) dataset contains reviews from Amazon spanning **13 years**:

| Metric | Value |
|--------|-------|
| Total Reviews | **568,454** |
| Unique Products | **74,258** |
| Unique Users | **256,059** |
| Time Span | Oct 1999 → Oct 2012 |
| Average Score | **4.18 / 5.0** |
| Avg Review Length | ~436 characters |

### Score Distribution

| Score | Count | Percentage |
|-------|-------|------------|
| ⭐ 1 | 52,268 | 9.2% |
| ⭐ 2 | 29,769 | 5.2% |
| ⭐ 3 | 42,640 | 7.5% |
| ⭐ 4 | 80,655 | 14.2% |
| ⭐ 5 | 363,122 | **63.9%** |

> ⚠️ **Note:** The dataset is heavily skewed toward positive reviews (64% are 5-star). Any ML modeling should account for this class imbalance.

---

## 🗄 Database Schema

```sql
CREATE TABLE Reviews (
    Id                      INTEGER PRIMARY KEY,
    ProductId               TEXT,        -- Amazon product ASIN
    UserId                  TEXT,        -- Unique reviewer ID
    ProfileName             TEXT,        -- Reviewer display name
    HelpfulnessNumerator    INTEGER,     -- Helpful votes received
    HelpfulnessDenominator  INTEGER,     -- Total votes received
    Score                   INTEGER,     -- Star rating (1-5)
    Time                    INTEGER,     -- Unix timestamp
    Summary                 TEXT,        -- Review title
    Text                    TEXT         -- Full review body
);
```

---

## 🔎 Analysis Methodology

### Sentiment Analysis — VADER

[VADER](https://github.com/cjhutto/vaderSentiment) (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool specifically tuned for social media and user-generated content. It handles:
- Punctuation emphasis (`"Great!!!"` is more positive than `"Great"`)
- Capitalization (`"GREAT"` is stronger than `"great"`)
- Degree modifiers (`"extremely good"` vs `"slightly good"`)
- Negation (`"not good"` correctly flips sentiment)

**Star-to-VADER Normalization:**

```
normalized_score = (star_rating - 3) / 2.0
```

| Star Rating | Normalized Score |
|-------------|-----------------|
| ★☆☆☆☆ (1) | -1.00 |
| ★★☆☆☆ (2) | -0.50 |
| ★★★☆☆ (3) | +0.00 |
| ★★★★☆ (4) | +0.50 |
| ★★★★★ (5) | +1.00 |

A **mismatch** is flagged when `|VADER_compound − normalized_score| > 0.4`.

### Quality Analysis — Composite Scoring

The quality analyzer evaluates each review on four dimensions:

**1. Readability (Flesch Reading Ease)**

```
FRE = 206.835 − 1.015 × (words / sentences) − 84.6 × (syllables / words)
```

| Score Range | Interpretation |
|-------------|---------------|
| 90–100 | Very easy (5th grade) |
| 60–70 | Standard (8th–9th grade) |
| 30–60 | Difficult (college level) |
| 0–30 | Very difficult (graduate level) |

**2. Informativeness**

Combines two sub-metrics:
- **Length score**: Reviews in the ideal word-count range (30–300 words) score 100%; shorter reviews are penalized proportionally
- **Vocabulary diversity**: Ratio of unique words to total words — higher diversity indicates richer content

**3. Helpfulness**

Community helpfulness ratio: `helpful_votes / total_votes`, scaled to 0–100. Reviews with no votes receive a neutral score of 50.

**4. Specificity**

Pattern-matched detection of concrete details:
- Quantities: `12 oz`, `24 pack`, `3 cups`
- Measurements: `5 mg`, `2.5 lb`, `100 cal`
- Prices: `$4.99`
- Dates: `01/15/2012`

---

## 📸 Sample Output

### `python main.py stats` (partial)

```
────────────────────────────────────────────────────────────
  📊  Dataset Summary
────────────────────────────────────────────────────────────

  Total Reviews       : 568,454
  Unique Products     : 74,258
  Unique Users        : 256,059
  Average Score       : 4.18 / 5.0

────────────────────────────────────────────────────────────
  ⭐  Score Distribution
────────────────────────────────────────────────────────────

  ★☆☆☆☆    52,268  (  9.2%)  ████
  ★★☆☆☆    29,769  (  5.2%)  ██
  ★★★☆☆    42,640  (  7.5%)  ███
  ★★★★☆    80,655  ( 14.2%)  ███████
  ★★★★★   363,122  ( 63.9%)  ███████████████████████████████
```

### `python main.py sentiment`

```
  Analyzed            : 100 reviews
  Avg VADER compound  : +0.6733
  Mismatches found    : 24  (24.0%)

   Rating   │ Normalized Stars   │ VADER Compound   │ Match?
  ──────────┼────────────────────┼──────────────────┼──────────
   ★☆☆☆☆    │ -1.00              │ -0.1605          │ ⚠ drift
   ★★☆☆☆    │ -0.50              │ +0.1710          │ ⚠ drift
   ★★★☆☆    │ +0.00              │ +0.4537          │ ⚠ drift
   ★★★★☆    │ +0.50              │ +0.7222          │ ✓ yes
   ★★★★★    │ +1.00              │ +0.8313          │ ✓ yes
```

### `python main.py quality`

```
────────────────────────────────────────────────────────────
  📐  Review Quality Analysis (sample = 100)
────────────────────────────────────────────────────────────

  Analyzed              : 100 reviews
  Avg Quality Score     : 62.4 / 100
  Avg Readability (FRE) : 67.3
  Avg Word Count        : 84
  Avg Unique Word Ratio : 58.21%

  🟢 High quality  : 47  (47.0%)
  🟡 Medium quality: 41  (41.0%)
  🔴 Low quality   : 12  (12.0%)

────────────────────────────────────────────────────────────
  Quality Score by Star Rating
────────────────────────────────────────────────────────────

   Rating            │ Avg Quality
  ───────────────────┼─────────────
   ★☆☆☆☆             │ 58.2
   ★★☆☆☆             │ 60.1
   ★★★☆☆             │ 61.5
   ★★★★☆             │ 63.8
   ★★★★★             │ 64.7
```

### `python main.py compare --products B007JFMH8M B000LKTHJK`

```
────────────────────────────────────────────────────────────
  📊  Head-to-Head Comparison
────────────────────────────────────────────────────────────

   Metric              │ B007JFMH8M       │ B000LKTHJK
  ─────────────────────┼──────────────────┼──────────────────
   Total Reviews        │ 142              │ 87
   Avg Score            │ 4.35             │ 3.92
   VADER Compound       │ +0.7210          │ +0.5891
   Mismatch %           │ 18.3%            │ 22.1%
   Avg Word Count       │ 96               │ 73
   Avg Helpfulness      │ 82.4%            │ 75.1%

────────────────────────────────────────────────────────────
  🏅  Winners
────────────────────────────────────────────────────────────

  By Avg Score     : B007JFMH8M
  By Review Volume : B007JFMH8M
  By Sentiment     : B007JFMH8M
```

---

## 📉 Charts Generated

Running `python main.py visualize` generates 6 charts in the `output/` directory:

| Chart | File | Description |
|-------|------|-------------|
| Score Distribution | `score_distribution.png` | Bar chart of 1-5 star rating counts |
| Yearly Trend | `yearly_trend.png` | Area chart showing exponential review growth |
| Review Length | `review_length_by_score.png` | Average review character count per star rating |
| Helpfulness | `helpfulness_by_score.png` | Average helpfulness ratio per star rating |
| Sentiment Comparison | `sentiment_comparison.png` | Side-by-side VADER compound vs normalized star rating |
| Quality by Score | `quality_by_score.png` | **🆕** Average composite quality score per star rating |

---

## ⚙️ Configuration

All tunable parameters are centralized in [`config.py`](config.py):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DEFAULT_SAMPLE_SIZE` | 100 | Reviews sampled for sentiment/quality analysis |
| `DEFAULT_SEARCH_LIMIT` | 20 | Max results for search queries |
| `POSITIVE_THRESHOLD` | 4 | Score ≥ 4 is considered "positive" |
| `SENTIMENT_MISMATCH_DELTA` | 0.4 | VADER vs star disagreement threshold |
| `QUALITY_LENGTH_IDEAL_MIN` | 30 | **🆕** Minimum ideal review word count |
| `QUALITY_LENGTH_IDEAL_MAX` | 300 | **🆕** Maximum ideal review word count |
| `QUALITY_WEIGHT_READABILITY` | 0.25 | **🆕** Weight for readability in composite score |
| `QUALITY_WEIGHT_INFORMATIVENESS` | 0.30 | **🆕** Weight for informativeness in composite score |
| `QUALITY_WEIGHT_HELPFULNESS` | 0.25 | **🆕** Weight for helpfulness in composite score |
| `QUALITY_WEIGHT_SPECIFICITY` | 0.20 | **🆕** Weight for specificity in composite score |
| `CHART_DPI` | 150 | Resolution of saved chart images |
| `CHART_STYLE` | `seaborn-v0_8-darkgrid` | Matplotlib plot style |

---

## 🧪 Testing

The project includes a comprehensive unit test suite using Python's `unittest` framework, compatible with both `unittest` and `pytest` test runners:

```bash
# Run with pytest
python -m pytest tests/ -v

# Run with unittest
python -m unittest discover tests/ -v

# Run with coverage (requires pytest-cov)
python -m pytest tests/ -v --cov=analyzers --cov=models --cov=utils
```

### Test Coverage

| Module | Tests | Coverage Areas |
|--------|-------|---------------|
| `analyzers/quality.py` | 5 tests | Syllable counting, Flesch scoring, single/batch analysis, quality labels |
| `analyzers/comparator.py` | 2 tests | Empty profiles, full comparison flow (mocked sentiment) |
| `utils/helpers.py` | 4 tests | Star strings, number formatting, text cleaning, truncation |
| `models/review.py` | 5 tests | Factory method, helpfulness ratio, word count, positivity, dates |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| [matplotlib](https://matplotlib.org/) | Chart generation |
| [nltk](https://www.nltk.org/) | VADER sentiment analysis |
| [pandas](https://pandas.pydata.org/) | Data manipulation (optional utilities) |

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-analysis`)
3. Write tests for your changes
4. Ensure all existing tests pass (`python -m pytest tests/ -v`)
5. Commit your changes (`git commit -m "Add new analysis feature"`)
6. Push to the branch (`git push origin feature/new-analysis`)
7. Open a Pull Request

### Ideas for Future Contributions

- **Topic Modeling**: LDA-based topic extraction from review text
- **Word Cloud Generation**: Visual word frequency maps for positive vs negative reviews
- **Time-Series Forecasting**: Predict future review volumes using ARIMA or Prophet
- **Deep Learning Sentiment**: Fine-tuned BERT or DistilBERT for more accurate sentiment classification
- **Interactive Dashboard**: Streamlit or Dash web interface for real-time exploration
- **Duplicate Review Detection**: Identify copy-paste or bot-generated reviews
- **User Reputation Scoring**: Rate reviewers based on helpfulness consistency and review quality

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Dataset: [Amazon Fine Food Reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) on Kaggle (originally from Stanford SNAP)
- Sentiment Analysis: [NLTK VADER](https://www.nltk.org/howto/sentiment.html)
- Readability: [Flesch Reading Ease](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests) formula
- Built with Python 🐍
