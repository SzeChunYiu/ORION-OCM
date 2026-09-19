# R4 — state, representation and morphology as contextual quotients

Let T be the registered continuation/test family and r(h,t) the context-relevant response of history h under test t.

Define

h ≡_T h'  iff  for every t in T, r(h,t)=r(h',t).

This is reflexive, symmetric and transitive because equality is.

The response signature sig_T(h)=(r(h,t))_{t∈T} is therefore a sufficient representation for exactly the registered test family.

## Separation lower bound
Suppose a representation z(h) is decoded by d_t(z) and is correct for every registered history/test. If some test t separates h1,h2, then z(h1) != z(h2). Otherwise the same representation value would force the decoder to emit the same response for both histories, contradicting correctness.

Hence the number of required internal distinguishable representation states is bounded below by the number of pairwise future-distinguishable history classes.

## Context dependence
A restricted test family can merge histories that a richer family separates. Therefore there is no unique context-free state quotient in the GMI core.

## Morphology/species
A morphology relative to a declared context/test family is the corresponding quotient class. This eliminates morphology as primitive ontology.

## Parent map
- Myhill-Nerode: recovered when histories are prefixes and tests are all continuations for deterministic language/transducer behavior.
- Bisimulation: generally structural/stepwise and can be finer or differently constrained than pure registered observational equivalence.
- Sufficient statistics/predictive-state representations: parent formalisms for retaining information sufficient for declared predictive distributions/tasks.
- Computational-mechanics causal states: parent predictive-equivalence quotient for stochastic processes under its assumptions.
- Blackwell/Le Cam: parent comparison of statistical experiments/information structures.

R4 imports these results when assumptions match; it does not rename them.

## Remints
Bijective relabeling of presentation symbols that preserves every response r preserves the quotient exactly. Search order, description length and reachability cost need not be invariant under the same remint.

Claim ceiling:
GRAND_GMI_V2_R4_CONTEXTUAL_EQUIVALENCE_STATE_AND_REPRESENTATION_QUOTIENT_AT_REGISTERED_SCOPE
