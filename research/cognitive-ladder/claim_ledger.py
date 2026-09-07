"""PUB-D1: the top-tier claim ledger.

Publication constitution #144 §21 asks for a ledger of the form
``Claim -> level -> hypothesis -> parent -> experiment -> replication -> result
-> limitation -> permitted wording``.

The last column is the one that does the work.  Every other column records what
happened; ``permitted_wording`` records what may therefore be *said*, and
``forbidden_wording`` records the sentence that the evidence does not support but
that would be tempting to write.  A programme does not usually fail by faking
data.  It fails by describing a real result in prose one level stronger than the
evidence, and that is a failure mode a table can catch.

The ledger is generated.  Edit this module and re-run it; do not edit the output.
"""

from __future__ import annotations

import json
import pathlib

LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")
EVIDENCE = ("E0", "E1", "E2", "E3", "E4", "E5")

CLAIMS = [
{
 "claim_id": "C1-SPARSE-LOOKUP",
 "claim": "Task-relevant computation touches a small fraction of a growing store.",
 "level": "L0", "evidence": "E1",
 "hypothesis": "k stays small while N grows, at matched answer correctness.",
 "strongest_parent": "an ordinary database index keyed on the supplied family identity",
 "experiment": "research/cognitive-ladder/run_scaling.py, scales 1x/3x/10x/30x",
 "replication": "none",
 "result": "PARENT_SUFFICIENT. The index parent matches the machine arm exactly on k, k/N, "
           "query work and answered-correctly at every scale. The machine arm's persistent bytes "
           "are strictly larger, because its reverse-index edges are charged.",
 "limitation": "The index key was supplied by the catalogue, so cheap lookup is a property of the "
               "key. Sparse execution on the real runtime is untested; its navigation still "
               "computes dense fixed points.",
 "permitted_wording": "An ordinary index reproduces the sparse-query behaviour exactly, so sparse "
                      "lookup under a supplied relevance key is not evidence of cognition.",
 "forbidden_wording": "The machine queries only a tiny fraction of its knowledge.",
},
{
 "claim_id": "C2-EXACT-REVOCATION",
 "claim": "Withdrawing a support invalidates exactly the objects that depended on it.",
 "level": "L0", "evidence": "E1",
 "hypothesis": "The observed cone equals the true cone; local revocation stays local while a "
               "genuinely global one does not.",
 "strongest_parent": "a truth-maintenance store, or an O(N) scan over declared supports",
 "experiment": "run_scaling.py revocation arms; local and globally-shared triggers",
 "replication": "none",
 "result": "The machine arm's cone is exact at every scale; local stays at 2 while the shared "
           "cone grows with N. Every arm without dependency edges observes the empty cone.",
 "limitation": "The dependency graph was built from the declarations that populated the store, so "
               "exactness is by construction. The gap over the index parent is a difference in "
               "default configuration, not achievability: an audited O(N) support scan recovers "
               "both cones and was not run. Protocol attack A9 is unanswered.",
 "permitted_wording": "Given a declared dependency graph, revocation is exact and its cost tracks "
                      "the true cone rather than the store size.",
 "forbidden_wording": "The machine discovers what its conclusions depend on.",
},
{
 "claim_id": "C3-SCOPED-FAILURE",
 "claim": "Negative knowledge is scoped to assumptions, so it transfers and reopens correctly.",
 "level": "L1", "evidence": "E2",
 "hypothesis": "Exclusions keyed on the assumption set avoid repeated dead ends without closing "
               "permanently shut.",
 "strongest_parent": "a full-strength nogood store with assumption-set keying and "
                     "dependency-directed retraction",
 "experiment": "run_failure.py, seven worlds including five hostiles",
 "replication": "none",
 "result": "The governed store avoids all 640 avoidable work units with zero false exclusions, "
           "zero missed reopenings and zero broken-shut. The nogood parent avoids the same 640 "
           "and ties exactly on four of seven worlds, separating only by four false exclusions on "
           "the three worlds where the failure's cause carries no information about correctness.",
 "limitation": "Every arm was handed the correct cause by the world. Whether a machine can tell an "
               "evaluator defect from a genuine refutation is untested here; that is experiment E2.",
 "permitted_wording": "Filtering exclusions by the cause of a failure avoids false exclusions that "
                      "a cause-blind nogood store makes, on worlds where the cause is known.",
 "forbidden_wording": "The machine learns from failure better than truth maintenance does.",
},
{
 "claim_id": "C4-MINIMUM-ESCALATION",
 "claim": "The machine escalates to the minimum sufficient level and refuses to escalate on "
          "exhaustion.",
 "level": "L1", "evidence": "E2",
 "hypothesis": "Requiring an exhibited obstruction witness yields minimum-level accuracy with zero "
               "false escalations.",
 "strongest_parent": "an exact repair planner taking the cheapest repair that admits a fit; and, "
                     "historically, a fully-resourced verified-regime-revision parent",
 "experiment": "run_escalation.py, nine registered worlds plus a commitment-derived draw",
 "replication": "none",
 "result": "Calibration only. The governed policy separates from three naive parents and from the "
           "repair planner on the worlds where the evidence channel rather than the representation "
           "is binding.",
 "limitation": "The world generator instantiates the defect the policy is built to detect, which "
               "is the failure-ledger pattern STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE. The "
               "binary jump decision is separately closed against a fully-resourced parent with a "
               "protected incremental gap of exactly zero.",
 "permitted_wording": "On worlds constructed to carry a known defect, a witness requirement "
                      "prevents the false escalations that timeout and saturation policies make.",
 "forbidden_wording": "The machine reliably diagnoses when its representation is insufficient.",
},
{
 "claim_id": "C5-RELEVANCE-DISCOVERY",
 "claim": "The machine discovers which part of memory is relevant without being told.",
 "level": "pending", "evidence": "pending",
 "hypothesis": "A discovered indexing feature keeps k small at matched correctness, and its "
               "adequacy degrades with N unless revised.",
 "strongest_parent": "a content-addressed inverted index on a hand-specified prediction prefix; "
                     "nearest-neighbour retrieval",
 "experiment": "E1, run_subspace.py",
 "replication": "none",
 "result": "pending",
 "limitation": "pending",
 "permitted_wording": "pending",
 "forbidden_wording": "The machine knows what is relevant.",
},
{
 "claim_id": "C6-CAUSE-DIAGNOSIS",
 "claim": "The machine infers why an attempt failed, from probes it chooses and pays for.",
 "level": "pending", "evidence": "pending",
 "hypothesis": "Diagnosis accuracy at lower cumulative probe cost than a stateless policy, because "
               "a diagnosis once made is not re-paid within its scope.",
 "strongest_parent": "a fixed near-optimal decision tree over the same probes; exhaustive probing",
 "experiment": "E2, run_diagnosis.py",
 "replication": "none",
 "result": "pending",
 "limitation": "pending",
 "permitted_wording": "pending",
 "forbidden_wording": "The machine understands its own failures.",
},
{
 "claim_id": "C7-DEPENDENCY-DISCOVERY",
 "claim": "The machine discovers which evidence its conclusions actually rest on.",
 "level": "pending", "evidence": "pending",
 "hypothesis": "A learned dependency graph reaches high precision and recall against a "
               "leave-one-out oracle, and its up-front discovery cost is repaid after a measurable "
               "number of revocations.",
 "strongest_parent": "full recomputation; a co-occurrence heuristic; the gifted declared-supports "
                     "ceiling",
 "experiment": "E3, run_depend.py",
 "replication": "none",
 "result": "pending",
 "limitation": "Leave-one-out cannot see redundant support, which is a limitation of the discovery "
               "method and not of the measurement.",
 "permitted_wording": "pending",
 "forbidden_wording": "The machine knows what it believes and why.",
},
{
 "claim_id": "C8-ESCALATION-INDEPENDENT",
 "claim": "Minimum-sufficient escalation holds on worlds not built around the policy's taxonomy.",
 "level": "pending", "evidence": "pending",
 "hypothesis": "Accuracy survives blind perturbation with ground truth from exhaustive repair "
               "search rather than generator intent.",
 "strongest_parent": "the exact repair planner",
 "experiment": "E4, run_escalation_independent.py",
 "replication": "this IS the replication that C4 lacks",
 "result": "pending",
 "limitation": "pending",
 "permitted_wording": "pending",
 "forbidden_wording": "The machine's escalation policy generalises.",
},
]


def main() -> int:
    here = pathlib.Path(__file__).parent
    for c in CLAIMS:
        assert c["level"] in LEVELS or c["level"] == "pending", c["claim_id"]
        assert c["evidence"] in EVIDENCE or c["evidence"] == "pending", c["claim_id"]
        assert c["forbidden_wording"], c["claim_id"]
    (here / "CLAIM_LEDGER_V1.json").write_text(json.dumps(
        {"schema": "orion.claim-ledger.v1", "constitution": "SzeChunYiu/ORION-OCM#144 PUB-D1",
         "claims": CLAIMS}, indent=2) + "\n")
    lines = [
        "# CLAIM_LEDGER_V1\n",
        "**GENERATED FILE — edit `claim_ledger.py`, then run `python claim_ledger.py`.**\n",
        "PUB-D1 of #144. The load-bearing columns are the last two. Every result is recorded with "
        "the sentence it licenses and the sentence it does not, because the way a programme like "
        "this fails is not fabricated data but a real result described one level too strongly.\n",
        "| claim | level | evidence | result |", "|---|---|---|---|",
    ]
    for c in CLAIMS:
        short = c["result"].split(".")[0] if c["result"] != "pending" else "_pending_"
        lines.append(f"| {c['claim_id']} | {c['level']} | {c['evidence']} | {short} |")
    lines.append("")
    for c in CLAIMS:
        lines.append(f"## {c['claim_id']}\n")
        lines.append(f"**Claim.** {c['claim']}\n")
        lines.append(f"**Level.** {c['level']} · **Evidence class.** {c['evidence']}\n")
        lines.append(f"**Hypothesis.** {c['hypothesis']}\n")
        lines.append(f"**Strongest parent.** {c['strongest_parent']}\n")
        lines.append(f"**Experiment.** `{c['experiment']}` · **Replication.** {c['replication']}\n")
        lines.append(f"**Result.** {c['result']}\n")
        lines.append(f"**Limitation.** {c['limitation']}\n")
        lines.append(f"**Permitted wording.** {c['permitted_wording']}\n")
        lines.append(f"**Forbidden wording.** _{c['forbidden_wording']}_\n")
    (here / "CLAIM_LEDGER_V1.md").write_text("\n".join(lines))
    pending = sum(1 for c in CLAIMS if c["result"] == "pending")
    print(f"wrote CLAIM_LEDGER_V1.json and .md: {len(CLAIMS)} claims, {pending} pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
