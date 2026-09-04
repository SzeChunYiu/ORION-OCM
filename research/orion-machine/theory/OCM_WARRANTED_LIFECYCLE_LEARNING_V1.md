# Warranted Lifecycle Learning

**Candidate formal object V1 — theorem calibration supported; novelty unresolved**

Date: 2026-09-03  
Scientific umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Focused P0 lane: ORION-V2 #221

## 1. Why a new object is needed

A learned system can be behaviorally correct now yet epistemically unsafe after an evidence, scope, policy, authority or verifier change. Conversely, it can be safe by retracting or abstaining while still retaining deleted information internally. Therefore current behavior, machine unlearning and warrant-preserving lifecycle behavior are different objectives.

Working term: **Warranted Lifecycle Learning (WLL)**. The name is provisional and creates no novelty authority.

A WLL system learns reusable procedures together with machine-checkable conditions under which they may remain live. It is evaluated over future task and update sequences, not only on a static test distribution.

## 2. State and update model

A warranted state contains at least

```text
x = (f, J, E, C, A, version, status)
```

where `f` is learned functional/procedural behavior; `J` is support/dependency structure; `E` is evidence state; `C` is certificate/checker state; `A` is authority/scope; `version` is an epoch identity; and `status` is live, revalidate, retract or abstain.

The update alphabet may contain evidence revocation/addition, scope change, authority expiry, verifier replacement, policy change and representation reminting.

## 3. Current versus lifecycle equivalence

For states `x,y`:

- `x ==_0 y` when all current task responses agree;
- `x ==_L y` when all responses agree after every finite permitted update sequence and subsequent task query.

### Theorem WLL-1 — strict warrant refinement

```text
x ==_L y  implies  x ==_0 y.
```

The implication can be strict.

**Proof.** The empty update sequence is permitted, so lifecycle agreement implies current agreement. For strictness, take two states with the same live skill and current output. In one state the skill has only the current primary support; in the other it also has an independent backup support. Revoking the primary support requires retract in the first state and retain in the second. Thus they are currently equivalent but not lifecycle equivalent.

A representation quotienting states only by current behavior can therefore destroy information required for later safe reuse.

## 4. Warrant-lift lower bound

Consider `p` skills and `h` authority/scope contexts per skill. During training every skill has a valid primary support, so all worlds have the same current behavior. Let `z[i,j]` indicate whether skill `i` has an independent backup support in context `j`.

There are `2^(p*h)` current-behavior-identical warrant worlds. Revoking the primary support and challenging each `(i,j)` yields response vector `z`, so all worlds are lifecycle-distinct.

### Theorem WLL-2

Any exact lifecycle representation with at most `C` certified acquisition bits, `B` persistent bits, `Q` future binary revalidation answers and at most `a` abstentions satisfies

```text
min(C,B) + Q + a >= p*h.
```

This is the support-only specialization of the lifecycle-identifiability frontier. It quantifies the minimum information that must refine one behavioral equivalence class.

## 5. Behavioral unlearning and warrant correctness are incomparable

### Theorem WLL-3

Under their standard observables, exact behavioral/model unlearning neither implies nor is implied by warrant correctness.

**Unlearning without warrant.** A training algorithm may output the same constant predictor before and after deletion, so exact behavioral unlearning is trivial. If the system nevertheless leaves a live claim whose sole support was the revoked record, warrant correctness fails.

**Warrant without unlearning.** A system may retain a deleted bit inside its raw model but mark every output depending on it unavailable and abstain. The authorized surface is warrant-correct, but the raw model is not equal in state or distribution to retraining without the record.

WLL is therefore not a synonym for privacy-oriented or distributional machine unlearning. A complete system may require both.

## 6. Authority non-amplification

Suppose a composite procedure requires components with declared authority scopes `S_1,...,S_m`.

### Theorem WLL-4

Without an additional bridge certificate, the sound authority scope of the composition is contained in

```text
intersection_i S_i.
```

**Proof.** For any context outside one component scope, construct a model in which every component satisfies its certificate inside scope while that component is wrong in the extra context. Authorizing the composite there would accept an unsupported output.

The exact checker enumerates finite scope tuples and includes a planted union-scope countermodel plus equal-scope no-alarm cases.

## 7. Exact finite calibration

The witness uses three skills and two contexts per skill:

- 64 latent warrant worlds;
- one current behavior class;
- 64 lifecycle equivalence classes;
- six additional exact lifecycle bits;
- deleting one future challenge produces 32 two-world collision classes;
- exact behavioral unlearning without warrant correctness;
- warrant correctness without exact model unlearning;
- exhaustive finite authority-scope checks with both over-authorization countermodels and no-alarm cases.

## 8. Strongest-parent attack

WLL must be reduced against exact/query learning, teaching dimension, process/trace supervision, proof-carrying code, truth-maintenance, belief revision, provenance, proof maintenance, incremental/self-adjusting computation, exact/certified/modular/ticketed machine unlearning, trust-management and authority logics, automata/transducer minimization, and an equally provisioned recurrent/looped Transformer implementation.

WLL is not novel merely because these parents have not used the same name.

## 9. Potentially novel theorem programme

A genuine residual requires an interaction theorem, not this calibration bundle alone:

> For a natural class of compositional learned procedures, characterize the optimal frontier among acquisition of independently checkable local traces, persistent warrant/dependency state, unseen procedural recombination, evidence/scope/verifier updates, revalidation queries, state recourse, abstention, false retention and useful retention. Establish a strict computational/query/communication separation under equal information, or prove the strongest parent product sufficient.

The key condition is that the warrant structure is learned or certified under limited interaction, not handed to the algorithm for free.

## 10. Authority

Supported: current behavior can be strictly coarser than lifecycle behavior; warrant multiplicity requires additional information, queries or abstention; unlearning and warrant correctness are logically incomparable; composite authority cannot exceed component authority without a bridge certificate; finite witnesses and planted failures pass.

Not supported: literature priority; a new architecture class; superiority to an equally provisioned recurrent Transformer; natural-language competence; lower total training/inference cost; quantum advantage; publication readiness.
