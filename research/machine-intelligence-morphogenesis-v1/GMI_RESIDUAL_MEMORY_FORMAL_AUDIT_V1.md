# Residual-memory formal audit and parent comparison (B12)

Date: 2026-09-14. Lane: `machine-intelligence-morphogenesis-v1`.

This is an additive audit of:

- `GMI_RESIDUAL_MEMORY_DERIVATION_V1.md`;
- `gmi_microscope/residual_memory_witness.py`;
- `microscopes/results/STAGE_RESIDUAL_MEMORY_V1.json`.

It closes a documentation gap in B12 of #602: the landed witness already derives
and reproduces the residual quotient, external-versus-absorbed boundary,
frequency/index law, update/drift law, and label-blind recovery, but the parent
comparison did not explicitly separate ordinary RAG, adapters, caches,
databases and nearest-neighbour datastores.

Nothing here changes the witness, receipt, runtime, candidate grammar, prices or
scientific result. The purpose is to make the mathematics and the parent
boundary explicit enough that the checklist can be read literally rather than
by implication.

## 0. Scope and claim ceiling

The result is an **exact finite-model characterization**, not a universal theorem
about every retrieval system.

The declared model has:

- a finite input set `X`;
- a target response `y : X -> Y`;
- an already installed description `g : X -> Y`;
- a residual set `R = {x in X : g(x) != y(x)}` of size `k`;
- deterministic exact serving;
- non-negative scalar prices for installation, probing, lookup, indexing and
  repair;
- an external side store whose routing key remains explicit and whose payload
  decoder is not permitted to hide arbitrary key-specific computation.

The executable witness instantiates this model on 16 four-bit inputs, three
responses, and a 23-rule description class. The algebra below is more general
than those particular numbers, but **only inside the declared cost and decoder
model**.

Current evidence class:

```text
EXACT_FINITE_ENUMERATION_PLUS_ALGEBRA
NO_REAL_SCALE_REPLICATION_CLAIM
NO_RAG_NOVELTY_CLAIM
NO_UNIVERSAL_EXTERNAL_MEMORY_OPTIMALITY_CLAIM
```

## 1. Predictive-target residual quotient

Let

```text
R = {x in X : g(x) != y(x)}.
```

Define an equivalence relation on residual keys by

```text
x ~R x'  iff  y(x) = y(x').
```

This is deliberately a quotient of the **payload obligation**, not of the keys.
The key set is still needed to decide whether and where the description fails.

### Proposition B12-Q — minimum payload alphabet

For a residual store whose key router selects a payload class and whose
payload-only decoder returns the demanded response, the minimum number of
payload symbols required for exactness is

```text
|R / ~R| = |y(R)|.
```

**Lower bound.** Suppose two residual keys `x,x'` require distinct target
responses but are assigned the same payload symbol. The payload-only decoder
receives the same symbol in both cases, so determinism forces the same decoded
response. It therefore cannot equal both `y(x)` and `y(x')`. Every distinct
required response needs a distinct payload symbol.

**Upper bound.** Assign each residual key the payload symbol `y(x)` and decode a
symbol as itself. This uses exactly `|y(R)|` payload symbols and serves every
residual key exactly.

Therefore the lower and upper bounds meet. QED.

This is exactly the distinction exercised by the landed matched twin:
`residual_collapse` and `residual_distinct` have the same base rule, the same
three residual keys and the same residual size, while their payload quotient has
one versus three classes.

**Boundary.** This is not a general code-length theorem. If the decoder is
allowed to inspect the key and contain arbitrary key-specific logic, information
can migrate from the payload into the decoder. The theorem is for the declared
key-router plus payload-decoder decomposition.

## 2. External memory versus full parametric absorption

Write the following prices:

```text
A  = cost to absorb/install one residual item into the description
W  = cost to write one residual item to the external store
E  = ordinary description-evaluation cost per query
P  = residual-membership probe cost per query
L  = external payload lookup cost on a residual hit
N  = number of served queries before the representation is rebuilt
f  = probability a served query lies in the residual
k  = residual cardinality
```

Under the witness accounting,

```text
C_external = k W + N (E + P + f L)
C_absorbed = k A + N E.
```

### Proposition B12-A — exact absorption crossover

External holding is strictly cheaper exactly when

```text
(A - W) k > N (P + f L).
```

**Proof.** Subtract `N E` from both costs, move `k W` to the right and collect
terms. No approximation is used. QED.

When `A > W` and `P + fL > 0`, the query-volume boundary is

```text
N* = (A - W) k / (P + f L),
```

with external holding preferred below the boundary and absorption above it.
If `A <= W`, external storage has no fixed-cost advantage to amortize and cannot
win in this model while its serving overhead is non-negative.

For the witness prices `A=4`, `W=1`, `P=1`, `L=3`, the committed rows reproduce:

```text
k=3, f=3/16  -> N* = 144/25
k=1, f=1/16  -> N* = 48/19
k=5, f=5/16  -> N* = 240/31
k=6, f=3/8   -> N* = 144/17.
```

The direction matters: for a fixed residual, more query reuse favors absorption
because the external side pays a query-time toll while absorption pays a larger
one-time installation cost.

## 3. Retrieval frequency and the probe law

The witness separates residual **size** from residual **query frequency**. If
residual keys receive relative query weight `w` and non-residual keys weight 1,
then for universe size `M`,

```text
f = w k / (w k + (M-k)).
```

Compare two external-serving policies after ordinary description evaluation:

```text
gated lookup       = P + f L
unconditional      = L.
```

### Proposition B12-F — probe threshold

Probe-before-lookup is strictly cheaper exactly when

```text
P < (1-f) L.
```

**Proof.** `P + fL < L` iff `P < L - fL = (1-f)L`. QED.

With the witness prices `P=1`, `L=3`, this becomes

```text
f < 2/3.
```

This law is independent of the way `f` was generated. Residual cardinality can
influence frequency, but size and frequency are not interchangeable variables;
the committed sweep contains verdict flips at fixed `k` and at fixed `w`.

## 4. Index-building law

The executable model for this comparison is explicit: an unindexed residual hit
scans `k` entries, an indexed hit costs one access, and index construction costs
`B` per stored item.

Without an index, hit work over `N` queries is `N f k`. With an index it is
`Bk + Nf`.

### Proposition B12-I — index crossover

Index construction is strictly beneficial exactly when

```text
N f (k - 1) > B k.
```

**Proof.** `Bk + Nf < Nfk` iff `Bk < Nf(k-1)`. QED.

Consequences inside this model:

- `k=1` can never repay an index, because the saving term is zero;
- increasing `N` or `f` can move a multi-item store across the boundary;
- the result is a law for the declared scan-versus-index realization, **not** a
  theorem that every database index has this complexity or build cost.

The witness instantiates `B=2` and exhibits both indexed and non-indexed sides,
including a fixed-`k=3` frequency flip at `N=64`.

## 5. Changing knowledge: local repair versus re-derivation

External memory is useful under change only if changed content can be identified.
Let `d` addressed residual entries change and let one atomic write cost `W`.

### Proposition B12-U1 — exact local-write cost

If one write can change at most one independently addressed entry, repairing
exactly `d` changed residual entries requires and suffices to perform `d` writes,
for cost `dW`.

**Necessity.** Each changed addressed entry must have its old payload replaced;
by assumption one write can replace at most one such entry, so fewer than `d`
writes leaves at least one changed entry stale.

**Sufficiency.** Write the new payload to each of the `d` changed addresses.
QED.

This formalizes the witness's locality result. It does not say a description can
never be locally edited; it says that a side store exposes per-entry
addressability by construction, while the particular description class must pay
whatever repair/research cost its realization entails.

For a general patch-versus-rederive comparison define:

```text
rho(d)    = one-time cost of constructing the best fresh description after d changes
S_p(d)    = per-query serving cost of the patched representation
S_f(d)    = per-query serving cost of the fresh representation.
```

Then

```text
C_patch(d,N) = dW + N S_p(d)
C_fresh(d,N) = rho(d) + N S_f(d).
```

### Proposition B12-U2 — drift/query boundary

Patch is strictly cheaper exactly when

```text
dW + N S_p(d) < rho(d) + N S_f(d).
```

If `G(d) = S_p(d)-S_f(d) > 0`, fresh re-derivation wins above

```text
N > (rho(d)-dW) / G(d),
```

provided the numerator is positive. There is **no theorem that this boundary is
monotone in d**: both `rho(d)` and `G(d)` may change when the best fresh
description changes class.

That is why the committed witness correctly rejects the intuitive slogan
"patch until it gets messy, then retrain": its exact boundary rises, peaks, and
then falls when the best fresh rule changes.

## 6. Reuse lifetime under invalidation

Let

```text
S = one-time storage cost
r = nominal reuse count
Llife = number of valid uses before the item becomes stale
C = recomputation cost per use
U = reuse/lookup cost per use.
```

Only `min(r,Llife)` uses can be credited to the retained item before knowledge
moves. Substituting effective reuse into PVR-3 yields

```text
S < (min(r,Llife)-1) (C-U).
```

This is a validity cap, not a heuristic penalty. Uses after invalidation cannot
be counted as savings because they answer the old obligation. If exact
revalidation on every use costs as much as recomputation (`U >= C`), the right
side is non-positive and retention has no strict cost advantage in this model.

## 7. Strong-parent comparison: what each familiar mechanism is

The point of this table is subtraction, not renaming. The mature mechanisms own
their ordinary functions; B12 contributes only the conditional boundary laws
above at the registered finite scope.

| parent / mechanism | where mutable knowledge lives | query-time external lookup? | relation to the B12 object | decisive distinction |
|---|---|---:|---|---|
| **full parametric absorption / fine-tuning** | principal model/description parameters | no | `absorb_all` side of the crossover | larger install/retraining cost may buy lower per-query toll |
| **Houlsby-style adapters** | small auxiliary trainable parameter modules while the base is frozen | normally no datastore retrieval | an **internal residual parameterization**, analogous to the audit's internal holding | residual state is executable parameters, not keyed external evidence |
| **ordinary RAG (Lewis et al.)** | non-parametric corpus/index plus parametric generator | yes | a broader external-memory parent; it becomes the B12 residual specialization only when the retrieved corpus is restricted to baseline prediction failures | RAG need not be residual relative to the parametric predictor; it may retrieve redundant/supporting evidence too |
| **kNN-LM / nearest-neighbour datastore (Khandelwal et al.)** | external key/value exemplars | yes | closest-key side-store parent | metric alignment controls whether a strict subset of keys can stand in for exact residual keys |
| **continuous cache (Grave et al.)** | recent activations/history | yes, transiently | cache parent when base computation can still answer after eviction | a survivable miss changes cost; a non-survivable residual miss changes correctness |
| **database / exact external store** | authoritative structured external records | yes | infrastructure capable of realizing either a full store or a residual store | "database" describes the storage/query substrate, not whether contents are predictor-relative residuals |

Primary references used for this taxonomy:

- Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP
  Tasks* (2020), https://arxiv.org/abs/2005.11401 .
- Houlsby et al., *Parameter-Efficient Transfer Learning for NLP* (2019),
  https://proceedings.mlr.press/v97/houlsby19a.html .
- Khandelwal et al., *Generalization through Memorization: Nearest Neighbor
  Language Models* (2019/2020), https://arxiv.org/abs/1911.00172 .
- Grave et al., *Improving Neural Language Models with a Continuous Cache*
  (2016/2017), https://arxiv.org/abs/1612.04426 .

### 7.1 Cache versus residual store is a correctness distinction

Let `b(x)` be the answer available after the auxiliary holding is evicted.
For a held key `x`:

```text
cache-like at x      iff b(x) is still correct and eviction only changes cost;
residual-essential   iff b(x) is incorrect/undefined and eviction changes correctness.
```

The landed eviction twin tests exactly this boundary: evicting entries already
covered by a correct rule preserves correctness; evicting residual entries does
not.

### 7.2 Adapter versus external residual is a state-placement distinction

An adapter can encode the same *function* as a residual holding without being an
external memory system. If its parameters are consulted as part of the model's
ordinary forward computation, it belongs on the internal/absorbed side of the
state-placement comparison. Calling it "RAG" would erase the very query-time
resource term B12 is deriving.

### 7.3 RAG versus residual RAG is a set-inclusion distinction

Let `D_RAG` be all records available to an ordinary retriever and `R` the
predictor's failure set. A residual-memory realization has external contents
whose authority is scoped to the residual obligation. Ordinary RAG does not
require `D_RAG` to equal `R`; it can contain evidence for points the parametric
model already answers correctly. Therefore:

```text
residual external memory  is a structural specialization of external retrieval;
external retrieval        is not, in general, a residual memory.
```

This prevents the checklist from "deriving RAG" merely by naming any side store.

## 8. Neutral recovery: what was and was not recovered

The landed neutral search never uses the substrings

```text
retriev, rag, index, database, adapter, cache, memor
```

in its candidate vocabulary. It enumerates mechanisms such as which subset to
hold, whether it is internal or on a side list, exact versus closest keying, and
whether to test first. Behaviourally identical candidates are collapsed and
remaining ties are broken **against** external holding.

The committed receipt nevertheless contains both internal and external selected
machines; under change, external selections increase relative to internal ones.
It also selects closest-key behavior only in the obligation where the metric
supports the compression.

The correct claim is therefore:

> In this finite candidate grammar and registered price model, label-blind search
> recovers residual-memory behavior in cells where that behavior is strictly
> cost-minimal after behavioral-equivalence collapse.

It is **not**:

> Any sufficiently general architecture search will rediscover RAG, databases,
> adapters, or an optimal memory architecture.

## 9. Falsifiers and audit disposition

The audit fails or must be weakened if any of the following is exhibited:

1. a residual payload in the declared decoder model uses fewer than `|y(R)|`
   payload classes while remaining exact;
2. direct substitution into the cost definitions contradicts any crossover
   equation above;
3. a claimed cache remains correct only because correctness logic was hidden in
   the cache rather than in the base description;
4. an alleged residual store contains arbitrary non-residual evidence while the
   claim still treats its storage/query cost as if only `R` were held;
5. a neutral-search win depends on a family label or banned architecture macro;
6. the result is promoted from the finite scalar model to a universal or
   real-scale RAG superiority claim without new evidence.

### B12 checklist mapping

| #602 B12 obligation | evidence | disposition |
|---|---|---|
| predictive-target residual quotient | landed witness §1 + Proposition B12-Q | supported at declared scope |
| external memory vs full parametric absorption | landed witness §3 + Proposition B12-A | supported at declared scope |
| retrieval frequency and index cost law | landed witness §3b/3c + Propositions B12-F/B12-I | supported at declared scope |
| adaptation/update law under changing knowledge | landed witness §4 + Propositions B12-U1/U2 + lifetime cap | supported at declared scope |
| compare ordinary RAG, adapters, caches, databases | §7 of this audit, with strongest-parent subtraction | supported as a taxonomy/boundary comparison, not a novelty claim |
| neutral recovery of residual-memory behavior | landed witness §6 + §8 claim ceiling | supported at declared finite grammar scope |

Terminal:

```text
B12_RESIDUAL_MEMORY_DERIVATION_SUPPORTED_AT_REGISTERED_FINITE_SCOPE
PARENT_MECHANISMS_OWN_RAG_ADAPTER_CACHE_DATABASE_FUNCTIONS
REAL_SCALE_AND_UNIVERSAL_ARCHITECTURE_CLAIMS_NOT_ESTABLISHED
```
