"""Sorting in North Sámi alphabetical order, for the scripts in this folder.

a á b c č d đ e f g h i j k l m n ŋ o p r s š t ŧ u v z ž, then æ/ä ø/ö å
as in Nordic dictionaries. Case is ignored. Spaces, hyphens and other
characters that are not letters only count when two words are otherwise
equal. Letters not in the alphabet sort after it.
"""

import unicodedata

ALPHABET = [
    "a",
    "á",
    "b",
    "c",
    "č",
    "d",
    "đ",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "ŋ",
    "o",
    "p",
    "r",
    "s",
    "š",
    "t",
    "ŧ",
    "u",
    "v",
    "z",
    "ž",
    "æä",
    "øö",
    "å",
]
RANK = {c: n for n, letters in enumerate(ALPHABET) for c in letters}


def _rank(c):
    if c in RANK:
        return RANK[c]
    # other accented letters (é, ï, ...) sort as their base letter
    base = unicodedata.normalize("NFD", c)[0]
    return RANK.get(base, len(ALPHABET) + ord(c))


def sort_key(word):
    word = unicodedata.normalize("NFC", word.lower())
    letters = [c for c in word if c.isalpha()]
    return ([_rank(c) for c in letters], word)
