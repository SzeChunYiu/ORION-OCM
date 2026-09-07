"""Create-only native F0 lifecycle commissioning; no learning or FLT claim."""
import argparse
from pathlib import Path
import time
import sys
REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / "src"), str(Path(__file__).resolve().parent)]
from adapter import ProofRuntimeView
from closed_session import ProofSession
from ocm.runtime.ocm_runtime import OCMRuntime
import lifecycle_replay as R
from lifecycle_replay import replay

PYTHON = Path("/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python")
PHASES = ("session_B", "register", "solve_B", "B_live", "persist_B", "close_B", "cold_live", "restore_B",
          "B_withdrawn", "cold_B_open", "B_reinstated", "discovery_withdrawn", "discovery_reinstated",
          "session_C", "bind_C", "solve_C", "two_routes", "close_C", "B_withdrawn_C_live",
          "both_withdrawn", "both_reinstated", "environment_withdrawn", "environment_reinstated", "cold_final")


def host_flags(): return {k: int(getattr(sys.flags, k)) for k in ("isolated", "no_site", "dont_write_bytecode")}


def require(condition, message):
    if not condition: raise ValueError(message)


def status_ok(value, terminal, applicable=True, routes=None):
    require(value.get("terminal") == terminal, "unexpected proof status: " + str(value))
    require(value.get("applicable") is applicable, "unexpected applicability")
    if routes is not None: require(value.get("authenticated_routes") == routes, "unexpected route count")


def run(manifest, expected_sha, directory, *, python_executable=PYTHON):
    started = time.monotonic(); directory = Path(directory).resolve(); directory.mkdir(exist_ok=False)
    (directory / "phases").mkdir(); phases = []; routes = []; solves = []; frozen = None; sessions = []
    result = {"schema": "ocm.proof-runtime-lifecycle.v1", "terminal": "CANNOT_CHECK", "phases": phases,
              "scope": "Exposed F0 integration commissioning; no learned method, scaling, FLT or comparative advantage claim.",
              "parent": "Conventional typed symbolic proposal plus Lean checking; no new matched parent experiment in this lifecycle."}
    def phase(name, call, validate=lambda value: None):
        require(name == PHASES[len(phases)], "unregistered phase order")
        row = {"name": name, "passed": False}; clock = time.monotonic()
        record = "phases/%02d-%s.json" % (len(phases), name)
        try:
            R.verify_freeze(frozen, frozen_sha); R.bound_imports(R.read(frozen))
            row["result"] = call()
            R.verify_freeze(frozen, frozen_sha); row["parent_imports"] = R.bound_imports(R.read(frozen))
            validate(row["result"]); row["passed"] = True
            return row["result"]
        except BaseException as exc:
            row["reason"] = type(exc).__name__ + ": " + str(exc); raise
        finally:
            row["wall_s"] = time.monotonic() - clock; R.save(directory / record, row)
            phases.append({"name": name, "passed": row["passed"], "record": record})
    def new_session(label):
        session = ProofSession(manifest, expected_sha, directory / ("session-" + label))
        sessions.append(session); return session.readiness
    def cold(name, terminal):
        def valid(value):
            require(type(value["returncode"]) is int and value["returncode"] == 0 and
                    value["terminal"] == "COMPLETED" and value["stderr"] == "", "cold replay did not complete")
            child = value["result"]
            require(value["cleanup"] == {"reaped": True, "group_absent": True} and
                    type(value["pid"]) is int and child["pid"] == value["pid"] and
                    child["imports_bound"] is True, "cold replay process/import binding failed")
            require(child["session_bound"] is False and child["host_operators"] == [] and
                    child["executable_operators"] == [] and child["read_only"] is True, "cold replay rebound or mutated")
            status_ok(child["status"], terminal)
        return phase(name, lambda: replay(directory, frozen, frozen_sha, python_executable), valid)
    def change(name, ids, restore, terminal, applicable=True):
        def action():
            evidence = sorted(view.rt.state.evidence.records); activity = R.activity(directory)
            issuer = [e.entry_hash for e in view.journal.entries()]
            if restore: view.rt.reinstate(ids)
            else: view.rt.revoke(ids)
            status = R.observe(view)
            require(evidence == sorted(view.rt.state.evidence.records) and activity == R.activity(directory) and
                    issuer == [e.entry_hash for e in view.journal.entries()], "revision minted evidence or dispatched")
            return {"evidence": ids, "status": status, "no_new_evidence_or_dispatch": True}
        return phase(name, action, lambda r: status_ok(r["status"], terminal, applicable))
    try:
        frozen, frozen_sha = R.make_freeze(REPO, manifest, expected_sha, directory, python_executable)
        result.update(freeze_sha256=frozen_sha, runtime_sha256=expected_sha)
        parent = {"executable": str(Path(sys.executable).resolve()), "version": sys.version,
                  "argv": sys.orig_argv, "flags": host_flags(), "imports": R.bound_imports(R.read(frozen))}
        R.save(directory / "parent.json", parent)
        require(parent["executable"] == str(Path(python_executable).resolve()) and
                parent["flags"] == {"isolated": 1, "no_site": 1, "dont_write_bytecode": 1},
                "parent must use registered standalone Python -I -S -B")
        phase("session_B", lambda: new_session("B"), lambda r: require(r["terminal"] == "READY", "session B unavailable"))
        def register():
            nonlocal view
            view = ProofRuntimeView.create(OCMRuntime(directory / "ocm"), sessions[-1], directory / "issuer")
            return {"registration": view.registration, "status": R.observe(view)}
        view = None
        phase("register", register, lambda r: status_ok(r["status"], "OPEN", routes=0))
        admitted = lambda r: require(r.get("terminal") == "ADMITTED" and r["solve"]["decision"] == "ANSWER", "solve did not admit")
        solves.append(phase("solve_B", view.attempt, admitted))
        phase("B_live", lambda: R.observe(view), lambda r: status_ok(r, "LIVE", routes=1))
        phase("persist_B", lambda: view.rt.persist().as_dict())
        phase("close_B", lambda: sessions[-1].close())
        cold("cold_live", "LIVE")
        def restore():
            nonlocal view
            view = ProofRuntimeView.restore(OCMRuntime(directory / "ocm"), directory / "issuer")
            require(view.session is None and not view.rt._host_operators and not view.rt.state.operators.operators,
                    "restored runtime rebound code")
            return R.observe(view)
        phase("restore_B", restore, lambda r: status_ok(r, "LIVE", routes=1))
        b = view.routes()[0]["plan"]["run_evidence_id"]
        a, s = (view.registration[k] for k in ("discovery_id", "environment_evidence_id"))
        change("B_withdrawn", [b], False, "OPEN"); cold("cold_B_open", "OPEN")
        change("B_reinstated", [b], True, "LIVE")
        change("discovery_withdrawn", [a], False, "LIVE", False)
        change("discovery_reinstated", [a], True, "LIVE")
        phase("session_C", lambda: new_session("C"), lambda r: require(r["terminal"] == "READY", "session C unavailable"))
        phase("bind_C", lambda: view.bind(sessions[-1]))
        solves.append(phase("solve_C", view.attempt, admitted))
        def two_routes():
            plans = [r["plan"] for r in view.routes()]
            require(len(plans) == 2 and len({p["run_id"] for p in plans}) == 2 and
                    len({p["run_evidence_id"] for p in plans}) == 2, "second independent run absent")
            for p, solved in zip(plans, solves):
                require(p["run_id"] == solved["run_id"] and R.raw(p["candidate"]) == R.raw(solved["solve"]["answer"]["candidate"]) and
                        p["handle"]["proposal_id"] == solved["solve"]["answer"]["proposal_id"], "route differs from actual solve")
                require(p["handle"]["checker"]["fresh_kernel_replay"] is True, "fresh kernel replay missing")
                support = view.rt.state.ks.atom(p["claim_id"]).warrant
                require(support.evidence == frozenset({p["run_evidence_id"], s}) and a not in support.evidence,
                        "correctness support differs from run and shared checker assumption")
                require(p["handle"]["terminal"] == "KERNEL_PASS" and p["handle"]["checker"]["axioms"] == [],
                        "route lacks fresh empty-axiom kernel pass")
            routes.extend(plans); return {"status": R.observe(view), "run_ids": [p["run_id"] for p in plans]}
        phase("two_routes", two_routes, lambda r: status_ok(r["status"], "LIVE", routes=2))
        phase("close_C", lambda: sessions[-1].close())
        c = routes[1]["run_evidence_id"]
        change("B_withdrawn_C_live", [b], False, "LIVE")
        change("both_withdrawn", [c], False, "OPEN")
        change("both_reinstated", [b, c], True, "LIVE")
        change("environment_withdrawn", [s], False, "OPEN")
        change("environment_reinstated", [s], True, "LIVE")
        cold("cold_final", "LIVE")
        require(tuple(p["name"] for p in phases) == PHASES and all(p["passed"] for p in phases), "incomplete lifecycle")
        R.verify_freeze(frozen, frozen_sha)
        result["terminal"] = "PROOF_RUNTIME_LIFECYCLE_COMMISSIONING_PASS"
    except BaseException as exc:
        result["reason"] = type(exc).__name__ + ": " + str(exc)
        if not isinstance(exc, Exception): raise
    finally:
        result.update(routes=routes, outer_wall_s=time.monotonic() - started,
                      bytes_before_result_write=sum(p.stat().st_size for p in directory.rglob("*") if p.is_file()),
                      cost_scope="Outer wall includes freeze, two cold sessions, solve/check/admission, status, revision and cold subprocess replay, through final freeze; excludes final result serialization and earlier runtime acquisition/preparation. Phase costs overlap nested session/checker receipts; do not sum nested and outer costs.",
                      cpu_s=None, peak_rss_bytes=None)
        R.save(directory / "result.json", result)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runtime-manifest", required=True); p.add_argument("--expected-sha", required=True)
    p.add_argument("--output", required=True); p.add_argument("--python", default=str(PYTHON))
    args = p.parse_args()
    value = run(args.runtime_manifest, args.expected_sha, args.output, python_executable=args.python)
    print(value["terminal"])
    raise SystemExit(0 if value["terminal"] == "PROOF_RUNTIME_LIFECYCLE_COMMISSIONING_PASS" else 1)
