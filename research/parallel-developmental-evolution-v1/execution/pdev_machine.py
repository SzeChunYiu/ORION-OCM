"""PDEV canonical serial lineage: GenerationSnapshotV1 + real M11 adoption.

The canonical lineage is ONE serial cell (issue #217 §3).  All parallel search
happens outside it; a generation transition happens only when this cell runs
the full M11 path -- proposal, shadow-evaluate, assurance, EXTERNAL adoption --
and the external authority is the frozen MODEL PROXY decision
(``HUMAN_GATE_BYPASSED__MODEL_PROXY``), never the search itself.

The cell reuses the pinned #149 ``evolution.EvolutionCell`` unchanged
(vendored, byte-identical), driven by:

* ``initial_config``  the #149 canonical g2 machine mapped into the morphology
  grammar (route_s=s3 signature_hash_parent -> feature/prefix9 with no
  discovery and no re-index; route_d=d1 lazy_learner -> lazy);
* ``allowed_edits``   the grammar's registered dimensions/values;
* ``runner``          ``pdev_runner.runner`` (the frozen external meter);
* ``edit_classes``    per-dimension legal change classes from the grammar.

The g2 mapping is recorded as a MORPHOLOGY-LEVEL mapping of the parent's
route vocabulary, not a byte-level re-execution of the parent's adapter; both
statements appear in every snapshot.

Python 3.8+ stdlib only (plus the vendored cell + ``ocm`` package at runtime).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

HERE = Path(__file__).resolve().parent
for entry in (HERE / "vendor" / "pinned", HERE, HERE.parent):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import pdev_grammar as G  # noqa: E402
import pdev_runner as R  # noqa: E402

SNAPSHOT_SCHEMA = "pdev217.generation_snapshot.v1"

#: The #149 canonical g2 machine (pinned run_v1_machine.json: route_s=s3,
#: route_d=d1) mapped into the morphology grammar.  This is the incumbent the
#: whole programme starts from: the lineage CONTINUES from g2.
G2_MORPHOLOGY: Dict[str, Any] = dict(G.INCUMBENT_G0)

#: The donor's initial machine (s0 discovering_arm / d0 learned arm) -- the
#: RESET control's starting morphology.
RESET_MORPHOLOGY: Dict[str, Any] = {
    "s_unit": "feature", "s_feature": "prefix9", "s_choose": True,
    "s_reindex": True, "s_bucket": 4, "s_growth": 1, "s_composite": "none",
    "d_unit": "learned", "d_composite": "none",
}

G2_MAPPING_RECEIPT = {
    "parent_run": "research/self-evolution-v1 pinned run_v1_machine.json "
                  "(vendored, origin_commit f0cc17c)",
    "parent_final_config": {"route_s": "s3", "route_d": "d1"},
    "parent_trajectory": ["g0", "g1", "g2", "g2"],
    "parent_terminal": "AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION",
    "mapping": {"route_s=s3 (signature_hash_parent)":
                "s_unit=feature, s_feature=prefix9, s_choose=False, "
                "s_reindex=False",
                "route_d=d1 (lazy_learner_arm)": "d_unit=lazy"},
    "mapping_status": "MORPHOLOGY_LEVEL_MAP (route vocabulary -> grammar); "
                      "not a byte-level re-execution of the parent adapter",
    "honest_ceiling": "g3 is NOT assumed; it is earned only by a fully "
                      "adopted PDEV transition",
}


def _edit_classes() -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for dim in G.UNION_WRITE_SET:
        classes = {cls for cls, ws in G.LEGAL_WRITE_SET.items() if dim in ws}
        classes.add("C5")  # organizational composition may reorganize units
        out[dim] = sorted(classes)
    return out


class ProxyDecisionMissing(Exception):
    """Fail-closed: no frozen external decision -> no adoption."""


#: Frozen resource budgets for one canonical develop cycle.  Justified ONLY by
#: the parent's pinned g2 run (run_v1_summary.json: measured cycle work 270274,
#: peak persistent_bytes 22943) scaled by ~10x headroom; set before any PDEV
#: candidate was measured.
DEFAULT_BUDGETS: Dict[str, int] = {"work": 4_000_000, "persistent_bytes": 400_000}

#: PDEV arm origin -> the M11 Origin enum's legal members (strict enum).  The
#: true arm name and its mechanism always travel in ``origin_ref``.
#: Arm mechanism -> ``Origin`` enum VALUE (lowercase; ``Origin`` is a str
#: Enum keyed by value, so ``Origin("HUMAN")`` would raise).
ORIGIN_MAP: Dict[str, str] = {
    "quality_diversity": "recombination",
    "search": "human",
    "automl_variant": "learned",
    "evolutionary": "recombination",
    "program_repair": "human",
    "reflection_retry": "human",
    "human": "human",
    "incumbent_control": "human",
    "existing_alternative": "existing_alternative",
    "ocm_composition": "human",
    "ocm_representation": "human",
    "ocm_index": "human",
    "ocm_acquisition": "human",
    "ocm_resource": "human",
    "donor_transfer": "transfer",
    "learned_policy": "learned",
}


def build_protocol(budgets: Optional[Mapping[str, int]] = None,
                   probe_limit: int = 6,
                   quality_margin: float = 0.0) -> Dict[str, Any]:
    budgets = dict(budgets) if budgets else dict(DEFAULT_BUDGETS)
    return {
        "resource_keys": list(R.RESOURCE_KEYS),
        "budgets": budgets,
        "probe_limit": probe_limit,
        "proposal_budget": 100,
        "adoption_budget": 100,
        "quality_margin": quality_margin,
        "edit_classes": _edit_classes(),
        "resource_aggregation": {"work": "sum", "persistent_bytes": "max"},
    }


class GovernedProxyAdopter:
    """External adoption authority replaced by its strongest legitimate model
    proxy: a fresh-context model decision recorded BEFORE the cell runs, over
    ONLY the frozen adoption packet.  Fail-closed on any mismatch."""

    def __init__(self, decision_path: str):
        self.decision_path = Path(decision_path)

    def decide(self, proposal, assurance):  # ocm ExternalAdopter interface
        from ocm.selfmodel.govern import AdoptionDecision
        if not self.decision_path.exists():
            raise ProxyDecisionMissing(
                "no frozen external decision at %s" % self.decision_path)
        payload = json.loads(self.decision_path.read_text())
        if payload.get("schema") != "pdev217.proxy_decision.v1":
            raise ProxyDecisionMissing("unknown decision schema")
        if payload.get("gate") != "HUMAN_GATE_BYPASSED__MODEL_PROXY":
            raise ProxyDecisionMissing("decision is not a labelled model proxy")
        if payload.get("proposal_fingerprint") not in (None, proposal.fingerprint()):
            raise ProxyDecisionMissing(
                "decision fingerprint %r does not match proposal %s"
                % (payload.get("proposal_fingerprint"), proposal.fingerprint()))
        approved = bool(payload.get("approved"))
        reason = str(payload.get("reason", "model-proxy decision on frozen packet"))
        token = "HUMAN_GATE_BYPASSED__MODEL_PROXY:" + hashlib.sha256(
            self.decision_path.read_bytes()).hexdigest()[:12]
        return AdoptionDecision(proposal.fingerprint(), approved, reason, token)


class PDEVLineage:
    """The one serial canonical cell plus its snapshot writer."""

    def __init__(self, root: str, budgets: Mapping[str, int],
                 mode: str = "CONTINUED"):
        from evolution import EvolutionCell
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        initial = G2_MORPHOLOGY if mode == "CONTINUED" else RESET_MORPHOLOGY
        allowed = {name: list(values) for name, values in G.DIMENSIONS}
        self.protocol = build_protocol(budgets)
        self.cell = EvolutionCell(self.root, initial, allowed_edits=allowed,
                                  protocol=self.protocol)
        self.mode = mode
        self.snapshot_dir = self.root / "snapshots"
        self.snapshot_dir.mkdir(exist_ok=True)

    # -- snapshot ---------------------------------------------------------

    def snapshot(self, generation_label: str, cycle: int,
                 extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        state = self.cell.state
        snap = {
            "schema": SNAPSHOT_SCHEMA,
            "mode": self.mode,
            "generation_label": generation_label,
            "cycle_index": cycle,
            "generation": state["generation"],
            "adoptions": list(state["adoptions"]),
            "rolled_back": list(state.get("rolled_back", [])),
            "config": state["config"],
            "config_digest": G.digest(state["config"]),
            "protocol_hash": state["protocol_hash"],
            "machine_sha256": hashlib.sha256(
                (self.root / "machine.json").read_bytes()).hexdigest(),
            "g2_mapping": G2_MAPPING_RECEIPT,
            "vendor_manifest_sha256": _vendor_sha(),
            "extra": dict(extra or {}),
        }
        snap["snapshot_sha256"] = hashlib.sha256(json.dumps(
            snap, sort_keys=True).encode()).hexdigest()
        path = self.snapshot_dir / ("gen_%s_cycle_%d.json"
                                    % (generation_label, cycle))
        path.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n")
        return snap

    # -- the one serial development cycle ----------------------------------

    def develop(self, winner: Mapping[str, Any], dev_tasks, shadow_suites,
                decision_path: str,
                obstruction: Optional[Mapping[str, Any]] = None
                ) -> Dict[str, Any]:
        """Run the M11 path for ONE generation-boundary candidate (or a small
        ranked library).  The winner record comes from the centre's frozen
        PDEV-8 selection; the cell independently re-measures it."""
        from evolution import Candidate
        origin = ORIGIN_MAP.get(str(winner.get("origin", "human")), "human")
        # ``edits`` is the DELTA against the cell's current config, not the
        # whole configuration: apply_candidate checks the declared class
        # against EVERY key it is asked to write, and rewriting an unchanged
        # C4-only dimension under a C3 declaration is illegal (rightly so --
        # the candidate never claimed to touch it).
        parent = self.cell.config
        edits = {key: value for key, value in winner["config"].items()
                 if parent.get(key) != value}
        if not edits:
            raise ValueError("winner is a structural no-op of the incumbent")
        candidates = [Candidate(
            candidate_id=str(winner["candidate_id"]),
            change_class=str(winner["change_class"]),
            target_component="morphology.configuration",
            edits=edits,
            origin=origin,
            origin_ref="pdev217 wave search; arm=%s; mechanism=%s"
                        % (winner.get("arm", "?"), winner.get("origin", "?")),
        )]
        certificate, registry = self._obstruction_certificate(winner,
                                                              obstruction)
        adopter = GovernedProxyAdopter(decision_path)
        entry = self.cell.develop(
            {"ecology": "development",
             "failure_id": "pdev-gen-%d" % self.cell.generation,
             "observed": "generation-boundary selection event",
             "resources": {}},
            candidates,
            dev_tasks=dev_tasks,
            shadow_suites=shadow_suites,
            runner=R.runner,
            external_adopter=adopter,
            certificate=certificate,
            registry=registry,
        )
        return entry

    # -- M11 obstruction certificate (escalation justification) ------------

    #: Mirrors of the vendored cell's layer machinery (kept literal so this
    #: module carries its own declaration of what it depends on).
    _CLASS_LAYER = {"C0": "D0", "C1": "D1", "C2": "D2", "C3": "D3",
                    "C4": "D6", "C5": "D7"}
    _LAYER_ORDER = ["D0", "D1", "D2", "D5", "D6", "D3", "D4", "D7", "D8"]
    _LOCAL = {"D0", "D1", "D2", "D5", "D6"}
    #: Layers the grammar's change classes can produce.
    _REPRESENTABLE = ("D2", "D6", "D3", "D7")

    def _obstruction_certificate(self, winner, obstruction):
        """Build the M11 escalation record for a non-local-layer winner.

        Honest material only: the registered alternatives are THIS WAVE's
        measured lower-layer candidates (centre-measured, charged), their
        warrants are the wave's measurement provenance (nothing revoked, so
        every warrant is LIVE), and the ceiling evidence is admitted into the
        cell's runtime as IMPORTED evidence BEFORE the cell runs, so the M11
        gate checks it LIVE in ``runtime.state.evidence.records``.  ``succeeded``
        carries the centre's own verdict: a lower-layer alternative that both
        dominates the incumbent and is finally admissible is a successful
        narrower repair and honestly INVALIDATES the certificate (escalation
        is then unjustified and the cell must refuse).
        """
        layer = self._CLASS_LAYER.get(str(winner.get("change_class")))
        if layer is None or layer in self._LOCAL:
            return None, None  # local-layer repair: no escalation certificate
        from ocm.selfmodel.diagnose import Attempt, ObstructionCertificate
        from ocm.selfmodel.model import Layer
        from ocm.kso.warrant import WarrantProfile
        from ocm.store.evidence import Channel

        alts = list((obstruction or {}).get("alternatives", []))
        below = [code for code in self._LAYER_ORDER
                 if self._LAYER_ORDER.index(code) < self._LAYER_ORDER.index(layer)
                 and code in self._REPRESENTABLE]
        incumbent_layer = Layer(below[-1] if below else "D2")

        attempts = []
        ceiling_payloads = []
        for alt in alts:
            token = "pdev217:%s" % alt["candidate_id"]
            attempts.append(Attempt(
                alternative_id=str(alt["candidate_id"]),
                layer=Layer(str(alt.get("layer", "D2"))),
                warrant=WarrantProfile.of(frozenset([token])),
                succeeded=bool(alt.get("dominates_incumbent")
                               and alt.get("admissible"))))
            ceiling_payloads.append({
                "kind": "lower-layer-alternative-measurement",
                "candidate_id": alt["candidate_id"],
                "layer": alt.get("layer"), "arm": alt.get("arm"),
                "vector": alt.get("vector"),
                "dominates_incumbent": bool(alt.get("dominates_incumbent")),
                "admissible": bool(alt.get("admissible"))})
        ceiling_payloads.append({
            "kind": "escalation-baseline",
            "winner": winner.get("candidate_id"),
            "winner_layer": layer,
            "incumbent_vector": (obstruction or {}).get("incumbent_vector"),
            "winner_vector": (obstruction or {}).get("winner_vector"),
            "wave_measured": (obstruction or {}).get("wave_measured")})
        eids = []
        for payload in ceiling_payloads:
            _, eid = self.cell.runtime.admit_evidence(
                payload, Channel.IMPORTED, "pdev217.wave-measurement.v1")
            eids.append(eid)
        ids = tuple(str(alt["candidate_id"]) for alt in alts)
        certificate = ObstructionCertificate(
            incumbent_layer=incumbent_layer,
            failed_obligation="generation-boundary improvement obligation: "
                              "dominate the incumbent (failures, work, "
                              "persistent_bytes) on the frozen dev suite",
            registered_alternatives=ids,
            attempts=tuple(attempts),
            resource_envelope={
                "wave_measured": (obstruction or {}).get("wave_measured", 0),
                "registered_alternatives": len(ids)},
            ceiling_evidence=tuple(eids),
            narrower_insufficient_because=(
                "every lower-layer alternative measured in this wave failed "
                "the obligation or was inadmissible; warrants are the wave's "
                "charged measurements (LIVE)"),
        )
        registry = {incumbent_layer: ids}
        return certificate, registry

    # -- PDEV-9 receipts ----------------------------------------------------

    def cold_restart_check(self) -> Dict[str, Any]:
        """Destroy the in-memory cell; reopen from disk; verify identity."""
        from evolution import EvolutionCell
        expected = (self.cell.generation, G.digest(self.cell.config),
                    self.cell.state["protocol_hash"])
        allowed = {name: list(values) for name, values in G.DIMENSIONS}
        reopened = EvolutionCell(self.root, G2_MORPHOLOGY if self.mode == "CONTINUED"
                                 else RESET_MORPHOLOGY,
                                 allowed_edits=allowed, protocol=self.protocol)
        observed = (reopened.generation, G.digest(reopened.config),
                    reopened.state["protocol_hash"])
        return {"schema": "pdev217.cold_restart.v1", "mode": self.mode,
                "expected": list(expected), "observed": list(observed),
                "exact": expected == observed}

    def rollback_counterfactual(self) -> Dict[str, Any]:
        """Clone the cell directory, adopt nothing new there, but exercise the
        M11 exact rollback of the latest adoption in the clone to prove the
        restoration path exists and is exact."""
        clone = Path(str(self.root) + "_rollback_cf")
        if clone.exists():
            shutil.rmtree(clone)
        shutil.copytree(self.root, clone)
        from evolution import EvolutionCell
        allowed = {name: list(values) for name, values in G.DIMENSIONS}
        clone_cell = EvolutionCell(clone, G2_MORPHOLOGY
                                  if self.mode == "CONTINUED" else RESET_MORPHOLOGY,
                                  allowed_edits=allowed, protocol=self.protocol)
        if not clone_cell.state["adoptions"]:
            receipt = {"schema": "pdev217.rollback_counterfactual.v1",
                       "mode": self.mode, "exercised": False,
                       "reason": "no live adoption in this lineage yet"}
            (self.root / "rollback_counterfactual.json").write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            return receipt
        before = G.digest(clone_cell.config)
        result = clone_cell.rollback_latest()
        after = G.digest(clone_cell.config)
        receipt = {"schema": "pdev217.rollback_counterfactual.v1",
                   "mode": self.mode, "exercised": True,
                   "config_digest_before": before,
                   "config_digest_after": after,
                   "m11_exact": bool(result["exact"]),
                   "generation_after_rollback": result["generation"]}
        (self.root / "rollback_counterfactual.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        return receipt


def _vendor_sha() -> str:
    manifest = HERE / "vendor" / "VENDOR_MANIFEST.json"
    if not manifest.exists():
        return ""
    return hashlib.sha256(manifest.read_bytes()).hexdigest()
