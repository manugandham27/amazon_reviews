# 🛒 Amazon Fine Food Reviews Analyzer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![NLTK](https://img.shields.io/badge/NLP-VADER-orange)](https://www.nltk.org/)
[![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-blue)](https://matplotlib.org/)

> A modular Python CLI toolkit for analyzing **568,454 Amazon Fine Food Reviews** with VADER sentiment analysis, statistical insights, and publication-quality chart visualizations.

---

## ✨ Features

| Command | Description |
|---------|-------------|
| `stats` | Comprehensive summary — score distribution, temporal trends, top products/reviewers, helpfulness analysis, review length stats |
| `sentiment` | VADER-based NLP sentiment scoring on random samples with star-rating mismatch detection |
| `search` | Full-text keyword search across review summaries and body text |
| `product` | Deep-dive into any product by ID — score breakdown, latest reviews, sentiment |
| `visualize` | Generate 5 publication-quality charts saved as PNGs |

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Project Architecture](#-project-architecture)
- [Dataset Overview](#-dataset-overview)
- [Database Schema](#-database-schema)
- [Sample Output](#-sample-output)
- [Charts Generated](#-charts-generated)
- [Configuration](#%EF%B8%8F-configuration)
- [Dependencies](#-dependencies)
- [Contributing](#-contributing)
- [License](#-license)

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

Generates 5 charts saved to the `output/` directory (see [Charts Generated](#-charts-generated) below).

---

## 🏗 Project Architecture

```
amazon_reviews/
│
├── main.py                        # CLI entry point — argparse with 5 subcommands
├── config.py                      # Centralized paths, thresholds, colors, constants
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
│   └── statistics.py              # StatisticsAnalyzer — descriptive analytics
│
├── visualizer/                    # Presentation layer
│   ├── __init__.py
│   └── charts.py                  # ChartGenerator — matplotlib chart factory
│
├── utils/                         # Shared utilities
│   ├── __init__.py
│   └── helpers.py                 # Text cleaning, console formatting, table printer
│
└── output/                        # Generated charts (auto-created)
    ├── score_distribution.png
    ├── yearly_trend.png
    ├── review_length_by_score.png
    ├── helpfulness_by_score.png
    └── sentiment_comparison.png
```

### Key Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `Review` | `models/review.py` | Dataclass for a single review with computed properties (`is_positive`, `helpfulness_ratio`, `word_count`, `date`) |
| `ReviewDatabase` | `models/database.py` | SQLite wrapper with context manager — queries, aggregations, random sampling |
| `SentimentAnalyzer` | `analyzers/sentiment.py` | VADER sentiment scoring, batch analysis, star-rating mismatch reports |
| `StatisticsAnalyzer` | `analyzers/statistics.py` | Descriptive stats — summaries, temporal trends, helpfulness/length analysis |
| `ChartGenerator` | `visualizer/charts.py` | Matplotlib chart factory — 5 chart types saved as PNGs |

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

---

## 📉 Charts Generated

Running `python main.py visualize` generates 5 charts in the `output/` directory:

| Chart | File | Description |
|-------|------|-------------|
| Score Distribution | `score_distribution.png` | Bar chart of 1-5 star rating counts |
| Yearly Trend | `yearly_trend.png` | Area chart showing exponential review growth |
| Review Length | `review_length_by_score.png` | Average review character count per star rating |
| Helpfulness | `helpfulness_by_score.png` | Average helpfulness ratio per star rating |
| Sentiment Comparison | `sentiment_comparison.png` | Side-by-side VADER compound vs normalized star rating |

---

## ⚙️ Configuration

All tunable parameters are centralized in [`config.py`](config.py):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DEFAULT_SAMPLE_SIZE` | 100 | Reviews sampled for sentiment analysis |
| `DEFAULT_SEARCH_LIMIT` | 20 | Max results for search queries |
| `POSITIVE_THRESHOLD` | 4 | Score ≥ 4 is considered "positive" |
| `SENTIMENT_MISMATCH_DELTA` | 0.4 | VADER vs star disagreement threshold |
| `CHART_DPI` | 150 | Resolution of saved chart images |
| `CHART_STYLE` | `seaborn-v0_8-darkgrid` | Matplotlib plot style |

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
3. Commit your changes (`git commit -m "Add new analysis feature"`)
4. Push to the branch (`git push origin feature/new-analysis`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Dataset: [Amazon Fine Food Reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) on Kaggle (originally from Stanford SNAP)
- Sentiment Analysis: [NLTK VADER](https://www.nltk.org/howto/sentiment.html)
- Built with Python 🐍
