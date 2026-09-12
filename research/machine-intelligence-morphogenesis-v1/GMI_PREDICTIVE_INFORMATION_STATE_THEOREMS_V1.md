# GMI Predictive-Information State Theorems v1

Status: **FORMAL STOCHASTIC PREDICTIVE-STATE HARDENING**

Status date: 2026-09-12.

Purpose:

> Add a representation-independent information lower bound for any state that is sufficient for registered future prediction. This complements exact response quotients, TV packing bounds and Hankel-rank linear realization theory.

---

# 1. Past, state and future

Let random variable `H` denote the registered past/history information available before state compression. Let `F` denote the protected future response/test variable under a frozen continuation/intervention protocol.

Let state be

\[
Z=s(H)
\]

(possibly stochastic with a registered encoder, but deterministic state is the base case).

Exact predictive sufficiency means

\[
F\perp H\mid Z.
\]

Equivalently, `H -> Z -> F` forms a Markov chain for the registered future variable.

---

# 2. Predictive information lower bound

## Theorem PI-1 — state information must dominate past-future mutual information

For any exact predictively sufficient state,

\[
I(H;F)
\le
I(H;Z)
\le
H(Z).
\]

### Proof

From the Markov chain `H -> Z -> F`, the data-processing inequality gives

\[
I(H;F)\le I(H;Z).
\]

For any variables,

\[
I(H;Z)\le H(Z).
\]

QED.

### Finite-state corollary

If `Z` takes at most `K` values,

\[
H(Z)\le\log_2K,
\]

so

\[
\boxed{K\ge2^{I(H;F)}}
\]

up to integer rounding in the cardinality statement.

Any exact finite state therefore requires at least

\[
\lceil I(H;F)\rceil
\]

bits of capacity in this information sense.

---

# 3. Interpretation

The quantity

\[
I_{pred}=I(H;F)
\]

is **predictive information**: how many bits about the registered future are present in the past.

GMI consequences:

```text
I_pred = 0:
    the registered future is independent of past; persistent state is not information-theoretically required for that future variable.

large I_pred:
    any exact sufficient state must preserve substantial information from history.
```

This bound is agnostic to whether the implementation is an RNN, HMM belief, SSM, explicit memory, Transformer context, database, or symbolic state.

---

# 4. State may contain more than predictive information

The lower bound need not be tight.

A state may additionally preserve:

```text
rollback/provenance
future obligations not included in F
control/intervention information
verification evidence
redundancy for robustness
implementation convenience
```

Conversely, the minimum semantic predictive state may have entropy strictly greater than `I(H;F)` because deterministic partition constraints/cardinality can exceed the average mutual-information requirement.

Thus predictive information is a lower bound, not a complete state constructor.

---

# 5. Controlled/interventional extension

Let future action/intervention sequence be `A` according to a registered protocol. Let future observations/rewards be `F`.

A control-predictive state sufficient under that protocol satisfies

\[
F\perp H\mid(Z,A).
\]

Conditioning on action plan gives

## Theorem PI-2

\[
I(H;F\mid A)
\le
I(H;Z\mid A)
\le
H(Z\mid A)
\le H(Z).
\]

Thus state must preserve information about history that remains predictive of future outcomes **after the planned intervention is known**.

This is the appropriate quantity for predictive-state control, not passive `I(H;F)` alone.

---

# 6. Belief-state connection

In a partially observed Markov system, the posterior belief over hidden state is a sufficient predictive state under the model.

PI-1 then implies the belief representation must have enough capacity to carry the predictive information from observation history into future observations/decisions.

A point estimate can fail when different posterior mixtures have the same mean but imply different futures/utilities.

This connects probabilistic-belief necessity to predictive information.

---

# 7. Approximate state via information bottleneck

For approximate prediction, exact conditional independence is relaxed. One natural registered trade is

\[
\min_Z I(H;Z)
\quad\text{subject to}\quad
I(Z;F)\ge I(H;F)-\epsilon
\]

or an obligation-specific distortion/risk constraint.

This is an information-bottleneck/rate-distortion style formulation of approximate predictive state.

GMI should not assume this scalar information criterion alone captures all semantic obligations, but it provides a principled base law for stochastic compression.

---

# 8. Connection to existing GMI state theorems

The predictive-state stack is now:

```text
future-response quotient:
    exact semantic equivalence classes for all registered continuations

TV packing:
    approximate cardinality lower bound from separated future distributions

Hankel rank:
    minimal exact linear predictive-state dimension

predictive information:
    representation-independent entropy/capacity lower bound
```

These are complementary, not competing.

---

# 9. Negative twin

If a benchmark exposes long histories but registered future target is IID and independent of them, then `I(H;F)=0`. A large context/recurrent state can still memorize history, but GMI should assign no predictive-semantic necessity to that memory unless another obligation (provenance, retention, etc.) demands it.

This guards against equating context length with intelligence.

---

# 10. Gap update

`GKF-07` / T4 now contains:

```text
exact future-response quotient minimality            CLOSED
TV packing lower bound                               CLOSED
linear Hankel-rank realization theorem               CLOSED/PARENT
predictive mutual-information lower bound            CLOSED
controlled conditional-information extension         CLOSED
finite-horizon identifiability no-go                 CLOSED

finite-data predictive-information estimator         OPEN
state construction attaining bound                   OPEN in general
nonlinear lifecycle-optimal realization              OPEN-BLOCKING
```

---

# 11. Claim ceiling

Mutual information is distribution- and protocol-relative. Estimating it reliably in high-dimensional real systems is itself difficult. This theorem does not identify the architecture or prove that a learned recurrent state reaches the information-theoretic optimum.
