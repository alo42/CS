"""English language data used to judge a candidate decryption.

Two things are needed to break a monoalphabetic cipher automatically:

  * a table of letter frequencies, to build a sensible starting key;
  * a way to tell English from gibberish, to steer the search.

The frequency table is the one printed in the laboratory work (table 2.2).
The language model is built at run time from the system word list, which
gives both a set of real English words and letter-pair statistics.
"""

import math
import os

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

# Table 2.2 of the laboratory work - frequency of the letters of English, in %.
ENGLISH_FREQUENCIES = {
    "a": 8.17, "b": 1.49, "c": 2.78, "d": 4.25, "e": 12.70, "f": 2.23,
    "g": 2.01, "h": 6.09, "i": 6.97, "j": 0.15, "k": 0.77, "l": 4.03,
    "m": 2.41, "n": 6.75, "o": 7.51, "p": 1.93, "q": 0.09, "r": 5.99,
    "s": 6.33, "t": 9.06, "u": 2.76, "v": 0.98, "w": 2.36, "x": 0.15,
    "y": 1.97, "z": 0.07,
}

# Letters in decreasing order of frequency: E, T, A, O, I, N, ...
ENGLISH_BY_FREQUENCY = sorted(
    ALPHABET, key=lambda letter: ENGLISH_FREQUENCIES[letter], reverse=True
)

WORD_LIST_PATHS = (
    os.environ.get("ENGLISH_WORD_LIST", ""),
    "/usr/share/dict/words",
    "/usr/dict/words",
    "/usr/share/dict/web2",
)


class WordListMissing(RuntimeError):
    """Raised when no system word list could be found."""


def word_list_path():
    """Return the first word list that exists on this machine."""
    for path in WORD_LIST_PATHS:
        if path and os.path.exists(path):
            return path
    raise WordListMissing(
        "no English word list found; looked in %s. Set the environment "
        "variable ENGLISH_WORD_LIST to the path of one."
        % ", ".join(p for p in WORD_LIST_PATHS if p)
    )


_WORDS_CACHE = None


def load_words():
    """Load the English words, lowercased, as a frozen set."""
    global _WORDS_CACHE
    if _WORDS_CACHE is None:
        with open(word_list_path(), encoding="utf-8", errors="ignore") as handle:
            _WORDS_CACHE = frozenset(
                word for word in (line.strip().lower() for line in handle)
                if word.isalpha() and word.isascii()
            )
    return _WORDS_CACHE


_BIGRAMS_CACHE = None


def bigram_log_probabilities():
    """Log-probabilities of letter pairs, estimated from the word list.

    `_` marks the start and the end of a word, so that pairs such as `_t`
    (a word starting with T) and `e_` (a word ending in E) are modelled too.
    Unseen pairs get a floor value instead of minus infinity, so that one
    impossible pair does not wipe out an otherwise good candidate.
    """
    global _BIGRAMS_CACHE
    if _BIGRAMS_CACHE is not None:
        return _BIGRAMS_CACHE

    counts = {}
    total = 0
    for word in load_words():
        padded = "_" + word + "_"
        for index in range(len(padded) - 1):
            pair = padded[index:index + 2]
            counts[pair] = counts.get(pair, 0) + 1
            total += 1

    floor = math.log(0.01 / total)
    model = {pair: math.log(count / total) for pair, count in counts.items()}
    model["__floor__"] = floor
    _BIGRAMS_CACHE = model
    return model
