"""Run cases and render results as Markdown (for humans) or JSON (for tools)."""
from __future__ import annotations

import json
from dataclasses import dataclass

from .cases import Case, provenance
from .faithfulness import FaithfulnessResult, check_faithfulness
from .semantics import MeaningResult, compare_meaning


@dataclass
class Row:
    case: Case
    system: str
    channel: str
    result: FaithfulnessResult
    meaning: MeaningResult

    @property
    def passed(self) -> bool:
        return self.result.passed and not self.meaning.missing and not self.meaning.contradicted


def evaluate(case: Case, text: str, channel: str = "full", system: str = "") -> Row:
    sms = channel == "sms"
    facts = check_faithfulness(
        case.source, text,
        must_keep=(case.sms_must_keep or case.must_keep) if sms else case.must_keep,
        may_drop=case.may_drop, may_add=case.may_add,
        numbers_optional=sms, keep_numbers=case.sms_keep_numbers,
    )
    return Row(case, system, channel, facts, compare_meaning(case.source, text, require_trend=not sms))


def run(cases: list[Case]) -> list[Row]:
    return [evaluate(c, cand.text, cand.channel, cand.system) for c in cases for cand in c.candidates]


def to_markdown(rows: list[Row]) -> str:
    passed = sum(r.passed for r in rows)
    out = [
        "# Sachet Eval: faithfulness report",
        "",
        f"**{passed} of {len(rows)}** outputs kept every critical fact and meaning, and invented or flipped nothing.",
        "",
        "| Case | Channel | System | Facts kept | Missing | Invented | Meaning lost / flipped | Verdict |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        res, m = r.result, r.meaning
        meaning = "; ".join([f"⚠️ {c}" for c in m.contradicted] + m.missing) or "–"
        out.append(
            f"| `{r.case.id}` | {r.channel} | {r.system} | {len(res.kept)}/{res.total} ({res.score:.0%}) "
            f"| {', '.join(res.missing) or '–'} | {', '.join(res.invented) or '–'} | {meaning} | {'✅ pass' if r.passed else '❌ fail'} |"
        )
    out += [
        "",
        "_Missing = in the official alert but not in the output. Invented = in the output but not in the official alert. "
        "Meaning = hazard, status (above/below warning or danger level), trend and action; ⚠️ marks a flipped meaning. "
        "SMS outputs must keep the place, status and action, but numbers are optional unless listed in `sms_keep_numbers`._",
        "",
    ]
    sourced = {r.case.id: r.case for r in rows if r.case.source_url}
    if sourced:
        out += ["## Sources", ""]
        out += [f"- `{c.id}` ({provenance(c)}): {c.issuer or 'source'}, {c.issued or 'date n/a'}: <{c.source_url}>" for c in sourced.values()]
        out.append("")
    return "\n".join(out)


def to_json(rows: list[Row]) -> str:
    return json.dumps([
        {"case": r.case.id, "language": r.case.language, "system": r.system, "channel": r.channel,
         "score": round(r.result.score, 4), "passed": r.passed, "kept": r.result.kept, "missing": r.result.missing,
         "invented": r.result.invented, "meaning_missing": r.meaning.missing, "meaning_flipped": r.meaning.contradicted,
         "provenance": provenance(r.case) if r.case.source_url else None}
        for r in rows
    ], ensure_ascii=False, indent=2)
