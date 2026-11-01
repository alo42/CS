"""Known-answer tests: the strongest check available on the sixteen round keys.

A single wrong bit in any one of K_1 ... K_16 changes the ciphertext, so a
full DES encryption that reproduces a published plaintext/ciphertext pair
confirms the whole key schedule at once - not only the rounds whose values
one happens to recognise.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bits
import des_reference

# Published DES test vectors (key, plaintext, ciphertext), all hexadecimal.
VECTORS = (
    ("133457799BBCDFF1", "0123456789ABCDEF", "85E813540F0AB405"),
    ("0101010101010101", "0000000000000000", "8CA64DE9C1B123A7"),
    ("0E329232EA6D0D73", "8787878787878787", "0000000000000000"),
)


class TestKnownAnswers(unittest.TestCase):
    def test_published_vectors(self):
        for key_hex, plain_hex, cipher_hex in VECTORS:
            key = bits.from_hex(key_hex, 64)
            plain = bits.from_hex(plain_hex, 64)
            produced = bits.to_hex(des_reference.encrypt(plain, key))
            self.assertEqual(produced, cipher_hex,
                             "key %s: expected %s, got %s"
                             % (key_hex, cipher_hex, produced))


if __name__ == "__main__":
    unittest.main()
