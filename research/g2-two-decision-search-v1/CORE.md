# G2.4 two-decision search / REFACTOR consumer

**Terminal:** `GETSTEPS_ZERO_LABEL_SPINE_ONLY`

G2.4 **cannot** be checked from this capsule. The literature-prescribed
REFACTOR consumer is GetSteps (Zhou et al., ICLR 2024, App. A.3): exact
compressed-proof step sequences. That count is **0**. A coarser
label-spine (`eldif` as an essential child of `orbi12i`) hits `inundif`
once; that only shows two P1 names co-occur, not that the compiled
`elsymdif` cut body is reused. Finite search never places a `cut-lemma-*`
in a successful derivation. Save-value is 0. GitHub was **not** checked.

This capsule **ADOPTS** the REFACTOR (ICLR 2024) *consumer* and **REJECTS** its
neural extractor. Evaluation is whether a compiled 2-step cut DAG occurs as a
**proper subtree** of a later P1-closed proof, not whether a held-out conclusion
is a 1-step identity of the lemma (Mooney 1989: macros help only if search uses
them). Later theorems are scored with vs without the lemmas (Kaliszyk & Urban
2015). Recurrence is scored by Wernhard save-value `(n-1)*(s-1)` on the held-out
forest.

Native 22/22 ordinary-cut admission is already on the custodian prefix (PR #179).
This run does not re-admit them.

## Parents

| Parent | Disposition |
|---|---|
| Mooney, IJCAI 1989, limited chaining | ADOPT: learned lemmas used at most once per derivation |
| Kaliszyk & Urban, JSC 2015 | ADOPT: later theorems WITH vs WITHOUT extra lemmas |
| Zhou et al., ICLR 2024 / arXiv 2402.17032 REFACTOR subroutine | ADOPT consumer (2-step DAG subtree); REJECT GNN extractor |
| Wernhard 2025/2026 DAG save-value | ADOPT scoring; no neural selector |

## Measured

- 43449 held-out theorems after `pssdif`; 1093 P1-closed by used-assertion ⊆ prefix
- **1** native-verified proper subtree: `inundif` contains `eldif` ⊢ `orbi12i` (`ocm-cut-04/05`)
- 3 whole-proof spine hits excluded as 1-step identity
- 48 finite-search invocations; lemma actions fire after matcher patch; **no** successful derivation uses `cut-lemma-*`
- save-value 0 (`SINGLE_HELD_OUT_USE`)

## Bank

Published search bank = syntax closure of the later goal **plus** the 22 lemma
conclusions. Matcher repair: `native_match`'s `typed_terms` (not only
`finite_search.T`) extended with `V*` atoms, `\` / `/_\`, and `(/)`.

[Result](RESULT.md) · [summary](SUMMARY.json) · [replay](records/replay-01/RESULT.json)
