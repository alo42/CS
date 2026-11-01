"""Checks for Laboratory Work No. 3, task 3.2.

Run from the LAB3 directory with:  python3 -m unittest discover -s tests

The English test vectors are the example worked out by hand in the laboratory
work itself, which is why the cipher functions accept the ordered alphabet as
a parameter: the same code is checked against the text of the assignment and
then used on the 31 Romanian letters.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vigenere
from romanian_alphabet import (
    ALPHABET,
    MIN_KEY_LENGTH,
    N,
    InvalidCharacterError,
    InvalidKeyError,
    normalize_text,
    parse_key,
)

ENGLISH = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class TestAlphabet(unittest.TestCase):
    def test_has_31_distinct_letters(self):
        self.assertEqual(N, 31)
        self.assertEqual(len(set(ALPHABET)), 31)

    def test_letters_are_coded_from_0_to_30(self):
        for letter, code in [("A", 0), ("Ă", 1), ("Â", 2), ("B", 3), ("I", 10),
                             ("Î", 11), ("S", 21), ("Ș", 22), ("T", 23),
                             ("Ț", 24), ("Z", 30)]:
            self.assertEqual(ALPHABET.index(letter), code)


class TestNormalization(unittest.TestCase):
    def test_uppercases_and_drops_spaces(self):
        self.assertEqual(normalize_text("cifrul vigenere"), "CIFRULVIGENERE")

    def test_cedilla_variants_are_the_comma_below_letters(self):
        self.assertEqual(normalize_text("Ş ş Ţ ţ"), "ȘȘȚȚ")

    def test_rejects_a_foreign_letter(self):
        with self.assertRaises(InvalidCharacterError) as raised:
            normalize_text("über")
        self.assertEqual(raised.exception.character, "ü")
        self.assertEqual(raised.exception.position, 1)

    def test_rejects_digits_and_punctuation(self):
        for text in ("abc123", "salut!", "a-b"):
            with self.assertRaises(InvalidCharacterError):
                normalize_text(text)

    def test_error_message_names_the_allowed_range(self):
        with self.assertRaises(InvalidCharacterError) as raised:
            normalize_text("7")
        self.assertIn("Romanian alphabet", str(raised.exception))
        self.assertIn("Z", str(raised.exception))


class TestKeyValidation(unittest.TestCase):
    def test_accepts_a_long_enough_keyword(self):
        self.assertEqual(parse_key("criptografie"), "CRIPTOGRAFIE")

    def test_accepts_exactly_the_minimum_length(self):
        key = parse_key("a" * MIN_KEY_LENGTH)
        self.assertEqual(len(key), MIN_KEY_LENGTH)

    def test_rejects_a_short_key(self):
        with self.assertRaises(InvalidKeyError):
            parse_key("super")

    def test_rejects_a_key_with_a_foreign_letter(self):
        with self.assertRaises(InvalidKeyError):
            parse_key("cheia-mea")

    def test_spaces_do_not_count_towards_the_length(self):
        # Six letters plus spaces is still six letters, hence too short.
        with self.assertRaises(InvalidKeyError):
            parse_key("c h e i a a")


class TestAssignmentExample(unittest.TestCase):
    """The example of the assignment: PERASPERAADASTRA with the key SUPER."""

    MESSAGE = "PERASPERAADASTRA"
    KEY = "SUPER"
    CRYPTOGRAM = "HYGEJHYGERVUHXIS"

    def test_encryption_matches_the_assignment(self):
        self.assertEqual(
            vigenere.encrypt(self.MESSAGE, self.KEY, ENGLISH), self.CRYPTOGRAM
        )

    def test_decryption_matches_the_assignment(self):
        self.assertEqual(
            vigenere.decrypt(self.CRYPTOGRAM, self.KEY, ENGLISH), self.MESSAGE
        )

    def test_the_codes_of_the_worked_table(self):
        rows = vigenere.steps(self.MESSAGE, self.KEY, "encrypt", ENGLISH)
        # First column of the table in the assignment: P(15) + S(18) = 7 -> H.
        self.assertEqual(rows[0], ("P", "S", 15, 18, 7, "H"))
        # Last column: A(0) + S(18) = 18 -> S.
        self.assertEqual(rows[-1], ("A", "S", 0, 18, 18, "S"))


class TestKeyStream(unittest.TestCase):
    def test_the_key_is_repeated_from_the_beginning(self):
        self.assertEqual(vigenere.key_stream("SUPER", 12), "SUPERSUPERSU")

    def test_a_key_longer_than_the_text_is_cut(self):
        self.assertEqual(vigenere.key_stream("SUPER", 3), "SUP")


class TestRomanianCipher(unittest.TestCase):
    KEY = "CRIPTOGRAFIE"

    def test_round_trip_on_a_romanian_message(self):
        message = normalize_text("Învață să ții secretele într o cheie")
        cryptogram = vigenere.encrypt(message, self.KEY)
        self.assertNotEqual(cryptogram, message)
        self.assertEqual(vigenere.decrypt(cryptogram, self.KEY), message)

    def test_round_trip_over_every_letter_of_the_alphabet(self):
        message = "".join(ALPHABET)
        cryptogram = vigenere.encrypt(message, self.KEY)
        self.assertEqual(vigenere.decrypt(cryptogram, self.KEY), message)

    def test_an_all_A_key_leaves_the_text_unchanged(self):
        # A has code 0, so every shift is 0 - the degenerate key.
        message = normalize_text("mesaj de proba")
        self.assertEqual(vigenere.encrypt(message, "AAAAAAA"), message)

    def test_the_same_letter_gets_different_cryptogram_letters(self):
        """The whole point of a polyalphabetic cipher."""
        cryptogram = vigenere.encrypt("AAAAAAAAAAAA", self.KEY)
        self.assertGreater(len(set(cryptogram)), 1)
        # With this key the cryptogram is simply the key itself.
        self.assertEqual(cryptogram, self.KEY)

    def test_a_one_letter_key_is_a_caesar_cipher(self):
        """Vigenere with |k| = 1 degenerates into the cipher of lab 1."""
        message = normalize_text("vigenere")
        shift = ALPHABET.index("D")
        expected = "".join(
            ALPHABET[(ALPHABET.index(letter) + shift) % N] for letter in message
        )
        self.assertEqual(vigenere.encrypt(message, "D"), expected)

    def test_formula_holds_for_every_pair_of_letters(self):
        for m in range(N):
            for k in range(N):
                cryptogram = vigenere.encrypt(ALPHABET[m], ALPHABET[k])
                self.assertEqual(cryptogram, ALPHABET[(m + k) % N])
                self.assertEqual(
                    vigenere.decrypt(cryptogram, ALPHABET[k]), ALPHABET[m]
                )


class TestTabulaRecta(unittest.TestCase):
    def test_it_is_31_by_31(self):
        table = vigenere.tabula_recta()
        self.assertEqual(len(table), N)
        self.assertTrue(all(len(row) == N for row in table))

    def test_every_row_is_a_permutation_of_the_alphabet(self):
        for row in vigenere.tabula_recta():
            self.assertEqual(sorted(row), sorted(ALPHABET))

    def test_a_cell_is_what_the_cipher_produces(self):
        table = vigenere.tabula_recta()
        for k in (0, 1, 10, 30):
            for m in (0, 5, 22, 30):
                self.assertEqual(
                    table[k][m], vigenere.encrypt(ALPHABET[m], ALPHABET[k])
                )


if __name__ == "__main__":
    unittest.main()
