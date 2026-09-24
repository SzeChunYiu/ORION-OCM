# AG5X-1 … AG5X-6 — the `G0` extension lowering ledger

All six results are stated at the registered finite scope fixed in `FREEZE_V1.md` and pinned
in `MANIFEST_V1.json`. Every number is reproduced by `RESULT_V1.json` (route A),
`ORACLE_RESULT_V1.json` (route B) and `TEST_RESULT_V1.json`. Nothing here is asserted about
any scope larger than the one enumerated.

---

## AG5X-1 — Every registered extension operator lowers exactly

**Statement.** For each of the sixteen operators registered by the four merged extension
packages, there is a composition of AJ5 lower roles over a natural-number register store that
reproduces the parent operator on every input of the registered universe, and reproduces the
parent's own declared resource vector on every such input.

**Quantifiers.** For all 1,296 one-step update pairs; all 46,656 kernel-composition pairs;
all 1,296 kernel transports and 36 distribution transports; all 27 deterministic maps and the
identity; all 648 graph-operator applications and their 1,296 site-relabeling cases; all 324
send, 648 receive, 324 apply-received, 6 external-call, 486 apply-external and 648 two-message
queue cases; all 27 propose/verify/adopt sweeps. 54,366 registered checks in total.

**Result.** `total_lowering_mismatches = 0`, `total_resource_mismatches = 0`.

**Assumptions.** Three-element state sets; the six registered weight rows; three sites; three
agents; the two registered tools; the three-element behavior vectors of the self-change
package. Exact integer arithmetic throughout — no floating-point value enters any quantity.
Weights are normalized pairs of naturals; no rational, matrix, queue, graph or receipt object
is admitted as a role.

**Falsifier.** One registered case on which the lowered operator disagrees with its parent
voids that operator's ledger entry. The executor publishes `RED` and names the gate.

**Strongest parents.** Register-machine instruction decomposition (Minsky); structural
operational semantics (Plotkin); the field-of-fractions construction; row-stochastic matrix
algebra; FIFO channel semantics; verifier-gated update. None of this is claimed novel.

**Forbidden extrapolation.** `G0_EXTENSIONS_ARE_THE_OPERATIONAL_BOTTOM`,
`UNIQUE_LOWEST_EXTENSION_BASIS`, `ALL_G0_EXTENSIONS_ENUMERATED`. Four registered families were
lowered; the set of conceivable extensions was not enumerated.

**Dependencies.** The AJ5 role basis and the auxiliary roles frozen in `FREEZE_V1.md` section
2, over the universes fixed in section 4; the operator semantics, registered universes and
declared resource vectors of the four merged extension packages
`gmi-833-g0-stochastic-update-v1`, `gmi-833-g0-local-graph-ops-v1`,
`gmi-833-g0-interaction-channels-v1` and `gmi-833-g0-governed-self-change-v1`, each pinned by
blob in `MANIFEST_V1.json` and compared against as authoritative. The mismatch counts are
computed by route A (`ag5_extension_lowering_v1.py`) and recomputed family by family by route
B (`independent_oracle_v1.py`), which imports neither route A nor any parent module.

---

## AG5X-2 — The twenty-one row status ledger, and no generator among them

**Statement.** Relative to the AJ5 role basis, none of the five core `G0` instructions and
none of the sixteen registered extension operators is a generator at this scope.

**Result.** `generator_count = 0` over `ledger_size = 21`:
`DERIVED_OPERATION` 7 · `MACRO` 12 · `SEMANTIC_CONVENIENCE` 1 ·
`RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE` 1. Four entries carry the
`EXTERNALLY_REGISTERED` qualifier: `CALL`, `VERIFY`, `ADOPT`, `APPLY_EXTERNAL`.

**How each status is assigned.** By measurement, never by hand.
`MACRO` iff the lowering exhibits exactly one role trace over the whole registered universe.
`RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE` iff the operator's result depends on a registered
structural parameter beyond its value arguments **and** its lowering cost varies with that
parameter. `DERIVED_OPERATION` otherwise. The five core statuses are read from AJ5's pinned
`primitive_status` through the crosswalk `DERIVED -> DERIVED_OPERATION`,
`PRESENTATION_ONLY -> SEMANTIC_CONVENIENCE`, which is published in the receipt and may not be
rewritten later.

**Assumptions.** "Generator" is relative to the declared role basis. A role basis is not
unique and this result does not argue that it is.

**Falsifier.** An operator for which no lowering into the declared roles exists is a
generator, and the count is wrong.

**Forbidden extrapolation.** That the AJ5 roles are themselves irreducible. They are the
declared floor of this tranche, not a proven bottom. `UNIQUE_LOWEST_EXTENSION_BASIS` stays
forbidden.

**Dependencies.** AG5X-1, whose exact lowering of all sixteen extension operators is what
rules out `GENERATOR`; the five-status vocabulary and the `EXTERNALLY_REGISTERED` qualifier
frozen in `FREEZE_V1.md` section 1; AJ5's pinned `primitive_status` for `READ`, `EMIT`, `INC`,
`DECJZ` and `HALT` (`gmi-833-aj5-g0-lowering-v1`, blob pinned in `MANIFEST_V1.json`), read
through the published crosswalk; AG5X-3 for the qualifier on `ADOPT` and AG5X-5 for the single
resource-priced entry. The ledger itself is the `ledger` block of `RESULT_V1.json`.

**Strongest parents.** `gmi-833-aj5-g0-lowering-v1`, which established the same status reading
for the five core instructions, including that a named opcode can be a macro; Minsky's
register-machine instruction decomposition (1967) and the classical theory of row-stochastic
matrices, which make `UPDATE`, `COMPOSE`, `IDENTITY_KERNEL`, `DETERMINISTIC_KERNEL` and
`TRANSPORT` named cases rather than generators (`PARENT_LEDGER.md`). Only the adjudication at
this scope is claimed.

---

## AG5X-3 — Governed self-change needs an externally registered admission relation

**Statement.** `ADOPT` is not a function of the machine-internal triple
`(active behavior, active version, pending candidate)`. The remaining dependence is on an
externally registered receipt, exactly as the AG5 row words it.

**Quantifiers.** All 27 registered candidates. Each controlled pair holds the internal triple
and the proposal fixed and varies only the receipt, and only in its `authority_id` and
`signature` fields — a control the executor checks
(`receipt_field_control_violations = 0`).

**Result.** `terminal_witness_pairs = 27 / 27`; `state_change_witness_pairs = 9 / 27`.
Dropping the admission guard from the lowering adopts proposals the parent refuses
(hostile `selfchange_drop_admit`, detected, control clean on all 27).

**Assumptions.** The receipt is registered data produced by a named authority; the fixture
policy `candidate[0] == 0` is a semantic fixture, not a safety rule, and the HMAC-style
binding is not a cryptographic-security claim. Both restrictions are inherited from the
parent package and are not weakened here.

**Falsifier.** If some internal state transform reproduced `ADOPT` on all registered cases,
the `EXTERNALLY_REGISTERED` qualifier would be false and this row would not be earned.

**Forbidden extrapolation.** `RECURSIVE_SELF_IMPROVEMENT_PROVED`,
`AUTONOMOUS_SELF_AUTHORITY`, `VERIFIER_INFALLIBLE`. Authority remains external; a lowering of
the adoption transition is not a licence for self-authority.

**Dependencies.** AG5X-1's exact lowering of `PROPOSE`, `VERIFY` and `ADOPT`; the
propose/verify/adopt transitions, authority fixture and receipt format of
`gmi-833-g0-governed-self-change-v1` (blob pinned in `MANIFEST_V1.json`); the internal-triple
falsifier frozen in `FREEZE_V1.md` section 6; the `adopt_externality` block of
`RESULT_V1.json`, matched by route B, and the hostile `selfchange_drop_admit` in
`TEST_RESULT_V1.json`.

**Strongest parents.** Lamport, *The Part-Time Parliament* (1998), and the wider literature on
externally attested state change, which own the pattern of an adoption step guarded by an
attestation produced outside the adopting process; `gmi-833-g0-governed-self-change-v1`, which
owns the transitions themselves (`PARENT_LEDGER.md`). This result only measures that the guard
cannot be folded into the internal state transform.

---

## AG5X-4 — The provenance tag is inert on state and total as an admission gate

**Statement.** The `EXTERNAL_DATA` tag changes no registered well-formed transition, and is
the whole of the admissibility test for externally produced values.

**Result.** `inert_differences = 0 / 486` well-formed applications with and without the tag
test. `forged_rejected_with_tag_gate = 24 / 24`; `forged_accepted_without_tag_gate = 24 / 24`.

**Reading.** The tag is a discipline annotation on the state map and a complete gate on
admissibility. Those are different roles and the receipt records both numbers rather than
collapsing them.

**Falsifier.** One well-formed transition that changes when the tag test is deleted refutes
inertness; one forged value the tagged path admits refutes totality.

**Forbidden extrapolation.** `EXTERNAL_RESPONSE_IS_TRUTH`, `AUTHORITY_DELEGATED_TO_TOOL`.
Returning from a tool does not make a value verified.

**Assumptions.** The registered channel universe of `FREEZE_V1.md` section 4: the two
registered tools, all three tool arguments, all 27 local states and all three agents, which
give the 486 well-formed `APPLY_EXTERNAL` applications; the 24 forged values are the
registered corruptions of each tool response (a wrong value, a `LOCAL_DATA` tag, an unknown
tool). Inertness is asserted only over registered well-formed transitions and totality only
over those 24 forgeries; exact integer arithmetic as in AG5X-1.

**Dependencies.** AG5X-1's exact lowering of `CALL` and `APPLY_EXTERNAL`; the channel and
external-call semantics of `gmi-833-g0-interaction-channels-v1` (blob pinned in
`MANIFEST_V1.json`); the tag falsifier frozen in `FREEZE_V1.md` section 6; the
`external_data_tag` block of `RESULT_V1.json`, matched by route B, and the hostile
`channel_tag_dropped` in `TEST_RESULT_V1.json`.

**Strongest parents.** Hoare, *Communicating Sequential Processes* (1978), and Milner, *A
Calculus of Communicating Systems* (1980), which own typed communication as composition;
`gmi-833-g0-interaction-channels-v1`, which owns the operator semantics and the provenance tag
(`PARENT_LEDGER.md`). Separating the tag's state effect from its admission role is the only
residual claimed.

---

## AG5X-5 — One operator is resource-priced, and the price is exhibited

**Statement.** `NEIGHBOR_UPDATE` is the single registered operator whose result depends on
structure beyond its value arguments and whose lowering cost varies with that structure.

**Result.** Over 756 same-state graph pairs, results differ on 680 for `NEIGHBOR_UPDATE` and
on 0 for both `POINTWISE` and `GLOBAL_BROADCAST`. The lowering's charged role count by edge
count is `0 -> 24`, `1 -> 28`, `2 -> 33`, `3 -> 39`, and the parent's declared resource vector
`(3 + 2|E|, 3, 2|E|, sum_v max(deg(v) - 1, 0))` is reproduced on all 648 cases.

**Falsifier.** If a constant charge reproduced the parent's vector, the status would be
`MACRO`, not resource-priced. The hostile `graph_constant_charge` plants exactly that and is
detected on all 216 graph/state cases, with the control clean.

**Forbidden extrapolation.** `UNIVERSAL_GRAPH_EXPRESSIVITY`, `GNN_DERIVED`,
`ARBITRARY_GROUP_EQUIVARIANCE`, `INFINITE_GRAPH_RESULT`. Three sites and eight graphs are the
whole registered scope.

**Assumptions.** The local/graph universe of `FREEZE_V1.md` section 4: all 8 simple undirected
graphs on three sites, all 27 states, the three registered operators and all 6 site
relabelings; structure means the registered adjacency, read from the register store. The
charged role counts are relative to this lowering and are deliberately outside the two-route
agreement set (`CORE.md`).

**Dependencies.** AG5X-1's exact lowering and resource-vector reproduction for `POINTWISE`,
`GLOBAL_BROADCAST` and `NEIGHBOR_UPDATE`; the operator semantics and declared resource vectors
of `gmi-833-g0-local-graph-ops-v1` (blob pinned in `MANIFEST_V1.json`); the
`RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE` rule of `FREEZE_V1.md` section 1 and its falsifier
in section 6; `graph_structure_dependence` and the cost-by-edge-count measurement in
`RESULT_V1.json`, and the hostile `graph_constant_charge` in `TEST_RESULT_V1.json`.

**Strongest parents.** `gmi-833-g0-local-graph-ops-v1`, which owns the three operators and the
declared vector reproduced above; AJ5's transfer boundary, which says instruction-count
descriptions do not transfer between lowerings; Plotkin's structural operational semantics (1981)
for the shape of every lowering (`PARENT_LEDGER.md`). None registered beyond these.

---

## AG5X-6 — A guard the registered scope cannot identify, stated rather than hidden

**Statement.** The extended universe identifies four of the five guards in the adoption
chain. The replay guard is **not** identified, and cannot be at this scope: adoption strictly
increments the active version, so a consumed proposal always also fails the version test and
no registered case makes the replay guard the single failure.

**Result.** Over 145 registered adoption attempts, `guard_isolable` is
`fresh: false`, `pending_ok: true`, `admitted: true`, `version_ok: true`, `accepted: true`.
Exhaustively over all 31 proper subsets of the guard chain, exactly 1 reproduces the parent's
outcome on every case — the subset that drops the replay guard alone — matching the
isolation analysis exactly (`prediction_matches: true`). The 27-case base universe identifies
only the accept guard and admits 15 reproducing subsets; adding the wrong-authority,
corrupted-signature, corrupted-binding, not-pending, replay and stale-version attempts
tightens 15 to 1.

**Why this is published as a result.** A checker that silently accepted the 15-subset state
would have licensed a four-guard lowering as if it were the parent's chain. The number is
recorded, the residual guard is named, and the structural reason is given.

**Falsifier.** A registered configuration in which a consumed proposal still matches the
current active version would isolate the replay guard and make this boundary false.

**Forbidden extrapolation.** That the replay guard is redundant. It is not identified at this
scope; that is a statement about the scope, not about the guard.

**Assumptions.** The governed self-change universe of `FREEZE_V1.md` section 4 extended with
the registered wrong-authority, corrupted-signature, corrupted-binding, not-pending, replay
and stale-version attempts, 145 adoption attempts in all; the parent's five-guard chain
(`fresh`, `pending_ok`, `admitted`, `version_ok`, `accepted`) and its rule that adoption
strictly increments the active version. A guard counts as identified when some registered case
makes it the single failure.

**Dependencies.** AG5X-3 and the adoption chain of `gmi-833-g0-governed-self-change-v1` (blob
pinned in `MANIFEST_V1.json`); the exhaustive guard null over all 31 proper subsets, published
as `adopt_guard_subsets_base_universe` and `adopt_guard_subsets_extended_universe` under
`nulls` in `RESULT_V1.json` and matched by route B; the hostiles `selfchange_allow_replay` and
`guard_isolation_trimmed` in `TEST_RESULT_V1.json`.

**Strongest parents.** Lamport (1998) and the literature on externally attested state change,
and `gmi-833-g0-governed-self-change-v1`, which owns verifier-gated adoption with replay
protection, listed as not claimed novel in `MANIFEST_V1.json`. The residual here is only the
named identifiability boundary.
