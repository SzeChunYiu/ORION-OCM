"""The two whole-system arms of the M12 lifetime (issue #14 §2, §9) and the template floor.

* `PersistentOCM` — ONE runtime identity for the whole lifetime: a single `OCMRuntime` ledger
  (under `root/chat/ledger`) shared by the M6 ChatSession (language + knowledge world), the M9
  work skills (demonstration evidence admitted into the same ledger; liveness read from it), the
  M10 ScienceLedger and the M11 SelfModel.  Nothing is reset between phases; `identity()` returns
  the ledger root and the state digest so the receipt can prove continuity.
* `WholeSystemParent` — the strongest faithful parent buildable here without a foundation model:
  the M7 MatchedParent for language (same manifest, lessons, corrections), the M9 SkillLibraryArm
  for work (explicit skill library with name-similarity transfer), the M10 parent procedures for
  science (entropy selection, naive/backdoor estimators with the *same* pre-registered analysis
  plan and kernel), and parameter search + reflection-retry for repair.  It receives identical
  tasks, demonstrations, lessons and budgets.  The experimental difference is declared, not
  hidden: explicit warrant/revocation/scope machinery, role-typed transfer, evidence dependence
  and identification gates, and the M11 governed self-change path.
* `TemplateFloor` — the M7 template arm for language plus no-op work/science (a floor, not a parent).

A frontier foundation-model reference arm cannot be built in this environment (no network, no
model): `FRONTIER_REFERENCE = CANNOT_CHECK` is recorded, never silently omitted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ocm.chat.session import ChatSession
from ocm.evaluation import m7_comparison as M7
from ocm.evaluation import m9_transfer_eval as M9
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.science import lifecycle as LC
from ocm.selfmodel import model as SM
from ocm.store.evidence import Channel
from ocm.work import contracts as C
from ocm.work import envs as E
from ocm.work import methods as M

FRONTIER_REFERENCE = "CANNOT_CHECK (no network / no foundation model in this environment; reference arm not built)"


def identity_chain(runtime) -> dict[str, Any]:
    """Batch 6 F5: the identity of a persistent machine is its ledger *chain* (head hash + length),
    the component fingerprints and the adoption lineage — not a root path string or a Python handle
    (both pass a same-path replaced log)."""
    evs = runtime.events
    return {"head": evs[-1].event_hash if evs else None, "length": len(evs), "root": str(runtime.root)}


def chain_continuous(before: dict[str, Any], runtime) -> bool:
    """The earlier head must still be an event hash in the current chain at its recorded position."""
    evs = runtime.events
    if before["head"] is None:
        return before["length"] == 0 and str(runtime.root) == before["root"]
    n = before["length"]
    return len(evs) >= n and n >= 1 and evs[n - 1].event_hash == before["head"] and str(runtime.root) == before["root"]


def adoption_predecessors_bound(runtime, adopted: dict[str, Any]) -> tuple[bool, list[str]]:
    """Batch-6 integration correction (ORION-V2 KSO_LIFETIME_BATCH6_INTEGRATION_REVIEW_V1): a chain
    extension with an *invented* adoption predecessor must be refused — every persisted adoption
    artifact's stamp must resolve to an evidence record in the replayed ledger, and its recorded
    pre-adoption state hash must be a hash the ledger actually passed through."""
    records = runtime.state.evidence.records
    seen_hashes = {ev.kso_state_hash for ev in runtime.events if getattr(ev, "kso_state_hash", None)}
    bad = []
    for fp, art in adopted.items():
        stamp = getattr(art, "stamped_evidence", None) or (art.get("stamped_evidence") if isinstance(art, dict) else None)
        prev = getattr(art, "previous_state_hash", None) or (art.get("previous_state_hash") if isinstance(art, dict) else None)
        if stamp not in records:
            bad.append(f"{fp}: stamp {stamp} not in the replayed ledger")
        elif prev and seen_hashes and prev not in seen_hashes:
            bad.append(f"{fp}: pre-adoption state hash never occurred in the ledger")
    return (not bad), bad


def mutant_accept_invented_predecessor(runtime, adopted: dict[str, Any]) -> bool:
    """Planted (integration-review hostile): a predecessor accepted because the chain head still extends."""
    return True


def mutant_identity_by_path(before: dict[str, Any], runtime) -> bool:
    """Planted (F5 hostile): identity judged by the root path string alone — passes a replaced log."""
    return str(runtime.root) == before["root"]


class PersistentOCM(M7.OCMArm):
    name = "ocm"

    def __init__(self, root: Path):
        self.root = Path(root)
        self.ablations = frozenset()
        self.s = ChatSession(self.root / "chat")
        self.last_lesson: str | None = None
        self.runtime = self.s.runtime                     # the one ledger
        self.science = LC.ScienceLedger(self.runtime)
        self.selfmodel = SM.SelfModel(self.runtime)
        self.work = M9.OCMArm()                            # skills / capsule / router live here; warrants in the ledger
        self.operator_lineage: dict[str, dict[str, list[C.Operator]]] = {}   # domain → operator id → previous versions
        self.demo_evidence: dict[str, str] = {}
        self.phase_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ restart = same identity
    def say(self, utt: str) -> str:
        if utt == "__restart__":
            # persist and reopen the SAME ledger root; every component is re-pointed at the reopened runtime
            # (the inherited restart reopened a session at a different path: ledger S31)
            self.s.runtime.persist()
            self.s = ChatSession(self.root / "chat")
            self.runtime = self.s.runtime
            for comp in (self.science, self.selfmodel):
                for attr in ("runtime", "rt"):
                    if hasattr(comp, attr):
                        setattr(comp, attr, self.runtime)
            return "restarted"
        return super().say(utt)

    # ------------------------------------------------------------------ identity
    def identity(self) -> dict[str, Any]:
        rt = self.s.runtime
        st = rt.state
        return {"ledger_root": str(rt.root), "evidence_records": len(st.evidence.records), "ks_digest": st.ks.digest(), "skills": sorted(self.work.skills), "science_conclusions": len(self.science.conclusions), "selfmodel_records": len(self.selfmodel.evidence), "one_runtime": rt is self.runtime and all(getattr(c, "runtime", getattr(c, "rt", None)) is rt for c in (self.science, self.selfmodel)), "chain": identity_chain(rt)}

    def state_digest(self) -> str:
        return hashlib.sha256(json.dumps(self.identity(), sort_keys=True).encode()).hexdigest()[:16]

    # ------------------------------------------------------------------ work (M9 arm over the shared ledger)
    def revoked_for(self, domain: str) -> set[str]:
        ev = self.runtime.state.evidence
        out = set()
        for sk in self.work.skills.values():
            for e in sk.warrant.evidence:
                if e in ev.records and ev.liveness([e]) is Liveness.DEAD:
                    out.add(e)
        return out

    def acquire(self, domain: str, ops, tasks, withheld) -> dict[str, Any]:
        rep = self.work.acquire(domain, ops, tasks, withheld)
        sk = self.work.skills.get(domain)
        if sk is not None and domain not in self.demo_evidence:
            # the demonstration warrant is admitted into the one ledger under the skill's own evidence id
            _, eid = self.runtime.admit_evidence({"demonstration": domain, "skill": sk.skill_id, "route": rep["route"]}, Channel.DEMONSTRATION, f"demo:{domain}")
            self.demo_evidence[domain] = eid
            self.work.skills[domain] = C.Skill(sk.skill_id, sk.skeleton, sk.bindings, sk.domain, WP.of(set(sk.warrant.evidence) | {eid}), sk.adapter, sk.known_failures, sk.lineage, sk.scope)
        return rep

    def solve(self, domain: str, ops, task):
        self.work.revoked = self.revoked_for(domain)
        return self.work.solve(domain, ops, task)

    def revoke_domain_demo(self, domain: str) -> str | None:
        eid = self.demo_evidence.get(domain)
        if eid:
            self.runtime.revoke([eid])
        return eid

    def info(self) -> dict:
        base = super().info()
        base.update({"work_skills": len(self.work.skills), "science_observations": len(self.science.observations) if hasattr(self.science, "observations") else None, "protected_exposure": 0})
        return base


class WholeSystemParent(M7.ParentArm):
    name = "whole_system_parent"

    def __init__(self, root: Path):
        super().__init__(Path(root) / "parent")
        self.work = M9.SkillLibraryArm()
        self.phase_log: list[dict[str, Any]] = []
        self.revoked_domains: set[str] = set()

    def identity(self) -> dict[str, Any]:
        return {"state_file": str(self.state), "skills": sorted(self.work.skills), "lessons": self.p.info.get("lessons")}

    def state_digest(self) -> str:
        return hashlib.sha256(json.dumps(self.identity(), sort_keys=True, default=str).encode()).hexdigest()[:16]

    def acquire(self, domain, ops, tasks, withheld):
        return self.work.acquire(domain, ops, tasks, withheld)

    def solve(self, domain, ops, task):
        if domain in self.revoked_domains:
            return None                                    # the parent's revocation is a per-domain flag (its own mechanism)
        return self.work.solve(domain, ops, task)

    def revoke_domain_demo(self, domain: str) -> str | None:
        self.revoked_domains.add(domain)
        return f"parent-flag:{domain}"

    def info(self) -> dict:
        base = super().info()
        base.update({"work_skills": len(self.work.skills), "protected_exposure": 0})
        return base


class TemplateFloor(M7.TemplateArm):
    name = "template_floor"

    def __init__(self, root: Path):
        super().__init__(Path(root))
        self.phase_log: list[dict[str, Any]] = []

    def identity(self) -> dict[str, Any]:
        return {"facts": len(self.facts)}

    def state_digest(self) -> str:
        return "template"

    def acquire(self, domain, ops, tasks, withheld):
        return {"route": "NONE", "cost": 0, "reused_operators": 0, "new_operators": 0}

    def solve(self, domain, ops, task):
        return None

    def revoke_domain_demo(self, domain: str) -> str | None:
        return None


ARMS = {"ocm": PersistentOCM, "whole_system_parent": WholeSystemParent, "template_floor": TemplateFloor}
