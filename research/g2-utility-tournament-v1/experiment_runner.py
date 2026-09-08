"""Qualified runner wrapper for the prospectively frozen G2 utility tournament.

The first CI attempt stopped in protocol tests before the study ran because the
research admission adapter attempted to admit an isolated non-quarantined
procedure atom. KSO correctly rejected it. This wrapper changes only that
engineering adapter: it creates an evidence-backed quarantined source atom and a
typed SUPPORT edge to the selected procedure, matching the runtime's admission
connectivity contract. Train/validation/test populations, candidate generation,
selection rule, budgets and terminals remain exactly those frozen in README.md.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g2_utility_frozen", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel


def connected_admit_selected_method(root: Path, method, training_receipt, tournament_receipt, revoke=False):
    runtime = OCMRuntime(root)
    _training_record, training_evidence = runtime.admit_evidence(
        training_receipt,
        Channel.PROOF,
        "g2-utility-tournament-training.v1",
        scope=E.SCOPE,
    )
    _utility_record, utility_evidence = runtime.admit_evidence(
        tournament_receipt,
        Channel.OBSERVATION,
        "g2-utility-tournament-validation.v1",
        scope=E.SCOPE,
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})

    source_payload = {
        "kind": "g2.utility-tournament.support.v1",
        "training_receipt": content_hash(training_receipt),
        "validation_receipt": content_hash(tournament_receipt),
    }
    source_id = "g2-tournament-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=E.SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )

    payload = {
        "kind": "generator.utility-tournament.v1",
        "fragments": method.fragments,
        "training_tasks": method.training_tasks,
        "fingerprint": method.fingerprint,
    }
    atom_id = "generator-tournament:" + content_hash(payload)
    edge = Hyperedge(
        "support:" + atom_id,
        (source_id,),
        (atom_id,),
        "SUPPORT",
        warrant=warrant,
    )
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=E.SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )

    if revoke:
        runtime.revoke((training_evidence,))
    runtime.persist()
    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if revoke:
        if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
            raise RuntimeError("revoked selected method remained live")
        return M.GeneratorMethod(), atom_id, training_evidence, utility_evidence

    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("selected OCM method did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("selected OCM method content identity mismatch")
    loaded = M.GeneratorMethod(
        tuple(tuple(fragment) for fragment in stored["fragments"]),
        tuple(stored["training_tasks"]),
    )
    if loaded.fingerprint != stored["fingerprint"]:
        raise RuntimeError("selected OCM method fingerprint mismatch")
    return loaded, atom_id, training_evidence, utility_evidence


# Change only the research adapter. The frozen E.run() resolves this global at call time.
E.admit_selected_method = connected_admit_selected_method

# Re-export for protocol tests.
admit_selected_method = connected_admit_selected_method


def run():
    return E.run()


def main():
    # Reuse the frozen CLI/output path and terminal reporting.
    E.admit_selected_method = connected_admit_selected_method
    E.main()


if __name__ == "__main__":
    main()
