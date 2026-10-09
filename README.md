# Laboratory Work No. 1 — The Caesar Cipher (Romanian alphabet)

Python implementation of the two tasks of the laboratory work:

* **Task 1.1** — the Caesar cipher over the 31-letter Romanian alphabet, with one numeric key.
* **Task 1.2** — the same cipher over an alphabet permuted by a keyword (two keys).

## Running

No dependencies beyond the standard library (Python 3.6+):

```bash
python3 main.py
```

The program asks for the task, the operation (encryption or decryption), the key(s) and the
text, and keeps asking for any value it rejects.

To run the checks:

```bash
python3 -m unittest discover -s tests
```

## Files

| File | Contents |
| --- | --- |
| `romanian_alphabet.py` | the letter encoding of Table 2 and all input validation |
| `caesar.py` | the permuted alphabet, encryption and decryption |
| `main.py` | the interactive program for both tasks |
| `tests/test_ciphers.py` | checks, including the examples worked out by hand in the assignment |

## Short theory

### The Caesar cipher

Every letter is replaced by the letter `k` positions further along the alphabet. The same key
is used for both directions:

```
c = e_k(x) = (x + k) mod n
m = d_k(y) = (y - k) mod n
```

where `x` and `y` are the *positions of the letters in the alphabet* (starting from 0) and
`n` is the length of the alphabet. For the Romanian alphabet `n = 31`, so the key space is
`k ∈ {1, …, 30}` — only **30 keys**, which an attacker simply tries one after another
(exhaustive search).

### The Caesar cipher with a permutation

The alphabet is first reordered by a keyword: the distinct letters of the keyword, in the
order they appear, followed by the remaining letters of the alphabet in their natural order.
The shift is then applied over this new order, so a letter's numeric code is its position in
the *permuted* alphabet.

The key space becomes

```
31! × 30 = 246,685,159,625,337,684,531,766,886,400,000,000 ≈ 2.47 × 10^35
```

which rules out exhaustive search, but it is
still a **monoalphabetic substitution**: every plaintext letter always maps to the same
ciphertext letter, so the letter frequencies of the language survive into the ciphertext and
the cipher falls to frequency analysis.

## Implementation notes

* **The encoding is explicit.** `ALPHABET` is a tuple of the 31 letters in the order of
  Table 2, and a letter's code is its index in that tuple. Unicode code points are never
  used to compute a shift, as required.
* **One algorithm, two tasks.** `encrypt`/`decrypt` take the ordered alphabet as a
  parameter. Task 1.1 passes the natural alphabet; task 1.2 passes the permuted one. This is
  also why the tests can replay the assignment's own English examples through the same code.
* **Decryption is written portably** as `(y - k + n) % n`: Python's `%` already returns a
  non-negative remainder, but the `+ n` makes the formula correct in languages whose
  remainder can come out negative.
* **Ș/Ț with a cedilla** (`Ş`, `Ţ`) are folded onto the comma-below letters, and the input is
  first put through Unicode NFC normalization, so text typed on different keyboards is
  accepted.
* **Validation re-asks instead of crashing.** An out-of-range or non-numeric key, a keyword
  shorter than 7 letters, and a character outside the alphabet each produce a message that
  states the allowed values (and, for text, which character was rejected) and the program
  asks again.

## Checked against the assignment

The worked examples printed in the laboratory work are used as test vectors:

| Input | Keys | Expected | Alphabet |
| --- | --- | --- | --- |
| `BRUTEFORCEATTACK` | k = 17 | `SILKVWFITVRKKRTB` | English, n = 26 |
| `CIFRULCEZAR` | k = 3 | `FLIUXOFHCDU` | English, n = 26 |
| `CIFRULCEZAR` | k = 3, k₂ = `CRYPTOGRAPHY` | `PLKTXQPJYDT` | English, permuted |
| `CIFRULCEZAR` | k = 3 | `FKITXOFHÂBT` | Romanian, n = 31 |
