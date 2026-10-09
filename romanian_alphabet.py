"""Letter encoding of the Romanian alphabet (Table 2 of Laboratory Work No. 1).

The whole point of this module is that the ciphers never look at Unicode code
points: a letter's numeric value is its *position* in the ALPHABET tuple below,
exactly as required by task 1.1, point 2.
"""

import unicodedata

# A = 0, Ă = 1, Â = 2, ..., Z = 30  (Table 2, n = 31)
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
# variants are treated as the same letter (implementation tip of task 1.1).
CEDILLA_VARIANTS = {
    "Ş": "Ș", "ş": "ș",
    "Ţ": "Ț", "ţ": "ț",
}

MIN_KEY = 1
MAX_KEY = N - 1          # 30: a shift of 0 (or of 31) would change nothing
MIN_KEYWORD_LENGTH = 7


class InvalidKeyError(ValueError):
    """Raised when key 1 is not an integer in the range MIN_KEY..MAX_KEY."""


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


class InvalidKeywordError(ValueError):
    """Raised when key 2 is too short or contains a non-Romanian letter."""


def normalize_text(raw):
    """Return `raw` uppercased, without spaces, as Romanian letters only.

    Cedilla spellings of Ș/Ț are folded onto the comma-below ones and the
    first character that is not a Romanian letter raises
    InvalidCharacterError, so the caller can tell the user exactly what was
    rejected.
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
    """Validate key 1: an integer between MIN_KEY and MAX_KEY inclusive."""
    stripped = raw.strip()
    try:
        key = int(stripped)
    except ValueError:
        raise InvalidKeyError(
            "%r is not an integer; key 1 must be a whole number between %d "
            "and %d inclusive" % (stripped, MIN_KEY, MAX_KEY)
        )
    if not MIN_KEY <= key <= MAX_KEY:
        raise InvalidKeyError(
            "the key %d is out of range; key 1 must be between %d and %d "
            "inclusive (the alphabet has %d letters, and a shift of 0 would "
            "leave the text unchanged)" % (key, MIN_KEY, MAX_KEY, N)
        )
    return key


def parse_keyword(raw):
    """Validate key 2: Romanian letters only, at least MIN_KEYWORD_LENGTH."""
    try:
        keyword = normalize_text(raw)
    except InvalidCharacterError as error:
        raise InvalidKeywordError(
            "key 2 may contain only letters of the Romanian alphabet: %s"
            % error
        )
    if len(keyword) < MIN_KEYWORD_LENGTH:
        raise InvalidKeywordError(
            "the keyword %r has %d letter(s); key 2 must have at least %d "
            "letters" % (keyword, len(keyword), MIN_KEYWORD_LENGTH)
        )
    return keyword
