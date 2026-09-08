"""Restarted producer then four held-out arms. Native success is not invented."""
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPSULE = HERE.parent


def rss_kib(usage):
    raw = usage.ru_maxrss
    if platform.system() == "Darwin":
        return int(raw / 1024)
    return int(raw)


def run(args, cwd):
    completed = subprocess.run(args, cwd=cwd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise SystemExit("child failed: " + " ".join(args) + "\n" + completed.stderr + completed.stdout)
    return completed


def load(path):
    return json.loads(Path(path).read_text())


def main(output):
    start = time.perf_counter()
    usage0 = resource.getrusage(resource.RUSAGE_SELF)
    output = Path(output)
    if output.exists():
        raise ValueError("output already exists")
    output.mkdir(parents=True)
    python = sys.executable
    producer = output / "producer-01"
    run([python, str(HERE / "producer.py"), str(producer)], CAPSULE.parent.parent)
    lemmas_path = producer / "LEMMAS.json"
    sealed = load(lemmas_path)
    arms = [
        ("RESET_OCM", output / "arm-reset-ocm", []),
        ("P1_LEMMAS", output / "arm-p1-lemmas", ["--lemmas", str(lemmas_path)]),
        ("ABLATION", output / "arm-ablation", ["--lemmas", str(lemmas_path)]),
        ("MM_PARENT", output / "arm-mm-parent", ["--lemmas", str(lemmas_path)]),
    ]
    child = []
    for arm, dest, extra in arms:
        argv = [python, str(HERE / "consumer.py"), str(dest), "--arm", arm, *extra]
        run(argv, CAPSULE.parent.parent)
        child.append(load(dest / "RESULT.json"))
    by_arm = {row["arm"]: row for row in child}
    reset, plus, ablation, parent = (by_arm[k] for k in ("RESET_OCM", "P1_LEMMAS", "ABLATION", "MM_PARENT"))
    consumed = plus["lemma_consumed"] or parent["lemma_consumed"]
    same_reset_ablation = reset["status_counts"] == ablation["status_counts"]
    same_plus_parent = plus["status_counts"] == parent["status_counts"]
    all_negative = plus["status_counts"].get("SCREENED_NEGATIVE_IN_DOMAIN") == plus["heldout_n"]
    kinds = sealed["abstraction_counts"]
    if consumed and not ablation["lemma_consumed"] and plus["status_counts"] != reset["status_counts"]:
        terminal = "CAUSAL_METHOD_REUSE_SUPPORTED"
    elif sealed["all_two_semantic_p1_steps"] and all_negative and not consumed:
        terminal = "NO_NEW_ABSTRACTION"
    elif not consumed:
        terminal = "NO_CAUSAL_REUSE_IN_ONE_STEP_DOMAIN"
    else:
        terminal = "UNKNOWN"
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "schema": "g2.causal-lemma-reuse.v1",
        "terminal": terminal,
        "pid": os.getpid(),
        "native_calls": 0,
        "native_acceptance": "UNKNOWN",
        "g2_4_causal_use_box": "NOT_YET" if terminal != "CAUSAL_METHOD_REUSE_SUPPORTED" else "SUPPORTED_IN_SCOPE",
        "causal_method_reuse_supported": terminal == "CAUSAL_METHOD_REUSE_SUPPORTED",
        "lemma_occurrences": sealed["n_occurrences"],
        "unique_lemmas": sealed["n_unique"],
        "abstraction_counts": kinds,
        "all_two_semantic_p1_steps": sealed["all_two_semantic_p1_steps"],
        "heldout_family": reset["heldout_family"],
        "heldout_ordinals": reset["heldout_ordinals"],
        "heldout_n": reset["heldout_n"],
        "lemma_consumed_on_fresh_task": consumed,
        "consumed_labels": plus["consumed_labels"],
        "arms": {
            "RESET_OCM": {"status_counts": reset["status_counts"], "lemma_consumed": reset["lemma_consumed"], "wall_s": reset["wall_s"], "pid": reset["pid"]},
            "P1_LEMMAS": {"status_counts": plus["status_counts"], "lemma_consumed": plus["lemma_consumed"], "lemmas_installed": plus["lemmas_installed"], "wall_s": plus["wall_s"], "pid": plus["pid"]},
            "ABLATION": {"status_counts": ablation["status_counts"], "lemma_consumed": ablation["lemma_consumed"], "lemmas_disabled": ablation["lemmas_disabled"], "wall_s": ablation["wall_s"], "pid": ablation["pid"]},
            "MM_PARENT": {"status_counts": parent["status_counts"], "lemma_consumed": parent["lemma_consumed"], "lemmas_installed": parent["lemmas_installed"], "native_acceptance": "UNKNOWN", "wall_s": parent["wall_s"], "pid": parent["pid"], "note": "Same ordinary $p rows as P1_LEMMAS. Metamath fragment written by producer; frozen PREFIX pin does not authorize successor native population."},
        },
        "ablation_matches_reset": same_reset_ablation,
        "mm_parent_matches_p1_lemmas": same_plus_parent,
        "distinct_consumer_pids": len({row["pid"] for row in child}) == 4,
        "producer_pid": load(producer / "PROCESS.json")["pid"],
        "producer_exited_before_consumers": True,
        "two_step_search": {"status": "NOT_IN_REGISTERED_ONE_STEP_DOMAIN", "note": "Held-out one-step matching is the revival screening domain. A broader 2-decision bank search was not registered and is not reported as a negative alias claim."},
        "measured_windows": {
            "wall_s": time.perf_counter() - start,
            "user_cpu_s": usage.ru_utime - usage0.ru_utime,
            "system_cpu_s": usage.ru_stime - usage0.ru_stime,
            "max_rss_kib": rss_kib(usage),
            "platform": platform.platform(),
            "nested_not_additive": True,
            "not_lifetime_cost": True,
            "children": {
                "producer": load(producer / "PROCESS.json"),
                "RESET_OCM": {"wall_s": reset["wall_s"], "user_cpu_s": reset["user_cpu_s"], "max_rss_kib": reset["max_rss_kib"]},
                "P1_LEMMAS": {"wall_s": plus["wall_s"], "user_cpu_s": plus["user_cpu_s"], "max_rss_kib": plus["max_rss_kib"]},
                "ABLATION": {"wall_s": ablation["wall_s"], "user_cpu_s": ablation["user_cpu_s"], "max_rss_kib": ablation["max_rss_kib"]},
                "MM_PARENT": {"wall_s": parent["wall_s"], "user_cpu_s": parent["user_cpu_s"], "max_rss_kib": parent["max_rss_kib"]},
            },
        },
        "interpretation": "22 unique two-logical-step P1 compositions were compiled as ordinary $p from the frozen DAG. A chronological held-out family after ordinal 4223 was screened in fresh processes. No lemma identity was invoked. Native successor checking remains UNKNOWN.",
        "error": None,
    }
    (output / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    (output / "PROCESS.json").write_text(json.dumps({
        "pid": os.getpid(),
        "terminal": terminal,
        "wall_s": result["measured_windows"]["wall_s"],
        "native_calls": 0,
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "python": sys.version,
    }, sort_keys=True, indent=2) + "\n")
    return 0 if terminal in ("CAUSAL_METHOD_REUSE_SUPPORTED", "NO_NEW_ABSTRACTION", "NO_CAUSAL_REUSE_IN_ONE_STEP_DOMAIN") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
