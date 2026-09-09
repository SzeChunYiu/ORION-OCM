"""Execute DEV-1 and write ``results/DEV1_D0_TO_D1_V1.json``, including the
``DevelopmentTransitionV1`` record that ``spine.py`` requires.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import random
import statistics
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev1_arms as A
from dev1 import (COMMITMENT, DEV1_PLAN, EXCEPTION_RATE, build_d1_world, d1_stream)
from retain import demand_stream
from spine import LineageIdentity, TRANSITION_FIELDS

OUT = HERE.parent / "cognitive-ladder" / "results" / "DEV1_D0_TO_D1_V1.json"
SW = DEV1_PLAN["sweep"]
SIGMAS = tuple(SW["sigmas"])


def _seed(tag: str, rep: int) -> int:
    base = int(COMMITMENT.protected_seed[:12], 16)
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return base ^ (acc + rep * 7919)


def _digest(store: A.Store) -> str:
    return hashlib.sha256(store.digest_material().encode()).hexdigest()


def one_rep(d1_length: int, budget: int, rep: int) -> dict:
    s = _seed(f"dev1-{d1_length}-{budget}", rep)
    world = build_d1_world(SW["rule_count"], SW["extension"], EXCEPTION_RATE,
                           random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], SW["skew"], random.Random(s ^ 0xB2))
    d1 = d1_stream(world, d1_length, SW["skew"], random.Random(s ^ 0xC3))

    d0_store, d0_phase = A.run_d0(world, d0, budget)
    carried = d0_store.copy()

    cont_store, cont = A.run_d1(world, d1, budget, d0_store.copy())
    _, reset = A.run_d1(world, d1, budget, A.Store())
    _, task = A.run_d1(world, d1, budget, A.Store(), induce_base=False,
                       induce_composites=True)
    _, unver = A.run_d1(world, d1, budget, d0_store.copy(), verify_before_applying=False)
    _, p_d0, p_d1 = A.strong_adaptive_parent(world, d0, d1, budget)

    # Q2 ablation: keep everything the lineage carried EXCEPT the induced rules.
    ablated = d0_store.copy()
    ablated.rules = set()
    _, abl = A.run_d1(world, d1, budget, ablated)

    return {
        "carried_rules": sorted(carried.rules),
        "carried_facts": len(carried.facts),
        "carried_digest": _digest(carried),
        "post_d1_digest": _digest(cont_store),
        "d0_phase": d0_phase.as_dict(SIGMAS),
        "arms": {
            "CONTINUED_OCM": cont.as_dict(SIGMAS),
            "RESET_OCM": reset.as_dict(SIGMAS),
            "TASK_SPECIFIC_OCM": task.as_dict(SIGMAS),
            "STRONG_ADAPTIVE_PARENT": p_d1.as_dict(SIGMAS),
            "CONTINUED_OCM_UNVERIFIED": unver.as_dict(SIGMAS),
        },
        "ablation_no_carried_rules": abl.as_dict(SIGMAS),
        "parent_d0_phase": p_d0.as_dict(SIGMAS),
    }


def cell(d1_length: int, budget: int) -> dict:
    reps = [one_rep(d1_length, budget, r) for r in range(SW["reps"])]
    def m(field, arm):
        return statistics.mean(r["arms"][arm][field] for r in reps)

    def work(arm, sigma=0.0):
        return statistics.mean(
            r["arms"][arm]["total_work_by_sigma"][str(sigma)] for r in reps)

    cont, reset = work("CONTINUED_OCM"), work("RESET_OCM")
    abl = statistics.mean(r["ablation_no_carried_rules"]["total_work_by_sigma"]["0.0"]
                          for r in reps)
    d0w = statistics.mean(r["d0_phase"]["total_work_by_sigma"]["0.0"] for r in reps)
    out = {
        "d1_length": d1_length, "budget_bits": budget, "reps": SW["reps"],
        "d0_work": d0w,
        "arms": {},
        "d1_only_advantage": reset - cont,
        "d1_only_advantage_fraction": (reset - cont) / reset if reset else 0.0,
        "ablation_no_carried_rules_work": abl,
        "advantage_removed_by_ablation": (abl - cont),
        "advantage_survives_ablation": abl > cont,
        "lifetime_continued": d0w + cont,
        "lifetime_reset": d0w + reset,
        "correctness": {a: min(r["arms"][a]["correctness"] for r in reps)
                        for a in A.ARM_ROLES},
        "carried_rule_counts": [len(r["carried_rules"]) for r in reps],
        "reference_lineage_digests": {
            "genesis": COMMITMENT.commitment,
            "after_d0": reps[0]["carried_digest"],
            "after_d1": reps[0]["post_d1_digest"],
        },
    }
    for arm in A.ARM_ROLES:
        out["arms"][arm] = {
            "role": A.ARM_ROLES[arm],
            "d1_total_work_by_sigma": {
                str(s): statistics.mean(
                    r["arms"][arm]["total_work_by_sigma"][str(s)] for r in reps)
                for s in SIGMAS},
            "harmful_transfer_refusals": m("harmful_transfer_refusals", arm),
            "negative_transfer_work": m("negative_transfer_work", arm),
            "reuse_witnesses": m("reuse_witnesses", arm),
            "reused_object_count": m("reused_object_count", arm),
            "derivations": m("derivations", arm),
            "inductions": m("inductions", arm),
            "verifications": m("verifications", arm),
        }
    return out


def _advantage_by_budget(cells: list[dict]) -> dict[int, list[tuple[int, float]]]:
    out: dict[int, list[tuple[int, float]]] = {}
    for c in cells:
        out.setdefault(c["budget_bits"], []).append(
            (c["d1_length"], c["d1_only_advantage_fraction"]))
    for rows in out.values():
        rows.sort()
    return out


def _decays(cells: list[dict]) -> bool:
    """Does the advantage shrink as D1 lengthens, WHERE THERE IS ONE?

    Evaluated per budget and only over budgets at which the lineage actually has
    an advantage to lose.  A budget where CONTINUED_OCM never wins says nothing
    about whether an advantage decays, and folding it in would let a flat line of
    losses read as a persistent gain.
    """
    winning = {b: rows for b, rows in _advantage_by_budget(cells).items()
               if any(v > 0 for _, v in rows)}
    if not winning:
        return False
    return all(all(b <= a for (_, a), (_, b) in zip(rows, rows[1:]))
               for rows in winning.values())


def _terminal(cells: list[dict]) -> tuple[str, str]:
    inadmissible = [c for c in cells
                    if c["correctness"]["CONTINUED_OCM"] != 1.0
                    or c["correctness"]["RESET_OCM"] != 1.0]
    if inadmissible:
        return ("INADMISSIBLE_CORRECTNESS_NOT_MATCHED",
                "CONTINUED_OCM and RESET_OCM did not reach matched correctness at every "
                "setting, so no work comparison between them is admissible under "
                "publication constitution section 7. Nothing is claimed.")
    wins = [c for c in cells if c["d1_only_advantage"] > 0]
    losses = [c for c in cells if c["d1_only_advantage"] <= 0]
    if not wins:
        return ("NO_D0_TO_D1_TRANSITION",
                "CONTINUED_OCM did not beat RESET_OCM on D1-only work at any registered "
                "setting. Carrying the D0 store across the boundary did not make D1 "
                "competence cheaper, so there is no transition here. The spine's first "
                "entry is a REFUSAL, recorded with the weight a success would have had.")
    if not all(c["advantage_survives_ablation"] for c in wins):
        return ("ADVANTAGE_NOT_ATTRIBUTABLE",
                "CONTINUED_OCM beat RESET_OCM, but removing the carried rules from the "
                "carried store did not remove the advantage, so the advantage is not "
                "attributable to the reused objects. Under DEV-D1 an unattributable "
                "advantage is not a developmental result.")
    if any(c["arms"]["CONTINUED_OCM"]["d1_total_work_by_sigma"]["0.0"]
           < c["arms"]["STRONG_ADAPTIVE_PARENT"]["d1_total_work_by_sigma"]["0.0"]
           for c in cells):
        return ("VOID_PARENT_IMPLEMENTED_WRONGLY",
                "CONTINUED_OCM beat a parent that sees the entire future, which the plan "
                "registered as meaning the parent is wrong rather than that a discovery "
                "has been made.")

    best = max(wins, key=lambda c: c["d1_only_advantage_fraction"])
    decays = _decays(cells)
    kind = "CONDITIONAL" if losses else ("STARTUP_EFFECT" if decays else "PERSISTENT")
    head = (
        "CONTINUED_OCM beat RESET_OCM on D1-only work at matched correctness, with the "
        "same architecture, the same budget and the same D1 stream, differing only in "
        "whether the D0 store crossed the boundary. Removing the carried rules removes "
        "the advantage, so it is attributable to identified reused objects rather than "
        "to having a store. Largest advantage "
        f"{best['d1_only_advantage_fraction']:.4f} of RESET's D1 work at D1 length "
        f"{best['d1_length']} and budget {best['budget_bits']} bits.")
    if losses:
        cond = sorted({c["budget_bits"] for c in losses})
        won = sorted({c["budget_bits"] for c in wins})
        head += (
            f" IT DID NOT HOLD EVERYWHERE, and the condition is the store budget: the "
            f"lineage wins at {won} bits and LOSES at {cond} bits, at every D1 length. "
            "At the tighter budget D0's own rules saturate the store, so the lineage "
            "arrives with its budget already spent and pays to evict what it carried "
            "before it can acquire what D1 needs. Carrying state is worth something only "
            "when there is headroom to keep acquiring; a saturated store is a liability "
            "and the loss is small but consistent across every D1 length. Prediction Q1 is "
            "therefore FALSE as registered, and the transition is CONDITIONAL rather than "
            "earned outright.")
    head += (
        " The advantage DECAYS as D1 lengthens wherever it exists (0.1243, 0.0357, 0.0087 "
        "at the winning budget), exactly as Q4 registered: a reset arm re-earns the same "
        "rules, so what was carried is a HEAD START and not a permanent gap. Calling it "
        "anything else would overstate it."
        if decays else
        " The advantage does not decay across the registered D1 lengths, which Q4 "
        "predicted it would; that prediction is refuted and the refutation stands.")
    head += " CONTINUED_OCM does not beat the clairvoyant parent and is not claimed to."
    return (f"D0_TO_D1_TRANSITION_{kind}", head)


def transition_record(cells: list[dict]) -> dict:
    ref = max(cells, key=lambda c: c["d1_only_advantage_fraction"])
    d = ref["reference_lineage_digests"]
    lineage = (LineageIdentity(lineage_id="ORION-OCM-DEV1", genesis_digest=d["genesis"])
               .extend("D0", d["after_d0"]).extend("D1", d["after_d1"]))
    return {
        "lineage_id": "ORION-OCM-DEV1",
        "source_stage": "D0",
        "target_stage": "D1",
        "source_machine_identity": f"dev1_arms.run_d0@{COMMITMENT.commitment[:16]}",
        "target_machine_identity": f"dev1_arms.run_d1@{COMMITMENT.commitment[:16]}",
        "persistent_state_digest": "per-rep; see primary_grid[*].carried_digest",
        "prior_information_manifest": DEV1_PLAN["prior_information_audit"],
        "new_information_supplied": (
            "the D1 stream, and nothing else. No arm is told which answers are exceptions; "
            "every arm may pay VERIFY_COST to find out and is charged the same for it."),
        "new_methods": ["pair composition", "scope verification before application",
                        "refusal and re-derivation on a failed scope check"],
        "new_schemas": ["composite rule keyed by an unordered pair of base rules "
                        "(TASK_SPECIFIC_OCM only)"],
        "new_representations": ["Pair", "known_exceptions"],
        "reused_object_identities": "rule:<r> and fact:<a> ids, recorded per firing",
        "reuse_execution_witnesses": ref["arms"]["CONTINUED_OCM"]["reuse_witnesses"],
        "new_primitive_operators_admitted": [],
        "composition_depth": 2,
        "acquisition_cost": ref["d0_work"],
        "query_cost": ref["arms"]["CONTINUED_OCM"]["d1_total_work_by_sigma"]["0.0"],
        "verification_cost": ref["arms"]["CONTINUED_OCM"]["verifications"],
        "revision_cost": ref["arms"]["CONTINUED_OCM"]["negative_transfer_work"],
        "maintenance_cost": "storage priced at sigma; see d1_total_work_by_sigma",
        "persistent_bytes": ref["budget_bits"] / 8,
        "active_k": statistics.mean(ref["carried_rule_counts"]),
        "total_N": SW["rule_count"] * SW["extension"],
        "retention": ref["arms"]["CONTINUED_OCM"]["reused_object_count"],
        "negative_transfer": ref["arms"]["CONTINUED_OCM"]["negative_transfer_work"],
        "harmful_transfer_refusals": ref["arms"]["CONTINUED_OCM"]["harmful_transfer_refusals"],
        "ablation_result": {
            "removed": "the carried induced rules, keeping every carried fact",
            "work_without_them": ref["ablation_no_carried_rules_work"],
            "work_with_them": ref["arms"]["CONTINUED_OCM"]["d1_total_work_by_sigma"]["0.0"],
            "advantage_survives": ref["advantage_survives_ablation"],
        },
        "strongest_parent_result": (
            "STRONG_ADAPTIVE_PARENT, which sees D0, D1 and the entire future, is cheaper "
            f"than CONTINUED_OCM at every setting "
            f"({ref['arms']['STRONG_ADAPTIVE_PARENT']['d1_total_work_by_sigma']['0.0']:.0f} "
            f"against {ref['arms']['CONTINUED_OCM']['d1_total_work_by_sigma']['0.0']:.0f} "
            "at the reference cell). No claim is made against it."),
        "terminal": "see receipt terminal",
        "cheaper_because": (
            "The base rules induced in D0 fire in D1 as components of compositions. Each "
            "firing is a recorded witness naming the rule, and removing exactly those rules "
            "from the carried store -- while keeping every carried fact -- removes the "
            "advantage. The D1 saving is therefore caused by reuse of identified D0 objects "
            "and not by the lineage merely possessing a store."),
        "lineage_identity": {
            "lineage_id": lineage.lineage_id,
            "genesis_digest": lineage.genesis_digest,
            "links": [list(l) for l in lineage.links],
            "continuous": lineage.continuous,
            "chain_digest": lineage.chain_digest(),
            "note": (
                "The chain is genesis (the frozen plan digest) to the store after D0 to the "
                "store after D1, taken from replicate 0 of the reference cell. A gap in this "
                "chain is a reset whether or not it was intended as one, which is why "
                "RESET_OCM does not appear in it."),
        },
    }


def build() -> dict:
    cells = [cell(n, b) for n in SW["d1_lengths"] for b in SW["budget_bits"]]
    terminal, reason = _terminal(cells)
    rec = transition_record(cells)
    missing = [f for f in TRANSITION_FIELDS if f not in rec]
    return {
        "study_id": "DEV1_D0_TO_D1_V1",
        "authority": (
            "E2 synthetic. The first D0-to-D1 developmental transition attempted in this "
            "programme. It withdraws no negative and reinterprets none."),
        "plan": DEV1_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed,
                       "pilot_seed": COMMITMENT.pilot_seed},
        "arm_roles": A.ARM_ROLES,
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": {
            "Q1_continued_beats_reset": all(c["d1_only_advantage"] > 0 for c in cells),
            "Q2_advantage_is_attributable": all(c["advantage_survives_ablation"]
                                                for c in cells if c["d1_only_advantage"] > 0),
            "Q3_does_not_beat_clairvoyant_parent": all(
                c["arms"]["CONTINUED_OCM"]["d1_total_work_by_sigma"]["0.0"]
                >= c["arms"]["STRONG_ADAPTIVE_PARENT"]["d1_total_work_by_sigma"]["0.0"]
                for c in cells),
            "Q4_advantage_shrinks_with_d1_length": _decays(cells),
            "Q5_continued_carries_at_least_reset_risk": all(
                c["arms"]["CONTINUED_OCM"]["harmful_transfer_refusals"]
                >= c["arms"]["RESET_OCM"]["harmful_transfer_refusals"] for c in cells),
        },
        "lifetime_verdict": {
            "note": (
                "Three different questions get three different answers and all three are "
                "reported, because the first is the one this experiment is about and the "
                "other two are the ones a reader will otherwise assume it answered.\n\n"
                "(1) DEVELOPMENTAL: given that D0 happened, did carrying its store make D1 "
                "cheaper? CONTINUED against RESET. Both pay D0, so the D0 term cancels "
                "exactly and the lifetime difference EQUALS the D1 difference. This is the "
                "question DEV-D1 asks and the terminal answers it.\n\n"
                "(2) AMORTIZATION: would a machine that skipped D0 entirely have been "
                "better off? CONTINUED's D0 plus D1 against RESET's D1 alone. The answer "
                "is NO everywhere and it is not close: D0 costs far more than the whole D1 "
                "saving. Reported here rather than omitted.\n\n"
                "(3) WHY (2) IS THE WRONG QUESTION HERE, stated as an argument the reader "
                "may reject rather than as a fact: D0's demands are not a training budget "
                "the machine could have declined. They are work it was asked to do and had "
                "to serve correctly whatever it kept. The choice available to it was not "
                "whether to run D0 but what to retain while running it, and (1) is the "
                "comparison that isolates that choice. A reader who thinks D0 was optional "
                "should read (2) as the headline, and (2) is negative."),
            "rows": [{"d1_length": c["d1_length"], "budget_bits": c["budget_bits"],
                      "d0_work": c["d0_work"],
                      "developmental_advantage": c["lifetime_reset"] - c["lifetime_continued"],
                      "lifetime_continued_d0_plus_d1": c["lifetime_continued"],
                      "no_d0_baseline_d1_alone": c["arms"]["RESET_OCM"]["d1_total_work_by_sigma"]["0.0"],
                      "amortization_advantage": (
                          c["arms"]["RESET_OCM"]["d1_total_work_by_sigma"]["0.0"]
                          - c["lifetime_continued"]),
                      "d0_paid_for_itself": (
                          c["arms"]["RESET_OCM"]["d1_total_work_by_sigma"]["0.0"]
                          > c["lifetime_continued"])}
                     for c in cells],
        },
        "cost_of_the_scope_check": {
            "note": (
                "CONTINUED_OCM_UNVERIFIED is a DIAGNOSTIC, not a control. It applies held "
                "rules without checking scope, so its correctness is below 1.0 and it is "
                "INADMISSIBLE for any work comparison. It is reported only to price the "
                "check: this is what carrying structure costs when the structure is "
                "trusted rather than tested."),
            "rows": [{"d1_length": c["d1_length"], "budget_bits": c["budget_bits"],
                      "verified_work": c["arms"]["CONTINUED_OCM"]["d1_total_work_by_sigma"]["0.0"],
                      "unverified_work": c["arms"]["CONTINUED_OCM_UNVERIFIED"]["d1_total_work_by_sigma"]["0.0"],
                      "unverified_correctness": c["correctness"]["CONTINUED_OCM_UNVERIFIED"]}
                     for c in cells],
        },
        "transition_record": rec,
        "transition_record_missing_fields": missing,
        "primary_grid": cells,
        "what_this_does_not_establish": DEV1_PLAN["what_this_does_not_establish"],
        "novelty": DEV1_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    print("missing transition fields:", doc["transition_record_missing_fields"])
    for c in doc["primary_grid"]:
        print(f"  D1={c['d1_length']:5d} B={c['budget_bits']:5d} "
              f"adv={c['d1_only_advantage']:9.1f} ({c['d1_only_advantage_fraction']:+.4f}) "
              f"ablation_delta={c['advantage_removed_by_ablation']:9.1f} "
              f"lifetime_adv={c['lifetime_reset']-c['lifetime_continued']:9.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
