# ORION-V2 feedback packet from the M12 lifetime (issue #14 §18)

One packet per unresolved failure family. Each names the observed OCM failure, the trace, the
strongest parent's behaviour, the suspected epistemic mechanism, the research question, and why
application-level engineering was insufficient. These are open items for the machine-epistemics
atlas, not claims.

## P1 — Carried-state lessons: revocation of one warrant does not remove a capability with another live warrant

* Observed: post-deployment `revoked_stops` 4/6 and `baseline_unknown` 4/6 in the lifetime (fresh arms: 6/6). A lesson word had acquired a live sense earlier in the lifetime; revoking the later lesson left the earlier warrant live.
* Trace: `M12_LIFETIME_EVAL_V2.json` phases.ocm.O1.A.post_deployment; ledger events for the two words.
* Parent: MatchedParent revokes by lesson name (6/6 revoked-stops) because it has no second warrant.
* Mechanism: ⊕ over warrants — a capability is LIVE while any warrant is LIVE; "revoke the lesson" is not "remove the capability".
* Question: what is the correct semantics of a *capability-level* revocation notice when the capability rests on several warrants — revoke all, revoke the named one and report the remainder, or ask? Which reading is licensed by the speaker's authority?
* Why engineering is insufficient: the choice is a policy over the warrant lattice with authority implications, not a code fix.

## P2 — Inference from one lifetime: the unit problem

* Observed: every non-language family is DESCRIPTIVE because one lifetime yields n ≤ 12 per family; pooling orderings was pseudo-replication (S32).
* Parent: same.
* Mechanism: the sample unit is the lifetime path; tasks inside one path are dependent through the shared state.
* Question: a valid inferential design for lifetime residuals — paired lifetimes with matched task streams, permutation over task order within a lifetime, or sequential analysis with pre-registered stopping — and its power at feasible n.
* Why engineering is insufficient: this is experimental design over dependent trials.

## P3 — Self-diagnosis without a counterfactual channel

* Observed: G works because the machine can run its registered alternatives in shadow; the historical replay (M11) can only audit governance.
* Parent: none.
* Mechanism: diagnosis as a distribution needs ablation evidence; without it every layer is UNKNOWN.
* Question: what can a self-model conclude from observational failure records alone (traces, warrants, resource state) — bounds on the diagnosis distribution, or a minimal set of cheap counterfactuals that identify the layer?
* Why engineering is insufficient: an identifiability question.

## P4 — False structural alarms from revoked dependencies

* Observed: a single revoked dependency makes every task fail (M11 S5; M12 F work step) and looks structural.
* Parent: n/a.
* Mechanism: reinstatement precedes escalation; the obstruction certificate's LIVE clause is the guard.
* Question: a lemma that any failure explained by a DEAD warrant on the path has minimum-sufficient layer ≤ D2, and its converse conditions.

## P5 — The identity of a persistent machine

* Observed: V1 split the runtime identity through a harness restart and nothing in the machine noticed (S31); the fix is a ledger-root invariant.
* Question: what is the epistemic identity of a machine — the ledger, the ledger plus the component fingerprints, or the lineage of adoptions — and what must a restart preserve for later commitments to be *the same machine's*?

## P6 — Frontier reference and human rating

* Observed: CANNOT_CHECK throughout the programme.
* Question (methodological): how to bind a foundation-model reference arm's information budget so that its result is a reference, not a mislabelled matched comparator.
