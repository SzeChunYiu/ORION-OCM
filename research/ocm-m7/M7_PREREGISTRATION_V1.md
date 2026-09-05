# M7 pre-registration — protected language stress test and matched-parent comparison

Frozen before any protected outcome access. Hash recorded in `M7_PREREGISTRATION_HASH_V1.json`
by `tools/m7_receipt.py` at freeze; any change opens a new versioned study.

## 1. Research questions and hypotheses

RQ1 conversational competence within the declared scope; RQ2 cognitive grounding (responses derive
from KSO/dialogue state, not from a component that can reconstruct answers); RQ3 continual
acquisition locality/sample-efficiency vs matched parents; RQ4 correction/revocation without
global retraining or unrelated regression; RQ5 ambiguity/unknown calibration; RQ6 negative
transfer refusal; RQ7 whole-system resources.

H-null for every RQ: the strongest faithful matched parent (§4) matches OCM on the primary metric
within the equivalence margin. Residual claims are per-RQ; a residual is claimed only where the
pre-registered test rejects equivalence in OCM's favour with the effect-size requirement met.

## 2. Primary metrics (denominators fixed; no aggregate)

| RQ | primary metric | denominator | test |
|---|---|---|---|
| RQ1 | expected-reply rate on the protected conversation suite | items | exact McNemar on discordant pairs |
| RQ2 | laundering audit incidents (must be 0) and meaning-following rate under random-meaning injection | probes | exact binomial vs 0 |
| RQ3 | post-deployment challenge: immediate acquisition, unseen compositional reuse, retention, restart, revocation, relearn — each pass/fail per lesson | lessons | exact McNemar |
| RQ4 | correction locality = affected corrected / unrelated changed (both counts) | probes | exact binomial per count |
| RQ5 | clarification precision/recall, honest-unknown accuracy, calibration (marker matches state) | items | exact McNemar |
| RQ6 | transfer precision and harmful-transfer rate on the negative-transfer suite | pairs | exact binomial |
| RQ7 | resource vector (wall, memory, persistent storage, KSO objects, update cost, external IO) | runs | reported, not tested |
| BLiMP | admissibility accuracy per phenomenon + coverage (frozen protocol §3.1) | pairs | per-phenomenon binomial CI |
| UD EWT | interpretability coverage and role-edge agreement per genre (frozen protocol §3.3) | sentences | CI |

Equivalence margin δ = 0.05 (absolute rate) with TOST at α = 0.05; residual requires the
one-sided exact test p < 0.05 AND difference ≥ δ. Minimum n per paired family: 40 items.

## 3. Datasets, versions, splits (custody manifests bound by the receipt)

Bounded world `KNOWLEDGE_MANIFEST_V1.json` (55 facts); M3 microworld protected split; M4 dialogue
microworld protected split; protected conversation suite `M7_PROTECTED_CONVERSATIONS_V1.json`
(human-authored, 12 conversations, not template-generated); bounded-knowledge factual suite
generated from the manifest + 20 out-of-scope questions; BLiMP six frozen phenomena (custody
manifest, `master`); UD EWT r2.14 dev/test (custody manifest); BabyLM: `CANNOT_CHECK_BABYLM_DATA`
unless the release/terms are pinned before protected access; CHILDES: `CANNOT_CHECK_CHILDES_DATA`
(no registration completed). Protected-test exposure of every arm = 0 (no tuning after freeze).

### 3.1 BLiMP admissibility protocol (frozen; OCM exposes no likelihoods)

A minimal pair is scored correct iff the acceptable sentence is INTERPRETED by the frozen inventory
and the unacceptable one is not; a pair where neither is INTERPRETED is *uncovered* and reported in
coverage, never as correct or incorrect. Accuracy is reported over covered pairs with the coverage
fraction beside it. No retrofitting of a favourable metric.

### 3.3 UD EWT protocol (frozen)

Per genre: interpretability coverage (fraction of sentences INTERPRETED under the frozen
inventory), and for covered sentences the agreement of ROLE:agent / ROLE:patient heads with UD
`nsubj` / `obj` lemmas. Reported as coverage + agreement, never collapsed.

## 4. Comparators

* **Strongest faithful matched parent** `MatchedParent.v1` (`src/ocm/comparators/matched_parent.py`):
  retrieval memory over the same 55 facts (triple lookup), dialogue-state memory (statement list
  with string-level supersession/retraction), in-context lesson memory (word table), template
  renderer, same interaction budget. It receives the same lessons, demonstrations, corrections and
  knowledge; it has no warrant intervals, no reopening cone, no version space, no gate.
* **Template baseline**: fact glosses only, no dialogue state.
* **External frontier reference**: `CANNOT_CHECK` in this study (external IO is disabled by the
  mechanism contract; would be non-matched in any case).
* **OCM ablations** (§6): −warrant/revocation, −workspace (last-turn memory), −construction
  abstraction (flat patterns, no NP recursion), −active clarification (first candidate), −gate.

## 5. Information and resource accounting

Per arm: training words, gold annotations, meaning graphs, lessons, dictionary entries, teacher
feedback, interaction turns, grounded observations, knowledge facts, retrieval documents,
protected exposure = 0 → `INFORMATION_BUDGET_RECEIPT` per run. Resources: wall per turn, peak
memory (RSS), persistent storage bytes, KSO objects, update cost (ledger events), external IO.

## 6. Ablations and hostile mutations

Ablations as in §4. Hostile mutations (each detectable by an automated check in the receipt):
contamination (protected utterances in any training/lesson set), split chosen after tuning
(hash compare), comparator denied annotations OCM receives (information receipt equality), meter
excludes storage (storage bytes must be nonzero), revoked construction in a cache (revocation
probe), hidden gold in preprocessing (laundering audit), hard-coded uncertainty wording (marker
must follow state under a random-state swap), rater sees identity (protocol), post-hoc removal
(item counts fixed), under-tuned parent (parent gets identical lessons), stopping when OCM leads
(fixed n).

## 7. Stopping rule and terminals

Fixed item counts (no sequential stopping). Terminals per claim: `OCM_LANGUAGE_RESIDUAL_SUPPORTED`
(pre-registered test rejects equivalence in OCM's favour and survives the relevant ablation),
`PARENT_SUFFICIENT` (equivalence not rejected, or parent matches), `CANNOT_CHECK` (data/tooling/
protocol failure). Mixed outcomes are expected and reported claim by claim.

## 8. Addendum (frozen 2026-09-05, before any V2 outcome access)

The V1 run exposed three system defects (ledger S22 clarification trap, S23 contradiction heuristic,
S24 lesson-bytes deduplication) which were fixed after V1 outcome access. V1 is therefore recorded as
`DEV_CALIBRATION` and carries no claim. The protected study is suite **V2**: new hand-authored
conversations `M7_PROTECTED_CONVERSATIONS_V2.json` (12, different content), six new lessons for the
post-deployment challenge, seven new negative-transfer items, the same generated factual suite (its
items were not changed; the S23 fix is a general planner rule). No system change is permitted after
V2 outcome access; the V2 receipt binds this file's hash.
