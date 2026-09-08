"""Executable causal intake for the incidents of #149.

Issue #149 opens a self-evolution lane whose development incidents F1 to F6 are,
one for one, the findings of this lane.  It records that F1, F5 and F6 "still
lack executable causal intake", that "F2/F3 share a receipt, not independent
evidence", and it warns twice against manufacturing intake from prose:

    Summary-only observations cannot certify a causal localization.
    A prose claim about a cached parent is not a measured cached-parent trace.
    Recover and bind original traces; never fabricate them from summaries.

This module answers that warning in the only way it can be answered.  Every
number below is **read out of a receipt file at run time**, never typed here, and
every receipt is bound by the sha256 of its bytes.  If a receipt changes, the
digest changes and the binding is stale; if a receipt is missing, the incident is
reported as unsupplied rather than described.

What this module deliberately does NOT do is claim that supplying a trace
certifies a causal localization.  It supplies the measurement; the diagnosis
remains open.  Three incidents carry qualifications strong enough that a
consumer relying on them without reading the qualification would be misled, and
those are carried in ``does_not_certify``.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).parent
RESULTS = HERE / "results"

#: The incident table of #149, quoted rather than paraphrased.
INCIDENTS = {
    "F1": ("Unary acquisition funnel and original checked traces", "No reusable methods"),
    "F2": ("Relevance-key growth and collision traces", "Fixed keys become dense"),
    "F3": ("Feature search, rebuild and query work", "Index maintenance fails to amortize"),
    "F4": ("Dependency interventions and revision traces", "Redundant supports missed"),
    "F5": ("Probe choices and matched cached-parent results",
           "Apparent diagnosis residual disappears"),
    "F6": ("Per-instance escalation contracts and oracle comparisons",
           "Authored labels disagree with independent checking"),
}


def _digest(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict | None:
    p = RESULTS / name
    if not p.is_file():
        return None
    return json.loads(p.read_text())


def _f2_f3() -> tuple[dict, dict]:
    """Relevance-key collision growth, and whether its repair amortises.

    These are two questions of one run and #149 is right that they are not two
    independent observations.  They are separable in principle -- collision
    growth is a property of the key, amortisation is a property of the search
    procedure that repairs it -- but nothing here separates them empirically,
    and the shared-receipt flag says so.
    """
    d = _load("SUBSPACE_E1_V1.json")
    if d is None:
        return ({"status": "RECEIPT_MISSING"}, {"status": "RECEIPT_MISSING"})
    rows = d["feature_report"].get("signature_hash_parent", [])
    growth = [
        {"scale": r["scale"], "methods": r["n_methods"], "max_bucket": r["max_bucket"],
         "collision_rate": r["collision_rate"], "adequate": r["adequate"]}
        for r in rows
    ]
    f2 = {
        "status": "EXECUTABLE_INTAKE_SUPPLIED",
        "measurement": "collision growth of a hand-specified relevance key as the store grows",
        "hand_specified_key_adequate_at": d.get("hand_specified_feature_adequate_at"),
        "hand_specified_key_inadequate_at": d.get("hand_specified_feature_inadequate_at"),
        "per_scale": growth,
        "does_not_certify": (
            "Correctness never degraded at any scale: a colliding key is slower and never wrong. "
            "So this is a cost observation, not a capability failure, and it cannot localize a "
            "capability fault."),
    }
    cross = d.get("crossover_queries_vs_exact_scan", {}).get("discovering_arm", {})
    f3 = {
        "status": "EXECUTABLE_INTAKE_SUPPLIED_WITH_SHARED_RECEIPT",
        "measurement": "whether repairing the key by re-indexing repays its own cost",
        "terminal": d.get("terminal"),
        "per_scale_crossover": cross,
        "shared_receipt_with": "F2",
        "shared_receipt_note": (
            "#149 is correct that F2 and F3 come from one receipt and are not two independent "
            "observations. They are separable in principle -- collision growth is a property of "
            "the key, amortisation a property of the repair procedure -- but no run here "
            "separates them."),
        "does_not_certify": (
            "The receipt's own limitation applies: the amortisation reading is specific to a "
            "search that rescans the whole feature language on every re-index, with no early "
            "exit. An incremental search was not run and would cost materially less. Treating "
            "INDEX_MAINTENANCE_DOMINATES as a property of re-indexing in general would "
            "overreach."),
    }
    return f2, f3


def _f4() -> dict:
    d = _load("DEPEND_E3_V1.json")
    if d is None:
        return {"status": "RECEIPT_MISSING"}
    audit = [
        {"scale": a["scale"], "N": a["N_persistent_objects"], "methods": a["methods"],
         "methods_with_support_invisible_to_leave_one_out":
             a["methods_with_support_invisible_to_leave_one_out"],
         "fraction_invisible": a["fraction_invisible"]}
        for a in d.get("ground_truth_audit", [])
    ]
    return {
        "status": "EXECUTABLE_INTAKE_SUPPLIED",
        "measurement": "fraction of methods whose support no single-element ablation can see",
        "terminal": d.get("terminal"),
        "per_scale": audit,
        "capability_gated_reanalysis": (
            "Restricting the work comparison to arms at precision and recall 1.0, as the "
            "publication constitution requires, leaves three arms. Under that gate the eager "
            "learned-dependency arm is dominated by the lazy learner that re-derives on demand, "
            "on both work and stale survivors. So the incident is not only that redundant "
            "supports are missed; it is that eager discovery is not yet worth its cost."),
        "does_not_certify": (
            "The learned arm's perfect precision and recall are arithmetic, not evidence: it runs "
            "the oracle's own leave-one-out procedure. The number measures how often redundancy "
            "occurs in this evidence stream, which is a property of the world, not a constant."),
    }


def _f5() -> dict:
    """The incident #149 records as lacking executable intake. It does not.

    #149 warns that "a prose claim about a cached parent is not a measured
    cached-parent trace". The cached parent here was measured, not asserted: the
    receipt carries the full per-arm cost table and the cumulative curve.
    """
    d = _load("DIAGNOSIS_E2_V1.json")
    if d is None:
        return {"status": "RECEIPT_MISSING"}
    base = d.get("constant_predictor_baseline", {})
    return {
        "status": "EXECUTABLE_INTAKE_SUPPLIED",
        "supersedes_149_note": (
            "#149 lists F5 as lacking executable causal intake. This receipt supplies it: the "
            "cached-parent comparison is a measured trace with a per-arm cost table, not a prose "
            "claim."),
        "measurement": "diagnosis accuracy and cumulative probe cost with the failure cause hidden",
        "terminal": d.get("terminal"),
        "episodes": base.get("episodes"),
        "cause_distribution": base.get("target_counts"),
        "constant_predictor_baseline_accuracy": base.get("best_constant_accuracy"),
        "does_not_certify": (
            "The residual is memoisation of one boolean per checker and scope, and the receipt "
            "states that giving the decision-tree parent the same cache would close it. Probe "
            "semantics are authored, so this is table inversion under a cost constraint and not "
            "evidence that a machine can learn what a probe means."),
    }


def _f6() -> dict:
    d = _load("ESCALATION_INDEPENDENT_E4_V1.json")
    if d is None:
        return {"status": "RECEIPT_MISSING"}
    v = d.get("generator_artifact_verdict", {})
    head = d.get("headline_contrast", {})
    return {
        "status": "EXECUTABLE_INTAKE_SUPPLIED",
        "supersedes_149_note": (
            "#149 lists F6 as lacking executable causal intake. This receipt supplies it, and its "
            "oracle is cross-checked against brute-force minimisation over the full repair "
            "powerset rather than against another authored label."),
        "measurement": "agreement between authored per-instance labels and an independent oracle",
        "verdict": v.get("verdict"),
        "authored_label_accuracy": v.get("old_generator_accuracy"),
        "independent_accuracy": v.get("independent_accuracy"),
        "accuracy_drop": v.get("accuracy_drop"),
        "registered_tolerance": v.get("registered_tolerance"),
        "lead_collapse": head.get("lead_collapse"),
        "does_not_certify": (
            "Removing the generator's circularity does not remove the ladder's authorship: the "
            "repair lattice and the escalation levels still share an author, so this remains E2. "
            "It also does not show that the escalation policy is good; on independent worlds the "
            "fully-resourced parent ties it."),
    }


def _f1() -> dict:
    """Not this lane's to supply, and the honest answer is to say so."""
    return {
        "status": "NOT_SUPPLIED_BY_THIS_LANE",
        "measurement": "acquisition funnel showing checked sound fragments that never became methods",
        "where_it_lives": [
            "research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md (the funnel table: "
            "21 attempts, three independently checked essential fragments, all singletons)",
            "research/math-language-learning-v1/CLAUSE-REVIVAL-RESULT.md (the clause donor, which "
            "acquires a method and still records NO_DEVELOPMENT_BENEFIT because every eligible "
            "development target is a Boolean tautology)",
        ],
        "why_not_supplied": (
            "This lane planned an experiment to reproduce and extend F1 in a self-contained clause "
            "world; it was cancelled before producing a receipt. Nothing here should be read as "
            "intake for F1."),
        "what_the_clause_revival_changes": (
            "It moves the bottleneck. Step-level abstraction does fix the discovery failure -- the "
            "pool goes from zero to one. The method then fires zero times because the task ecology "
            "contains no essential composite target. Any successor experiment must therefore "
            "control opportunity separately from discovery, and must include a tautological-ecology "
            "control on which a correctly discovered method is expected to show no benefit."),
    }


def build() -> dict:
    f2, f3 = _f2_f3()
    bindings = {"F1": _f1(), "F2": f2, "F3": f3, "F4": _f4(), "F5": _f5(), "F6": _f6()}
    sources = {
        "F2": "SUBSPACE_E1_V1.json", "F3": "SUBSPACE_E1_V1.json",
        "F4": "DEPEND_E3_V1.json", "F5": "DIAGNOSIS_E2_V1.json",
        "F6": "ESCALATION_INDEPENDENT_E4_V1.json",
    }
    reproduce = {
        "F2": "python run_subspace.py --out results/SUBSPACE_E1_V1.json",
        "F3": "python run_subspace.py --out results/SUBSPACE_E1_V1.json",
        "F4": "python run_depend.py --out results/DEPEND_E3_V1.json",
        "F5": "python run_diagnosis.py --out results/DIAGNOSIS_E2_V1.json",
        "F6": "python run_escalation_independent.py "
              "--out results/ESCALATION_INDEPENDENT_E4_V1.json",
    }
    for fid, b in bindings.items():
        name = sources.get(fid)
        b["incident_description"] = INCIDENTS[fid][0]
        b["diagnostic_challenge"] = INCIDENTS[fid][1]
        if name:
            b["receipt"] = f"research/cognitive-ladder/results/{name}"
            b["receipt_sha256"] = _digest(RESULTS / name)
            b["reproduce"] = reproduce[fid]
    supplied = sum(1 for b in bindings.values()
                   if str(b["status"]).startswith("EXECUTABLE_INTAKE_SUPPLIED"))
    return {
        "schema": "orion.incident-intake.v1",
        "consumer_issue": "SzeChunYiu/ORION-OCM#149",
        "producer_lane": "research/cognitive-ladder",
        "authority": (
            "This binds measured traces to the incidents of #149. Supplying a trace does not "
            "certify a causal localization, and every binding carries what it does not certify. "
            "Numbers are read from receipts at run time and are never transcribed here."),
        "incidents_supplied": supplied,
        "incidents_total": len(bindings),
        "bindings": bindings,
    }


def main() -> int:
    doc = build()
    (HERE / "INCIDENT_INTAKE_V1.json").write_text(json.dumps(doc, indent=2) + "\n")
    lines = [
        "# INCIDENT_INTAKE_V1\n",
        "**GENERATED FILE — edit `incident_intake.py`, then run `python incident_intake.py`.**\n",
        "Executable causal intake for the six development incidents of "
        "[#149](https://github.com/SzeChunYiu/ORION-OCM/issues/149), whose incident table is one "
        "for one the findings of this lane.\n",
        "#149 warns that summary-only observations cannot certify a causal localization, that a "
        "prose claim about a cached parent is not a measured cached-parent trace, and that traces "
        "must never be fabricated from summaries. Every number below is read out of a receipt at "
        "run time and each receipt is bound by the sha256 of its bytes. Supplying a trace is not "
        "the same as certifying a diagnosis, so each binding carries a `does_not_certify` note.\n",
        f"**{doc['incidents_supplied']} of {doc['incidents_total']} incidents have executable "
        "intake in this lane.**\n",
        "| incident | challenge | status | receipt |", "|---|---|---|---|",
    ]
    for fid, b in doc["bindings"].items():
        lines.append(f"| **{fid}** | {b['diagnostic_challenge']} | {b['status']} | "
                     f"{'`' + b['receipt'].split('/')[-1] + '`' if b.get('receipt') else '—'} |")
    lines.append("")
    for fid, b in doc["bindings"].items():
        lines.append(f"## {fid} — {b['incident_description']}\n")
        lines.append(f"**Challenge (#149).** {b['diagnostic_challenge']}\n")
        lines.append(f"**Status.** `{b['status']}`\n")
        if b.get("supersedes_149_note"):
            lines.append(f"**Correction to #149.** {b['supersedes_149_note']}\n")
        if b.get("receipt"):
            lines.append(f"**Receipt.** `{b['receipt']}`  \n"
                         f"**sha256.** `{b['receipt_sha256']}`  \n"
                         f"**Reproduce.** `{b['reproduce']}`\n")
        if b.get("shared_receipt_note"):
            lines.append(f"**Shared receipt.** {b['shared_receipt_note']}\n")
        if b.get("why_not_supplied"):
            lines.append(f"**Why not supplied.** {b['why_not_supplied']}\n")
        if b.get("where_it_lives"):
            lines.append("**Where the trace lives.**\n")
            for w in b["where_it_lives"]:
                lines.append(f"- {w}")
            lines.append("")
        if b.get("what_the_clause_revival_changes"):
            lines.append(f"**What the clause revival changes.** "
                         f"{b['what_the_clause_revival_changes']}\n")
        if b.get("capability_gated_reanalysis"):
            lines.append(f"**Capability-gated re-analysis.** {b['capability_gated_reanalysis']}\n")
        if b.get("does_not_certify"):
            lines.append(f"**Does not certify.** {b['does_not_certify']}\n")
    (HERE / "INCIDENT_INTAKE_V1.md").write_text("\n".join(lines))
    print(f"wrote INCIDENT_INTAKE_V1.json and .md: "
          f"{doc['incidents_supplied']}/{doc['incidents_total']} incidents with executable intake")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
