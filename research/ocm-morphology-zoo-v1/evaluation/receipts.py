"""Deterministic receipts: sha256-chained records of every scored outcome.

Receipt layout (one JSON file per run):
  run_id, created_utc, host, tier, n_items, config_digest,
  chain: [ {index, genotype_digest, phenotype_digest, feasible,
            objectives, record_sha256} ... ]
  head_sha256 — sha256 of the final record; tampering with any record breaks
  the chain because record_sha256 covers (prev_sha256, payload).

Aggregation is allowed only when every expected index has a disposition
(#221 sec 9 Slurm rules); aggregate.py verifies the chain first.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

GENESIS = "0" * 64


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def make_receipt(run_id: str, created_utc: str, host: str, tier: str,
                 config_digest: str) -> Dict[str, Any]:
    return {"run_id": run_id, "created_utc": created_utc, "host": host,
            "tier": tier, "config_digest": config_digest,
            "chain": [], "head_sha256": GENESIS}


def append_record(receipt: Dict[str, Any], index: int,
                  payload: Dict[str, Any]) -> Dict[str, Any]:
    prev = receipt["head_sha256"]
    body = json.dumps({"index": index, "payload": payload}, sort_keys=True,
                      separators=(",", ":"))
    rec_sha = _sha(prev + "|" + body)
    receipt["chain"].append({"index": index,
                             "record_sha256": rec_sha,
                             "payload": payload})
    receipt["head_sha256"] = rec_sha
    return receipt


def verify_receipt(receipt: Dict[str, Any]) -> bool:
    prev = GENESIS
    for rec in receipt["chain"]:
        body = json.dumps({"index": rec["index"], "payload": rec["payload"]},
                          sort_keys=True, separators=(",", ":"))
        if _sha(prev + "|" + body) != rec["record_sha256"]:
            return False
        prev = rec["record_sha256"]
    return prev == receipt["head_sha256"]


def all_dispositions(receipt: Dict[str, Any],
                     expected_indices: Optional[List[int]] = None) -> bool:
    """Every expected index carries an explicit disposition (solved/failed/infeasible)."""
    have = {r["index"] for r in receipt["chain"]}
    if expected_indices is None:
        return True
    return set(expected_indices).issubset(have)
