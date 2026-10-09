"""Checks for Laboratory Work No. 1.

Run from the repository root with:  python3 -m unittest discover -s tests

The English test vectors are the examples worked out by hand in the
laboratory work itself, which is why the cipher functions accept the ordered
alphabet as a parameter: the same code is checked against the text of the
assignment and then used on the 31 Romanian letters.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import caesar
from romanian_alphabet import (
    ALPHABET,
    N,
    InvalidCharacterError,
    InvalidKeyError,
    InvalidKeywordError,
    normalize_text,
    parse_key,
    parse_keyword,
)

ENGLISH = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class TestAlphabet(unittest.TestCase):
    def test_has_31_distinct_letters(self):
        self.assertEqual(N, 31)
        self.assertEqual(len(set(ALPHABET)), 31)

    def test_encoding_matches_table_2(self):
        for letter, code in [("A", 0), ("Ă", 1), ("Â", 2), ("B", 3), ("I", 10),
                             ("Î", 11), ("S", 21), ("Ș", 22), ("T", 23),
                             ("Ț", 24), ("Z", 30)]:
            self.assertEqual(ALPHABET.index(letter), code)


class TestNormalization(unittest.TestCase):
    def test_uppercases_and_drops_spaces(self):
        self.assertEqual(normalize_text("cifrul cezar"), "CIFRULCEZAR")

    def test_cedilla_variants_are_the_comma_below_letters(self):
        # Ş/Ţ (cedilla) must be accepted as Ș/Ț (comma below).
        self.assertEqual(normalize_text("Ş ş Ţ ţ"), "ȘȘȚȚ")

    def test_rejects_a_foreign_letter(self):
        with self.assertRaises(InvalidCharacterError) as raised:
            normalize_text("über")
        # The rejected character is reported exactly as it was typed, so the
        # message points at what the user actually has to change.
        self.assertEqual(raised.exception.character, "ü")
        self.assertEqual(raised.exception.position, 1)

    def test_rejects_digits_and_punctuation(self):
        for text in ["abc1", "salut!", "a-b"]:
            with self.assertRaises(InvalidCharacterError):
                normalize_text(text)


class TestKeyValidation(unittest.TestCase):
    def test_accepts_the_whole_allowed_range(self):
        for key in range(1, 31):
            self.assertEqual(parse_key(" %d " % key), key)

    def test_rejects_out_of_range_and_non_numeric(self):
        for raw in ["0", "31", "-3", "", "three", "3.5"]:
            with self.assertRaises(InvalidKeyError):
                parse_key(raw)

    def test_keyword_must_have_at_least_seven_letters(self):
        with self.assertRaises(InvalidKeywordError):
            parse_keyword("cripto")
        self.assertEqual(parse_keyword("criptare"), "CRIPTARE")

    def test_keyword_rejects_foreign_letters(self):
        with self.assertRaises(InvalidKeywordError):
            parse_keyword("cripto-grafie")


class TestPermutedAlphabet(unittest.TestCase):
    def test_reproduces_the_english_example_of_the_assignment(self):
        permuted = caesar.build_permuted_alphabet("CRYPTOGRAPHY", ENGLISH)
        self.assertEqual("".join(permuted), "CRYPTOGAHBDEFIJKLMNQSUVWXZ")

    def test_is_always_a_permutation_of_all_31_letters(self):
        for keyword in ["CRIPTOGRAFIE", "ȘTIINȚĂ", "ZZZZZZZ", "ABCDEFG"]:
            permuted = caesar.build_permuted_alphabet(keyword)
            self.assertEqual(len(permuted), N)
            self.assertEqual(sorted(permuted), sorted(ALPHABET))

    def test_keeps_only_the_first_occurrence_of_a_letter(self):
        permuted = caesar.build_permuted_alphabet("AAABBBCCC")
        self.assertEqual(permuted[:3], ("A", "B", "C"))


class TestCaesar(unittest.TestCase):
    def test_english_examples_of_the_assignment(self):
        self.assertEqual(caesar.encrypt("S", 3, ENGLISH), "V")
        self.assertEqual(caesar.decrypt("V", 3, ENGLISH), "S")
        self.assertEqual(caesar.encrypt("CIFRULCEZAR", 3, ENGLISH), "FLIUXOFHCDU")
        self.assertEqual(
            caesar.encrypt("BRUTEFORCEATTACK", 17, ENGLISH), "SILKVWFITVRKKRTB"
        )

    def test_romanian_alphabet(self):
        # C=4 -> 7=F, I=10 -> 13=K, ..., Z=30 -> (30+3) mod 31 = 2 = Â
        self.assertEqual(caesar.encrypt("CIFRULCEZAR", 3), "FKITXOFHÂBT")

    def test_wrap_around_uses_the_modulo(self):
        self.assertEqual(caesar.encrypt("Z", 1), "A")
        self.assertEqual(caesar.decrypt("A", 1), "Z")

    def test_round_trip_for_every_key(self):
        text = normalize_text("Aceasta este o propozitie in limba romana")
        for key in range(1, 31):
            self.assertEqual(caesar.decrypt(caesar.encrypt(text, key), key), text)


class TestCaesarWithKeyword(unittest.TestCase):
    def test_english_example_of_the_assignment(self):
        permuted = caesar.build_permuted_alphabet("CRYPTOGRAPHY", ENGLISH)
        self.assertEqual(caesar.encrypt("CIFRULCEZAR", 3, permuted), "PLKTXQPJYDT")

    def test_differs_from_the_plain_cipher(self):
        permuted = caesar.build_permuted_alphabet("CRIPTOGRAFIE")
        self.assertNotEqual(
            caesar.encrypt("CIFRULCEZAR", 3, permuted),
            caesar.encrypt("CIFRULCEZAR", 3),
        )

    def test_round_trip_for_every_key(self):
        permuted = caesar.build_permuted_alphabet(normalize_text("știință"))
        text = normalize_text("Șase țări în Europa")
        for key in range(1, 31):
            self.assertEqual(
                caesar.decrypt(caesar.encrypt(text, key, permuted), key, permuted),
                text,
            )


if __name__ == "__main__":
    unittest.main()
