# AE12 named results

Every result is stated at the registered finite scope of `FREEZE_V1.md` and uses
only the constants of `PROSPECTIVE_REGISTER_V1.json`. All quantities are exact
rationals in bits; no float appears in any claim. Route A is
`ae12_fep_audit_v1.py`, route B is `independent_fep_oracle_v1.py`, and the two
agree on every value reported below.

Throughout, a *registered dyadic agent world* has every probability equal to `0`
or to an integer power of `1/2`. That restriction is the whole reason the
entropies, divergences and free energies here are exact rationals rather than
transcendental numbers. Divergences use the standard convention that
`KL(q||p) = +infinity` when `q` charges a `p`-null atom; the receipt carries the
string `INF` for that value.

---

## AE12-1 — on the registered worlds, free-energy minimisation *is* exact Bayesian inference

*Scope.* The registered dyadic worlds `W_SPLIT`, `W_TRI`, `W_CORR`, the full
dyadic variational family, a correctly specified generative model.
*Quantifiers.* For every registered world and every observation of positive
evidence.

For every such pair, the minimiser of `F(q, o) = KL(q||P0) - E_q[log2 L(o|s)]`
over the registered family equals the exact Bayes posterior
`P0(s) L(o|s) / P(o)`, and the minimum equals the surprisal `-log2 P(o)`
exactly. On `W_SPLIT` the four observations each have evidence `1/4`, so the
minimum free energy is exactly `2` bits at each of them, attained at the
posteriors `(1, 0)`, `(1/2, 1/2)`, `(1/2, 1/2)` and `(0, 1)`. The registered
families have sizes `3`, `9` and `35`.

This is a restatement of the parent identity
`F(q, o) = -log2 P(o) + KL(q || posterior)`, not a new theorem. Its role here is
to fix the scope at which active inference **owns** perception, so that the
following results can be read as boundary-mapping rather than as competition.

**Assumptions.** Finite registered dyadic world; variational family containing
the posterior; generative model equal to the true model; positive evidence.
**Dependencies.** Exact dyadic logarithm; the registered family enumeration.
**Falsifiers.** A registered world and observation at which the minimiser differs
from the exact posterior, or at which the minimum differs from `-log2 P(o)`.
**Strongest parents.** Variational inference and the evidence lower bound
(Jordan, Ghahramani, Jaakkola and Saul 1999, doi:10.1023/A:1007665907178; Blei,
Kucukelbir and McAuliffe 2017, doi:10.1080/01621459.2017.1285773); active
inference as a process theory (Friston, FitzGerald, Rigoli, Schwartenbeck and
Pezzulo 2017, doi:10.1162/NECO_a_00912). **Nothing here is claimed novel.**

---

## AE12-2 — the unrestricted-family assumption is necessary, and its price is exactly one bit

*Scope.* `W_CORR`, whose `o0`-posterior `(1/2, 0, 0, 1/2)` is perfectly
correlated across the registered factorization.
*Quantifiers.* For the whole registered mean-field subfamily.

The posterior is not a product distribution. Over the `9` product distributions
in the registered mean-field subfamily the minimum free energy is exactly `2`
bits, while over the `35`-member full family it is exactly `1` bit. The
mean-field restriction therefore costs exactly `1` bit and returns a minimiser
that is not the posterior. Restricting the family breaks the AE12-1 equality.

**Assumptions.** The registered factorization; the dyadic family with minimum
atom `1/16`. **Dependencies.** AE12-1 for the unrestricted value.
**Falsifiers.** A product distribution in the registered subfamily attaining `1`
bit, or a demonstration that the posterior factorizes.
**Strongest parents.** Mean-field variational inference and its known bias
(Jordan et al. 1999, doi:10.1023/A:1007665907178); the technical critique of
unconditional free-energy equivalences (Biehl, Pollock and Kanai 2021,
doi:10.3390/e23030293).

---

## AE12-3 — the correct-specification assumption is necessary

*Scope.* `W_TRI_MIS`: the true likelihood and a model likelihood that exchanges
two state rows. *Quantifiers.* At the registered observation `o0`.

Free-energy minimisation returns the posterior *of the model held*, which is
`(1/2, 0, 1/2)`, while the true posterior is `(1/2, 1/2, 0)`. The two differ.
The AE12-1 equality is therefore an equality with the model's posterior and not
with the truth; reading it as "free-energy minimisation performs correct
inference" requires the generative model to be correct, which is an assumption
about the world and not a property of the functional.

**Assumptions.** The registered prior and the two registered likelihood tables.
**Dependencies.** AE12-1. **Falsifiers.** An observation at which the two
posteriors coincide while the likelihoods differ, or a minimiser equal to the
true posterior under the model held. **Forbidden extrapolation.** This says
nothing about how large the error is in unregistered worlds.
**Strongest parents.** Model misspecification in Bayesian inference; Biehl,
Pollock and Kanai 2021, doi:10.3390/e23030293.

---

## AE12-4 — the ambiguity term is preference-independent, so no preference prior reproduces an arbitrary utility order

*Scope.* `W_AMB`, whose two actions induce **identical** predicted outcome
distributions `(1/2, 1/2)`. *Quantifiers.* For every preference distribution on
the outcome set — not merely for the registered dyadic family.

Expected free energy decomposes as `G(a) = KL(Pa(o) || C) + E_{s~Pa}[H(L(.|s))]`.
When two actions induce the same `Pa(o)`, the risk terms are equal for **any**
`C` whatsoever and cancel in the difference, so `G(a0) - G(a1)` equals the
ambiguity difference, which is exactly `1` bit, independently of `C`. The
expected-free-energy order on `{a0, a1}` is therefore pinned.

The expected-utility order is not pinned: among the six permutations of the
registered utility values over the registered states, `2` strictly prefer `a0`
and `4` fail to prefer `a1` strictly. Those orders cannot be reproduced by any
preference prior. The registered utility itself happens to make the two actions
exactly indifferent, with difference `0`; the strict contradiction is carried by
the permutations `(1, 0, 1/2)` and `(1, 1/2, 0)` of the same value multiset, so
no constant outside the register is used.

The exhaustive census over the whole `27`-element space of registered-shape
likelihood tables finds this structure in exactly `2` of them, an exact rate of
`2/27`; the sampled null fires on `22` of `200` draws, rate `11/100`; and the
detector raises no alarm on the clean registered worlds `W_SPLIT`, `W_TRI` and
`W_AGREE1`.

**Assumptions.** Horizon `1`; the registered decomposition of expected free
energy into risk and ambiguity; identical predicted outcome distributions.
**Dependencies.** The exact dyadic entropy; the registered action state
distributions and utility values. **Falsifiers.** A preference distribution
making the gap other than `1` bit; a pair of actions with identical predicted
outcomes whose risk terms do not cancel; a permutation census contradicting the
counts above. **Forbidden extrapolation.** This does not show that active
inference and expected utility disagree in general, only that the ambiguity term
cannot be absorbed into a preference prior at this scope.
**Strongest parents.** Expected free energy and its risk/ambiguity decomposition
(Friston et al. 2017, doi:10.1162/NECO_a_00912; Parr, Pezzulo and Friston 2022,
doi:10.7551/mitpress/12441.001.0001); control as inference (Todorov 2009,
doi:10.1073/pnas.0710743106; Levine 2018, arXiv:1805.00909).

---

## AE12-5 — the criticism table is evaluated, not cited

*Scope.* Four registered criticisms, each paired with a registered finite
predicate. *Quantifiers.* Each predicate is evaluated exactly on its registered
object.

`MARKOV_BLANKET_EXISTS` is decided by an exhaustive search over every partition
of the variables into non-empty internal, blanket and external sets. It holds on
`SYS_MB_OK`, with `4` admissible partitions, and fails on `SYS_MB_FAIL`, where
the parity constraint leaves `0`. Existence of the partition is therefore a
property of the joint distribution and not something a system supplies by being
a system. `FEP_EQUALS_BAYES_UNDER_RESTRICTED_FAMILY` is false by AE12-2 and
`EFE_RECOVERS_UTILITY_ORDERING` is false by AE12-4.

**Assumptions.** The registered three-variable supports; uniform mass on each
support. **Dependencies.** AE12-2, AE12-4. **Falsifiers.** A partition of
`SYS_MB_FAIL` satisfying the conditional independence, or a failure of the
independence on one of the four partitions of `SYS_MB_OK`.
**Strongest parents.** Aguilera, Millidge, Tschantz and Buckley 2022,
doi:10.1016/j.plrev.2021.11.001; Bruineberg, Dolega, Dewhurst and Baltieri 2022,
doi:10.1017/S0140525X21002351; Biehl, Pollock and Kanai 2021,
doi:10.3390/e23030293. The criticisms are theirs; the residual here is only that
each is attached to a predicate a machine evaluates.

---

## AE12-6 — three control principles are discriminated on one registered world, and agree on another

*Scope.* `W_DISC1` and `W_AGREE1`. *Quantifiers.* Over all `45` weight triples
of the registered grid.

On `W_DISC1` the expected free energies are `(1, 0, 1)` bits, so expected free
energy chooses `a1`; cardinality-`1` rate-distortion control chooses `a0`; and
the CPC family chooses `a0` or `a1` depending on the weights, never both at
once, so **no** weight in the grid reproduces the choices of both comparators.
Action `a2` is never chosen, and the receipt states exactly why: its term vector
is dominated by `a1`'s — equal predictive loss `1/2`, equal control regret `1/2`
and strictly larger cost `2` against `1` — so no weighting can select it.

On `W_AGREE1` the expected free energies are `(1, 3/2, 3)` bits and `b0`
minimises cost, predictive loss, control regret and expected free energy
simultaneously; all three principles choose `b0`. The contrast shows the
discrimination on `W_DISC1` is a property of that world and not of the
comparison procedure.

**Assumptions.** Horizon `1`; codebook cardinality `1`; the registered costs,
utilities and preference distributions; the frozen lexicographic tie-break.
**Dependencies.** AE12-4 for the ambiguity term. **Falsifiers.** A weight in the
grid at which the CPC choice coincides with both comparators on `W_DISC1`; a
disagreement on `W_AGREE1`; a term-vector computation contradicting the reported
domination. **Forbidden extrapolation.** Nothing here ranks the three
principles; it locates one world where they differ and one where they do not.
**Strongest parents.** Rate-distortion theory (Shannon 1959; Berger 1971);
rational inattention (Sims 2003, doi:10.1016/S0304-3932(03)00029-1); expected
free energy (Friston et al. 2017, doi:10.1162/NECO_a_00912).

---

## AE12-7 — the prospective comparison, including its two refutations

*Scope.* The eight predictions of `PROSPECTIVE_REGISTER_V1.json`, committed
before any executor blob of this package existed. *Quantifiers.* Every
prediction is reported.

Six are confirmed. Two are refuted and are reported as refuted, each with its
exact values, a single-stage attribution and the statement that was actually
earned. `AE12-P4` predicted an expected-utility difference of `1/2` on `W_AMB`;
the registered utility in fact makes the two actions exactly indifferent, so the
difference is `0`. The attribution is to the registered utility vector, not to
the audit, and the earned statement is strictly stronger than the registered one,
being quantified over every preference distribution rather than over the
registered dyadic family. `AE12-P5` predicted that the CPC family would select
all three actions of `W_DISC1`; it selects two, because `a2` is term-vector
dominated, and the discrimination the row asks for survives intact.

Neither the freeze nor the register was edited. A pre-registration that can only
ever be confirmed is not a pre-registration.

**Assumptions.** The register's self-digest verifies, and the executor refuses to
emit on mismatch. **Dependencies.** AE12-1 through AE12-6.
**Falsifiers.** A prediction absent from the receipt; a refutation without exact
values or without an attribution; a receipt emitted under a digest mismatch.
**Strongest parents.** Pre-registration practice in the experimental sciences;
no technical parent is claimed.

---

## AE12-8 — parent sufficiency at the perception scope

*Scope.* Perception as exact Bayesian inference on the registered dyadic worlds,
with the full dyadic family and a correctly specified model.
*Quantifiers.* Every registered world and observation.

At that scope the parent owns the result outright: the equality of AE12-1 is the
parent's identity. The receipt emits the terminal `PARENT_SUFFICIENT` with the
owning parent named, and records `novelty_claimed: false`. The boundary of the
sufficiency is exactly the three assumptions AE12-2, AE12-3 and AE12-4 show to be
necessary. Marking sufficiency is a success terminal, not a defeat, and the
manifest carries `GMI_NOVEL_OVER_ACTIVE_INFERENCE` as a forbidden promotion.

**Assumptions.** AE12-1's three assumptions. **Dependencies.** AE12-1, AE12-2,
AE12-3, AE12-4. **Falsifiers.** A registered scope at which the parent identity
fails while the package still claims sufficiency, or a novelty claim anywhere in
the package's artifacts. **Strongest parents.** Jordan et al. 1999,
doi:10.1023/A:1007665907178; Friston et al. 2017, doi:10.1162/NECO_a_00912.
