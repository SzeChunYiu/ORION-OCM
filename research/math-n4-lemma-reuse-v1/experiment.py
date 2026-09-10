"""MATH-1 / N4 remaining-gate microscope: causal lemma reuse at Hilbert scope.

Bounded positive implicational calculus. Not Metamath N4 close, not FLT, and not
unscoped CAUSAL_PROOF_METHOD_REUSE_SUPPORTED. The Metamath LIBRARY-ARTIFACT is an
off-host custody pointer; this experiment uses an exact miniature kernel instead.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import kernel as K  # noqa: E402

SCHEMA = "math-n4-lemma-reuse.result.v1"
CONSUMER_MP_BUDGET = 4000
PRIMITIVE_ACQUIRE_SIZE = 4
LIBRARY_CONSUMER_SIZE = 2
FAMILY_A_IDS = ("task:family-a-uvw", "task:family-a-u2v2w2")
FAMILY_B_IDS = ("task:family-b-xyz", "task:family-b-x2y2z2")
FRESH_ID = "task:fresh-pqr"
VALIDATE_PREFIX_ATOMS = {"A": "i", "B": "j", "C": "k"}
VALIDATE_SWAP_ATOMS = {"A": "l", "B": "m", "C": "n"}
FRESH_ATOMS = {"A": "p", "B": "q", "C": "r"}
# Frozen SK catalog is declared prior information for family-B SWAP admission.
# Size-4 exhaustive search does not inhabit SWAP; C is the catalog hit.
SK_CATALOG = (("I", K.I_TERM), ("B", K.B_TERM), ("C", K.C_TERM))
LIBRARY_ARTIFACT = (
    REPO / "research" / "ordinary-goal-cohort-result-v1"
    / "records" / "qualification-01" / "LIBRARY-ARTIFACT.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rss_kib() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def cost_vector(search: dict, check: dict, storage: dict, acquisition: dict) -> dict:
    return {
        "search": search,
        "check": check,
        "storage": storage,
        "acquisition": acquisition,
    }


def inspect_metamath_library() -> dict[str, Any]:
    if not LIBRARY_ARTIFACT.is_file():
        return {
            "present": False,
            "runtime_available": False,
            "disposition": "MISSING_LIBRARY_ARTIFACT",
        }
    data = json.loads(LIBRARY_ARTIFACT.read_text(encoding="utf-8"))
    joined = Path(data.get("joined_prefix", {}).get("path") or "")
    return {
        "present": True,
        "bytes": LIBRARY_ARTIFACT.stat().st_size,
        "sha256": sha256_file(LIBRARY_ARTIFACT),
        "runtime_available": joined.is_file(),
        "joined_prefix_exists": joined.is_file(),
        "disposition": (
            "METAMATH_RUNTIME_AVAILABLE"
            if joined.is_file()
            else "MINIATURE_HILBERT_MICROSCOPE"
        ),
        "reason": (
            "Joined prefix is on disk."
            if joined.is_file()
            else "LIBRARY-ARTIFACT.json is a custody pointer to an off-host Metamath prefix; no kernel runtime in this environment."
        ),
    }


def neural_status() -> str:
    for name in ("torch", "transformers", "tensorflow"):
        if importlib.util.find_spec(name) is not None:
            # Package importability is not a prover. No weights are loaded.
            return "CANNOT_CHECK_NO_NEURAL_PROVER_IN_THIS_ENVIRONMENT"
    return "CANNOT_CHECK_NO_NEURAL_PROVER_IN_THIS_ENVIRONMENT"


def goal_prefix(atoms: dict[str, str]) -> K.Formula:
    return K.instantiate_schema(K.PREFIX_SCHEMA, atoms)


def goal_swap(atoms: dict[str, str]) -> K.Formula:
    return K.instantiate_schema(K.SWAP_SCHEMA, atoms)


def goal_suffix(atoms: dict[str, str]) -> K.Formula:
    return K.instantiate_schema(K.SUFFIX_SCHEMA, atoms)


def result_summary(row: K.SearchResult) -> dict[str, Any]:
    payload = row.as_dict()
    payload["conclusion"] = K.pretty(row.proof.conclusion) if row.proof is not None else None
    payload["subgoal_count"] = len(row.subgoals)
    payload["subgoals"] = [K.pretty(s) for s in row.subgoals[:8]]
    return payload


def acquire_prefix(training: tuple[tuple[str, K.Formula], ...]) -> dict[str, Any]:
    start = time.perf_counter()
    found_terms = []
    rows = []
    for task_id, goal in training:
        row = K.inhabit_well_typed(goal, ("S", "K"), {}, PRIMITIVE_ACQUIRE_SIZE)
        if row.status != "FOUND" or row.term is None:
            raise RuntimeError(f"family A failed to inhabit {task_id}")
        proof = K.reconstruct_proof(row.term, goal)
        if K.check_proof(proof) != goal:
            raise RuntimeError(f"family A kernel mismatch {task_id}")
        found_terms.append(row.term)
        rows.append({
            "task_id": task_id,
            "goal": K.pretty(goal),
            "term": K.term_pretty(row.term),
            "search": row.costs.as_dict(),
            "proof_length": len(proof.steps),
        })
    if len({K.term_pretty(term) for term in found_terms}) != 1:
        raise RuntimeError("family A proofs did not anti-unify to one combinator")
    witness = found_terms[0]
    lemma = K.Lemma(
        lemma_id="PREFIX",
        schema=K.PREFIX_SCHEMA,
        witness_term=witness,
        support_ids=tuple(task_id for task_id, _goal in training),
        authorized=True,
    )
    holdout = goal_prefix(VALIDATE_PREFIX_ATOMS)
    holdout_proof = K.reconstruct_proof(witness, holdout)
    K.check_proof(holdout_proof)
    return {
        "lemma": lemma,
        "rows": rows,
        "holdout": {
            "goal": K.pretty(holdout),
            "proof_length": len(holdout_proof.steps),
            "kernel_ok": K.check_proof(holdout_proof) == holdout,
        },
        "wall_s": time.perf_counter() - start,
        "search_nodes": sum(r["search"]["nodes"] for r in rows),
        "terms_enumerated": sum(r["search"]["terms_enumerated"] for r in rows),
        "kernel_checks": 2 + len(rows),
    }


def acquire_swap(training: tuple[tuple[str, K.Formula], ...]) -> dict[str, Any]:
    start = time.perf_counter()
    size4_rows = []
    for task_id, goal in training:
        row = K.inhabit_well_typed(goal, ("S", "K"), {}, PRIMITIVE_ACQUIRE_SIZE)
        size4_rows.append({
            "task_id": task_id,
            "status": row.status,
            "terms_enumerated": row.costs.terms_enumerated,
            "nodes": row.costs.nodes,
        })
        if row.status == "FOUND":
            raise RuntimeError("SWAP was inhabited at size 4; catalog would be redundant")
    catalog_hits = []
    catalog_checks = 0
    for name, term in SK_CATALOG:
        ok = True
        for _task_id, goal in training:
            catalog_checks += 1
            if not K.term_unifies_goal(term, goal):
                ok = False
                break
        if ok:
            catalog_hits.append(name)
    if catalog_hits != ["C"]:
        raise RuntimeError(f"expected unique catalog hit C, got {catalog_hits}")
    witness = K.C_TERM
    proofs = []
    for task_id, goal in training:
        proof = K.reconstruct_proof(witness, goal)
        if K.check_proof(proof) != goal:
            raise RuntimeError(f"family B kernel mismatch {task_id}")
        proofs.append({
            "task_id": task_id,
            "goal": K.pretty(goal),
            "proof_length": len(proof.steps),
        })
    lemma = K.Lemma(
        lemma_id="SWAP",
        schema=K.SWAP_SCHEMA,
        witness_term=witness,
        support_ids=tuple(task_id for task_id, _goal in training),
        authorized=True,
    )
    holdout = goal_swap(VALIDATE_SWAP_ATOMS)
    holdout_proof = K.reconstruct_proof(witness, holdout)
    K.check_proof(holdout_proof)
    return {
        "lemma": lemma,
        "size4_misses": size4_rows,
        "catalog": [name for name, _term in SK_CATALOG],
        "catalog_hits": catalog_hits,
        "catalog_prior_information": True,
        "rows": proofs,
        "holdout": {
            "goal": K.pretty(holdout),
            "proof_length": len(holdout_proof.steps),
            "kernel_ok": K.check_proof(holdout_proof) == holdout,
        },
        "wall_s": time.perf_counter() - start,
        "search_nodes": sum(r["nodes"] for r in size4_rows),
        "terms_enumerated": sum(r["terms_enumerated"] for r in size4_rows),
        "kernel_checks": catalog_checks + len(proofs) + 1,
    }


def persist_library(path: Path, lemmas: dict[str, K.Lemma]) -> int:
    payload = {
        "schema": "math-n4-lemma-reuse.library.v1",
        "lemmas": [K.lemma_to_json(lemma) for lemma in lemmas.values()],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path.stat().st_size


def load_library(path: Path) -> dict[str, K.Lemma]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    lemmas = {}
    for row in payload["lemmas"]:
        lemma = K.lemma_from_json(row)
        lemmas[lemma.lemma_id] = lemma
    return lemmas


def revoke_support(lemmas: dict[str, K.Lemma], withdrawn: set[str]) -> dict[str, K.Lemma]:
    out = {}
    for lemma_id, lemma in lemmas.items():
        authorized = lemma.authorized and not (set(lemma.support_ids) & withdrawn)
        out[lemma_id] = K.Lemma(
            lemma_id=lemma.lemma_id,
            schema=lemma.schema,
            witness_term=lemma.witness_term,
            support_ids=lemma.support_ids,
            authorized=authorized,
        )
    return out


def authorized_only(lemmas: dict[str, K.Lemma]) -> dict[str, K.Lemma]:
    return {k: v for k, v in lemmas.items() if v.authorized}


def consume(goal: K.Formula, lemmas: dict[str, K.Lemma], mp_budget: int = CONSUMER_MP_BUDGET) -> K.SearchResult:
    return K.goal_only_mp_search(goal, authorized_only(lemmas), max_mp=mp_budget)


def restart_consumer(library_path: Path, goal: K.Formula) -> dict[str, Any]:
    goal_path = library_path.parent / "goal.json"
    out_path = library_path.parent / "restart-result.json"
    goal_path.write_text(json.dumps(K.formula_to_json(goal)) + "\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable, "-B", str(HERE / "experiment.py"),
            "--restart-consumer",
            "--library", str(library_path),
            "--goal", str(goal_path),
            "--out", str(out_path),
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO),
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"restart failed rc={proc.returncode}: {proc.stderr[-2000:]} {proc.stdout[-2000:]}"
        )
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    payload["returncode"] = proc.returncode
    payload["parent_pid"] = os.getpid()
    return payload


def run_restart_consumer(library: Path, goal_path: Path) -> dict[str, Any]:
    lemmas = load_library(library)
    goal = K.json_to_formula(json.loads(goal_path.read_text(encoding="utf-8")))
    row = consume(goal, lemmas)
    return {
        "pid": os.getpid(),
        "status": row.status,
        "lemmas_used": list(row.lemmas_used),
        "one_step_hits": list(row.one_step_hits),
        "proof_length": len(row.proof.steps) if row.proof else None,
        "mp_attempts": row.costs.mp_attempts,
        "kernel_checks": row.costs.kernel_checks,
        "subgoals": [K.pretty(s) for s in row.subgoals[:8]],
    }


def failure_attempt_study() -> dict[str, Any]:
    dead_a = K.imp(K.imp("a", "a"), "a")
    dead_b = K.imp(K.imp("b", "b"), "b")
    success = K.imp("b", "b")
    memory = K.FailureMemory()
    first = K.inhabit_by_enumeration(dead_a, ("S", "K"), {}, 3, failure_memory=memory)
    before = len(memory.nogoods)
    second = K.inhabit_by_enumeration(dead_b, ("S", "K"), {}, 3, failure_memory=memory)
    live = K.inhabit_well_typed(success, ("S", "K"), {}, 3)
    return {
        "first_task_id": "task:dead-a",
        "second_task_id": "task:dead-b",
        "success_task_id": "task:live-b-identity",
        "first_status": first.status,
        "second_status": second.status,
        "success_status": live.status,
        "nogoods_after_first": before,
        "skipped_on_second": second.skipped_nogoods,
        "second_terms_enumerated": second.costs.terms_enumerated,
        "first_terms_enumerated": first.costs.terms_enumerated,
        "memory_contains_first_task_id": memory.contains_task_id("task:dead-a"),
        "memory_contains_second_task_id": memory.contains_task_id("task:dead-b"),
        "nogood_shapes": memory.as_list()[:12],
        "keyed_by_alpha_shape": True,
        "not_task_id_blacklist": (
            not memory.contains_task_id("task:dead-a")
            and not memory.contains_task_id("task:dead-b")
        ),
        "success_outside_failure_scope": live.status == "FOUND",
        "compatible_dead_end_skipped": second.skipped_nogoods > 0,
    }


def decide_terminal(payload: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    fresh = payload["fresh"]
    both = fresh["both"]
    invoked = set(both["lemmas_used"]) == {"PREFIX", "SWAP"}
    found = both["status"] == "FOUND"
    one_step_zero = list(fresh["one_step_hits"]) == []
    prefix_only_fail = fresh["prefix_only"]["status"] != "FOUND"
    swap_only_fail = fresh["swap_only"]["status"] != "FOUND"
    primitive_fail = fresh["primitive"]["status"] != "FOUND"
    ablation_harder = (
        fresh["prefix_only"]["costs"]["mp_attempts"] > both["costs"]["mp_attempts"]
        and fresh["swap_only"]["costs"]["mp_attempts"] > both["costs"]["mp_attempts"]
    )
    restart_ok = (
        payload["restart"]["status"] == "FOUND"
        and set(payload["restart"]["lemmas_used"]) == {"PREFIX", "SWAP"}
        and payload["restart"]["pid"] != os.getpid()
    )
    revoke_prefix_ok = payload["revocation"]["revoke_prefix"]["status"] != "FOUND"
    revoke_swap_ok = payload["revocation"]["revoke_swap"]["status"] != "FOUND"
    revoke_both_matches_primitive = (
        payload["revocation"]["revoke_both"]["status"] == fresh["primitive"]["status"]
    )
    restore_ok = payload["revocation"]["restore"]["status"] == "FOUND"
    failure_ok = (
        payload["failure_attempts"]["not_task_id_blacklist"]
        and payload["failure_attempts"]["compatible_dead_end_skipped"]
        and payload["failure_attempts"]["success_outside_failure_scope"]
    )
    subgoals = bool(both.get("subgoals"))
    holdout_disjoint = payload["partition"]["fresh_atoms_disjoint_from_acquisition"]
    criteria = {
        "fresh_found_with_both_lemmas": found and invoked,
        "one_step_zero_on_composition": one_step_zero,
        "primitive_cannot_at_budget": primitive_fail,
        "prefix_ablation_loses_proof": prefix_only_fail,
        "swap_ablation_loses_proof": swap_only_fail,
        "ablation_increases_mp_cost": ablation_harder,
        "os_process_restart": restart_ok,
        "revoke_prefix_restores_weaker_search": revoke_prefix_ok,
        "revoke_swap_restores_weaker_search": revoke_swap_ok,
        "revoke_both_matches_primitive": revoke_both_matches_primitive,
        "restore_returns_lemma_use": restore_ok,
        "failure_memory_shape_not_task_id": failure_ok,
        "subgoal_intermediates_recorded": subgoals,
        "fresh_atoms_held_out": holdout_disjoint,
    }
    if all(criteria.values()):
        return "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE", criteria
    if not found or not invoked:
        return "NO_CAUSAL_REUSE", criteria
    return "NO_CAUSAL_REUSE", criteria


def run() -> dict[str, Any]:
    started = time.perf_counter()
    library_note = inspect_metamath_library()
    family_a = (
        (FAMILY_A_IDS[0], goal_prefix({"A": "u", "B": "v", "C": "w"})),
        (FAMILY_A_IDS[1], goal_prefix({"A": "u2", "B": "v2", "C": "w2"})),
    )
    family_b = (
        (FAMILY_B_IDS[0], goal_swap({"A": "x", "B": "y", "C": "z"})),
        (FAMILY_B_IDS[1], goal_swap({"A": "x2", "B": "y2", "C": "z2"})),
    )
    fresh_goal = goal_suffix(FRESH_ATOMS)
    acquisition_atoms = {
        "u", "v", "w", "u2", "v2", "w2",
        "x", "y", "z", "x2", "y2", "z2",
        "i", "j", "k", "l", "m", "n",
    }
    fresh_atoms = set(FRESH_ATOMS.values())

    acq_a = acquire_prefix(family_a)
    acq_b = acquire_swap(family_b)
    lemmas = {"PREFIX": acq_a["lemma"], "SWAP": acq_b["lemma"]}

    one_step = K.one_step_screen(fresh_goal, lemmas)
    primitive = consume(fresh_goal, {})
    prefix_only = consume(fresh_goal, {"PREFIX": lemmas["PREFIX"]})
    swap_only = consume(fresh_goal, {"SWAP": lemmas["SWAP"]})
    both = consume(fresh_goal, lemmas)
    both_lib = K.inhabit_well_typed(
        fresh_goal, ("S", "K", "PREFIX", "SWAP"), lemmas, LIBRARY_CONSUMER_SIZE,
    )

    top1_ids = K.retrieve_nearest_lemmas(fresh_goal, lemmas, 1)
    top2_ids = K.retrieve_nearest_lemmas(fresh_goal, lemmas, 2)
    retrieval_top1 = consume(fresh_goal, {i: lemmas[i] for i in top1_ids})
    retrieval_top2 = consume(fresh_goal, {i: lemmas[i] for i in top2_ids})

    with tempfile.TemporaryDirectory(prefix="math-n4-lemma-") as temp:
        root = Path(temp)
        library_path = root / "library.json"
        storage_bytes = persist_library(library_path, lemmas)
        loaded = load_library(library_path)
        restart = restart_consumer(library_path, fresh_goal)
        revoked_prefix = revoke_support(loaded, set(FAMILY_A_IDS))
        revoked_swap = revoke_support(loaded, set(FAMILY_B_IDS))
        revoked_both = revoke_support(loaded, set(FAMILY_A_IDS) | set(FAMILY_B_IDS))
        revoke_p = consume(fresh_goal, revoked_prefix)
        revoke_s = consume(fresh_goal, revoked_swap)
        revoke_b = consume(fresh_goal, revoked_both)
        restored = consume(fresh_goal, loaded)

    failures = failure_attempt_study()
    wall = time.perf_counter() - started

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "issue": 165,
        "lane": "MATH-1",
        "scope": "bounded MATH-1 microscope; not N4 completion of Metamath",
        "domain": "positive implicational Hilbert calculus / typed SK combinatory logic",
        "metamath_library": library_note,
        "do_not_expand_flt": True,
        "unscoped_causal_reuse_not_claimed": True,
        "partition": {
            "family_a_ids": list(FAMILY_A_IDS),
            "family_b_ids": list(FAMILY_B_IDS),
            "fresh_id": FRESH_ID,
            "fresh_goal": K.pretty(fresh_goal),
            "fresh_atoms": sorted(fresh_atoms),
            "acquisition_atoms": sorted(acquisition_atoms),
            "fresh_atoms_disjoint_from_acquisition": fresh_atoms.isdisjoint(acquisition_atoms),
        },
        "acquisition": {
            "prefix": {k: v for k, v in acq_a.items() if k != "lemma"},
            "swap": {k: v for k, v in acq_b.items() if k != "lemma"},
            "representation_introduced": ["PREFIX", "SWAP"],
            "operators_before": ["K", "S", "MP"],
            "operators_after": ["K", "S", "MP", "PREFIX", "SWAP"],
        },
        "fresh": {
            "one_step_hits": list(one_step),
            "one_step_invocations": len(one_step),
            "primitive": result_summary(primitive),
            "prefix_only": result_summary(prefix_only),
            "swap_only": result_summary(swap_only),
            "both": result_summary(both),
            "library_inhabitation": result_summary(both_lib),
        },
        "retrieval_parent": {
            "method": "bag-of-symbols Jaccard after alpha-normalization",
            "top1_ids": list(top1_ids),
            "top2_ids": list(top2_ids),
            "top1": result_summary(retrieval_top1),
            "top2": result_summary(retrieval_top2),
        },
        "restart": restart,
        "revocation": {
            "revoke_prefix": result_summary(revoke_p),
            "revoke_swap": result_summary(revoke_s),
            "revoke_both": result_summary(revoke_b),
            "restore": result_summary(restored),
        },
        "failure_attempts": failures,
        "neural_guided_prover": neural_status(),
        "transformer_proof_reference": neural_status(),
        "costs": cost_vector(
            search={
                "fresh_both_mp_attempts": both.costs.mp_attempts,
                "fresh_primitive_mp_attempts": primitive.costs.mp_attempts,
                "fresh_prefix_only_mp_attempts": prefix_only.costs.mp_attempts,
                "fresh_swap_only_mp_attempts": swap_only.costs.mp_attempts,
                "fresh_both_nodes": both.costs.nodes,
                "library_inhabitation_terms": both_lib.costs.terms_enumerated,
                "consumer_mp_budget": CONSUMER_MP_BUDGET,
            },
            check={
                "fresh_both_kernel_checks": both.costs.kernel_checks,
                "fresh_both_kernel_rejects": both.costs.kernel_rejects,
                "acquisition_kernel_checks": acq_a["kernel_checks"] + acq_b["kernel_checks"],
            },
            storage={
                "library_bytes": storage_bytes,
                "lemma_count": 2,
                "failure_memory_entries": failures["nogoods_after_first"],
            },
            acquisition={
                "prefix_wall_s": acq_a["wall_s"],
                "swap_wall_s": acq_b["wall_s"],
                "prefix_terms_enumerated": acq_a["terms_enumerated"],
                "swap_terms_enumerated": acq_b["terms_enumerated"],
                "prefix_search_nodes": acq_a["search_nodes"],
                "swap_search_nodes": acq_b["search_nodes"],
                "catalog_prior_information": True,
                "catalog": [name for name, _term in SK_CATALOG],
            },
        ),
        "process": {
            "pid": os.getpid(),
            "max_rss_kib": rss_kib(),
            "study_wall_s": wall,
        },
        "claim_boundary": (
            "Causal lemma reuse is supported only in this miniature Hilbert/SK "
            "microscope. It does not close MATH-1 / N4 for Metamath, does not "
            "expand FLT, and does not emit unscoped CAUSAL_PROOF_METHOD_REUSE_SUPPORTED."
        ),
    }
    terminal, criteria = decide_terminal(payload)
    payload["terminal"] = terminal
    payload["criteria"] = criteria
    payload["n4_metamath_status"] = "OPEN"
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    parser.add_argument("--restart-consumer", action="store_true")
    parser.add_argument("--library", type=Path)
    parser.add_argument("--goal", type=Path)
    args = parser.parse_args()
    if args.restart_consumer:
        if args.library is None or args.goal is None:
            raise SystemExit("--library and --goal are required for --restart-consumer")
        result = run_restart_consumer(args.library, args.goal)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"pid": result["pid"], "status": result["status"], "lemmas_used": result["lemmas_used"]}))
        return
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": result["terminal"],
        "one_step_invocations": result["fresh"]["one_step_invocations"],
        "lemmas_used": result["fresh"]["both"]["lemmas_used"],
        "primitive": result["fresh"]["primitive"]["status"],
        "ablation_prefix": result["fresh"]["prefix_only"]["status"],
        "ablation_swap": result["fresh"]["swap_only"]["status"],
        "mp_both": result["fresh"]["both"]["costs"]["mp_attempts"],
        "mp_prefix_only": result["fresh"]["prefix_only"]["costs"]["mp_attempts"],
        "mp_swap_only": result["fresh"]["swap_only"]["costs"]["mp_attempts"],
        "restart_pid": result["restart"]["pid"],
        "neural": result["neural_guided_prover"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
