# Attention Sequence Theorem V1 — Corrigendum V2

**Capsule:** `gmi-attention-sequence-v1`  
**Issue:** #602 B7 / sequence-routing microscope  
**Strongest parents:** decision-tree/query complexity, sparse routing/local algorithms, amortized/lifecycle accounting  
**Evidence:** P1 algebra + P2 exact finite checks  
**Ceiling:** bounded G2 mechanism/phase law; **not** a universal attention theorem

## 0. Historical correction

The original V1 text contained two load-bearing mistakes and is corrected here rather
than silently overwritten conceptually:

1. its T2 formula `log(M/K)/log(N/H)` was not derived from the lookup-cost model
   implemented by the witness;
2. its T3 section wrote mutually incompatible cost equations and even displayed an
   impossible inequality of the form `C/K > L + C/K`.  The later
   `ggu/phase-rv-attention-fix` branch also reversed the meaning of the crossover
   in code/tests and therefore is **not** an authority.

Those formulas are retracted.  T1 is retained with a missing feasibility guard fixed;
T2 and T3 below are the corrected results.  The stronger access-sufficiency statement
in #694 T602-34 remains the parent-first authority for *whether* a sparse reader is
exactly admissible.  The present capsule only prices already-admissible schemes.

---

## 1. Registered cost model

Let an exact obligation require access to `M >= 1` relevant targets.  Assume a full
reader and a sparse/local reader are both already proved sufficient for the protected
obligation.

- `C > 0`: charged cost per attended target;
- `K`: sparse slot count, required to satisfy `0 < K < M`;
- `L >= 0`: charged lookup/routing cost **per registered target** under this bounded
  model.

Then

\[
C_{full}=MC,
\]

\[
C_{sparse}=KC+ML.
\]

No cost inequality is allowed to legalize an insufficient access pattern; obligation
sufficiency comes first, as in #694 T602-34.

---

## 2. T1 — exact sparse/full cost condition

For legal `0<K<M`, sparse routing is strictly cheaper iff

\[
KC+ML<MC
\iff
L<C\left(1-\frac KM\right).
\]

This is an arithmetic identity.  In particular:

- `K=0` is **not** treated as a valid attention solution merely because its arithmetic
  cost is small;
- at `K=M`, a sparse implementation that still pays positive lookup cost is more
  expensive than full routing rather than "equivalent";
- equality is a tie and does not count as a strict sparse win.

The result is conditional on exactness/admissibility and says nothing universal about
attention architectures.

---

## 3. T2 — locality-induced lookup phase boundary

Freeze a locality coordinate `lambda in [0,1]` and a positive worst/base lookup price
`L0`.  In this microscope locality reduces lookup cost linearly:

\[
L(\lambda)=L_0(1-\lambda).
\]

Substitute that *same* cost into T1.  The raw strict threshold is

\[
\lambda^*=1-\frac{C(1-K/M)}{L_0}.
\]

Therefore, for legal `0<K<M`,

\[
C_{sparse}<C_{full}
\iff
\lambda>\lambda^*.
\]

The raw threshold is deliberately not clipped:

- `lambda* < 0` means sparse wins for every legal `lambda in [0,1]`;
- `0 <= lambda* < 1` gives an actual within-domain phase boundary;
- `lambda* >= 1` means no strict sparse win occurs in the registered locality range.

This replaces the unsupported logarithmic V1 formula.  Other locality/lookup laws can
be registered, but they must derive their own threshold from their own charged cost
function rather than reuse this one.

---

## 4. T3 — growing-sequence carry crossover

The original V1 attempted to compare a fixed-slot reader with a state-carry reader but
used incompatible costs.  Corrigendum V2 registers one coherent finite model.

Let the number of target obligations grow with sequence length as

\[
M(N)=N\,\lceil\log_2 N\rceil,
\]

with `M(1)=1`.  Compare:

### Fixed-slot serving

A fixed reader with `K` parallel slots pays

\[
C_F(N)=M(N)\frac CK.
\]

### Retained state / recurrent carry

A carry mechanism pays a one-time build/retention cost `B >= 0` and per-target lookup
cost `L >= 0`:

\[
C_R(N)=B+M(N)L.
\]

Define the per-target marginal saving

\[
\Delta=\frac CK-L.
\]

Then:

- if `Delta <= 0`, no finite sequence length makes the recurrent carry strictly
  cheaper in this model;
- if `Delta > 0`, recurrent carry is strictly cheaper exactly when

\[
M(N)\Delta>B.
\]

Hence the exact crossover is the least positive integer

\[
N^*=\min\{N\ge1:M(N)(C/K-L)>B\}.
\]

This is simply a retained-structure amortization law.  A larger build cost moves the
crossover later.  Increasing `K` makes fixed serving cheaper and therefore also moves
the crossover later; once `C/K <= L`, the crossover disappears.

### Registered exact example

For

```text
C = 1
L = 1/16
B = 16
K in {1,2,4,8,16}
```

the exhaustive integer witness gives

```text
K=1   -> N*=6
K=2   -> N*=10
K=4   -> N*=18
K=8   -> N*=43
K=16  -> NO_FINITE_CROSSOVER
```

At each finite `N*`, the state-carry cost is strictly lower and at `N*-1` it is not.
The `K=16` terminal follows exactly from `C/K=L`.

---

## 5. Scope, parent subtraction, and falsifiers

Parent work owns sparse/adaptive querying, locality/indexing, state-space recurrence,
and amortized lifecycle accounting.  The only GMI-relevant residual here is the common
obligation/resource bookkeeping and its prospectively registered phase boundary.

This capsule does **not** establish:

- that sparse access is sufficient for an arbitrary task;
- a universal locality law;
- a universal long-context architecture winner;
- a real-scale transformer/state-space result;
- architecture novelty.

Falsifiers at this registered scope are direct:

1. a legal `(M,K,C,L)` cell where T1's algebra disagrees with charged costs;
2. a `lambda` cell where T2's direct charged comparison disagrees with the derived
   threshold;
3. a reported finite `N*` where recurrent carry does not strictly win, or where it
   already wins at `N*-1`;
4. a finite crossover reported when `C/K <= L`.

`attention_witness.py` uses exact `Fraction` arithmetic for every acceptance decision,
and `test_attention_sequence.py` checks the theorem under ordinary and optimized
Python in CI.
