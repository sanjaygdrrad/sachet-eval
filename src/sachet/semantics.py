"""Meaning checks: the parts of an alert that are words, not numbers.

Numbers can all survive while the meaning flips ("above the danger level" → "below the
danger level"). This module detects, in Nepali and English:

  hazard  : flood · flash flood · landslide
  status  : normal · warning level · danger level, and whether the river is ABOVE or BELOW it
  trend   : rising · falling · steady
  action  : move to high ground · keep away from the river · stay alert

Detection is keyword-based and transparent. Statuses are paired with "above/below" words
within the same clause, so contradictions can be flagged.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .normalize import normalize

# Keyword lists (normalised, lower-case). Extend as new real alerts show new phrasings.
HAZARD = {
    "flash flood": ["आकस्मिक बाढी", "आकस्मिक बहाव", "अचानक बाढी", "flash flood"],
    "flood": ["बाढी", "flood"],
    "landslide": ["पहिरो", "landslide"],
}
STATUS = {
    "danger level": ["खतराको तह", "खतरा तह", "खतराको सूचक", "danger level", "danger mark", "danger"],
    "warning level": ["सतर्कता तह", "चेतावनी तह", "warning level", "alert level"],
    "normal": ["सामान्य", "normal"],
}
ABOVE = ["माथि", "पार", "नाघ", "above", "crossed", "exceeded", "over the"]
BELOW = ["तल", "तलै", "below", "under"]
TREND = {
    "rising": ["बढ्दो", "बढ्दै", "बढ्न", "बढ्ने", "बढिरहेको", "rising", "increasing", "going up", "may rise", "will rise", "rises"],
    "falling": ["घट्दो", "घट्दै", "घटिरहेको", "falling", "receding", "decreasing", "going down"],
    "steady": ["स्थिर", "steady", "stable"],
}
ACTION = {
    "move to high ground": ["उच्च तथा सुरक्षित स्थान", "उच्च स्थान", "अग्लो ठाउँ", "सुरक्षित स्थान", "सुरक्षित उच्च स्थान",
                            "high ground", "higher ground", "safe ground", "safe place"],
    "keep away from the river": ["टाढा रहनुहोस्", "टाढा बस्नुहोस्", "टाढा रहनु", "टाढा बस्नु", "keep away", "stay away", "away from the river", "away from river"],
    "stay alert": ["सतर्क रहनुहोस्", "सतर्कता अपनाऔं", "सतर्कता अपनाउनुहोस्", "stay alert", "be alert", "remain alert", "be careful"],
}

_CLAUSE = re.compile(r"[।॥;\n]+|\.(?!\d)")   # don't split "6.8"
# Labels that mention a hazard without stating one is happening (e.g. the flood hotline).
_NOT_A_HAZARD = ["बाढी सूचना", "बाढी पूर्वसूचना", "बाढी सम्बन्धी पूर्वसूचना", "flood information", "flood info", "flood hotline", "flood forecast bulletin", "बाढी पूर्वानुमान बुलेटिन"]


def _has(text: str, words: list[str]) -> bool:
    return any(normalize(w) in text for w in words)


@dataclass
class Meaning:
    hazards: set[str] = field(default_factory=set)
    statuses: dict[str, set[str]] = field(default_factory=dict)  # status -> {"above","below"} (empty = mentioned only)
    trends: set[str] = field(default_factory=set)
    actions: set[str] = field(default_factory=set)


def extract_meaning(text: str) -> Meaning:
    t = normalize(text)
    m = Meaning()
    th = t
    for label in _NOT_A_HAZARD:
        th = th.replace(normalize(label), " ")
    for name, words in HAZARD.items():
        if _has(th, words):
            m.hazards.add(name)
    if "flash flood" in m.hazards and not re.search(r"(?<!आकस्मिक )(?<!अचानक )बाढी|(?<!flash )flood", th):
        m.hazards.discard("flood")  # only "flash flood" was mentioned
    for clause in filter(None, (c.strip() for c in _CLAUSE.split(t))):
        found = [s for s, words in STATUS.items() if _has(clause, words)]
        levels = [s for s in found if s != "normal"]   # "normal" is a state, not a level
        for s in found:
            rel: set[str] = set()
            if s != "normal" and len(levels) == 1:   # with two levels in one clause, don't guess
                if _has(clause, ABOVE):
                    rel.add("above")
                if _has(clause, BELOW):
                    rel.add("below")
            m.statuses.setdefault(s, set()).update(rel)
    for name, words in TREND.items():
        if _has(t, words):
            m.trends.add(name)
    for name, words in ACTION.items():
        if _has(t, words):
            m.actions.add(name)
    return m


@dataclass
class MeaningResult:
    missing: list[str] = field(default_factory=list)
    contradicted: list[str] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)


def compare_meaning(source: str, output: str, require_trend: bool = True) -> MeaningResult:
    src, out = extract_meaning(source), extract_meaning(output)
    r = MeaningResult()

    def need(label: str, ok: bool) -> None:
        (r.kept if ok else r.missing).append(label)

    for h in sorted(src.hazards):
        need(f"hazard: {h}", h in out.hazards or (h == "flood" and "flash flood" in out.hazards))
    for s, rels in sorted(src.statuses.items()):
        if s == "normal":
            need("status: normal", "normal" in out.statuses)
            continue
        for rel in sorted(rels):
            opposite = "below" if rel == "above" else "above"
            out_rels = out.statuses.get(s, set())
            if opposite in out_rels and rel not in out_rels:
                r.contradicted.append(f"{s}: source says {rel}, rewrite says {opposite}")
            else:
                need(f"{rel} {s}", s in out.statuses)
    if require_trend:
        for tr in sorted(src.trends):
            other = {"rising": "falling", "falling": "rising"}.get(tr)
            if other and other in out.trends and tr not in out.trends:
                r.contradicted.append(f"trend: source says {tr}, rewrite says {other}")
            else:
                need(f"trend: {tr}", tr in out.trends)
    for a in sorted(src.actions):
        need(f"action: {a}", a in out.actions)
    return r
