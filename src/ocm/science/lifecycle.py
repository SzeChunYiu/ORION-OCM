"""Scientific correction / revocation (M10 §12), cross-field method transfer (M10 §13) and the
scientific communication gate (M10 §14).

* `ScienceLedger` runs conclusions on the M2 runtime: observations and verifier outcomes are
  evidence records; a conclusion is admitted *derived* from its supporting evidence (⊗ of distinct
  sources ⊕ …), so retracting E1 reopens exactly the conclusions that rested on it; unrelated
  knowledge stays; replacement support yields a new record with lineage; reports carry a revision
  note.
* Cross-field transfer maps the M9 work roles to science roles (gather → inspect evidence,
  act_smallest → discriminating low-risk experiment, verify → statistical/formal validation,
  classify → diagnose fault) through the M9 `TransferMap`: partial transfer with adapters; the
  "verify" role must be re-bound to a *validation* operator (a work verifier is not a statistical
  test — superficial similarity refused by role).
* Communication gate: a rendered scientific sentence carries a strength marker (`proves`,
  `causes`, `suggests`, `is consistent with`, `cannot determine`); the allowed marker is fixed by
  the epistemic state (kernel PASS ⇒ proves; identified causal estimate ⇒ causes; association
  only ⇒ is consistent with / suggests; CANNOT_CHECK ⇒ cannot determine).  Fluent wording that
  exceeds the state is downgraded or refused (hostile: "elegant report language hides
  CANNOT_CHECK").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

from ocm.work import contracts as WC

STRENGTH = ("cannot determine", "is consistent with", "suggests", "causes", "proves")


@dataclass
class ScienceLedger:
    runtime: OCMRuntime
    observations: dict[str, str] = field(default_factory=dict)      # obs id → evidence id
    conclusions: dict[str, dict[str, Any]] = field(default_factory=dict)

    def observe(self, obs_id: str, source: str, payload: Mapping[str, Any], *, channel: Channel = Channel.OBSERVATION) -> str:
        _, eid = self.runtime.admit_evidence({"obs": obs_id, "source": source, **payload}, channel, source, scope=Scope.of("science"))
        self.observations[obs_id] = eid
        return eid

    def conclude(self, cid: str, statement: str, *, support: Sequence[str], kind: str, identification: Sequence[str] = (), lineage: Sequence[str] = ()) -> str:
        """Derived record: warrant = ⊗ of the supporting observations' evidence (each a distinct source
        is expected to be counted by the caller; here support ids are the distinct sources chosen)."""
        ev_ids = [self.observations[o] for o in support]
        derived = WarrantProfile.of(set(ev_ids))
        _, eid = self.runtime.admit_evidence({"conclusion": cid, "statement": statement, "kind": kind, "identification": list(identification), "lineage": list(lineage)}, Channel.PROOF if kind == "FORMAL" else Channel.OBSERVATION, "science.conclude", scope=Scope.of("science"), derived_from=derived, authority=Authority.of(source=1))
        self.conclusions[cid] = {"evidence_id": eid, "statement": statement, "support": list(support), "kind": kind, "lineage": list(lineage)}
        return eid

    def liveness(self, cid: str) -> Liveness:
        return self.runtime.state.evidence.liveness([self.conclusions[cid]["evidence_id"]])

    def retract(self, obs_id: str) -> dict[str, Any]:
        rep = self.runtime.revoke([self.observations[obs_id]])
        dead = sorted(c for c in self.conclusions if self.liveness(c) is Liveness.DEAD)
        return {"retracted": obs_id, "conclusions_dead": dead, "reopen": sorted(rep.reopen)}

    def replace_support(self, cid: str, new_obs: str) -> str:
        """Replacement support = a new conclusion record with lineage; the old stays dead."""
        old = self.conclusions[cid]
        return self.conclude(f"{cid}#2", old["statement"], support=[o for o in old["support"] if self.runtime.state.evidence.liveness([self.observations[o]]) is Liveness.LIVE] + [new_obs], kind=old["kind"], lineage=old["lineage"] + [cid])


# ------------------------------------------------------------------ cross-field transfer
SCIENCE_ROLE_MAP = {"gather": "inspect_evidence", "classify": "diagnose", "check_policy": "check_assumptions", "act_smallest": "discriminating_experiment", "verify": "validate", "document": "report"}


def science_transfer_map(source: WC.Skill, science_ops: Mapping[str, WC.Operator], correspondence_evidence: str) -> WC.TransferMap:
    """Work roles → science roles; every science operator is registered under the *science* role,
    so the M9 transfer refuses a work-role operator masquerading (e.g. a work verifier bound as a
    statistical validation)."""
    mapping = {}
    for role in source.skeleton:
        target_role = SCIENCE_ROLE_MAP.get(role)
        op = next((o for o in science_ops if science_ops[o].role == target_role), None)
        if op:
            mapping[role] = op
    return WC.TransferMap(f"tm:{source.skill_id}->science", source.skill_id, "science", mapping, ("roles registered",), tuple(r for r in source.skeleton if r in mapping), tuple(r for r in source.skeleton if r not in mapping), dict(SCIENCE_ROLE_MAP), 0.4, ("withheld",), WarrantProfile.of({correspondence_evidence}))


def transported_science_skill(source: WC.Skill, tm: WC.TransferMap, science_ops: Mapping[str, WC.Operator]) -> tuple[WC.TransferVerdict, WC.Skill | None, str]:
    """Like M9 `transported_skill` but the role agreement is checked through the science role map."""
    if tm.correspondence_warrant.liveness(()) is Liveness.DEAD:
        return WC.TransferVerdict.REFUSE_TRANSFER, None, "correspondence dead"
    bindings = {}
    for role in source.skeleton:
        tgt = tm.role_mapping.get(role)
        if tgt is None or tgt not in science_ops:
            return WC.TransferVerdict.ADAPTER_REQUIRED, None, f"no science binding for {role}"
        if science_ops[tgt].role != SCIENCE_ROLE_MAP.get(role):
            return WC.TransferVerdict.REFUSE_TRANSFER, None, f"{tgt} is {science_ops[tgt].role}, not {SCIENCE_ROLE_MAP.get(role)}"
        bindings[role] = tgt
    return WC.TransferVerdict.TRANSFER, WC.Skill(f"{source.skill_id}->science", source.skeleton, bindings, "science", tm.warrant(source), dict(tm.adapter), source.known_failures, source.lineage + (tm.transfer_id,)), "ok"


# ------------------------------------------------------------------ communication gate
def allowed_strength(state: Mapping[str, Any]) -> str:
    """The strongest marker the epistemic state licenses."""
    if state.get("kernel") == "PASS" and state.get("correspondence") == "LIVE":
        return "proves"
    if state.get("causal_identified") and state.get("liveness") == "LIVE":
        return "causes"
    if state.get("liveness") == "LIVE" and state.get("association"):
        return "suggests"
    if state.get("liveness") in ("LIVE", "UNKNOWN") and state.get("association"):
        return "is consistent with"
    return "cannot determine"


def gate_sentence(sentence: str, state: Mapping[str, Any]) -> tuple[bool, str, str]:
    """(committed, sentence, reason): a sentence whose marker exceeds the licensed strength is
    downgraded to the licensed marker; a CANNOT_CHECK hidden by fluent wording is refused."""
    licensed = allowed_strength(state)
    used = next((m for m in sorted(STRENGTH, key=len, reverse=True) if m in sentence), None)
    if used is None:
        return False, sentence, "no strength marker: refused (state must be expressed)"
    if STRENGTH.index(used) <= STRENGTH.index(licensed):
        return True, sentence, "within licensed strength"
    if licensed == "cannot determine":
        return False, sentence.replace(used, "cannot determine"), "refused: wording exceeds a CANNOT_CHECK state"
    return True, sentence.replace(used, licensed), f"downgraded {used!r} → {licensed!r}"


def mutant_fluent_overclaim(sentence: str) -> str:
    """Planted (M10 §14/§17): fluent wording converts weak evidence into 'proves/causes'."""
    return sentence.replace("is consistent with", "proves").replace("suggests", "causes")
