"""
Configuration constants for the Amazon Fine Food Reviews Analysis project.
"""
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.sqlite")
CSV_PATH = os.path.join(BASE_DIR, "Reviews.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# --- Database ---
TABLE_NAME = "Reviews"

# --- Analysis Defaults ---
DEFAULT_SAMPLE_SIZE = 100
DEFAULT_SEARCH_LIMIT = 20
POSITIVE_THRESHOLD = 4          # Score >= 4 is "positive"
SENTIMENT_MISMATCH_DELTA = 0.4  # VADER vs star disagreement threshold

# --- Quality Analysis ---
QUALITY_LENGTH_IDEAL_MIN = 30   # Minimum ideal word count for a good review
QUALITY_LENGTH_IDEAL_MAX = 300  # Maximum ideal word count before diminishing returns
QUALITY_WEIGHT_READABILITY = 0.25
QUALITY_WEIGHT_INFORMATIVENESS = 0.30
QUALITY_WEIGHT_HELPFULNESS = 0.25
QUALITY_WEIGHT_SPECIFICITY = 0.20

# --- Visualization ---
CHART_DPI = 150
CHART_STYLE = "seaborn-v0_8-darkgrid"
COLOR_PALETTE = [
    "#e74c3c",  # 1-star  red
    "#e67e22",  # 2-star  orange
    "#f1c40f",  # 3-star  yellow
    "#2ecc71",  # 4-star  green
    "#27ae60",  # 5-star  dark green
]

# --- Console Formatting ---
HEADER_COLOR = "\033[1;36m"   # bold cyan
SUCCESS_COLOR = "\033[1;32m"  # bold green
WARN_COLOR = "\033[1;33m"     # bold yellow
ERROR_COLOR = "\033[1;31m"    # bold red
RESET_COLOR = "\033[0m"
