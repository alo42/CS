"""Bit strings for DES, and the operations the standard performs on them.

A bit string is a plain list of 0/1 integers.  FIPS 46-3 numbers the bits of
a block from 1 on the left, and every table of the standard is written in
those terms, so `permute` below indexes its table 1-based and nothing in the
program has to re-number anything.
"""


class InvalidBitsError(ValueError):
    """Raised when a text does not describe a bit string of the right size."""


def permute(block, table):
    """Return the block rearranged by `table`, a 1-based list of positions.

    This single function performs PC-1 and PC-2 - and, in the full cipher, IP,
    E and P as well: in DES every table is read the same way, "the bit of the
    output at position i is the bit of the input at position table[i]".
    """
    return [block[position - 1] for position in table]


def rotate_left(block, amount):
    """Rotate a block one or more places to the left (the LS_i of the standard)."""
    amount %= len(block)
    return block[amount:] + block[:amount]


def from_bytes(data):
    """The bits of a byte string, most significant bit of each byte first."""
    bits = []
    for byte in data:
        for offset in range(7, -1, -1):
            bits.append((byte >> offset) & 1)
    return bits


def from_hex(text, length):
    """Read `length` bits from a hexadecimal string of length/4 digits."""
    digits = "".join(text.split()).lower()
    if digits.startswith("0x"):
        digits = digits[2:]
    if len(digits) * 4 != length:
        raise InvalidBitsError(
            "%d hexadecimal digits are needed for %d bits, %d given"
            % (length // 4, length, len(digits))
        )
    bits = []
    for digit in digits:
        if digit not in "0123456789abcdef":
            raise InvalidBitsError("%r is not a hexadecimal digit" % digit)
        value = int(digit, 16)
        for offset in range(3, -1, -1):
            bits.append((value >> offset) & 1)
    return bits


def from_binary(text, length):
    """Read a bit string written out as 0s and 1s (spaces are ignored)."""
    digits = "".join(text.split())
    if len(digits) != length:
        raise InvalidBitsError(
            "%d bits are needed, %d given" % (length, len(digits))
        )
    if any(digit not in "01" for digit in digits):
        raise InvalidBitsError("only the digits 0 and 1 are allowed")
    return [int(digit) for digit in digits]


def to_hex(block):
    """The block as hexadecimal; the length must be a multiple of 4."""
    digits = []
    for start in range(0, len(block), 4):
        value = 0
        for bit in block[start:start + 4]:
            value = value * 2 + bit
        digits.append("%X" % value)
    return "".join(digits)


def group(block, size):
    """The block written out in groups of `size` bits, separated by spaces."""
    return " ".join(
        "".join(str(bit) for bit in block[start:start + size])
        for start in range(0, len(block), size)
    )
