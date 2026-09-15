"""Exact finite developmental capability predictions (602 L4 / 592.28 support).

Parents
-------
- research/gmi-developmental-taxonomy-v1 (A3): INFO/RECODE/SKILL/LAW/MORPH
  structure kinds on the n=3 fixture.
- research/gmi-biology-predictions-v1 (592.25-28 lane): ecology/resource/
  verifier developmental trajectories (exact integer lift here).
- research/gmi-capability-contract-v1 (A4): capability row ids reused as labels.

All values are exact ints / frozensets / tuples. CPython 3.8 safe. No network.
No sampling. Held-out literature registry is never an input to prediction.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Stages and ecology (biology-parent integer lift)
# ---------------------------------------------------------------------------

STAGES: Tuple[str, ...] = (
    "infant",
    "toddler",
    "child",
    "adolescent",
    "adult",
)

# (E, R, V, S) at each stage. S = social-topology budget coordinate.
# Human-like high ecology E=9 held fixed (biology HUMAN_E), R/V/S grow.
STAGE_ECOLOGY: Tuple[Tuple[int, int, int, int], ...] = (
    (9, 1, 1, 0),  # infant
    (9, 2, 2, 1),  # toddler
    (9, 4, 4, 2),  # child
    (9, 6, 6, 4),  # adolescent
    (9, 8, 8, 5),  # adult
)

assert len(STAGES) == len(STAGE_ECOLOGY)


# ---------------------------------------------------------------------------
# Accumulated structure schedule (taxonomy kinds, exact)
# ---------------------------------------------------------------------------
# skill_count mirrors |K| growth under SKILL; recode/law/morph are 0/1 flags
# after the corresponding g-preserving taxonomy predicates have fired.
# Derived from the taxonomy witness round-robin prefix (INFO,RECODE,SKILL,
# LAW,MORPH) x rounds — frozen here so prediction never needs network I/O.

# stage -> (skill_count, recode, law, morph, info_updates)
STRUCTURE_AT_STAGE: Tuple[Tuple[int, int, int, int, int], ...] = (
    (0, 0, 0, 0, 0),  # infant: no accumulated structure
    (0, 1, 0, 0, 1),  # toddler: INFO + RECODE
    (1, 1, 0, 0, 2),  # child: + SKILL (|K|=1)
    (2, 1, 1, 0, 3),  # adolescent: + SKILL (|K|=2) + LAW
    (3, 1, 1, 1, 4),  # adult: + SKILL (|K|=3) + MORPH
)

assert len(STRUCTURE_AT_STAGE) == len(STAGES)


# ---------------------------------------------------------------------------
# Capability catalogue (A4 ids + social-depth ladder)
# ---------------------------------------------------------------------------

CAPABILITIES: Tuple[str, ...] = (
    "cap-perception",
    "cap-working-memory",
    "cap-procedural-memory",
    "cap-compositional-reasoning",
    "cap-abstraction-concept",
    "cap-social-cognition",
    "cap-hierarchical-skill",
    "cap-metacognition",
)

# Direct prior-structure / ecology gates (exact).
# Fields: min_R, min_S, min_skill, need_recode, need_law, need_morph, deps
Gate = Tuple[int, int, int, int, int, int, Tuple[str, ...]]

GATES: Dict[str, Gate] = {
    "cap-perception": (1, 0, 0, 0, 0, 0, ()),
    "cap-working-memory": (2, 0, 0, 0, 0, 0, ("cap-perception",)),
    "cap-procedural-memory": (2, 0, 1, 0, 0, 0, ("cap-working-memory",)),
    "cap-compositional-reasoning": (
        4,
        0,
        2,
        1,
        0,
        0,
        ("cap-procedural-memory",),
    ),
    "cap-abstraction-concept": (
        4,
        0,
        2,
        1,
        0,
        0,
        ("cap-procedural-memory",),
    ),
    "cap-social-cognition": (2, 1, 0, 0, 0, 0, ("cap-working-memory",)),
    "cap-hierarchical-skill": (
        6,
        0,
        3,
        1,
        0,
        0,
        ("cap-compositional-reasoning",),
    ),
    "cap-metacognition": (
        6,
        0,
        2,
        1,
        1,
        0,
        ("cap-abstraction-concept",),
    ),
}

assert set(GATES) == set(CAPABILITIES)

# Social inference depth ladder (exact). Depth d requires S >= threshold
# and all shallower depths already available.
SOCIAL_DEPTH_S_THRESHOLDS: Tuple[int, ...] = (0, 1, 2, 4, 5)  # depth 0..4
# depth d>=2 also requires compositional abstraction for nested inference
SOCIAL_DEPTH_NEEDS_COMPOSITION: int = 3


# Sensitive-period law for MORPH (resource/ecology assumptions):
# MORPH is admissible only when R >= MORPH_COST and V < V_LOCK.
# Outside that window morphology change is locked (high verifier freeze).
MORPH_COST: int = 3
V_LOCK: int = 7


# Forbidden fit fields (held-out / identity leakage)
FORBIDDEN_FIT_FIELDS = frozenset(
    (
        "heldout_outcome",
        "held_out",
        "citation",
        "literature_id",
        "source_ref",
        "dataset_id",
        "test_outcome",
        "family_name",
    )
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def stage_index(name_or_idx):
    if isinstance(name_or_idx, int):
        if name_or_idx < 0 or name_or_idx >= len(STAGES):
            raise ValueError("stage index out of range: %r" % (name_or_idx,))
        return name_or_idx
    if name_or_idx not in STAGES:
        raise ValueError("unknown stage: %r" % (name_or_idx,))
    return STAGES.index(name_or_idx)


def ecology_at(stage):
    i = stage_index(stage)
    E, R, V, S = STAGE_ECOLOGY[i]
    return {"E": E, "R": R, "V": V, "S": S, "stage": STAGES[i], "t": i}


def structure_at(stage):
    i = stage_index(stage)
    sk, recode, law, morph, info = STRUCTURE_AT_STAGE[i]
    return {
        "skill_count": sk,
        "recode": recode,
        "law": law,
        "morph": morph,
        "info_updates": info,
        "stage": STAGES[i],
        "t": i,
    }


def _check_cap(cap):
    if cap not in GATES:
        raise ValueError("unknown capability: %r" % (cap,))
    return cap


def depends_on_accumulated_structure(cap):
    """True iff emergence gate requires taxonomy-accumulated structure."""
    _check_cap(cap)
    min_R, min_S, min_skill, need_recode, need_law, need_morph, _deps = GATES[cap]
    return (
        min_skill > 0
        or need_recode == 1
        or need_law == 1
        or need_morph == 1
    )


def gate_satisfied(cap, stage, emerged):
    """Whether cap's local gates hold at stage given already-emerged set."""
    _check_cap(cap)
    eco = ecology_at(stage)
    st = structure_at(stage)
    min_R, min_S, min_skill, need_recode, need_law, need_morph, deps = GATES[cap]
    if eco["R"] < min_R:
        return False
    if eco["S"] < min_S:
        return False
    if st["skill_count"] < min_skill:
        return False
    if need_recode and st["recode"] != 1:
        return False
    if need_law and st["law"] != 1:
        return False
    if need_morph and st["morph"] != 1:
        return False
    for d in deps:
        if d not in emerged:
            return False
    return True


def morph_admissible(stage):
    """Sensitive-period predicate for MORPH under resource/verifier assumptions."""
    eco = ecology_at(stage)
    return eco["R"] >= MORPH_COST and eco["V"] < V_LOCK


def sensitive_period_morph():
    """Return (first_stage_name, last_stage_name) or None if empty/all/none."""
    admissible = [STAGES[i] for i in range(len(STAGES)) if morph_admissible(i)]
    if not admissible:
        return None
    if len(admissible) == len(STAGES):
        # no selective window — not a sensitive period under these assumptions
        return None
    return (admissible[0], admissible[-1])


# ---------------------------------------------------------------------------
# Core predictors (never read held-out)
# ---------------------------------------------------------------------------

def emergence_stage(cap):
    """Earliest stage index where cap emerges; None if never."""
    _check_cap(cap)
    emerged = set()
    # process in dependency order within each stage via iterative pass
    for t in range(len(STAGES)):
        progressed = True
        while progressed:
            progressed = False
            for c in CAPABILITIES:
                if c in emerged:
                    continue
                if gate_satisfied(c, t, emerged):
                    emerged.add(c)
                    progressed = True
                    if c == cap:
                        return t
    return None


def predict_emergence_ordering():
    """Map capability -> earliest stage name (or None)."""
    out = {}
    for cap in CAPABILITIES:
        t = emergence_stage(cap)
        out[cap] = None if t is None else STAGES[t]
    return out


def ordered_emergence_sequence():
    """Capabilities sorted by emergence stage, then by catalogue order."""
    pairs = []
    for i, cap in enumerate(CAPABILITIES):
        t = emergence_stage(cap)
        pairs.append((t if t is not None else 10**9, i, cap, t))
    pairs.sort()
    return [(cap, None if t is None else STAGES[t]) for _, _, cap, t in pairs]


def prior_structure_dependencies():
    """Map capability -> {depends: bool, deps: tuple, structure_gates: dict}."""
    out = {}
    for cap in CAPABILITIES:
        min_R, min_S, min_skill, need_recode, need_law, need_morph, deps = GATES[cap]
        out[cap] = {
            "depends_on_accumulated_structure": depends_on_accumulated_structure(cap),
            "capability_deps": deps,
            "min_skill": min_skill,
            "need_recode": need_recode,
            "need_law": need_law,
            "need_morph": need_morph,
            "min_R": min_R,
            "min_S": min_S,
        }
    return out


def predict_compositional_abstraction_stage():
    """Stage name when compositional abstraction emerges, or None."""
    t = emergence_stage("cap-compositional-reasoning")
    return None if t is None else STAGES[t]


def social_inference_depth_at(stage):
    """Exact social inference depth (0..4) available at stage."""
    eco = ecology_at(stage)
    S = eco["S"]
    depth = 0
    for d in range(1, len(SOCIAL_DEPTH_S_THRESHOLDS)):
        if S < SOCIAL_DEPTH_S_THRESHOLDS[d]:
            break
        if d >= SOCIAL_DEPTH_NEEDS_COMPOSITION:
            # nested social inference requires compositional abstraction
            if emergence_stage("cap-compositional-reasoning") is None:
                break
            if emergence_stage("cap-compositional-reasoning") > stage_index(stage):
                break
        depth = d
    return depth


def predict_social_depth_trajectory():
    """List of (stage_name, depth) across development."""
    return [(STAGES[t], social_inference_depth_at(t)) for t in range(len(STAGES))]


def predict_sensitive_periods():
    """Dict of predicted sensitive periods under resource/ecology assumptions."""
    morph_win = sensitive_period_morph()
    return {
        "MORPH": {
            "window": morph_win,
            "cost": MORPH_COST,
            "V_lock": V_LOCK,
            "admissible_stages": [
                STAGES[i] for i in range(len(STAGES)) if morph_admissible(i)
            ],
            "rationale": (
                "MORPH admissible iff R>=MORPH_COST and V<V_LOCK; "
                "high verifier freezes morphology outside the window"
            ),
        }
    }


# ---------------------------------------------------------------------------
# Held-out comparison (formal registry; never used for fit)
# ---------------------------------------------------------------------------

def load_heldout_registry(path=None):
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "HELDOUT_DEVELOPMENTAL_REGISTRY_V1.json",
        )
    with open(path, "r", encoding="utf-8") as fh:
        reg = json.load(fh)
    if not isinstance(reg, dict) or reg.get("schema") != "HeldOutDevelopmentalRegistryV1":
        raise ValueError("bad held-out registry schema")
    if not reg.get("fit_forbidden"):
        raise ValueError("registry must declare fit_forbidden")
    return reg


def refuse_fit_record(record):
    """Raise if a proposed fit record smuggles held-out / identity fields."""
    if not isinstance(record, dict):
        raise ValueError("fit record must be a dict")
    bad = FORBIDDEN_FIT_FIELDS.intersection(record)
    if bad:
        raise ValueError("forbidden fit fields present: %s" % (sorted(bad),))
    return True


def compare_heldout(registry=None):
    """Score frozen predictions against held-out literature/dataset claims.

    Never feeds registry entries into gates or emergence. Returns exact
    per-entry match (1) / mismatch (0) / abstain (-1).
    """
    if registry is None:
        registry = load_heldout_registry()
    ordering = predict_emergence_ordering()
    composition_stage = predict_compositional_abstraction_stage()
    social_traj = dict(predict_social_depth_trajectory())
    sensitive = predict_sensitive_periods()

    results = []
    for entry in registry["entries"]:
        eid = entry["id"]
        ctype = entry["claim_type"]
        verdict = -1
        detail = ""

        if ctype == "ordering":
            earlier = entry["earlier"]
            later = entry["later"]
            te = ordering.get(earlier)
            tl = ordering.get(later)
            if te is None or tl is None:
                verdict = -1
                detail = "abstain: capability never emerges in finite schedule"
            else:
                verdict = 1 if STAGES.index(te) < STAGES.index(tl) else 0
                detail = "%s@%s vs %s@%s" % (earlier, te, later, tl)

        elif ctype == "composition_stage_at_or_after":
            min_stage = entry["min_stage"]
            if composition_stage is None:
                verdict = -1
                detail = "abstain: composition never emerges"
            else:
                verdict = (
                    1
                    if STAGES.index(composition_stage) >= STAGES.index(min_stage)
                    else 0
                )
                detail = "composition@%s vs min %s" % (composition_stage, min_stage)

        elif ctype == "social_depth_nondecreasing":
            depths = [social_traj[s] for s in STAGES]
            nondec = all(depths[i] <= depths[i + 1] for i in range(len(depths) - 1))
            increases = depths[-1] > depths[0]
            verdict = 1 if (nondec and increases) else 0
            detail = "depths=%s" % (depths,)

        elif ctype == "sensitive_period_exists":
            kind = entry.get("kind", "MORPH")
            win = sensitive.get(kind, {}).get("window")
            verdict = 1 if win is not None else 0
            detail = "window=%s" % (win,)

        elif ctype == "structure_dependence":
            cap = entry["capability"]
            expected = bool(entry["expected_depends"])
            actual = depends_on_accumulated_structure(cap)
            verdict = 1 if actual == expected else 0
            detail = "depends=%s expected=%s" % (actual, expected)

        else:
            raise ValueError("unknown held-out claim_type: %r" % (ctype,))

        results.append(
            {
                "id": eid,
                "claim_type": ctype,
                "verdict": verdict,
                "detail": detail,
                "source_split": entry.get("source_split", "held_out"),
            }
        )

    n_match = sum(1 for r in results if r["verdict"] == 1)
    n_mismatch = sum(1 for r in results if r["verdict"] == 0)
    n_abstain = sum(1 for r in results if r["verdict"] == -1)
    return {
        "results": results,
        "n_match": n_match,
        "n_mismatch": n_mismatch,
        "n_abstain": n_abstain,
        "n_entries": len(results),
    }


def summary():
    ordering = predict_emergence_ordering()
    return {
        "stages": list(STAGES),
        "capabilities": list(CAPABILITIES),
        "emergence_ordering": ordering,
        "ordered_sequence": ordered_emergence_sequence(),
        "prior_structure": {
            c: depends_on_accumulated_structure(c) for c in CAPABILITIES
        },
        "compositional_abstraction_stage": predict_compositional_abstraction_stage(),
        "social_depth_trajectory": predict_social_depth_trajectory(),
        "sensitive_periods": predict_sensitive_periods(),
        "heldout_comparison": compare_heldout(),
    }


def crosscheck_taxonomy_structure_kinds():
    """Optional exact cross-check vs taxonomy witness kinds if parent present.

    Returns True if parent module loads and the frozen STRUCTURE_AT_STAGE
    skill/recode/law/morph flags are consistent with a prefix of the
    taxonomy witness log kinds. Raises only on hard inconsistency when
    the parent is present.
    """
    tax_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "gmi-developmental-taxonomy-v1",
        "taxonomy_v1.py",
    )
    if not os.path.isfile(tax_path):
        return False
    import importlib.util

    spec = importlib.util.spec_from_file_location("tax_parent", tax_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    kinds = [label for (_a, _b, label) in mod.WITNESS_LOG]
    # expected kind multiset growth along our schedule checkpoints
    # toddler: INFO, RECODE
    # child: + SKILL
    # adolescent: + SKILL, LAW  (and an INFO from next round may interleave;
    # we only require cumulative kind counts, not order isomorphism)
    required_counts = [
        {"INFO": 0, "RECODE": 0, "SKILL": 0, "LAW": 0, "MORPH": 0},
        {"INFO": 1, "RECODE": 1, "SKILL": 0, "LAW": 0, "MORPH": 0},
        {"INFO": 1, "RECODE": 1, "SKILL": 1, "LAW": 0, "MORPH": 0},
        {"INFO": 1, "RECODE": 1, "SKILL": 2, "LAW": 1, "MORPH": 0},
        {"INFO": 1, "RECODE": 1, "SKILL": 3, "LAW": 1, "MORPH": 1},
    ]
    # verify taxonomy log can supply at least these cumulative counts
    from collections import Counter

    total = Counter(kinds)
    for req in required_counts:
        for k, v in req.items():
            if total[k] < v:
                raise AssertionError(
                    "taxonomy witness lacks kind %s count %d (have %d)"
                    % (k, v, total[k])
                )
    # verify our STRUCTURE_AT_STAGE skill/recode/law/morph match required
    for t, req in enumerate(required_counts):
        sk, recode, law, morph, _info = STRUCTURE_AT_STAGE[t]
        if sk != req["SKILL"]:
            raise AssertionError("skill_count mismatch at t=%d" % t)
        if recode != (1 if req["RECODE"] else 0):
            raise AssertionError("recode mismatch at t=%d" % t)
        if law != (1 if req["LAW"] else 0):
            raise AssertionError("law mismatch at t=%d" % t)
        if morph != (1 if req["MORPH"] else 0):
            raise AssertionError("morph mismatch at t=%d" % t)
    return True


if __name__ == "__main__":
    import pprint

    pprint.pprint(summary())
    print("taxonomy_crosscheck:", crosscheck_taxonomy_structure_kinds())
