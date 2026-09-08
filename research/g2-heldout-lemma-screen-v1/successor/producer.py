"""Producer: compile unique SCREENED_NEGATIVE cuts, seal ordinary $p lemmas, exit."""
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]

import compile_lemmas as C
import load_inputs as L


def rss_kib(usage):
    raw = usage.ru_maxrss
    if platform.system() == "Darwin":
        return int(raw / 1024)
    return int(raw)


def main(output):
    start = time.perf_counter()
    usage0 = resource.getrusage(resource.RUSAGE_SELF)
    output = Path(output)
    if output.exists():
        raise ValueError("output already exists")
    output.mkdir(parents=True)
    negatives = L.load_negatives()
    unique = L.unique_negatives(negatives)
    opportunity = L.load_opportunity()
    p1 = L.load_p1()
    bodies = L.cut_bodies(opportunity, [row["canonical_id"] for row in unique])
    work = {}
    lemmas = C.compile_all(unique, bodies, p1, work)
    kinds = {}
    for row in lemmas:
        kinds[row["abstraction"]] = kinds.get(row["abstraction"], 0) + 1
    sealed = {
        "schema": "g2.compiled-ordinary-lemmas.v1",
        "n_occurrences": negatives["occurrences"],
        "n_unique": len(lemmas),
        "native_calls": 0,
        "native_acceptance": "UNKNOWN",
        "native_reason": "Frozen PREFIX pin authorizes 4095 prefix theorems only. Successor P1+lemma library is not that pin. DAG proofs are replayable through typed_emit.",
        "abstraction_counts": kinds,
        "all_two_semantic_p1_steps": all(row["semantic_applications"] == 2 for row in lemmas),
        "lemmas": lemmas,
        "ordinary_parent_rows": C.ordinary_parent_rows(lemmas),
        "compile_work": work,
    }
    (output / "LEMMAS.json").write_text(json.dumps(sealed, sort_keys=True, indent=2) + "\n")
    mm = emit_mm_fragment(lemmas)
    (output / "LEMMAS.mm").write_text(mm)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    process = {
        "pid": os.getpid(),
        "role": "producer",
        "n_lemmas": len(lemmas),
        "native_calls": 0,
        "wall_s": time.perf_counter() - start,
        "user_cpu_s": usage.ru_utime - usage0.ru_utime,
        "system_cpu_s": usage.ru_stime - usage0.ru_stime,
        "max_rss_kib": rss_kib(usage),
        "lemma_bytes": (output / "LEMMAS.json").stat().st_size,
        "mm_bytes": (output / "LEMMAS.mm").stat().st_size,
        "platform": platform.platform(),
        "argv": sys.argv,
    }
    (output / "PROCESS.json").write_text(json.dumps(process, sort_keys=True, indent=2) + "\n")
    return 0


def emit_mm_fragment(lemmas):
    """Ordinary $p projection for the conventional Metamath parent. Not a checked library."""
    lines = [
        "$( Ordinary derived-lemma projection. Variables V0 V1 V2 stand for class parameters.",
        "   Native checking of a successor library is UNKNOWN under the frozen PREFIX pin. $)",
        "$v V0 V1 V2 $.",
        "cV0 $f class V0 $.",
        "cV1 $f class V1 $.",
        "cV2 $f class V2 $.",
        "",
    ]
    for row in lemmas:
        lines.append("${")
        for hyp in row["essential"]:
            lines.append(hyp["label"] + " $e " + " ".join(hyp["statement"]) + " $.")
        proof = " ".join(row["proof"]).replace("cut-f0", "cV0").replace("cut-f1", "cV1").replace("cut-f2", "cV2")
        lines.append(row["label"] + " $p " + " ".join(row["statement"]) + " $= " + proof + " $.")
        lines.append("$}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
