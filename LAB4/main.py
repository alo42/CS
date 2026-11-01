"""Laboratory Work No. 4, task 2.5 - the DES key schedule.

Given K+, determine all sixteen round keys K_1 ... K_16.  The key may be
typed as the 8-character DES key (K+ is then computed with PC-1), typed
directly as K+, or generated at random.

Every table used and every intermediate value is printed, as the assignment
requires.

Run it with:  python3 main.py
"""

import random
import sys

import bits
import key_schedule
from des_tables import (
    DROPPED_BY_PC2,
    HALF_BITS,
    KEY_BITS,
    KPLUS_BITS,
    PARITY_BITS,
    PC1,
    PC2,
    ROUNDS,
    SHIFTS,
    format_table,
)

RULE = "=" * 72
THIN = "-" * 72


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
        except bits.InvalidBitsError as error:
            print("  [invalid input] %s\n" % error)


def ask_choice(prompt, choices):
    """Ask for one of the keys of `choices` (a dict of label -> value)."""
    def parse(raw):
        answer = raw.strip()
        if answer not in choices:
            raise bits.InvalidBitsError(
                "%r is not one of the options; type %s"
                % (answer, " or ".join(sorted(choices)))
            )
        return choices[answer]

    return ask(prompt, parse)


def parse_key(raw):
    """Read the 64-bit key: 8 characters, or 16 hexadecimal digits."""
    text = raw.strip()
    compact = "".join(text.split())
    if len(compact) == 16 and all(c in "0123456789abcdefABCDEF" for c in compact):
        return bits.from_hex(compact, KEY_BITS), None
    if len(text) == 8:
        try:
            # One byte per character: the key is 8 symbols, 64 bits.
            return bits.from_bytes(text.encode("latin-1", "strict")), text
        except UnicodeEncodeError as error:
            raise bits.InvalidBitsError(
                "the character %r has no single-byte code, so it cannot be "
                "one of the 8 symbols of a DES key; use characters with an "
                "ASCII code, or give the key as 16 hexadecimal digits"
                % text[error.start]
            )
    raise bits.InvalidBitsError(
        "the key must be 8 characters (64 bits, one byte per character) or "
        "16 hexadecimal digits; %d character(s) given" % len(text)
    )


def parse_kplus(raw):
    """Read K+: 56 bits as 0s and 1s, or 14 hexadecimal digits."""
    compact = "".join(raw.split())
    if len(compact) == 14:
        return bits.from_hex(compact, KPLUS_BITS)
    return bits.from_binary(raw, KPLUS_BITS)


def show_key(key, characters):
    """Print the 64-bit key, with the ASCII codes when it came from text."""
    print("  The key K (64 bits):")
    if characters is not None:
        print("    character " + "  ".join("%3s" % c for c in characters))
        print("    ASCII     " + "  ".join("%3d" % ord(c) for c in characters))
    print("    hex       %s" % bits.to_hex(key))
    print("    bits      %s" % bits.group(key[:32], 8))
    print("              %s" % bits.group(key[32:], 8))
    print()


def show_pc1(key, kplus):
    """Print PC-1, the bits it discards, and the resulting K+."""
    print(THIN)
    print("Step 1 - PC-1: K  ->  K+   (56 of the 64 bits, reordered)")
    print(THIN)
    print(format_table(PC1, 7, "  Table PC-1:"))
    print()
    print("  The 8 bits PC-1 leaves out are the parity bits of the key -")
    print("  positions %s - which carry no key material."
          % ", ".join(str(position) for position in PARITY_BITS))
    print("    parity bits of K: %s"
          % " ".join(str(key[position - 1]) for position in PARITY_BITS))
    print()
    print("  K+ (56 bits, in groups of 7):")
    print("    %s" % bits.group(kplus, 7))
    print("    hex %s" % bits.to_hex(kplus))
    print()


def show_halves(kplus):
    """Print C_0 and D_0, the two halves K+ is split into."""
    c0, d0 = key_schedule.split(kplus)
    print(THIN)
    print("Step 2 - split K+ into two halves of 28 bits")
    print(THIN)
    print("  C0 = %s" % "".join(str(bit) for bit in c0))
    print("  D0 = %s" % "".join(str(bit) for bit in d0))
    print()
    return c0, d0


def show_shift_schedule():
    """Print the rotation schedule LS_i."""
    print(THIN)
    print("Step 3 - the rotation schedule LS_i")
    print(THIN)
    print("    round  " + " ".join("%2d" % (i + 1) for i in range(ROUNDS)))
    print("    shift  " + " ".join("%2d" % shift for shift in SHIFTS))
    print("  The sixteen shifts add up to %d, the length of a half, so after"
          % sum(SHIFTS))
    print("  round 16 the halves are back where they started: C16 = C0.")
    print()


def show_rounds(records):
    """Print every round: the shift, the two halves, and the round key."""
    print(THIN)
    print("Step 4 - the rounds: C_i = LS_i(C_i-1), D_i = LS_i(D_i-1),")
    print("         then K_i = PC-2(C_i D_i)")
    print(THIN)
    print(format_table(PC2, 6, "  Table PC-2:"))
    print()
    print("  PC-2 keeps 48 of the 56 bits; the ones it never names -")
    print("  positions %s of C_i D_i - are dropped in every round."
          % ", ".join(str(position) for position in DROPPED_BY_PC2))
    print()

    for record in records:
        index = record["round"]
        print("  Round %d   (rotate both halves left by %d)"
              % (index, record["shift"]))
        print("    C%-2d = %s" % (index - 1, _text(record["previous_c"])))
        print("    D%-2d = %s" % (index - 1, _text(record["previous_d"])))
        print("    C%-2d = %s" % (index, _text(record["c"])))
        print("    D%-2d = %s" % (index, _text(record["d"])))
        print("    K%-2d = %s" % (index, bits.group(record["key"], 6)))
        print("          hex %s" % bits.to_hex(record["key"]))
        print()


def _text(block):
    return "".join(str(bit) for bit in block)


def show_summary(records, pairs):
    """Print the sixteen round keys together, and the closing check."""
    print(THIN)
    print("The sixteen round keys")
    print(THIN)
    for record in records:
        print("  K%-2d = %s   (%s)"
              % (record["round"], bits.group(record["key"], 6),
                 bits.to_hex(record["key"])))
    print()
    closes = key_schedule.check_rotations_close(pairs)
    print("  Check: C16 = C0 and D16 = D0 ... %s"
          % ("yes" if closes else "NO - the schedule is wrong"))
    print()


def run_schedule(kplus):
    """Print steps 2 to 4 and the summary, starting from K+."""
    show_halves(kplus)
    show_shift_schedule()
    records = key_schedule.schedule(kplus)
    show_rounds(records)
    show_summary(records, key_schedule.halves(kplus))


def from_full_key(key, characters):
    """Task 2.5 starting from the 8-character key: PC-1 first, then K+."""
    print()
    print(RULE)
    print("Task 2.5 - the sixteen round keys of DES, starting from the key")
    print(RULE)
    show_key(key, characters)
    kplus = key_schedule.permuted_choice_1(key)
    show_pc1(key, kplus)
    run_schedule(kplus)


def from_kplus(kplus):
    """Task 2.5 exactly as stated: K+ is given, the round keys are wanted."""
    print()
    print(RULE)
    print("Task 2.5 - the sixteen round keys of DES, starting from K+")
    print(RULE)
    print("  K+ (56 bits, in groups of 7):")
    print("    %s" % bits.group(kplus, 7))
    print("    hex %s" % bits.to_hex(kplus))
    print()
    run_schedule(kplus)


def menu_key():
    key, characters = ask(
        "Key - 8 characters or 16 hexadecimal digits: ", parse_key
    )
    from_full_key(key, characters)


def menu_kplus():
    kplus = ask(
        "K+ - 56 bits (0s and 1s) or 14 hexadecimal digits: ", parse_kplus
    )
    from_kplus(kplus)


def menu_random():
    key = [random.randint(0, 1) for _ in range(KEY_BITS)]
    print("\n  A random 64-bit key was generated: %s" % bits.to_hex(key))
    from_full_key(key, None)


def menu_tables():
    print()
    print(RULE)
    print("The tables of the DES key schedule")
    print(RULE)
    print(format_table(PC1, 7, "  PC-1 - chooses 56 of the 64 bits of K:"))
    print()
    print("    dropped (parity bits): %s"
          % ", ".join(str(position) for position in PARITY_BITS))
    print()
    print("  LS_i - the left rotation of round i:")
    print("    round  " + " ".join("%2d" % (i + 1) for i in range(ROUNDS)))
    print("    shift  " + " ".join("%2d" % shift for shift in SHIFTS))
    print()
    print(format_table(PC2, 6, "  PC-2 - chooses 48 of the 56 bits of C_i D_i:"))
    print()
    print("    dropped: %s"
          % ", ".join(str(position) for position in DROPPED_BY_PC2))
    print()


def main():
    print(RULE)
    print("Laboratory Work No. 4 - DES, task 2.5: the sixteen round keys")
    print(RULE)

    menu = {"1": menu_key, "2": menu_kplus, "3": menu_random,
            "4": menu_tables, "0": None}
    while True:
        print("\n  1) Enter the key (8 characters or 16 hex digits)")
        print("  2) Enter K+ directly (56 bits)")
        print("  3) Generate a random key")
        print("  4) Show the tables PC-1, LS_i and PC-2")
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
