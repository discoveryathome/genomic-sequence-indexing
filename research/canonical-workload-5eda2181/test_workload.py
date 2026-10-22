"""Small explicit semantic controls, separate from the exposed corpus replay."""
from collections import Counter
from itertools import product
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workload import windows
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from trial import oracle


def test_overlap_order_canonicalization_and_repeats():
    assert list(windows(["AAATTT"], 3)) == [
        (0, 0, "AAA"), (0, 1, "AAT"), (0, 2, "AAT"), (0, 3, "AAA")]


def test_invalid_windows_and_record_boundaries():
    assert list(windows(["AAANAAA", "AA", "A", "aaaxaaa"], 3)) == [
        (0, 0, "AAA"), (0, 4, "AAA"), (3, 0, "AAA"), (3, 4, "AAA")]
    # The adapter drops N windows; the project still treats N literally.
    assert list(windows(["NAN"], 3)) == []
    assert oracle(["NAN"], "NAN") == 1


@pytest.mark.parametrize("k", [1, 3, 5])
def test_odd_k_counts_match_both_strands_exhaustively(k):
    records = ["AAAATTTTCGTANACGTACGT", "ACG", "TTTAAA", "N"]
    counts = Counter(word for _, _, word in windows(records, k))
    for letters in product("ACGT", repeat=k):
        word = "".join(letters)
        reverse = word.translate(str.maketrans("ACGT", "TGCA"))[::-1]
        assert word != reverse
        assert counts[min(word, reverse)] == oracle(records, word)


def test_even_palindrome_is_explicitly_incompatible():
    assert list(windows(["AT"], 2)) == [(0, 0, "AT")]
    assert oracle(["AT"], "AT") == 2


@pytest.mark.parametrize("k", [0, -1, True, 1.5])
def test_reject_invalid_k(k):
    with pytest.raises(ValueError, match="positive integer"):
        list(windows(["ACGT"], k))
