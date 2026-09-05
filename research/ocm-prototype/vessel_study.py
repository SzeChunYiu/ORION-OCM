"""Registered tiny lifecycle study; evaluator answers never enter operator inputs."""
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

from ocm.language.meaning import canonical
from ocm.learning import methods as M
import minimal_language_learning as L
from vessel_ops import CATALOGUE


def run(root):
    root = Path(root)
    if root.exists() and any(root.iterdir()):
        raise ValueError("study requires an empty custody directory")
    wall, cpu = time.perf_counter(), time.process_time()
    children_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    worker = Path(__file__).with_name("vessel_pilot.py")
    def call(action, **fields):
        process = subprocess.run([sys.executable, str(worker), str(root), json.dumps({"action": action, **fields})],
                                 check=True, text=True, capture_output=True)
        return json.loads(process.stdout)
    setup = call("setup")
    fixture = setup["fixture"]
    language = {"kind": "language", "utterance": "girl ball push"}
    polynomial = {"kind": "polynomial", "coefficients": ["1", "2", "1"]}
    rows, events = {}, {}
    def query(name, request, **fields):
        rows[name] = call("query", request=request, **fields)
        return rows[name]
    query("language_initial", language)
    query("polynomial_initial", polynomial)
    query("language_reload", language)
    query("polynomial_reload", polynomial)
    events["language_first_revoke"] = call("revoke", evidence=fixture["language_lessons"][:1])
    query("language_alternate", language)
    events["language_last_revoke"] = call("revoke", evidence=fixture["language_lessons"][1:])
    query("language_revoked", language)
    query("math_after_language_revoke", polynomial)
    call("reinstate", evidence=fixture["language_lessons"])
    query("language_restored", language)
    events["generator_revoke"] = call("revoke", evidence=fixture["generator_lessons"][:1])
    query("math_primitive_fallback", polynomial)
    query("language_after_generator_revoke", language)
    call("reinstate", evidence=fixture["generator_lessons"][:1])
    query("math_generator_restored", polynomial)
    query("wrong_output", polynomial, fault="wrong_output")
    query("missing_checker", polynomial, fault="missing_checker")
    query("wrong_scope", polynomial, fault="wrong_scope")
    query("exhausted", {**polynomial, "slots": 0})
    query("checker_injection", {**polynomial, "checker": "always-pass"})
    # These expected meanings are evaluator-only; workers see utterance or polynomial goal data.
    expected_language = canonical(L.transitive_meaning("girl", "push", "ball"))[1]
    def language_ok(name):
        row = rows[name]
        return bool(row["admitted_id"] and row["selected"] == CATALOGUE[0]
                    and row["answer"]["digest"] == expected_language)
    def math_ok(name):
        row = rows[name]
        return bool(row["admitted_id"] and M.normal_form(tuple(row["answer"]["program"]))
                    == M.PolynomialTask("evaluation", tuple(polynomial["coefficients"])).coefficients)
    stages = ["TASK", "GROUNDING", "REPRESENTATION", "NAVIGATION", "EXTRACTION", "EXECUTION",
              "COMPOSITION", "CHECK", "DECISION", "COMMITMENT"]
    checks = {
        "shared_core_and_catalogue": all(row["fixture"] == setup["identity"] and row["catalogue"] == list(CATALOGUE)
                                         for row in rows.values()),
        "actual_full_stage_traces": all([s["stage"] for s in row["trace"]["stages"]] == stages
                                        for row in rows.values() if row["admitted_id"]),
        "both_domains_checked_and_admitted": language_ok("language_initial") and math_ok("polynomial_initial"),
        "pure_proposal_backends": all(row["pure_proposals"] for row in rows.values() if row["trace"]),
        "fresh_process_reuse": language_ok("language_reload") and math_ok("polynomial_reload")
            and len({row["pid"] for row in rows.values()}) == len(rows),
        "language_alternate_support": language_ok("language_alternate") and events["language_first_revoke"]["liveness"].get(
            rows["language_initial"]["admitted_id"]) == "LIVE",
        "language_last_support_revoked": rows["language_revoked"]["admitted_id"] is None
            and events["language_last_revoke"]["liveness"].get(rows["language_initial"]["admitted_id"]) == "DEAD",
        "unrelated_arithmetic_retained": math_ok("math_after_language_revoke"),
        "language_restored": language_ok("language_restored"),
        "generator_reused": rows["polynomial_initial"]["selected"] == CATALOGUE[1],
        "generator_revoked_primitive_fallback": math_ok("math_primitive_fallback")
            and rows["math_primitive_fallback"]["selected"] == CATALOGUE[2],
        "prior_mathematical_truth_retained": events["generator_revoke"]["liveness"].get(
            rows["polynomial_initial"]["admitted_id"]) == "LIVE",
        "unrelated_language_retained": language_ok("language_after_generator_revoke"),
        "generator_restored": math_ok("math_generator_restored")
            and rows["math_generator_restored"]["selected"] == CATALOGUE[1],
        "wrong_output_refused": rows["wrong_output"]["admitted_id"] is None,
        "missing_checker_refused": rows["missing_checker"]["admitted_id"] is None
            and rows["missing_checker"]["status"] == "CANNOT_CHECK",
        "wrong_scope_refused": rows["wrong_scope"]["admitted_id"] is None
            and rows["wrong_scope"]["trace"]["stages"][-1]["reason"] == "REFUSED:OUT_OF_SCOPE",
        "budget_exhaustion_refused": rows["exhausted"]["admitted_id"] is None,
        "input_payload_cannot_select_checker": rows["checker_injection"]["status"] == "INPUT_REFUSED",
    }
    from vessel_parents import run as run_parents
    parent = run_parents(root, language, polynomial)
    parent["terminal"] = ("PARENT_SUFFICIENT_AT_TINY_CAPABILITY_SCOPE" if parent["polynomial"]["checked"]
        and parent["language"]["digest"] == expected_language else "CANNOT_CHECK_PARENT_CAPABILITY")
    checks["independent_catalogue_parent"] = (parent["independently_executed"]
        and not parent["shared_solver_invoked"] and parent["polynomial"]["enumerated_programs"] == 341
        and parent["polynomial"]["checked"] and parent["language"]["digest"] == expected_language)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"claim_scope": "trusted-host same-loop engineering gate", "checks": checks,
        "passed": all(checks.values()), "rows": rows, "lifecycle_events": events, "comparator": parent,
        "terminal": "COMMON_LOOP_SUPPORTED_AT_TINY_REGISTERED_SCOPE" if all(checks.values()) else "GATE_FAILED",
        "measurements": {"wall_seconds": time.perf_counter() - wall,
            "cpu_seconds": time.process_time() - cpu + children.ru_utime + children.ru_stime
                - children_before.ru_utime - children_before.ru_stime,
            "persistent_bytes": sum(p.stat().st_size for p in root.rglob("*") if p.is_file()),
            "adapter_source_bytes": setup["identity"]["adapter_source_bytes"],
            "reused_implementation_sources": setup["identity"]["reused_implementation_sources"]},
        "unmeasured": ["energy", "exact active-state bytes", "allocator-resident field bytes",
            "dependency installation and parent-process imports before study", "fine-grained replay/hash/index IO work", "total prior information content", "installed dependency artifact hashes"],
        "limits": ["global navigation and hashing remain; stage counts are proxies", "no immutable process isolation",
            "no continued acquisition after restart claim", "no compression utility or strong-LLM parity claim",
            "independent parents establish tiny task capability, not matched lifelong governance"]}
