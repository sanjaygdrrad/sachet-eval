"""Entry point for the public web portal (runs in the browser via Pyodide).

Everything the page shows is computed here, in the same tested Python code as the CLI.
Inputs are plain text from the form; the output is a JSON-friendly dict.
"""
from __future__ import annotations

import re

from .cases import Case
from .facts import extract_facts
from .integrity import check_integrity
from .report import evaluate
from .semantics import extract_meaning


def parse_names(text: str) -> list[list[str]]:
    """'नारायणी / Narayani, चितवन / Chitwan' → [["नारायणी","Narayani"],["चितवन","Chitwan"]].

    One name per line or comma-separated; alternative spellings separated by "/" or "|".
    """
    groups = []
    for chunk in re.split(r"[,\n،]+", text or ""):
        aliases = [a.strip() for a in re.split(r"[/|]", chunk) if a.strip()]
        if aliases:
            groups.append(aliases)
    return groups


def parse_values(text: str) -> list[str]:
    return [v.strip() for v in re.split(r"[,\n]+", text or "") if v.strip()]


def check(source: str, rewrite: str, channel: str = "full", names: str = "",
          may_drop: str = "", may_add: str = "", sms_numbers: str = "") -> dict:
    source, rewrite = (source or "").strip(), (rewrite or "").strip()
    if not source or not rewrite:
        return {"ok": False, "error": "Please paste both the official alert and the rewritten version."}
    channel = "sms" if channel == "sms" else "full"
    case = Case(id="portal", language="ne", source=source, must_keep=parse_names(names),
                may_drop=parse_values(may_drop), may_add=parse_values(may_add),
                sms_keep_numbers=parse_values(sms_numbers))
    row = evaluate(case, rewrite, channel=channel, system="portal")
    integrity = check_integrity(source)
    meaning = extract_meaning(source)
    return {
        "ok": True,
        "passed": row.passed,
        "channel": channel,
        "facts": {"kept": row.result.kept, "missing": row.result.missing, "invented": row.result.invented,
                  "total": row.result.total, "score": round(row.result.score, 4)},
        "meaning": {"kept": row.meaning.kept, "missing": row.meaning.missing, "flipped": row.meaning.contradicted},
        "source_integrity": {"corrupted": integrity.corrupted, "broken_words": integrity.orphans[:10],
                             "devanagari_words": integrity.words},
        "detected_in_source": {
            "numbers": sorted(str(f) for f in extract_facts(source)),
            "hazards": sorted(meaning.hazards),
            "statuses": {k: sorted(v) for k, v in meaning.statuses.items()},
            "trends": sorted(meaning.trends),
            "actions": sorted(meaning.actions),
        },
        "names_checked": len(case.must_keep),
    }


def case_toml(source: str, rewrite: str, channel: str = "full", names: str = "", note: str = "") -> str:
    """A ready-to-paste case file, for contributing an example to the repository."""
    def q(s: str) -> str:
        return '"""\n' + (s or "").strip().replace("\\", "\\\\").replace('"""', '\\"\\"\\"') + '\n"""'
    groups = parse_names(names)
    mk = "[" + ", ".join("[" + ", ".join('"' + a.replace('"', "'") + '"' for a in g) + "]" for g in groups) + "]"
    return "\n".join([
        'id = "contributed-TODO"', 'language = "ne"', 'source_url = "TODO: link to the official alert"',
        f'note = "{(note or "Contributed via the Sachet portal").replace(chr(34), chr(39))}"', "",
        f"source = {q(source)}", "", f"must_keep = {mk}", "", "[[candidates]]",
        'system = "TODO: which tool or person wrote it"', f'channel = "{"sms" if channel == "sms" else "full"}"',
        f"text = {q(rewrite)}", "",
    ])
