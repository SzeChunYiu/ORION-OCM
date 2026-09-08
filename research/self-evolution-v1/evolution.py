"""Bounded DEVELOPMENT-only cognitive change orchestration over real M11 APIs.

The host supplies task runners, a finite declarative candidate library and external
adoption authority. This is library search, not autonomous mechanism invention.
No result from a protected ecology is an admissible input. Unknown responsibility
layers remain unknown; successful interventions identify tested sufficiency only.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.event import EventStatus, EventType
from ocm.store.evidence import Channel
from ocm.selfmodel.diagnose import LOCAL, ORDER, ObstructionCertificate, diagnose
from ocm.selfmodel.govern import (AdoptionLedger, Assurance, ExternalAdopter, Meter,
                                 assure, register_prediction, shadow_evaluate)
from ocm.selfmodel.model import AblationEvidence, FailureRecord, Layer, SelfModel
from ocm.selfmodel.proposal import (CLASS_ORDER, ChangeClass, Origin, Prediction,
                                   PROTECTED_TARGETS, PROTECTED_TOKENS,
                                   SelfChangeProposal, touches_protected_target)


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def plain(value: Any) -> Any:
    return json.loads(json.dumps(value, allow_nan=False))


CLASS_LAYER = {"C0": "D0", "C1": "D1", "C2": "D2", "C3": "D3",
               "C4": "D6", "C5": "D7"}


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    change_class: str
    target_component: str
    edits: Mapping[str, Any]
    origin: str = "human"
    origin_ref: str = "host-supplied finite library; prior-art lineage must be specified separately"

    @property
    def layer(self) -> Layer:
        return Layer(CLASS_LAYER[self.change_class])


Runner = Callable[[dict[str, Any], Sequence[Mapping[str, Any]]], dict[str, Any]]


class EvolutionCell:
    """Persisted finite candidate search with externally governed M11 adoption.

    Protocol keys: resource_keys (required measured vector), budgets (same keys),
    probe_limit, proposal_budget, adoption_budget; quality_margin defaults to 0.
    Optional edit_classes maps config keys to allowed C0..C5 classes. All values
    and task/config identities are frozen by the host before this cell executes.
    """

    def __init__(self, root: str | Path, initial_config: Mapping[str, Any], *,
                 allowed_edits: Mapping[str, Sequence[Any]], protocol: Mapping[str, Any]):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.protocol = plain(protocol)
        self.allowed_edits = plain(allowed_edits)
        self.protocol_hash = digest({"protocol": self.protocol,
                                     "allowed_edits": self.allowed_edits})
        self.resource_keys = tuple(self.protocol.get("resource_keys", ()))
        if not self.resource_keys or set(self.resource_keys) != set(self.protocol.get("budgets", {})):
            raise ValueError("register a nonempty resource vector and all budget dimensions")
        for value in self.protocol["budgets"].values():
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError("invalid resource budget")
        margin = self.protocol.get("quality_margin", 0)
        if type(margin) not in (int, float) or not math.isfinite(margin) or not 0 <= margin <= 1:
            raise ValueError("quality margin must be registered in [0, 1]")
        self.runtime = OCMRuntime(self.root / "m11")
        self.self_model = SelfModel(self.runtime)
        self.ledger = AdoptionLedger.load(self.runtime, meter=Meter(
            budget=self.protocol.get("proposal_budget", 100)))
        self.ledger.window_budget = self.protocol.get("adoption_budget", 100)
        self.path = self.root / "machine.json"
        if self.path.exists():
            envelope = json.loads(self.path.read_text())
            if digest(envelope["machine"]) != envelope["sha256"]:
                raise ValueError("machine snapshot digest mismatch")
            self.state = envelope["machine"]
            if self.state["protocol_hash"] != self.protocol_hash:
                raise ValueError("protocol or candidate edit space changed across restart")
            installations = [event.payload.get("payload", {}).get("machine_sha256")
                             for event in self.runtime.events
                             if event.event_type is EventType.EVIDENCE_ADMITTED
                             and event.status is EventStatus.PASS
                             and event.payload.get("source") == "host-machine-installation.v1"]
            if not installations or installations[-1] != envelope["sha256"]:
                raise ValueError("machine snapshot does not match latest durable M11 installation receipt")
            if self.state["generation"] != len(self.state["adoptions"]):
                raise ValueError("generation does not match admission history")
            history = self.ledger.adoption_history
            if any(fp not in history for fp in self.state["adoptions"]):
                raise ValueError("snapshot claims an admission absent from M11")
            if set(history) != set(self.state["adoptions"]) | set(self.state.get("rolled_back", ())):
                raise ValueError("incomplete host installation: M11/snapshot diverge")
        else:
            if self.ledger.adoption_history:
                raise ValueError("existing M11 history without machine snapshot")
            self.state = {"schema": "ocm.self_evolution.machine.v1", "generation": 0,
                          "config": plain(initial_config), "protocol_hash": self.protocol_hash,
                          "components": {}, "history": [], "seen_tasks": [],
                          "seen_semantic_ids": [],
                          "adoptions": [], "rolled_back": [], "cache": {}, "freeze": None}
            self._save()

    @property
    def config(self) -> dict[str, Any]:
        return copy.deepcopy(self.state["config"])

    @property
    def generation(self) -> int:
        return self.state["generation"]

    def _save(self) -> None:
        payload = {"machine": self.state, "sha256": digest(self.state)}
        # Bind installed configuration/history/freeze to the external runtime's
        # durable event chain, not merely a recomputable adjacent JSON checksum.
        self.runtime.admit_evidence({"machine_sha256": payload["sha256"],
                                    "generation": self.generation},
                                   Channel.IMPORTED, "host-machine-installation.v1")
        self.runtime.persist()
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        temporary.replace(self.path)

    def apply_candidate(self, config: Mapping[str, Any], candidate: Candidate) -> dict[str, Any]:
        """A fixed data dispatcher: no eval, imports, source edits or callbacks in edits."""
        if candidate.change_class not in CLASS_LAYER:
            raise ValueError("only C0-C5 cognition is replaceable")
        Origin(candidate.origin)
        if not candidate.edits or not candidate.origin_ref:
            raise ValueError("candidate needs edits and provenance")
        # Reject protected writes BEFORE experimental execution, not just adoption.
        if any(candidate.target_component.startswith(prefix) for prefix in PROTECTED_TARGETS):
            raise PermissionError("candidate targets protected authority/evaluation")
        def strings(value):
            if isinstance(value, Mapping):
                for key, child in value.items():
                    yield str(key)
                    yield from strings(child)
            elif isinstance(value, (tuple, list)):
                for child in value:
                    yield from strings(child)
            elif isinstance(value, str):
                yield value
        if any(token in text.lower() for text in strings(candidate.edits) for token in PROTECTED_TOKENS):
            raise PermissionError("candidate contains protected write tokens")
        result = plain(config)
        for key, value in candidate.edits.items():
            if key not in self.allowed_edits or value not in self.allowed_edits[key]:
                raise ValueError("candidate edits outside registered finite dispatcher")
            classes = self.protocol.get("edit_classes", {}).get(key)
            if classes is not None and candidate.change_class not in classes:
                raise ValueError("declared change class mismatches registered edit class")
            result[key] = plain(value)
        return result

    def _measure(self, runner: Runner, config: dict[str, Any], tasks: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        start = time.perf_counter_ns()
        result = plain(runner(copy.deepcopy(config), copy.deepcopy(tasks)))
        result["host_elapsed_ns"] = time.perf_counter_ns() - start
        if (type(result.get("n")) is not int or result["n"] != len(tasks) or not tasks
                or type(result.get("success")) is not int
                or not 0 <= result["success"] <= result["n"]):
            raise ValueError("runner must return one measured result per supplied task")
        if type(result.get("preservation_violations")) is not int or result["preservation_violations"] < 0:
            raise ValueError("runner must explicitly measure preservation violations")
        for key in self.resource_keys:
            value = result.get("resources", {}).get(key)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError("missing/nonfinite measured resource dimension: " + key)
        return result

    def _dominates(self, challenger: Mapping[str, Any], incumbent: Mapping[str, Any]) -> bool:
        """Registered vector Pareto improvement with quality noninferiority."""
        if challenger["preservation_violations"] or incumbent["n"] != challenger["n"]:
            return False
        margin = self.protocol.get("quality_margin", 0)
        if challenger["success"] < incumbent["success"] - margin * incumbent["n"]:
            return False
        if not all(challenger["resources"][k] <= incumbent["resources"][k] for k in self.resource_keys):
            return False
        return (challenger["success"] > incumbent["success"] or
                any(challenger["resources"][k] < incumbent["resources"][k] for k in self.resource_keys))

    def _task_ids(self, tasks: Sequence[Mapping[str, Any]]) -> list[str]:
        ids = []
        for task in tasks:
            if task.get("ecology") != "development" or not isinstance(task.get("task_id"), str):
                raise ValueError("only explicitly development-scoped, identified tasks accepted")
            if not isinstance(task.get("semantic_id"), str) or not task["semantic_id"]:
                raise ValueError("host must supply a stable semantic_id for each actual task contract")
            ids.append(task["task_id"])
        return ids

    def develop(self, observation: Mapping[str, Any], candidates: Sequence[Candidate], *,
                dev_tasks: Sequence[Mapping[str, Any]],
                shadow_suites: Mapping[str, Sequence[Mapping[str, Any]]], runner: Runner,
                external_adopter: ExternalAdopter,
                certificate: ObstructionCertificate | None = None,
                registry: Mapping[Layer, Sequence[str]] | None = None) -> dict[str, Any]:
        """One diagnosis/proposal cycle; zero or one actual generation increments.

        Shadow suites are disjoint DEVELOPMENT samples, never protected tests.
        Failure observations must omit human diagnosis/repair labels. The caller
        is responsible for semantic blinding; this API also rejects named leaks.
        """
        if self.state["freeze"] is not None:
            raise PermissionError("frozen generation cannot ingest further outcomes")
        if observation.get("ecology") != "development":
            raise PermissionError("protected results cannot enter self-evolution")
        if {"human_diagnosis", "oracle_layer", "expected_repair", "true_layer"} & observation.keys():
            raise ValueError("diagnosis labels must be blinded at intake")
        # Frozen dataclasses do not freeze nested mappings. Detach the entire
        # library before invoking any host runner, so aliases held by that runner
        # cannot change the edit that a later proposal will install.
        candidates = tuple(Candidate(**plain(asdict(candidate))) for candidate in candidates)
        dev_ids = self._task_ids(dev_tasks)
        shadow_ids = [i for tasks in shadow_suites.values() for i in self._task_ids(tasks)]
        all_ids = dev_ids + shadow_ids
        semantic_ids = [task["semantic_id"] for task in dev_tasks] + [
            task["semantic_id"] for tasks in shadow_suites.values() for task in tasks]
        if not dev_ids or "target" not in shadow_suites or not shadow_ids:
            raise ValueError("nonempty development and target shadow suites required")
        if len(set(all_ids)) != len(all_ids) or set(all_ids) & set(self.state["seen_tasks"]):
            raise ValueError("development experiences and shadow tasks must be disjoint across cycles")
        if (len(set(semantic_ids)) != len(semantic_ids)
                or set(semantic_ids) & set(self.state["seen_semantic_ids"])):
            raise ValueError("semantic task overlap across development/shadow/cycles")
        if len({c.candidate_id for c in candidates}) != len(candidates):
            raise ValueError("candidate identifiers must be unique")
        # Intake becomes irrevocable exposure even if a later runner fails.
        self.state["seen_tasks"].extend(all_ids)
        self.state["seen_semantic_ids"].extend(semantic_ids)
        self._save()
        trace_eid = self.self_model.record("actual-trace:" + digest(observation), plain(observation))
        failure = FailureRecord(str(observation.get("failure_id", digest(observation))),
            str(observation.get("task_id", dev_ids[0])), str(observation.get("environment", "cognitive-ladder")),
            str(observation.get("observed", "recorded failure/opportunity")),
            str(observation.get("expected", "registered machine-quality contract")),
            (trace_eid,), tuple(Layer), (), plain(observation.get("resources", {})),
            "LIVE" if observation.get("uncertainty") == "LIVE" else "UNKNOWN",
            "registered", len(dev_ids), "development")
        failure_eid = self.self_model.ingest_failure(failure)
        entry = {"cycle": len(self.state["history"]), "generation_before": self.generation,
                 "ecology": "development", "failure": asdict(failure),
                 "source_observation": plain(observation),
                 "initial_diagnosis": asdict(diagnose(failure)), "probes": [],
                 "origin_claim": "finite host library search; no autonomous invention",
                 "dev_task_ids": dev_ids, "shadow_task_ids": shadow_ids,
                 "semantic_ids": semantic_ids,
                 "registered_candidate_library": [asdict(c) for c in candidates],
                 "protocol_hash": self.protocol_hash}
        baseline = self._measure(runner, self.config, dev_tasks)
        entry["incumbent_development"] = baseline
        baseline_eid = self.self_model.record("actual-baseline:" + digest({"tasks": dev_ids, "result": baseline}),
            {"task_ids": dev_ids, "semantic_ids": semantic_ids[:len(dev_ids)], "result": baseline,
             "provenance": "new development execution; not recovered historical trace"})
        # The original summary retains UNKNOWN unless its source explicitly
        # warranted LIVE. New measured probes support a separate scoped record.
        failure = replace(failure, observed=json.dumps(baseline, sort_keys=True),
                          trace_ids=(trace_eid, baseline_eid), uncertainty="LIVE")
        failure_eid = self.self_model.ingest_failure(failure)
        entry["measured_failure"] = asdict(failure)
        # Cheap general discriminating intervention: test lower change classes
        # first, exhaust that class, then rank measured successful interventions.
        # This is ordered finite search, not Bayesian causal identification.
        ordered = sorted(candidates, key=lambda c: (CLASS_ORDER.index(ChangeClass(c.change_class)),
                                                    digest(asdict(c))))
        ablations = []
        eligible = []
        successful_class = None
        for candidate in ordered[:self.protocol.get("probe_limit", len(ordered))]:
            rank = CLASS_ORDER.index(ChangeClass(candidate.change_class))
            if successful_class is not None and rank > successful_class:
                break
            changed = self.apply_candidate(self.config, candidate)
            if changed == self.config:
                continue
            measured = self._measure(runner, changed, dev_tasks)
            works = self._dominates(measured, baseline)
            probe = {"candidate": asdict(candidate), "measurement": measured, "restored_contract": works}
            eid = self.self_model.record("probe:" + digest(probe), probe, derived_from=(failure_eid,))
            entry["probes"].append(probe)
            ablations.append(AblationEvidence(candidate.candidate_id, candidate.layer, works, eid))
            if works:
                eligible.append((candidate, measured))
                successful_class = rank
        failure = replace(failure, ablations=tuple(ablations))
        self.self_model.ingest_failure(failure)
        diagnosis = diagnose(failure, certificate=certificate, registry=registry)
        entry["diagnosis"] = asdict(diagnosis)
        entry["diagnosis_ceiling"] = "lowest successful TESTED registered intervention; untested layers UNKNOWN"
        if not eligible:
            entry["terminal"] = "SELF_DIAGNOSIS_NOT_IDENTIFIABLE"
            return self._finish(entry)
        candidate, measured = min(eligible, key=lambda pair: (
            -pair[1]["success"], tuple(pair[1]["resources"][k] for k in self.resource_keys),
            digest(asdict(pair[0]))))
        if candidate.layer not in LOCAL:
            lower_ids = {c.candidate_id for c in candidates if ORDER.index(c.layer) < ORDER.index(candidate.layer)}
            attempted = {a.change for a in ablations if not a.task_succeeded}
            live_witness = (certificate is not None and registry is not None and certificate.valid(registry)
                            and lower_ids <= attempted
                            and bool(certificate.ceiling_evidence)
                            and all(e in self.runtime.state.evidence.records
                                    and self.runtime.state.evidence.liveness([e]).value == "LIVE"
                                    for e in certificate.ceiling_evidence))
            if not live_witness:
                entry["terminal"] = "CANNOT_CHECK_OBSTRUCTION"
                return self._finish(entry)
        preserved = tuple(shadow_suites)
        deltas = {k: (measured["resources"][k] - baseline["resources"][k]) / baseline["n"]
                  for k in self.resource_keys}
        prediction = Prediction(("target",) if measured["success"] > baseline["success"] else (),
                                (), deltas, preserved, (),
                                ("development effect may fail on disjoint shadow tasks",),
                                self.protocol.get("quality_margin", 0))
        component = candidate.target_component
        self.state["components"].setdefault(component, {"artifact": digest(self.config)})
        incumbent_config_hash = digest(self.config)
        proposed_config = self.apply_candidate(self.config, candidate)
        proposed_config_json = json.dumps(proposed_config, sort_keys=True, allow_nan=False)
        proposed_config_hash = digest(proposed_config)
        def install_frozen_config(artifact):
            if digest(artifact) != incumbent_config_hash:
                raise ValueError("proposal applied to an unregistered incumbent config")
            return json.loads(proposed_config_json)
        proposal = SelfChangeProposal("cycle-" + str(entry["cycle"]) + ":" + candidate.candidate_id,
            "1", tuple(a.evidence_id for a in ablations) + (failure_eid,), component,
            candidate.layer.value, self.state["components"][component]["artifact"],
            ChangeClass(candidate.change_class), plain(candidate.edits),
            install_frozen_config, prediction,
            preserved, (), "target", "M11 exact data rollback; reopen all method cache", "development",
            "this-cycle", Origin(candidate.origin), candidate.origin_ref, tuple(dev_ids))
        if touches_protected_target(proposal):
            raise PermissionError("registered candidate reaches protected constitution")
        self.ledger.propose(proposal)
        receipt = register_prediction(self.runtime, proposal)
        entry["prediction"] = asdict(prediction)
        entry["prediction_receipt"] = asdict(receipt)
        entry["proposal"] = {"fingerprint": proposal.fingerprint(), "candidate": asdict(candidate),
                             "incumbent_config_hash": incumbent_config_hash,
                             "proposed_config_hash": proposed_config_hash}
        # Persist prediction before any independent shadow runner call.
        self.runtime.persist()
        shadow = shadow_evaluate(self.runtime, self.config, proposal,
            lambda config, tasks: self._measure(runner, config, tasks), shadow_suites)
        assurance = assure(proposal, shadow, protocol_hash=self.protocol_hash,
            frozen_protocol_hash=self.state["protocol_hash"], budget=self.protocol["budgets"],
            rollback_exists=True, prediction_receipt=receipt, runtime=self.runtime,
            held_out_task_ids=shadow_ids)
        checks = dict(assurance.checks)
        checks["external_resource_frontier"] = self._dominates(shadow.challenger["target"], shadow.incumbent["target"])
        checks["external_preservation"] = all(r["preservation_violations"] == 0 for r in shadow.challenger.values())
        checks["external_all_suite_resources"] = all(
            row["resources"][k] <= self.protocol["budgets"][k]
            for row in shadow.challenger.values() for k in self.resource_keys)
        checks["external_preservation_resource_noninferiority"] = all(
            shadow.challenger[name]["resources"][k] <= shadow.incumbent[name]["resources"][k]
            for name in shadow_suites for k in self.resource_keys)
        assurance = Assurance(all(checks.values()), checks, tuple(k for k, v in checks.items() if not v))
        decision = external_adopter.decide(proposal, assurance)
        entry.update(shadow=asdict(shadow), assurance=asdict(assurance), external_decision=asdict(decision))
        entry["resource_prediction_calibration"] = {
            k: {"predicted_delta_per_task": deltas[k],
                "observed_delta_per_task": (shadow.challenger["target"]["resources"][k]
                    - shadow.incumbent["target"]["resources"][k]) / shadow.incumbent["target"]["n"],
                "signed_error": (shadow.challenger["target"]["resources"][k]
                    - shadow.incumbent["target"]["resources"][k]) / shadow.incumbent["target"]["n"] - deltas[k]}
            for k in self.resource_keys}
        # Even a permissive external policy cannot bypass this lane's contract.
        if not assurance.passed or not decision.approved:
            entry["terminal"] = "SELF_EVOLUTION_REGRESSES" if not assurance.passed else "EXTERNAL_ADOPTION_REJECTED"
            return self._finish(entry)
        challenger, migration = self.ledger.adopt(proposal, decision, self.config,
                                                 self.state["components"], cache=self.state["cache"])
        if digest(challenger) != proposed_config_hash:
            raise ValueError("installed configuration differs from measured shadow challenger")
        self.state["config"] = plain(challenger)
        self.state["components"] = plain(migration["components"])
        # Conservative reopening: no derived method cache survives a config edit.
        reopened_cache_keys = sorted(self.state["cache"])
        self.state["cache"] = {}
        self.state["generation"] += 1
        self.state["adoptions"].append(proposal.fingerprint())
        entry["migration"] = plain(migration)
        entry["reopened_cache_keys"] = reopened_cache_keys
        entry["terminal"] = "DEVELOPMENT_CHANGE_ADOPTED"
        return self._finish(entry)

    def _finish(self, entry: dict[str, Any]) -> dict[str, Any]:
        rows = [entry["incumbent_development"]] + [p["measurement"] for p in entry["probes"]]
        if "shadow" in entry:
            rows += list(entry["shadow"]["incumbent"].values()) + list(entry["shadow"]["challenger"].values())
        aggregation = self.protocol.get("resource_aggregation", {})
        peaks = {k for k in self.resource_keys if aggregation.get(k,
                 "max" if any(token in k.lower() for token in ("storage", "bytes", "memory", "rss")) else "sum") == "max"}
        entry["measured_runner_cost"] = {k: sum(r["resources"][k] for r in rows)
                                         for k in self.resource_keys if k not in peaks}
        entry["peak_runner_resources"] = {k: max(r["resources"][k] for r in rows) for k in peaks}
        entry["runner_elapsed_ns"] = sum(r["host_elapsed_ns"] for r in rows)
        entry["cost_ceiling"] = "declared additive runner counters summed, storage peaks maximized; whole host overhead not fully charged"
        entry["challengers_evaluated"] = len(entry["probes"]) + int("shadow" in entry)
        entry["generation_after"] = self.generation
        self.state["history"].append(plain(entry))
        self._save()
        return plain(entry)

    def rollback_latest(self) -> dict[str, Any]:
        """Host invokes exact M11 rollback; no automatic self-issued authority."""
        if self.state["freeze"] is not None:
            raise PermissionError("protected freeze forbids configuration mutation")
        if not self.state["adoptions"]:
            raise ValueError("no live adoption")
        fp = self.state["adoptions"][-1]
        artifact, components, exact = self.ledger.rollback(fp, cache=self.state["cache"])
        if not exact:
            raise ValueError("M11 rollback failed exact restoration")
        self.state["config"] = plain(artifact)
        self.state["components"] = plain(components)
        self.ledger.acknowledge_rollback_installation(fp, components=components, cache=self.state["cache"])
        self.state["adoptions"].pop()
        self.state["rolled_back"].append(fp)
        self.state["generation"] -= 1
        self._save()
        return {"rolled_back": fp, "exact": exact, "generation": self.generation}

    def freeze_for_protected(self, *, comparator: Mapping[str, Any], budgets: Mapping[str, Any],
                             protected_protocol_hash: str) -> dict[str, Any]:
        """Freeze identities only. Protected execution/intake is deliberately absent."""
        if not protected_protocol_hash or not comparator or not budgets:
            raise ValueError("protected protocol, comparator and budgets must be identified")
        if self.state["freeze"] is not None:
            return copy.deepcopy(self.state["freeze"])
        frozen = {"generation": self.generation, "config_hash": digest(self.config),
                  "self_improvement_history_hash": digest(self.state["history"]),
                  "field_operator_architecture": self.config,
                  "comparator": plain(comparator), "budgets": plain(budgets),
                  "protected_protocol_hash": protected_protocol_hash,
                  "development_protocol_hash": self.protocol_hash}
        frozen["freeze_hash"] = digest(frozen)
        self.state["freeze"] = frozen
        self._save()
        return copy.deepcopy(frozen)
