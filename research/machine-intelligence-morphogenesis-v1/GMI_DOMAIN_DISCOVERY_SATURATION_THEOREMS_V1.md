# GMI Domain Discovery Saturation Theorems v1

Status: **FORMAL DISCOVERY-SCOPE HARDENING / CONDITIONAL STOPPING LAW**

Status date: 2026-09-12.

Purpose:

> Give the domain-discovery programme a mathematically legitimate registered-scope stopping rule under explicit discoverability assumptions. Absolute ontological completeness remains impossible; material-domain saturation can be bounded when every material domain has a minimum probability of being recovered by an independent registered search unit.

---

# 1. Registered discovery distribution

Fix a domain-discovery constitution:

```text
ecology family
carrier/operator grammar ensemble
search algorithms/encodings
search budgets
parent-reduction criteria
novelty admission rules
```

An **independent search unit** is one preregistered draw/run block from this frozen discovery process.

Suppose there are `K` material irreducible domains in the registered scope with recovery probabilities

\[
p_1,\ldots,p_K,
\qquad
\sum_i p_i\le1,
\]

where leftover probability may correspond to rediscovering already-reduced/non-domain outcomes.

---

# 2. Minimum discoverability assumption

Assume every material domain satisfies

\[
p_i\ge p_{min}>0.
\]

## Theorem DSAT-1 — finite richness bound

Then

\[
\boxed{K\le\left\lfloor\frac1{p_{min}}\right\rfloor.}
\]

### Proof

Because probabilities sum to at most one,

\[
1\ge\sum_i p_i\ge Kp_{min}.
\]

QED.

### Interpretation

A minimum discoverability assumption turns the otherwise open-ended material domain tail into a finite registered class.

---

# 3. Probability of missing a fixed domain

After `n` independent search units, domain `i` is never recovered with probability

\[
(1-p_i)^n
\le
(1-p_{min})^n
\le
\exp(-np_{min}).
\]

---

# 4. Theorem DSAT-2 — all material domains recovered with high probability

By a union bound over `K` domains,

\[
P(\text{some material domain remains unseen})
\le
K e^{-np_{min}}.
\]

Therefore it is sufficient that

\[
\boxed{
n\ge\frac1{p_{min}}\ln\frac{K}{\delta}}
\]

to recover every material domain with probability at least `1-delta`.

Using DSAT-1 to eliminate unknown `K`, a conservative sufficient condition is

\[
\boxed{
n\ge
\frac1{p_{min}}
\left[
\ln\frac1{p_{min}}
+
\ln\frac1\delta
\right]}
\]

(up to integer rounding).

---

# 5. Consecutive no-new-domain runs are not enough without p_min

The prior unseen-domain impossibility theorem showed that arbitrarily many domains can hide in arbitrarily small probability mass.

DSAT-2 therefore does **not** justify a stopping rule from “we ran search many times and saw nothing new” unless a minimum discoverability/materiality threshold has been registered or otherwise bounded.

### GMI discipline

Every saturation claim must state:

```text
p_min or equivalent materiality/discoverability assumption
independence definition for search units
number of search units n
confidence delta
grammar/search scope
parent reduction/admission scope
```

---

# 6. Material-domain threshold

Often domains with vanishingly tiny discovery probability or negligible capability/resource impact are not scientifically material to the registered programme.

Define a material domain as one satisfying both:

```text
registered novelty/reduction criterion
registered minimum ecological/capability mass/value
```

The discoverability lower bound may then be justified only for this material subset.

The resulting claim is:

> all domains above the declared materiality/discoverability threshold are likely recovered at the registered scope.

It is not:

> no other mathematical domain exists.

---

# 7. Independent search encodings

If multiple search encodings `e=1,...,m` have different domain recovery probabilities `p_{i,e}`, one can define a mixed independent search-unit schedule.

For a fixed schedule with `n_e` runs of encoding `e`, probability of missing domain `i` is

\[
\prod_e(1-p_{i,e})^{n_e}
\le
\exp\left(-\sum_en_ep_{i,e}\right).
\]

## Theorem DSAT-3 — heterogeneous encoding coverage

If every material domain satisfies cumulative discovery exposure

\[
\sum_en_ep_{i,e}\ge\Lambda,
\]

then probability any of `K` domains is missed is at most

\[
K e^{-\Lambda}.
\]

Thus it is sufficient that

\[
\Lambda\ge\ln(K/\delta).
\]

### Interpretation

A domain can be hard for one grammar yet easy for another. Saturation should be based on cumulative cross-encoding exposure, not repeated copies of one biased search.

---

# 8. Capture-recapture / singleton diagnostics remain useful

DSAT-2 is assumption-driven. Chao/Good-Turing/Pitman-Yor diagnostics in `GMI_DOMAIN_RICHNESS_DISCOVERY_THEORY_V1.md` remain useful empirical checks on whether the assumed tail looks plausible.

A strong saturation claim should require consistency between:

```text
minimum-discoverability bound
observed singleton/doubleton recurrence
unseen-mass estimate
capture-recapture across encodings
grammar-expansion sensitivity
```

If the empirical tail contradicts the assumed `p_min`, the bound is invalidated.

---

# 9. Grammar expansion as a saturation hostile

Even if one frozen grammar/search process satisfies DSAT-2, adding new primitive carrier/operator descriptions can expose domains with zero probability under the predecessor grammar.

Therefore recursive closure requires a **grammar-expansion hostile**:

1. freeze predecessor saturation claim;
2. enlarge/remint grammar without target-domain macros;
3. rerun known-domain rediscovery and open search;
4. measure whether genuinely irreducible domains appear;
5. if they do, predecessor saturation was only grammar-relative and the successor scope expands.

---

# 10. Practical stopping ladder

A registered domain campaign may use:

```text
S0 observed count only
S1 recurrence/unseen-mass diagnostics
S2 multiple independent search encodings
S3 explicit materiality + p_min discoverability model
S4 DSAT-2/DSAT-3 sample bound satisfied
S5 grammar-expansion hostile yields no material irreducible domain
S6 fresh independent replication of saturation conclusion
```

Only S4+ supports a quantitative registered-scope saturation statement.

---

# 11. Gap update

Domain-richness theory now has:

```text
observed count lower bound                              CLOSED
Good-Turing/Chao/BNP diagnostic framework              REGISTERED
unseen-domain distribution-free upper bound            IMPOSSIBLE
minimum-discoverability richness bound                 CLOSED
minimum-discoverability all-domain sample bound        CLOSED
heterogeneous-encoding exposure bound                  CLOSED
grammar-expansion hostile                              REGISTERED

empirical p_min justification                           OPEN-BLOCKING
broad independent discovery campaigns                   OPEN-BLOCKING
materiality/capability weighting                        OPEN
```

---

# 12. Claim ceiling

These theorems do not prove the real domain universe finite. They give a valid conditional stopping rule for domains above a frozen materiality/discoverability threshold under a frozen discovery process. Any claim must retain those conditions explicitly.
