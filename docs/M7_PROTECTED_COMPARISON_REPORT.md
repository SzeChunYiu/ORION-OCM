# M7 — protected comparison report (claim by claim)

Date 2026-09-05. Study identity = sha256 of `research/ocm-m7/M7_PREREGISTRATION_V1.md` (bound by
`docs/provenance/M7_RECEIPT_V1.json`). Terminal for the milestone: **MIXED**, claim by claim, as the
pre-registration permits. Nothing here is a superiority claim about the architecture; the strongest
faithful matched parent was built in this repository from known components with identical
knowledge, lessons, corrections and budget.

## 1. What was run

* **V1 (DEV_CALIBRATION).** The first run exposed three OCM defects (ledger S22 pending-clarification
  trap, S23 contradiction-by-object-difference heuristic, S24 lesson-bytes deduplication) that were
  fixed after outcome access. V1 carries no claim.
* **V2 (PROTECTED).** New hand-authored conversations (12, 54 paired turns), six new lessons, seven
  new negative-transfer items, the generated factual suite (30 in-scope + 20 out-of-scope), the
  laundering audit; frozen in the pre-registration addendum before any V2 outcome access; no system
  change afterwards.

Arms: OCM Alpha; OCM −revocation; OCM −workspace (last-turn memory); OCM −active clarification;
MatchedParent.v1; template baseline.

## 2. Terminal table (V2; δ = 0.05, TOST at α = 0.05, minimum n = 40)

| claim | OCM | matched parent | n | test | terminal |
|---|---|---|---|---|---|
| RQ1 conversations | 53/54 | 33/54 | 54 | RESIDUAL_A (difference +0.37) | **OCM_LANGUAGE_RESIDUAL_SUPPORTED** |
| RQ1 conversations vs template | 53/54 | 10/54 | 54 | RESIDUAL_A | OCM_LANGUAGE_RESIDUAL_SUPPORTED |
| RQ1 factual | 30/30 | 27/30 | 30 | INCONCLUSIVE | CANNOT_CHECK (n < 40) |
| RQ2 laundering audit | 0 incidents / 3 probes | — | 3 | — | reported (incidents 0; n < 40) |
| RQ3 acquired / reuse / retained / revoked / relearned | 6/6, 5/6, 6/6, 6/6, 6/6 | 3/6, 3/6, 3/6, 6/6, 3/6 | 6 | INCONCLUSIVE | CANNOT_CHECK (n < 40) |
| RQ5 honest unknown | 20/20 | 17/20 | 20 | INCONCLUSIVE | CANNOT_CHECK (n < 40) |
| RQ6 negative transfer | 7/7 | 5/7 | 7 | INCONCLUSIVE | CANNOT_CHECK (n < 40) |

Mechanism attribution for the RQ1 residual (ablations, n = 54): −clarification 52/54 and
−revocation 52/54 are EQUIVALENT to full OCM on this suite (those mechanisms are exercised by RQ3/RQ5,
where n is below the minimum); −workspace 49/54 is INCONCLUSIVE. The residual over the parent is
therefore supported as a *system* claim; which mechanism carries it is CANNOT_CHECK at this n.
Where OCM −revocation loses revoked_stops 0/6 vs 6/6, the direction is as designed but n < 40.

## 3. External families (frozen protocols)

| family | result | terminal |
|---|---|---|
| BLiMP (6 phenomena, 6 000 pairs) | covered 0 / 6 000 under the admissibility protocol | CANNOT_CHECK (coverage 0) |
| UD EWT dev (800 sentences, 3 genres) | interpreted 0 / 800 | CANNOT_CHECK (coverage 0) |
| BabyLM 10M / 100M | data/terms not pinned | CANNOT_CHECK_BABYLM_DATA |
| CHILDES | no registration | CANNOT_CHECK_CHILDES_DATA |
| blinded human rating | protocol frozen (M6 report §4), not run | CANNOT_CHECK |
| frontier reference | external IO disabled | CANNOT_CHECK (non-matched by design) |

Coverage 0 is the honest statement of the Alpha inventory's size (≈ 60 lexemes, 7 constructions):
it is the lead for the revival backlog, not a hidden number.

## 4. Information and resource accounting (V2)

Per arm the receipt records knowledge facts (55 for every arm), lessons, statements, interaction
turns, protected exposure (0 for every arm), persistent bytes, ledger events, wall time and peak
RSS; external IO = 0 for every arm. The matched parent received identical lessons and corrections.

## 5. Hostile mutations (automated checks)

Contamination: protected utterances are absent from every lesson set (string check in the
harness). Split after tuning: V2 hash bound before outcome access. Comparator denied annotations:
information receipts show identical lesson counts. Meter excludes storage: persistent bytes are
nonzero for OCM and parent. Revoked construction in cache: the revocation probe is a family. Hidden
gold: the laundering audit injects a gold field into a forbidden channel (not surfaced). Hard-coded
uncertainty: the gate refuses a marker that does not follow state (M6 tests). Post-hoc removal:
item counts are fixed in the suite files. Under-tuned parent: identical lessons. Stopping when OCM
leads: fixed n.

## 6. Decision and what it means

`OCM_LANGUAGE_RESIDUAL_SUPPORTED` for one claim (RQ1 conversations, n = 54) against a matched
parent built here; `CANNOT_CHECK` for the remaining claims because the protected suites are below
the pre-registered minimum size, and for every external family by coverage or data terms;
`PARENT_SUFFICIENT` where ablations showed the mechanism was not needed on this suite. The
language programme's scientific gate closes with this mixed table; it does not close with a win.

## 7. Revival backlog (negatives are leads)

1. Coverage: a structural-alignment learner over UD EWT gold `nsubj`/`obj` (an E1-like channel,
   counted as annotation information) to grow the lexicon and constructions before re-running BLiMP
   and UD under the same frozen protocols.
2. Suite size: extend the protected conversation suite and the post-deployment lessons to n ≥ 40
   per family (new hand-authored content, frozen before access) so RQ3/RQ5/RQ6 become decidable.
3. Parent strength: add a fine-tuning/adapter comparator when a matched neural learner becomes
   feasible off-Mac (billy-old CPU) — reported as CANNOT_CHECK here.
4. Human rating: run the frozen blinded protocol with ≥ 3 raters.

## 8. Addendum after theory batch 4 (D1 / MEG-32)

The equivalence scale is the **paired rate difference** d = (a_only − b_only)/n with margin δ = 0.05,
tested through the exact Clopper–Pearson interval of the discordant proportion; at n = 54 a single
discordant pair bounds |d| ≤ 1/54 < δ, so the EQUIVALENT verdicts for the ablations are exact on
that scale. On the discordant-proportion scale p_d at δ = 1/10 (D1's scale) equivalence needs
n_d ≥ 76 discordant pairs and is therefore CANNOT_CHECK here — both scales are now named. The M2.1
revival terminal (0/540 discordant) is a θ-scale equivalence at δ_u ≥ 7/1000 and is relabelled as
such in the ledger (S28).
