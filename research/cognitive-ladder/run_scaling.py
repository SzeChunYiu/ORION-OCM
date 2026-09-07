"""Run the active-subspace scaling pilot and emit its receipt.

    python run_scaling.py --out results/SCALING_PILOT_V1.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from scaling import SCALING_PLAN
from scaling_arms import SWEEP_NOTES, fits_for, sweep, sweep_table


def terminal_for(rows) -> tuple[str, str]:
    """Fixed before the run: the terminal is a function of the table."""
    ocm = {r["N"]: r for r in rows if r["arm"] == "ocm_arm"}
    idx = {r["N"]: r for r in rows if r["arm"] == "index_parent"}
    same_k = all(ocm[n]["k"] == idx[n]["k"] for n in ocm)
    same_work = all(ocm[n]["query_work"] == idx[n]["query_work"] for n in ocm)
    sparse = all(ocm[n]["k_over_N"] < 0.1 for n in ocm)
    if same_k and same_work:
        return ("PARENT_SUFFICIENT", (
            "an ordinary index matches the OCM arm exactly on k and on query work at every "
            "registered scale; sparse lookup under a supplied family key is a property of the "
            "key, not a finding about cognition"))
    if not sparse:
        return ("LINEAR_GLOBAL_WORK_DOMINATES", "k did not stay small relative to N")
    return ("ACTIVE_SUBSPACE_SCALING_SUPPORTED_AT_SCOPE",
            "the OCM arm separated from the indexed parent")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    if out.exists():
        print(f"refusing to overwrite existing receipt {out}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)

    results = sweep()
    rows = sweep_table(results)
    terminal, reason = terminal_for(rows)
    ocm = [r for r in rows if r["arm"] == "ocm_arm"]
    crossover = {}
    for r in ocm:
        scan = next(s for s in rows if s["arm"] == "global_scan_ablation" and s["N"] == r["N"])
        per_query_saving = scan["query_work"] - r["query_work"]
        crossover[r["scale"]] = (
            None if per_query_saving <= 0
            else int(-(-r["index_build_work"] // per_query_saving)))

    receipt = {
        "receipt": "CL_SCALING_PILOT_V1",
        "study_id": "CL-SCALING-PILOT-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E1",
        "contribution_level": "L0",
        "study_role": "ENGINEERING_CALIBRATION_OF_THE_METERS",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "plan": SCALING_PLAN,
        "table": rows,
        "loglog_fits": fits_for(rows),
        "crossover_queries_vs_global_scan": crossover,
        "revision": {
            arm: [{
                "scale": r.scale_id,
                "N": r.queries[0].n_objects,
                "local_cone_exact": r.local_revision.observed_changed_ids
                == r.local_revision.expected_changed_ids,
                "local_cone_size": len(r.local_revision.observed_changed_ids),
                "local_true_cone_size": len(r.local_revision.expected_changed_ids),
                "global_cone_exact": r.global_revision.observed_changed_ids
                == r.global_revision.expected_changed_ids,
                "global_cone_size": len(r.global_revision.observed_changed_ids),
                "global_true_cone_size": len(r.global_revision.expected_changed_ids),
            } for r in per_scale if r.local_revision and r.global_revision]
            for arm, per_scale in results.items()
        },
        "terminal": terminal,
        "terminal_reason": reason,
        "sweep_notes": list(SWEEP_NOTES),
        "what_this_does_not_establish": [
            "The revocation gap is about DEFAULT BEHAVIOUR, not achievability. A stronger parent "
            "could rediscover both cones by scanning every object's declared supports at O(N); the "
            "unaudited hostile does exactly that and gets them exactly right. An audited version of "
            "that parent is not run here, so the separation reported is that the plain index holds "
            "no dependency edges and therefore does nothing, not that it could not.",
            "The machine arm's persistent bytes EXCEED every parent's, because its reverse-index "
            "edges are charged as index bytes. Exact revocation is bought with storage and the "
            "receipt charges it rather than omitting it.",
            "The dependency graph was built from the same declarations that populated the store, so "
            "revocation is exact by construction. These numbers measure the cost of exact "
            "revocation, not dependency discovery, and protocol attack A9 is not answered.",
            "Nothing about cognition. The index key is the family identity the catalogue supplies, "
            "so cheap lookup is a property of the supplied key.",
            "No claim of sparse execution on the real OCM runtime; this lane's store is a stand-in "
            "for it and the runtime's own navigation still computes dense fixed points.",
            "No lifetime economics: acquisition compute, energy and maintenance over a real "
            "lifetime are not measured here.",
        ],
        "hostiles_that_fired": [
            "unaudited_scan_hostile returns CANNOT_CHECK rather than a favourable k",
            "rebuild_index_hostile has the same per-query k as the OCM arm and far worse total "
            "work, which is why the crossover query count is reported",
            "the globally shared revocation produces a cone that grows with N, so revision "
            "locality here is not imposed by the benchmark",
            "cache_parent answers none of the probe positions because they lie beyond its cached "
            "magnitude, while carrying the largest persistent state of any arm",
        ],
        "authority": (
            "This receipt calibrates the active-subspace meters. It establishes that k is "
            "instrumented rather than inferred, that index construction is charged on the same "
            "axis as query work, and that the uninstrumented path reports CANNOT_CHECK. It "
            "establishes no scaling law and no advantage over any parent."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(json.dumps({"terminal": terminal, "crossover": crossover, "out": str(out)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
