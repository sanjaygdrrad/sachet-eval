"""Word error rate: used to check intelligibility of generated speech.

Phase 2 will transcribe each TTS audio clip with speech recognition and compare the
transcript with the script that was spoken. WER works on any script, including Devanagari.
"""
from __future__ import annotations

import unicodedata

from .normalize import normalize


def _tokens(text: str) -> list[str]:
    # Replace punctuation (incl. the Devanagari danda ।) and symbols with spaces.
    # Note: regex \w would wrongly split Nepali words at vowel signs (ो, े, ्), so we
    # classify characters with the Unicode database instead.
    cleaned = "".join(" " if unicodedata.category(c)[0] in "PS" else c for c in normalize(text))
    return cleaned.split()


def word_error_rate(reference: str, hypothesis: str) -> float:
    """(substitutions + deletions + insertions) / words in reference."""
    ref, hyp = _tokens(reference), _tokens(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i] + [0] * len(hyp)
        for j, h in enumerate(hyp, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (r != h))
        prev = cur
    return prev[-1] / len(ref)
