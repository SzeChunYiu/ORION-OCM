"""Actual OCM solve/check/admit and authenticated proof-support subview, F0 only."""
import json
from pathlib import Path
import time
from ocm.runtime import solve as SV
from ocm.runtime.operator_index import SolveOperatorIndex
from ocm.operators.registry import OperatorSpec as RegisteredOperator, BackendKind
from ocm.store.ledger import LedgerStore
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from route_data import clone, encoded, hashed
import route_registration as registration
import route_journal as journal
import route_recovery as recovery
from route_plan import make_plan
from session_bindings import canonical


class ProofRuntimeView:
    def __init__(self, rt, session, root, store, reg):
        self.rt = rt; self.session = session; self.root = root; self.journal = store
        self.registration = reg; self._issuer_head = store.head().entry_hash if store.head() else None
        self.fault = lambda stage: None

    @classmethod
    def create(cls, rt, session, root):
        root = Path(root).resolve(); root.mkdir(exist_ok=False)
        reg = registration.register(rt, session, root)
        view = cls(rt, session, root, LedgerStore(root), reg)
        journal.append(view, "REGISTERED", {"sha256": hashed(reg)}, "registration")
        view.bind(session)
        return view

    @classmethod
    def restore(cls, rt, root, session=None):
        root, store = journal.open_existing(root)
        view = cls(rt, session, root, store, json.loads((root / "registration.json").read_bytes()))
        journal.verify(view)
        if session is not None: view.bind(session)
        return view

    def bind(self, session):
        reg = self.registration; journal.verify(self)
        if (session.task_sha256 != reg["task_sha256"] or session.environment_id != reg["environment_id"] or
                session.readiness["terminal"] != "READY"):
            raise ValueError("new host session does not match registered task/environment")
        self.session = session
        scope = Scope.of(reg["environment_id"])
        self.rt.register_operator(RegisteredOperator("mechanical.fixed-f0", reg["task_sha256"], BackendKind.PROOF,
            lambda ks, bindings: self._backend(ks, "mechanical.fixed-f0", bindings),
            (reg["procedure_id"],), output_type="proof", scope=scope, checker=self._checker))

    def _backend(self, ks, op_id, bindings):
        reg = self.registration; atom = ks.atom(reg["procedure_id"])
        meta = dict(atom.meta)
        raw = meta["descriptor_json"].encode()
        if (raw != canonical(reg["task"]) or meta["environment_id"] != reg["environment_id"] or
                atom.content_ref != reg["task_sha256"]): raise ValueError("KSO task binding changed")
        return self.session.propose(raw, reg["task_sha256"])

    def _checker(self, data):
        handle = self.session.check(data); self._last_handle = clone(handle)
        return SV.Status.PASS if handle["terminal"] == "KERNEL_PASS" else SV.Status.CANNOT_CHECK

    def attempt(self):
        started = time.monotonic(); self._last_handle = None
        journal.verify(self)
        if self.session is None: raise ValueError("explicit host session rebinding required")
        reg = self.registration
        op = SV.OperatorSpec("mechanical.fixed-f0", reg["task_sha256"], self._backend,
            (reg["procedure_id"],), output_type="proof", scope=Scope.of(reg["environment_id"]), checker=self._checker)
        task = SV.Task(reg["goal_id"], (SV.QueryPart("construct registered formal proof", "goal",
                       (reg["procedure_id"],)),), context=reg["environment_id"])
        outcome = self.rt.solve(task, SolveOperatorIndex((op,)))
        result = {"terminal": "CANNOT_CHECK", "solve": outcome.as_dict()}
        if outcome.decision is SV.Decision.ANSWER:
            plan = self.admit_checked(outcome.answer, self._last_handle)
            result.update(terminal="ADMITTED", run_id=plan["run_id"])
        result["wall_s"] = time.monotonic() - started
        result["cost_scope"] = "Includes solve, session sealing, authentication, artifact fsync, admission and journal commit; cold runtime setup, later persistence/replay and final result serialization separate."
        return result

    def admit_checked(self, proposal, handle):
        with journal.writer(self.root):
            journal.verify(self)
            try: plan = make_plan(self, proposal, handle)
            except (KeyError, TypeError) as exc: raise ValueError("unissued proof data") from exc
            run = plan["run_id"]
            if any(r["plan"]["run_id"] == run for r in self.routes()): raise ValueError("run already prepared")
            journal.append(self, "PREPARED", {"run_id": run, "plan": plan, "sha256": hashed(plan)}, "prepare:" + run)
            self.fault("prepared")
        self.recover(run)
        return plan

    def routes(self): return clone(journal.routes(self))
    def recover(self, run_id): return clone(recovery.recover(self, run_id))

    def proof_status(self):
        try:
            reg = self.registration; routes = self.routes(); support = WarrantProfile.zero()
            pending = 0; unavailable = []; authenticated = 0
            for route in routes:
                if route["commit"] is None:
                    pending += 1; continue
                try: recovery.check_committed(self, route)
                except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
                    unavailable.append({"run_id": route["plan"]["run_id"], "reason": str(exc)}); continue
                authenticated += 1
                support = support.join(self.rt.state.ks.atom(route["plan"]["claim_id"]).warrant)
            support = self.rt.state.nogoods.filter_interval(support)
            support = self.rt.state.evidence.nogoods.filter_interval(support)
            status = support.liveness(self.rt.state.revoked | self.rt.state.evidence.revoked)
            discovery = self.rt.state.evidence.citation_warrant([reg["discovery_id"]])
            discovery = self.rt.state.nogoods.filter_interval(self.rt.state.evidence.nogoods.filter_interval(discovery))
            applicable = discovery.liveness(self.rt.state.revoked | self.rt.state.evidence.revoked) is Liveness.LIVE
            terminal = "LIVE" if status is Liveness.LIVE else "CANNOT_CHECK" if (
                status is Liveness.UNKNOWN or pending or unavailable) else "OPEN"
            return {"terminal": terminal, "applicable": applicable, "support": support.as_dict(),
                    "authenticated_routes": authenticated, "pending_routes": pending, "unavailable_routes": unavailable}
        except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
            return {"terminal": "CANNOT_CHECK", "reason": type(exc).__name__ + ": " + str(exc)}
