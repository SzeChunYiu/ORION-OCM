# GMI uncertainty decomposition v1

Parent: #602 Section M  
Closure child: #750

## Scope

This directory closes only the registered **finite latent-model** epistemic/aleatoric variance contract.
It does not claim a universal decomposition of uncertainty, posterior calibration, morphology/capability
calibration, or that real-world randomness is intrinsically irreducible.

For a finite latent space `Theta`, prospectively registered exact weights `pi(theta)`, and exact
conditional outcome kernels `K(y|theta)`, define

```text
m(theta) = E[Y | theta]
v(theta) = Var(Y | theta)
mu       = E_pi[m(theta)]
A        = E_pi[v(theta)]
E_mean   = Var_pi[m(theta)]
T        = Var(Y)
```

The exact theorem proved in `PROOFS_V1.md` is

```text
T = A + E_mean.
```

`A` is the registered aleatoric variance component. `E_mean` is the epistemic variance of the
**predictive mean**. The latter is intentionally narrower than all model uncertainty.

## Strongest parents / subtraction

The mathematics is parent-owned: the law of total variance / conditional-variance decomposition.
The epistemic/aleatoric terminology is standard Bayesian/ML uncertainty taxonomy (including the
Hüllermeier–Waegeman and Kendall–Gal lines named in #750).

The repository contribution is only:

1. a frozen finite exact contract;
2. an exact-rational executable oracle;
3. a full-marginal non-identifiability theorem with a smallest explicit twin;
4. fail-closed handling when latent semantics are absent or malformed;
5. a deterministic normal/optimized replay receipt and CI gate.

No novelty is claimed for the law of total variance itself.

## Frozen semantics

A registered model has the form

```json
{
  "latent_semantics": "registered",
  "latent": [
    {
      "id": "theta0",
      "weight": "1/2",
      "kernel": {"-1": "1/2", "1": "1/2"}
    }
  ]
}
```

All probabilities and outcomes are integers or explicit rational strings `p/q`. JSON floating-point
numbers and decimal strings are rejected. Latent weights and every conditional kernel must be
non-negative and normalize exactly to one.

## Load-bearing non-identifiability twin

The complete predictive marginal

```text
P(Y=-1)=1/2, P(Y=+1)=1/2
```

has at least these two latent explanations:

- one latent state with a fair `±1` kernel: `A=1`, `E_mean=0`;
- two equally weighted latent states, each deterministic at `-1` or `+1`: `A=0`, `E_mean=1`.

The **entire marginal distribution is identical**, not merely its mean/variance. Therefore neither a
variance nor the full predictive marginal identifies the epistemic/aleatoric split without registered
latent semantics.

## Required controls

`UNCERTAINTY_CONTRACT_V1.json` and `check_uncertainty_decomposition_v1.py` freeze and verify:

- pure aleatoric: point-mass latent distribution + noisy kernel;
- pure epistemic-mean: uncertain latent distribution + deterministic kernels;
- mixed case with both components nonzero;
- identical latent means but different higher moments, proving `E_mean=0` does not mean zero model uncertainty;
- the full-marginal non-identifiability twin;
- absent latent semantics -> `CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS`;
- bad weight/kernel normalization, negative mass, duplicate latent IDs, duplicate rational outcomes,
  zero denominators, floats and decimal strings -> fail closed.

## Claim ceiling

Allowed terminal:

```text
EXACT_EPISTEMIC_ALEATORIC_SEPARATION_FOR_REGISTERED_FINITE_LATENT_MODELS
```

Forbidden from this artifact alone:

```text
UNIVERSAL_UNCERTAINTY_DECOMPOSITION
POSTERIOR_CALIBRATED
ALEATORIC_INTRINSICALLY_IRREDUCIBLE_PROVED
CAPABILITY_UNCERTAINTY_CALIBRATED
MORPHOLOGY_UNCERTAINTY_CALIBRATED
COMPLETE_GMI
```
