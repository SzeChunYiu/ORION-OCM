#!/usr/bin/env python3
"""Route B - independent oracle for AA21.

Written against the FROZEN CENSUS SOURCE, not against route A.  It imports
nothing from `finite_universal_harness_v1.py`.  Where route A reads the
registered gap population out of `GMI_GAP_GRAPH_V1.json`, route B never opens
that file: it re-derives the `GAP-FIN2UNIV-*` population from
`CORPUS_INDEX_V1.json` by reconstructing the parent census' emission rule, and
it additionally re-reads that rule out of `corpus_census_v1.py` so the rule
itself is cross-checked rather than copied on trust.

stdlib only; exact integer arithmetic; python3.8-compatible.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = ROOT / "research" / "gmi-833-corpus-census-v1"


class OracleError(RuntimeError):
    pass


def rule_from_census_source() -> Tuple[str, int]:
    """Recover the gap-id construction from the parent census source text.

    Returns (prefix, hex truncation length).  If the source no longer says what
    this oracle assumes, the oracle fails loudly instead of agreeing by
    coincidence with route A.
    """
    text = (SRC / "corpus_census_v1.py").read_text(encoding="utf-8")
    hit = re.search(
        r'gap_id=f"(GAP-FIN2UNIV-)\{hashlib\.sha256\(oid\.encode\(\)\)\.hexdigest\(\)\[:(\d+)\]',
        text,
    )
    if hit is None:
        raise OracleError("census source no longer states the FIN2UNIV gap-id rule")
    return hit.group(1), int(hit.group(2))


def predicate_from_census_source() -> Tuple[str, Tuple[str, ...]]:
    """Recover the FIN2UNIV firing condition from the parent census source."""
    text = (SRC / "corpus_census_v1.py").read_text(encoding="utf-8")
    hit = re.search(
        r'if obj\["quantifier_class"\] == "([A-Z_]+)" and obj\["proof_evidence_mode"\] in \{([^}]*)\}',
        text,
    )
    if hit is None:
        raise OracleError("census source no longer states the FIN2UNIV condition")
    modes = tuple(sorted(re.findall(r'"([A-Z_]+)"', hit.group(2))))
    return hit.group(1), modes


def derive() -> Dict[str, object]:
    prefix, cut = rule_from_census_source()
    quant, modes = predicate_from_census_source()

    with (SRC / "CORPUS_INDEX_V1.json").open("r", encoding="utf-8") as handle:
        index = json.load(handle)

    seen = Counter()          # object_id -> how many object rows fire
    order = []                # first-appearance order of firing object ids
    total_objects = 0
    by_mode = Counter()
    by_path = Counter()
    for obj in index["scientific_objects"]:
        total_objects += 1
        if obj["quantifier_class"] != quant:
            continue
        if obj["proof_evidence_mode"] not in modes:
            continue
        oid = obj["object_id"]
        if oid not in seen:
            order.append(oid)
        seen[oid] += 1
        by_mode[obj["proof_evidence_mode"]] += 1
        by_path[obj["source_path"]] += 1

    records = sum(seen.values())
    ids = []
    for oid in order:
        digest = hashlib.sha256(oid.encode("utf-8")).hexdigest()
        ids.append(prefix + digest[:cut])

    return {
        "schema": "GMI_833_AA21_FINITE_UNIVERSAL_ORACLE_V1",
        "route": "B",
        "recovered_predicate": {"quantifier_class": quant, "proof_evidence_modes": list(modes)},
        "recovered_gap_id_rule": {"prefix": prefix, "hex_truncation": cut},
        "objects_scanned": total_objects,
        "firing_object_rows": records,
        "distinct_firing_object_ids": len(seen),
        "distinct_gap_ids": len(set(ids)),
        "duplicate_object_rows": records - len(seen),
        "by_evidence_mode": dict(sorted(by_mode.items())),
        "distinct_source_files": len(by_path),
        "top_source_files": [list(x) for x in by_path.most_common(5)],
        "gap_ids": sorted(set(ids)),
        "claim_ids": sorted(seen),
    }


if __name__ == "__main__":
    out = derive()
    printable = {k: v for k, v in out.items() if k not in ("gap_ids", "claim_ids")}
    print(json.dumps(printable, indent=2, sort_keys=True))
