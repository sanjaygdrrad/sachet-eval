"""Assemble the public portal into _site/: the web page plus the Sachet Python package.

    python scripts/build_portal.py && python -m http.server -d _site 8000
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

shutil.rmtree(SITE, ignore_errors=True)
shutil.copytree(ROOT / "portal", SITE)
(SITE / "py" / "sachet").mkdir(parents=True)
files = sorted(p.name for p in (ROOT / "src" / "sachet").glob("*.py"))
for name in files:
    shutil.copy2(ROOT / "src" / "sachet" / name, SITE / "py" / "sachet" / name)
(SITE / "py" / "manifest.json").write_text(json.dumps(files), encoding="utf-8")
(SITE / ".nojekyll").write_text("", encoding="utf-8")
print(f"Built {SITE} with {len(files)} Python modules")
