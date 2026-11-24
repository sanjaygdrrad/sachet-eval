import json
from pathlib import Path

from sachet.cli import main

EXAMPLES = str(Path(__file__).resolve().parents[1] / "cases" / "examples")


def test_markdown_report_lists_every_candidate(capsys):
    assert main(["eval", EXAMPLES]) == 0
    out = capsys.readouterr().out
    assert "2 of 4" in out and "example-unsafe" in out and "8.6" in out


def test_strict_mode_fails_when_any_candidate_fails(capsys):
    assert main(["eval", EXAMPLES, "--strict"]) == 1


def test_json_output(capsys, tmp_path):
    out_file = tmp_path / "r.json"
    main(["eval", EXAMPLES, "--json", "--out", str(out_file)])
    rows = json.loads(out_file.read_text(encoding="utf-8"))
    assert {r["system"] for r in rows} >= {"example-faithful", "example-unsafe"}
    assert all(set(r) >= {"case", "score", "passed", "missing", "invented"} for r in rows)


def test_lint_flags_the_corrupted_pdf_copy(capsys):
    raw = str(Path(EXAMPLES).parents[0] / "real" / "dhm-flood-bulletin-2078-05-29.raw.txt")
    assert main(["lint", raw]) == 1
    assert "likely corrupted" in capsys.readouterr().out


def test_wrong_folder_gives_a_clear_one_line_error(capsys, tmp_path):
    assert main(["eval", str(tmp_path / "nope")]) == 2
    err = capsys.readouterr().err
    assert "not found" in err and "Traceback" not in err


def test_lint_missing_file_gives_a_clear_error(capsys, tmp_path):
    assert main(["lint", str(tmp_path / "nope.txt")]) == 2
    assert "file not found" in capsys.readouterr().err
