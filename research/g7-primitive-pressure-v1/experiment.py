"""G7 primitive-pressure measurement on frozen lineage receipts.

Cites research/g7-lineage-v1 through research/g7-lineage-d6-v6 RESULT.json.
Does not overwrite them, does not rerun the lineage, and does not import
production ocm modules. Historical M11 generations are not relabeled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

SCHEMA = "ocm.g7.primitive-pressure.result.v1"
ISSUE = 165
GATE = "primitive_pressure_tracked"
SALT = "orion-ocm-g7-primitive-pressure-v1"
LINEAGE_ID = "orion-ocm-g7-lineage-v1:microscope-d0-d1"
ALREADY_EARNED_PREFIX = "donor:already-earned:"

TERMINAL_DECLINES = "PRIMITIVE_PRESSURE_DECLINES_AT_SCOPE"
TERMINAL_PERSISTS = "PRIMITIVE_PRESSURE_PERSISTS"
TERMINAL_PARENT = "PARENT_SUFFICIENT"
ALLOWED_TERMINALS = frozenset({TERMINAL_DECLINES, TERMINAL_PERSISTS, TERMINAL_PARENT})

CITATIONS: tuple[dict[str, Any], ...] = (
    {
        "capsule": "research/g7-lineage-v1/RESULT.json",
        "sha256": "018b9cb8077a6a1bb8665746928a786a4eb3b807f0708d563cc6ea54da7bb653",
        "earned_transitions": 2,
        "final_stage": "OCM_1",
    },
    {
        "capsule": "research/g7-lineage-d2-v2/RESULT.json",
        "sha256": "e54bbd42fa47db51e88f75992266d62d633f55b77547e5bd9e44b1ead19b2645",
        "earned_transitions": 3,
        "final_stage": "OCM_2",
    },
    {
        "capsule": "research/g7-lineage-d3-v3/RESULT.json",
        "sha256": "6409f43a089791c78c0484a5f8b1e94fde35baa6de2aa2f726966768fa55eb71",
        "earned_transitions": 4,
        "final_stage": "OCM_3",
    },
    {
        "capsule": "research/g7-lineage-d4-v4/RESULT.json",
        "sha256": "8a66c42aa1b091dfcae7f4cdda33615a6a811e5d98866e4ad849d698cf096c70",
        "earned_transitions": 5,
        "final_stage": "OCM_4",
    },
    {
        "capsule": "research/g7-lineage-d5-v5/RESULT.json",
        "sha256": "2dcbf03e0535d21383303b5a4e9a3fc01bd9e04dd1b1e97783ea54a9d70fdadd",
        "earned_transitions": 6,
        "final_stage": "OCM_5",
    },
    {
        "capsule": "research/g7-lineage-d6-v6/RESULT.json",
        "sha256": "91212afaf97724bdce1c7b0a6457cca223883451d488d25568be69183eb61895",
        "earned_transitions": 7,
        "final_stage": "OCM_6",
        "primary": True,
    },
)

EXPECTED_STAGES = (
    ("EMPTY", "OCM_0"),
    ("OCM_0", "OCM_1"),
    ("OCM_1", "OCM_2"),
    ("OCM_2", "OCM_3"),
    ("OCM_3", "OCM_4"),
    ("OCM_4", "OCM_5"),
    ("OCM_5", "OCM_6"),
)

NOT_ISSUED = (
    "PHASED_COGNITIVE_DEVELOPMENT",
    "DEVELOPMENTAL_EVOLVABILITY_SUPPORTED",
    "DEVELOPMENTAL_CROSS_FAMILY_TRANSFER_SUPPORTED",
    "DEVELOPMENTAL_AMORTIZATION_SUPPORTED_AT_SCOPE",
    "CAUSAL_METHOD_REUSE_SUPPORTED",
    "MINIMUM_SELF_EXTENDING_VESSEL",
    "PROGRAMME_CLOSED",
    "ISSUE_73_PROTOTYPE",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def is_already_earned(identity: str) -> bool:
    return identity.startswith(ALREADY_EARNED_PREFIX)


def new_hand_authored(transition: dict[str, Any]) -> list[str]:
    if transition["source_stage"] == "EMPTY":
        identities = list(transition["imported_donor_identities"])
    else:
        identities = list(transition["primitive_operators_added"])
    return [ident for ident in identities if not is_already_earned(ident)]


def verified_competence(transition: dict[str, Any]) -> int:
    return sum(1 for row in transition["actual_execution_witnesses"] if row.get("verified"))


def learned_objects(transition: dict[str, Any]) -> int:
    return sum(
        1
        for row in transition["new_methods_schemas"]
        if row.get("origin_category") in ("LEARNED_COMPOSITION", "LEARNED_APPLICABILITY")
    )


def kendall_tau(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("kendall_tau needs two equal-length series of length >= 2")
    conc = disc = 0
    n = len(xs)
    for i in range(n):
        for j in range(i + 1, n):
            dx = xs[j] - xs[i]
            dy = ys[j] - ys[i]
            product = dx * dy
            if product > 0:
                conc += 1
            elif product < 0:
                disc += 1
    denom = n * (n - 1) / 2
    return (conc - disc) / denom


def mean_first_difference(values: list[float]) -> float:
    if len(values) < 2:
        raise ValueError("need at least two points")
    return sum(values[i] - values[i - 1] for i in range(1, len(values))) / (len(values) - 1)


def decide(p_stack_continued: list[float], p_stack_reset: list[float]) -> str:
    if len(p_stack_continued) != len(p_stack_reset) or len(p_stack_continued) < 2:
        return TERMINAL_PERSISTS
    if all(cont == reset for cont, reset in zip(p_stack_continued, p_stack_reset)):
        return TERMINAL_PARENT
    stages = [float(i) for i in range(len(p_stack_continued))]
    tau = kendall_tau(stages, p_stack_continued)
    mean_d = mean_first_difference(p_stack_continued)
    later_beats_reset = all(
        p_stack_continued[i] < p_stack_reset[i] for i in range(1, len(p_stack_continued))
    )
    declines = (
        len(p_stack_continued) >= 7
        and p_stack_continued[-1] < p_stack_continued[0]
        and mean_d < 0
        and tau < 0
        and later_beats_reset
        and p_stack_reset[0] == 1.0
    )
    if declines:
        return TERMINAL_DECLINES
    return TERMINAL_PERSISTS


def load_json(rel: str) -> dict[str, Any]:
    path = REPO / rel
    return json.loads(path.read_text(encoding="utf-8"))


def cite_predecessors() -> list[dict[str, Any]]:
    rows = []
    for spec in CITATIONS:
        path = REPO / spec["capsule"]
        digest = sha256_file(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if digest != spec["sha256"]:
            raise RuntimeError(
                "frozen RESULT hash mismatch for %s: got %s want %s"
                % (spec["capsule"], digest, spec["sha256"])
            )
        if payload.get("lineage_id") != LINEAGE_ID:
            raise RuntimeError("lineage id mismatch in %s" % spec["capsule"])
        if payload.get("terminal") != "PHASED_COGNITIVE_DEVELOPMENT":
            raise RuntimeError("predecessor terminal is not PHASED_COGNITIVE_DEVELOPMENT: %s" % spec["capsule"])
        if payload.get("earned_transitions") != spec["earned_transitions"]:
            raise RuntimeError("earned_transitions mismatch in %s" % spec["capsule"])
        if payload.get("final_stage") != spec["final_stage"]:
            raise RuntimeError("final_stage mismatch in %s" % spec["capsule"])
        rows.append(
            {
                "capsule": spec["capsule"],
                "sha256": digest,
                "terminal": payload["terminal"],
                "earned_transitions": payload["earned_transitions"],
                "final_stage": payload["final_stage"],
                "lineage_id": payload["lineage_id"],
                "primary": bool(spec.get("primary")),
                "historical_m11_relabeled": bool(payload.get("historical_m11_relabeled", False)),
            }
        )
    if any(row["historical_m11_relabeled"] for row in rows):
        raise RuntimeError("a cited G7 RESULT relabeled historical M11")
    return rows


def measure_transitions(d6: dict[str, Any]) -> list[dict[str, Any]]:
    transitions = list(d6["transitions"])
    if len(transitions) != 7:
        raise RuntimeError("D6 RESULT must contain seven earned transitions, got %d" % len(transitions))
    series = []
    cumulative: list[str] = []
    for index, transition in enumerate(transitions):
        expected_source, expected_target = EXPECTED_STAGES[index]
        if (transition["source_stage"], transition["target_stage"]) != (expected_source, expected_target):
            raise RuntimeError(
                "unexpected stage pair at T%d: %s -> %s"
                % (index, transition["source_stage"], transition["target_stage"])
            )
        if transition.get("lineage_id") != LINEAGE_ID:
            raise RuntimeError("transition T%d lineage mismatch" % index)
        new_prims = new_hand_authored(transition)
        for ident in new_prims:
            if ident not in cumulative:
                cumulative.append(ident)
        n_new = len(new_prims)
        n_cum = len(cumulative)
        q_t = verified_competence(transition)
        n_learned = learned_objects(transition)
        parent = transition["strongest_parent_result"]
        p_stack_continued = n_new / n_cum if n_cum else 0.0
        p_stack_reset = 1.0
        p_comp_continued = n_new / q_t if q_t else 0.0
        p_comp_reset = n_cum / q_t if q_t else 0.0
        series.append(
            {
                "id": "T%d" % index,
                "source_stage": transition["source_stage"],
                "target_stage": transition["target_stage"],
                "new_hand_authored": new_prims,
                "n_new": n_new,
                "n_cum": n_cum,
                "Q": q_t,
                "n_learned": n_learned,
                "p_stack_continued": p_stack_continued,
                "p_stack_reset": p_stack_reset,
                "p_comp_continued": p_comp_continued,
                "p_comp_reset": p_comp_reset,
                "reset_costs_more_or_fails_reuse": bool(parent.get("reset_costs_more_or_fails_reuse")),
                "parent_ties_continued_mechanism": bool(parent.get("parent_ties_continued_mechanism")),
                "winner": parent.get("winner"),
                "continued_work_units": parent["CONTINUED_OCM"]["work_units"],
                "reset_work_units": parent["RESET_OCM"]["work_units"],
                "parent_work_units": parent["STRONG_ADAPTIVE_PARENT"]["work_units"],
                "transition_terminal": transition["terminal"],
            }
        )
    return series


def run_study() -> dict[str, Any]:
    citations = cite_predecessors()
    d6 = load_json("research/g7-lineage-d6-v6/RESULT.json")
    series = measure_transitions(d6)
    p_stack_continued = [row["p_stack_continued"] for row in series]
    p_stack_reset = [row["p_stack_reset"] for row in series]
    terminal = decide(p_stack_continued, p_stack_reset)
    stages = [float(i) for i in range(len(p_stack_continued))]
    tau = kendall_tau(stages, p_stack_continued)
    mean_d = mean_first_difference(p_stack_continued)
    later_beats_reset = all(
        p_stack_continued[i] < p_stack_reset[i] for i in range(1, len(p_stack_continued))
    )
    result = {
        "schema": SCHEMA,
        "issue": ISSUE,
        "gate": GATE,
        "salt": SALT,
        "git_head": git_head(),
        "lineage_id": LINEAGE_ID,
        "scope": "registered G7 miniature microscope D0-D6; not programme-wide",
        "primary_source": "research/g7-lineage-d6-v6/RESULT.json",
        "citations": citations,
        "series": series,
        "p_stack_continued": p_stack_continued,
        "p_stack_reset": p_stack_reset,
        "p_comp_continued": [row["p_comp_continued"] for row in series],
        "p_comp_reset": [row["p_comp_reset"] for row in series],
        "kendall_tau_stack_continued": tau,
        "mean_first_difference_stack_continued": mean_d,
        "t6_stack_lt_t0": p_stack_continued[-1] < p_stack_continued[0],
        "later_continued_beats_reset": later_beats_reset,
        "reset_reimports_full_stack": all(value == 1.0 for value in p_stack_reset),
        "earned_transitions": len(series),
        "historical_m11_relabeled": False,
        "programme_tick": False,
        "issue_73": False,
        "src_edited": False,
        "lineage_rerun": False,
        "ml_trained": False,
        "terminal": terminal,
        "not_issued": list(NOT_ISSUED),
        "claim_boundary": (
            "Primitive-pressure stack fraction on the existing earned G7 "
            "transitions versus reset, at this miniature scope. Not a "
            "programme-wide developmental close and not #73."
        ),
    }
    if terminal not in ALLOWED_TERMINALS:
        raise RuntimeError("illegal terminal %s" % terminal)
    if result["programme_tick"] or result["issue_73"] or result["historical_m11_relabeled"]:
        raise RuntimeError("honesty flags tripped")
    return result


def write_outputs(out: Path | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or run_study()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    capsule = HERE / "RESULT.json"
    capsule.write_text(text, encoding="utf-8")
    if out is not None and out.resolve() != capsule.resolve():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None)
    parser.add_argument("positional_out", nargs="?", default=None)
    args = parser.parse_args(argv)
    target = args.out or args.positional_out
    out = Path(target) if target else HERE / "RESULT.json"
    result = write_outputs(out)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "earned_transitions": result["earned_transitions"],
                "p_stack_continued": result["p_stack_continued"],
                "kendall_tau_stack_continued": result["kendall_tau_stack_continued"],
                "mean_first_difference_stack_continued": result["mean_first_difference_stack_continued"],
                "later_continued_beats_reset": result["later_continued_beats_reset"],
                "programme_tick": result["programme_tick"],
                "issue_73": result["issue_73"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return result


if __name__ == "__main__":
    main()
