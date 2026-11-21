import pytest

from sachet.wer import word_error_rate


def test_identical_is_zero_ignoring_punctuation_and_danda():
    assert word_error_rate("पानीको सतह बढेको छ।", "पानीको सतह बढेको छ") == 0.0


def test_one_substitution_in_four_nepali_words():
    # regression: Devanagari vowel signs must not split words
    assert word_error_rate("पानीको सतह बढेको छ।", "पानीको सतह बढ्यो छ") == pytest.approx(0.25)


def test_deletion_and_insertion():
    assert word_error_rate("move to high ground now", "move to ground now please") == pytest.approx(0.4)


def test_empty_reference():
    assert word_error_rate("", "") == 0.0 and word_error_rate("", "x") == 1.0
