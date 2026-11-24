import tomllib
from pathlib import Path

from sachet.capimport import cap_to_case_toml
from sachet.faithfulness import check_faithfulness

SAMPLE = Path(__file__).parent / "data" / "sample-cap.xml"


def test_cap_import_makes_a_valid_case():
    case = tomllib.loads(cap_to_case_toml(SAMPLE))
    assert case["id"] == "sample-cap" and case["language"] == "ne"
    assert "११ मिटर" in case["source"] and case["source_url"] == "https://example.gov.np/a"
    systems = [c["system"] for c in case["candidates"]]
    assert "cap-en (in the same alert)" in systems and "gati:summary160 ne-np" in systems


def test_english_block_from_cap_is_faithful_to_nepali_source():
    case = tomllib.loads(cap_to_case_toml(SAMPLE))
    en = next(c["text"] for c in case["candidates"] if c["system"].startswith("cap-en"))
    assert check_faithfulness(case["source"], en).passed


def test_may_add_allows_an_added_ad_date():
    src = "मंसिर १ बिहान ८:४० बजे"
    out = "Mangsir 1 / 17 Nov, 8:40 AM"
    assert not check_faithfulness(src, out).passed            # "17" looks invented...
    assert check_faithfulness(src, out, may_add=["17"]).passed  # ...unless declared as an allowed addition
