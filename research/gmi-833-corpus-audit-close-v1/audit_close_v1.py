#!/usr/bin/env python3
"""GMI #833 Section-B corpus audit adjudication close v1.

Converts the mechanical census (research/gmi-833-corpus-census-v1) dispositions
into adjudicated Section-B rows for a frozen subset: the GREEN mainline
(EXPLICIT claim-class objects) plus a seeded stratified 200-object sample of
the AMBER/RED space. The VERDICTS table below is the human adjudication layer;
this module validates it against the census and reproduces
ADJUDICATIONS_V1.json byte-identically. It never overwrites a census
disposition and never promotes any object.

Claim ceiling: GMI_SECTION_B_ADJUDICATION_AT_FROZEN_CENSUS_SUBSET_SCOPE
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import subprocess

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CENSUS_DIR = REPO_ROOT / "research" / "gmi-833-corpus-census-v1"

CLAIM_CEILING = "GMI_SECTION_B_ADJUDICATION_AT_FROZEN_CENSUS_SUBSET_SCOPE"
SCHEMA = "GMI_833_CORPUS_AUDIT_CLOSE_V1"
SAMPLE_SEED = 833200
SAMPLE_SIZE = 200
CLAIM_CLASSES = frozenset({
    "THEOREM", "LAW", "CLAIM", "COROLLARY", "PROPOSITION", "LEMMA", "AXIOM",
})
VERDICTS = frozenset({
    "CONFIRMED", "OVERSTRONG", "DUPLICATE", "COMPUTATION_ONLY",
    "ENUMERATION_SUBSTITUTED", "POST_HOC_ASSUMPTION", "UNKNOWN",
})
FORBIDDEN_PROMOTIONS = [
    "GMI_CORPUS_AUDIT_CLOSE_COMPLETE",
    "GMI_THEORY_BASELINE_V1_FROZEN",
    "WHOLE_CORPUS_ADJUDICATED",
    "ANY_OBJECT_AUTO_PROMOTED",
    "OVERCLAIMS_RETRACTED_IN_THIS_PACKAGE",
    "ALL_GMI_THEOREMS_TRUE",
    "ONTOLOGICAL_COMPLETENESS",
    "COMPLETE_GMI",
]

NO_SMUGGLING_DIR = REPO_ROOT / "research" / "gmi-833-no-smuggling-audit-v1"


class AuditCloseError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Census loading and frozen-scope reconstruction
# ---------------------------------------------------------------------------

def load_census():
    index = json.loads((CENSUS_DIR / "CORPUS_INDEX_V1.json").read_text(encoding="utf-8"))
    audit = json.loads((CENSUS_DIR / "AUDIT_V1.json").read_text(encoding="utf-8"))
    gaps = json.loads((CENSUS_DIR / "GMI_GAP_GRAPH_V1.json").read_text(encoding="utf-8"))
    return index, audit, gaps["gaps"]


def frozen_scope(objects):
    """Return (mainline_ids, sample_ids) exactly as frozen in FREEZE_V1.md."""
    mainline = [o for o in objects
                if o["audit_disposition"] == "GREEN" and o["id_kind"] == "EXPLICIT"
                and o["object_class"] in CLAIM_CLASSES]
    mainline_ids = {o["object_id"] for o in mainline}
    ar = [o for o in objects if o["audit_disposition"] in ("AMBER", "RED")]
    strata = {}
    for o in ar:
        strata.setdefault((o["audit_disposition"], o["object_class"]), []).append(o)
    quota = {k: max(1, round(len(g) * SAMPLE_SIZE / len(ar))) for k, g in strata.items()}
    over = sum(quota.values()) - SAMPLE_SIZE
    if over > 0:
        for k in sorted(quota, key=lambda k: (-quota[k], k)):
            if over <= 0:
                break
            take = min(over, quota[k] - 1)
            quota[k] -= take
            over -= take
    if sum(quota.values()) != SAMPLE_SIZE:
        raise AuditCloseError("sample quota allocation does not sum to 200")
    rng = random.Random(SAMPLE_SEED)
    sample_ids = []
    for k in sorted(strata):
        members = sorted(strata[k], key=lambda x: (x["source_path"], x["source_locator"], x["object_id"]))
        picks = rng.sample(members, quota[k])
        sample_ids.extend(o["object_id"] for o in picks)
    if len(set(sample_ids)) != len(sample_ids):
        raise AuditCloseError("sample contains duplicate object ids")
    if mainline_ids & set(sample_ids):
        raise AuditCloseError("sample overlaps the GREEN mainline")
    return sorted(mainline_ids), sorted(sample_ids)
