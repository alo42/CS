# Laboratory Work No. 4 — Block Ciphers. The DES Algorithm

Task 2.5: *in the DES algorithm K+ is given; determine all sixteen round keys
K₁ … K₁₆.* The assignment selects the task by `nr_sarcina = n mod 11`, and
with n = 16 in the group register that is `16 mod 11 = 5`.

## Running

No dependencies beyond the standard library (Python 3.6+):

```bash
python3 main.py
```

The program offers four entries:

1. enter the key — 8 characters, or 16 hexadecimal digits — and K+ is
   obtained with PC-1 before the schedule is built;
2. enter K+ directly, as 56 bits or 14 hexadecimal digits — task 2.5 as it is
   stated;
3. generate a random key;
4. print the tables PC-1, LS_i and PC-2.

Every table used and every intermediate value is printed: the ASCII codes of
the key characters, the parity bits PC-1 discards, K+, C₀ and D₀, and then for
each of the sixteen rounds the shift applied, both halves before and after it,
and the round key PC-2 extracts.

To run the checks:

```bash
python3 -m unittest discover -s tests
```

## Files

| File | Contents |
| --- | --- |
| `bits.py` | bit strings and the operations DES performs on them |
| `des_tables.py` | PC-1, the rotation schedule LS_i and PC-2 |
| `key_schedule.py` | K+ → C₀D₀ → the sixteen round keys, with every intermediate value |
| `main.py` | the interactive program |
| `tests/test_key_schedule.py` | checks against the standard worked example, and structural properties |
| `tests/des_reference.py` | the DES data path — used only to verify the key schedule |
| `tests/test_known_answer.py` | published test vectors encrypted with the schedule's round keys |
| `report.html` | the report, ready to be printed to PDF |

## The key schedule

```
K  --PC-1-->  K+  -->  C_0 D_0
C_i = LS_i(C_{i-1})        D_i = LS_i(D_{i-1})
K_i = PC-2(C_i D_i)
```

PC-1 keeps 56 of the 64 bits of the key, dropping positions 8, 16, …, 64 —
the parity bits. The sixteen shifts LS_i add up to 28, the length of a half,
so C₁₆ = C₀ and D₁₆ = D₀. PC-2 keeps 48 of the 56 bits of C_iD_i, dropping
positions 9, 18, 22, 25, 35, 38, 43 and 54.

## Verification

The implementation reproduces the standard worked example — key
`133457799BBCDFF1`, K+ = `F0CCAAF556678F`, K₁ = `1B02EFFC7072`,
K₁₆ = `CB3D8B0E17F5` — for all sixteen round keys, not only the ones usually
quoted.

Because a round key cannot be checked against anything on its own,
`tests/des_reference.py` adds the DES data path (IP, E, the S-boxes, P, IP⁻¹)
and drives it with the round keys this program produces. It reproduces three
published plaintext/ciphertext pairs, which a single wrong bit anywhere in the
schedule would break. That file is a test fixture, not part of task 2.5.
