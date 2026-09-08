"""Exposed native method/lifecycle correspondence probe; no protected evaluation.

The ordinary parent below shares OCM's exact learner and solver. Equality is a
kernel-level emulation control, NOT an independently implemented whole-machine
competitor. This probe deliberately cannot emit architecture net benefit.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import tempfile
from time import perf_counter_ns, process_time_ns

EXPECTED_METHODS_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"


def git_blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def run(root: Path) -> dict:
    from ocm.learning import methods as M
    from ocm.runtime.ocm_runtime import OCMRuntime

    methods_path = Path(M.__file__)
    if git_blob(methods_path.read_bytes()) != EXPECTED_METHODS_BLOB:
        raise RuntimeError("frozen exact method source drift; requalify, do not silently update")
    src_root = methods_path.parents[2]
    inventory = [(str(p.relative_to(src_root)), hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in sorted(src_root.rglob("*.py"))]
    source_digest = hashlib.sha256(json.dumps(inventory, separators=(",", ":")).encode()).hexdigest()
    started_wall, started_cpu = perf_counter_ns(), process_time_ns()
    timings = {}

    def phase(name, fn):
        w, c = perf_counter_ns(), process_time_ns()
        result = fn()
        timings[name] = {"wall_ns": perf_counter_ns() - w, "cpu_ns": process_time_ns() - c}
        return result

    training_tasks = (M.PolynomialTask("train-increment", (2, 2, 1)),
                      M.PolynomialTask("train-double", (2, 4, 2)))
    validation_tasks = (M.PolynomialTask("validate-decrement", (0, 2, 1)),
                        M.PolynomialTask("validate-fourth", (1, 4, 6, 4, 1)))
    training = phase("training_search", lambda: tuple((t, M.solve(t)) for t in training_tasks))
    ordinary = phase("ordinary_learn", lambda: M.learn_generator(training))
    rt = phase("runtime_start", lambda: OCMRuntime(root))
    admission = phase("native_learn_validate_admit", lambda: M.admit_generator(rt, training, validation_tasks))
    rt = phase("native_restart_after_admission", lambda: OCMRuntime(root))
    native = phase("native_load", lambda: M.load_generator(rt, admission["generator_id"]))
    if native != ordinary:
        raise RuntimeError("persisted native generator differs from same-information ordinary learner")

    # Complete exposed finite grammar, never a tuned subset or a held-out claim.
    coefficients = {M.normal_form(p) for length in range(5) for p in product(M.PRIMITIVES, repeat=length)}
    used = {t.coefficients for t in training_tasks + validation_tasks}
    transfer = sorted(coefficients - used)
    budget = M.SearchBudget(slots=1000, max_length=4)

    def compare():
        rows = []
        for i, cs in enumerate(transfer):
            task = M.PolynomialTask(f"exposed-transfer-{i}", cs)
            # Both get the exact same input; the kernel parent gets no future outcome.
            n = M.solve(task, budget, native)
            p = M.solve(task, budget, ordinary)
            if n.as_dict() != p.as_dict() or not M.verify_solution(task, n):
                raise RuntimeError("kernel correspondence failed")
            rows.append({"task": task.fingerprint, "slots": n.slots,
                         "checked": n.candidates_checked, "program": n.program})
        return rows

    rows = phase("paired_exposed_kernel_queries", compare)
    supports = frozenset([admission["validation_evidence"]] + [r["evidence_id"] for r in admission["training"]])
    observed_revoked = set()
    lifecycle = []

    def check(label):
        expected = not bool(supports & observed_revoked)
        try:
            loaded = M.load_generator(rt, admission["generator_id"])
            actual = True
            if loaded != ordinary:
                raise RuntimeError("live generator changed")
        except ValueError:
            actual = False
        if actual != expected:
            raise RuntimeError(f"support-state correspondence failed at {label}")
        lifecycle.append({"event": label, "native_live": actual, "conjunction_parent_live": expected})

    def lifecycle_probe():
        nonlocal rt
        check("initial_restarted")
        for support in sorted(supports):
            rt.revoke([support]); observed_revoked.add(support)
            check("revoke_support")
            rt = OCMRuntime(root)
            check("restart_revoked")
            rt.reinstate([support]); observed_revoked.remove(support)
            check("reinstate_support")
            rt = OCMRuntime(root)
            check("restart_reinstated")
        rt.persist()
        rt = OCMRuntime(root)
        check("snapshot_restart")

    phase("native_revocation_reinstatement_restart", lifecycle_probe)
    full_wall = perf_counter_ns() - started_wall
    full_cpu = process_time_ns() - started_cpu
    return {
        "terminal": "NATIVE_KERNEL_PARENT_EQUIVALENT__ARCHITECTURE_BENEFIT_UNESTABLISHED",
        "source": {"methods_git_blob": EXPECTED_METHODS_BLOB, "src_py_inventory_sha256": source_digest,
                   "src_py_inventory": inventory},
        "population": {"grammar_programs": sum(4**i for i in range(5)),
                       "distinct_targets": len(coefficients), "excluded_training_validation_targets": len(used),
                       "exposed_transfer_targets": len(transfer), "protected_holdout": False},
        "learned_fragments": ordinary.fragments, "generator_fingerprint": ordinary.fingerprint,
        "generator_given_to_native_search_after_restart": True,
        "kernel_parent_equal_rows": len(rows), "query_rows": rows,
        "lifecycle_observations": lifecycle, "source_support_count": len(supports),
        "observer_run": {"wall_ns": full_wall, "cpu_ns": full_cpu, "phases": timings,
                         "native_final_tree_bytes": sum(p.stat().st_size for p in root.rglob("*") if p.is_file())},
        "limits": [
            "exposed qualification only; no protected evaluation or architecture admission",
            "ordinary parent uses the same learner/solver implementation, not independent replication",
            "parent equality covers the method kernel and tested single-conjunction liveness, not full OCM semantics",
            "parent persistence, crash consistency, concurrent writers and whole-machine cost are NOT qualified",
            "timings are instrumentation timings of this mixed probe, NOT per-arm speed estimates",
            "no measured time is promoted to a worst-case cost bound in the finite theorem",
            "fragment discovery is from existing two training tasks; this is not novel or broad endogenous discovery",
        ],
        "architecture_net_benefit_established": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="ocm-native-benefit-bridge-") as directory:
        report = run(Path(directory))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"terminal": report["terminal"], "population": report["population"],
                      "kernel_parent_equal_rows": report["kernel_parent_equal_rows"],
                      "lifecycle_observations": len(report["lifecycle_observations"]),
                      "learned_fragments": report["learned_fragments"]}, sort_keys=True))


if __name__ == "__main__":
    main()
