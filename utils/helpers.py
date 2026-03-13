"""
Utility helpers — text cleaning, formatting, and display functions.
"""
import re
import textwrap
from datetime import datetime
from typing import List, Dict, Any

from config import HEADER_COLOR, SUCCESS_COLOR, WARN_COLOR, ERROR_COLOR, RESET_COLOR


# ── Text Helpers ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Basic text cleaning: strip HTML tags, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)          # remove HTML tags
    text = re.sub(r"&[a-z]+;", " ", text)          # remove HTML entities
    text = re.sub(r"\s+", " ", text).strip()       # collapse whitespace
    return text


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text and append ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def unix_to_date(ts: int) -> str:
    """Convert unix timestamp to YYYY-MM-DD string."""
    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")


# ── Console Formatting ──────────────────────────────────────────────────────

def header(title: str) -> str:
    """Render a bold cyan section header."""
    line = "─" * 60
    return f"\n{HEADER_COLOR}{line}\n  {title}\n{line}{RESET_COLOR}\n"


def success(msg: str) -> str:
    return f"{SUCCESS_COLOR}✓ {msg}{RESET_COLOR}"


def warn(msg: str) -> str:
    return f"{WARN_COLOR}⚠ {msg}{RESET_COLOR}"


def error(msg: str) -> str:
    return f"{ERROR_COLOR}✗ {msg}{RESET_COLOR}"


def format_number(n) -> str:
    """Format a number with comma separators."""
    if isinstance(n, float):
        return f"{n:,.2f}"
    return f"{n:,}"


def print_table(headers: List[str], rows: List[List[Any]], col_widths: List[int] = None):
    """Print a simple formatted table to the console."""
    if not col_widths:
        col_widths = []
        for i, h in enumerate(headers):
            max_w = len(str(h))
            for row in rows:
                if i < len(row):
                    max_w = max(max_w, len(str(row[i])))
            col_widths.append(min(max_w + 2, 60))

    # Header
    hdr = "│".join(f" {str(h).ljust(col_widths[i])} " for i, h in enumerate(headers))
    sep = "┼".join("─" * (w + 2) for w in col_widths)
    print(f"  {hdr}")
    print(f"  {sep}")

    # Rows
    for row in rows:
        line = "│".join(
            f" {truncate(str(row[i]), col_widths[i]).ljust(col_widths[i])} "
            if i < len(row) else " " * (col_widths[i] + 2)
            for i in range(len(headers))
        )
        print(f"  {line}")


def stars_str(score: int) -> str:
    """Return a ★/☆ string for a given 1-5 score."""
    return "★" * score + "☆" * (5 - score)
