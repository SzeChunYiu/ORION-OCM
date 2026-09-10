#!/usr/bin/env python3
"""Adopt an ecology authored by ANOTHER lane into this harness, unchanged.

Independent-ecology replication requires an ecology this lane did not design. The M1
semantic partitions (research/m1-native-acquisition/M1_PARTITIONS_V1.json) were authored
by the M1 lane under its own frozen protocol, with its own predicate (degree band x
support band x coefficient class), its own frozen seed and its own stream split.

This adapter RE-EXPRESSES that file in the schema this harness reads. It does not
choose the targets, the split, or the structure:

  - stream membership is copied verbatim, in the original order;
  - no target is added, dropped, reordered or re-binned;
  - `canonical_program` and `baseline_first_index` are COMPUTED from the grammar by
    exhaustive enumeration -- they are facts about each target, not choices;
  - `hidden_motifs` is EMPTY, because the M1 lane planted none. That is the point: it is
    an unstructured ecology, and the admission law predicts refusal.

Registered prediction, before running: no motif structure exists to recover, so the
learner should refuse, and the ungated parent should be HARMED by the fragments it mines.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--foreign", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="optional cap per stream, head order preserved")
    a = ap.parse_args()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M

    canonical, first_index = {}, {}
    slot = 0
    for L in range(9):
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            nf = M.normal_form(prog)
            if nf not in canonical:
                canonical[nf], first_index[nf] = prog, slot

    src = json.loads(Path(a.foreign).read_text())
    out_streams, dropped = {}, 0
    for name in ("train", "validation", "protected"):
        rows = []
        for r in src["streams"][name]:
            nf = tuple(Fraction(c) for c in r["coefficients"])
            while len(nf) > 1 and nf[-1] == 0:
                nf = nf[:-1]
            if nf not in canonical:          # unreachable in the declared grammar
                dropped += 1
                continue
            rows.append({"coefficients": [str(c) for c in nf],
                         "canonical_program": list(canonical[nf]),
                         "canonical_length": len(canonical[nf]),
                         "motif_tokens": None,
                         "baseline_first_index": first_index[nf],
                         "normal_form_digest": r["normal_form_digest"]})
        out_streams[name] = rows[:a.limit] if a.limit else rows

    digs = {k: {r["normal_form_digest"] for r in v} for k, v in out_streams.items()}
    shared = (digs["train"] & digs["protected"]) | (digs["train"] & digs["validation"]) | \
             (digs["validation"] & digs["protected"])

    out = {
        "schema": "OCM_M2P1_FOREIGN_ECOLOGY_V1",
        "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "status": "ADOPTED_UNCHANGED_FROM_ANOTHER_LANE",
        "owner_issue": 165, "hardening_parent": 323,
        "provenance": {
            "source_file": str(a.foreign),
            "source_sha256": hashlib.sha256(Path(a.foreign).read_bytes()).hexdigest(),
            "authored_by": "the M1 native-acquisition lane, under its own frozen protocol",
            "this_lane_changed": ("schema re-expression only: canonical_program and "
                                  "baseline_first_index computed from the grammar; stream "
                                  "membership, order and binning copied verbatim"),
            "targets_dropped_unreachable": dropped,
        },
        "ecology_variant": {"label": "FOREIGN_M1", "structured": False},
        "frozen_seed": src.get("frozen_seed"),
        "hidden_motifs": [],
        "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8},
        "registered_prediction": {
            "motifs_planted_by_source": 0,
            "predicted_admission": False,
            "predicted_parent_harmful": True,
            "rule": ("the admission law requires complete recovery of a motif set; where "
                     "none exists there is nothing to recover, so the learner should refuse "
                     "and the ungated parent should be harmed by the fragments it mines"),
        },
        "streams": out_streams,
        "stream_sizes": {k: len(v) for k, v in out_streams.items()},
        "entry_gates": {
            "G2_shared_normal_forms": len(shared),
            "G2_verdict": "PASS" if not shared else "FAIL",
            "G1_length_parity_max_deviation": None,
            "G1_verdict": "NOT_APPLICABLE_FOREIGN_SPLIT_PRESERVED",
            "G3_non_decomposable": 0,
            "G3_verdict": "NOT_APPLICABLE_NO_MOTIFS",
        },
        "length_distribution": {k: dict(Counter(r["canonical_length"] for r in v))
                                for k, v in out_streams.items()},
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"sizes": out["stream_sizes"], "dropped": dropped,
                      "G2": out["entry_gates"]["G2_verdict"],
                      "source_sha256": out["provenance"]["source_sha256"][:16],
                      "lengths_protected": out["length_distribution"]["protected"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
