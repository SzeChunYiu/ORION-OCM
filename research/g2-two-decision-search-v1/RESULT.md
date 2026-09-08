# Two-decision / REFACTOR result

One-step identity of held-out conclusions with cut lemmas was not the test.
The consumer is non-neural REFACTOR: match each of the 22 compiled 2-step DAGs
as a subtree of a later P1-closed official proof, then (separately) run
2-decision finite-bank search with lemma conclusions in the bank and parent.

Prefix pin `b12e2bac9f6fe8a6fda972d74dbfb21c2e85cd86040fd447c685c693ae0af1cd`.
Native 22/22 admission is PR #179 (not rerun). GitHub G2.4 was not checked.

| Stage | Count |
|---|---:|
| Compiled 2-step DAGs | 22 |
| Held-out `$p` after `pssdif` | 43449 |
| Label-set P1-closed | 1093 |
| Prefilter trees built | 6 |
| Proper semantic-spine hits | 1 (`inundif`) |
| Whole-proof spine hits (excluded as 1-step) | 3 |
| Exact GetSteps hits | 0 |
| Native-verified proper hit | 1 (`inundif`, dummy `$d` restored) |
| Search invocations | 48 |
| `cut-lemma-*` in a successful derivation | 0 |
| Wernhard save-value | 0 |

`inundif` is after `pssdif`, not an acquisition theorem. Its official proof
contains `eldif` as an essential child of `orbi12i` — the 2-step DAG of
`ocm-cut-04` / `ocm-cut-05` — under a larger `uneqri` root. That is a proper
subtree replacement in the REFACTOR sense. The same proof natively verifies on
CUSTODIAN-PREFIX once `$d x A $. $d x B $.` is emitted. Three later proofs
(`bnj1138`, `sbcori`, `ssinss2d`) have the 2-step as the *whole* tree; those
are the 1-step identity case and were excluded.

Save-value on the held-out forest is `(1-1)*(2-1) = 0`: a single later use does
not compress. That is `SINGLE_HELD_OUT_USE`, not a large recurrence.

## Search (Kaliszyk / Mooney)

Bank: syntax closure of the later goal plus the 22 lemma conclusions
(published; official held-out intermediates were not used as training).

Matcher repair (one bug): `finite_search` calls `native_match.match`, which
loads its own `typed_terms`. Patching only `finite_search.T` left lemmas at
`lemma_actions=0`. Patching `native_match.T` to admit class `\` / `/_\` / `(/)`
and extra atoms produced **8 lemma actions** on `inundif` (20 vs 12 P1-only
actions). Seven 0-premise lemmas relaxed as unused bank facts. No derivation of
a held-out *goal* contained a `cut-lemma-*` label at `max_decisions` 2 or 3
(Mooney: macros that do not appear in the successful proof do not help).
Ablation compiled the lemmas (charged) then searched P1 only and matched P1.

Targets: `inundif` plus five chronological P1-closed theorems (`ndisj` …
`inssdif0OLD`), not lemma conclusions.

## What G2.4 may claim

G2.4 **cannot** be checked. GetSteps replacements are 0. Label-spine
recurrence of `eldif`/`orbi12i` in `inundif` is not the compiled cut body.
Finite search did not consume a lemma. Save-value is 0. GitHub was not
flipped.

[summary](SUMMARY.json) · [replay](records/replay-01/RESULT.json)
