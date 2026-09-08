"""Measure JSONL rewrite vs SQLite parents: N entries vs wall and bytes.

Writes raw per-append vectors plus summaries. Does not change production stores.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocm.store.ledger import LedgerStore
from ocm.store.sqlite_ledger import SQLiteLedgerStore
from wal_ledger import CheckpointedWALLedger

DEFAULT_NS = (64, 128, 256, 512, 1024, 2048)
PAYLOAD_PAD = "x" * 32


def _rss_bytes() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(usage)
    return int(usage) * 1024


def _dir_bytes(path: Path) -> int:
    return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _run_backend(
    name: str,
    factory: Callable[[Path], Any],
    n: int,
    work: Path,
) -> dict[str, Any]:
    root = work / name / f"n{n}"
    root.mkdir(parents=True)
    rss_before = _rss_bytes()
    store = factory(root)
    append_s: list[float] = []
    rewrite_bytes: list[int] = []
    prev_dir = _dir_bytes(root)
    ledger_path = getattr(store, "path", None)
    t0 = time.perf_counter()
    head = None
    for index in range(n):
        started = time.perf_counter()
        entry = store.append(
            "EVENT",
            {"i": index, "pad": PAYLOAD_PAD},
            expected_head=head,
        )
        append_s.append(time.perf_counter() - started)
        head = entry.entry_hash
        if name == "jsonl" and ledger_path is not None:
            # NamedTemporaryFile + os.replace writes the entire new file.
            rewrite_bytes.append(int(ledger_path.stat().st_size))
        else:
            now = _dir_bytes(root)
            rewrite_bytes.append(max(0, now - prev_dir))
            prev_dir = now
    total_s = time.perf_counter() - t0
    head_started = time.perf_counter()
    observed_head = store.head()
    head_s = time.perf_counter() - head_started
    assert observed_head is not None
    assert observed_head.sequence == n - 1
    restart_started = time.perf_counter()
    restarted = factory(root)
    restarted_head = restarted.head()
    restart_s = time.perf_counter() - restart_started
    assert restarted_head == observed_head
    suffix_rows = getattr(restarted, "suffix_rows_verified_on_open", None)
    snapshot_seq = getattr(restarted, "snapshot_sequence_on_open", None)
    extras: dict[str, Any] = {}
    if hasattr(store, "checkpoint"):
        extras["forced_checkpoint"] = store.checkpoint()
        extras["snapshot_count"] = store.snapshot_count()
        extras["kind_handle_count"] = store.kind_handle_count()
        extras["checkpoint_wall_s"] = store.checkpoint_wall_s
        extras["wal_checkpoint_wall_s"] = store.wal_checkpoint_wall_s
    if hasattr(store, "journal_mode"):
        extras["journal_mode"] = store.journal_mode()
    if hasattr(store, "physical_bytes"):
        extras["physical_bytes_method"] = store.physical_bytes()
    return {
        "backend": name,
        "n": n,
        "total_wall_s": total_s,
        "mean_append_s": sum(append_s) / n,
        "median_append_s": sorted(append_s)[n // 2],
        "first_append_s": append_s[0],
        "last_append_s": append_s[-1],
        "last8_mean_append_s": sum(append_s[-8:]) / min(8, n),
        "head_s": head_s,
        "restart_head_s": restart_s,
        "suffix_rows_verified_on_open": suffix_rows,
        "snapshot_sequence_on_open": snapshot_seq,
        "dir_bytes": _dir_bytes(root),
        "cumulative_rewrite_bytes": int(sum(rewrite_bytes)),
        "rss_max_bytes": _rss_bytes(),
        "rss_max_bytes_before": rss_before,
        "append_s": append_s,
        "rewrite_bytes": rewrite_bytes,
        **extras,
    }


def measure(ns: tuple[int, ...], work: Path) -> dict[str, Any]:
    factories: dict[str, Callable[[Path], Any]] = {
        "jsonl": LedgerStore,
        "sqlite_parent": SQLiteLedgerStore,
        "wal_checkpointed": lambda root: CheckpointedWALLedger(root, checkpoint_interval=64),
    }
    rows = []
    for n in ns:
        for name, factory in factories.items():
            rows.append(_run_backend(name, factory, n, work))
    return {
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": sys.version,
            "pid": os.getpid(),
        },
        "incumbent_ledger_sha256": _file_sha256(SRC / "ocm" / "store" / "ledger.py"),
        "sqlite_parent_sha256": _file_sha256(SRC / "ocm" / "store" / "sqlite_ledger.py"),
        "ns": list(ns),
        "payload_pad_chars": len(PAYLOAD_PAD),
        "rows": rows,
    }


def summarize(raw: dict[str, Any]) -> dict[str, Any]:
    by_backend: dict[str, list[dict[str, Any]]] = {}
    for row in raw["rows"]:
        slim = {
            key: value
            for key, value in row.items()
            if key not in {"append_s", "rewrite_bytes"}
        }
        by_backend.setdefault(row["backend"], []).append(slim)
    jsonl = {row["n"]: row for row in by_backend["jsonl"]}
    wal = {row["n"]: row for row in by_backend["wal_checkpointed"]}
    sqlite = {row["n"]: row for row in by_backend["sqlite_parent"]}
    last_n = max(raw["ns"])
    first_n = min(raw["ns"])
    jsonl_total = jsonl[last_n]["total_wall_s"]
    wal_total = wal[last_n]["total_wall_s"]
    sqlite_total = sqlite[last_n]["total_wall_s"]
    n_ratio = last_n / first_n
    return {
        "by_backend": by_backend,
        "last_n": last_n,
        "first_n": first_n,
        "n_ratio": n_ratio,
        "jsonl_total_s": jsonl_total,
        "sqlite_total_s": sqlite_total,
        "wal_total_s": wal_total,
        "jsonl_head_s": jsonl[last_n]["head_s"],
        "sqlite_head_s": sqlite[last_n]["head_s"],
        "wal_head_s": wal[last_n]["head_s"],
        "jsonl_cumulative_rewrite_bytes": jsonl[last_n]["cumulative_rewrite_bytes"],
        "sqlite_cumulative_rewrite_bytes": sqlite[last_n]["cumulative_rewrite_bytes"],
        "wal_cumulative_rewrite_bytes": wal[last_n]["cumulative_rewrite_bytes"],
        "total_speedup_vs_jsonl": {
            "sqlite_parent": jsonl_total / sqlite_total if sqlite_total else None,
            "wal_checkpointed": jsonl_total / wal_total if wal_total else None,
        },
        "jsonl_total_growth": jsonl_total / jsonl[first_n]["total_wall_s"],
        "sqlite_total_growth": sqlite_total / sqlite[first_n]["total_wall_s"],
        "wal_total_growth": wal_total / wal[first_n]["total_wall_s"],
        "jsonl_dir_bytes_last": jsonl[last_n]["dir_bytes"],
        "sqlite_dir_bytes_last": sqlite[last_n]["dir_bytes"],
        "wal_dir_bytes_last": wal[last_n]["dir_bytes"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "results")
    parser.add_argument(
        "--ns",
        type=int,
        nargs="+",
        default=list(DEFAULT_NS),
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="g5-physical-bench-") as tmp:
        raw = measure(tuple(args.ns), Path(tmp))
    summary = summarize(raw)
    raw_path = args.out / "scaling_raw.json"
    summary_path = args.out / "scaling_summary.json"
    raw_path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "raw": str(raw_path),
                "summary": str(summary_path),
                **{
                    key: summary[key]
                    for key in (
                        "last_n",
                        "jsonl_total_s",
                        "sqlite_total_s",
                        "wal_total_s",
                        "jsonl_head_s",
                        "sqlite_head_s",
                        "wal_head_s",
                        "jsonl_cumulative_rewrite_bytes",
                        "sqlite_cumulative_rewrite_bytes",
                        "wal_cumulative_rewrite_bytes",
                        "total_speedup_vs_jsonl",
                        "jsonl_total_growth",
                        "sqlite_total_growth",
                        "wal_total_growth",
                    )
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
