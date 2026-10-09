"""The two ciphers of Laboratory Work No. 1.

Both tasks are the same algorithm; they only differ in the order of the
alphabet the shift is applied to:

  * task 1.1 shifts over ALPHABET (the natural order of Table 2);
  * task 1.2 shifts over the alphabet permuted by the keyword (Table 3).

So `encrypt`/`decrypt` take the ordered alphabet as a parameter and
`build_permuted_alphabet` produces the one task 1.2 needs.
"""

from romanian_alphabet import ALPHABET


def _codes(alphabet):
    """Map each letter to its position in `alphabet` (its numeric code)."""
    return {letter: code for code, letter in enumerate(alphabet)}


def build_permuted_alphabet(keyword, alphabet=ALPHABET):
    """Order the alphabet by `keyword`, then by the remaining letters.

    Only the first occurrence of a repeated letter of the keyword is kept, so
    the result is always a permutation of all the letters of `alphabet`.
    """
    permuted = []
    for letter in keyword:
        if letter not in permuted:
            permuted.append(letter)
    for letter in alphabet:
        if letter not in permuted:
            permuted.append(letter)
    return tuple(permuted)


def encrypt(text, key, alphabet=ALPHABET):
    """c = e_k(x) = (x + k) mod n, letter by letter."""
    to_code = _codes(alphabet)
    n = len(alphabet)
    return "".join(alphabet[(to_code[letter] + key) % n] for letter in text)


def decrypt(text, key, alphabet=ALPHABET):
    """m = d_k(y) = (y - k) mod n, letter by letter.

    `+ n` before the modulo keeps the result in 0..n-1 even in languages
    whose remainder may come out negative (Python's % already would, but the
    formula is written in the portable form the laboratory work asks for).
    """
    to_code = _codes(alphabet)
    n = len(alphabet)
    return "".join(alphabet[(to_code[letter] - key + n) % n] for letter in text)
