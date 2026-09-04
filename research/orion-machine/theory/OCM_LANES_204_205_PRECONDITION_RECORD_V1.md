# Lanes #204 and #205 — precondition record

Date: 2026-09-04 · Umbrella: ORION-V2 #194 · Execution master: #197
Depends on the terminals recorded in `OCM_LANE_200_TERMINAL_V1.md`, `OCM_LANE_201_TERMINAL_V1.md`,
`OCM_LANE_202_TERMINAL_V1.md` and `OCM_OPERATIONAL_SEMANTICS_V1.md`.

## 0. Substrate-form restatement (operator directive, #194 comment 5539487737, 2026-09-04)

Under the directive both lanes **dissolve** rather than wait. #204: natural language is one
*encoding* of the instruction channel; the substrate fixes only what warrant an instruction can
carry (a positive certificate), and which encodings the machine comes to use is an emergent-form
question the directive reserves for discovery — so there is no OCM-specific language prediction to
bridge to. #205: a quantum operator would be one more *form* the substrate might discover; no
classical operator with an access model has been frozen, so there is nothing to lift. The
terminals below record the unmet preconditions of the lanes as chartered.

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** Neither lane is started. Each is gated by a
precondition that the theory lanes did not meet, and the terminal each lane offers for that case is
recorded rather than left implicit.

## #204 — bounded language/task bridge

Issue text: *"Blocked by: formal semantics, resource contract, and at least one surviving theorem
candidate."*

| Precondition | State after the theory lanes |
|---|---|
| formal semantics | V1 draft exists (`OCM_OPERATIONAL_SEMANTICS_V1.md`); terminal `PARENT_OBJECT_ADOPTED`, not `SEMANTICS_V1_FROZEN` (freeze requires the independent audit OM-WP3-015, unreturned) |
| resource contract | V0 vector exists as counters in `reference/ocm_reference_semantics.py`; the frontier lane (#202) records `TRADEOFF_FRONTIER_ONLY`, with comparator equivalence `CANNOT_CHECK` (no matched manifest registered) |
| at least one surviving theorem candidate | none: #200 `INTERFACE_HIERARCHY_ONLY` (residual not earned), #201 `PARENT_SUFFICIENT`, #202 `TRADEOFF_FRONTIER_ONLY`, #203 `PARENT_OBJECT_ADOPTED` |

**Terminal recorded: `FORMAL_ONLY`.** The bridge asks which tasks should show nonzero Warrant Lift
and whether traces, memory or certified representations help on a language slice. With Warrant
Lift collapsed to conditional Hartley entropy and every interface gain attributed to a parent, the
only pre-experimental prediction the theory licenses is the parents' own: extra observation refines
the version space (trace learning), and absence of positive support is not a negative (closed-world
assumption). No OCM-specific prediction exists to test, so no arm design, curriculum or small neural
instantiation is authorised. `PARENT_SUFFICIENT` is not chosen because no bridge experiment was run
for a parent to be sufficient *for*; `CANNOT_CHECK` is not chosen because nothing was attempted and
blocked by a missing tool.

Non-consequence: this record says nothing about English, frontier LLMs, parameter efficiency or
post-Transformer architecture, and forbids none of the parents' experiments from being run under
their own names in a separate lane.

Reopens if a theorem candidate survives parent subtraction and the kill-gate in a later lane.

## #205 — conditional quantum-operator integration

Issue text: *"Blocked by: classical OCM semantics/resource contract and an operator with an earned
quantum query/resource separation."* and *"Do not use Warrant Lift or lifecycle uncertainty as a
quantum resource unless a genuine quantum operator and access model are defined."*

| Precondition | State after the theory lanes |
|---|---|
| classical semantics / resource contract | as for #204: draft, not frozen |
| an operator with an earned classical-lower / quantum-upper separation | none registered: every classical object of #200–#203 is parent-owned or an equivalence; no operator was frozen with an identical classical/quantum access model |
| Warrant Lift as a quantum resource | forbidden by the issue; and Warrant Lift is `H_0(L|B)`, a counting quantity with no access model attached |

**Terminal recorded: `NO_ELIGIBLE_OPERATOR`.** Nothing in the classical audit produced an operator
whose query complexity is even stated, let alone separated. OM-WP1-F05's own alternative
`NO_ELIGIBLE_OPERATOR_YET` is the same disposition. `QUERY_ONLY_ADVANTAGE` and
`CONDITIONAL_QUANTUM_OPERATOR_RESIDUAL` are unavailable without an operator; `PARENT_SUFFICIENT`
would name a quantum parent for a classical non-result, which is the vocabulary laundering the
issue forbids.

Non-consequence: no statement about ORION-Q's own programme (`SzeChunYiu/ORION#679`, `#698`,
`#903`, `#908`) is made or altered; those contracts were not consumed here.

Reopens if a classical operator is frozen with an explicit access model and a classical lower bound
whose quantum upper bound is then proved under the same model, with state preparation, oracle
construction, readout, error correction and verification counted.
