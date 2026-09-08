# Native lemma admission

Pinned prefix: `CUSTODIAN-PREFIX.mm` sha256
`b12e2bac9f6fe8a6fda972d74dbfb21c2e85cd86040fd447c685c693ae0af1cd`
(1,806,915 bytes, last `$p` is `pssdif`). Checker: vendor `mmverify.py`,
proofs verified only from each `cut-lemma-XX` label.

| Quantity | Count |
|---|---:|
| Unique non-alias cuts | 22 |
| Native calls | 22 |
| `NATIVE_VERIFIED` | 22 |
| `NATIVE_REJECTED` | 0 |
| Zero-premise ordinary lemmas | 7 |
| Held-out theorems after `pssdif` | 43462 |
| Alpha matches in first 5,000 | 0 |
| Cut-lemma labels used on `inssdif0` search | 0 |

Zero-premise sources: `elsymdif`, `ssdifim`, `ssdifsym`, `indif1`, `dif32`,
two `sscon34b` variants. These are not the named training theorems: P1 `indif1`
and P1 `dif32` have different statements from the extracted cuts.

`inssdif0` is P1-closed: its published proof verifies on the prefix with no
added lemmas. Bounded search on a 9-wff bank produced 25 actions and
`NO_PROOF_WITHIN_BOUND` on both P1 and P1+lemmas (bank too small to ground
`ssdif0`/`indif2`). That is incomplete search, not a capability residual.

G2.4 remains unchecked. Next: enlarge the bank to the official `inssdif0`
intermediates, then hunt P1-closed held-out theorems whose 2-step
`incom`/`difeq1i` or `uncom`/`difeq2i` pattern matches an admitted cut.
