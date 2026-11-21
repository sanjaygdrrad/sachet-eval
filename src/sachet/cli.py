"""Command line:  sachet eval cases/ [--json] [--out report.md] [--strict]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .cases import load_cases
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
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")   # Nepali text on Windows consoles
    rows = run(load_cases(args.paths))
    text = to_json(rows) if args.json else to_markdown(rows)
    print(text)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    return 1 if args.strict and not all(r.result.passed for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
