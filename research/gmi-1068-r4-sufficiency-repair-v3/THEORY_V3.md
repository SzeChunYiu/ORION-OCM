# R4 residual repair: parameter and predictive sufficiency

Freeze: remote commit `b1c83995c77c6c2bcc89db50872ff8f5d666a75c`,
[`R4_RESIDUAL_FREEZE_V3.md`](../gmi-1068-recursive-audit-v3/R4_RESIDUAL_FREEZE_V3.md).
The historical R4 successor computed its two predictive verdicts as literal
booleans. This additive module replaces that evidence with conditional laws
computed from joint probability tables and checked independently. It does not
rewrite or validate the entire historical R4 receipt. Whole-round semantic
integration remains **OPEN**.

## Definitions and conditioning convention

Let Theta, X and Y have finite declared alphabets. A normalized nonnegative joint
law P(theta,x,y) is supplied, and every declared theta must have positive prior
mass pi(theta). Let S=f(X) be a deterministic statistic. Marginals and
conditionals are obtained by exact sums and division; conditionals are used only
where the conditioning event has positive probability. Unsupported conditioning
events are recorded explicitly, rather than assigned arbitrary conditional laws.

Write P_theta for the conditional family of X given Theta=theta. Classical
parameter sufficiency means that there is a kernel K(x|s), independent of theta,
equal to P_theta(X=x|S=s) whenever P_theta(S=s)>0. In this finite, full-support
setting it is equivalent to

    P(X=x|S=s,Theta=theta) = P(X=x|S=s)

for all positive-probability (s,theta). This is X independent of Theta given S.

Here **predictive sufficiency** has a different declared target:

    P(Y=y|X=x) = P(Y=y|S=f(x))

for every supported x, under the supplied joint mixture law. It is Y independent
of X given S. It is not the assertion of independence after additionally
conditioning on Theta, and it does not claim sufficiency for every possible
future variable, intervention, prior, task or experiment.

**Proposition 1 (classical finite equivalence).** The parameter criterion above
is equivalent to the classical common-kernel definition, and its truth does not
depend on which strictly positive prior represents the same family P_theta.

**Proof.** Conditioning the joint law on Theta=theta cancels pi(theta), yielding
P_theta(X|S). If the equality holds, choose K=P(X|S). Conversely, if the same K
works for every supported theta at s, the mixture P(X|S=s), obtained by averaging
those conditional distributions with P(theta|s), equals K as well. Every theta
has positive prior, so none of the declared family members is silently omitted.
The existence of that common K depends on the family rather than those positive
mixing weights. QED.

This prior invariance is a statement about parameter sufficiency. Predictive
sufficiency under a mixture can depend on the mixing distribution in general.
The three checked priors below establish stability only for the given fixtures.

**Proposition 2 (independent denominator-free check).** For any finite random
variables A,B,S, conditional independence is equivalent to

    P(A=a,B=b,S=s) P(S=s) = P(A=a,S=s) P(B=b,S=s)

for every a,b,s. **Proof.** When P(s)>0, divide by P(s)^2 to obtain the
factorization of the conditional joint law. This factorization is equivalent
to equality of the conditional distributions on every supported conditioning
event. When P(s)=0, nonnegativity makes all involved joint masses zero, so both
sides vanish. QED.

The candidate computes and compares normalized conditional distributions. The
independent oracle enumerates weighted atoms and computes the cross-products in
Proposition 2, once with (A,B)=(Theta,X), once with (A,B)=(Y,X). It does not import
the candidate's marginalization or conditioning functions.

## Two countermodels and four mechanism interventions

Use binary alphabets and, initially, pi(0)=pi(1)=1/2. In all rows S is constant.
“Independent” means X is an independent fair bit. Models are constructed by
enumerating Theta and an independent auxiliary fair coin; the displayed verdicts
are expected mathematical outcomes, never literal results in the analyzer.

| Model | X mechanism | Y mechanism | Parameter sufficient | Predictive sufficient |
|---|---|---|---|---|
| A | Independent of Theta | Y=X | Yes | No |
| B | X=Theta | Y=0 | No | Yes |
| A: change future | Independent of Theta | Y=0 | Yes | Yes |
| A: change observation | X=Theta | Y=X | No | No |
| B: change observation | Independent of Theta | Y=0 | Yes | Yes |
| B: change future | X=Theta | Y=X | No | No |

**Proposition 3 (incomparability).** Neither of the two sufficiency notions
implies the other in the declared finite setting.

**Proof.** In A, P(X|Theta) is fair for both theta values, so a constant statistic
is parameter sufficient. But P(Y=1|X=0)=0 and P(Y=1|X=1)=1, whereas
P(Y=1|S)=1/2: it is not predictive sufficient. In B, P(X|Theta=0) and
P(X|Theta=1) are different point masses, so the constant statistic is not
parameter sufficient. Since Y=0 always, its conditional law is the same with
or without X; the statistic is predictive sufficient. QED.

Each mechanism intervention changes an actual joint law and flips one of the
verdicts while preserving the other. They defeat a checker that memorizes A/B
or copies a parameter-sufficiency verdict into its prediction verdict. Replacing
S by the identity map makes both notions hold in every model: within each
statistic fibre X is known, making both conditional equalities immediate.

The same computations are repeated with pi(1)=1/3 and 2/3, keeping every theta
supported. Consistent permutations of Theta/X/Y/S labels preserve the verdicts.
No claim of full-support joint cells is made: deterministic models necessarily
contain zero cells. A model with both theta values supported but X identically
zero checks that unsupported X=1 conditionals are reported and skipped correctly.
A prior assigning zero mass to a declared theta is rejected at the schema gate,
rather than being treated as a valid test of the whole declared family.

## Exhaustive registered finite evidence

For denominator d in {4,6}, enumerate every nonnegative integer eight-cell count
vector summing to d and with both theta marginals positive. Assign probability
count/d. There are

    C(d+7,7) - 2 C(d+3,3)

such vectors: stars-and-bars gives the first term; the two excluded cases put
all mass into one theta's four cells and are disjoint when d>0. Counts are 260
and 1548. For each, test all four binary maps X->S against the independent oracle,
giving 4*(260+1548)=7232 comparisons. Laws repeated across denominators are
counted as occurrences, not distinct probability distributions. This grid checks
the executable implementation; Propositions 1–3 supply the mathematical scope.

Every receipt includes the joint laws, normalized conditional distributions,
failure witnesses, independent cross-product discrepancies, zero-event records,
enumeration counts and a digest of the exhaustive outcomes. Negative controls
include fixed verdicts, conflation of the two definitions, omitted theta support,
negative/non-normalized/inexact probabilities. No result is inferred from an
expected status string alone.

## Ownership, reproduction and remaining gaps

Conditional independence and classical sufficient statistics are established
probability/statistical concepts. For the general statistical context see
[Bahadur (1954), Sufficiency and Statistical Decision Functions](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-25/issue-3/Sufficiency-and-Statistical-Decision-Functions/10.1214/aoms/1177728715.full).
The finite criteria needed here are proved explicitly above; no unrestricted
measure-theoretic theorem is imported. This is an evidence repair of the GMI
application, not a claim to have discovered these distinctions.

Run `python3 -I -B check_sufficiency_v3.py`, using the full path if necessary.
The default recomputes the result and checks it against `RESULT_V3.json`.
`--write` explicitly regenerates the receipt. Both implementations are loaded
from reviewed sibling paths. Receipt inputs and historical file bytes are hashed;
the receipt does not recursively contain its own hash or its commit hash.

The proofs are not Lean-verified. This module does not repair every R4 semantic
bridge, establish a complete future-test family, solve general conditional-law
estimation from samples, certify minimal learned representations, or close the
R0–R17 programme. Conditional independence is evaluated from a supplied exact
joint law; learning or validating that law in a real environment is separate.
