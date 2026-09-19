# AF1 exact G0 microscope and corrected-boundary note

Authority: issue #833, AF addendum comment `5693269426`.

Parent execution semantics: `research/gmi-833-g0-register-core-v1/g0_register_core_v1.py`, Git blob `6c80e7b1ee0cceedb5dc48eaf28bd3011750d80a`.

## Purpose

AF1 requires an **exact finite `G0` microscope**, not merely a Boolean-function table. `check_g0_micro_v1.py` therefore constructs and executes four programs through the registered `G0-reg-v1` interpreter:

- `C0`: constant 0;
- `C1`: constant 1;
- `ID`: copy the binary input;
- `NOT`: complement the binary input.

On the registered identity task their exact scores are

```text
C0 = 1/2
C1 = 1/2
ID = 1
NOT = 0
```

with the exact G0 raw resource vectors written to `G0_RESULT_V1.json`. This gives the required first-direction microscope: `C0` and `C1` have the same current capability; a development relation that allows `C0 -> ID` but freezes `C1` yields different developmental response.

The development edge itself is deliberately external to the G0 execution semantics: G0 establishes the machine behaviours/resources, while AF/HST supplies the registered development law. This preserves the repository's separation between machine execution and developmental reachability.

## Why the literal converse cannot be earned

The AF text asks for machines with the same current capability but different `Gamma`, **and conversely**. The registered AF definition makes the second conjunct impossible if read as equality of the full response object:

```text
Current(M0,Q,V) = zero-development slice of Gamma.
```

Therefore

```text
Gamma_A = Gamma_B
=> zero_step_slice(Gamma_A) = zero_step_slice(Gamma_B)
=> Current_A = Current_B.
```

So two machines with different current capability cannot have identical full `Gamma` under this definition. This is not an empirical failure; it is a definition-level implication.

A weaker future-envelope statement is valid and useful. Define the diagnostic projection

```text
Gamma+ = capability projection of profiles after >=1 registered development step.
```

The finite AF microscope already shows `ID` and `NOT` have different current identity-task capability (`1` vs `0`) while a common reset-and-enumerate development law gives both the same post-development capability projection

```text
Gamma+ = {0, 1/2, 1}.
```

That does **not** establish equality of full `Gamma` because the zero-step slices and histories remain different.

## Reconciliation rule

The authoritative AF checkbox

`Construct exact finite G0 microscopes where two machines have the same current capability but different Gamma, and conversely.`

must remain unchecked as written. The first direction is now G0-executed GREEN; the literal converse is a logic-gap requiring wording repair. The reconciliation registry therefore moves this row from auto-checkable tasks to `deferred_tasks` rather than laundering the corrected `Gamma+` result into the stronger sentence.

Claim ceiling remains:

`GMI_AF0_AF3_DEVELOPMENTAL_RESPONSE_PROVENANCE_AND_BARRIER_CONTEXT_FORMALIZED_AT_REGISTERED_FINITE_SCOPE`.
