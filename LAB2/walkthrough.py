"""The manual attack on variant 16, one deduction at a time.

Each stage records what was noticed in the text and the substitutions that
followed from it. Replaying them reproduces the step-by-step breaking
described in section 2.3 of the laboratory work: after every stage the
letters already recovered appear in lowercase and the ones still unknown
stay as uppercase ciphertext.
"""

STAGES = (
    (
        "the giveaway word",
        "The three-letter group WQV occurs 43 times as a word and 67 times "
        "as a trigram - far more than anything else in the cryptogram. The "
        "commonest three-letter word in English is THE, and V is also the "
        "most frequent letter here (12.50%, against 12.70% for E in "
        "English).",
        {"w": "t", "q": "h", "v": "e"},
    ),
    (
        "TO and OF",
        "WN occurs 8 times and now reads T-. The only common English "
        "two-letter word beginning with T is TO, so N is O - which agrees "
        "with N being the fourth most frequent letter at 7.32%, against "
        "7.51% for O. NC, the most frequent two-letter word at 28 "
        "occurrences, then reads O- and must be OF.",
        {"n": "o", "c": "f"},
    ),
    (
        "A and AND",
        "T stands alone as a word 15 times, and English has only two "
        "one-letter words, A and I. TGO is the second most frequent "
        "three-letter word (18 times), exactly as AND is in English; "
        "reading T as A makes TGO fit AND and fixes two more letters.",
        {"t": "a", "g": "n", "o": "d"},
    ),
    (
        "IN and IT",
        "XG (13 times) now reads -N. It cannot be AN, because A is already "
        "T, so X is I and XG is IN. This is confirmed at once by XW, the "
        "second most frequent two-letter word at 19 occurrences, which now "
        "reads IT.",
        {"x": "i"},
    ),
    (
        "TELEGRAPH",
        "WVSVJITUQ appears 8 times and reads TE-E--A-H. The repeated E in "
        "that pattern and the subject of the passage leave only one "
        "reading: TELEGRAPH.",
        {"s": "l", "j": "g", "i": "r", "u": "p"},
    ),
    (
        "WAS, AS and IS",
        "RTP occurs 7 times and reads -AS, which can only be WAS. That "
        "makes P equal to S, and the two-letter words TP and XP then read "
        "AS and IS, both of which are common English words.",
        {"p": "s", "r": "w"},
    ),
    (
        "CRYPTOGRAPHY, MORE and USE",
        "HIFUWNJITUQF (4 times) reads -R-PTOGRAPH-, which in a text about "
        "secret writing can only be CRYPTOGRAPHY. ZNIV then reads -ORE and "
        "is MORE, and DPV reads -SE and is USE.",
        {"h": "c", "f": "y", "z": "m", "d": "u"},
    ),
    (
        "the rare letters",
        "Seven letters are left, and each is fixed by a single word in "
        "which it is the only remaining unknown: XZUNPPXAXSXWF = "
        "IMPOSSIBILITY, IVBDXIVZVGWP = REQUIREMENTS, ZTENI = MAJOR, "
        "VTPXSFPNSKVO = EASILY SOLVED, LVFRNIO = KEYWORD, PUVHXTSXMVO = "
        "SPECIALIZED and VYHVUW = EXCEPT.",
        {"a": "b", "b": "q", "e": "j", "k": "v", "l": "k", "m": "z", "y": "x"},
    ),
)


def replay():
    """Yield (stage number, title, explanation, key so far) after each step."""
    key = {}
    for number, (title, explanation, substitutions) in enumerate(STAGES, start=1):
        key.update(substitutions)
        yield number, title, explanation, dict(key)
