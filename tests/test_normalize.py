from sachet.normalize import canonical_number, normalize


def test_devanagari_digits_become_latin():
    assert normalize("सतह ६.८ मिटर") == "सतह 6.8 मिटर"


def test_nepali_and_western_grouping_removed():
    assert normalize("1,00,000 and 12,500") == "100000 and 12500"


def test_decimal_comma_is_not_treated_as_grouping():
    assert normalize("6,8") == "6,8"


def test_zero_width_joiners_removed_and_spaces_collapsed():
    assert normalize("नेपा‍ल   Nepal") == "नेपाल nepal"


def test_canonical_number():
    assert canonical_number("06.50") == "6.5"
    assert canonical_number("007") == "7"
    assert canonical_number("0.0") == "0"
    assert canonical_number("1,149") == "1149"
