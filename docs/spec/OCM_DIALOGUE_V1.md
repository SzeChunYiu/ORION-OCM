# OCM_DIALOGUE_V1 — persistent dialogue cognition (M4)

Status: engineering spec for `src/ocm/dialogue/`; theory in ORION-V2 batch 2 (B1 discourse-state
warrant, B5 supersession) and batch 3 (C1 clarification value, C2 commitment gate, C7 contradiction
policy). Obligations: `docs/theorems/OCM_DIALOGUE_OBLIGATION_REGISTRY_V1.json`. No novelty claim.

## 1. The loop (M4 target loop, implemented in `session.DialogueRuntime.hear`)

utterance → M3 `interpret` (candidate meanings with ⊗ warrants) → workspace update (turn log,
entities, commitments) → cognition (answer from the three layers; reference; clarification value)
↔ language planning (`gate.ResponsePlan`) → `gate.commit_gate` (six invariants) → external
commitment (machine turn recorded with its evidence) → new dialogue evidence (OBSERVATION /
INTERACTION / DEMONSTRATION records in the runtime ledger).

## 2. Three epistemic layers (`workspace.py`)

| layer | object | authority | how it changes |
|---|---|---|---|
| utterance content | `Turn` (immutable log) | — | append only |
| speaker commitment | `Commitment` ← OBSERVATION evidence, `speaker=1`, conversation scope | `Authority.of(speaker=1)` | ACTIVE → SUPERSEDED (correction) / RETRACTED (revocation); never edited |
| machine warrant | runtime liveness of cited evidence; `machine_commitments` only via `propose_promote` | meet(speaker record, bridge) — never `world_truth` from speech alone | admit under a LIVE bridge; revocation of the bridge kills the promotion |

Ten speakers asserting p leave the machine layer empty (receipt: leakage 0/51).

## 3. Reference (`reference.py`)

RESOLVED / AMBIGUOUS / NEEDS_CLARIFICATION / UNKNOWN_REFERENT from constraints (pronoun features,
description, head noun, alias, ordinal); recency orders an ambiguity set only. Hostiles:
`mutant_nearest_noun`, `mutant_most_recent_turn_only`. Entities are introduced from interpreted
meanings; nothing is clipped (reference after a ≥ 12-turn gap: 5/5).

## 4. Clarification (`clarify.py`; C1 / MEG-33)

value(question) = E[# query cells determined after the answer] − cost − repeat penalty; ask iff
max value > 0. Irrelevant ambiguity ⇒ no question; consequential ⇒ ask; a question pinning every
candidate beats one isolating a single candidate; repeats are penalised. The answer is INTERACTION
evidence; the ambiguity set is never collapsed by score. Hostiles: `mutant_always_ask`,
`mutant_never_ask`.

## 5. Correction, supersession, retraction (`workspace.commit(supersedes=…)`, `retract`)

Correction supersedes the speaker's latest active commitment on the *same canonical proposition*
(either polarity; ledger S15): new OBSERVATION evidence with `supersedes=old`, old evidence
revoked (KS-T22 reopening of exactly the dependents), both records linked, history intact.
Retraction revokes without a successor. Hostiles: `mutant_correction_overwrites_history`; the
"stale cached answer" hostile is excluded by construction (answers are recomputed from live
commitments).

## 6. Commitment gate and feedback (`gate.py`; C2 / MEG-25, M4 §7–§8)

G1 surface meaning digest = plan digest; G2 asserted propositions LIVE (or REPORTED when they rest
on speaker commitments); G3 epistemic marker = state's required marker; G4 referents resolved;
G5 no protected content id; G6 renderer holds no store handle. Refusals are structured
`FeedbackEvent`s naming the stage to reopen (reference / solve / warrant / nogoods / learn /
clarify / render). Hostiles: `mutant_renderer_injects_fact`, `mutant_drop_uncertainty`.

## 7. Dialogue acts (`gate.Act`)

ASSERT, ANSWER, ASK, CLARIFY, ACKNOWLEDGE, CORRECT, RETRACT, REQUEST, CONFIRM, REPORT_UNKNOWN,
REPORT_UNCERTAIN — every machine turn carries one and passes the gate.

## 8. Persistence

Workspace state is written atomically next to the runtime ledger after every mutation and
reloaded on `DialogueRuntime.resume`; a workspace referencing evidence absent from the ledger is
CANNOT_CHECK. The receipt restarts 18 of 49 protected dialogues midway with no behavioural change.

## 9. Evaluation (`research/ocm-m4/M4_DIALOGUE_EVAL_V1.json`)

Frozen dialogue microworld, eight families, protected split by content hash. Metrics with
denominators: expected act and committed 251/251; entity introduction 11/11; ambiguous-pronoun
candidate recall 4/4; unique pronoun resolved 7/7; reference after gap ≥ 12 turns 5/5;
supersession recorded 9/9; dependent answer reopened 9/9; unrelated answer intact 20/20;
clarification needed 4 / asked 4 / unnecessary 0; assertion→belief leakage 0/51; answers citing
evidence 11/11; contradiction reported with both 7/7; wall per turn grows from 2 ms (2 turns) to
6 ms (14 turns). Authority: synthetic; no real-conversation result, no comparator. MultiWOZ 2.4
custody script provided for the comparator lane (no result claimed).

## 10. Known limits

Reference covers pronouns, descriptions, aliases, ordinals; discourse deixis ("that idea") and
omitted arguments are not implemented. Topic tracking is a focus stack without semantic retrieval
cost accounting beyond wall time. Production (M6) is not attempted: surfaces are canned strings
whose meaning graphs are supplied by the plan. Real protected human conversations are not yet
collected.
