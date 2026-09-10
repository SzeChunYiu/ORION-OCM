# M2-P1 hidden-family ecology — registered design (no scored run in this commit)

Lane `LANE_M2_TRAVERSAL_CAPITAL_OPUS`. Parent #323 §5–§6. Successor to the M2
negatives in [RESULT.md](RESULT.md). **Design only.** Arms, gates, metrics and the
claim ceiling are registered here *before* any scored execution.

## The requirement M2-N2 forces

M2-N2 showed that on the M1 ecology a rule fit on developmental history is
indistinguishable from the same rule fit on the declared grammar alone. That is not a
defect of OCM; it is a property of the benchmark: **the agent is handed the complete
generative grammar, so the optimal structural prior is derivable a priori and history
is redundant by construction.**

Testing developmental transfer therefore requires an ecology carrying **latent family
structure that is not derivable from the declared grammar** — so that observed history
is the only available source of the prior.

## Entry gate (blocking, runs before any scored arm)

Generate the ecology, then run the **existing** feature-sufficiency ladder
(`m2_probe_v3_feature_sufficiency.py`) against it. Required:

```text
free-fit accuracy  ~= chance          (grammar alone recovers nothing)
dev-fit  accuracy  >> chance          (history recovers the family)
```

If free-fit tracks dev-fit, **the generator is wrong and the generator is fixed** — not
the arms. This is M2-N2's own control reused as a precondition, which is what stops the
same failure recurring in a new costume.

Two further generator constraints, both learned from the M2 negatives:

1. **Length-distribution parity.** The protected slice must match the ecology's length
   distribution. M1's 7/8-at-max slice against a 68 % base rate is what let a constant
   impersonate a structural prior (M2-N1, M2-N4). Parity is asserted, not assumed.
2. **Ordering, not pruning, is the headline.** A wrong hard-prune deletes the answer
   (M2-N3: the value function is a cliff). `ORDER` is the primary integration mode;
   `PRUNE` is secondary and reported separately.

## Arms

| arm | history | purpose |
|---|---|---|
| `RESET` | none | anchor |
| `LIBRARY_ONLY` | solved objects only | solution capital |
| `FAMILY_PRIOR_ORDER` | family prior from dev traversal | **headline** |
| `FAMILY_PRIOR_PRUNE` | same | cliff check, secondary |
| `FREE_FIT_ORDER` | grammar only | M2-N2 control |
| `SHUFFLED_HISTORY` | labels permuted | negative control |
| `ORACLE_FAMILY` | true family id | calibration only |
| `ORDINARY_ADAPTIVE_PARENT` | same history, no gate | strong parent |

Targets must be **new**: held out from history, disjoint normal forms, externally
verified by the independent checker, exactly as the M1 harness already enforces.

## Frozen terminals

- `NO_FAMILY_HEADROOM` — even `ORACLE_FAMILY` does not reduce burden. Generator is
  redesigned; no architecture conclusion.
- `FAMILY_PREDICTABLE_WITHOUT_HISTORY` — entry gate fails. Generator defect.
- `FAMILY_HEADROOM_OCM_MISSES` — oracle wins, history-fit does not. Carrier attribution.
- `HISTORY_INDUCED_SEARCH_PRIOR` — `FAMILY_PRIOR_ORDER` beats `RESET` **and**
  `LIBRARY_ONLY` **and** `FREE_FIT_ORDER` **and** `SHUFFLED_HISTORY`, on new externally
  verified targets, with a search-geometry receipt (rank of `m*` before discovery).
- `CANNOT_CHECK_<reason>` — distinct from PASS everywhere.

## Claim ceiling, registered before the run

A positive here is a statement about an ecology **we authored**. It is therefore
ceilinged at:

> history-induced search-prior transfer, on an authored ecology whose family structure
> is measured not to be surface-derivable.

It is explicitly **not** general developmental intelligence, and **not** fresh-world
replication: #323's success certificate remains unmet until an ecology someone else
authored shows the same effect. Cost accounting charges acquisition, retrieval,
matching, rejected candidates, verification and storage, per #323 HDI-14.

## Pre-registered ecology variants (written before any M2-P1 scored result was read)

`methods.solve` interleaves the guided and baseline streams — odd slots guided, even
slots baseline — so a guided arm pays a **2× toll on the baseline stream** and only
wins where the compositional shortcut exceeds that toll. This is a property of the
registered integration mode, not a tunable, and it has a predictable consequence:

> on targets whose canonical program is short, the baseline reaches the answer before
> the motif composition can pay for the interleave, so guided search is *expected* to
> lose there.

`validate_generator`'s no-slowdown rule requires `candidate.slots <= baseline.slots`
on **every** held-out task. A single short target can therefore veto admission of a
generator that is strongly beneficial on the rest of the ecology. That is the same
refusal that produced M1's `NO_NATIVE_EFFECT`, and it is correct behaviour by the
registered learner — it must not be relaxed (#323 §11).

Two ecologies are therefore registered up front:

| ecology | membership rule | purpose |
|---|---|---|
| `E1` | canonical program length ≥ 4 | as emitted, `M2P1_ECOLOGY_V1.json` |
| `E2` | canonical program length ≥ 6 | interleave-toll-aware variant |

`E2` is **not** a threshold tune of the learner, the admission gate, or any metric.
It is a statement about which ecology the compositional claim is made over, declared
before the outcome is known. If `E1` admits, `E2` is reported as a robustness replicate.
If `E1` refuses, the refusal is attributed to a single stage — the interleave toll on
short targets — and `E2` is the pre-registered revival, with the attribution evidenced
by the per-target `B_slots` of the vetoing tasks rather than asserted.

Both ecologies carry the same blocking gates (G1 parity, G2 disjointness, G3
decomposability, G4 surface-predictor null). Replication is run on **fresh worlds**
(different frozen seeds, therefore different hidden motif sets) and a **fresh host**
(LUNARC), per #323's certificate.
