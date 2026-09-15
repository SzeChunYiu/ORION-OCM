# gmi-833-uncertainty-contract-v1

Bounded #851 / #833-C foundation tranche for typed uncertainty, dependence-safe composition, and global abstention/non-identifiability semantics.

## Scope

- distinguishes feasible sets, confidence sets, predictive laws, latent predictive models, and selective predictions;
- imports the merged finite chain/DAG uncertainty theorems without re-claiming their parent mathematics;
- defines `UNKNOWN`, `IDENTIFIED`, `CANNOT_IDENTIFY`, `CANNOT_CHECK`, and `INCONSISTENT_REGISTERED_ASSUMPTIONS` as distinct semantics;
- preserves arbitrary-dependence union-bound composition and shared-ancestor structure;
- forbids epistemic/aleatoric decomposition from a marginal predictive law without registered latent semantics;
- pins strongest merged parent receipts by Git blob, claim ceiling, and semantic field.

## Reproduce

```bash
python3 -I -B research/gmi-833-uncertainty-contract-v1/test_uncertainty_contract_v1.py -v
python3 -I -O -B research/gmi-833-uncertainty-contract-v1/test_uncertainty_contract_v1.py -v
python3 -I -B research/gmi-833-uncertainty-contract-v1/uncertainty_contract_v1.py
```

Claim ceiling: `GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`.
