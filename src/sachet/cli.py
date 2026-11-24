"""Command line:  sachet eval cases/ [--json] [--out report.md] [--strict]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .cases import load_cases
from .integrity import check_integrity
from .capimport import cap_to_case_toml
from .report import run, to_json, to_markdown


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sachet", description="Evaluate LLM rewrites of disaster alerts for factual faithfulness.")
    ap.add_argument("--version", action="version", version=f"sachet-eval {__version__}")
    sub = ap.add_subparsers(dest="command", required=True)
    ev = sub.add_parser("eval", help="score every candidate in the given case files/folders")
    ev.add_argument("paths", nargs="+", help="TOML case files or folders")
    ev.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    ev.add_argument("--out", type=Path, help="also write the report to this file")
    ev.add_argument("--strict", action="store_true", help="exit with code 1 if any candidate fails (for CI)")
    li = sub.add_parser("lint", help="check text files for corrupted Devanagari (e.g. copied from legacy-font PDFs)")
    li.add_argument("paths", nargs="+", type=Path, help="text files")
    fc = sub.add_parser("from-cap", help="turn a CAP 1.2 alert (XML) into a case file")
    fc.add_argument("cap", type=Path, help="CAP 1.2 XML file")
    fc.add_argument("--lang", default="ne", help="language of the official source text (default: ne)")
    fc.add_argument("--id", help="case id (default: from the file name)")
    fc.add_argument("--out", type=Path, help="write the case here instead of printing it")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")   # Nepali text on Windows consoles

    if args.command == "from-cap":
        if not args.cap.is_file():
            print(f"sachet: error: file not found: {args.cap}", file=sys.stderr)
            return 2
        toml = cap_to_case_toml(args.cap, args.lang, args.id)
        if args.out:
            args.out.write_text(toml, encoding="utf-8")
            print(f"Wrote {args.out}. Now fill in must_keep, may_drop and may_add.")
        else:
            print(toml)
        return 0

    if args.command == "lint":
        missing = [p for p in args.paths if not p.is_file()]
        if missing:
            print(f"sachet: error: file not found: {', '.join(map(str, missing))} (current folder: {Path.cwd()})", file=sys.stderr)
            return 2
        bad = 0
        for p in args.paths:
            r = check_integrity(p.read_text(encoding="utf-8"))
            verdict = "❌ likely corrupted" if r.corrupted else "✅ looks intact"
            print(f"{p}: {verdict}. {len(r.orphans)} broken word(s) in {r.words} Devanagari words ({r.ratio:.0%})")
            for o in r.orphans[:8]:
                print(f"    · {o}")
            bad += r.corrupted
        return 1 if bad else 0
    try:
        rows = run(load_cases(args.paths))
    except (FileNotFoundError, ValueError) as e:   # wrong folder, missing or invalid case file
        print(f"sachet: error: {e}", file=sys.stderr)
        return 2
    text = to_json(rows) if args.json else to_markdown(rows)
    print(text)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    return 1 if args.strict and not all(r.result.passed for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
