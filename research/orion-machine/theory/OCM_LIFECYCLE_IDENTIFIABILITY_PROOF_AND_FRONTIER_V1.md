# Lifecycle Identifiability for Proof-Carrying Experience

**Theorem candidate V1 — exact finite calibration completed; novelty not established**

Date: 2026-09-03  
Scientific umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Focused hardening lane: ORION-V2 #221

## Disposition

```text
GENERAL INFORMATION FRONTIER = PROVED
EXACT MODULAR-REVOCATION INSTANCE = FINITELY VERIFIED
ONE-WITNESS RETENTION IMPOSSIBILITY = PROVED
COMPUTATIONAL SEPARATION = OPEN
PRIORITY / NOVELTY = OPEN
POST-TRANSFORMER ARCHITECTURE RESIDUAL = NOT EARNED
```

The result below is deliberately narrower than “OCM is novel.” It formalizes a lifecycle obligation: a learner must both use learned modules on unseen compositions and later preserve only the modules that remain justified when evidence, scope, policy, or verifier identity changes.

## 1. General lifecycle response-profile bound

Let `Omega_T` be the latent worlds consistent with a fixed ordinary training history `T`. Let

```text
F: Omega_T -> {0,1}^k
```

map each world to all future decisions that the system is required to answer. These may include held-out compositional outputs and post-revocation retain/retract decisions. Write `M = |F(Omega_T)|`.

During acquisition, the learner receives at most `C` bits of certified information and stores a persistent state of at most `B` bits. Later it may ask at most `Q` adaptive binary revalidation questions. It returns a vector in `{0,1,ABSTAIN}^k`, abstaining on at most `a` coordinates, and it must never be wrong on a non-abstained coordinate.

### Theorem LI-1 — lifecycle identifiability frontier

Every such learner satisfies

```text
min(C,B) + Q + a >= ceil(log2 M).
```

### Proof

The certified acquisition transcript has at most `2^C` values and the persistent state has at most `2^B` values. Because the latter is computed from the former, at most `2^min(C,B)` distinct persistent states can matter. From any state, `Q` adaptive binary answers generate at most `2^Q` future transcripts. A partial output with at most `a` abstentions is compatible with at most `2^a` complete binary response profiles. Therefore one algorithm can soundly cover at most

```text
2^min(C,B) * 2^Q * 2^a
```

distinct profiles. This number must be at least `M`. Taking `log2` proves the claim.

This theorem counts certified information rather than treating proof traces as free. It also treats abstention as an explicit resource, not as a silent success.

## 2. Exact modular-revocation family

Let `p` reusable binary modules be represented by `theta in F_2^p`. Ordinary endpoint training reveals

```text
A theta = b
```

where `A` has rank `r`. Hence `p-r` module degrees of freedom remain. For each module and each of `h` authority/scope contexts, a hidden bit `z[i,j]` records whether an independently valid alternative support exists after the training-time primary support is revoked.

A held-out compositional suite supplies `p-r` independent linear functionals completing the row space of `A`. A revocation suite asks the scope-specific support questions `z[i,j]`. The complete future profile is

```text
F(theta,z) = (C theta, z)
```

and has

```text
N = (p-r) + p*h
M = 2^N.
```

Thus LI-1 becomes

```text
min(C_acq,B) + Q + a >= (p-r) + p*h.
```

The bound is tight in this direct-bit model: store `s` profile bits, query `q` later, and abstain on `a`, with `s+q+a=N` and `C_acq>=s`.

## 3. One-witness retention impossibility

Suppose training reveals one valid support `S` for a learned operator and `e in S`. Two monotone worlds are consistent with the same training record:

1. `S` is the only valid support;
2. `S` is valid and an independent support `T` with `e notin T` also exists.

After `e` is revoked, always retaining is unsound in world 1; always retracting destroys a still-supported useful operator in world 2. Therefore a sound and retention-complete system needs at least one of:

- additional certified acquisition information about alternative support;
- a future revalidation query;
- explicit abstention.

This is the smallest non-vacuous example of why a single successful training trace is not enough for safe lifelong reuse.

## 4. Exact finite validation

The executable witness uses

```text
p=4, r=2, h=2, N=10.
```

It enumerates `2^10 = 1024` latent lifecycle worlds. All 1024 produce distinct complete future profiles. A planted mutation deletes one independent future obligation; the map collapses to 512 profiles, each shared by exactly two worlds. The planted mutation demonstrates that the injectivity gate can fail.

The first checker draft exposed and retained an implementation defect: deleting coordinate `-1` with Python slices duplicated most of the profile rather than removing the final coordinate. The corrected checker normalizes negative indices before deletion. No theorem statement changed; the hostile mutation now genuinely creates the predicted collision.

## 5. Strongest-parent subtraction

The theorem does not claim novelty for any individual ingredient.

| Parent family | What it already owns | What is still being tested |
|---|---|---|
| computational-trace and query learning | extra observations/queries can change identifiability and sample complexity | a lifecycle objective joining unseen modular use with later support revocation |
| teaching dimension / privileged information | side information can distinguish a target version space | exact cost of certified acquisition retained for future authority-scoped challenges |
| proof-carrying code and certifying computation | certificate-gated execution | learning reusable procedures and maintaining their justification over time |
| TMS/ATMS, provenance, incremental and self-adjusting computation | dependency recording, invalidation and output-sensitive recomputation | dependencies/support alternatives are themselves learned under limited certified evidence |
| certified and ticketed unlearning | deletion guarantees and stored auxiliary information | selective retention of still-supported reusable procedures under multiple independent supports and scope changes |
| dynamic graph coloring / recourse | representation-size versus update-recourse trade-offs | joint acquisition-learning-support-revalidation frontier |
| recurrent/looped Transformers | implementation of iterative finite computations | no architecture claim unless an equal-interface compilation incurs a proved resource loss |

The information inequality is elementary and may be parent-owned. The potential contribution is the problem class and a stronger theorem, not the counting step alone.

## 6. Required upgrade before a novelty claim

A publishable breakthrough requires all of the following:

1. replace direct hidden bits by a natural compositional-program or learned-operator class;
2. give the strongest parent exactly the same observations, certificate bits, memory, verifier and future queries;
3. prove a computational, query, communication or cell-probe lower bound, not only a cardinality bound;
4. provide an output-sensitive constructive learner/repair algorithm;
5. prove useful retention, so delete-everything cannot pass;
6. compile the algorithm into an equally provisioned recurrent Transformer and state whether the result is architecture-neutral;
7. complete theorem-level primary-source subtraction and independent hostile proof reconstruction.

## 7. Candidate stronger statement

The next proof target is provisionally:

> For a natural class of compositional programs with multiple scoped, independently certifiable support paths, characterize the optimal frontier among certified acquisition, persistent proof/dependency state, post-change revalidation queries, procedural recourse, abstention, false retention and held-out recombination. Prove a strict lower/upper separation from a comparator that receives the same total information but lacks a lifecycle-sufficient representation—or show that no such separation exists.

## 8. Authority

This artifact establishes a theorem and a finite calibration under its stated model. It establishes neither literature priority nor an OCM architecture advantage, natural-language competence, parameter efficiency, quantum advantage or publication readiness.
