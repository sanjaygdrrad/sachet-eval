"""Extraction of safety-critical facts: dates, times and numbers.

Phase 1 is deliberately rule-based and transparent: anyone can see why a fact was found.
Place names, rivers and hotline names are listed per test case (``must_keep``) instead of
being guessed, because a missed or misspelled place is exactly the error we must catch.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .normalize import canonical_number, normalize

# 2081-05-12 · 2081/5/12 · 12.05.2081
_DATE = re.compile(r"(?<!\d)(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})(?!\d)|(?<!\d)(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})(?!\d)")
# 7:00 · 19:30 · 7.30 is NOT a time (could be a level), so only ':' counts
_TIME = re.compile(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)")
_NUMBER = re.compile(r"(?<![\d.])\d+(?:\.\d+)?(?![\d])")


@dataclass(frozen=True, order=True)
class Fact:
    kind: str   # "date" | "time" | "number"
    value: str  # canonical form, e.g. "2081-5-12", "7:00", "6.8"

    def __str__(self) -> str:
        return self.value if self.kind == "number" else f"{self.value} ({self.kind})"


def extract_facts(text: str) -> Counter[Fact]:
    """Return every date, time and number in ``text`` (as a multiset)."""
    s = normalize(text)
    found: Counter[Fact] = Counter()

    def take(pattern: re.Pattern[str], make) -> None:
        nonlocal s
        for m in list(pattern.finditer(s)):
            found[make(m)] += 1
        s = pattern.sub(" ", s)  # don't count the same digits twice

    def date(m: re.Match[str]) -> Fact:
        y, mo, d = (m.group(1), m.group(2), m.group(3)) if m.group(1) else (m.group(6), m.group(5), m.group(4))
        return Fact("date", f"{int(y)}-{int(mo)}-{int(d)}")

    take(_DATE, date)
    take(_TIME, lambda m: Fact("time", f"{int(m.group(1))}:{m.group(2)}"))
    take(_NUMBER, lambda m: Fact("number", canonical_number(m.group(0))))
    return found
