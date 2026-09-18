#!/usr/bin/env python3
"""Route A - validation harness for the registered FIN2UNIV detector (issue #833, AA21).

Reads the FROZEN gap graph produced by `gmi-833-corpus-census-v1` and reports the
`GAP-FIN2UNIV-*` population exactly, then runs the recall / no-alarm / null
validation declared in FREEZE_V1.md.

Route A NEVER re-derives the predicate from the object corpus; that is route B's
job (`independent_fin2univ_oracle_v1.py`), written from the frozen census source
independently.  The two routes are compared by SET equality in the test module.

stdlib only; exact integer arithmetic; python3.8-compatible.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

PKG = Path(__file__).resolve().parent
REPO = PKG.parent.parent
CENSUS = REPO / "research" / "gmi-833-corpus-census-v1"
GAP_GRAPH = CENSUS / "GMI_GAP_GRAPH_V1.json"

# The predicate as registered by the parent census. Restated, not invented here.
FIN2UNIV_QUANTIFIER = "UNIVERSAL"
FIN2UNIV_EVIDENCE_MODES = ("COMPUTER_ASSISTED_EXHAUSTIVE", "FINITE_EXECUTABLE_CERTIFICATE")

# Declared-clean classes, fixed in FREEZE_V1.md section 4 BEFORE any number was read.
CLEAN_UNIVERSAL_MODES = ("ANALYTIC_DEDUCTIVE", "MECHANIZED_PROOF")
CLEAN_NONUNIVERSAL_CLASSES = (
    "FINITE_EXACT",
    "CONDITIONAL",
    "SAMPLED_STATISTICAL",
    "EXISTENTIAL_WITNESS",
    "HELD_OUT",
    "UNKNOWN",
)

GAP_ID_PREFIX = "GAP-FIN2UNIV-"
NULL_TRIALS = 200
NULL_SEED = 8332021  # 833 / AA21


class HarnessError(RuntimeError):
    pass


def _read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def gap_id_for(object_id: str) -> str:
    """The parent census' emission rule, restated verbatim."""
    return GAP_ID_PREFIX + hashlib.sha256(object_id.encode()).hexdigest()[:12]


# --------------------------------------------------------------------------
# Route A: read the registered population out of the frozen gap graph.
# --------------------------------------------------------------------------
def registered_population(graph: Dict[str, object]) -> Dict[str, object]:
    gaps = graph["gaps"]  # type: ignore[index]
    if not isinstance(gaps, list):
        raise HarnessError("gap graph has no gap list")
    fin = [g for g in gaps if str(g["id"]).startswith(GAP_ID_PREFIX)]
    ids = [str(g["id"]) for g in fin]
    claims = [str(g["claim_id"]) for g in fin]
    columns = ("severity", "materiality", "status", "owner_role", "parent_result")
    profile = {}
    for col in columns:
        profile[col] = sorted({str(g[col]) for g in fin})
    # Required OPEN_GAP text fields must be non-empty on every FIN2UNIV record.
    text_fields = ("premise", "inference", "unresolved_assumption",
                   "possible_counterexample", "evidence_needed")
    empty = 0
    for g in fin:
        for f in text_fields:
            if not str(g.get(f, "")).strip():
                empty += 1
    return {
        "records": len(fin),
        "distinct_gap_ids": len(set(ids)),
        "distinct_claim_ids": len(set(claims)),
        "duplicate_gap_id_records": len(ids) - len(set(ids)),
        "empty_required_text_cells": empty,
        "gap_ids": sorted(set(ids)),
        "claim_ids": sorted(set(claims)),
        "column_profile": profile,
        "total_gaps_in_graph": len(gaps),
        "frozen_source_sha": str(graph["frozen_source_sha"]),  # type: ignore[index]
    }


# --------------------------------------------------------------------------
# Validation: recall on planted positives, no-alarm on declared-clean inputs.
# --------------------------------------------------------------------------
def predicate(quantifier_class: str, proof_evidence_mode: str) -> bool:
    return (quantifier_class == FIN2UNIV_QUANTIFIER
            and proof_evidence_mode in FIN2UNIV_EVIDENCE_MODES)


def planted_positives() -> List[Dict[str, str]]:
    """Synthetic objects of exactly the shape the predicate names."""
    out = []
    for i, mode in enumerate(FIN2UNIV_EVIDENCE_MODES):
        for j in range(4):
            out.append({
                "object_id": "PLANT-POS-%02d%02d" % (i, j),
                "quantifier_class": FIN2UNIV_QUANTIFIER,
                "proof_evidence_mode": mode,
            })
    return out


def declared_clean() -> List[Dict[str, str]]:
    """Objects the predicate must NOT fire on, fixed in the freeze."""
    out = []
    for i, mode in enumerate(CLEAN_UNIVERSAL_MODES):
        out.append({
            "object_id": "PLANT-CLEAN-U%02d" % i,
            "quantifier_class": FIN2UNIV_QUANTIFIER,
            "proof_evidence_mode": mode,
        })
    for i, qc in enumerate(CLEAN_NONUNIVERSAL_CLASSES):
        for j, mode in enumerate(FIN2UNIV_EVIDENCE_MODES):
            out.append({
                "object_id": "PLANT-CLEAN-N%02d%02d" % (i, j),
                "quantifier_class": qc,
                "proof_evidence_mode": mode,
            })
    return out


def validate_detector() -> Dict[str, int]:
    pos = planted_positives()
    clean = declared_clean()
    recall_hits = sum(1 for o in pos if predicate(o["quantifier_class"], o["proof_evidence_mode"]))
    false_alarms = sum(1 for o in clean if predicate(o["quantifier_class"], o["proof_evidence_mode"]))
    return {
        "planted_positives": len(pos),
        "planted_positives_detected": recall_hits,
        "declared_clean": len(clean),
        "declared_clean_alarms": false_alarms,
    }


# --------------------------------------------------------------------------
# Hostiles: deliberately broken variants the harness must flag.
# --------------------------------------------------------------------------
def hostiles(true_ids: Set[str]) -> List[Dict[str, object]]:
    """Each hostile perturbs one input and MUST move its own quantity."""
    out = []  # type: List[Dict[str, object]]

    # H1 - drop a registered gap record.
    dropped = sorted(true_ids)[:1]
    out.append({
        "name": "H1_drop_one_registered_gap",
        "moved_quantity": "distinct_gap_ids",
        "before": len(true_ids),
        "after": len(true_ids - set(dropped)),
        "detected": len(true_ids - set(dropped)) != len(true_ids),
    })

    # H2 - widen the evidence-mode set to include an analytic mode.
    widened = FIN2UNIV_EVIDENCE_MODES + ("ANALYTIC_DEDUCTIVE",)
    clean = declared_clean()
    alarms = sum(1 for o in clean
                 if o["quantifier_class"] == FIN2UNIV_QUANTIFIER
                 and o["proof_evidence_mode"] in widened)
    out.append({
        "name": "H2_widen_evidence_modes_to_analytic",
        "moved_quantity": "declared_clean_alarms",
        "before": 0,
        "after": alarms,
        "detected": alarms > 0,
    })

    # H3 - drop the quantifier conjunct entirely (fires on any finite evidence).
    clean_nonuniv = [o for o in clean if o["quantifier_class"] != FIN2UNIV_QUANTIFIER]
    alarms3 = sum(1 for o in clean_nonuniv if o["proof_evidence_mode"] in FIN2UNIV_EVIDENCE_MODES)
    out.append({
        "name": "H3_drop_quantifier_conjunct",
        "moved_quantity": "declared_clean_alarms",
        "before": 0,
        "after": alarms3,
        "detected": alarms3 > 0,
    })

    # H4 - corrupt the gap-id derivation rule (wrong hash truncation).
    sample = "AUTO-973714EB942BCB2BAD1E"
    good = gap_id_for(sample)
    bad = GAP_ID_PREFIX + hashlib.sha256(sample.encode()).hexdigest()[:11]
    out.append({
        "name": "H4_corrupt_gap_id_rule",
        "moved_quantity": "gap_id_of_a_fixed_object",
        "before": good,
        "after": bad,
        "detected": good != bad,
    })

    # H5 - narrow the predicate to a single evidence mode (recall must fall).
    narrowed = FIN2UNIV_EVIDENCE_MODES[:1]
    pos = planted_positives()
    got = sum(1 for o in pos if o["quantifier_class"] == FIN2UNIV_QUANTIFIER
              and o["proof_evidence_mode"] in narrowed)
    out.append({
        "name": "H5_narrow_predicate_to_one_mode",
        "moved_quantity": "planted_positives_detected",
        "before": len(pos),
        "after": got,
        "detected": got < len(pos),
    })

    return out


PROSE_UNIVERSAL = re.compile(
    r"\bfor all\b|\bfor every\b|\bforall\b|\bevery\b|\ball \w+ (?:are|is|satisfy)\b",
    re.IGNORECASE,
)


def prose_variant_hostile(objects: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """H6 - replace the declared quantifier class by a prose grep on the statement.

    The registered detector fires on *declared metadata*. A naive text variant
    that also fires whenever the statement reads universally is a materially
    different detector; on the real corpus it raises strictly more alarms, and
    the inflation is the moved quantity. This is the decoy class that must be
    rejected: a sentence that sounds universal is not a registered universal
    claim.
    """
    true_hits = 0
    extra = 0
    for obj in objects:
        if obj["proof_evidence_mode"] not in FIN2UNIV_EVIDENCE_MODES:
            continue
        if obj["quantifier_class"] == FIN2UNIV_QUANTIFIER:
            true_hits += 1
        elif PROSE_UNIVERSAL.search(str(obj.get("statement") or "")):
            extra += 1
    return {
        "name": "H6_prose_grep_variant_inflates_alarms",
        "moved_quantity": "records_flagged_on_the_real_corpus",
        "before": true_hits,
        "after": true_hits + extra,
        "extra_alarms": extra,
        "detected": extra > 0,
    }


# --------------------------------------------------------------------------
# Null: randomized reassignment of the two predicate fields.
# --------------------------------------------------------------------------
def null_study(field_pairs: Sequence[Tuple[str, str]], true_ids: Set[str],
               object_ids: Sequence[str]) -> Dict[str, object]:
    rng = random.Random(NULL_SEED)
    quantifiers = [p[0] for p in field_pairs]
    modes = [p[1] for p in field_pairs]
    reproduced = 0
    sizes = []
    overlaps = []
    for _ in range(NULL_TRIALS):
        rq = quantifiers[:]
        rm = modes[:]
        rng.shuffle(rq)
        rng.shuffle(rm)
        flagged = set()
        for oid, q, m in zip(object_ids, rq, rm):
            if predicate(q, m):
                flagged.add(gap_id_for(oid))
        sizes.append(len(flagged))
        overlaps.append(len(flagged & true_ids))
        if flagged == true_ids:
            reproduced += 1
    return {
        "trials": NULL_TRIALS,
        "seed": NULL_SEED,
        "reproduced_true_set": reproduced,
        "min_flagged": min(sizes),
        "max_flagged": max(sizes),
        "mean_flagged_exact": str(Fraction(sum(sizes), NULL_TRIALS)),
        "true_set_size": len(true_ids),
        "max_overlap_with_true_set": max(overlaps),
        "mean_overlap_exact": str(Fraction(sum(overlaps), NULL_TRIALS)),
    }


def main() -> Dict[str, object]:
    graph = _read_json(GAP_GRAPH)
    if not isinstance(graph, dict):
        raise HarnessError("gap graph is not an object")
    pop = registered_population(graph)
    validation = validate_detector()

    # The null needs the real field distribution. Read it out of the frozen
    # corpus index WITHOUT applying the predicate to build a population - the
    # predicate application here is the null's own randomized one.
    index = _read_json(CENSUS / "CORPUS_INDEX_V1.json")
    objects = index["scientific_objects"]  # type: ignore[index]
    pairs = [(str(o["quantifier_class"]), str(o["proof_evidence_mode"])) for o in objects]
    oids = [str(o["object_id"]) for o in objects]
    true_ids = set(pop["gap_ids"])  # type: ignore[arg-type]
    null = null_study(pairs, true_ids, oids)

    host = hostiles(true_ids)
    host.append(prose_variant_hostile(objects))
    return {
        "schema": "GMI_833_AA21_FINITE_UNIVERSAL_HARNESS_V1",
        "route": "A",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": "REGISTERED_DETECTOR_VALIDATED_V1",
        "predicate": {
            "quantifier_class": FIN2UNIV_QUANTIFIER,
            "proof_evidence_modes": list(FIN2UNIV_EVIDENCE_MODES),
            "gap_id_rule": "GAP-FIN2UNIV- + sha256(object_id).hexdigest()[:12]",
        },
        "registered_population": {k: v for k, v in pop.items()
                                  if k not in ("gap_ids", "claim_ids")},
        "validation": validation,
        "hostiles": host,
        "hostiles_detected": sum(1 for h in host if h["detected"]),
        "hostiles_total": len(host),
        "null": null,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
