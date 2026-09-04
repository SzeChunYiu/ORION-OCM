"""KSO M6a — integrate real Lean-kernel proof receipts as warranted knowledge.

This module consumes the already-frozen ME-X3 protected Lean receipt. It does NOT rerun the
protected campaign and does NOT claim a new frontier-math result. Its purpose is narrower and
load-bearing: a proof accepted by the registered Lean kernel becomes a warranted, connected KSO
math atom through the frozen M0 EXACT_CHECKER admission path; a registered corrupted proof,
CANNOT_CHECK, disagreement, or malformed receipt cannot become warranted knowledge.

The upstream ME-X3 scientific terminal remains PARENT_SUFFICIENT (M and B5 tie 0.944 on the
registered joint endpoint). This file only integrates the exact verifier channel.

Important provenance rule: ME-X3 deliberately has one good and one corrupted proof file for the
same theorem task. Therefore KSO certificate atoms are keyed by proof-file identity, not theorem
identity. A theorem may have several candidate proofs; only kernel-verified proof certificates earn
warrant.

Exit: 0 pass, 1 defect, 2 CANNOT_CHECK.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN_RECEIPT = ROOT / "research" / "experiments" / "me-x3" / "results" / "ME_X3_LEAN_RECEIPT_PROTECTED_V1.json"


class CannotCheck(RuntimeError):
    pass


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CannotCheck(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        raise CannotCheck(f"cannot import {path}: {exc}") from exc
    return mod


m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
kso = m0.kso
ONE = m0.ONE


@dataclass(frozen=True)
class VerifiedMathAtom:
    task_id: str
    source_file: str
    evidence_id: int
    atom_id: str


def _evidence_id(receipt: Mapping[str, object], row: Mapping[str, object]) -> int:
    payload = "|".join(
        (
            str(receipt.get("lean_commit", "")),
            str(receipt.get("lean_version", "")),
            str(row.get("task_id", "")),
            str(row.get("file", "")),
            str(row.get("verdict", "")),
        )
    )
    return int(hashlib.sha256(payload.encode()).hexdigest()[:15], 16)


def _proof_atom_id(file: str) -> str:
    return "math:proof:" + hashlib.sha256(file.encode()).hexdigest()[:20]


def load_receipt(path: Path = LEAN_RECEIPT) -> dict[str, object]:
    if not path.exists():
        raise CannotCheck(f"Lean receipt missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CannotCheck(f"Lean receipt unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise CannotCheck("Lean receipt must be a JSON object")
    return data


def validate_receipt(receipt: Mapping[str, object]) -> tuple[tuple[Mapping[str, object], ...], tuple[Mapping[str, object], ...]]:
    rows_raw = receipt.get("rows")
    if not isinstance(rows_raw, list):
        raise CannotCheck("Lean receipt rows missing")
    rows: tuple[Mapping[str, object], ...] = tuple(r for r in rows_raw if isinstance(r, dict))
    if len(rows) != len(rows_raw):
        raise CannotCheck("Lean receipt contains non-object row")
    if int(receipt.get("n", -1)) != len(rows):
        raise CannotCheck("Lean receipt n does not match rows")
    if int(receipt.get("cannot_check", -1)) != 0:
        raise CannotCheck("upstream Lean receipt contains CANNOT_CHECK rows")
    if int(receipt.get("disagreements", -1)) != 0:
        raise AssertionError("upstream Lean receipt disagrees with the exhaustive oracle")
    if receipt.get("agrees_with_exhaustive_oracle") is not True:
        raise AssertionError("upstream Lean/oracle agreement is not established")

    accepted: list[Mapping[str, object]] = []
    rejected: list[Mapping[str, object]] = []
    seen_files: set[str] = set()
    for row in rows:
        expect = row.get("expect")
        verdict = row.get("verdict")
        file = str(row.get("file", ""))
        task = str(row.get("task_id", ""))
        if not file or not task or file in seen_files:
            raise CannotCheck("Lean row has blank/duplicate identity")
        seen_files.add(file)
        if expect == "ACCEPT" and verdict == "VERIFIED_BY_LEAN_KERNEL":
            accepted.append(row)
        elif expect == "REJECT" and verdict == "REJECTED_FOR_THE_REGISTERED_REASON":
            rejected.append(row)
        else:
            raise CannotCheck(f"unusable Lean row {file}: expect={expect} verdict={verdict}")

    if int(receipt.get("verified_by_lean_kernel", -1)) != len(accepted):
        raise CannotCheck("verified_by_lean_kernel count mismatch")
    if int(receipt.get("rejected_for_registered_reason", -1)) != len(rejected):
        raise CannotCheck("rejected_for_registered_reason count mismatch")
    if not accepted or not rejected:
        raise CannotCheck("positive and negative proof controls are both required")
    return tuple(accepted), tuple(rejected)


def base_math_space():
    return kso.KnowledgeSpace(
        (
            kso.Atom("math:library", "math_library", ONE),
            kso.Atom("math:lean-kernel", "exact_checker", ONE),
        ),
        (
            kso.Hyperedge(
                "math:library-to-kernel",
                ("math:library",),
                ("math:lean-kernel",),
                "SUPPORT",
                profile=ONE,
            ),
        ),
    )


def admit_verified_rows(receipt: Mapping[str, object], accepted: Sequence[Mapping[str, object]]):
    ks = base_math_space()
    atoms: list[VerifiedMathAtom] = []
    evidence_ids: set[int] = set()
    atom_ids: set[str] = set()
    for row in accepted:
        eid = _evidence_id(receipt, row)
        if eid in evidence_ids:
            raise CannotCheck("proof evidence identity collision")
        evidence_ids.add(eid)
        task = str(row["task_id"])
        file = str(row["file"])
        atom_id = _proof_atom_id(file)
        if atom_id in atom_ids:
            raise CannotCheck("proof atom identity collision")
        atom_ids.add(atom_id)
        atom = kso.Atom(atom_id, "verified_proof_certificate", (frozenset({eid}),))
        edge = kso.Hyperedge(
            f"math:kernel-certifies:{hashlib.sha256(file.encode()).hexdigest()[:20]}",
            ("math:lean-kernel",),
            (atom_id,),
            "SUPPORT",
            profile=ONE,
        )
        ks, adm = m0.admit(ks, atom, (edge,), m0.CertificateKind.EXACT_CHECKER)
        if not (adm.warranted and adm.edges_added == 1 and adm.reachable_by_navigation):
            raise AssertionError(f"verified proof {file} failed M0 EXACT_CHECKER admission")
        atoms.append(VerifiedMathAtom(task, file, eid, atom_id))
    return ks, tuple(atoms)


def check_revocation(ks, proof: VerifiedMathAtom) -> dict[str, object]:
    amap = ks.atom_map()
    atom = amap[proof.atom_id]
    if not kso.profile_live(atom.profile, ()):  # no-alarm
        raise AssertionError("verified proof certificate is not live before revocation")
    if kso.profile_live(atom.profile, {proof.evidence_id}):
        raise AssertionError("verified proof certificate stayed live after its evidence was revoked")
    before = kso.navigation_matrix(ks)
    after = kso.navigation_matrix(ks, revoked={proof.evidence_id})
    ids = ks.ids
    src = ids.index("math:lean-kernel")
    dst = ids.index(proof.atom_id)
    if not (before[src][dst] > 0 and after[src][dst] == 0):
        raise AssertionError("revocation did not remove the certified path exactly")
    return {
        "proof_atom": proof.atom_id,
        "task_id": proof.task_id,
        "source_file": proof.source_file,
        "evidence_id": proof.evidence_id,
        "pre_live": True,
        "post_live": False,
        "pre_navigation_share_positive": True,
        "post_navigation_share": "0",
    }


def hostile_mutations(receipt: Mapping[str, object]) -> dict[str, int]:
    detected = {}

    cc = copy.deepcopy(dict(receipt))
    cc["cannot_check"] = 1
    try:
        validate_receipt(cc)
        detected["cannot_check_blocks_admission"] = 0
    except CannotCheck:
        detected["cannot_check_blocks_admission"] = 1

    dg = copy.deepcopy(dict(receipt))
    dg["disagreements"] = 1
    dg["agrees_with_exhaustive_oracle"] = False
    try:
        validate_receipt(dg)
        detected["oracle_disagreement_blocks_admission"] = 0
    except AssertionError:
        detected["oracle_disagreement_blocks_admission"] = 1

    flipped = copy.deepcopy(dict(receipt))
    rows = flipped["rows"]
    assert isinstance(rows, list)
    bad = next(r for r in rows if isinstance(r, dict) and r.get("expect") == "REJECT")
    bad["verdict"] = "VERIFIED_BY_LEAN_KERNEL"
    try:
        validate_receipt(flipped)
        detected["corrupted_proof_cannot_be_promoted"] = 0
    except CannotCheck:
        detected["corrupted_proof_cannot_be_promoted"] = 1

    missing = copy.deepcopy(dict(receipt))
    rows2 = missing["rows"]
    assert isinstance(rows2, list)
    rows2.pop()
    try:
        validate_receipt(missing)
        detected["row_count_drift_detected"] = 0
    except CannotCheck:
        detected["row_count_drift_detected"] = 1

    if any(v != 1 for v in detected.values()):
        raise AssertionError(f"hostile mutation escaped: {detected}")
    return detected


def run_m6a(path: Path = LEAN_RECEIPT) -> dict[str, object]:
    receipt = load_receipt(path)
    accepted, rejected = validate_receipt(receipt)
    ks, proof_atoms = admit_verified_rows(receipt, accepted)
    rejected_atom_ids = {_proof_atom_id(str(r["file"])) for r in rejected}
    if rejected_atom_ids & set(ks.ids):
        raise AssertionError("a rejected proof certificate became a warranted KSO atom")
    if len(proof_atoms) != len(accepted) or len(set(p.atom_id for p in proof_atoms)) != len(proof_atoms):
        raise AssertionError("proof atom count/identity mismatch")
    if any(not kso.profile_live(ks.atom_map()[p.atom_id].profile, ()) for p in proof_atoms):
        raise AssertionError("admitted proof atom is not live")
    lifecycle = check_revocation(ks, proof_atoms[0])
    hostiles = hostile_mutations(receipt)
    return {
        "terminal": "M6A_FORMAL_MATH_VERIFIER_CHANNEL_INTEGRATED_PARENT_SUFFICIENT",
        "source": {
            "receipt": str(path.relative_to(ROOT)),
            "lean_version": receipt.get("lean_version"),
            "lean_commit": receipt.get("lean_commit"),
            "rows": receipt.get("n"),
            "kernel_verified": len(accepted),
            "registered_rejections": len(rejected),
            "cannot_check": receipt.get("cannot_check"),
            "disagreements": receipt.get("disagreements"),
        },
        "kso": {
            "verified_proof_atoms": len(proof_atoms),
            "rejected_proof_atoms": 0,
            "all_verified_atoms_warranted_and_live": True,
            "rejected_certificate_identities_excluded": len(rejected_atom_ids),
            "lifecycle": lifecycle,
        },
        "hostiles": hostiles,
        "upstream_scientific_terminal": "PARENT_SUFFICIENT",
        "authority": {
            "formal_math_verifier_channel_integrated": True,
            "protected_campaign_rerun": False,
            "open_frontier_problem_solved": False,
            "frontier_math_discovery": False,
            "novelty": False,
            "M6_full": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--receipt", type=Path, default=LEAN_RECEIPT)
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    try:
        r = run_m6a(a.receipt)
        if a.out:
            a.out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(r, sort_keys=True))
        return 0
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except Exception as exc:
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
