# Grand GMI Continuous Lift Boundary Theorem V1

Status: **THEOREM / TRANSFER BOUNDARY + DECIDABLE CONTRACT GATE + EXACT WITNESSES**
Date: 2026-09-13

Authority for the derivation layer lifted here:
`MORPHOLOGY_PHASE_LAW_DERIVATION_V1.md`. Retained predecessors:
`MEASURABLE_CONTINUOUS_GMI_THEOREM_V1.md`,
`CONTINUOUS_REALIZATION_BRIDGE_THEOREM_V1.md`,
`APPROXIMATE_SEMANTIC_GEOMETRY_THEOREM_V1.md`.

## 1. Gap addressed

`RECURSIVE_GAP_AUDIT_20260913.md` records the continuous/quantum realization
obligation as requiring "the stated compactness, measurability, effective
descriptions, admitted operations and measured resource contract for the
actual instance", and warns that "exact finite simulations are not experiments
on arbitrary substrates". Both statements are correct and neither is
actionable: they list properties without saying which conclusion each one buys.

The new derivation layer makes that question sharp, because PL-1 to PL-5 were
stated over a finite registered allocation domain. This theorem determines
which of them survive the lift to an infinite instance, and gates the rest
behind a decidable contract predicate that abstains by field.

The result is asymmetric and useful: the lower-bound half transfers with no
regularity at all, while every interpretive result needs a specific contract
field.

## 2. CL-1 — the derived lower bound lifts without regularity

> **CL-1.** PL-2 holds in any instance, finite or infinite, with no
> compactness, measurability or effectivity hypothesis.

### Proof

Inspect PL-2's proof. It uses exactly two facts: that the admitted machine's
allocation lies in the relaxed feasible set, and that the accounting map and
scalar functional are nondecreasing. The bound itself is an infimum, which
exists in the extended reals for any nonempty set bounded below. None of those
steps mentions the cardinality or topology of the domain. QED.

The witness registers the set `{1 + 1/n : n >= 1}` with declared infimum `1`,
and checks all 64 sampled members against it, plus 192 transported
comparisons under nonnegative accounting overheads.

So a robust family **exclusion** obtained from derived bounds is not a
finite-scope artifact. This is the one part of the phase law that needs no
continuous contract.

## 3. CL-2 — attainment, hence the tightness certificate, needs compactness

> **CL-2.** Without an attainment hypothesis the PL-3b tightness certificate
> is unavailable, so an abstention cannot be classified as epistemic or
> physical at all.

### Proof

PL-3b requires `L_F = U_F`, and `U_F` is the cost of a construction. In the
registered set the infimum `1` is attained by no member, so no construction
can certify tightness. Nor does a positive slack help: the sampled gap is
`1/64` and the deeper sample's gap is `1/128`, strictly smaller, and the gaps
shrink without limit. So no member and no finite margin certifies the bound.
QED.

This is a structural unavailability, not missing data. PL-3's separation of
epistemic from physical abstention — the result that makes a phase-diagram
boundary region interpretable — simply does not apply to a non-compact
instance. Lower semicontinuity plus compactness, or an explicit attainment
witness, is therefore a hypothesis with content and not a convenience.

## 4. CL-3 — no finite observation window determines the bound

> **CL-3.** Every finite window of observed realizations yields a minimum
> strictly above the derived bound, and widening the window strictly lowers it.

### Proof

For the registered set, the window `n <= N` has minimum `1 + 1/N > 1`, and the
window `n <= 2N` has minimum `1 + 1/(2N) < 1 + 1/N`. The witness records
`3/2, 5/4, 9/8, 17/16, 33/32` for windows `2, 4, 8, 16, 32`. QED.

Consequently a bound read off finitely many observed or benchmarked
realizations is not the derived bound, and cannot be substituted for it. An
effective description of the instance — not a sample of it — is what makes the
derived bound computable. This is the continuous analogue of DU-4: a budgeted
or sampled answer does not license the limit.

## 5. CL-4 — transport still needs the measured resource contract

PL-2's accounting-soundness contract does not weaken on the lift. The witness
takes a member of cost `4/3` above the bound `1`, and an accounting map that
undercharges it to `5/6`, which is below the bound. Establishing that the
accounting map undercharges is exactly what a measured resource contract is
for; without it, CL-1 has an undischarged hypothesis and proves nothing about
the instance.

## 6. CL-5 — the contract is a decidable gate, field by field

Register the contract as five Boolean fields: `attainment_witness`,
`measurable_response_kernels`, `effective_description`, `admitted_operations`,
`measured_resource_contract`. Each licenses exactly one result:

| Missing field | Result withheld |
|---|---|
| `measured_resource_contract` | PL-2 derived lower bound |
| `attainment_witness` | PL-3b tightness certificate |
| `effective_description` | computable derived bound |
| `measurable_response_kernels` | well-defined response quotient |
| `admitted_operations` | legal process composition |

> **CL-5.** The gate is decidable, each field withholds exactly the results
> that depend on it, an empty contract licenses nothing, and a malformed
> declaration abstains with a typed error rather than defaulting to available.

### Proof

By enumeration over the registered fields, checked by the accompanying
checker: the complete contract licenses all five results; dropping each single
field withholds exactly the expected set; the empty contract licenses none;
and four malformed declarations — empty, partial, carrying an unregistered
field, and carrying a non-Boolean value — are each rejected. QED.

This follows the abstention convention of
`CERTIFICATE_INPUT_CORRECTION_20260913.md`: an absent contract field is not a
permissive default.

## 7. What this closes and what it does not

Closed: the continuous obligation is no longer an undifferentiated list. It is
now known which conclusion each field buys, the lower-bound half of the
derivation layer is proved to need none of them, and the remaining results are
gated by a decidable predicate that abstains by field.

Not closed, and not closable this way:

- **no experiment on any substrate has occurred.** The witnesses are rational
  sets standing in for non-compact instances. A rational set with no minimum
  demonstrates the transfer boundary; it is not a physical continuum;
- discharging the contract for a real instance requires actual compactness,
  measurability, effectivity and measurement proofs about that instance, which
  no amount of theory supplies;
- quantum external I/O retains its own separate boundary in
  `QUANTUM_CLASSICAL_CUT_BOUNDARY_AUDIT_V1.md`;
- the empirical obligations in the recursive audit are unchanged.

Terminal: `GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_GREEN_AT_FINITE_SCOPE`.

## 8. Parent mathematics and contribution boundary

The parent facts are elementary: existence of an infimum for a nonempty set
bounded below, non-attainment on a set that is not closed, monotone transport,
and the standard role of compactness and lower semicontinuity in attainment.
No novelty is claimed for them. The contribution is the determination of which
registered Grand-GMI results transfer to an instance lacking those properties,
the field-by-field contract gate, and the exact rational witnesses.
