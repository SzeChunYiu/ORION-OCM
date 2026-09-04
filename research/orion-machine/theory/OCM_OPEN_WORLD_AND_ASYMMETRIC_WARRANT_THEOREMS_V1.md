# Open-World and Asymmetric Warrant Theorems

**WLL theorem tranche V1 — mathematical proofs plus finite semantic checker**

Date: 2026-09-03  
Umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
P0 lane: ORION-V2 #221

## Status

```text
OPEN-WORLD POSITIVE-WITNESS IMPOSSIBILITY = PROVED
GENERAL RETAIN = NP-COMPLETE
GENERAL RETRACT = coNP-COMPLETE
CHEAP SYMMETRIC NONINTERACTIVE CERTIFICATES = BLOCKED UNLESS NP=coNP
EXPLICIT CLOSED-WORLD SUPPORT PROTOCOL = CONSTRUCTIVE CALIBRATION
NOVELTY / PRIORITY = OPEN
```

These results sharpen Warranted Lifecycle Learning (WLL). A machine cannot treat “I have seen some valid support” as equivalent to “I know the complete support state,” and positive and negative warrant decisions have different complexity in unrestricted implicit support systems.

## 1. Support model

A learned skill has a support relation `V(I,w)`, where `I` contains the skill, currently valid evidence, scope, authority, policy and verifier epoch, while `w` is a candidate derivation/support witness. Assume `V` is decidable in polynomial time.

```text
RETAIN(I)  iff  exists w: V(I,w)=1
RETRACT(I) iff  no w: V(I,w)=1.
```

Abstention is a distinct third action and is never silently counted as RETRACT.

## 2. Open-world positive-witness impossibility

A positive-witness-only learner observes a finite set `P` of valid supports but receives no certificate that `P` is complete.

### Theorem WLL-5

Suppose a revocation set `R` intersects every support in `P`, and the open-world support universe admits an unobserved support `T` disjoint from `R`. No learner using only observation `P` can always choose RETAIN or RETRACT while satisfying both:

1. soundness: never retain when no valid support survives;
2. retention completeness: never retract when a valid support survives.

### Proof

Construct two worlds consistent with the same observation:

```text
W0 = P
W1 = P union {T}.
```

In `W0`, every support is hit by `R`, so RETRACT is required. In `W1`, `T` survives, so RETAIN is required. The learner receives identical observations and must return the same action in both worlds; either action violates one requirement.

For randomized learners under the uniform distribution over the two worlds, every no-abstention strategy has error at least `1/2`. A zero-error learner must obtain a completeness/closure certificate, make a future support-discovery query or abstain.

A valid positive proof establishes existence. It does not establish that all alternatives have been enumerated. This is a formal reason to preserve `CANNOT_CHECK` in open-world warrant states.

## 3. Retain/retract complexity asymmetry

### Theorem WLL-6

For polynomial-time support verifiers, general RETAIN is NP-complete and general RETRACT is coNP-complete.

### Proof

RETAIN is in NP because `w` is a polynomially checkable witness. It is NP-hard by reduction from SAT: let `I` encode a CNF formula `phi`, let `w` be an assignment, and define `V(I,w)=1` exactly when `w` satisfies `phi`. RETAIN holds exactly when `phi` is satisfiable. RETRACT is the complement, hence coNP-complete.

### Corollary WLL-6A — no universal cheap symmetric certificate system

Suppose both RETAIN and RETRACT admitted polynomial-size noninteractive certificates checked by a deterministic polynomial-time verifier for every instance. Then RETRACT would be in NP, so coNP is contained in NP and `NP=coNP`.

Therefore, unless `NP=coNP`, a fully general proof-carrying lifecycle machine cannot promise short ordinary certificates for both survival and absence of survival. It must restrict the support language, compile support into a larger tractable representation, use a stronger interactive/probabilistic proof system with explicit resources, perform expensive revalidation/search, or abstain.

The statement does not rule out short certificates on structured practical instances.

## 4. Explicit closed-world protocol

Let a scope/version-bound manifest enumerate a complete finite support family `S=(S_1,...,S_m)`. After revocation `R`:

- RETAIN has a short witness: an index `j` with `S_j` disjoint from `R`;
- RETRACT can be verified by scanning the complete manifest, or by a hitting certificate naming one revoked atom in each `S_j`, together with the manifest's completeness/authority certificate.

### Theorem WLL-7

With an explicit complete support family and inverted atom-to-support index, monotone revocations can be maintained with:

- storage `O(sum_j |S_j| + m)`;
- update work `O(sum_{e in Delta R} deg(e))`;
- `O(1)` live-skill query after maintaining each support's unrevoked count and the number of surviving supports.

This is a constructive calibration closely related to truth-maintenance, provenance and self-adjusting computation; it is not claimed as a new algorithm.

## 5. Why this matters to learning

Ordinary prediction learning asks which function is correct now. WLL asks for a learned object whose behavior remains defensible over future update sequences. WLL-5 and WLL-6 imply:

1. unlimited current input-output data may reveal nothing about undiscovered alternative support;
2. a positive proof-carrying trace can certify RETAIN but cannot, by itself, certify exhaustive absence;
3. learning only behavior can leave future lifecycle decisions information-theoretically unidentified;
4. learning arbitrary compact implicit support can leave future retraction computationally hard;
5. a WLL system should learn or compile a tractable, scope-bound warrant representation and retain an honest abstention route.

This creates a concrete OCM research target: **warrant compilation is a learned resource, not free metadata**.

## 6. Potentially novel residual

The individual ingredients collide with SAT/UNSAT, open-world reasoning, machine unlearning, provenance, truth maintenance, knowledge compilation and proof systems. The candidate contribution is a joint learning theorem:

> Learn a reusable procedural factorization and a scope-bound support representation from local certified experience, such that held-out compositions work and future evidence/authority changes admit output-sensitive, warrant-correct repair. Characterize the optimal trade-off among acquisition, compiled warrant size, revalidation, recourse, abstention, false retention and useful retention.

A novelty claim requires a natural target class and a strict lower/upper frontier not already inherited from exact learning, knowledge compilation, provenance, unlearning or dynamic algorithms.

## 7. Finite semantic validation

The companion checker validates satisfiable implicit support with a positive assignment witness; unsatisfiable support with no witness; an exact open-world ambiguous pair with opposite correct actions; rejection of a negative-warrant certificate without a completeness manifest; acceptance of explicit positive and negative certificates with correct assumptions; exhaustive support-family/revocation cases over four evidence atoms; and both RETAIN and RETRACT no-alarm coverage.

Finite enumeration does not prove NP/coNP hardness; the reductions above do.

## 8. Authority and non-consequences

Supported: positive-only open-world support cannot guarantee exact sound and retention-complete updates; general implicit RETAIN/RETRACT decisions have NP/coNP asymmetry; a universal cheap symmetric noninteractive certificate system would imply `NP=coNP`; explicit complete support manifests yield a tractable parent-owned calibration.

Not supported: literature priority or novelty; practical intractability for every real system; post-Transformer architecture separation; privacy-preserving machine unlearning; natural-language competence; quantum advantage; publication readiness.
