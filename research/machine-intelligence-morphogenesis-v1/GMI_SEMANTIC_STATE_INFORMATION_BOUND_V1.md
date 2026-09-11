# GMI Semantic-State Information Bound v1

Status: **PARENT-OWNED FORMAL CORRECTION / INTERPRETATION BOUND**

Refs: GMI-v1, `GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_V1.md`, #233, #377.

## 1. Why this correction is necessary

Track B previously used finite examples where a global developmental state space contains exponentially many distinguishable configurations, e.g.

\[
|S| = 3^n.
\]

That fact does **not** imply that encoding one current state requires exponentially many bits.

For a finite exact state set of size `N`, the fixed-length information lower bound is logarithmic in `N`:

\[
b \ge \lceil\log_2 N\rceil.
\]

Therefore, if

\[
N=3^n,
\]

then

\[
b\ge \lceil n\log_2 3\rceil,
\]

which is linear in `n`.

So a factored representation of `n` ternary variables is not obtaining an exponential reduction in the information needed to identify one exact current state merely because the global state space has `3^n` members.

This distinction is now load-bearing in GMI.

---

# 2. Exact finite state-information lower bound

Let `S_Ω` be a finite exact semantic developmental sufficient-state set for a registered obligation `Ω`, with

\[
N=|S_\Omega|.
\]

Suppose every state in `S_Ω` is pairwise future-distinguishable under the registered intervention/development class, so exact semantic preservation requires unique decoding of the current semantic state.

Any lossless finite encoding must provide at least `N` distinct code states.

For a fixed-length binary code of length `b`, there are at most `2^b` codewords, therefore

\[
2^b\ge N
\]

and hence

\[
\boxed{b\ge\lceil\log_2 N\rceil}.
\]

This is ordinary counting/source-coding mathematics, not a new GMI theorem.

---

# 3. Distribution-sensitive version

If semantic states occur under a registered distribution `p(s)` and a uniquely decodable/prefix code is used, expected code length satisfies the familiar source-coding lower bound

\[
\mathbb E[\ell(S)] \ge H(S),
\]

up to the assumptions of the selected coding theorem/formalism.

This again concerns **state information**, not the time or program complexity of updating, querying or predicting the state.

GMI must not substitute entropy for those other costs without a justified bridge.

---

# 4. Four quantities that must remain separate

## 4.1 Current-state information

How many bits are needed to identify the current exact semantic state?

For `N=3^n` exact states:

\[
\Theta(\log N)=\Theta(n).
\]

## 4.2 Explicit global state enumeration

How many global states would an explicit table enumerate?

For `n` ternary variables:

\[
3^n.
\]

This can be exponential even though one current state is encodable in linear bits.

## 4.3 Transition/model description complexity

How large is an explicit description of the update dynamics?

A flat transition table over all global states can require exponentially many entries, while a factored/shared local rule can be much smaller when the true dynamics admit that structure.

For example, a designed system with `n` cells sharing one local transition law may require:

```text
O(n) current-state storage
+ O(1) or compact shared rule description
```

whereas a fully enumerated global transition table may scale with the number of global configurations.

This is a **model/dynamics description** advantage, not a current-state information advantage.

## 4.4 Update/query/revision work

A correct factorization can allow one intervention to touch only its actual dependency cone.

This may yield local rather than global update/recomputation work.

But locality must be earned by the true dependency semantics; it cannot be inferred merely from storing variables separately.

---

# 5. Factorization benefit — corrected statement

The admissible statement is:

> A factored realization can be exponentially more compact than a flat **enumeration of global transition/model structure**, and can support more local update/query/revision when the obligation's true dependency structure permits it, even though the information needed to encode one exact current state may remain only linear in the number of factors.

The inadmissible shortcut is:

```text
3^n possible global states
=> exponential bits required for one state
=> factorization exponentially compresses current-state information
```

That implication is false.

---

# 6. Consequence for the “basic cognitive unit” question

This correction strengthens the view that useful “basic units” may be **factorization coordinates**, not metaphysical atoms.

A local unit can be valuable because it provides:

```text
compact shared transition structure
local causal/update boundaries
reusable computation
parallelism
sparse activation
modular revision
```

without implying that the unit is information-theoretically irreducible or that the global semantic state intrinsically needs exponential storage.

Therefore:

```text
FACTOR = useful realization coordinate
```

must remain distinct from:

```text
FUNDAMENTAL COGNITIVE ATOM = unearned claim
```

---

# 7. Relation to morphology

Two semantically equivalent morphologies may encode the same current semantic information while differing greatly in:

```text
transition/model description size
build/training cost
serving work
update/revision locality
verification cost
parallelism/hardware fit
plasticity
morphogenetic discovery cost
```

These are exactly the realization-level quantities governed by `GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_V1.md`.

Thus the important morphology question is not simply:

> Which architecture compresses the state space most?

It is:

> Which admissible realization gives the best complete developmental/lifetime frontier for the registered obligation?

---

# 8. Continuous / stochastic / approximate boundary

The finite exact counting bound does not directly settle:

```text
continuous state spaces
finite-precision numerical realizations
stochastic latent-state models
lossy/approximate state representations
belief states
quantized neural representations
```

Those require explicit precision, distortion, noise, topology or measure assumptions.

Rate-distortion, Information Bottleneck, predictive-state and approximation theory receive first refusal.

Do not claim an exact quotient or bit lower bound by silently discretizing a continuous system after observing outcomes.

---

# 9. External memory and hidden state

An implementation may not evade the bound by moving information into an uncounted side channel.

For a realization-level storage claim, count all state required to distinguish the registered semantic situations, including where applicable:

```text
parameters
persistent memory
optimizer state
replay buffers
indexes
external databases
caches
latent program state
legally available external memory
```

The semantic quotient itself remains implementation-independent; the storage/resource accounting belongs to the realization.

---

# 10. Parent ownership

This correction is parent-owned by ordinary information/counting and source-coding theory, together with state-minimization/factorization parents.

Track B claims no novelty for:

\[
b\ge \lceil\log_2 N\rceil.
\]

Its role is to prevent an invalid inference inside the larger GMI synthesis.

---

# 11. Registered proposition

`GMI-RP11 — semantic-state information lower bound / factorization interpretation`

For a finite exact semantic sufficient-state set with `N` pairwise future-distinguishable states, every lossless fixed-length binary encoding requires at least

\[
\lceil\log_2 N\rceil
\]

bits.

For `N=3^n`, this is `Θ(n)`, not `Θ(3^n)`.

Any exponential factorization claim must therefore identify a different quantity, such as:

```text
global transition-table size
model description size
search enumeration
update/revision work
```

and prove/measure that quantity explicitly.

---

# 12. Terminal

```text
SEMANTIC_STATE_INFORMATION_BOUND_CORRECTION_REGISTERED_V1
```

Claim boundary:

> This correction narrows interpretation. It does not weaken the separate empirical possibility that factorized morphologies obtain very large model-description, search, locality or lifetime-resource advantages.
