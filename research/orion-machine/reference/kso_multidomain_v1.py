"""Controlled multi-domain KSO — one KnowledgeSpace holds learned procedures and Lean proofs.

This closes a structural integration gap in the prototype: M3 procedures and M6a proof
certificates no longer need separately constructed knowledge spaces. A single warranted hypergraph
contains a procedure region and a formal-mathematics region joined by a neutral root.

Evidence identities are globally namespaced/content-bound. The finite checks require cross-domain
non-interference: revoking a procedure lesson cannot kill a Lean proof and revoking a proof cannot
kill an unrelated learned procedure.

This is a controlled two-domain integration, not a scalability or open-domain claim.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent


def _load(name: str):
    if name in sys.modules:
        return sys.modules[name]
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m0 = _load("kso_m0_freeze_checks_v1")
kso = m0.kso
m3 = _load("kso_m3_learning_v1")
m5 = _load("kso_m5_chat_v1")
m6 = _load("kso_m6_formal_math_v1")
ONE = m0.ONE


def global_evidence_id(namespace: str, payload: str) -> int:
    if not namespace.strip() or not payload:
        raise ValueError("evidence namespace and payload are required")
    return int(hashlib.sha256(f"{namespace}|{payload}".encode()).hexdigest()[:15], 16)


@dataclass
class UnifiedKSO:
    space: object = field(init=False)
    revoked: set[int] = field(default_factory=set)
    procedures: dict[str, object] = field(default_factory=dict)
    procedure_evidence: dict[str, int] = field(default_factory=dict)
    proof_atoms: dict[str, object] = field(default_factory=dict)
    feedback_counts: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.space = kso.KnowledgeSpace(
            (
                kso.Atom("kso:root", "root", ONE),
                kso.Atom("proc:library", "procedure_library", ONE),
                kso.Atom("math:library", "math_library", ONE),
                kso.Atom("math:lean-kernel", "exact_checker", ONE),
            ),
            (
                kso.Hyperedge("root-procedure-region", ("kso:root",), ("proc:library",), "SUPPORT", profile=ONE),
                kso.Hyperedge("root-math-region", ("kso:root",), ("math:library",), "SUPPORT", profile=ONE),
                kso.Hyperedge("math-library-kernel", ("math:library",), ("math:lean-kernel",), "SUPPORT", profile=ONE),
            ),
        )
        self.space.validate()

    def teach(self, command) -> dict[str, object]:
        if not isinstance(command, m5.TeachCommand):
            raise TypeError("teach expects canonical TeachCommand")
        if command.name in self.procedures:
            raise ValueError(f"procedure already registered: {command.name}")
        digest = m5.command_digest(command)
        eid = global_evidence_id("procedure-lesson", digest)
        lesson = m3.Lesson(command.name, m3.Channel.INSTRUCTION, eid, declared_table=command.table)
        receipt = m3.learn_instruction(lesson)
        if receipt.learned is None or not receipt.warranted:
            raise RuntimeError("instruction failed to identify a warranted procedure")
        proc = receipt.learned
        atom_id = f"proc:{command.name}"
        atom = kso.Atom(atom_id, "learned_procedure", (frozenset({eid}),))
        edge = kso.Hyperedge(
            f"proc-library-admits:{command.name}",
            ("proc:library",),
            (atom_id,),
            "COMPOSITION",
            profile=ONE,
        )
        self.space, adm = m0.admit(self.space, atom, (edge,), m0.CertificateKind.INSTRUCTION, revoked=self.revoked)
        if not (adm.warranted and adm.reachable_by_navigation):
            raise RuntimeError("procedure failed unified KSO admission")
        self.procedures[command.name] = proc
        self.procedure_evidence[command.name] = eid
        return {"status": "LEARNED", "name": command.name, "evidence_id": eid, "atom_id": atom_id}

    def solve(self, command) -> dict[str, object]:
        if not isinstance(command, m5.SolveCommand):
            raise TypeError("solve expects canonical SolveCommand")
        proc = self.procedures.get(command.name)
        if proc is None:
            return {"status": "GAP_UNKNOWN_PROCEDURE", "result": None}
        atom_id = f"proc:{command.name}"
        atom = self.space.atom_map()[atom_id]
        if not kso.profile_live(atom.profile, self.revoked):
            return {"status": "GAP_REVOKED_PROCEDURE", "result": None}
        status, value = m3.execute_composite(proc, command.combinator, command.x, self.revoked)
        return {"status": status, "result": value, "name": command.name, "combinator": command.combinator}

    def feedback(self, name: str, verdict: str) -> dict[str, object]:
        self.feedback_counts[name] = self.feedback_counts.get(name, 0) + 1
        lesson = m3.Lesson(name, m3.Channel.FEEDBACK, 0, endpoint_feedback=(("unified", int(verdict == "success")),))
        rec = m3.learn_feedback(lesson)
        if rec.learned is not None or rec.warranted:
            raise AssertionError("feedback unexpectedly created warrant")
        return {"status": rec.status, "name": name}

    def ingest_math_receipt(self) -> dict[str, int]:
        receipt = m6.load_receipt()
        accepted, rejected = m6.validate_receipt(receipt)
        evidence_seen = set(self._all_registered_evidence())
        for row in accepted:
            file = str(row["file"])
            if file in self.proof_atoms:
                raise ValueError(f"proof already registered: {file}")
            local = m6._evidence_id(receipt, row)
            eid = global_evidence_id("lean-proof", str(local))
            if eid in evidence_seen:
                raise RuntimeError("cross-domain evidence collision")
            evidence_seen.add(eid)
            atom_id = m6._proof_atom_id(file)
            if atom_id in self.space.ids:
                raise RuntimeError("cross-domain atom collision")
            atom = kso.Atom(atom_id, "verified_proof_certificate", (frozenset({eid}),))
            edge = kso.Hyperedge(
                f"unified-kernel-certifies:{hashlib.sha256(file.encode()).hexdigest()[:20]}",
                ("math:lean-kernel",),
                (atom_id,),
                "SUPPORT",
                profile=ONE,
            )
            self.space, adm = m0.admit(self.space, atom, (edge,), m0.CertificateKind.EXACT_CHECKER, revoked=self.revoked)
            if not (adm.warranted and adm.reachable_by_navigation):
                raise RuntimeError("verified proof failed unified KSO admission")
            self.proof_atoms[file] = m6.VerifiedMathAtom(str(row["task_id"]), file, eid, atom_id)
        rejected_ids = {m6._proof_atom_id(str(r["file"])) for r in rejected}
        if rejected_ids & set(self.space.ids):
            raise AssertionError("rejected proof entered unified KSO")
        return {"verified": len(accepted), "rejected": len(rejected)}

    def revoke_evidence(self, evidence_id: int) -> None:
        self.revoked.add(evidence_id)

    def reinstate_evidence(self, evidence_id: int) -> None:
        self.revoked.discard(evidence_id)

    def revoke_procedure(self, name: str) -> None:
        if name not in self.procedure_evidence:
            raise KeyError(name)
        self.revoke_evidence(self.procedure_evidence[name])

    def reinstate_procedure(self, name: str) -> None:
        if name not in self.procedure_evidence:
            raise KeyError(name)
        self.reinstate_evidence(self.procedure_evidence[name])

    def proof_live(self, file: str) -> bool:
        p = self.proof_atoms[file]
        return kso.profile_live(self.space.atom_map()[p.atom_id].profile, self.revoked)

    def revoke_proof(self, file: str) -> None:
        self.revoke_evidence(self.proof_atoms[file].evidence_id)

    def _all_registered_evidence(self) -> tuple[int, ...]:
        out = list(self.procedure_evidence.values())
        out.extend(p.evidence_id for p in self.proof_atoms.values())
        return tuple(out)

    def root_activation(self) -> dict[str, Fraction]:
        p = kso.navigation_matrix(self.space, revoked=self.revoked)
        seed = [Fraction(1, 1) if atom_id == "kso:root" else Fraction(0, 1) for atom_id in self.space.ids]
        a = kso.restart_fixed_point(p, seed, Fraction(1, 2))
        return dict(zip(self.space.ids, a, strict=True))


def run_multidomain() -> dict[str, object]:
    u = UnifiedKSO()
    text = m5.TextCodec()
    teach = text.parse("teach AND where 00=0 01=0 10=0 11=1")
    query = text.parse("solve NOT AND on 11")
    learned = u.teach(teach)
    before_math = u.solve(query)
    math = u.ingest_math_receipt()
    if before_math != u.solve(query):
        raise AssertionError("math ingestion changed unrelated procedure behavior")
    first_file = sorted(u.proof_atoms)[0]
    if not u.proof_live(first_file):
        raise AssertionError("verified proof is not live")

    closure = m0.ungated_closure(u.space, ("kso:root",))
    proc_atom = str(learned["atom_id"])
    proof_atom = u.proof_atoms[first_file].atom_id
    if proc_atom not in closure or proof_atom not in closure:
        raise AssertionError("root cannot structurally reach both domains")
    activation = u.root_activation()
    if not (activation[proc_atom] > 0 and activation[proof_atom] > 0):
        raise AssertionError("root navigation does not activate both domains")

    proc_eid = u.procedure_evidence["AND"]
    proof_eid = u.proof_atoms[first_file].evidence_id
    if proc_eid == proof_eid or len(set(u._all_registered_evidence())) != len(u._all_registered_evidence()):
        raise AssertionError("global evidence namespace collision")

    u.revoke_procedure("AND")
    proc_after_revoke = u.solve(query)
    proof_after_proc_revoke = u.proof_live(first_file)
    if proc_after_revoke["status"] != "GAP_REVOKED_PROCEDURE" or not proof_after_proc_revoke:
        raise AssertionError("procedure revocation crossed domain boundary")

    u.reinstate_procedure("AND")
    u.revoke_proof(first_file)
    proc_after_proof_revoke = u.solve(query)
    proof_after_own_revoke = u.proof_live(first_file)
    if proc_after_proof_revoke["status"] != "PASS" or proof_after_own_revoke:
        raise AssertionError("proof revocation crossed domain boundary")

    feedback = UnifiedKSO()
    fb = feedback.feedback("ORPHAN", "success")
    if "proc:ORPHAN" in feedback.space.ids:
        raise AssertionError("feedback created a procedure atom")

    return {
        "terminal": "CONTROLLED_MULTIDOMAIN_KSO_GREEN",
        "space": {
            "atoms": len(u.space.atoms),
            "hyperedges": len(u.space.hyperedges),
            "verified_math_proofs": math["verified"],
            "registered_bad_proofs_excluded": math["rejected"],
            "learned_procedures": len(u.procedures),
            "root_reaches_procedure_region": proc_atom in closure,
            "root_reaches_math_region": proof_atom in closure,
            "root_activates_both": True,
        },
        "noninterference": {
            "procedure_revocation_leaves_math_proof_live": proof_after_proc_revoke,
            "proof_revocation_leaves_procedure_executable": proc_after_proof_revoke["status"] == "PASS",
            "global_evidence_ids_unique": True,
        },
        "feedback": {"status": fb["status"], "created_procedure_atom": False},
        "boundary": {
            "domains": ["learned_boolean_procedures", "Lean_verified_formal_math"],
            "scalability_established": False,
            "automatic_domain_router": False,
            "open_domain_language": False,
            "novelty": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    argparse.ArgumentParser().parse_args(argv)
    try:
        r = run_multidomain()
    except Exception as exc:
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    print(json.dumps(r, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
