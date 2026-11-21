"""Evaluation cases, written as TOML files (easy to edit by hand, Unicode-friendly)."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Candidate:
    system: str          # which LLM/pipeline produced it, e.g. "gpt-x-simplify-v1"
    text: str            # the rewritten alert (the script a TTS system would speak)


@dataclass
class Case:
    id: str
    language: str        # "ne", "en", "mai", ...
    source: str          # the official alert text
    must_keep: list[list[str]] = field(default_factory=list)
    may_drop: list[str] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    note: str = ""
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
        must_keep=groups, may_drop=[str(x) for x in data.get("may_drop", [])], note=data.get("note", ""), path=path,
        candidates=[Candidate(system=c["system"], text=c["text"].strip()) for c in data.get("candidates", [])],
    )


def load_cases(paths: list[str | Path]) -> list[Case]:
    files: list[Path] = []
    for p in map(Path, paths):
        files += sorted(p.rglob("*.toml")) if p.is_dir() else [p]
    return [load_case(f) for f in files]
