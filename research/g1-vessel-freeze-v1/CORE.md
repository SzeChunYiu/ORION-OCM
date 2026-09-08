# G1 vessel freeze — current executable machine

**Terminal:** `COMPACT_VESSEL_PARTIAL`

This freezes the live machine at
`b35093a26e51ccf4829aa1218957827d95db8923` as

```text
M_t = (F_t, O_t, Π_t, C)
```

and discharges the G1.1 architecture inventory. It does not claim the
vessel is minimal (G1.2 was not run) and does not claim learned state
dominates authored source (G1.3 is a single-head count).

[Manifest](MANIFEST.json) ·
[Immutable vs mutable](IMMUTABLE_VS_MUTABLE.json) ·
[Prior information](PRIOR_INFORMATION.json) ·
[Duplicate cores](DUPLICATE_CORES.json) ·
[Domain contracts](DOMAIN_CONTRACTS.json) ·
[Architecture rules](ARCHITECTURE_RULES.json) ·
[G1 checkboxes](G1_CHECKBOXES.json) ·
[G1.3 counts](G1_3_COUNTS.json) ·
[Source freeze](SOURCE_FREEZE.json) ·
[Terminal](TERMINAL.json)

No production code was deleted. Nothing was pushed.

## Frozen machine

| Slot | Live implementation | ORION-V2 binding |
|---|---|---|
| `F_t` | one `KnowledgeSpace` + evidence registry + organisation views on one `ocm.runtime.ocm_runtime.OCMRuntime` | `𝒦_t` |
| `O_t` | `OperatorRegistry` + KSO procedure algebra; work `Operator`/`Skill` is a parallel donor schema | `𝓟_t` |
| `Π_t` | `solve.py` stage pipeline + runtime orchestration + jump/self-change proposals | `𝔐_t` executive (`η`, `𝒞`, `𝒰`, `𝒥`) |
| `C` | `constitution` hard gates, injected `CommitAuthority`, resource meter | `𝔠 = (Check, Authority, Meter, Commit)` |

Issue #165 and the KSO contract both write `Π_t`. They are not the same
object. This freeze calls KSO navigation `Π_nav` and the #165 executive
`Π_exec`.

Required transition, as implemented:

```text
o_t = Π_exec(F_t, goal_t, O_t, budget_t)
Δ_t = o_t(...)
(F, O, Π)_{t+1} = Admit_C(Δ_t)
```

The solver reads and does not write. Learners propose and do not admit.
Commit authority is host-injected; internal composition strips the
`commit` coordinate. Physical ledger bytes are not warrant.

## Lifecycle surfaces (present, not causally proven)

The G1 vessel must already contain machinery for

```text
experience → represent → check → learn → persist
→ retrieve → execute → revise → consolidate → propose change
```

Those surfaces exist (`MANIFEST.json` `lifecycle_surfaces`). Causal
`experience → scoped method → restart → fresh-task use` remains G2 and
is not claimed. Programme `CORE.md` still records that bottleneck.

## Domain entry

Language, mathematics and procedural work enter through typed
field/operator contracts:

- language registers `meaning:*` types and admits representation atoms
  through `language.field_bridge`;
- dialogue commitments bind through that same bridge;
- proof kernels are declared donor checkers (`propositional` exact;
  `lean4` is `CANNOT_CHECK`);
- work/science write evidence into the shared runtime ledger.

`DOMAIN_CORE_FORK_REQUIRED` is not issued. Compact views
(`MeaningGraph`, `DialogueWorkspace`, work dict-state) are not second
Check/Authority/Meter/Commit cores.

## What is not eliminated

Two retained schemas would look like extra cores if read carelessly:

1. `ocm.runtime.OCMRuntime` (from `runtime/state.py`) is the M0 custody
   runtime. Live cognition imports `ocm.runtime.ocm_runtime.OCMRuntime`.
2. `work.Operator` is a parallel operator API on KSO warrants, not a
   second truth store.

Both stay. G1.1 “eliminate duplicated cognitive cores” is therefore
**not earned as deletion**. The inventory is complete: there is no live
second `F` or `C`.

## G1.3 snapshot (bounded)

Non-comment `src/ocm/` lines at this head:

| role | nloc |
|---|---|
| F | 5287 |
| PRIOR | 5046 |
| Π | 3588 |
| HARNESS | 4551 |
| O | 1392 |
| C | 1094 |

Authored domain source is almost as large as field machinery.
Controller source is smaller than `F` and larger than `O`. This is not
`CONTROLLER_GROWTH_DOMINATES` (no growth series) and not
`STATE_SIZE_DOMINATES` (no instance-state bytes).

## Earned checkboxes

**G1.1 earned:** freeze manifest; ORION-V2 bindings; immutable
machinery; mutable state; prior-information classification; typed
domain contracts.

**G1.1 not earned:** eliminate duplicated cores.

**§2 architecture rules earned:** external non-self-certifying `C`;
no new cores by default; donor operators; method origin/scope/warrant
history; neural/approximate outputs remain proposals; storage is not
authority; no new core issue opened.

**§2 partial / design-only:** intelligence accumulates in `F`/`O`
(design yes, empirical no); `Π` remains small (solve is
domain-general, but 3588 nloc plus domain planners).

**G1.2:** none.

**G1.3 earned:** count retained domain rules as prior.
**G1.3 partial:** source snapshot.
**G1.3 not earned:** growth-across-domains; competence-in-state;
controller hostile.

## Terminal

`COMPACT_VESSEL_PARTIAL` is the only G1 exit issued.

Not issued: `MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE`,
`CURRENT_KSO_PARENT_SUFFICIENT`, `DOMAIN_CORE_FORK_REQUIRED`,
`CONTROLLER_GROWTH_DOMINATES`, `STATE_SIZE_DOMINATES`.
