from sachet.faithfulness import check_faithfulness

SOURCE = "नारायणी नदीको देवघाटमा सतह ६.८ मिटर, खतराको तह ६.५ मिटर। साँझ ७:०० बजेसम्म।"
PLACES = [["नारायणी", "Narayani"], ["देवघाट", "Devghat"]]


def test_faithful_rewrite_passes_even_with_latin_digits():
    r = check_faithfulness(SOURCE, "Narayani at Devghat: 6.8 m, danger level 6.5 m, until 7:00 pm.", PLACES)
    assert r.passed and r.score == 1.0


def test_swapped_number_is_missing_and_invented():
    r = check_faithfulness(SOURCE, "नारायणी देवघाट: ८.६ मिटर, खतरा ६.५ मिटर, ७:०० बजे", PLACES)
    assert not r.passed
    assert "6.8" in r.missing and "8.6" in r.invented


def test_invented_time_fails():
    r = check_faithfulness(SOURCE, "नारायणी देवघाट ६.८ ६.५ ७:०० र ९:०० बजे", PLACES)
    assert "9:00 (time)" in r.invented and not r.passed


def test_dropped_place_fails_but_alias_counts():
    assert not check_faithfulness(SOURCE, "नारायणी ६.८ ६.५ ७:००", PLACES).passed
    assert check_faithfulness(SOURCE, "Narayani, Devghat ६.८ ६.५ ७:००", PLACES).passed


def test_may_drop_allows_omission_but_not_change():
    src = "120 mm of rain in 24 hours"
    assert check_faithfulness(src, "120 mm of rain", may_drop=["24"]).passed
    changed = check_faithfulness(src, "120 mm of rain in 12 hours", may_drop=["24"])
    assert not changed.passed and "12" in changed.invented


def test_no_facts_means_full_score():
    assert check_faithfulness("Stay safe.", "Stay safe!").score == 1.0
