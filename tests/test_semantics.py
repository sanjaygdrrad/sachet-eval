from sachet.semantics import compare_meaning, extract_meaning


def test_reads_status_and_above_below_in_nepali_and_english():
    assert extract_meaning("नारायणी नदी खतराको तह पार गरेको छ").statuses == {"danger level": {"above"}}
    assert extract_meaning("The river is below the warning level.").statuses == {"warning level": {"below"}}


def test_flipped_above_below_is_flagged_as_contradiction():
    r = compare_meaning("नारायणी नदी खतराको तह पार गरेको छ", "The Narayani is below the danger level")
    assert r.contradicted == ["danger level: source says above, rewrite says below"]


def test_flipped_trend_is_flagged():
    r = compare_meaning("River above its warning level, rising.", "River above warning level, falling.")
    assert "trend: source says rising, rewrite says falling" in r.contradicted


def test_dropped_action_is_missing():
    r = compare_meaning("तुरुन्त उच्च तथा सुरक्षित स्थानमा जानुहोस्।", "नदी खतराको तह पार")
    assert "action: move to high ground" in r.missing


def test_hotline_label_is_not_a_flood_statement():
    assert extract_meaning("बाढी सूचना: ११५५").hazards == set()
    assert extract_meaning("flood information: 1155").hazards == set()


def test_normal_does_not_block_above_below_pairing():
    m = extract_meaning("बहाव सामान्य तथा सतर्कता तह भन्दा तलै रहेको छ।")
    assert m.statuses["warning level"] == {"below"} and "normal" in m.statuses


def test_residents_of_riverbank_is_not_an_instruction():
    assert "keep away from the river" not in extract_meaning("नदी किनारका बासिन्दाहरूलाई सूचना").actions


def test_decimal_numbers_do_not_split_clauses():
    m = extract_meaning("Level is above the danger level of 6.8 m.")
    assert m.statuses == {"danger level": {"above"}}
