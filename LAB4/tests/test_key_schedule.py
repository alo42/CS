"""Checks for Laboratory Work No. 4, task 2.5.

Run from the LAB4 directory with:  python3 -m unittest discover -s tests

The reference values are those of the standard worked example of DES, the one
built on the key 133457799BBCDFF1; every one of the sixteen round keys is
pinned, not only the first and the last.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bits
import key_schedule
from des_tables import (
    DROPPED_BY_PC2,
    HALF_BITS,
    KEY_BITS,
    KPLUS_BITS,
    PARITY_BITS,
    PC1,
    PC2,
    ROUND_KEY_BITS,
    ROUNDS,
    SHIFTS,
)

KEY_HEX = "133457799BBCDFF1"
KPLUS = "11110000110011001010101011110101010101100110011110001111"
C0 = "1111000011001100101010101111"
D0 = "0101010101100110011110001111"

ROUND_KEYS = (
    "000110110000001011101111111111000111000001110010",
    "011110011010111011011001110110111100100111100101",
    "010101011111110010001010010000101100111110011001",
    "011100101010110111010110110110110011010100011101",
    "011111001110110000000111111010110101001110101000",
    "011000111010010100111110010100000111101100101111",
    "111011001000010010110111111101100001100010111100",
    "111101111000101000111010110000010011101111111011",
    "111000001101101111101011111011011110011110000001",
    "101100011111001101000111101110100100011001001111",
    "001000010101111111010011110111101101001110000110",
    "011101010111000111110101100101000110011111101001",
    "100101111100010111010001111110101011101001000001",
    "010111110100001110110111111100101110011100111010",
    "101111111001000110001101001111010011111100001010",
    "110010110011110110001011000011100001011111110101",
)


def text(block):
    return "".join(str(bit) for bit in block)


class TestTables(unittest.TestCase):
    def test_pc1_chooses_56_distinct_bits(self):
        self.assertEqual(len(PC1), KPLUS_BITS)
        self.assertEqual(len(set(PC1)), KPLUS_BITS)
        self.assertTrue(all(1 <= position <= KEY_BITS for position in PC1))

    def test_pc1_drops_exactly_the_parity_bits(self):
        self.assertEqual(PARITY_BITS, (8, 16, 24, 32, 40, 48, 56, 64))

    def test_pc2_chooses_48_distinct_bits(self):
        self.assertEqual(len(PC2), ROUND_KEY_BITS)
        self.assertEqual(len(set(PC2)), ROUND_KEY_BITS)
        self.assertTrue(all(1 <= position <= KPLUS_BITS for position in PC2))

    def test_pc2_drops_eight_known_positions(self):
        self.assertEqual(DROPPED_BY_PC2, (9, 18, 22, 25, 35, 38, 43, 54))

    def test_the_shifts_add_up_to_the_length_of_a_half(self):
        self.assertEqual(len(SHIFTS), ROUNDS)
        self.assertEqual(sum(SHIFTS), HALF_BITS)

    def test_the_shifts_are_one_in_rounds_1_2_9_and_16(self):
        ones = [index + 1 for index, shift in enumerate(SHIFTS) if shift == 1]
        self.assertEqual(ones, [1, 2, 9, 16])


class TestBits(unittest.TestCase):
    def test_hex_and_back(self):
        block = bits.from_hex(KEY_HEX, KEY_BITS)
        self.assertEqual(len(block), KEY_BITS)
        self.assertEqual(bits.to_hex(block), KEY_HEX)

    def test_a_character_becomes_its_ascii_code(self):
        self.assertEqual(text(bits.from_bytes(b"A")), "01000001")

    def test_binary_input_ignores_spaces(self):
        self.assertEqual(bits.from_binary("1010 1010", 8),
                         [1, 0, 1, 0, 1, 0, 1, 0])

    def test_rejects_the_wrong_number_of_bits(self):
        for call in (lambda: bits.from_hex("FF", KEY_BITS),
                     lambda: bits.from_binary("101", 8),
                     lambda: bits.from_hex("GG", 8)):
            with self.assertRaises(bits.InvalidBitsError):
                call()

    def test_permute_is_one_based(self):
        # The table "3 1 2" moves the third bit to the front.
        self.assertEqual(bits.permute([1, 0, 0], (3, 1, 2)), [0, 1, 0])

    def test_rotate_left_wraps_around(self):
        self.assertEqual(bits.rotate_left([1, 0, 0, 0], 1), [0, 0, 0, 1])
        self.assertEqual(bits.rotate_left([1, 0, 0, 0], 2), [0, 0, 1, 0])


class TestWorkedExample(unittest.TestCase):
    """The standard worked example, key 133457799BBCDFF1."""

    def setUp(self):
        self.key = bits.from_hex(KEY_HEX, KEY_BITS)
        self.kplus = key_schedule.permuted_choice_1(self.key)

    def test_pc1_gives_the_expected_kplus(self):
        self.assertEqual(text(self.kplus), KPLUS)

    def test_the_two_halves(self):
        c, d = key_schedule.split(self.kplus)
        self.assertEqual(text(c), C0)
        self.assertEqual(text(d), D0)

    def test_all_sixteen_round_keys(self):
        keys = key_schedule.round_keys(self.kplus)
        self.assertEqual(len(keys), ROUNDS)
        for index, (produced, expected) in enumerate(zip(keys, ROUND_KEYS), 1):
            self.assertEqual(text(produced), expected, "K%d differs" % index)

    def test_starting_from_kplus_gives_the_same_keys(self):
        """Task 2.5 proper: K+ is given, the key itself is not needed."""
        kplus = bits.from_binary(KPLUS, KPLUS_BITS)
        records = key_schedule.schedule(kplus)
        self.assertEqual([text(record["key"]) for record in records],
                         list(ROUND_KEYS))

    def test_the_schedule_records_every_round(self):
        records = key_schedule.schedule(self.kplus)
        self.assertEqual(len(records), ROUNDS)
        for record, shift in zip(records, SHIFTS):
            self.assertEqual(record["shift"], shift)
            # Each half really is the previous one rotated by that shift.
            self.assertEqual(record["c"],
                             bits.rotate_left(record["previous_c"], shift))
            self.assertEqual(record["d"],
                             bits.rotate_left(record["previous_d"], shift))


class TestProperties(unittest.TestCase):
    """Properties that must hold for any K+, not only for the example."""

    def setUp(self):
        self.kplus = bits.from_hex("0123456789ABCD", KPLUS_BITS)

    def test_every_round_key_is_48_bits(self):
        for key in key_schedule.round_keys(self.kplus):
            self.assertEqual(len(key), ROUND_KEY_BITS)

    def test_the_halves_come_back_to_the_start(self):
        pairs = key_schedule.halves(self.kplus)
        self.assertEqual(len(pairs), ROUNDS + 1)
        self.assertEqual(pairs[0], pairs[ROUNDS])
        self.assertTrue(key_schedule.check_rotations_close(pairs))

    def test_the_sixteen_keys_are_all_different(self):
        keys = [text(key) for key in key_schedule.round_keys(self.kplus)]
        self.assertEqual(len(set(keys)), ROUNDS)

    def test_an_all_zero_kplus_gives_all_zero_round_keys(self):
        """A weak key: rotating zeros changes nothing, so every K_i is zero."""
        zeros = [0] * KPLUS_BITS
        for key in key_schedule.round_keys(zeros):
            self.assertEqual(set(key), {0})

    def test_the_parity_bits_of_the_key_do_not_matter(self):
        """Flipping a parity bit leaves all sixteen round keys unchanged."""
        key = bits.from_hex(KEY_HEX, KEY_BITS)
        before = key_schedule.round_keys(key_schedule.permuted_choice_1(key))
        for position in PARITY_BITS:
            flipped = list(key)
            flipped[position - 1] ^= 1
            after = key_schedule.round_keys(
                key_schedule.permuted_choice_1(flipped)
            )
            self.assertEqual(after, before)

    def test_a_single_key_bit_changes_many_round_keys(self):
        """Flipping a real key bit must disturb the schedule, not one round."""
        key = bits.from_hex(KEY_HEX, KEY_BITS)
        before = key_schedule.round_keys(key_schedule.permuted_choice_1(key))
        flipped = list(key)
        flipped[0] ^= 1                      # bit 1 is not a parity bit
        after = key_schedule.round_keys(key_schedule.permuted_choice_1(flipped))
        changed = sum(1 for a, b in zip(before, after) if a != b)
        self.assertGreater(changed, ROUNDS // 2)

    def test_rejects_a_kplus_of_the_wrong_size(self):
        with self.assertRaises(ValueError):
            key_schedule.split([0] * 55)
        with self.assertRaises(ValueError):
            key_schedule.permuted_choice_1([0] * 63)


if __name__ == "__main__":
    unittest.main()
