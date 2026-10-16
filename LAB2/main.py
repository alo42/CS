"""Laboratory Work No. 2 - cryptanalysis of a monoalphabetic cipher.

    python3 main.py analyse      frequency analysis of the ciphertext
    python3 main.py walkthrough  the manual attack, one deduction at a time
    python3 main.py solve        recover the key automatically
    python3 main.py decrypt      print the plaintext using the recovered key

Every command accepts --file to work on a different ciphertext.
"""

import argparse
import sys
import textwrap

import frequency
import solver
import substitution
import walkthrough
from english import ENGLISH_FREQUENCIES

RULE = "=" * 78

# The key recovered for variant 15, as a 26-letter string: position i is the
# plaintext letter that ciphertext letter i stands for.
RECOVERED_KEY = "bqfujyncrgvkzodshwlapetixm"


def read_ciphertext(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def show_excerpt(text, width=76, lines=6):
    """Print the opening of a text, wrapped, for a quick visual check."""
    flat = " ".join(text.split())
    wrapped = textwrap.wrap(flat, width=width)[:lines]
    for line in wrapped:
        print("    " + line)
    if len(textwrap.wrap(flat, width=width)) > lines:
        print("    ...")


def command_analyse(text):
    print(RULE)
    print("Frequency analysis of the ciphertext")
    print(RULE)

    letters = frequency.letters_only(text)
    print("\nLength: %d characters, of which %d are letters.\n" % (len(text), len(letters)))

    print("Letters of the cryptogram, most frequent first, lined up with the")
    print("letters of English in the same order (table 2.2):\n")
    print("    rank  cipher       %      English       %")
    for rank, (cipher, percent, english, english_percent) in enumerate(
        frequency.comparison_table(text), start=1
    ):
        print("    %4d     %s     %6.2f         %s      %6.2f"
              % (rank, cipher, percent, english.upper(), english_percent))

    print("\nMost frequent words of one, two and three letters:")
    for length in (1, 2, 3):
        common = frequency.word_counts(text, length=length, top=6)
        shown = ", ".join("%s (%d)" % (word.upper(), count) for word, count in common)
        print("    %d letter : %s" % (length, shown))

    print("\nMost frequent trigrams: ", end="")
    print(", ".join("%s (%d)" % (gram.upper(), count)
                    for gram, count in frequency.ngrams(text, 3, top=6)))
    print("Most frequent bigrams:  ", end="")
    print(", ".join("%s (%d)" % (gram.upper(), count)
                    for gram, count in frequency.ngrams(text, 2, top=6)))
    print("Doubled letters:        ", end="")
    print(", ".join("%s (%d)" % (gram.upper(), count)
                    for gram, count in frequency.doubles(text, top=6)))
    print()


def command_walkthrough(text):
    print(RULE)
    print("Breaking the cipher, one deduction at a time")
    print(RULE)

    for number, explanation, key in walkthrough.replay():
        print("\n--- Step %d " % number + "-" * 60)
        for line in textwrap.wrap(explanation, width=76):
            print(line)
        print("\n  substitutions so far: %s" % substitution.key_to_string(key))
        print("  (lowercase = recovered plaintext, UPPERCASE = still unknown)\n")
        show_excerpt(substitution.partial_decrypt(text, key))

    final = dict(substitution.key_from_string(RECOVERED_KEY))
    print("\n" + RULE)
    print("All 26 letters recovered.")
    print(RULE)
    print("\nKey (ciphertext a..z -> plaintext): %s\n" % RECOVERED_KEY)
    print(substitution.decrypt(text, final))


def command_solve(text):
    print(RULE)
    print("Recovering the key automatically (hill climbing)")
    print(RULE)
    print("\nStarting key, from matching the frequency orders alone:")
    start = solver.starting_key(text)
    print("    %s" % substitution.key_to_string(start))
    print("\n  which decrypts the opening to:\n")
    show_excerpt(substitution.decrypt(text, start), lines=3)

    def report(attempt, score, plaintext):
        print("\n  restart %2d   best score %7.3f" % (attempt, score))
        show_excerpt(plaintext, lines=2)

    print("\nSearching...")
    key, score, plaintext = solver.solve(text, on_restart=report)
    print("\n" + RULE)
    print("Best key found: %s   (score %.3f)" % (substitution.key_to_string(key), score))
    expected = substitution.key_from_string(RECOVERED_KEY)
    print("Matches the key recovered by hand: %s" % (key == expected))
    print(RULE)
    print()
    print(plaintext)


def command_decrypt(text):
    key = substitution.key_from_string(RECOVERED_KEY)
    print(substitution.decrypt(text, key))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cryptanalysis of a monoalphabetic cipher by frequency analysis."
    )
    parser.add_argument(
        "command",
        choices=["analyse", "walkthrough", "solve", "decrypt"],
        help="what to do",
    )
    parser.add_argument(
        "--file", default="ciphertext.txt", help="ciphertext file (default: ciphertext.txt)"
    )
    args = parser.parse_args(argv)

    text = read_ciphertext(args.file)
    {
        "analyse": command_analyse,
        "walkthrough": command_walkthrough,
        "solve": command_solve,
        "decrypt": command_decrypt,
    }[args.command](text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
