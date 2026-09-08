"""Fresh consumer: load sealed lemmas only if the arm says so. No producer traces."""
import argparse
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]

import load_inputs as L
import screen_heldout as S


def rss_kib(usage):
    raw = usage.ru_maxrss
    if platform.system() == "Darwin":
        return int(raw / 1024)
    return int(raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--arm", required=True, choices=("RESET_OCM", "P1_LEMMAS", "ABLATION", "MM_PARENT"))
    parser.add_argument("--lemmas", default="")
    args = parser.parse_args()
    start = time.perf_counter()
    usage0 = resource.getrusage(resource.RUSAGE_SELF)
    output = Path(args.output)
    if output.exists():
        raise ValueError("output already exists")
    output.mkdir(parents=True)
    p1 = L.load_p1()
    held = L.load_heldout()
    lemmas = []
    disabled = []
    if args.lemmas:
        sealed = json.loads(Path(args.lemmas).read_text())
        lemmas = sealed["ordinary_parent_rows"]
        if args.arm == "ABLATION":
            disabled = [row["label"] for row in lemmas]
            lemmas = []
    if args.arm in ("RESET_OCM", "ABLATION"):
        parent = p1
    else:
        parent = p1 + lemmas
    work = {}
    screened = S.screen_family(held["theorems"], parent, work)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "schema": "g2.heldout-consumer.v1",
        "arm": args.arm,
        "pid": os.getpid(),
        "fresh_process": True,
        "heldout_family": held["family"],
        "heldout_ordinals": held["ordinals"],
        "heldout_n": len(held["theorems"]),
        "parent_n": len(parent),
        "p1_n": len(p1),
        "lemmas_installed": 0 if args.arm in ("RESET_OCM", "ABLATION") else len(lemmas),
        "lemmas_disabled": disabled,
        "native_calls": 0,
        "native_acceptance": "UNKNOWN",
        "lemma_consumed": screened["lemma_consumed"],
        "consumed_labels": screened["consumed_labels"],
        "status_counts": screened["status_counts"],
        "theorems": screened["theorems"],
        "work": work,
        "acquisition_labels_excluded": True,
        "wall_s": time.perf_counter() - start,
        "user_cpu_s": usage.ru_utime - usage0.ru_utime,
        "system_cpu_s": usage.ru_stime - usage0.ru_stime,
        "max_rss_kib": rss_kib(usage),
        "platform": platform.platform(),
        "argv": sys.argv,
    }
    (output / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    (output / "PROCESS.json").write_text(json.dumps({
        "pid": os.getpid(),
        "arm": args.arm,
        "lemma_consumed": result["lemma_consumed"],
        "wall_s": result["wall_s"],
        "user_cpu_s": result["user_cpu_s"],
        "system_cpu_s": result["system_cpu_s"],
        "max_rss_kib": result["max_rss_kib"],
        "native_calls": 0,
    }, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
