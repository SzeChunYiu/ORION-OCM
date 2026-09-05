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
)

EXPORTS: tuple[Export, ...] = (
    Export("a failure attributed to a revoked dependency can look structural (every task fails) — the theory needs a false-structural-alarm lemma", ("ledger S5 scenario", "M11 S5"), "atlas: reinstatement precedes escalation"),
    Export("recorded replay can only audit governance (narrowness, witnesses); diagnostic accuracy needs an ablation channel — the theory should state what a self-model can conclude without counterfactual access", ("M11 historical replay",), "atlas: observational limits of self-diagnosis"),
)


def audit(intakes: Sequence[Intake] = INTAKES) -> dict[str, Any]:
    by = {s.value: sum(i.status is s for i in intakes) for s in IntakeStatus}
    return {"intakes": len(intakes), "by_status": by, "defects_with_fix_ref": sum(1 for i in intakes if i.status is IntakeStatus.DEFECT_FOUND and i.fix_ref), "exports": len(EXPORTS)}
