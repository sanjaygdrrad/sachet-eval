"""Text normalisation shared by every metric.

Nepali alerts mix Devanagari digits (६.८) and Latin digits (6.8), and Nepali number
grouping (1,00,000). Everything is normalised so that the same fact compares equal
no matter how it is written.
"""
from __future__ import annotations

import re
import unicodedata

DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

# 1,149 · 12,500 · 1,00,000 (Nepali/Indian grouping)
_GROUPED = re.compile(r"(?<![\d.])\d{1,3}(?:,\d{2,3})+(?![\d,])")


def normalize(text: str) -> str:
    """Unicode NFC, Latin digits, lower-case Latin letters, single spaces."""
    text = unicodedata.normalize("NFC", text).translate(DEVANAGARI_DIGITS)
    text = _GROUPED.sub(lambda m: m.group(0).replace(",", ""), text)
    text = text.replace("‍", "").replace("‌", "")  # zero-width joiners
    return re.sub(r"\s+", " ", text).strip().lower()


def canonical_number(raw: str) -> str:
    """'06.50' → '6.5', '007' → '7', '1,149' → '1149'."""
    raw = raw.replace(",", "")
    if "." in raw:
        whole, frac = raw.split(".", 1)
        whole = whole.lstrip("0") or "0"
        frac = frac.rstrip("0")
        return f"{whole}.{frac}" if frac else whole
    return raw.lstrip("0") or "0"
