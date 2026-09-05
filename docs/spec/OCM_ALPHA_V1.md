# OCM_ALPHA_V1 — Conversational OCM Alpha (M6)

Status: engineering spec for `src/ocm/chat/`, `src/ocm/knowledge/`, `src/ocm/language/realize.py`,
`src/ocm/dialogue/planner.py`. Terminal `LANGUAGE_KSO_ALPHA` means a working bounded-world
conversational machine, not human-level language. No comparator, no novelty claim.

## 1. Entry point

`python -m ocm.chat [--state PATH] [--new-session] [--diagnostic] [--seed S] [--knowledge-manifest
PATH] [--resource-budget N] [--demo] [--script FILE]`. Normal mode prints replies only; diagnostic
mode prints, per turn, the trace assembled from the runtime's actual events: interpretation
candidates (constructions, digests, evidence), dialogue state, KSO objects (warrant ids), operators
(ledger event operators), checks (gate/feedback events), response plan, sentence plan
(register, contractions), resources (wall time, ledger events), committed response, ledger
sequence numbers. `--demo` runs the deterministic eleven-point demonstration (§15 of issue #8).
External IO is zero; the mechanism arm calls no external model.

## 2. The causal path

utterance → M3 interpretation → M4 workspace → knowledge world / cognition → `ResponsePlan.v1`
(act, goal, content items with layer + marker + evidence, rhetorical relation, marker requirement,
reference strategy, register, length target, clause obligations, open checks, feedback events) ↔
feedback (MISSING_REFERENT / MISSING_PREMISE / UNSUPPORTED_ASSERTION reopen the plan) → surface
(realisation is a reverse-checked codec; bounded-world answers use the fact glosses) → commitment
gate (six invariants) → committed machine turn with evidence → ledger persisted.

## 3. Bounded world with provenance (`knowledge/world.py`)

Four statements kept apart: source document exists (`SourceDocument`), source asserts P (IMPORTED
evidence, `source=1`), OCM parsed P (fact digest), P verified under declared authority (separate
PROOF evidence, `verified=1`). Fact warrant = ⊕ assertions ⊗ verification; repetition never raises
authority (`mutant_repetition_raises_authority`). `revoke_source` revokes that source's assertion
evidence and reports the facts that died (rumour:v1 → exactly `rum:paris:germany`). Manifest:
55 controlled facts, 13 families, 3 documents (curated, almanac = unverified source claims,
rumour = deliberately wrong). Custody: Simple Wikipedia articles with revision ids (source
assertion only; ingestion of their text is a follow-up).

## 4. Capabilities delivered (issue #8 §3)

factual answer (verified → "Yes." with evidence; unverified → "A source says so, but I have not
verified it"); explain (live facts about the topic + one hop; missing premise named); compare
(shared / differing relations, only live facts; no comparative minted); summarise the
conversation (speaker-attributed); clarification (M4 policy); ask for a demonstration when a word
or construction is unknown; acknowledge/correct (supersession); retract by revoking evidence;
calibrated markers (ASSERTED / REPORTED / UNCERTAIN / DENIED); explicit unknown; teach-back
(the lesson evidence is cited in the acknowledgement); style requests (brief / detailed /
formal / casual) without factual change.

## 5. Learning in chat and persistence

`teach: <word> = <concept>` (INSTRUCTION evidence → new sense), `teach: <utterance> => <agent>
<verb> <patient>` (DEMONSTRATION evidence → exact alignment, M5), `teach: construction …`
(version-space acquisition, M3/M5), `revoke <evidence>` / `reinstate <evidence>`. Learned senses
and constructions are saved keyed on their ledger evidence and restored on restart; the world
index is restored and checked against the ledger (missing evidence ⇒ CANNOT_CHECK).

## 6. Receipt (`research/ocm-m6/M6_ALPHA_SCENARIO_EVAL_V1.json`)

Nine frozen scenario families (everyday factual, explanation, ambiguity, correction, unknown,
teaching, topic switch + return over 12 turns, contradictory source/user, style shift): 42/42
expected replies; every scenario restart-consistent; hostiles (assertion→belief, revoked-still-
asserted, unknown-not-hallucinated) clean; incidents — answer laundering 0, revoked asserted
live 0, assertion became belief 0, restart lost state 0; latency mean 28 ms, max 77 ms per turn;
external IO 0.

## 7. Known limits (ledger S18–S19)

Question forms over the world are a small registered set (is X in Y / is X a Y / does X R Y / is X
the capital of Y / what is X / compare / summarize); pending clarification state is session-local
(the open ambiguity item is persisted, the numbered menu is not); realisation variants are limited
to active/passive/negation/question with contractions; human blinded evaluation is a frozen
protocol (report §4) not yet run; matched comparators belong to M7.
