import math
from collections import Counter
from typing import Tuple, Dict
from .models import LexicalMetrics

SCRABBLE_TILE_VALUES: Dict[str, int] = {
    **{c: 1 for c in "EAIONRTLSU"},
    **{c: 2 for c in "DG"},
    **{c: 3 for c in "BCMP"},
    **{c: 4 for c in "FHVWY"},
    **{c: 5 for c in "K"},
    **{c: 8 for c in "JX"},
    **{c: 10 for c in "QZ"},
}


def calculate_shannon_entropy(text: str) -> float:
    """Computes exact Shannon entropy: H(X) = -sum(P(x) * log2(P(x)))."""
    if not text:
        return 0.0
    text_clean = text.lower()
    length = len(text_clean)
    counts = Counter(text_clean)
    entropy = -sum((count / length) * math.log2(count / length) for count in counts.values())
    return round(entropy, 4)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes the standard Levenshtein edit distance between two strings."""
    s1, s2 = s1.lower(), s2.lower()
    m, n = len(s1), len(s2)
    if m < n:
        return levenshtein_distance(s2, s1)
    if n == 0:
        return m

    previous_row = list(range(n + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1] + [0] * n
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row[j + 1] = min(insertions, deletions, substitutions)
        previous_row = current_row

    return previous_row[n]


def normalized_similarity(s1: str, s2: str) -> float:
    """Calculates 1 - (dist / max(len1, len2)). Returns 1.0 for exact matches."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return round(1.0 - (dist / max_len), 4)


def calculate_scrabble_score(word: str) -> int:
    """Calculates official English tournament Scrabble score for a word."""
    return sum(SCRABBLE_TILE_VALUES.get(char.upper(), 0) for char in word if char.isalpha())


def compute_all_metrics(word: str) -> LexicalMetrics:
    """Produces the complete lexical metrics suite for a string."""
    word_clean = word.lower()
    vowels = set("aeiou")
    freq = dict(Counter(word_clean))
    vowel_count = sum(freq.get(v, 0) for v in vowels)
    consonant_count = sum(freq.get(c, 0) for c in freq if c.isalpha() and c not in vowels)

    return LexicalMetrics(
        length=len(word),
        shannon_entropy=calculate_shannon_entropy(word),
        scrabble_score=calculate_scrabble_score(word),
        char_frequencies=freq,
        vowel_count=vowel_count,
        consonant_count=consonant_count,
    )
