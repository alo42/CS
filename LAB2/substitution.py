"""Applying a (possibly partial) monoalphabetic key to a text.

A key maps a *ciphertext* letter to a *plaintext* letter. Only letters are
substituted; digits, punctuation and spaces are left exactly as they are,
as stated in the task.
"""

from english import ALPHABET


def empty_key():
    """A key with nothing decided yet."""
    return {}


def key_from_string(plain_for_each_cipher_letter):
    """Build a key from a 26-letter string: position i is the plaintext
    letter that ciphertext letter `ALPHABET[i]` stands for.

    A dot or a space in the string means that letter is still unknown.
    """
    text = plain_for_each_cipher_letter.strip().lower()
    if len(text) != 26:
        raise ValueError(
            "a key must have exactly 26 characters, got %d" % len(text)
        )
    key = {}
    for cipher_letter, plain_letter in zip(ALPHABET, text):
        if plain_letter not in (".", " ", "_", "?"):
            key[cipher_letter] = plain_letter
    return key


def key_to_string(key):
    """The inverse of `key_from_string`; unknown letters become dots."""
    return "".join(key.get(letter, ".") for letter in ALPHABET)


def decrypt(text, key):
    """Decrypt, keeping the capitalisation of the ciphertext.

    Used for the final plaintext, once the key is complete.
    """
    out = []
    for char in text:
        lowered = char.lower()
        if lowered in key:
            plain = key[lowered]
            out.append(plain.upper() if char.isupper() else plain)
        else:
            out.append(char)
    return "".join(out)


def partial_decrypt(text, key):
    """Decrypt in the style used by the laboratory work.

    Letters that have already been worked out are shown in *lowercase*
    (they are plaintext now); letters still unknown stay as the *uppercase*
    ciphertext letter. This is what makes a half-broken message readable,
    e.g. `tIe` for a word whose middle letter is not yet decided.
    """
    out = []
    for char in text:
        if not char.isalpha():
            out.append(char)
            continue
        lowered = char.lower()
        if lowered in key:
            out.append(key[lowered])
        else:
            out.append(lowered.upper())
    return "".join(out)


def conflicts(key):
    """Return the plaintext letters this key assigns to more than one
    ciphertext letter - a key must be a one-to-one mapping."""
    seen = {}
    clashing = {}
    for cipher_letter, plain_letter in sorted(key.items()):
        if plain_letter in seen:
            clashing.setdefault(plain_letter, [seen[plain_letter]]).append(cipher_letter)
        else:
            seen[plain_letter] = cipher_letter
    return clashing
