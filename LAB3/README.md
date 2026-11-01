# Laboratory Work No. 3 — Polyalphabetic Ciphers

Task 3.2: the Vigenère cipher over the Romanian alphabet (31 letters, coded
0 … 30). Variant 16 is an even number in the group register, so task 3.2 is
the one assigned; task 3.1 (Playfair) is for the odd numbers.

## Running

No dependencies beyond the standard library (Python 3.6+):

```bash
python3 main.py
```

The program asks for the operation (encrypt or decrypt), the key — at least 7
Romanian letters — and the message or the cryptogram, and prints the result
together with the table of the transformation, letter by letter. The second
menu entry prints the Tabula Recta of the 31 letters.

To run the checks:

```bash
python3 -m unittest discover -s tests
```

## Files

| File | Contents |
| --- | --- |
| `romanian_alphabet.py` | the 31-letter encoding and all input validation |
| `vigenere.py` | the key stream, encryption, decryption, the Tabula Recta |
| `main.py` | the interactive program |
| `tests/test_vigenere.py` | checks, including the example worked out in the assignment |
| `report.html` | the report, ready to be printed to PDF |

## The cipher

```
c_i = (m_i + k_i) mod 31        m_i = (c_i - k_i) mod 31
```

`k_i` is the code of the letter of the key that falls on position `i`, the key
being repeated from the beginning once it runs out. A letter's code is its
position in the alphabet tuple, so no `ord()`/`chr()` appears in the cipher and
the Romanian diacritics need no special handling.

## Example

```
key        CRIPTOGRAFIE
plaintext  CRIPTOGRAFIAESTEARTADEAPASTRASECRETE
cryptogram GHRDMBNHALREIIÂȚTEARDKIȚCIÂFTFLȚRKÂJ
```

In this one message the plaintext letter `A` is enciphered as `A`, `E`, `T`,
`R`, `I` and `C`, and the ciphertext letter `I` stands for `A`, `E` and `S` —
which is exactly what a polyalphabetic cipher is for: the letter frequencies
of the language no longer pass through into the cryptogram.
