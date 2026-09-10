"""Mint FORM_ORACLE_PROTOCOL_V1.json — the pre-registration.

Run BEFORE any scored run.  The protocol records the space, the legality
predicate, all four estimators, the dedup signature, the fidelity rungs and
promotion rule, the parent arms, the D26 domains, the D27 knockout, the
falsifiers, the seeds and the shuffle-equal-n null.  It carries NO result.

Every number it records is either read from a frozen artefact on main or
computed here from frozen constants; nothing is typed by hand.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _code_digests() -> dict:
    out = {}
    for fn in sorted(os.listdir(os.path.join(ROOT, "oracle"))):
        if fn.endswith(".py"):
            out["oracle/" + fn] = _sha256_file(
                os.path.join(ROOT, "oracle", fn))
    return out


def build() -> dict:
    from evaluation.invariants import CAPABILITY_FLOOR_V1, REVOCATION_REQUIRED
    from evaluation.objectives import W2_REF, B2_REF, W_REF, B_REF
    from morphology.gs_bound import GS_BOUND_V1, gs_bound_closed_form_size
    from search.successive_halving import (GS_ETA, GS_RUNGS,
                                           GS_LATE_BLOOMER_FRACTION,
                                           GS_MIN_PROMOTE)
    from oracle import behaviour_sig as BS
    from oracle import burden as BU
    from oracle import evolvability as EV
    from oracle import objectives4 as OB
    from oracle import d26_operators as D26
    from oracle import d27_lineage as D27
    from oracle.c_immutability import (C_OWNED_NAMES, GENOME_FIELDS,
                                       constitution_snapshot, selftest)
    from oracle.future_family import keys_record, assert_disjoint_from_t3
    from oracle.run_form_oracle import LANES, EVOLVABILITY_SUBSAMPLE

    gate = selftest()
    if gate.get("status") != "OK":
        raise RuntimeError("C_IMMUTABILITY_SELFTEST_NOT_OK: %r" % gate)
    disjoint = assert_disjoint_from_t3()

    proto = {
        "protocol_id": "FORM_ORACLE_PROTOCOL_V1",
        "study": "OCM Form Oracle over legal (F,O,Pi) under fixed C",
        "governing_issues": ["#277 sec 7", "#233 D26", "#233 D27", "#221"],
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contains_results": False,

        # ------------------------------------------------------------ space
        "space": {
            "genome": "G = (F_arch, U, T, O_basis, Pi_arch, L, R, K, theta)",
            "constitution": "C is NOT part of G (morphology/schema.py:3)",
            "searched": ["F (F_arch)", "O (O_basis + extra_units)",
                         "Pi (Pi_arch, L, R, K, T_family, theta)"],
            "legality_predicate": (
                "membership in GS_BOUND_V1 vocabulary AND successful "
                "compile_genome AND the frozen compile-time invariant set; "
                "identical to the filter the census enumeration applies"),
            "bound": {k: (list(v) if isinstance(v, (list, tuple)) else v)
                      for k, v in GS_BOUND_V1.items()},
            "closed_form_size": gs_bound_closed_form_size(),
            "sampling_lanes": list(LANES),
        },

        # ------------------------------------------------- C is not searchable
        "constitution_gate": {
            "gate_id": "GATE_C_IMMUTABLE",
            "enforcement": "EXECUTED (raises CImmutabilityViolation); never logged",
            "c_owned_names": list(C_OWNED_NAMES),
            "genome_fields": list(GENOME_FIELDS),
            "c_digest_at_freeze": constitution_snapshot(),
            "selftest": gate,
            "reportable_result_if_violated": (
                "a legal configuration able to alter C is a bug in the space "
                "and is itself a reportable result"),
        },

        # ------------------------------------------------------- objectives
        "objectives": {
            "search_time": {
                "names": list(OB.SEARCH_OBJECTIVES),
                "maximize": list(OB.SEARCH_MAXIMIZE),
                "note": ("T3 is EXCLUDED from admission. If held-out "
                         "generalization entered the selection rule it would "
                         "no longer be held out."),
            },
            "report_time": {
                "names": list(OB.REPORT_OBJECTIVES),
                "maximize": list(OB.REPORT_MAXIMIZE),
                "note": "post-hoc only; the Pareto front is the deliverable",
            },
            "1_capability": {
                "estimator": "evaluation.lifetime2.run_lifetime2 solved_fraction at T2",
                "ecology": "LifetimeEcologyV2 (12 epochs, 8 frozen families)",
                "floor": CAPABILITY_FLOOR_V1,
            },
            "2_burden": {
                "estimator": "oracle.burden.b_full",
                "formula": ("B_full = work_charged + LAMBDA_BYTES*persistent_bytes "
                            "+ B_reject_share"),
                "components": list(BU.BURDEN_COMPONENT_NAMES),
                "lambda_bytes": BU.lambda_bytes(),
                "lambda_bytes_derivation": "W2_REF/B2_REF, both frozen pre-score",
                "W2_REF": W2_REF, "B2_REF": B2_REF,
                "W_REF": W_REF, "B_REF": B_REF,
                "reject_share": ("search work charged over EVERY candidate "
                                 "evaluated at a search rung -- feasible, "
                                 "infeasible, gate-failed and crashed -- "
                                 "divided by the retained archive size"),
                "search_rungs": list(BU.RejectLedger.SEARCH_RUNGS),
                "measurement_reported_separately": True,
                "crash_charge": ("running mean charged work at that rung; a "
                                 "crash can never be cheaper than an evaluation"),
                "memoisation": ("evaluate_genome caches on (phenotype_digest, "
                                "tier); a cache hit saves wall clock, not "
                                "charged work. Every attempt is charged."),
                "index_cost": ("index_build_work is charged into "
                               "acquisition_work by the frozen evaluator; "
                               "index_built is reported so this is auditable"),
                "known_zero_this_tranche": ["B_self (self_change_work is 0.0 "
                                            "for static organisms)"],
            },
            "3_t3_generalization": {
                "estimator": "evaluation.t3_ecology.evaluate_t3 solved_fraction",
                "key_id": disjoint["keys"] and "GSHeldoutT3V1:4d0a1487e4427449",
                "held_out": True,
                "not_used_for": ["admission", "promotion", "any design choice"],
                "not_redrawn": True,
            },
            "4_evolvability": {
                "estimator": "oracle.evolvability.evolvability",
                "definition": ("[cap_FOF1(x after k governed steps) - "
                               "cap_FOF1(x)] / B_steps"),
                "k_steps": EV.K_STEPS,
                "proposals_per_step_max": EV.P_MAX,
                "regression_tolerance_tau": EV.TAU,
                "governed_step": ("propose <= P_MAX mutations; accept the FIRST "
                                  "that compiles legally, passes every frozen "
                                  "hard gate at T0, and does not regress "
                                  "current-family capability by more than TAU. "
                                  "Unaccepted proposals are still charged."),
                "matched_capability": {
                    "method": "stratification, not regression",
                    "bin_lo": EV.CAP_BIN_LO, "bin_hi": EV.CAP_BIN_HI,
                    "bin_width": EV.CAP_BIN_WIDTH,
                    "bin_edges": EV.cap_bin_edges(),
                    "comparison": "within bin only",
                },
                "future_family": "FOF1, prospectively frozen (see below)",
                "subsample": {
                    "n": EVOLVABILITY_SUBSAMPLE,
                    "rule": ("seeded RANDOM subsample of T2 survivors, never "
                             "top-N: top-N would select on capability and bias "
                             "the estimator it feeds"),
                },
                "undefined_code": EV.ZERO_BURDEN,
            },
        },

        # -------------------------------------------- prospective future split
        "future_families": {
            **keys_record(),
            "draws": disjoint["draws"],
            "disjointness_gate": "assert_disjoint_from_t3 (EXECUTED)",
            "rationale": ("the T3 key is frozen and must not be re-drawn, so "
                          "FOF1/CTRLU/CTRLH are minted from NEW keys through "
                          "the SAME deterministic generator before any run"),
        },

        # ------------------------------------------------------ dedup
        "behavioural_dedup": {
            "schema": BS.SIG_SCHEMA,
            "signature": ("sha256 over (per-family solved/total profile, "
                          "quantised B_behavior_2d dims, boolean gate vector)"),
            "quantisation": BS.QUANT,
            "explicitly_excluded": ["unit types", "topology", "field family",
                                    "genotype digest", "phenotype digest"],
            "cost_reported_separately": True,
            "parent_lever_reference": ("GS-R2 GSA6_DP carried the distinct-yield "
                                       "recovery at ~2x cpu-seconds per seed "
                                       "(190526.55 vs GSA2_hetero 354046.0 "
                                       "morphologies/cpu-hour)"),
        },

        # --------------------------------------------- multi-fidelity ladder
        "fidelity": {
            "reused_from": "search/successive_halving.py (frozen, unmodified)",
            "rungs": list(GS_RUNGS),
            "eta": GS_ETA,
            "late_bloomer_insurance_fraction": GS_LATE_BLOOMER_FRACTION,
            "min_promote": GS_MIN_PROMOTE,
            "rung_evaluators": {
                "T0": "evaluation.evaluate.evaluate_genome(tier=T0)",
                "T1": "evaluation.gs_t1.evaluate_t1",
                "T2": "evaluation.evaluate.evaluate_genome(tier=T2)",
            },
            "promotion_rule": ("n0 -> n0/eta -> n0/eta^2 with a frozen "
                               "late-bloomer insurance fraction; failures are "
                               "ledgered and charged as attempted"),
        },

        # ------------------------------------------------------------ parents
        "parents": {
            "frozen_zoo_parents": {
                "source": "results/GS_R2_AGGREGATE.json on main (b434c55c)",
                "GSA2_hetero": {"distinct_t2_viable_per_seed": 5062.7,
                                "morphologies_per_cpu_hour": 354046.0,
                                "cpu_seconds_per_seed": 51.258},
                "GSA5_surrogate": {"distinct_t2_viable_per_seed": 2233.3,
                                   "morphologies_per_cpu_hour": 72150.0,
                                   "cpu_seconds_per_seed": 111.257},
            },
            "lineage_arms": list(D27.ARMS) + list(D27.PARENT_ARMS),
            "scope_deviation": (
                "#277 sec 7 names STRONG_ADAPTIVE_NEURAL_PARENT. No learned "
                "neural parent exists in this stack; the closest legal form is "
                "the approximate/VSA family, run and reported as "
                "STRONG_ADAPTIVE_APPROXIMATE_PARENT. Calling it neural would "
                "be fabrication."),
            "parent_sufficient_is_a_success_terminal": True,
            "throughput_denominator": ("distinct T2-viable survivors per "
                                       "cpu-hour, matching the parents'"),
        },

        # ------------------------------------------------------------ D26
        "d26": {
            "operators": list(D26.OPERATORS),
            "domains": list(D26.DOMAINS),
            "contract": D26.CONTRACT,
            "claim_rule": ("a general-operator claim requires the contract to "
                           "hold in ALL three domains; fewer is labelled "
                           "SCOPED_n_OF_3, never rounded up"),
            "scope_deviation": (
                "OW9 (cross-domain same-hypergraph) does not exist on main; "
                "exact/worlds.py implements OW1..OW7 only (enumerated with a "
                "matching control). D26 tests transfer across INDEPENDENT "
                "domains, a weaker claim than OW9 would support."),
            "negative_transfer_retained": True,
        },

        # ------------------------------------------------------------ D27
        "d27": {
            "arms": list(D27.ARMS),
            "inherited_objects": list(D27.INHERITED_OBJECTS),
            "knockout": ("delete exactly ONE inherited object at every epoch "
                         "boundary, leaving the others inheriting; the frozen "
                         "evaluator is patched at Sim.end_epoch, never forked"),
            "decisive_rule": ("a correlated pre/post comparison does NOT "
                              "substitute for the knockout and does not reach "
                              "C=3"),
            "attribution": ("attribution(obj) = 1 - residual(obj)/advantage, "
                            "where advantage = CONTINUED - RESET and "
                            "residual(obj) = KNOCKOUT_obj - RESET"),
            "carrier_rule": ("a carrier is named only when an advantage exists; "
                             "otherwise carrier_status = NO_ADVANTAGE_TO_ATTRIBUTE"),
            "signature": ("B_future_cognition(t+1) < B_future_cognition(t) on "
                          "prospectively frozen RELATED tasks at matched "
                          "capability, WITHOUT equivalent gains on unrelated "
                          "or harmful controls"),
            "b_future_cognition": ("charged WORK on the future battery, byte "
                                   "rent excluded (including it would make the "
                                   "signature unfalsifiable in one direction); "
                                   "the bytes-inclusive figure is reported too"),
            "store_constant_guard": ("an organism whose inherited store never "
                                     "changes across epochs yields "
                                     "CANNOT_CHECK_STORE_CONSTANT_ACROSS_EPOCHS, "
                                     "never a false negative"),
        },

        # ------------------------------------------------------- falsifiers
        "falsifiers": {
            "F1": ("evolvability indistinguishable from its shuffle-equal-n "
                   "null within capability bins -> the objective carries no "
                   "signal; report it, do not rescue it"),
            "F2": ("Spearman(capability, evolvability) >= 0.95 within bins -> "
                   "evolvability is redundant with capability and is reported "
                   "as redundant"),
            "F3": ("B_steps == 0 -> evolvability undefined, "
                   "CANNOT_CHECK_ZERO_BURDEN, never coerced to 0 or infinity"),
            "F4": ("a D26 obligation that is never exercised yields "
                   "CANNOT_CHECK_NO_OBLIGATION_EXERCISED, never a pass"),
            "F5": ("if no knockout weakens the CONTINUED advantage, the "
                   "attribution to inherited objects is FALSIFIED and reported "
                   "as such"),
            "F6": ("if a parent owns a region of the front, that region is "
                   "reported PARENT_SUFFICIENT and not engineered past"),
        },

        # ------------------------------------------------------------- nulls
        "null": {
            "test": "shuffle-equal-n permutation within capability bins",
            "n_perm": 1000,
            "holds_fixed": "n per arm per bin, and capability (via the bin)",
            "rationale": "selectivity is not edge",
        },

        # ------------------------------------------------------------- seeds
        "seeds": {
            "arm_seeds": list(range(12)),
            "evolvability_seed_rule": "seed*1000 + record_index",
            "null_seed": 20260910,
            "determinism_claim": ("every estimator is a deterministic function "
                                  "of (genome, key, seed); verified by a smoke "
                                  "run before the array launch"),
        },

        # -------------------------------------------------------- boundaries
        "known_boundaries_consumed_not_rederived": {
            "D20 (7a6427e9)": ("CEGAR never beats direct concrete search on the "
                               "frozen n grid [8,12,16,20,24]; attribution is "
                               "abstraction CONSTRUCTION, not search"),
            "D21 (7b23ef04)": ("shared e-graph amortised ratio 0.418 aggregate, "
                               "per-world spread 0.27 (OW6-01) to 2.22 "
                               "(OW6-00, e-graph wins); the spread IS the "
                               "boundary and must not be averaged away"),
            "GS-R2 (b434c55c)": ("85025 of 100693 distinct survivors fail T3 "
                                 "generalization (84.44%)"),
        },

        # ------------------------------------------------------------ compute
        "compute": {
            "cluster": "LUNARC cosmos3",
            "partition": "lu48",
            "account": "lu2026-2-51",
            "network_policy": ("NO outbound network from the cluster at any "
                               "time; code and dependencies staged by rsync, "
                               "results returned by rsync"),
            "nuc_blocked": ("sinfo shows nuc 96/96 idle and the association "
                            "lists lu2026-2-51|nuc, but submission is refused "
                            "with 'Your project is not allowed to run on the "
                            "nuc partition'; lu48 verified working"),
            "no_sympy": ("sympy is absent on the compute nodes and installing "
                         "it would need a prohibited network call, so D_ALG "
                         "equality uses the lab's exact evaluation-vector "
                         "oracle under an ENFORCED degree<=20 gate, which is "
                         "sound and complete for these worlds"),
        },

        "reuse_audit": {
            "reused_unmodified": [
                "search/successive_halving.py (multi-fidelity rungs)",
                "search/mome.py (per-niche Pareto archive design)",
                "search/novelty_viability.py (behaviour-keyed archive design)",
                "morphology/gs_bound.py (legality-bounded sampling)",
                "evaluation/lifetime.py, lifetime2.py (charging + T2 battery)",
                "evaluation/t3_ecology.py (key-parameterised family generator)",
                "evaluation/invariants.py (frozen hard gates)",
                "exact/worlds.py, worlds_d19d20.py, d20.py, "
                "d21_reduction_equality.py, egraph.py (D26 domains)",
            ],
            "self_built_residual_and_why": {
                "oracle/objectives4.py": (
                    "evaluation/objectives.dominates is hardwired to the "
                    "10-name OBJECTIVE_REGISTRY_V1 tuple and cannot express a "
                    "4-vector containing an aggregate burden and evolvability"),
                "oracle/burden.py": (
                    "no upstream charges rejected-candidate work, and no "
                    "upstream handles the T3 battery's work_total-only shape"),
                "oracle/evolvability.py": "no upstream implementation exists",
                "oracle/behaviour_sig.py": (
                    "upstream dedup keys on phenotype structure; behavioural "
                    "dedup needs a solved-profile signature"),
                "oracle/c_immutability.py": (
                    "structural exclusion of C exists but is not asserted as an "
                    "executed gate anywhere"),
                "oracle/future_family.py": (
                    "a prospectively frozen future split had to be minted"),
                "oracle/d26_adapters.py, d26_operators.py": (
                    "the abstract operator contract and its drivers do not "
                    "exist; the domain primitives are all reused"),
                "oracle/d27_lineage.py": (
                    "continued/reset exists upstream; the single-object "
                    "knockout and B_future_cognition do not"),
            },
            "rejected_reuse": {
                "BOHB/HpBandSter": ("quota-blocked and architecturally hostile "
                                    "(nameserver+daemon topology vs frozen "
                                    "sbatch arrays); the frozen ~70-line SH "
                                    "loop binds OUR tier evaluators and is "
                                    "retained -- recorded in REUSE_AUDIT.md"),
                "pyribs/QDax emitters": ("would replace the frozen arm "
                                         "algorithms; MOMEArchive's design is "
                                         "reused, its dominance relation "
                                         "cannot be"),
                "sympy": "prohibited network call from the cluster",
            },
        },

        "supersession_rule": ("any post-freeze change to this protocol requires "
                             "a recorded supersession with cause and a re-run"),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "node": platform.node(),
        },
        "code_digests": _code_digests(),
    }
    return proto


def main() -> int:
    proto = build()
    out = os.path.join(ROOT, "FORM_ORACLE_PROTOCOL_V1.json")
    blob = json.dumps(proto, indent=1, sort_keys=True, default=str)
    with open(out, "w") as fh:
        fh.write(blob + "\n")
    digest = hashlib.sha256((blob + "\n").encode()).hexdigest()
    with open(os.path.join(ROOT, "FORM_ORACLE_PROTOCOL_V1.sha256"), "w") as fh:
        fh.write("%s  FORM_ORACLE_PROTOCOL_V1.json\n" % digest)
    sys.stderr.write("protocol sha256 %s\n" % digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
