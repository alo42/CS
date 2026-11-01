"""Laboratory Work No. 3, task 3.2 - the Vigenere cipher over Romanian.

Interactive program: the user chooses the operation, types the key and the
message (or the cryptogram) and gets back the cryptogram (or the decrypted
message).

Run it with:  python3 main.py
"""

import sys

import vigenere
from romanian_alphabet import (
    ALPHABET,
    MIN_KEY_LENGTH,
    N,
    InvalidCharacterError,
    InvalidKeyError,
    normalize_text,
    parse_key,
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
        except (InvalidCharacterError, InvalidKeyError) as error:
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


def show_alphabet(per_row=16):
    """Print the alphabet together with the code of every letter."""
    print("  Alphabet in use (n = %d):" % N)
    for start in range(0, N, per_row):
        row = range(start, min(start + per_row, N))
        print("    code   " + " ".join("%2d" % code for code in row))
        print("    letter " + " ".join(" %s" % ALPHABET[code] for code in row))
    print()


def show_steps(rows, operation, per_row=16):
    """Print the six-row table of the transformation, in blocks of columns."""
    if operation == "encrypt":
        labels = ("Plaintext  M", "Key        K", "M (codes)   ",
                  "K (codes)   ", "M+K (mod %2d)" % N, "Ciphertext C")
    else:
        labels = ("Ciphertext C", "Key        K", "C (codes)   ",
                  "K (codes)   ", "C-K (mod %2d)" % N, "Plaintext  M")

    print("  The transformation, letter by letter:")
    for start in range(0, len(rows), per_row):
        block = rows[start:start + per_row]
        for index, label in enumerate(labels):
            cells = " ".join("%2s" % str(row[index]) for row in block)
            print("    %s  %s" % (label, cells))
        print()


def show_tabula_recta():
    """Print the Tabula Recta for the 31 Romanian letters."""
    table = vigenere.tabula_recta()
    print()
    print(RULE)
    print("Tabula Recta for the Romanian alphabet (row = key letter,")
    print("column = plaintext letter, cell = ciphertext letter)")
    print(RULE)
    print("     " + " ".join(ALPHABET))
    for row, letters in enumerate(table):
        print("  %s  %s" % (ALPHABET[row], " ".join(letters)))
    print()


def run_task():
    """Run one encryption or decryption, asking for everything it needs."""
    print()
    print(RULE)
    print("Task 3.2 - Vigenere cipher (Romanian alphabet, n = %d)" % N)
    print(RULE)

    operation = ask_choice(
        "Operation - 1 = encrypt, 2 = decrypt: ", {"1": "encrypt", "2": "decrypt"}
    )

    key = ask(
        "Key (at least %d Romanian letters): " % MIN_KEY_LENGTH, parse_key
    )

    label = "Plaintext" if operation == "encrypt" else "Cryptogram"
    text = ask(
        "%s (spaces are allowed and removed): " % label, normalize_text
    )
    if not text:
        print("  [invalid input] the text contains no letters at all.\n")
        return

    print()
    show_alphabet()
    print("  Key used: %s  (repeated to the length of the text)\n" % key)
    show_steps(vigenere.steps(text, key, operation), operation)

    if operation == "encrypt":
        result = vigenere.encrypt(text, key)
        print("  Plaintext  (uppercase, no spaces) : %s" % text)
        print("  Cryptogram                        : %s\n" % result)
    else:
        result = vigenere.decrypt(text, key)
        print("  Cryptogram (uppercase, no spaces) : %s" % text)
        print("  Decrypted message                 : %s\n" % result)


def main():
    print(RULE)
    print("Laboratory Work No. 3 - the Vigenere cipher over the Romanian "
          "alphabet")
    print(RULE)

    menu = {"1": run_task, "2": show_tabula_recta, "0": None}
    while True:
        print("\n  1) Task 3.2 - encrypt or decrypt a text")
        print("  2) Show the Tabula Recta of the 31 letters")
        print("  0) Exit")
        try:
            chosen = ask_choice("Your choice: ", menu)
            if chosen is None:
                break
            chosen()
        except Quit:
            break

    print("\nGoodbye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
