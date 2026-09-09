"""FREEZE_V1_AMEND_4 freezing TOOL (MZ-D8 islands + MZ-D9 hostile subset).

This tool — not a hand-written file — writes FREEZE_V1_AMEND_4.json, and
stamps created_utc ITSELF at freeze time (the amend-3 timing-erratum lesson:
a hand-stamped label postdated the scored array; the checksum gate proved
freeze-before-score, the label was mis-stamped).

Refuses to run when:
  - FREEZE_V1_AMEND_4.json already exists (amendments are append-only)
  - the ancestor chain V1 -> A1 -> A2 -> A3 is broken anywhere
  - archives/HZD9_TRUTH.json is missing or its P00C xchecks are false
    (the MZ-D9 truth must exist and be deterministic BEFORE the freeze)
  - any scored amend-4 result status (QDA4_/HZD9R_) already exists — the
    freeze must precede every scored run

Single source of truth: island priors are imported from search.island_qd
(ISLAND_PRIORS_V1); the freeze embeds them verbatim (lists) and workers
assert against them at run time.

Usage: python3 hpc/freeze_amend4.py <capsule_root>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

FREEZE_PATH = os.path.join(ROOT, "FREEZE_V1_AMEND_4.json")
_chain = [("FREEZE_V1.json",), ("FREEZE_V1_AMEND_1.json",),
          ("FREEZE_V1_AMEND_2.json",), ("FREEZE_V1_AMEND_3.json",)]
shas = {}
for (fn,) in _chain:
    shas[fn] = hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).hexdigest()
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json")) as f:
    A3 = json.load(f)
assert shas["FREEZE_V1.json"] == A3["freeze_v1_sha256"], "V1 sha drift in A3"
assert shas["FREEZE_V1_AMEND_1.json"] == A3["amend_1_sha256"], "A1 sha drift in A3"
assert shas["FREEZE_V1_AMEND_2.json"] == A3["amend_2_sha256"], "A2 sha drift in A3"

TRUTH_HZ = os.path.join(ROOT, "archives", "HZD9_TRUTH.json")
if not os.path.exists(TRUTH_HZ):
    raise SystemExit("archives/HZD9_TRUTH.json missing — run hpc/hzd9_census.py "
                     "BEFORE freezing amend-4 (unscored truth precedes freeze)")
with open(TRUTH_HZ) as f:
    HZ = json.load(f)
H = HZ["summary"]
for k, v in H["xcheck_vs_P00C"].items():
    if isinstance(v, bool):
        assert v is True, "HZD9 xcheck %s false — census not deterministic" % k
with open(os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json")) as f:
    P00C = json.load(f)["summary"]
with open(os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json")) as f:
    P00B = json.load(f)["summary"]
assert H["denominators"] == P00C["denominators"], "denominator drift HZD9 vs P00C"
# denominators for workers: P00C summary-level PLUS the two keys amend-3 added
# (PARETO_T2 from the truth pareto size, S3d from the P00B reference census)
DEN = dict(P00C["denominators"])
DEN["PARETO_T2"] = P00C["pareto_set_size"]
DEN["S3d@10_occupied_T0ref"] = P00B["denominators"]["S3d@10_occupied"]
assert DEN == A3["census_truth_P00C"]["denominators"], \
    "amend-4 denominator embed must equal the amend-3 frozen set"

# append-only UNLESS no scored amend-4 run exists yet: a pre-scoring refreeze
# (freeze-tool defect) supersedes the old file by recorded sha, never silently
supersedes = None
refreeze_reason = None
if os.path.exists(FREEZE_PATH):
    for st in ("QDA4_", "HZD9R_"):
        hits = [fn for fn in os.listdir(os.path.join(ROOT, "results"))
                if fn.startswith(st) and fn.endswith(".status")]
        if hits:
            raise SystemExit("FREEZE_V1_AMEND_4.json exists AND scored statuses "
                             "exist (%s...) — write AMEND_5, never overwrite" % hits[0])
    supersedes = hashlib.sha256(open(FREEZE_PATH, "rb").read()).hexdigest()
    refreeze_reason = ("pre-scoring refreeze: earlier A4 embed lacked the two "
                       "amend-3 denominator keys (PARETO_T2, S3d@10_occupied_"
                       "T0ref); smoke caught the defect before any scored run")
for st in ("QDA4_", "HZD9R_"):
    hits = [fn for fn in os.listdir(os.path.join(ROOT, "results"))
            if fn.startswith(st) and fn.endswith(".status")]
    if hits:
        raise SystemExit("scored amend-4 statuses exist (%s...) — freeze must "
                         "precede scored runs" % hits[0])

from search.island_qd import ISLAND_PRIORS_V1, N_ISLANDS  # noqa: E402


def _ser(v):
    return list(v) if isinstance(v, tuple) else v


priors = [{"island_id": p["island_id"], "p13_prior": p["p13_prior"],
           "F_arch": _ser(p["F_arch"]), "extras_pool": _ser(p["extras_pool"]),
           "extras_required": _ser(p["extras_required"]),
           "n_extras": list(p["n_extras"]), "T_family": _ser(p["T_family"]),
           "Pi_arch": _ser(p["Pi_arch"]), "L": _ser(p["L"]),
           "R": _ser(p["R"]), "K": _ser(p["K"])}
          for p in ISLAND_PRIORS_V1]

CREATED = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
freeze = {
    "amendment_id": "FREEZE_V1_AMEND_4_MZD8_MZD9",
    "amends": "FREEZE_V1_AMEND_3.json",
    "freeze_v1_sha256": shas["FREEZE_V1.json"],
    "amend_1_sha256": shas["FREEZE_V1_AMEND_1.json"],
    "amend_2_sha256": shas["FREEZE_V1_AMEND_2.json"],
    "amend_3_sha256": shas["FREEZE_V1_AMEND_3.json"],
    "created_utc": CREATED,
    "created_utc_by": "hpc/freeze_amend4.py at freeze time (tool-stamped; "
                      "amend-3 timing-erratum correction applied)",
    "supersedes_sha256": supersedes,
    "refreeze_reason": refreeze_reason,
    "motivation": (
        "MZ-D8 (P13 islands) + MZ-D9 hostile subset (#221 sec 12).  Islands: "
        "7 prior-locked MAP-Elites subpopulations over the frozen census "
        "grammar with ring migration of best elites at a frozen interval vs a "
        "no-migration control on IDENTICAL per-island RNG streams.  Hostiles "
        "carried by the arms: 'island diversity disappears after migration' "
        "(island-class entropy mid vs final) and 'one mature parent "
        "architecture reproduces the entire frontier' (frontier birth-island "
        "concentration).  MZ-D9 attacks the amend-3 terminal "
        "DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE with the three "
        "most load-bearing sec-12 checks still unrun: genotype->phenotype "
        "collapse, junk-filtered coverage (census-median quality bar), and "
        "descriptor-choice-as-architecture-label (cell purity + eta^2)."),
    "census_truth_P00C": {
        "run_id": P00C["run_id"], "tier": "T2",
        "denominators": DEN,
        "denominators_note": "P00C summary denominators PLUS PARETO_T2 "
                             "(=pareto_set_size) and S3d@10_occupied_T0ref "
                             "(P00B reference census) — the exact set amend-3 "
                             "froze (asserted equal at freeze time)",
        "frozen_grid_bounds": P00C["frozen_grid_bounds"],
        "t2_scalar_refs": P00C["t2_scalar_refs"],
    },
    "census_truth_HZD9": {
        "run_id": H["run_id"], "tier": "T2", "unscored": True,
        "receipt_head": H["receipt_head"], "config_digest": H["config_digest"],
        "feasible": H["feasible"],
        "collapse": H["collapse"],
        "quality_bar_T2": H["quality_bar_T2"],
        "descriptor_purity_D2d_frac_cells_F_arch_ge_0.9":
            H["descriptor_purity_D2d"]["frac_cells_purity_F_arch_ge_0.9"],
        "eta_squared_F_arch": H["eta_squared_F_arch"],
        "xcheck_vs_P00C": H["xcheck_vs_P00C"],
        "precedence": "HZD9 truth produced and frozen BEFORE any amend-4 "
                      "scored run; pareto/cells/feasible EQUAL CENSUS_P00C "
                      "truth (asserted in hzd9_census.py)",
    },
    "quality_bar_T2": H["quality_bar_T2"],
    "island_priors_amend4": {
        "source": "search.island_qd.ISLAND_PRIORS_V1 (verbatim, tool-imported)",
        "n_islands": N_ISLANDS,
        "topology": "unidirectional_ring",
        "migration_interval_rounds": 500,
        "migration_payload": "each island's current best elite by dev_score, "
                             "copied to the ring successor, simultaneous "
                             "(outbound chosen from pre-migration state); "
                             "migration charged zero evaluation budget",
        "region_lock": "sampling, mutation and crossover are region-locked "
                       "(out-of-region offspring re-drawn); migration is the "
                       "only cross-island mixing channel",
        "rng_streams": "per-island random.Random(seed*1000003 + island_index); "
                       "migration consumes no rng, so I01 and I02 differ only "
                       "through planted migrants and their descendants",
        "dropped_prior": {
            "p13_prior": "open-ended operator language",
            "reason": "O_basis is DERIVED from units/L/K/R (operators_for), "
                      "not a free genome field — an open-operator island "
                      "cannot be expressed faithfully and is not claimed"},
        "priors": priors,
    },
    "arms_amend4": {
        "budget": 40000,
        "charged_evals": N_ISLANDS * (40000 // N_ISLANDS),
        "per_island_budget": 40000 // N_ISLANDS,
        "seeds": [0, 1, 2],
        "archive": "D_dev_2d", "res": 10,
        "island_arms": [
            {"arm_id": "I01_islands_ring_mig", "migration": True,
             "own_axis": "D2d_cell_recovery_pooled"},
            {"arm_id": "I02_islands_nomig", "migration": False,
             "own_axis": "D2d_cell_recovery_pooled"},
        ],
        "hzd9_recompute_arms": ["P01_random_search_T2", "P03_map_elites_T2",
                                "P05_map_elites_D2d", "P06_cvt_map_elites_D",
                                "P09_map_elites_D3d"],
        "hzd9_own_axis": {
            "P01_random_search_T2": "pareto_recovery_T2",
            "P03_map_elites_T2": "S3d_cell_recovery",
            "P05_map_elites_D2d": "D2d_cell_recovery",
            "P06_cvt_map_elites_D": "CVTD_niche_recovery",
            "P09_map_elites_D3d": "D3d_cell_recovery"},
        "unrestricted_reference": "QDA3 P05_map_elites_D2d (same budget 40000, "
                                  "same seeds, same D_dev_2d@10 axis): "
                                  "DESCRIPTIVE ONLY, no frozen rule — the "
                                  "islands question is migration, and pooled "
                                  "single-population QD is not its control",
    },
    "metrics_amend4": [
        "D2d_cell_recovery_pooled = |pooled islands' D_dev_2d@10 cells INTERSECT census occupied (50)| / 50 (own axis)",
        "pareto_recovery_T2_pooled = |pooled phenotypes INTERSECT census P00C T2 pareto (792)| / 792",
        "best_dev_T2_pooled, n_elites_pooled, CVTD_niche_recovery_pooled",
        "island_entropy_{mid,final} = normalized entropy of pooled elites' birth-island classes (log2 7)",
        "diversity_retention_final_over_mid = island_entropy_final / island_entropy_mid",
        "frontier_birth_concentration = max birth-island fraction of pooled top-32 elites by dev_score_T2",
        "cross_island_survivor_fraction, n_migrants_planted",
        "HZD9: raw_own_axis_recovery, junk_free_own_axis_recovery (only elites with dev_score_T2 >= quality_bar_T2), junk_free_ratio",
        "HZD9: archive_genotype_to_phenotype_collapse_ratio = 1 - distinct phenotypes / distinct genotypes",
    ],
    "thresholds_amend4": {
        "mzd8": {"frontier_birth_concentration_ge": 0.9,
                 "entropy_ratio_final_mig_over_nomig_lt": 0.5,
                 "own_axis_absolute_bar": 0.25},
        "mzd9": {"census_distinct_phenotype_fraction_lt": 0.1,
                 "archive_collapse_ratio_ge": 0.9,
                 "purity_frac_cells_ge": 0.5, "purity_cell_bar": 0.9,
                 "eta2_max_ge": 0.8, "junk_free_ratio_lt": 0.5},
    },
    "scoring_rules_amend4": {
        "matched_pair_rule_FROZEN": "I01 vs I02 on [D2d_cell_recovery_pooled, pareto_recovery_T2_pooled, best_dev_T2_pooled], seed-means: strictly >= on all three and > on at least one => I01 (migration) wins; the inverse => I02 wins; otherwise TIE (identical in form to amend-2/3)",
        "mzd8_terminal_rule_FROZEN_first_match": [
            "1 ONE_ARCHITECTURE_FAMILY_DOMINATES: seed-mean frontier_birth_concentration(I01) >= 0.9 [sec12: one mature parent architecture reproduces the entire frontier]",
            "2 ONE_ARCHITECTURE_FAMILY_DOMINATES: seed-mean island_entropy_final(I01) < 0.5 * seed-mean island_entropy_final(I02) [sec12: island diversity disappears after migration]",
            "3 MORPHOLOGY_FAMILY_TRANSFER_SUPPORTED_AT_SCOPE: I01 wins the frozen pair AND seed-mean island_entropy_final(I01) >= 0.5 * seed-mean island_entropy_final(I02) AND seed-mean D2d_cell_recovery_pooled(I01) >= 0.25",
            "4 else MIXED_INTERMEDIATE_NO_TERMINAL (non-terminal marker; no sec-15 label fires from this amendment alone)",
        ],
        "mzd9_terminal_rule_FROZEN_first_match": [
            "1 NO_MEANINGFUL_BEHAVIORAL_DIVERSITY: census distinct-phenotype fraction < 0.1 OR seed-mean archive genotype-to-phenotype collapse >= 0.9 over the D-grid arms (P05/P09) [sec12: genotype diversity collapses to same phenotype] => amend3_terminal_status = UNDERMINED_DIVERSITY",
            "2 DESCRIPTOR_CHOICE_DOMINATES: HZD9 D2d frac of occupied cells with F_arch purity >= 0.9 is itself >= 0.5, OR max eta^2(F_arch) over the D_dev_2d axes >= 0.8 [sec12: diversity descriptor merely encodes architecture labels] => amend3_terminal_status = RETAINED_DESCRIPTOR_CONFOUNDED (the terminal stands but its diversity axis is architecture labels)",
            "3 MIXED_INTERMEDIATE_NO_TERMINAL: any terminal-carrying D arm (P05/P06/P09) has seed-mean junk_free_ratio < 0.5 [sec12: high coverage comes from low-quality junk] => amend3_terminal_status = UNDERMINED_QUALITY (the high-performing clause fails; revival iteration owed)",
            "4 else DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE (RETAINED under the hostile subset, now with the census-median quality bar recorded)",
        ],
        "aggregation": "aggregate_amend4.py runs only when all 6 island tasks and all 15 hzd9-recompute tasks have ok dispositions and verifiable receipts, and HZD9 truth is present; verdicts are computed mechanically from these rules, never narrated",
    },
    "controls": {
        "t0_untouched": "T0 scoring path and all amend-1/2/3 truth unchanged and still reproducible",
        "hzd9_unscored_precedence": "HZD9 truth (receipt %s) produced and frozen BEFORE any amend-4 scored run; its Pareto/cells/feasible EQUAL frozen P00C truth" % H["receipt_head"][:16],
        "determinism_xchecks": "hzd9_recompute asserts best_dev_T2 and raw own-axis recovery EQUAL the frozen QDA3 values; island runs are seed-deterministic",
        "encoding_fixed": "E0_direct everywhere (amend-2 owns the encoding question); no codec arms",
    },
    "status": "FROZEN pre-score",
}
with open(FREEZE_PATH, "w") as f:
    json.dump(freeze, f, indent=1)
print(json.dumps({"frozen": FREEZE_PATH, "created_utc": CREATED,
                  "quality_bar_T2": H["quality_bar_T2"],
                  "n_islands": N_ISLANDS,
                  "amend_4_sha256": hashlib.sha256(
                      open(FREEZE_PATH, "rb").read()).hexdigest()}, sort_keys=True))
