# Warranted Lifecycle Learning: Strict Interface Hierarchy

**Candidate theorem package V1 — exact finite hierarchy proved; novelty unresolved**

Date: 2026-09-03  
Umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
P0 lane: ORION-V2 #221

## 1. Purpose

The programme needs a theorem that distinguishes which learning information is available, rather than claiming that recurrence or memory alone creates a new architecture.

Define four observation interfaces:

```text
I0 = endpoint input/output only
I1 = I0 + raw local execution trace
I2 = I1 + independently checked positive support witnesses
I3 = I2 + scope/epoch-bound closure information sufficient to decide that no unobserved support exists
```

The lifecycle target contains both held-out compositional behavior and post-revocation retain/retract decisions.

## 2. Fiber criterion

For an observation map `O: Omega -> observations` and lifecycle target `F: Omega -> {0,1}^k`, exact lifecycle identification from `O` is possible if and only if `F` is constant on every fiber `O^-1(o)`.

For zero-error partial output, a coordinate can be answered at observation `o` if and only if that coordinate of `F` is constant over the fiber. The maximum exact coverage is therefore the number of constant target coordinates; all others must be queried, represented by additional certified state, or reported as abstention.

This criterion is elementary but prevents false completion: current prediction correctness cannot manufacture missing lifecycle information.

## 3. Modular witness family

Let `theta in {0,1}^p` encode reusable procedural modules. Endpoint training reveals only a lower-rank composite observation. A raw trace reveals `theta`. For each module `i`:

- `k_i=1` means an independently checked backup support was observed;
- `u_i=1` means an additional valid backup exists but was not observed by the positive-only interface;
- actual post-revocation support is `z_i = k_i OR u_i`.

The lifecycle target is `F(theta,k,u)=(theta,z)`.

The interfaces are nested: I0 sees endpoint behavior; I1 also sees `theta`; I2 also sees `k`; I3 sees a closure-certified complete in-scope support state including `z`.

## 4. Strict hierarchy theorem

### Theorem WLL-8

On the registered modular family, the interfaces form a strict lifecycle identifiability hierarchy:

```text
I0 < I1 < I2 < I3.
```

Here `Ia < Ib` means `Ib` refines `Ia`, and there exists a pair of worlds that `Ia` cannot distinguish, that require different lifecycle responses, while `Ib` distinguishes them.

### Proof

1. **I0 < I1.** Choose two module vectors satisfying the same endpoint constraint but differing on a held-out primitive/composition query. Endpoint observations agree; raw local traces differ.
2. **I1 < I2.** Hold `theta` fixed. In one world an independently checked backup witness for a module is observed; in the other it is not. Raw traces agree. I2 can soundly answer RETAIN for the witnessed module after primary-support revocation.
3. **I2 < I3.** Hold `theta` and all observed positive witnesses fixed. Compare a world with no further support to one with an unobserved surviving support. I2 observations agree but correct actions are RETRACT and RETAIN respectively. A valid closure-certified record distinguishes them.
4. I3 contains every coordinate of the registered lifecycle target, so the target is constant on each I3 fiber.

Thus the hierarchy is strict.

## 5. General impossibility at the positive-only rung

No finite positive-only interface can be exact on an open-world support class that permits an unobserved surviving support. Consequently positive proof-carrying experience can strictly improve safe coverage; missing positive evidence is not a negative certificate; exact RETRACT requires closure, further search/query, a stronger proof system, or abstention.

## 6. Exact finite result

The checker uses three modules; endpoint constraint `theta_0 XOR theta_1=0`; three observed-positive and three unobserved-backup bits; 256 worlds; and six lifecycle target coordinates.

It verifies every interface fiber, exact/partial coverage, nested refinement and a strict witness for each adjacent pair. It also plants the false rule “missing positive support means no support” and exhibits two I2-indistinguishable worlds requiring opposite post-revocation actions.

The finite model gives:

- I0: at least five of six target coordinates may require abstention;
- I1: all three functional coordinates are answerable, but all three warrant coordinates may require abstention;
- I2: positive support witnesses add context-specific safe RETAIN answers, but worst-case open-world fibers still require three abstentions;
- I3: exact six-coordinate lifecycle response with zero abstention.

## 7. Why this is stronger than “traces help”

The hierarchy separates three different gains: raw traces expose procedural factorization and enable held-out reuse; positive certified support exposes some safe future retention; closure-certified warrant enables exact negative decisions.

Computational-trace learning owns the first gain. Proof-carrying execution owns local certificate checking. Provenance/TMS owns explicit dependency propagation. The proposed residual is the theorem-level joint learning contract and its acquisition/update frontier.

## 8. Strongest-parent kill test

This package is not novel unless full reconstruction fails to find the same object in the exact product of computational-trace/exact/query learning; privileged information and teaching dimension; proof-carrying code/certifying computation; TMS/ATMS, provenance, belief revision and self-adjusting computation; open-world reasoning and knowledge compilation; certified/modular/ticketed unlearning; and recurrent/looped Transformer implementation with identical interfaces.

A parent product may implement every rung. If so, the architecture claim dies, and the result can survive only as an interface theorem if its exact lifecycle hierarchy or frontier is itself new.

## 9. Next decisive theorem

Replace direct bits with a natural class of compositional programs and implicit support relations, then prove a tight frontier among certified acquisition, compiled warrant state, future queries, recourse, abstention and false/over-retraction risk. The lower bound must be computational/query/communication-theoretic; the upper bound must be an output-sensitive learner/repair algorithm. An equally provisioned recurrent Transformer receives the same interfaces.

## 10. Authority

Supported: the strict four-interface hierarchy on the stated family; the fiberwise exact-coverage criterion; positive certificates can improve local safe coverage without making the open-world problem exact; closure information is necessary for the top rung in the registered model.

Not supported: literature priority, a new architecture class, Transformer superiority, natural-language competence, lower total system cost, quantum advantage or publication readiness.
