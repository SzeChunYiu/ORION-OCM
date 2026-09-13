# Grand GMI Claim Ledger — Continuous Lift Boundary V1

Status date: 2026-09-13. Additive to the Grand-GMI claim ledgers. Authority:
`CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md`.

| ID | Claim | Status | Scope |
|---|---|---|---|
| CL1 | PL-2's derived lower bound holds in any instance, finite or infinite, with no compactness, measurability or effectivity hypothesis; it uses only feasible-set membership and monotonicity. | THEOREM | any nonempty feasible set bounded below |
| CL2 | Without an attainment hypothesis the PL-3b tightness certificate is unavailable, so an abstention cannot be classified as epistemic or physical at all. | THEOREM / NO-GO | non-compact instances |
| CL3 | Every finite observation window yields a minimum strictly above the derived bound, and widening strictly lowers it, so a bound read off finitely many observed realizations is not the derived bound. | THEOREM / NO-GO | infinite registered instances |
| CL4 | PL-2's accounting-soundness contract does not weaken on the lift; establishing that the accounting map undercharges is exactly the work a measured resource contract does. | THEOREM / HYPOTHESIS REQUIREMENT | registered accounting map |
| CL5 | The five-field continuous contract is a decidable gate: each field withholds exactly the results depending on it, an empty contract licenses nothing, and a malformed declaration abstains with a typed error. | THEOREM / INPUT-VALIDATION REQUIREMENT | registered contract declaration |

## Field-to-result gate

| Missing field | Result withheld |
|---|---|
| `measured_resource_contract` | PL-2 derived lower bound |
| `attainment_witness` | PL-3b tightness certificate |
| `effective_description` | computable derived bound |
| `measurable_response_kernels` | well-defined response quotient |
| `admitted_operations` | legal process composition |

## Exact witness aggregate

- registered set `{1 + 1/n : n >= 1}` with declared infimum `1`: all `64` sampled members respect it, across `192` transported comparisons under nonnegative accounting overheads;
- the infimum is attained by no member; the sampled gap is `1/64` and the deeper sample's gap `1/128`, so no member and no finite margin certifies tightness;
- finite window minima for depths `2, 4, 8, 16, 32` are `3/2, 5/4, 9/8, 17/16, 33/32`, each strictly above `1` and strictly improving;
- an accounting map undercharging a cost of `4/3` to `5/6` falls below the bound;
- the complete contract licenses all five results, each single missing field withholds exactly its dependent result, the empty contract licenses none, and `4` malformed declarations are rejected;
- no physical continuum is measured and no experiment on any substrate is performed.

Terminal: `GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_GREEN_AT_FINITE_SCOPE`.
A rational set with no minimum demonstrates the transfer boundary; it is not a
physical continuum. Discharging the contract for a real instance requires
proofs and measurements about that instance.
