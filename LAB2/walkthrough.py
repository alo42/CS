"""The manual attack on variant 15, one deduction at a time.

Each stage records what was noticed in the text and the substitutions that
followed from it. Replaying them reproduces the step-by-step breaking
described in section 2.3 of the laboratory work: after every stage the
letters already recovered appear in lowercase and the ones still unknown
stay as uppercase ciphertext.
"""

STAGES = (
    (
        "The three-letter group WQV occurs 35 times - far more than any "
        "other word. The commonest three-letter word in English is THE, and "
        "V is also the most frequent letter of the cryptogram (13.84%, "
        "against 12.70% for E in English).",
        {"w": "t", "q": "h", "v": "e"},
    ),
    (
        "Among two-letter words, NC appears 19 times, XG 12 and WN 11. With "
        "W already standing for T, WN must be TO. The other two are then OF "
        "and IN, which also agrees with N being the fourth most frequent "
        "letter and matching O.",
        {"n": "o", "c": "f", "x": "i", "g": "n"},
    ),
    (
        "TGO is the second most frequent three-letter word (16 times) and "
        "now reads a-n-d: AND. T is the third most frequent letter of the "
        "cryptogram, which fits A.",
        {"t": "a", "o": "d"},
    ),
    (
        "The title of the passage, WQV WVSVJITUQ, now reads THE TE-E--A-H. "
        "The subject of the text and the pattern of repeated letters make "
        "TELEGRAPH the only sensible reading.",
        {"s": "l", "j": "g", "i": "r", "u": "p"},
    ),
    (
        "TP occurs 5 times and reads A-. It cannot be AT, since T is "
        "already W, so TP is AS and P is S. This also makes XP read IS, and "
        "RTP (5 times) read -AS, that is WAS, so R is W.",
        {"p": "s", "r": "w"},
    ),
    (
        "The long word HIFUWNJITUQF now reads -R-PTOGRAPH-. The text is "
        "about secret writing, so this is CRYPTOGRAPHY: H is C and F is Y.",
        {"h": "c", "f": "y"},
    ),
    (
        "ZTOV reads -ADE, so Z is M (MADE). PTZDVS then reads SAM-EL, so D "
        "is U, giving the name SAMUEL - Samuel Morse, who fits the subject.",
        {"z": "m", "d": "u"},
    ),
    (
        "Only the rare letters are left, and each is now fixed by a single "
        "word: AV = -E is BE, KNSDZXGNDP = -OLUMINOUS is VOLUMINOUS, "
        "VYUVGPV = E-PENSE is EXPENSE, MNGV = -ONE is ZONE, VBDTS = E-UAL "
        "is EQUAL, EDPW = -UST is JUST and LVFP = KEYS fixes L as K.",
        {"a": "b", "k": "v", "y": "x", "m": "z", "b": "q", "e": "j", "l": "k"},
    ),
)


def replay():
    """Yield (stage number, explanation, key so far) after each deduction."""
    key = {}
    for number, (explanation, substitutions) in enumerate(STAGES, start=1):
        key.update(substitutions)
        yield number, explanation, dict(key)
