"""Laboratory Work No. 1 - Caesar cipher over the Romanian alphabet.

Interactive program for both tasks:

  * task 1.1 - the plain Caesar cipher (one numeric key);
  * task 1.2 - the Caesar cipher with an alphabet permuted by a keyword.

Run it with:  python3 main.py
"""

import sys

import caesar
from romanian_alphabet import (
    ALPHABET,
    MAX_KEY,
    MIN_KEY,
    MIN_KEYWORD_LENGTH,
    N,
    InvalidCharacterError,
    InvalidKeyError,
    InvalidKeywordError,
    normalize_text,
    parse_key,
    parse_keyword,
)

RULE = "=" * 72


class Quit(Exception):
    """Raised when the user ends the input (Ctrl-D / Ctrl-C)."""


def ask(prompt, parse):
    """Ask for a value until `parse` accepts it, reporting every rejection."""
    while True:
        try:
            raw = input(prompt)
        except (EOFError, KeyboardInterrupt):
            raise Quit
        try:
            return parse(raw)
        except (InvalidKeyError, InvalidCharacterError, InvalidKeywordError) as error:
            print("  [invalid input] %s\n" % error)


def ask_choice(prompt, choices):
    """Ask for one of the keys of `choices` (a dict of label -> value)."""
    def parse(raw):
        answer = raw.strip()
        if answer not in choices:
            raise InvalidKeyError(
                "%r is not one of the options; type %s"
                % (answer, " or ".join(sorted(choices)))
            )
        return choices[answer]

    return ask(prompt, parse)


def show_alphabet(alphabet, title, per_row=16):
    """Print the alphabet together with the code of every letter."""
    print(title)
    for start in range(0, len(alphabet), per_row):
        row = range(start, min(start + per_row, len(alphabet)))
        print("    code   " + " ".join("%2d" % code for code in row))
        print("    letter " + " ".join(" %s" % alphabet[code] for code in row))
    print()


def run_task(task_number, use_keyword):
    """Run one encryption or decryption, asking for everything it needs."""
    print()
    print(RULE)
    print(
        "Task %s - Caesar cipher%s (Romanian alphabet, n = %d)"
        % (task_number, " with a keyword permutation" if use_keyword else "", N)
    )
    print(RULE)

    operation = ask_choice(
        "Operation - 1 = encrypt, 2 = decrypt: ", {"1": "encrypt", "2": "decrypt"}
    )

    key = ask(
        "Key 1 - numeric shift (%d..%d): " % (MIN_KEY, MAX_KEY), parse_key
    )

    alphabet = ALPHABET
    if use_keyword:
        keyword = ask(
            "Key 2 - keyword (at least %d Romanian letters): "
            % MIN_KEYWORD_LENGTH,
            parse_keyword,
        )
        alphabet = caesar.build_permuted_alphabet(keyword)
        print()
        print("  Keyword used: %s" % keyword)
        show_alphabet(
            alphabet, "  Permuted alphabet (check it by hand against Table 3):"
        )
    else:
        print()
        show_alphabet(ALPHABET, "  Alphabet in use (Table 2):")

    label = "plaintext" if operation == "encrypt" else "ciphertext"
    text = ask("%s (spaces are allowed and removed): " % label.capitalize(), normalize_text)
    if not text:
        print("  [invalid input] the text contains no letters at all.\n")
        return

    if operation == "encrypt":
        result = caesar.encrypt(text, key, alphabet)
        print("\n  Plaintext  (uppercase, no spaces) : %s" % text)
        print("  Ciphertext                        : %s\n" % result)
    else:
        result = caesar.decrypt(text, key, alphabet)
        print("\n  Ciphertext (uppercase, no spaces) : %s" % text)
        print("  Decrypted message                 : %s\n" % result)


def main():
    print(RULE)
    print("Laboratory Work No. 1 - the Caesar cipher over the Romanian alphabet")
    print(RULE)

    menu = {"1": ("1.1", False), "2": ("1.2", True), "0": None}
    while True:
        print("\n  1) Task 1.1 - Caesar cipher with a numeric key")
        print("  2) Task 1.2 - Caesar cipher with a numeric key and a keyword")
        print("  0) Exit")
        try:
            chosen = ask_choice("Your choice: ", menu)
            if chosen is None:
                break
            task_number, use_keyword = chosen
            run_task(task_number, use_keyword)
        except Quit:
            break

    print("\nGoodbye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
