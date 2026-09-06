"""ORION-V2 ↔ OCM intake and export protocol (M11 §15).

Theory travels one way as *obligations*: an ORION-V2 theorem (MEG-nn / batch item) is imported
as an `Intake` record naming the theorem, the OCM obligation ids (KS-Tnn) it discharges or opens,
the runtime defect it exposed (if any), and a status.  Imported fixes carry the origin
`ORION_V2_IMPORT` on any proposal they trigger, so the self-model never presents them as its own
invention (M11 §7).  Runtime findings travel the other way as `Export` records (an open item for
the theory atlas: a gap the machine hit that no theorem covers).  Both directions are data with
evidence ids; neither carries authority (the theory does not adopt itself into the runtime, the
runtime does not certify theory).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence


class IntakeStatus(str, Enum):
    IMPORTED = "IMPORTED"                   # theorem read; obligations mapped
    DISCHARGED = "DISCHARGED"               # runtime obligation test exists and passes
    DEFECT_FOUND = "DEFECT_FOUND"           # theorem exposed a runtime defect (fix carries ORION_V2_IMPORT origin)
    OPEN = "OPEN"                           # obligation named, no runtime test yet


@dataclass(frozen=True)
class Intake:
    theorem: str                            # e.g. "MEG-33 (batch 5 E3)"
    source_ref: str                         # ORION-V2 path or PR
    obligations: tuple[str, ...]            # KS-Tnn ids in the OCM registry
    runtime_defect: str | None
    fix_ref: str | None                     # OCM ledger row / commit that applied the fix
    status: IntakeStatus


@dataclass(frozen=True)
class Export:
    finding: str                            # runtime gap the theory does not cover
    evidence: tuple[str, ...]               # ledger rows / receipts
    proposed_atlas_item: str                # the open item for the theory atlas


# The record of the programme so far (data; extended by each batch).
INTAKES: tuple[Intake, ...] = (
    Intake("B1(ii) derived promotion", "ORION-V2 research/machine-epistemics-theory batch 2 (PR #333)", ("KS-T67",), "promoted atom stayed LIVE after its bridge was revoked (S21)", "ledger S21: admit_evidence(derived_from=…)", IntakeStatus.DEFECT_FOUND),
    Intake("C4 enabling verdict absorbs CANNOT_CHECK", "batch 3 (PR #341)", ("KS-T68", "KS-T69"), "solve loop discarded the enabled set (S20)", "ledger S20", IntakeStatus.DEFECT_FOUND),
    Intake("C7 verdict policy", "batch 3 (PR #341)", ("KS-T70",), None, None, IntakeStatus.DISCHARGED),
    Intake("D1 equivalence names its scale", "batch 4 (PR #343)", ("KS-T71",), "equivalence verdicts without a scale (S28)", "M7 report §8 addendum; ledger S28", IntakeStatus.DEFECT_FOUND),
    Intake("E1 self-model fibre without self-authority", "batch 5 (PR #344)", ("KS-T96",), "failure records were plain observations: revoking a trace did not reopen the diagnoses built on it", "ledger S34; tests/m11/test_batch5_defects.py::test_E1", IntakeStatus.DEFECT_FOUND),
    Intake("E2 diagnosis distribution / E3 obstruction certificate ⇔ Jump precondition", "batch 5 (PR #344)", ("KS-T97", "KS-T98"), "alarm took a frequency term; certificate judged its own alternative list instead of the registry closure", "ledger S34; tests/m11/test_batch5_defects.py::test_E2_E3", IntakeStatus.DEFECT_FOUND),
    Intake("E4 proposal object and pre-outcome prediction / E5 shadow non-interference and assurance chain", "batch 5 (PR #344)", ("KS-T99", "KS-T100"), "no disjointness clause on the proposer's dev tasks; digest string instead of a K_self receipt; non-interference compared the state hash only", "ledger S34; tests/m11/test_batch5_defects.py::test_E4_E5, ::test_E5", IntakeStatus.DEFECT_FOUND),
    Intake("E6 stamped DPO adoption and hash-exact rollback / E7 meter and livelock bound", "batch 5 (PR #344)", ("KS-T101", "KS-T102"), "rollback left caches and exactness to the caller; the meter was a mutable field reachable through a nested key", "ledger S34; tests/m11/test_batch5_defects.py::test_E6, ::test_E7", IntakeStatus.DEFECT_FOUND),
    Intake("E8 KS-T12/T14 improvement halves", "batch 5 (PR #344)", ("KS-T12", "KS-T14"), None, None, IntakeStatus.OPEN),
    Intake("F1 capability-level revocation over ⊕ / F4 false-structural-alarm lemma / F5 epistemic identity", "batch 6 (PR #347)", ("KS-T114", "KS-T110", "KS-T112"), "revocation reported no live remainder; no reinstate/reroute candidate before escalation; identity judged by path string and handle", "ledger S35; tests/m11/test_batch6_obligations.py", IntakeStatus.DEFECT_FOUND),
    Intake("batch 6 consequences 5 and 7: persisted adoption artifacts; evidence-derived Jump assessment", "batch 6 (PR #347)", ("KS-T113", "KS-T111"), "adoption artifacts lived in process memory; jump sufficiency was a caller flag", "ledger S35; selfmodel/jump_evidence.py", IntakeStatus.DEFECT_FOUND),
    Intake("F2 unit of inference / F8 reference-arm binding", "batch 6 (PR #347)", ("KS-T115",), "pooled orderings were pseudo-replication (S32); reference arm needed the REFERENCE label", "M12 V3 paired lifetimes; reference receipts", IntakeStatus.DISCHARGED),
    Intake("G7 licence vs truth grading / G8 paired-lifetime sizes and family bound", "batch 7 (PR #349)", ("KS-T117",), "V3 rule had no primary family, unbounded family count and a two-sided unanimous test (S37); out-of-scope suite was all world-false", "M12 V4 (PR #34); ledger S37–S38", IntakeStatus.DEFECT_FOUND),
    Intake("G1 registered-class Jump levels / G5 KS-T12 and KS-T14 clauses", "batch 7 (PR #349)", ("KS-T111", "KS-T12", "KS-T116"), "J4/J5 proposals accepted without a registered class; unconditional improvement claims", "selfmodel/jump_evidence.py (registered_class); registry clauses", IntakeStatus.DEFECT_FOUND),
    Intake("G2 MEG-07 structural clause / G3 CF prefix commitment / G4 MDL decision / G6 (+,×) measure / G9 MEG-34 bound", "batch 7 (PR #349)", (), None, None, IntakeStatus.OPEN),
    Intake("H1 FDX-01 closure interface / H3 FDX-03 information conservation / H4 FDX-05 reversibility classes", "batch 8 (PR #359)", ("KS-T118", "KS-T120", "KS-T121"), "commitment gate read epoch-bounded scopes as current on context alone; information receipt lacked the channel join; rollback exactness class was implicit", "tests/m11/test_batch8_obligations.py; lifetime.machine.info; AdoptionLedger.last_rollback", IntakeStatus.DEFECT_FOUND),
    Intake("H2 FDX-02 controlled viability (PARENT_SUFFICIENT)", "batch 8 (PR #359)", ("KS-T119",), "decision/gate lack typed risk, resource and envelope coordinates", None, IntakeStatus.OPEN),
    Intake("I1 FDX-08 stochastic warrant dynamics / I2 FDX-11 bifurcation / I3 FDX-13 self-model calibration / I4 FDX-15 attribution theorem", "batch 9 (PR #365)", ("KS-T122", "KS-T123", "KS-T124", "KS-T125"), "monitor triggers per step at fixed level; no model-id slot for rate claims; obstruction certificate lacks the evidence-invariance half; calibration receipts untagged; V4/V5 attribution clause 4 declared, not ablated", None, IntakeStatus.OPEN),
    Intake("J1 FDX-06 distributed epistemics / J2 FDX-07 epistemic games / J3 FDX-14 whole-system lower bounds", "batch 10 (PR #364)", ("KS-T126", "KS-T127", "KS-T128", "KS-T129", "KS-T130", "KS-T131", "KS-T132", "KS-T133"), "imported records lack per-principal message assumptions; revocation state last-writer-wins across registries; independence counted over ids not principals; admission has no CANNOT_REPRESENT", None, IntakeStatus.OPEN),
    Intake("K1 FDX-09 construction-learning frontier / K2 FDX-10 representation discovery / K3 FDX-12 prefix commitment", "batch 11 (PR #366)", ("KS-T134", "KS-T135", "KS-T136", "KS-T137", "KS-T138", "KS-T139", "KS-T140", "KS-T141"), "chart packed by sub-derivation identity and undercounted derivations; no identification receipt on the induced grammar; relation vocabulary registered by fiat; realiser channel undeclared", "ledger S42 + phase F (span-lexical packing, Catalan test); Grammar.identification (H1/H2); REPRESENTATION_INTRODUCTION_RECEIPT (H5); H7 (realiser channel declaration) deferred: src/ocm/language/realize.py is pinned by the frozen N1 language bootstrap manifest (research/ocm-n1/LANGUAGE_BOOTSTRAP_MANIFEST_V1.json), so the declaration enters at the N2 bootstrap freeze; H6/H8 open", IntakeStatus.DEFECT_FOUND),
    Intake("Mechanised core: liveness order, warrant intervals, oplus/otimes, reopening cone, authority meet in Lean 4.14.0", "batch 12 (PR #367)", (), None, "no runtime change: the OCM exact checkers are the finite oracle the Lean statements agree with", IntakeStatus.DISCHARGED),
    Intake("Field map V1: theorem table, dependency graph, exactly bounded impossibilities, derived obligation registry KS-T118-T141", "batch 13 (PR #368)", (), None, "docs/theorems/OCM_OBLIGATION_REGISTRY_DERIVED_V1.json copied verbatim; 21 obligations OPEN, 3 PROVED", IntakeStatus.OPEN),
)

EXPORTS: tuple[Export, ...] = (
    Export("a failure attributed to a revoked dependency can look structural (every task fails) — the theory needs a false-structural-alarm lemma", ("ledger S5 scenario", "M11 S5"), "atlas: reinstatement precedes escalation"),
    Export("recorded replay can only audit governance (narrowness, witnesses); diagnostic accuracy needs an ablation channel — the theory should state what a self-model can conclude without counterfactual access", ("M11 historical replay",), "atlas: observational limits of self-diagnosis"),
)


def audit(intakes: Sequence[Intake] = INTAKES) -> dict[str, Any]:
    by = {s.value: sum(i.status is s for i in intakes) for s in IntakeStatus}
    return {"intakes": len(intakes), "by_status": by, "defects_with_fix_ref": sum(1 for i in intakes if i.status is IntakeStatus.DEFECT_FOUND and i.fix_ref), "exports": len(EXPORTS)}
