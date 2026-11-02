import pytest
from lexical_hub.lexical_math import (
    calculate_shannon_entropy,
    levenshtein_distance,
    normalized_similarity,
    calculate_scrabble_score,
    compute_all_metrics,
)


def test_shannon_entropy_identical_characters():
    assert calculate_shannon_entropy("aaaa") == 0.0


def test_shannon_entropy_calculation():
    # 'ab' has 2 symbols, p=0.5 each -> -2 * (0.5 * log2(0.5)) = 1.0
    assert calculate_shannon_entropy("ab") == 1.0


def test_levenshtein_identical():
    assert levenshtein_distance("kitten", "kitten") == 0
    assert normalized_similarity("kitten", "kitten") == 1.0


def test_levenshtein_known_distance():
    # kitten -> sitting: k->s, e->i, +g = 3 edits
    assert levenshtein_distance("kitten", "sitting") == 3
    assert normalized_similarity("kitten", "sitting") == pytest.approx(1.0 - (3 / 7), 0.001)


def test_scrabble_scoring():
    # Q(10) + U(1) + I(1) + Z(10) = 22
    assert calculate_scrabble_score("QUIZ") == 22
    assert calculate_scrabble_score("quiz") == 22


def test_compute_all_metrics():
    metrics = compute_all_metrics("hello")
    assert metrics.length == 5
    assert metrics.scrabble_score == 8  # H(4)+E(1)+L(1)+L(1)+O(1)
    assert metrics.vowel_count == 2
    assert metrics.consonant_count == 3
    assert metrics.char_frequencies["l"] == 2
