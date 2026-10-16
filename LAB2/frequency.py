"""Frequency analysis of a ciphertext.

Everything the cryptanalyst looks at before guessing anything: how often
each letter occurs, which pairs and triples repeat, and which short words
appear - the "personality traits" of the letters the laboratory work talks
about.
"""

import re
from collections import Counter

from english import ALPHABET, ENGLISH_FREQUENCIES


def letters_only(text):
    """The letters of the text, lowercased, with everything else dropped."""
    return [char.lower() for char in text if char.isalpha()]


def letter_counts(text):
    """How many times each letter of the alphabet occurs."""
    counts = Counter(letters_only(text))
    return {letter: counts.get(letter, 0) for letter in ALPHABET}


def letter_percentages(text):
    """The same, as a percentage of all the letters in the text."""
    counts = letter_counts(text)
    total = sum(counts.values()) or 1
    return {letter: 100.0 * count / total for letter, count in counts.items()}


def by_frequency(text):
    """Letters ordered from the most to the least frequent."""
    percentages = letter_percentages(text)
    return sorted(ALPHABET, key=lambda letter: (-percentages[letter], letter))


def ngrams(text, size, top=None):
    """The most common sequences of `size` letters, within words."""
    counts = Counter()
    for word in words(text):
        for index in range(len(word) - size + 1):
            counts[word[index:index + size]] += 1
    common = counts.most_common(top)
    return common


def words(text):
    """The words of the text, lowercased, letters only."""
    return re.findall(r"[a-z]+", text.lower())


def word_counts(text, length=None, top=None):
    """The most common whole words, optionally of one given length."""
    found = words(text)
    if length is not None:
        found = [word for word in found if len(word) == length]
    return Counter(found).most_common(top)


def pattern(word):
    """The repetition pattern of a word, e.g. `wqvw` -> `ABCA`.

    Two words share a pattern exactly when one could be the encryption of
    the other, which is what makes short repeated words so useful.
    """
    seen = {}
    out = []
    for letter in word:
        if letter not in seen:
            seen[letter] = ALPHABET[len(seen)].upper()
        out.append(seen[letter])
    return "".join(out)


def doubles(text, top=None):
    """Doubled letters (SS, EE, TT, OO, FF are the common ones in English)."""
    counts = Counter()
    for word in words(text):
        for index in range(len(word) - 1):
            if word[index] == word[index + 1]:
                counts[word[index] * 2] += 1
    return counts.most_common(top)


def comparison_table(text):
    """Rows of (cipher letter, its %, English letter of the same rank, its %).

    Lining the two orders up like this is the first step of the attack
    described in the laboratory work.
    """
    percentages = letter_percentages(text)
    cipher_order = by_frequency(text)
    english_order = sorted(
        ALPHABET, key=lambda letter: -ENGLISH_FREQUENCIES[letter]
    )
    rows = []
    for rank, cipher_letter in enumerate(cipher_order):
        english_letter = english_order[rank]
        rows.append((
            cipher_letter.upper(),
            percentages[cipher_letter],
            english_letter,
            ENGLISH_FREQUENCIES[english_letter],
        ))
    return rows
