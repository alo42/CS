"""The Vigenere cipher of Laboratory Work No. 3, task 3.2.

The mathematical model is the one given in the assignment, with the alphabet
length taken from the alphabet actually in use (n = 31 for Romanian):

    c_i = (m_i + k_i) mod n        m_i = (c_i - k_i) mod n

where k_i is the code of the letter of the key that falls on position i, the
key being repeated from the beginning once it runs out.  The alphabet is a
parameter so that the very same code can be checked against the 26-letter
English example worked out in the assignment.
"""

from romanian_alphabet import ALPHABET


def _codes(alphabet):
    """Map each letter to its position in `alphabet` (its numeric code)."""
    return {letter: code for code, letter in enumerate(alphabet)}


def key_stream(key, length):
    """Repeat `key` until it covers `length` letters: k_i = key[i mod |key|]."""
    return "".join(key[position % len(key)] for position in range(length))


def encrypt(text, key, alphabet=ALPHABET):
    """c_i = (m_i + k_i) mod n, letter by letter."""
    to_code = _codes(alphabet)
    n = len(alphabet)
    stream = key_stream(key, len(text))
    return "".join(
        alphabet[(to_code[letter] + to_code[k]) % n]
        for letter, k in zip(text, stream)
    )


def decrypt(text, key, alphabet=ALPHABET):
    """m_i = (c_i - k_i) mod n, letter by letter.

    `+ n` before the modulo keeps the result in 0..n-1 even in languages whose
    remainder may come out negative (Python's % already would, but the formula
    is written in the portable form the laboratory work asks for).
    """
    to_code = _codes(alphabet)
    n = len(alphabet)
    stream = key_stream(key, len(text))
    return "".join(
        alphabet[(to_code[letter] - to_code[k] + n) % n]
        for letter, k in zip(text, stream)
    )


def steps(text, key, operation, alphabet=ALPHABET):
    """Return the worked table of the transformation, one column per letter.

    Each entry is the tuple (input letter, key letter, input code, key code,
    output code, output letter) - the six rows of the table used in the
    assignment to show the cipher by hand.
    """
    to_code = _codes(alphabet)
    n = len(alphabet)
    rows = []
    for letter, k in zip(text, key_stream(key, len(text))):
        value, shift = to_code[letter], to_code[k]
        if operation == "encrypt":
            result = (value + shift) % n
        else:
            result = (value - shift + n) % n
        rows.append((letter, k, value, shift, result, alphabet[result]))
    return rows


def tabula_recta(alphabet=ALPHABET):
    """The Tabula Recta: row k, column m holds the letter (m + k) mod n."""
    n = len(alphabet)
    return [
        [alphabet[(column + row) % n] for column in range(n)]
        for row in range(n)
    ]
