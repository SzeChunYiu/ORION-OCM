"""Run-directory layout + frozen IO helpers shared by centre and workers.

Layout under a run root::

    manifests/BATCH.json               frozen wave denominators (before submit)
    task_ledger.json                   TaskLedger state (centre-written only)
    generations/g{G}/suites.json       this generation's frozen suites
    generations/g{G}/incumbent.json    incumbent measured on those suites
    generations/g{G}/waves/w{W}/batch.json
    generations/g{G}/waves/w{W}/eval/{candidate_id}.json
    generations/g{G}/waves/w{W}/verify/{candidate_id}.json
    generations/g{G}/waves/w{W}/aggregate.json
    generations/g{G}/ADOPTION_PACKET.json / decision.json / cycle_receipt.json
    CANDIDATE_LEDGER.jsonl             append-only, one row per evaluation
    GENERATION_LEDGER.jsonl            one row per canonical generation cycle
    search_history.jsonl               measured rows feeding every arm equally
    DIVERSITY_ARCHIVE_V1.json          the QD archive (persists across gens)
    parents/{arm}/serial_state.json    serial controls (CONTINUED / RESET / PARENT)
    lineage/{mode}/                    PDEVLineage (canonical M11 cell)

Workers NEVER write anything outside their per-candidate file and the two
append-only ledgers; only the centre mutates state.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

CANDIDATE_LEDGER = "CANDIDATE_LEDGER.jsonl"
GENERATION_LEDGER = "GENERATION_LEDGER.jsonl"
SEARCH_HISTORY = "search_history.jsonl"


def run_paths(root: str) -> Dict[str, Path]:
    base = Path(root)
    out = {
        "root": base,
        "manifests": base / "manifests",
        "generations": base / "generations",
        "parents": base / "parents",
        "lineage": base / "lineage",
        "results": base / "results",
        "archive": base / "DIVERSITY_ARCHIVE_V1.json",
        "task_ledger": base / "task_ledger.json",
        "history": base / SEARCH_HISTORY,
        "candidate_ledger": base / CANDIDATE_LEDGER,
        "generation_ledger": base / GENERATION_LEDGER,
        "state": base / "generations" / "state.json",
    }
    for key in ("manifests", "generations", "parents", "lineage", "results"):
        out[key].mkdir(parents=True, exist_ok=True)
    return out


def gen_dir(root: str, generation: int) -> Path:
    path = Path(root) / "generations" / ("g%d" % generation)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_suites(root: str, generation: int) -> Dict[str, Any]:
    """Inner suite map from a generation's frozen suites.json payload."""
    payload = read_json(gen_dir(root, generation) / "suites.json")
    return payload["suites"]


def wave_dir(root: str, generation: int, wave: int) -> Path:
    path = gen_dir(root, generation) / "waves" / ("w%d" % wave)
    path.mkdir(parents=True, exist_ok=True)
    (path / "eval").mkdir(exist_ok=True)
    (path / "verify").mkdir(exist_ok=True)
    return path


def write_json(path, payload: Mapping[str, Any]) -> Dict[str, Any]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    os.replace(str(tmp), str(path))
    return dict(payload)


def read_json(path) -> Dict[str, Any]:
    with open(path) as handle:
        return json.load(handle)


def append_jsonl(path, row: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def read_jsonl(path) -> List[Dict[str, Any]]:
    try:
        with open(path) as handle:
            return [json.loads(line) for line in handle if line.strip()]
    except FileNotFoundError:
        return []


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execution_envelope(job_id: str, array_index: Optional[int]) -> Dict[str, Any]:
    return {"job_id": job_id, "array_index": array_index,
            "slurm_job_id": os.environ.get("SLURM_JOB_ID", ""),
            "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID", ""),
            "host": os.environ.get("SLURMD_NODENAME", ""),
            "submitted_unix": None,
            "written_unix": time.time()}
