# GMI Domain Richness and Discovery Theory v1

Status: **PROSPECTIVE THEORY / DISCOVERY-ESTIMATION PROGRAMME — NOT A CLAIM THAT TOTAL DOMAIN COUNT IS KNOWN**

Status date: 2026-09-12.

Purpose:

> Define what it could mean to estimate how many machine-intelligence domains exist, how much domain mass remains undiscovered, and when a registered domain search is approaching saturation.

This file complements `GMI_DOMAIN_DERIVATION_COMPLETENESS_V1.md` and issue #426.

---

# 1. Absolute domain count is not currently identifiable

Without bounds on description length, precision, operator vocabulary, ecology family and accepted reduction overhead, the space of realizations is open-ended. Therefore the unqualified question

> “How many machine-intelligence domains exist in total?”

has no scientifically usable finite answer at present.

GMI instead defines **registered domain richness** relative to:

\[
\mathfrak R=(\mathcal E,\mathcal J,\mathcal G,L,p,\mathcal B,\mathcal T),
\]

where:

```text
E  ecology/obligation family
J  legal interventions and developmental histories
G  neutral carrier/operator grammar
L  description/search budget
p  precision/representation bound
B  accepted lifecycle burden coordinates
T  accepted reduction-overhead class
```

Let

\[
N_{dom}(\mathfrak R)
\]

be the number of irreducible structural domains reachable or expressible under that registration.

This quantity may be finite even though unrestricted domain space is open-ended.

---

# 2. Observed count is a lower bound

After a discovery campaign, let

```text
D_obs  number of accepted/recurrently observed domains
f_r    number of domains observed in exactly r independent sampling units
```

where a sampling unit is a preregistered independent search encoding × ecology-family × seed block, not one candidate evaluation.

Then always:

\[
D_{obs}\le N_{dom}(\mathfrak R).
\]

Rarely recovered domains contain most information about what remains unseen.

---

# 3. Chao/Good-Turing style lower-bound estimator

For replicated incidence-style discovery campaigns, define

\[
\widehat N_{Chao}
=
D_{obs}
+
\frac{f_1^2}{2f_2}
\]

when `f_2>0`, with the usual bias-corrected fallback when `f_2=0`.

Interpretation:

```text
many singletons + few doubletons -> likely many domains remain undiscovered
few singletons and stable recurrence -> discovery may be approaching saturation
```

This is a **lower-bound / diagnostic estimator**, not proof of total domain completeness. Heterogeneous discoverability can make the true tail much larger.

---

# 4. Good-Turing unseen discovery mass

Let a total of `n` accepted domain-recovery events be observed across independent registered sampling units, and `f_1` be the number of domains seen once.

Use the Good-Turing diagnostic

\[
\hat p_{unseen}\approx \frac{f_1}{n}
\]

as a first estimate of the probability mass assigned to as-yet-unseen domain classes under the current discovery distribution.

This estimates **discovery mass**, not ontological count.

A low unseen mass can coexist with infinitely many extremely rare domains.

---

# 5. Bayesian nonparametric discovery model

Fit a Pitman-Yor style domain-discovery model to recurrence counts:

\[
P(\text{new domain at next draw}\mid n,k)
=
\frac{\theta+\sigma k}{\theta+n},
\]

where:

```text
n  accepted domain-recovery events
k  distinct recovered domains
sigma  tail/discount parameter
θ      concentration parameter
```

Use posterior predictive distributions for:

```text
new domains in next m search units
probability next campaign yields a new domain
expected richness growth under more search
credible intervals on saturation
```

No single BNP prior is authoritative. Report sensitivity to prior family and detection heterogeneity.

---

# 6. Multi-search capture-recapture

Use at least three materially different domain-discovery channels:

```text
carrier/operator grammar synthesis
quality-diversity / novelty search
program/equation synthesis
coevolutionary ecology-machine search
human/literature seeded candidate generation held separate from confirmatory search
```

For each domain `d`, record detection vector

\[
I_d=(I_{d1},\dots,I_{dm}).
\]

Overlap among independent channels estimates detection heterogeneity and unseen richness.

If one domain is found only by one encoding, it is not yet evidence of a stable discovered domain; it is a singleton until recurrence.

---

# 7. Discovery curves

For search budget `b`, define:

\[
K(b)=\text{number of distinct accepted domains discovered by budget }b.
\]

Track:

```text
raw K(b)
new-domain rate dK/db
singleton fraction f1/K
cross-encoding recurrence
estimated unseen mass
estimated lower-bound richness
```

A plateau in `K(b)` alone is insufficient because the search may simply be trapped in a biased grammar.

---

# 8. Domain-search saturation gate

A registered search can claim **empirical saturation at scope** only if all hold:

```text
S1 neutral grammar rediscovers all known calibration domains
S2 >=3 materially different search encodings have been used
S3 ecology families include withheld combinations and resource regimes
S4 new-domain rate remains below frozen epsilon across a large additional search tranche
S5 singleton fraction is small/stable
S6 unseen-mass estimates are below frozen epsilon with uncertainty
S7 Chao/BNP richness estimates no longer materially exceed observed recurrent richness
S8 rejected-candidate audits show bounded triage false-negative rate
S9 grammar expansion audits do not immediately reopen large unseen mass
S10 literature/parent search does not reveal a missing known domain the grammar could not express
```

Terminal:

`DOMAIN_DISCOVERY_EMPIRICALLY_SATURATED_AT_REGISTERED_SCOPE`

This must never be shortened to “all domains discovered.”

---

# 9. Open-endedness diagnostic

If the fitted discovery process exhibits persistent Heaps/Pitman-Yor-like growth

\[
E[K(n)]\propto n^\sigma,\qquad \sigma>0,
\]

with stable recurrence and valid new domains, then the evidence favors an **open/heavy-tailed domain ecology** rather than a small finite catalogue.

This itself is a falsifiable hypothesis.

---

# 10. Domain generator calibration using existing domains

Existing D1-D8 are held-out calibration fossils.

The generator must be tested in leave-one-domain-out fashion:

1. remove one known domain label and all named macros;
2. provide only primitive carrier/operator vocabulary allowed by the registration;
3. expose ecologies predicted to favor the held-out domain;
4. run neutral search;
5. test whether the domain's carrier/operator signature reappears;
6. run bounded reduction back to the held-out reference implementation.

Metrics:

```text
recovery probability
search burden
rank/time to recovery
structural distance from target domain
frontier quality
reduction overhead
false novel-domain rate
```

A generator that cannot rediscover existing domains is not trusted for unseen-domain estimates.

---

# 11. Domain prediction calibration

For each known domain `D_i`, freeze a pre-outcome descriptor

\[
X=(\Psi(O),P,H),
\]

and predict:

```text
frontier occupancy probability
capability ceiling under resource budget
learning/resource elasticity
niche boundaries
negative twins
substrate repricing response
```

Use leave-domain-family-out and held-ecology validation.

A domain theory is not calibrated by reconstructing labels after seeing outcomes.

---

# 12. Search for genuinely weak domains

Neutral domain search must retain candidates that are scientifically distinct even when they are poor performers.

A candidate can be a valid weak domain if it survives structural reduction but exhibits one or more of:

```text
low asymptotic capability ceiling
poor resource elasticity
very high sample/intervention burden
fragile robustness
narrow ecology niche
catastrophic scaling of memory/communication/search
poor transfer
high verification/precision cost
```

Do not discard these as failed architectures. They are evidence about the shape of the domain universe.

---

# 13. Weak-domain preservation protocol

Quality-diversity archives must preserve cells along structural descriptors, not only performance.

At least one archive lane must optimize:

```text
structural novelty subject to minimal admissibility
```

rather than quality alone.

Randomly promote low-quality structurally novel candidates to full-fidelity evaluation to estimate whether triage suppresses weak domains.

---

# 14. Domain richness is ecology-weighted

Define both:

\[
N_{struct}(\mathfrak R)
\]

for irreducible structural domains and

\[
N_{frontier}(\mathfrak R,\mu_E)
\]

for domains that occupy a non-negligible Pareto region under ecology distribution `μ_E`.

A structurally valid domain can be so weak that

\[
Pr_{e\sim\mu_E}[D\in\mathcal D^*(e)]\approx0.
\]

Both counts matter.

---

# 15. Capability-weighted undiscovered mass

For undiscovered domains, raw count is less informative than potential frontier impact.

Define conceptual quantity

\[
U_{cap}
=
E[\Delta HV(\text{next unseen domain})],
\]

where `HV` is protected multiobjective frontier hypervolume.

The search should prioritize experiments with high expected information about both:

```text
P(new domain)
P(frontier-relevant domain | new)
```

while preserving a separate weak-domain discovery lane.

---

# 16. Claim ceiling

Current allowed claim:

> GMI now has a registered statistical framework for estimating unseen-domain discovery mass and lower-bounding domain richness, calibrated by rediscovery of known domains.

Not allowed:

```text
finite total number of machine-intelligence domains is known
all domains can be discovered by any fixed grammar
observed domain saturation proves ontological completeness
rare weak domains can be ignored
```

Desired terminal:

`NO_EVIDENCE_OF_MATERIAL_UNDISCOVERED_DOMAIN_MASS_AT_REGISTERED_SCOPE`.
