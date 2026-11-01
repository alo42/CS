"""Task 2.5 of Laboratory Work No. 4: from K+ to the sixteen round keys.

The key schedule of DES is the part of the algorithm that turns one key into
the sixteen subkeys K_1 ... K_16 used by the sixteen rounds:

    K   --PC-1-->  K+   -->  C_0 D_0
    C_i = LS_i(C_{i-1}),  D_i = LS_i(D_{i-1})
    K_i = PC-2(C_i D_i)

Every function returns the intermediate values as well as the result, because
the assignment requires all the intermediate steps to be shown on screen.
"""

import bits
from des_tables import (
    HALF_BITS,
    KEY_BITS,
    KPLUS_BITS,
    PC1,
    PC2,
    ROUNDS,
    SHIFTS,
)


def permuted_choice_1(key):
    """K+ = PC-1(K): drop the 8 parity bits of the key and reorder the rest.

    This is task 2.1 of the laboratory work, and the step that produces the
    K+ which task 2.5 starts from.
    """
    if len(key) != KEY_BITS:
        raise ValueError("the key has %d bits, %d expected" % (len(key), KEY_BITS))
    return bits.permute(key, PC1)


def split(kplus):
    """C_0 and D_0: the left and the right half of K+ (this is task 2.2)."""
    if len(kplus) != KPLUS_BITS:
        raise ValueError("K+ has %d bits, %d expected" % (len(kplus), KPLUS_BITS))
    return kplus[:HALF_BITS], kplus[HALF_BITS:]


def halves(kplus):
    """All the pairs (C_i, D_i), from i = 0 to i = 16.

    C_i and D_i are obtained from C_{i-1} and D_{i-1} by a left rotation of
    LS_i places - one place in rounds 1, 2, 9 and 16, two in the others.
    """
    c, d = split(kplus)
    pairs = [(c, d)]
    for shift in SHIFTS:
        c = bits.rotate_left(c, shift)
        d = bits.rotate_left(d, shift)
        pairs.append((c, d))
    return pairs


def round_key(c, d):
    """K_i = PC-2(C_i D_i): 48 of the 56 bits of the two halves (task 2.3)."""
    return bits.permute(c + d, PC2)


def round_keys(kplus):
    """The sixteen round keys K_1 ... K_16 - the answer to task 2.5."""
    return [round_key(c, d) for c, d in halves(kplus)[1:]]


def schedule(kplus):
    """The whole key schedule as a list of one record per round.

    Each record is a dictionary holding everything that happens in round i:
    the shift applied, the two halves before and after it, and the round key
    that PC-2 extracts from them.
    """
    pairs = halves(kplus)
    records = []
    for index, shift in enumerate(SHIFTS):
        previous_c, previous_d = pairs[index]
        c, d = pairs[index + 1]
        records.append({
            "round": index + 1,
            "shift": shift,
            "previous_c": previous_c,
            "previous_d": previous_d,
            "c": c,
            "d": d,
            "key": round_key(c, d),
        })
    return records


def from_key(key):
    """The whole schedule starting from the 64-bit key instead of from K+."""
    kplus = permuted_choice_1(key)
    return kplus, schedule(kplus)


def check_rotations_close(pairs):
    """C_16 = C_0 and D_16 = D_0, because the shifts add up to 28.

    Returned rather than asserted, so that the program can state it on screen
    as one more piece of evidence that the schedule was built correctly.
    """
    if len(pairs) != ROUNDS + 1:
        raise ValueError("expected %d pairs of halves" % (ROUNDS + 1))
    return pairs[0] == pairs[ROUNDS]
