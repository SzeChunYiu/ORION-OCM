# M12 — One persistent OCM across a frozen heterogeneous lifetime

Milestone issue: #14 (end of this roadmap version). Pre-registration: `research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V2.md`
(V1 is kept as the DEV_CALIBRATION freeze). Evidence: `research/ocm-m12/M12_LIFETIME_EVAL_V2.json` (PROTECTED),
`M12_LIFETIME_EVAL_V1.json` (DEV_CALIBRATION), `docs/provenance/M12_REPLICATION_RECEIPT_V1.json`, bound by
`docs/provenance/M12_RECEIPT_V1.json`. Obligations KS-T104…T109. Ledger rows S31–S33.

## 1. What was evaluated

One `PersistentOCM` (one ledger root shared by the M6 chat session, the M9 work skills, the M10
science ledger and the M11 self-model; never reset) against a `WholeSystemParent` (M7 matched
parent for language, M9 skill library for work, M10 parent procedures for science, parameter
search and retry for repair; identical manifest, lessons, demonstrations, plans and budgets) and
a template floor, across three orderings of phases A–G. The frontier reference arm, blinded human
rating and external benchmarks are CANNOT_CHECK in this environment and are recorded as such.

## 2. Principal ordering O1 (A→B→C→D→E→F→G), OCM vs parent

| Family | n | OCM | Parent | Paired terminal (δ = 0.05) |
|---|---|---|---|---|
| A conversations (M7 V2 protected) | 54 | 53 | 33 | OCM_RESIDUAL (RESIDUAL_A) |
| A factual in-scope | 30 | 30 | 27 | DESCRIPTIVE |
| A honest unknown | 20 | 20 | 17 | DESCRIPTIVE |
| A post-deployment lessons (6 × 7 steps) | 42 | 37 | 30 | INCONCLUSIVE |
| A negative transfer | 7 | 7 | 5 | DESCRIPTIVE |
| B enterprise (protected ids) | 10 | 10 | 10 | DESCRIPTIVE (equal) |
| C software (protected ids) | 10 | 10 | 10 | DESCRIPTIVE (equal) |
| D causal identification | 5 | 5 | 3 | DESCRIPTIVE |
| D experiment selection | 4 | 4 | 4 | DESCRIPTIVE (equal) |
| D pre-registered analysis | 12 | 12 | 12 | DESCRIPTIVE (equal) |
| D propositional kernel | 8 | 8 | 8 | DESCRIPTIVE (equal) |
| D communication gate | 4 | 4 | 2 | DESCRIPTIVE |
| E cross-domain transfer cells | 6 / 4 | 6 | 0 | DESCRIPTIVE |

Post-deployment steps in the lifetime (OCM): baseline-unknown 4/6, acquired 6/6, compositional
reuse 5/6, retained after restart 6/6, revoked-stops 4/6, unrelated intact 6/6, relearned 6/6.
The two baseline and two revoked-stops misses are carried-state effects of one instance: a lesson
word already had a live sense from an earlier conversation, so the utterance was interpretable
before the lesson and stayed interpretable after revoking only the later lesson. The fresh-arm
M7 numbers do not have this history; the lifetime numbers are the protected result.

Acquisition: OCM learned the first work domain for 12 and transferred to the second for 7 (role-typed
capsule + one withheld test) in every ordering; the parent learned each for 6 and paid 12 on the
later domain (a failed similarity transfer plus a new demonstration).

Revision (F): OCM stale behaviours 0, dependents reopened 3/3, unrelated intact 2/2 in every
ordering (rumour source revoked → "I used to have support for … but it was revoked"; retracted
observation kills exactly C0, C1; the revoked demonstration stops the skill). The parent keeps the
rumour fact live after the same notice (1 stale) — the declared mechanism difference.

Self-repair (G, fault undisclosed to the machine; one fault per ordering): operator fault → D2,
restore operator; learned-literal skill → D6, re-induce; environment drift → D2, upgrade policy
operator. Diagnosis, minimum class, assurance, external adoption, target 0/6 → 6/6, preservation
and exact rollback held in all three; parameter search and retry solved none.

Unknown/frontier: OCM "always attempts" 0 (A, D, unregistered domain); parent 3 (A) + 2 (D).

## 3. Robustness orderings O2, O3

Identical family vectors for phase A (A is always first), 10/10 on both work domains, the same
D/E/F outcomes, and G solved for the other two drawn faults. Reported descriptively only (S32).

## 4. Kill gates and integrity

All zero in V2: protected exposure, external IO, live-on-revoked after F, self-change touching a
protected target, missing phase outcomes, CANNOT_CHECK counted as pass, identity reset or split.
V1 (DEV_CALIBRATION) had an identity split caused by the harness restart (S31), which the new
gate now catches; V1's pooled statistics were pseudo-replication (S32); the V1 learning-policy
fault was plantable at the operator table (S33). None of the three was a mechanism change.

## 5. Claim tiers (pre-registered rules, V2)

| Tier | Holds | Basis |
|---|---|---|
| 0 operational | yes | all phases, all orderings, one ledger root, gates 0 |
| 1 capability | yes | every family with n ≥ 10 at ≥ 0.8 |
| 2 lifelong-learning | descriptive yes | later domain 7 < 12 in every ordering; lessons 37 ≥ 30; inferential INCONCLUSIVE at n = 42 |
| 3 transfer | descriptive yes | precision 1.0, harmful accepted 0 vs parent 2 per ordering |
| 4 epistemic integrity | descriptive yes | stale 0, reopened 3, intact 2; unknown 20 ≥ 17 (n = 20, DESCRIPTIVE) |
| 5 self-reorganisation | descriptive yes | 3/3 vs 0/3 |
| 6 broad | yes with one inferential family | A conversations RESIDUAL_A at n = 54 |

## 6. Exit gate

Before replication the code returns CANNOT_CHECK by rule (tier 6 needs a MATCH replication
receipt). The replication verdict and the final exit terminal are recorded in
`docs/provenance/M12_REPLICATION_RECEIPT_V1.json` and in the `exit_gate_final` field of the V2
receipt; see §7.

## 7. Replication and final terminal

Replication: the same frozen code and V2 pre-registration were run in a fresh `uv` Python 3.11
environment on a second host (billy-laptop; principal run on billy-old). The `deterministic`
blocks are byte-identical (receipt verdict MATCH, block SHA-256 `3671aecc8aaa5e69…`).
A same-host re-run on billy-old was also identical (determinism, not replication).

**Final terminal: `FULL_OCM_RESIDUAL_SUPPORTED`**, in scope: relative to the matched whole-system parent buildable in
this environment, with matched information, integrity gates at zero, resources reported, the
negative-transfer and revision stress inside the lifetime, and the independent replay above. One
family is inferential (A conversations, n = 54); every other residual is descriptive. Against a
frontier foundation-model whole-system parent (issue #14 §9) the claim is
CANNOT_CHECK_MATCHED_PARENT: no such parent can be built here. No consciousness, human-equivalence
or universal-intelligence claim is implied by any tier.

## 8. What this does and does not show

* It shows that one instance with explicit evidence identities can carry language, work, science,
  transfer, revision and governed self-repair through a lifetime without reset, and that on this
  bounded ecology the declared mechanism difference produces the residuals listed, with exactly one
  inferential family (conversations, n = 54).
* It does not show a residual over a frontier foundation-model agent (CANNOT_CHECK), human
  usefulness (CANNOT_CHECK), or any inferential residual on work, science, transfer or
  self-repair (n < 40 by design of one lifetime).
* PARENT_SUFFICIENT holds descriptively on B, C, D-selection, D-analysis and D-proof: the parent
  matches OCM wherever the task needs no revision, identification, role typing or repair.

## 9. Revival backlog

Longer lifetimes (n ≥ 40 per work/science family from one instance), a second language suite so
that A is not identical across orderings, a stronger repair parent (learned failure classifier over
traces) with the same candidate channel, a foundation-model reference arm when one is available,
and blinded human rating of the A conversations.
