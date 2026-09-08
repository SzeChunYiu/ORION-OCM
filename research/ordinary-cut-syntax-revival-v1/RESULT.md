# Syntax revival result

All 76 frozen proposals were screened in original order. Ground admission uses
P1 syntax axioms rather than the tiny `A C_ B` / `(ph /\ ps)` fragment.

| Stage | Count |
|---|---:|
| Proposals replayed | 76 |
| Ground admitted | 63 |
| Still UNKNOWN | 13 |
| `ALIAS_FOUND_PROOF_READY` | 39 |
| `SCREENED_NEGATIVE_IN_DOMAIN` | 24 |
| Aliases using cut premises | 0 |
| Native calls | 0 |

Matcher work: 272,349 P1 visits, 3,584,972 type checks, 1,243,338 token
states, wall 184.7 s, peak RSS 54 MiB.

The 39 aliases are existing P1 theorems (`ssinss1`, `inss`, `symdifeq1`, …)
and do not use the cut's extra premises. The 24 negatives passed syntax and are
not one-step P1 aliases. Those 24 are the next causal-reuse candidates: compile
as ordinary derived lemmas, restart, held-out family, removal ablation.

Not claimed: `CAUSAL_METHOD_REUSE_SUPPORTED`, novelty, native admission.
