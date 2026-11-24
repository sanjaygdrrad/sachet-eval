"""Faithfulness: does a rewritten alert keep every critical fact, and invent none?

Verdict is deliberately strict. In a flood warning, one wrong number is a failure.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .facts import Fact, extract_facts
from .normalize import normalize


@dataclass
class FaithfulnessResult:
    kept: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)     # in the source, absent from the output
    invented: list[str] = field(default_factory=list)    # in the output, absent from the source
    total: int = 0

    @property
    def score(self) -> float:
        """Share of critical facts kept (1.0 = all kept)."""
        return 1.0 if self.total == 0 else len(self.kept) / self.total

    @property
    def passed(self) -> bool:
        return not self.missing and not self.invented


def _present(aliases: list[str], text_norm: str) -> bool:
    return any(normalize(a) in text_norm for a in aliases)


def check_faithfulness(source: str, output: str, must_keep: list[list[str]] | None = None,
                       may_drop: list[str] | None = None) -> FaithfulnessResult:
    """Compare ``output`` with ``source``.

    ``must_keep`` lists names that must survive, each as a group of acceptable spellings,
    e.g. ``[["नारायणी", "Narayani"], ["देवघाट", "Devghat"]]``.
    ``may_drop`` lists source numbers/times/dates that are context, not safety-critical
    (e.g. "24" in "120 mm in 24 hours"). They may be left out, but never changed.
    """
    res = FaithfulnessResult()
    src, out = extract_facts(source), extract_facts(output)
    optional = {f for f in src if any(f in extract_facts(x) for x in (may_drop or []))}

    # A fact counts once: repeating "1155" twice in the official text doesn't require
    # the rewrite to repeat it. What matters is that it is present, and unchanged.
    for fact in sorted(set(src)):
        if fact in optional and fact not in out:
            continue  # allowed to be left out
        res.total += 1
        (res.kept if fact in out else res.missing).append(str(fact))

    for fact in sorted(set(out) - set(src)):
        res.invented.append(str(fact))

    out_norm = normalize(output)
    for aliases in must_keep or []:
        res.total += 1
        label = " / ".join(aliases)
        (res.kept if _present(aliases, out_norm) else res.missing).append(label)

    return res


def facts_summary(text: str) -> Counter[Fact]:
    return extract_facts(text)
