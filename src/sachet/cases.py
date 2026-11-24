"""Evaluation cases, written as TOML files (easy to edit by hand, Unicode-friendly)."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Candidate:
    system: str          # which LLM/pipeline produced it, e.g. "gpt-x-simplify-v1"
    text: str            # the rewritten alert (the script a TTS system would speak)
    channel: str = "full"   # "full" (radio / phone script) or "sms" (short message)


@dataclass
class Case:
    id: str
    language: str        # "ne", "en", "mai", ...
    source: str          # the official alert text
    must_keep: list[list[str]] = field(default_factory=list)
    may_drop: list[str] = field(default_factory=list)
    may_add: list[str] = field(default_factory=list)
    sms_must_keep: list[list[str]] = field(default_factory=list)   # names an SMS must keep (default: must_keep)
    sms_keep_numbers: list[str] = field(default_factory=list)      # numbers an SMS must keep (default: none)
    relayed_by: str = ""                                           # e.g. "Gati", if not taken from the agency directly
    candidates: list[Candidate] = field(default_factory=list)
    note: str = ""
    issuer: str = ""
    issued: str = ""
    source_url: str = ""
    path: Path | None = None


def load_case(path: str | Path) -> Case:
    path = Path(path)
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in ("id", "language", "source") if k not in data]
    if missing:
        raise ValueError(f"{path}: missing required field(s): {', '.join(missing)}")
    groups = [g if isinstance(g, list) else [g] for g in data.get("must_keep", [])]
    return Case(
        id=data["id"], language=data["language"], source=data["source"].strip(),
        must_keep=groups, may_drop=[str(x) for x in data.get("may_drop", [])], may_add=[str(x) for x in data.get("may_add", [])], note=data.get("note", ""), path=path,
        issuer=data.get("issuer", ""), issued=str(data.get("issued", "")), source_url=data.get("source_url", ""),
        candidates=[Candidate(system=c["system"], text=c["text"].strip(), channel=c.get("channel", "full")) for c in data.get("candidates", [])],
        sms_must_keep=[g if isinstance(g, list) else [g] for g in data.get("sms_must_keep", [])],
        sms_keep_numbers=[str(x) for x in data.get("sms_keep_numbers", [])],
        relayed_by=data.get("relayed_by", ""),
    )


def load_cases(paths: list[str | Path]) -> list[Case]:
    files: list[Path] = []
    for p in map(Path, paths):
        if not p.exists():
            raise FileNotFoundError(f"'{p}' not found (current folder: {Path.cwd()}). "
                                    "Run sachet from the project folder, or give the full path.")
        files += sorted(p.rglob("*.toml")) if p.is_dir() else [p]
    if not files:
        raise FileNotFoundError(f"No .toml case files found in: {', '.join(map(str, paths))}")
    return [load_case(f) for f in files]


OFFICIAL_DOMAINS = ("hydrology.gov.np", "dhm.gov.np", "bipadportal.gov.np", "ndrrma.gov.np", "moha.gov.np",
                    "nepalpolice.gov.np", "neoc.gov.np")
OFFICIAL_ACCOUNTS = ("x.com/ndrrma_nepal", "twitter.com/ndrrma_nepal", "facebook.com/nepalfloodalert")


def provenance(case: Case) -> str:
    """'official', 'relayed from official (by X)' or 'unverified source', from the source link."""
    from urllib.parse import urlparse
    url = case.source_url.lower()
    host = urlparse(url).hostname or ""
    official = any(host == d or host.endswith("." + d) for d in OFFICIAL_DOMAINS) or any(a in url for a in OFFICIAL_ACCOUNTS)
    if official and case.relayed_by:
        return f"relayed from official (by {case.relayed_by})"
    return "official" if official else "unverified source"
