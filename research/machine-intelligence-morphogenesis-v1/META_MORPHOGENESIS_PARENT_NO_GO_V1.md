# Meta-morphogenesis parent no-go v1

Status: **Q5 parent subtraction / scope correction.**

## Claim attacked

A weak Track-B Q5 claim would be:

> The search process that generates machine architectures can itself learn/evolve and thereby find better architectures more efficiently.

This is heavily parent-owned.

## Existing parent territory

At minimum:

- learned optimizers learn update procedures from task distributions;
- AutoML/NAS optimizes architecture/search decisions;
- AutoML-Zero/evolutionary algorithm discovery searches learning algorithms themselves;
- evolved RL algorithms search computational graphs representing update/loss rules;
- MetaBBO/meta-optimization learns or discovers optimization algorithms;
- evolutionary search can directly optimize evolvability/offspring variation;
- modern learned mutation kernels bias architecture evolution using prior high-performing designs;
- PowerPlay/OOPS alters future search bias through accumulated solver/task experience.

Therefore:

```text
SEARCH_GENERATOR_CAN_IMPROVE
```

is not a Track-B novelty claim.

## Formal reduction

Let morphology generator/search be parameterized by `phi`:

\[
\Gamma_\phi(M'\mid E,H).
\]

Let an outer objective evaluate descendant quality/resource cost across ecologies:

\[
J(\phi)=\mathbb E_{E,M'\sim\Gamma_\phi}[U(M',E)-\lambda C(M',E)].
\]

Updating `phi` by gradient, evolution, Bayesian optimization, RL or another outer-loop optimizer is ordinary meta-optimization unless a stronger residual is shown.

## Stronger Q5 requirement

A Track-B-specific positive would need all of:

1. **fresh ecologies:** improvement measured on disjoint future ecology families, not the same NAS/search table;
2. **morphology-level target:** improvement in finding frontier-improving developmental-equivalence classes, not just hyperparameters within one architecture family;
3. **complete cost:** generator training/search/evaluation cost charged;
4. **causal inherited change:** later generator has measurably changed proposal/search geometry before discovering the new morphology;
5. **continued-vs-reset control:** same current ecology information but without inherited generator-development history;
6. **strong parent:** MetaBBO/AutoML/evolutionary learned-mutation/PowerPlay-class parent receives matched rights;
7. **slope:** useful morphology discovery per unit complete search resource improves across genuine generations, not one lucky search.

Candidate metric:

\[
\eta_\Gamma(g)=
\frac{\text{verified frontier gain on fresh ecologies}}
     {\text{complete morphology-generation/search/evaluation cost}}.
\]

A strong result requires a registered positive trend or lower first-useful-morphology burden across matched generations.

## Negative terminals

```text
META_OPTIMIZATION_PARENT_SUFFICIENT
SEARCH_GENERATOR_IMPROVEMENT_DOES_NOT_TRANSFER
GENERATOR_TRAINING_COST_DOMINATES
NO_MULTI_GENERATION_MORPHOGENESIS_GAIN
POWERPLAY_AUTOML_PARENT_SUFFICIENT
CANNOT_CHECK_<reason>
```

Positive scoped terminal:

```text
CROSS_ECOLOGY_META_MORPHOGENESIS_SUPPORTED_AT_SCOPE
```

## Relationship to #149 / RSI

This is structurally similar to governed RSI but the object being improved is specifically the **generator/search over intelligence morphologies**, not merely the current agent code.

#149's external governance rules should therefore be inherited if this lane ever becomes executable:

```text
proposal/search cannot change evaluator/constitution
protected outcomes stay outside the generator
failed/rejected generator changes are retained and charged
rollback is external
```

## Current Q5 conclusion

```text
META_MORPHOGENESIS_CONCEPT_PARENT_OWNED_AT_WEAK_LEVEL
CROSS_ECOLOGY_RECURSIVE_MORPHOGENESIS_UNESTABLISHED
```

This moves the question upward rather than abandoning it.