"""Letter encoding of the Romanian alphabet (31 letters) and input validation.

Task 3.2 asks for the Vigenere cipher over the Romanian alphabet, "codificate
cu numerele 0, 1, ... 30".  As in Laboratory Work No. 1, the ciphers never look
at Unicode code points: a letter's numeric value is its *position* in the
ALPHABET tuple below, so no ord()/chr() appears anywhere in the cipher.
"""

import unicodedata

# A = 0, Ă = 1, Â = 2, ..., Z = 30  (n = 31)
ALPHABET = (
    "A", "Ă", "Â", "B", "C", "D", "E", "F", "G", "H", "I", "Î", "J", "K", "L",
    "M", "N", "O", "P", "Q", "R", "S", "Ș", "T", "Ț", "U", "V", "W", "X", "Y",
    "Z",
)

N = len(ALPHABET)  # 31

# The lowercase letters in the very same order, so that position i of one
# tuple always corresponds to position i of the other.
LOWERCASE = (
    "a", "ă", "â", "b", "c", "d", "e", "f", "g", "h", "i", "î", "j", "k", "l",
    "m", "n", "o", "p", "q", "r", "s", "ș", "t", "ț", "u", "v", "w", "x", "y",
    "z",
)

LETTER_TO_CODE = {letter: code for code, letter in enumerate(ALPHABET)}
LOWER_TO_UPPER = dict(zip(LOWERCASE, ALPHABET))

# Ș and Ț are often typed with a cedilla instead of a comma below; the two
# variants are treated as the same letter.
CEDILLA_VARIANTS = {
    "Ş": "Ș", "ş": "ș",
    "Ţ": "Ț", "ţ": "ț",
}

MIN_KEY_LENGTH = 7       # "Lungimea cheii nu trebuie sa fie mai mica de 7"


class InvalidCharacterError(ValueError):
    """Raised when the text contains something other than a Romanian letter."""

    def __init__(self, character, position):
        self.character = character
        self.position = position
        super().__init__(
            "the character %r (position %d) is not a letter of the Romanian "
            "alphabet; allowed letters are %s (uppercase or lowercase) and "
            "spaces, which are removed"
            % (character, position, " ".join(ALPHABET))
        )


class InvalidKeyError(ValueError):
    """Raised when the key is too short or contains a non-Romanian letter."""


def normalize_text(raw):
    """Return `raw` uppercased, without spaces, as Romanian letters only.

    This is the preparation the task asks for - "in mesaj mai intai trebuie
    eliminate spatiile, apoi toate literele se vor transforma in majuscule".
    Cedilla spellings of Ș/Ț are folded onto the comma-below ones, and the
    first character that is not a Romanian letter raises
    InvalidCharacterError so the caller can tell the user exactly what was
    rejected and what the allowed range is.
    """
    # NFC recomposes letters typed as "S" + combining comma below, etc.
    text = unicodedata.normalize("NFC", raw)

    letters = []
    for position, char in enumerate(text, start=1):
        if char.isspace():          # spaces are allowed in the input...
            continue                # ...and simply dropped
        char = CEDILLA_VARIANTS.get(char, char)
        char = LOWER_TO_UPPER.get(char, char)
        if char not in LETTER_TO_CODE:
            raise InvalidCharacterError(char, position)
        letters.append(char)
    return "".join(letters)


def parse_key(raw):
    """Validate the key: Romanian letters only, at least MIN_KEY_LENGTH."""
    try:
        key = normalize_text(raw)
    except InvalidCharacterError as error:
        raise InvalidKeyError(
            "the key may contain only letters of the Romanian alphabet: %s"
            % error
        )
    if len(key) < MIN_KEY_LENGTH:
        raise InvalidKeyError(
            "the key %r has %d letter(s); it must have at least %d"
            % (key, len(key), MIN_KEY_LENGTH)
        )
    return key
