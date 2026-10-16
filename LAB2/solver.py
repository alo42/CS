"""Automatic recovery of a monoalphabetic key by hill climbing.

The manual attack of the laboratory work - match frequencies, guess a word,
substitute, look at what appears - is exactly what this does mechanically:

  1. start from the key that matches the two frequency orders (the first
     step of the manual attack);
  2. score the decryption: how much does it look like English?
  3. swap two plaintext letters of the key; keep the swap if the score
     improves, undo it otherwise;
  4. repeat until no swap helps, and restart from a shuffled key several
     times so a local maximum cannot trap the search.

The score combines two signals, because neither alone is enough: letter
pair statistics give a smooth gradient while the text is still gibberish,
and the count of real English words sharpens the final steps.
"""

import random

import frequency
from english import ALPHABET, ENGLISH_BY_FREQUENCY, bigram_log_probabilities, load_words
from substitution import decrypt


def starting_key(ciphertext):
    """Match the most frequent ciphertext letter to E, the next to T, ...

    This is the opening move of the manual attack described in section 2.3.
    """
    cipher_order = frequency.by_frequency(ciphertext)
    return dict(zip(cipher_order, ENGLISH_BY_FREQUENCY))


class Scorer:
    """Judges how English a candidate decryption looks."""

    def __init__(self, ciphertext, word_weight=12.0):
        self.words = frequency.words(ciphertext)
        self.bigrams = bigram_log_probabilities()
        self.floor = self.bigrams["__floor__"]
        self.dictionary = load_words()
        self.word_weight = word_weight
        self.letter_total = sum(len(word) for word in self.words) or 1

    def score(self, key):
        table = str.maketrans("".join(ALPHABET), "".join(key[c] for c in ALPHABET))
        bigram_total = 0.0
        word_total = 0.0
        for word in self.words:
            plain = word.translate(table)
            padded = "_" + plain + "_"
            for index in range(len(padded) - 1):
                bigram_total += self.bigrams.get(padded[index:index + 2], self.floor)
            if plain in self.dictionary:
                # Longer words matching is much stronger evidence than
                # short ones, which match almost by accident.
                word_total += len(plain) ** 2
        return bigram_total / self.letter_total + self.word_weight * word_total / self.letter_total


def _climb(key, scorer, rng):
    """Swap plaintext letters until no single swap improves the score."""
    best = dict(key)
    best_score = scorer.score(best)
    letters = list(ALPHABET)
    improved = True
    while improved:
        improved = False
        pairs = [(a, b) for i, a in enumerate(letters) for b in letters[i + 1:]]
        rng.shuffle(pairs)
        for first, second in pairs:
            candidate = dict(best)
            candidate[first], candidate[second] = best[second], best[first]
            candidate_score = scorer.score(candidate)
            if candidate_score > best_score:
                best, best_score = candidate, candidate_score
                improved = True
    return best, best_score


def solve(ciphertext, restarts=12, seed=20242, on_restart=None):
    """Recover the key. Returns (key, score, plaintext)."""
    rng = random.Random(seed)
    scorer = Scorer(ciphertext)

    best_key, best_score = _climb(starting_key(ciphertext), scorer, rng)
    if on_restart:
        on_restart(0, best_score, decrypt(ciphertext, best_key))

    for attempt in range(1, restarts):
        shuffled = list(ALPHABET)
        rng.shuffle(shuffled)
        key, score = _climb(dict(zip(ALPHABET, shuffled)), scorer, rng)
        if score > best_score:
            best_key, best_score = key, score
        if on_restart:
            on_restart(attempt, best_score, decrypt(ciphertext, best_key))

    return best_key, best_score, decrypt(ciphertext, best_key)
