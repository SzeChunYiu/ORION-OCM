# M9 — method/operator space and real-work transfer: study report

Date 2026-09-05. Terminal: **CANNOT_CHECK for `M9_METHOD_TRANSFER_SUPPORTED` at this n** (the
descriptive signature is present; the paired families are far below the pre-registered minimum
of 40 and the environments are OCM-authored, so no SUPPORTED claim is made); external agent
benchmarks are `CANNOT_CHECK` by tooling. No novelty claim.

## 1. Objects delivered (issue #11 §1–§4, §11–§14)

`TaskContract.v1` (initial observable state, goal, allowed/forbidden actions, hidden checker-only
state, budgets, authority, side-effect policy, rollback); generic `Operator` (preconditions,
backend, expected effects, checker, cost, warrant, authority, scope, known failures, lineage,
registered *role*); `Skill` = ordered roles + bindings + adapter; `SkillCapsule.v1` = invariant
skeleton + per-domain bindings + adapters (a missing binding is `ADAPTER_REQUIRED`); `TransferMap.v1`
with Λ(transported) = Λ(source) ⊗ Λ(correspondence), `REFUSE_TRANSFER` when a target operator's
registered role differs from the source role (superficial similarity), `ADAPTER_REQUIRED` for a
missing binding; induction (memoised / skeleton / subtrace) accepted only by a withheld
intervention test; routers (name similarity / typed / OCM: domain, liveness, allowed, role
agreement, recorded failures); diagnosis layers; drift revision with lineage and ⊗ evidence.

## 2. Environments (self-contained, exact oracle state, versioned)

Enterprise support (gather facts → classify urgency → check policy → smallest authorised action →
verify → document; `refund_all` is the superficially similar broad action; `delete_account` is
unauthorised), software operations (collect logs → localise → runbook → minimal repair → verify →
incident note; `rewrite_all` regresses; `force_push` unauthorised), data-analysis preflight
(inspect → check assumptions → select method → execute → verify → report; `plain_mean` ignores
the assumption check; `drop_rows` unauthorised). Version 2 of each changes the policy / runbook /
method table so a stale binding fails the hidden checker.

## 3. Lifetime study (V2, protected; V1 was DEV_CALIBRATION — ledger S27)

Three orderings (A→B→C, C→A→B, B→C→A), six tasks per domain, one demonstration per new domain,
every arm validates on one withheld task before use.

| arm | success | later-domain acquisition cost (mean) | later route | unauthorised attempts |
|---|---|---|---|---|
| OCM (capsule + transfer map + router) | 54/54 | 7 | TRANSFER | 0 |
| OCM −router | 54/54 | 7 | TRANSFER | 0 |
| OCM −transfer | 54/54 | 12 | LEARN_NEW | 0 |
| fresh start (matched validation) | 54/54 | 12 | LEARN_NEW | 0 |
| trajectory memory (replay) | 54/54 | 12 | LEARN_NEW (replay never fits) | 0 |
| skill library (name-similarity transfer) | 54/54 | 12 | LEARN_NEW (similarity transfer fails the withheld run) | 0 |
| fresh start, unvalidated — *not matched* | 54/54 | 6 | LEARN_NEW | 0 |

Cost unit = operator applications observed/run to acquire competence in a domain (demonstration
= 6, withheld validation run = 6, correspondence evidence = 1). Transfer precision 6/6 (every
attempted transfer was beneficial); harmful transfers 0; false refusals 0. Success is not
discriminating on these environments (every correct skeleton solves them); the signature is in
the acquisition cost: prior structure lowers later cost from 12 to 7 for OCM, and the parents that
carry only traces or names cannot reuse it. Paired success claims: EQUIVALENT at n = 9 →
`CANNOT_CHECK` under the pre-registered minimum n.

## 4. Transfer matrix (OCM enterprise skill after the A→B→C lifetime): 14/14 as expected

T0 identical new instance TRANSFER · T1 new parameters TRANSFER · T2 subprocedure TRANSFER ·
T3 composition TRANSFER · T4 new vocabulary/domain TRANSFER · T5 partial → ADAPTER_REQUIRED ·
T6 representation correspondence TRANSFER · T7 superficial similarity → REFUSE_TRANSFER ·
T8 outside authority → REFUSE_TRANSFER · T9 source revoked → REFUSE_TRANSFER · T10 environment
drift → REFINE_REQUIRED (diagnosed OPERATOR_WRONG under the old version label) · T11 conflicting
lessons → LEARN_NEW (revised skill with lineage) · T12 router with a wrong candidate → picks the
right skill · T13 short-horizon help, final harm → REFUSE_TRANSFER.

## 5. Hostiles (planted, detected)

Similarity transfer keeping the source warrant (`mutant_similarity_transfer`); try-every-skill
routing (`mutant_try_every_skill`); broad-action trace accepted without the withheld test; destroy
operators in every domain refused by the contract; unvalidated comparator labelled not matched.

## 6. CANNOT_CHECK

WorkArena++, CRMArena-Pro, TUA-Bench, SWE-bench Verified, TheAgentCompany: no network, no
container runtime, no LLM agent in the mechanism arm; frontier-agent comparators likewise.
Credit assignment under real tool failures, learned latent operators, fine-tuned agents: not built.

## 7. Backlog

Larger protected task families (n ≥ 40 per cell) on the OCM-authored environments; a
subtrace/overlap-aware induction study against program-induction parents; real sandboxed
benchmarks when a container runtime is available off-Mac; the diagnosis hostile (router swap with
fixed skill) as an automated matrix cell; theory batch 4 D2 (per-channel bounds) for the
acquisition-cost accounting.
