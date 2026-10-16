"""Checks for Laboratory Work No. 2.

Run from the LAB2 directory with:  python3 -m unittest discover -s tests
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import frequency
import solver
import substitution
import walkthrough
from english import ALPHABET
from main import RECOVERED_KEY

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIPHERTEXT = open(os.path.join(HERE, "ciphertext.txt"), encoding="utf-8").read()


class TestSubstitution(unittest.TestCase):
    def test_key_round_trips_through_its_string_form(self):
        key = substitution.key_from_string(RECOVERED_KEY)
        self.assertEqual(substitution.key_to_string(key), RECOVERED_KEY)

    def test_recovered_key_is_one_to_one(self):
        key = substitution.key_from_string(RECOVERED_KEY)
        self.assertEqual(len(key), 26)
        self.assertEqual(sorted(key.values()), sorted(ALPHABET))
        self.assertEqual(substitution.conflicts(key), {})

    def test_only_letters_are_substituted(self):
        key = substitution.key_from_string(RECOVERED_KEY)
        plain = substitution.decrypt(CIPHERTEXT, key)
        self.assertEqual(len(plain), len(CIPHERTEXT))
        for original, decrypted in zip(CIPHERTEXT, plain):
            if not original.isalpha():
                self.assertEqual(original, decrypted)

    def test_capitalisation_is_preserved(self):
        key = substitution.key_from_string(RECOVERED_KEY)
        plain = substitution.decrypt(CIPHERTEXT, key)
        for original, decrypted in zip(CIPHERTEXT, plain):
            if original.isalpha():
                self.assertEqual(original.isupper(), decrypted.isupper())

    def test_partial_decrypt_marks_what_is_still_unknown(self):
        key = {"w": "t", "q": "h", "v": "e"}
        self.assertEqual(substitution.partial_decrypt("WQV ZTOV", key), "the ZTOe")


class TestFrequency(unittest.TestCase):
    def test_pattern_detects_repeated_letters(self):
        self.assertEqual(frequency.pattern("wqvw"), "ABCA")
        self.assertEqual(frequency.pattern("abc"), "ABC")
        self.assertEqual(frequency.pattern("aabb"), "AABB")

    def test_cipher_words_and_plain_words_share_a_pattern(self):
        # A substitution cannot change the shape of a word.
        self.assertEqual(frequency.pattern("wqv"), frequency.pattern("the"))
        self.assertEqual(frequency.pattern("xzunppxaxsxwf"),
                         frequency.pattern("impossibility"))

    def test_the_most_frequent_letter_is_v(self):
        self.assertEqual(frequency.by_frequency(CIPHERTEXT)[0], "v")

    def test_the_most_frequent_three_letter_word_is_wqv(self):
        self.assertEqual(frequency.word_counts(CIPHERTEXT, length=3, top=1),
                         [("wqv", 43)])


class TestWalkthrough(unittest.TestCase):
    def test_each_stage_has_a_title_and_an_explanation(self):
        for _, title, explanation, _ in walkthrough.replay():
            self.assertTrue(title and explanation)

    def test_every_stage_only_adds_letters(self):
        previous = {}
        for _, _, _, key in walkthrough.replay():
            for letter, plain in previous.items():
                self.assertEqual(key[letter], plain)
            previous = key

    def test_the_stages_end_at_the_recovered_key(self):
        final = list(walkthrough.replay())[-1][3]
        self.assertEqual(substitution.key_to_string(final), RECOVERED_KEY)


class TestSolver(unittest.TestCase):
    def test_starting_key_maps_the_commonest_letter_to_e(self):
        self.assertEqual(solver.starting_key(CIPHERTEXT)["v"], "e")

    def test_solver_recovers_the_key_of_variant_15(self):
        key, _, _ = solver.solve(CIPHERTEXT, restarts=4)
        self.assertEqual(substitution.key_to_string(key), RECOVERED_KEY)

    def test_solver_recovers_a_key_it_has_never_seen(self):
        # Encrypt a known English text with a random key and break it again.
        plain = substitution.decrypt(
            CIPHERTEXT, substitution.key_from_string(RECOVERED_KEY)
        )
        rng = random.Random(7)
        shuffled = list(ALPHABET)
        rng.shuffle(shuffled)
        encrypt_key = dict(zip(ALPHABET, shuffled))
        cipher = substitution.decrypt(plain, encrypt_key)
        recovered, _, cracked = solver.solve(cipher, restarts=4)
        self.assertEqual(cracked.lower(), plain.lower())


class TestPlaintext(unittest.TestCase):
    def test_plaintext_is_recognisable_english(self):
        plain = substitution.decrypt(
            CIPHERTEXT, substitution.key_from_string(RECOVERED_KEY)
        ).lower()
        for phrase in ["the telegraph", "cryptography", "cryptanalysts",
                       "vigenere", "thomas jefferson", "wheel cypher"]:
            self.assertIn(phrase, plain)

    def test_recovered_key_is_an_affine_cipher(self):
        # Encryption turns out to be c = (7x + 19) mod 26 - a useful check
        # that the key is right, since a wrong key would show no structure.
        key = substitution.key_from_string(RECOVERED_KEY)
        encrypt = {plain: cipher for cipher, plain in key.items()}
        for index, plain_letter in enumerate(ALPHABET):
            expected = ALPHABET[(7 * index + 19) % 26]
            self.assertEqual(encrypt[plain_letter], expected)


if __name__ == "__main__":
    unittest.main()
