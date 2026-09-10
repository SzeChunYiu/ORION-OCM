"""GS failure memory (#221 sec 18 GS-R0): every failed evaluation task
auto-appends a FAILURES.jsonl entry (candidate id, tier, counterexample /
nogood, one-stage attribution) that the next round's gate reads
automatically.

Discipline
----------
* Append-only JSONL; one JSON object per line; never rewritten.
* Concurrency: each Slurm array task writes its own shard file
  (ZOO_FAILURES_JSONL, set by the worker to results/FAILURES_<task>.jsonl);
  the aggregate merges shards.  Direct per-line appends to a shared NFS
  file are avoided by design.
* Fairness: evaluation is deterministic and cached, and the GS arms never
  SKIP a sampled genome because of the ledger — skipping would bias
  morphologies-per-CPU-hour against the fixed-budget baselines.  The
  ledger's role is (a) one-stage attribution for the bottleneck table and
  (b) priors for the NEXT round's gate/sampler (read_failures_summary).
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FAILURES_JSONL = os.path.join(_ROOT, "results", "FAILURES.jsonl")

# frozen first-match order for one-stage attribution (mirrors the gate
# evaluation order in evaluation/invariants.py)
_GATE_ORDER = (
    "GATE_CORRECTNESS",
    "GATE_INVARIANTS",
    "GATE_PROTECTED_ISOLATION",
    "GATE_REVOCATION_FIDELITY",
    "GATE_CAPABILITY_FLOOR",
)

_LOCK = threading.Lock()


def failures_path() -> str:
    return os.environ.get("ZOO_FAILURES_JSONL", DEFAULT_FAILURES_JSONL)


def _utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def stage_attribution(result: Dict[str, Any]) -> Dict[str, str]:
    """ONE-stage attribution of a failed evaluation: the first hard gate
    (frozen order) that is False, plus the sharpest counterexample the
    evaluation dict offers for that stage."""
    gates = result.get("gates") or {}
    stage = "gate:UNKNOWN"
    for g in _GATE_ORDER:
        if gates.get(g) is False:
            stage = "gate:%s" % g
            break
    ev = result.get("evaluation") or {}
    cex: List[str] = []
    if gates.get("GATE_CORRECTNESS") is False:
        if ev.get("harmful_transfers"):
            cex.append("harmful_transfers=%s" % ev["harmful_transfers"])
        if ev.get("stale_answers"):
            cex.append("stale_answers=%s" % ev["stale_answers"])
    if gates.get("GATE_CAPABILITY_FLOOR") is False:
        cex.append("solved_fraction=%s<%s" % (
            ev.get("solved_fraction", "NA"), ev.get("capability_floor", 0.5)))
    if gates.get("GATE_REVOCATION_FIDELITY") is False:
        cex.append("R=none_while_revocation_worlds_scored")
    if gates.get("GATE_PROTECTED_ISOLATION") is False:
        cex.append("external_io=%s" % ev.get("external_io", "NA"))
    return {"stage": stage, "counterexample": ";".join(cex) or "no_detail"}


def append_failure(entry: Dict[str, Any]) -> str:
    """Append one failure-memory entry.  Returns the path written.  Never
    raises into the caller's evaluation path: ledger failure is logged to
    stderr and swallowed (a broken ledger must not destroy retained
    evaluation data)."""
    path = failures_path()
    rec = dict(entry)
    rec["record_utc"] = _utc()
    rec.setdefault("schema", "GS_FAILURE_V1")
    line = json.dumps(rec, sort_keys=True)
    try:
        with _LOCK:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a") as fh:
                fh.write(line + "\n")
    except OSError as e:  # pragma: no cover - ledger is best-effort
        import sys
        print("[failure_memory] ledger append failed: %r" % e, file=sys.stderr)
    return path


def read_failures(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Read every well-formed entry from a ledger file (or the default)."""
    p = path or failures_path()
    out: List[Dict[str, Any]] = []
    if not os.path.exists(p):
        return out
    with open(p) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                continue  # torn line from a killed task; retained, skipped
    return out


def read_failures_all(shard_glob: str = "FAILURES*.jsonl") -> List[Dict[str, Any]]:
    """Merge every ledger shard under results/ (used by aggregation)."""
    import glob
    base = os.path.dirname(failures_path()) or os.path.join(_ROOT, "results")
    out: List[Dict[str, Any]] = []
    for p in sorted(glob.glob(os.path.join(base, shard_glob))):
        out.extend(read_failures(p))
    return out


def read_failures_summary(path: Optional[str] = None) -> Dict[str, Any]:
    """The summary the NEXT round's gate/sampler reads automatically:
    per-stage counts, per grammar-signature nogood counts, and the top
    blocked signatures (a sampler prior — never a skip rule)."""
    recs = read_failures(path) if path else read_failures_all()
    by_stage: Dict[str, int] = {}
    by_sig: Dict[str, int] = {}
    for r in recs:
        st = r.get("stage", "?")
        by_stage[st] = by_stage.get(st, 0) + 1
        sig = r.get("grammar_signature")
        if sig:
            by_sig[sig] = by_sig.get(sig, 0) + 1
    top = sorted(by_sig.items(), key=lambda kv: -kv[1])[:64]
    return {
        "schema": "GS_FAILURE_SUMMARY_V1",
        "n_failures": len(recs),
        "by_stage": dict(sorted(by_stage.items())),
        "top_blocked_signatures": [{"grammar_signature": s, "count": n}
                                   for s, n in top],
        "read_utc": _utc(),
    }
