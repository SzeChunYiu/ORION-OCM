# Claim disposition — #748 / #602 Section M

## Scientific question

Can uncertainty attached to one developmental version be transported to a changed version without silently inheriting old samples or assuming the update is known more precisely than registered?

## Result

At the registered finite/set-valued scope, yes, under an explicit transition relation. If source set `C_0` covers `theta_0` with failure probability at most `alpha`, and registered relation failures have budgets `beta_t`, then recursive relational-image propagation gives simultaneous finite-chain coverage at least

`1 - alpha - sum_t beta_t`,

with no independence assumption. Exact relations preserve the source failure budget. A missing relation maps to the full target domain and therefore forces `CANNOT_IDENTIFY_NO_RELATION` except for queries constant on that domain.

## Load-bearing assumptions

- source confidence coverage is valid at its own version;
- developmental relation(s) are preregistered before source activation;
- each relation contains the true transition except on events covered by the registered `beta_t` budgets;
- the target domain is correctly registered;
- raw source evidence is not treated as target-version evidence.

## Nearest counterexamples

- copy the source set across an unrestricted change from truth `0` to truth `1`: source coverage is one, copied target coverage is zero;
- use a misspecified relation omitting the true target: relational-image coverage can fail;
- multiply marginal success probabilities: the 200-atom certificate has joint good `187/200` but independent-product value `374319/400000`, so independence is false even though the union bound is exact.

## Evidence classes

- P1: DT-1/DT-3/DT-4/DT-5/DT-6 deterministic/set-theoretic results;
- P3: DT-2 probability guarantee from source/relation failure premises via union bound;
- P2: exact rational/finitary controls, hostile tests, five-kind A3 chain, affine corner enumeration, nonlinear relation, and dependence certificate;
- no P4 developmental empirical claim.

## Strongest parents

Set-valued analysis, interval analysis, reachability-set propagation, and the union bound own the underlying mathematics. ARC-6/#655 owns source statistical coverage; #657 owns replay-resistant version noninheritance; #628 owns developmental change labels.

## Claim ceiling

`SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE`

Not earned here: G7 developmental prediction, real transition calibration, capability-prediction calibration, morphology-phase calibration, physical freshness, or complete GMI.

## #602 consequence once this hardening is merged and CI-green

Check only:

- `Propagate uncertainty through developmental updates.`

Do not infer closure of the neighboring Section-M rows.
