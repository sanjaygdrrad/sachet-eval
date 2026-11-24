from pathlib import Path

from sachet.cases import Case, load_case, provenance
from sachet.report import evaluate

REAL = Path(__file__).resolve().parents[1] / "cases" / "real"


def test_sms_profile_needs_place_status_action_but_not_numbers():
    case = load_case(REAL / "gati" / "ndrrma-narayani-2026-09-27.toml")
    good_sms = "नारायणी खतराको तह पार: चितवन, नवलपरासी पूर्व र पश्चिम। तुरुन्त उच्च स्थानमा जानुहोस्, किनारबाट टाढा रहनुहोस्।"
    row = evaluate(case, good_sms.replace("नवलपरासी पूर्व र पश्चिम", "नवलपरासी पूर्व, नवलपरासी पश्चिम"), channel="sms")
    assert row.passed, (row.result.missing, row.meaning.missing)


def test_sms_with_wrong_number_still_fails():
    case = load_case(REAL / "gati" / "ndrrma-narayani-2026-09-27.toml")
    row = evaluate(case, "नारायणी ९ मिटर, खतराको तह पार: चितवन, नवलपरासी पूर्व, नवलपरासी पश्चिम। उच्च स्थानमा जानुहोस्, टाढा रहनुहोस्।", channel="sms")
    assert not row.passed and "9" in row.result.invented


def test_full_script_flipping_above_to_below_fails():
    case = load_case(REAL / "gati" / "ndrrma-narayani-2026-09-27.toml")
    en = next(c.text for c in case.candidates if c.system.startswith("cap-en"))
    row = evaluate(case, en.replace("has crossed the danger level", "is below the danger level"))
    assert not row.passed and row.meaning.contradicted


def test_provenance_labels():
    assert provenance(Case(id="a", language="ne", source="x", source_url="https://bipadportal.gov.np/")) == "official"
    assert provenance(Case(id="b", language="ne", source="x", source_url="https://bipadportal.gov.np/", relayed_by="Gati")) == "relayed from official (by Gati)"
    assert provenance(Case(id="c", language="ne", source="x", source_url="https://example.com/news")) == "unverified source"
