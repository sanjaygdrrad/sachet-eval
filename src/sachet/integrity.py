"""Text integrity: detect Devanagari that was corrupted on the way in.

Official bulletins are often PDFs in legacy font encodings. Copying or machine-reading
them drops conjunct letters (e.g. "विज्ञान" → "िव ान", "स्रोत" → "ोत"). Feeding such
text to an LLM or TTS system produces wrong words and wrong speech, so it must be
caught before the text enters a pipeline.

Heuristic (no dictionary needed): a Devanagari vowel sign or virama cannot start a
word. When one does, a letter in front of it was lost.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# dependent vowel signs, virama, nukta, candrabindu/anusvara/visarga
_SIGNS = "".join(chr(c) for c in range(0x0900, 0x0980) if unicodedata.category(chr(c)) in ("Mn", "Mc"))
_ORPHAN = re.compile(rf"(?:(?<=^)|(?<=[\s\-–,;:()\"'।|]))[{_SIGNS}]+\S*", re.MULTILINE)
_DEVANAGARI_WORD = re.compile(r"[ऀ-ॿ]+")


@dataclass
class IntegrityResult:
    words: int = 0
    orphans: list[str] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        return 0.0 if self.words == 0 else len(self.orphans) / self.words

    @property
    def corrupted(self) -> bool:
        # one orphan can be a typo; several, or >1 % of words, means a broken extraction
        return len(self.orphans) >= 3 or self.ratio > 0.01


def check_integrity(text: str) -> IntegrityResult:
    text = unicodedata.normalize("NFC", text)
    return IntegrityResult(
        words=len(_DEVANAGARI_WORD.findall(text)),
        orphans=[m.group(0) for m in _ORPHAN.finditer(text)],
    )
