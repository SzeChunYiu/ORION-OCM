# Extra negatives after complete matching

Replay-01 stopped after 63 of 76 screens. Its last 13 rows are
`UNKNOWN_RESOURCE`. Replay-02 finished those 13: five became one-step aliases
(`sscon34b` × 2, `rcompleq` × 3) and eight became in-domain negatives. Those
eight unique bodies are the gap between 24/22 and 32/30.

Pinned prefix: `CUSTODIAN-PREFIX.mm` sha256
`b12e2bac9f6fe8a6fda972d74dbfb21c2e85cd86040fd447c685c693ae0af1cd`
(1,806,915 bytes, last `$p` is `pssdif`). Checker: vendor `mmverify.py`,
proofs verified only from each `extra-cut-XX` label.

| Quantity | Count |
|---|---:|
| Replay-01 negatives / unique | 24 / 22 |
| Replay-02 negatives / unique | 32 / 30 |
| Extra unique bodies | 8 |
| Native calls | 8 |
| `NATIVE_VERIFIED` | 8 |
| `NATIVE_REJECTED` | 0 |
| Two-semantic-step P1 compositions | 8 |
| Exact named-P1 statement matches | 0 |
| Distinct compiled statements | 5 |
| Statements already in #179 | 1 |
| New statements vs #179 | 4 |
| New zero-premise lemmas | 1 |

| Label | Source | Ordinal | Hyps | Semantic steps | Abstraction | Statement role |
|---|---|---:|---:|---|---|---|
| `extra-cut-00` | `sscon34b` | 4158 | 2 | `bilani`+`sseq12d` | `P1_CHAIN` | Same conclusion as `cut-lemma-21` |
| `extra-cut-01` | `sscon34b` | 4158 | 1 | `sscon`+`imbitrid` | `P1_COMPOSITION` | One direction of complement reversal |
| `extra-cut-02` | `sscon34b` | 4158 | 3 | `sseq12d`+`imbitrid` | `P1_COMPOSITION` | Same statement as `extra-cut-01` |
| `extra-cut-03` | `rcompleq` | 4159 | 0 | `sscon34b`+`ancoms` | `P1_COMPOSITION` | New zero-premise; `ancoms`-swap of named `sscon34b` |
| `extra-cut-04` | `rcompleq` | 4159 | 2 | `ancoms`+`anbi12d` | `P1_COMPOSITION` | `eqss` unfolding of named `rcompleq` |
| `extra-cut-05` | `rcompleq` | 4159 | 1 | `sscon34b`+`anbi12d` | `P1_COMPOSITION` | Same statement as `extra-cut-04` |
| `extra-cut-06` | `rcompleq` | 4159 | 1 | `ancom`+`bitrid` | `P1_COMPOSITION` | Conjunct swap of `extra-cut-04` |
| `extra-cut-07` | `rcompleq` | 4159 | 3 | `anbi12d`+`bitrid` | `P1_COMPOSITION` | Same statement as `extra-cut-06` |

Compile path is RAW `proposal.target` / `proposal.hypotheses` / `proposal.proof`,
not a V0/V1/V2 `typed_emit` remap. Named `sscon34b` and `rcompleq` sit in the
prefix before `pssdif`; the extracted cuts are two-step rearrangements of
those theorems (A/B swap, one-direction, or equality-as-mutual-inclusion),
not one-step query aliases and not new named statements.

The useful library enlargement for a later 2-decision search is the new
zero-premise `extra-cut-03` plus the four new statements. `extra-cut-00`
does not add a new conclusion. G2.4 remains unchecked.
