from sachet.facts import Fact, extract_facts


def test_extracts_dates_times_numbers_without_double_counting():
    facts = extract_facts("सतह ६.८ मिटर, साँझ ७:०० बजे, मिति २०८१-०५-१२")
    assert facts == {Fact("number", "6.8"): 1, Fact("time", "7:00"): 1, Fact("date", "2081-5-12"): 1}


def test_day_first_date_format():
    assert Fact("date", "2081-5-12") in extract_facts("12/05/2081")


def test_same_value_in_different_scripts_is_equal():
    assert extract_facts("६.५ मिटर") == extract_facts("6.50 m")


def test_counts_repeated_numbers():
    assert extract_facts("42 then 42")[Fact("number", "42")] == 2
