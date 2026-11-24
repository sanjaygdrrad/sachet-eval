from pathlib import Path

from sachet.cases import load_case
from sachet.integrity import check_integrity

REAL = Path(__file__).resolve().parents[1] / "cases" / "real"


def test_text_copied_from_the_legacy_font_pdf_is_flagged():
    raw = (REAL / "dhm-flood-bulletin-2078-05-29.raw.txt").read_text(encoding="utf-8")
    r = check_integrity(raw)
    assert r.corrupted and len(r.orphans) >= 10
    assert any(o.startswith("ि") for o in r.orphans)   # e.g. "िव" from "विज्ञान"


def test_clean_reconstruction_is_intact():
    case = load_case(REAL / "dhm-flood-bulletin-2078-05-29.toml")
    r = check_integrity(case.source)
    assert not r.corrupted and r.orphans == []


def test_ordinary_nepali_with_conjuncts_and_danda_is_intact():
    assert not check_integrity("जल तथा मौसम विज्ञान विभाग। सतर्कता तह भन्दा तल। (स्रोत)").orphans


def test_english_text_has_no_devanagari_words():
    assert check_integrity("Flood notice: rivers are normal.").words == 0
