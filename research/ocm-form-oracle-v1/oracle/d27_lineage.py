"""D27 — continued-vs-reset causal development (#277 sec 7 + #233 D27).

The decisive test is a KNOCKOUT, not a correlated pre/post comparison: delete
the exact inherited object claimed to cause the gain, hold everything else
fixed, and require the advantage to weaken or disappear.

The frozen T2 evaluator already carries the continued/reset contrast
(lifetime2.run_lifetime2(org, reset=...)), and it accumulates exactly four
inheritable objects across epochs:

    methods       reusable solved-case methods      (Sim.methods)
    schemas       abstraction schemas               (Sim.schemas)
    facts         admitted persistent facts         (Sim.facts)
    index_built   the built exact-retrieval index   (Sim.index_built)

RESET wipes all four at every epoch boundary.  A KNOCKOUT wipes exactly ONE and
leaves the other three inheriting, so an advantage attributed to (say) methods
must survive the schema knockout and must NOT survive the method knockout.
That is a single-object causal claim, and it is what reaches C=3.

The evaluator is NOT forked.  The knockout is installed by patching
Sim.end_epoch for the duration of one run: the original runs first (so the
epoch's recorded work and bytes are unchanged), then the named field is zeroed
so it cannot be inherited into the next epoch -- exactly parallel to how RESET
wipes at the start of the next epoch.

B_future_cognition
------------------
The signature that matters is not a higher score.  It is

    B_future_cognition(t+1) < B_future_cognition(t)

on PROSPECTIVELY FROZEN related tasks (FOF1) at matched capability, WITHOUT
equivalent gains on unrelated (CTRLU) or harmful (CTRLH) controls.  Here t
indexes developmental epochs: B_future_cognition(t) is the work the frozen
future-family battery charges when the organism enters it carrying exactly the
store it held at the end of epoch t.  Epoch-wise stores are snapshotted by the
same end_epoch patch, so no separate accounting path can disagree with the run.

SCOPE DEVIATION, recorded: #277 sec 7 names STRONG_ADAPTIVE_NEURAL_PARENT.  No
learned neural parent exists in this stack -- the closest legal form is the
approximate / VSA family (approx_projection_vsa, assoc_similarity), which is
adaptive and approximate but not learned.  It is therefore run and reported as
STRONG_ADAPTIVE_APPROXIMATE_PARENT.  Calling it neural would be fabrication.
"""
from __future__ import annotations

import contextlib
from typing import Any, Dict, List, Optional, Tuple

INHERITED_OBJECTS: Tuple[str, ...] = ("methods", "schemas", "facts",
                                      "index_built")

ARMS: Tuple[str, ...] = (
    "CONTINUED_OCM",
    "RESET_OCM",
    "KNOCKOUT_methods",
    "KNOCKOUT_schemas",
    "KNOCKOUT_facts",
    "KNOCKOUT_index_built",
)

PARENT_ARMS: Tuple[str, ...] = (
    "TASK_SPECIFIC_OCM",
    "STRONG_PERSISTENT_NON_NEURAL_PARENT",
    "STRONG_ADAPTIVE_APPROXIMATE_PARENT",
)

_ZERO = {"methods": 0, "schemas": 0, "facts": 0, "index_built": False}


@contextlib.contextmanager
def _knockout(fields: Tuple[str, ...], snapshots: Optional[List] = None):
    """Patch Sim.end_epoch: original first, then wipe `fields`.

    Always restored, including on exception.  `snapshots`, if given, collects
    the per-epoch inheritable store BEFORE the wipe.
    """
    from evaluation.lifetime import Sim
    original = Sim.end_epoch

    def patched(self):  # noqa: ANN001
        original(self)
        if snapshots is not None:
            snapshots.append({k: getattr(self, k) for k in INHERITED_OBJECTS})
        for f in fields:
            setattr(self, f, _ZERO[f])

    Sim.end_epoch = patched
    try:
        yield
    finally:
        Sim.end_epoch = original


def run_arm(genome: Any, arm: str) -> Dict[str, Any]:
    """One D27 arm on the frozen T2 developmental battery."""
    from evaluation.lifetime2 import run_lifetime2
    from morphology.compile import compile_genome
    from evaluation.invariants import hard_gate_report

    org = compile_genome(genome)
    snaps: List[Dict[str, Any]] = []
    if arm == "RESET_OCM":
        with _knockout((), snaps):
            ev = run_lifetime2(org, reset=True)
    elif arm == "CONTINUED_OCM":
        with _knockout((), snaps):
            ev = run_lifetime2(org, reset=False)
    elif arm.startswith("KNOCKOUT_"):
        f = arm[len("KNOCKOUT_"):]
        if f not in INHERITED_OBJECTS:
            return {"arm": arm, "status": "CANNOT_CHECK_UNKNOWN_OBJECT"}
        with _knockout((f,), snaps):
            ev = run_lifetime2(org, reset=False)
    else:
        return {"arm": arm, "status": "CANNOT_CHECK_UNKNOWN_ARM"}

    from oracle.burden import b_own, burden_components
    gates = hard_gate_report(org, ev)
    return {
        "arm": arm,
        "status": "OK",
        "genotype_digest": org.genotype_digest,
        "phenotype_digest": org.phenotype_digest,
        "feasible": bool(gates["feasible"]),
        "capability": float(ev.get("solved_fraction", 0.0)),
        "B_exec": float(ev.get("reasoning_work", 0.0)),
        "B_own": b_own(ev),
        "components": burden_components(ev),
        "work_total": float(ev.get("work_total", 0.0)),
        "active_kN": ev.get("active_kN"),
        "verification_calls": float(ev.get("verification_work", 0.0)),
        "harmful_transfers": int(ev.get("harmful_transfers", 0)),
        "stale_answers": int(ev.get("stale_answers", 0)),
        "epoch_capabilities": ev.get("epoch_capabilities", []),
        "epoch_work": ev.get("epoch_work", []),
        "inherited_store_by_epoch": snaps,
        "per_family": ev.get("per_family", {}),
    }


def first_useful_epoch(rec: Dict[str, Any]) -> Optional[int]:
    """Hitting time: first epoch with a solved task. None if never."""
    for i, c in enumerate(rec.get("epoch_capabilities", []) or []):
        if c and c > 0:
            return i
    return None


# ------------------------------------------------------------ B_future_cognition

@contextlib.contextmanager
def _seeded_sim(store: Dict[str, Any]):
    """Make t3_ecology build its Sim pre-loaded with an inherited store.

    Patches the name t3_ecology.Sim only; the evaluator body is untouched, so
    charging and gates stay exactly the frozen ones.
    """
    from evaluation import t3_ecology as t3
    original = t3.Sim

    class Seeded(original):  # type: ignore[misc,valid-type]
        def __init__(self, org):  # noqa: ANN001
            super().__init__(org)
            for k in INHERITED_OBJECTS:
                if k in store:
                    setattr(self, k, store[k])

    t3.Sim = Seeded
    try:
        yield
    finally:
        t3.Sim = original


def b_future_cognition(genome: Any, store: Dict[str, Any],
                       key: str) -> Dict[str, Any]:
    """Work the frozen future battery charges to an organism entering it with
    exactly `store` inherited."""
    from evaluation.t3_ecology import run_t3
    from morphology.compile import compile_genome
    from oracle.burden import b_own, b_work_only
    org = compile_genome(genome)
    with _seeded_sim(store):
        ev = run_t3(org, key)
    return {
        # WORK charged on the future family. Byte rent excluded by design --
        # see burden.b_work_only for why including it makes the signature
        # unfalsifiable in one direction. Both figures are reported.
        "B_future_cognition": b_work_only(ev),
        "B_future_cognition_incl_bytes": b_own(ev),
        "work_total": float(ev.get("work_total", 0.0)),
        "capability": float(ev.get("solved_fraction", 0.0)),
        "harmful_transfers": int(ev.get("harmful_transfers", 0)),
        "store": dict(store),
    }


def future_cognition_curve(genome: Any, continued: Dict[str, Any],
                           key: str) -> Dict[str, Any]:
    """B_future_cognition(t) across the developmental epochs of one CONTINUED run."""
    snaps = continued.get("inherited_store_by_epoch") or []
    if not snaps:
        return {"status": "CANNOT_CHECK_NO_EPOCH_SNAPSHOTS"}
    # If the inherited store never changes across development there is nothing
    # for B_future_cognition to vary with, so a flat curve here would be a
    # property of the sampling, not evidence against the hypothesis. That is a
    # CANNOT_CHECK, not a negative: the frozen future battery does consult
    # methods / schemas / facts / index_built (t3_ecology lines 146, 158, 183,
    # 201), so the mechanism exists and only this organism fails to exercise it.
    distinct = {tuple(sorted(st.items())) for st in snaps}
    if len(distinct) < 2:
        return {"status": "CANNOT_CHECK_STORE_CONSTANT_ACROSS_EPOCHS",
                "n_epochs": len(snaps), "store": snaps[0] if snaps else None}
    curve = []
    for t, store in enumerate(snaps):
        r = b_future_cognition(genome, store, key)
        r["t"] = t
        curve.append(r)
    b = [c["B_future_cognition"] for c in curve]
    b_bytes = [c["B_future_cognition_incl_bytes"] for c in curve]
    caps = [c["capability"] for c in curve]
    # The signature: burden on frozen future tasks FALLS with development,
    # while capability does not fall (matched-or-better capability).
    decreasing = all(b[i + 1] <= b[i] + 1e-9 for i in range(len(b) - 1))
    strictly = len(b) > 1 and b[-1] < b[0] - 1e-9
    cap_not_worse = len(caps) > 1 and caps[-1] >= caps[0] - 1e-9
    return {
        "status": "OK", "key": key, "curve": curve,
        "b_first": b[0], "b_last": b[-1],
        "b_incl_bytes_first": b_bytes[0], "b_incl_bytes_last": b_bytes[-1],
        "cap_first": caps[0], "cap_last": caps[-1],
        "monotone_non_increasing": decreasing,
        "strictly_decreased": strictly,
        "capability_not_worse": cap_not_worse,
        "signature_present": bool(strictly and cap_not_worse),
    }


def signature_with_controls(genome: Any, continued: Dict[str, Any]) -> Dict[str, Any]:
    """The full signature test: related family must improve, controls must not.

    A gain that shows up equally on the unrelated control is not developmental
    amortisation, it is a general speed-up, and it is reported as such.
    """
    from oracle.future_family import FOF1_KEY, CTRLU_KEY, CTRLH_KEY
    rel = future_cognition_curve(genome, continued, FOF1_KEY)
    if rel.get("status") != "OK":
        # Do not spend the two control batteries on an organism whose related
        # curve could not be computed.
        return {"status": rel.get("status", "CANNOT_CHECK"), "related": rel}
    unr = future_cognition_curve(genome, continued, CTRLU_KEY)
    hrm = future_cognition_curve(genome, continued, CTRLH_KEY)

    def _drop(c):
        if c.get("status") != "OK" or not c.get("b_first"):
            return None
        return (c["b_first"] - c["b_last"]) / c["b_first"]

    d_rel, d_unr, d_hrm = _drop(rel), _drop(unr), _drop(hrm)
    equivalent_on_unrelated = (
        d_rel is not None and d_unr is not None
        and d_unr >= 0.5 * d_rel and d_rel > 0)
    return {
        "status": "OK",
        "related": rel, "unrelated_control": unr, "harmful_control": hrm,
        "relative_drop_related": (round(d_rel, 6) if d_rel is not None else None),
        "relative_drop_unrelated": (round(d_unr, 6) if d_unr is not None else None),
        "relative_drop_harmful": (round(d_hrm, 6) if d_hrm is not None else None),
        "harmful_transfers_on_harmful_control": sum(
            c.get("harmful_transfers", 0) for c in (hrm.get("curve") or [])),
        "equivalent_gain_on_unrelated_control": equivalent_on_unrelated,
        # The directive's signature, stated exactly: related improves, controls
        # do not gain equivalently.
        "B_FUTURE_COGNITION_SIGNATURE": bool(
            rel.get("signature_present") and not equivalent_on_unrelated),
    }


def knockout_attribution(by_arm: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Attribute the continued-over-reset advantage to ONE inherited object.

    advantage      = CONTINUED - RESET            (on the metric of interest)
    residual(obj)  = KNOCKOUT_obj - RESET
    attribution(obj) = 1 - residual(obj)/advantage
      ~1  removing obj removes the advantage  -> obj carries it
      ~0  removing obj changes nothing        -> obj does not carry it

    A knockout that does not weaken the advantage FALSIFIES attribution to that
    object.  Nothing here is rescued by re-attribution after the fact: every
    object is tested and every result is reported.
    """
    def _get(arm, field):
        r = by_arm.get(arm)
        if not r or r.get("status") != "OK":
            return None
        v = r.get(field)
        return float(v) if isinstance(v, (int, float)) else None

    out: Dict[str, Any] = {"metrics": {}}
    for field, sense in (("capability", "higher_better"),
                         ("B_exec", "lower_better"),
                         ("B_own", "lower_better")):
        cont = _get("CONTINUED_OCM", field)
        rst = _get("RESET_OCM", field)
        if cont is None or rst is None:
            out["metrics"][field] = {"status": "CANNOT_CHECK_MISSING_ARM"}
            continue
        adv = (cont - rst) if sense == "higher_better" else (rst - cont)
        per_obj = {}
        for obj in INHERITED_OBJECTS:
            ko = _get("KNOCKOUT_%s" % obj, field)
            if ko is None:
                per_obj[obj] = {"status": "CANNOT_CHECK_MISSING_ARM"}
                continue
            resid = (ko - rst) if sense == "higher_better" else (rst - ko)
            attrib = (None if abs(adv) < 1e-12
                      else round(1.0 - (resid / adv), 6))
            per_obj[obj] = {
                "status": "OK",
                "knockout_value": round(ko, 6),
                "residual_advantage": round(resid, 6),
                "attribution": attrib,
                "weakens_advantage": (attrib is not None and attrib > 0.0),
            }
        ranked = sorted(
            [(o, d["attribution"]) for o, d in per_obj.items()
             if d.get("status") == "OK" and d.get("attribution") is not None],
            key=lambda kv: -kv[1])
        out["metrics"][field] = {
            "status": "OK", "sense": sense,
            "continued": round(cont, 6), "reset": round(rst, 6),
            "advantage_continued_over_reset": round(adv, 6),
            "advantage_present": adv > 1e-12,
            "per_object": per_obj,
            "ranked_attribution": ranked,
            # A carrier is only meaningful when there IS an advantage to carry.
            # Naming one where CONTINUED is no better than RESET would attribute
            # a gain that does not exist.
            "carrier": (ranked[0][0]
                        if (adv > 1e-12 and ranked and ranked[0][1] > 0.5)
                        else None),
            "carrier_status": ("OK" if adv > 1e-12
                               else "NO_ADVANTAGE_TO_ATTRIBUTE"),
        }
    return out
