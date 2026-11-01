"""The tables of the DES key schedule, exactly as printed in FIPS 46-3.

Only the three tables the key schedule needs are defined here - PC-1, the
rotation schedule and PC-2.  The tables of the data path (IP, E, the eight
S-boxes, P) belong to the other tasks of the laboratory work and are not used
by task 2.5.
"""

# PC-1 (Permuted Choice 1): picks 56 of the 64 bits of the key and reorders
# them.  The 8 bits it leaves out - 8, 16, 24, 32, 40, 48, 56, 64 - are the
# parity bits of the key, which carry no key material.
PC1 = (
    57, 49, 41, 33, 25, 17,  9,
     1, 58, 50, 42, 34, 26, 18,
    10,  2, 59, 51, 43, 35, 27,
    19, 11,  3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
     7, 62, 54, 46, 38, 30, 22,
    14,  6, 61, 53, 45, 37, 29,
    21, 13,  5, 28, 20, 12,  4,
)

# PC-2 (Permuted Choice 2): picks 48 of the 56 bits of C_i D_i to form the
# round key.  The 8 bits it never names - 9, 18, 22, 25, 35, 38, 43, 54 - are
# simply dropped in that round.
PC2 = (
    14, 17, 11, 24,  1,  5,
     3, 28, 15,  6, 21, 10,
    23, 19, 12,  4, 26,  8,
    16,  7, 27, 20, 13,  2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
)

# LS_i: how far C_{i-1} and D_{i-1} are rotated to the left in round i.
# The 16 values add up to 28, which is why C_16 = C_0 and D_16 = D_0.
SHIFTS = (1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1)

KEY_BITS = 64
KPLUS_BITS = 56
HALF_BITS = 28
ROUND_KEY_BITS = 48
ROUNDS = 16

# The bits of the 64-bit key that PC-1 discards (the parity bits).
PARITY_BITS = tuple(position for position in range(1, KEY_BITS + 1)
                    if position not in PC1)

# The bits of C_i D_i that PC-2 discards.
DROPPED_BY_PC2 = tuple(position for position in range(1, KPLUS_BITS + 1)
                       if position not in PC2)


def format_table(table, per_row, title):
    """Lay a table out in rows, the way the standard prints it."""
    lines = [title]
    for start in range(0, len(table), per_row):
        row = table[start:start + per_row]
        lines.append("    " + " ".join("%2d" % value for value in row))
    return "\n".join(lines)
