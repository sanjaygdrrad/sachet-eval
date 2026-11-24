"""Run cases and render results as Markdown (for humans) or JSON (for tools)."""
from __future__ import annotations

import json
from dataclasses import dataclass

from .cases import Case
from .faithfulness import FaithfulnessResult, check_faithfulness


@dataclass
class Row:
    case: Case
    system: str
    result: FaithfulnessResult


def run(cases: list[Case]) -> list[Row]:
    return [Row(c, cand.system, check_faithfulness(c.source, cand.text, c.must_keep, c.may_drop, c.may_add)) for c in cases for cand in c.candidates]


def to_markdown(rows: list[Row]) -> str:
    passed = sum(r.result.passed for r in rows)
    out = [
        "# Sachet Eval: faithfulness report",
        "",
        f"**{passed} of {len(rows)}** outputs kept every critical fact and invented none.",
        "",
        "| Case | Lang | System | Facts kept | Missing | Invented | Verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        res = r.result
        out.append(
            f"| `{r.case.id}` | {r.case.language} | {r.system} | {len(res.kept)}/{res.total} ({res.score:.0%}) "
            f"| {', '.join(res.missing) or '–'} | {', '.join(res.invented) or '–'} | {'✅ pass' if res.passed else '❌ fail'} |"
        )
    out += ["", "_Missing = in the official alert but not in the output. Invented = in the output but not in the official alert._", ""]
    sourced = {r.case.id: r.case for r in rows if r.case.source_url}
    if sourced:
        out += ["## Sources", ""]
        out += [f"- `{c.id}`: {c.issuer or 'source'}, {c.issued or 'date n/a'}: <{c.source_url}>" for c in sourced.values()]
        out.append("")
    return "\n".join(out)


def to_json(rows: list[Row]) -> str:
    return json.dumps([
        {"case": r.case.id, "language": r.case.language, "system": r.system, "score": round(r.result.score, 4),
         "passed": r.result.passed, "kept": r.result.kept, "missing": r.result.missing, "invented": r.result.invented}
        for r in rows
    ], ensure_ascii=False, indent=2)
