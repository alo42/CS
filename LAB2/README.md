# Laboratory Work No. 2 — Cryptanalysis of a Monoalphabetic Cipher

Breaking variant 16 by frequency analysis: an intercepted English message,
enciphered with a monoalphabetic substitution in which only the letters were
replaced.

## Running

No dependencies beyond the standard library (Python 3.6+):

```bash
python3 main.py analyse      # frequency tables of the ciphertext
python3 main.py walkthrough  # the manual attack, one deduction at a time
python3 main.py solve        # recover the key automatically
python3 main.py decrypt      # the plaintext, using the recovered key
```

To run the checks:

```bash
python3 -m unittest discover -s tests
```

`solve` needs an English word list. It uses `/usr/share/dict/words` (present on
macOS and most Linux systems); set `ENGLISH_WORD_LIST` to point somewhere else.
The other three commands need no word list.

## Files

| File | Contents |
| --- | --- |
| `ciphertext.txt` | the intercepted cryptogram, variant 16 |
| `plaintext.txt` | the recovered message |
| `english.py` | English letter frequencies (table 2.2) and the language model |
| `frequency.py` | letter, bigram, trigram and word statistics |
| `substitution.py` | applying a full or partial key to a text |
| `walkthrough.py` | the eight deductions that break this cryptogram |
| `solver.py` | automatic key recovery by hill climbing |
| `main.py` | the command-line program |
| `tests/test_cryptanalysis.py` | checks, including breaking a freshly made cipher |

## Result

The key, written as the plaintext letter that each ciphertext letter stands for:

```
ciphertext  a b c d e f g h i j k l m n o p q r s t u v w x y z
plaintext   b q f u j y n c r g v k z o d s h w l a p e t i x m
```

The message is a passage on how the telegraph reshaped nineteenth-century
cryptology, opening *"The first one was waiting in the wings."* and ending on
Thomas Jefferson's wheel cypher.

The enciphering key is not random: it is the affine cipher

```
c = (7x + 19) mod 26
```

Nothing in the attack relies on that — the key was recovered letter by letter
from the frequencies — but it is a useful confirmation that the solution is
right, since a wrong key would show no such structure.

## How the attack goes

1. **Count.** `V` is the most frequent letter at 12.50%, against 12.70% for
   `E` in English, and the profile follows English closely in shape.
2. **Find the giveaway word.** `WQV` occurs 43 times as a word and 67 times as
   a trigram — `THE`.
3. **Use the short words.** `WN` (8) reads `T-` and can only be `TO`; `NC`
   (28, the commonest two-letter word) is then `OF`. `T` alone 15 times plus
   `TGO` (18) gives `AND`, and `XG` (13) gives `IN`, confirmed by `XW` (19)
   reading `IT`.
4. **Read what appears.** `WVSVJITUQ` becomes `TELEGRAPH`, `RTP` becomes
   `WAS`, `HIFUWNJITUQF` becomes `CRYPTOGRAPHY`.
5. **Mop up the rare letters.** Each of the last seven is fixed by one word:
   `XZUNPPXAXSXWF` = `IMPOSSIBILITY`, `IVBDXIVZVGWP` = `REQUIREMENTS`,
   `ZTENI` = `MAJOR`, `VTPXSFPNSKVO` = `EASILY SOLVED`, `LVFRNIO` = `KEYWORD`,
   `PUVHXTSXMVO` = `SPECIALIZED`, `VYHVUW` = `EXCEPT`.

`python3 main.py walkthrough` replays all eight steps, printing the message
after each one with the letters recovered so far in lowercase.

The same key is also found mechanically by `python3 main.py solve`, which hill-
climbs from the frequency-matched key, scoring candidates on letter-pair
statistics and on how many real English words they produce.
