import tomllib

from sachet.portal import case_toml, check, parse_names

NARAYANI = ("नारायणी नदी खतराको तह पार गरेको छ। NDRRMA, असोज ११ बिहान ८ बजे: हालको स्तर ११ मिटर (खतराको तह ११ मिटर); "
            "अपेक्षित उच्चतम करिब १३.० मिटर। स्थान: चितवन, नवलपरासी पूर्व, नवलपरासी पश्चिम। तुरुन्त उच्च तथा सुरक्षित स्थानमा जानुहोस्।")


def test_parse_names_with_aliases_and_separators():
    assert parse_names("नारायणी / Narayani, चितवन | Chitwan\nदेवघाट") == [["नारायणी", "Narayani"], ["चितवन", "Chitwan"], ["देवघाट"]]


def test_requires_both_texts():
    assert check("", "x")["ok"] is False


def test_faithful_full_script_passes():
    en = ("The Narayani River has crossed the danger level. NDRRMA, Asoj 11, 8 AM: current level 11 m (danger level 11 m); "
          "expected peak about 13.0 m. Areas: Chitwan, Nawalparasi East and Nawalparasi West. Move to high, safe ground now.")
    r = check(NARAYANI, en, "full", "नारायणी / Narayani, चितवन / Chitwan")
    assert r["ok"] and r["passed"], r


def test_flipped_meaning_is_reported():
    r = check(NARAYANI, "The Narayani is below the danger level at 11 m, peak 13 m, Asoj 11, 8 AM. Move to high ground.", "full")
    assert not r["passed"] and r["meaning"]["flipped"]


def test_sms_needs_names_and_action_not_numbers():
    sms = "नारायणी खतराको तह पार: चितवन। तुरुन्त उच्च स्थानमा जानुहोस्।"
    assert check(NARAYANI, sms, "sms", "नारायणी / Narayani, चितवन / Chitwan")["passed"]
    assert not check(NARAYANI, "नारायणी खतराको तह पार।", "sms", "नारायणी, चितवन")["passed"]


def test_reports_corrupted_source_text():
    r = check("जल तथा मौसम िव ान िवभाग। जल ोत। िसंचाई म ालय", "x", "full")
    assert r["source_integrity"]["corrupted"]


def test_contributed_case_toml_is_valid():
    data = tomllib.loads(case_toml(NARAYANI, 'Say "hi" """ test', "sms", "नारायणी / Narayani"))
    assert data["must_keep"] == [["नारायणी", "Narayani"]] and data["candidates"][0]["channel"] == "sms"
