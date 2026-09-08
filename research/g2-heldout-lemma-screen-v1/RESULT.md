# Causal lemma-reuse result

Producer compiled 22 unique cuts, wrote sealed ordinary `$p` rows, and exited.
Four later OS processes loaded only sealed state and screened held-out family
H1 (ordinals 4224–4233: `ndisj` … `dif0`). Acquisition theorems were not used
as evaluation.

| Stage | Count |
|---|---:|
| SCREENED_NEGATIVE occurrences | 24 |
| Unique canonical bodies compiled | 22 |
| Two semantic P1 steps each | 22 |
| COMMUTE_TRANSPORT | 9 |
| P1_CHAIN | 10 |
| DEFINITION_UNFOLDING | 3 |
| Held-out theorems (after 4223) | 10 |
| Lemma identities consumed on held-out | 0 |
| Native calls | 0 |

| Arm | Process | Installed lemmas | Held-out one-step | Lemma consumed | Wall |
|---|---:|---:|---|---|---:|
| RESET_OCM / P1 only | 71368 | 0 | 10 SCREENED_NEGATIVE | no | 17.05 s |
| P1 + lemmas | 71652 | 22 | 10 SCREENED_NEGATIVE | no | 17.45 s |
| Ablation (lemmas loaded then disabled) | 72130 | 0 (22 disabled) | 10 SCREENED_NEGATIVE | no | 16.91 s |
| Metamath parent (same `$p` rows) | 72459 | 22 | 10 SCREENED_NEGATIVE | no | 17.18 s |

Ablation matched RESET. The conventional parent received the same lemmas and
matched P1+lemmas. There was no capability delta to remove.

Producer wall 0.027 s, lemma JSON 73 841 bytes, Metamath fragment 5 864 bytes.
Outer replay wall 69.0 s. Child RSS ≈ 54 MiB. Nested costs are not additive
and are not a lifetime total.

Native: frozen PREFIX pin
`9fbdc890cb89ad6805ced1fac23a1e9942775d5a7f60296bc0e064102806e411` authorizes
4 095 prefix theorems only. DAG proofs replay through `typed_emit`. Successor
library checking is UNKNOWN, not a fabricated pass.

All 22 lemmas are two-logical-step P1 compositions (commutativity transport,
definition unfolding, or existing-assertion chaining). That is
`NO_NEW_ABSTRACTION`, not a one-step primitive alias (those 39 stayed in the
revival). Held-out one-step matching is the registered screening domain; a
broader 2-decision bank search was not registered.

Not claimed: `CAUSAL_METHOD_REUSE_SUPPORTED`, novelty, native admission,
lifetime cost advantage.
