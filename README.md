# Amazon Fine Food Reviews Analyzer

A Python CLI toolkit for analyzing 568K+ Amazon Fine Food Reviews using sentiment analysis, statistical insights, and chart-based visualizations.

## Features

- **📊 Summary Statistics** — Score distribution, temporal trends, top products/reviewers, helpfulness analysis
- **🧠 Sentiment Analysis** — VADER-based NLP sentiment scoring with star-rating mismatch detection  
- **🔍 Full-Text Search** — Search reviews by keyword across summaries and review text
- **📦 Product Deep-Dive** — Analyze any product by ID with score breakdown and sentiment
- **📉 Chart Generation** — 5 publication-quality matplotlib charts saved to `output/`

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download NLTK data (first run only)
python -c "import nltk; nltk.download('vader_lexicon')"
```

> **Note:** This project requires the Amazon Fine Food Reviews SQLite database (`database.sqlite`) in the project root. The dataset is available on [Kaggle](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews).

## Usage

```bash
# Show comprehensive summary statistics
python main.py stats

# Run sentiment analysis on a random sample
python main.py sentiment --sample-size 100

# Search reviews by keyword
python main.py search --query "chocolate" --limit 10

# Analyze a specific product
python main.py product --id B007JFMH8M

# Generate all charts (saved to output/)
python main.py visualize
```

## Project Structure

```
├── main.py                    # CLI entry point (5 subcommands)
├── config.py                  # Centralized configuration
├── requirements.txt           # matplotlib, nltk, pandas
├── models/
│   ├── review.py              # Review dataclass
│   └── database.py            # ReviewDatabase query handler
├── analyzers/
│   ├── sentiment.py           # VADER sentiment analyzer
│   └── statistics.py          # Descriptive statistics
├── visualizer/
│   └── charts.py              # Matplotlib chart generator
└── utils/
    └── helpers.py             # Text/console formatting utilities
```

## Dataset

- **568,454** reviews across **74,258** products by **256,059** users
- Time span: October 1999 → October 2012
- Average score: 4.18 / 5.0 (64% are 5-star reviews)

## Requirements

- Python 3.8+
- matplotlib, nltk, pandas
