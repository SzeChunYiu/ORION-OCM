"""DEV-D1 and DEV-D8 of #151: the developmental transition receipt and its controls.

Issue #151 asks for one persistent OCM lineage carrying earned competence across
developmental stages, with a continued-versus-reset-versus-strong-parent
comparison at every transition. Its immediate task list opens with DEV-D1,
"define ``DevelopmentTransitionV1`` and lineage identity", and DEV-D8, "define
continued/reset/task-specific/strong-parent controls for each transition".

This module does those two, and then does the thing that makes them useful: it
reads the receipts that actually exist in the repository and reports how many
complete transitions they support. The answer at the time of writing is zero,
and the value of the artifact is that it says so precisely rather than
aspirationally, naming for each stage exactly which required field has no
evidence behind it.

The distinction the whole spine turns on, from #151 section 3: the decisive
question is not whether the older machine scores higher, it is whether prior
developmental experience causally made the next competence cheaper. A receipt
that records only the first is not a developmental result, so ``cheaper_because``
is a required field and a transition without it is incomplete by construction.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).parent
LADDER = HERE.parent / "cognitive-ladder"

#: #151 section 1. A stage is a rung of the developmental lineage, not a domain.
STAGES = (
    ("D0", "basic exact interaction"),
    ("D1", "composition, failure and scope"),
    ("D2", "planning and uncertainty"),
    ("D3", "formal mathematics and controlled language"),
    ("D4", "coding, tools and scientific investigation"),
    ("D5", "metacognition and learning to learn"),
    ("D6", "governed self-evolution"),
)

#: DEV-D8. Every transition needs all four; a transition missing the reset arm
#: cannot distinguish development from the tasks simply getting easier, which is
#: the failure mode #151 section 6 names explicitly.
REQUIRED_ARMS = {
    "CONTINUED_OCM": "full earned prior developmental state",
    "RESET_OCM": "same immutable architecture and current-stage information, no prior competence",
    "STRONG_ADAPTIVE_PARENT": "strongest faithful parent with matched information, memory, tools "
                              "and adaptation permissions",
    "TASK_SPECIFIC_OCM": "built for this stage alone; bounds how much of any gain is generality",
}

#: #151 section 4. Every field is required. A receipt missing one is INCOMPLETE
#: rather than partial, because a developmental claim resting on an absent
#: coordinate is exactly what the constitution forbids.
TRANSITION_FIELDS = (
    "lineage_id", "source_stage", "target_stage",
    "source_machine_identity", "target_machine_identity", "persistent_state_digest",
    "prior_information_manifest", "new_information_supplied",
    "new_methods", "new_schemas", "new_representations",
    "reused_object_identities", "reuse_execution_witnesses",
    "new_primitive_operators_admitted", "composition_depth",
    "acquisition_cost", "query_cost", "verification_cost", "revision_cost",
    "maintenance_cost", "persistent_bytes", "active_k", "total_N",
    "retention", "negative_transfer", "harmful_transfer_refusals",
    "ablation_result", "strongest_parent_result", "terminal",
    # not in #151's list, added because section 3 makes it the decisive question
    "cheaper_because",
)


@dataclass(frozen=True)
class LineageIdentity:
    """DEV-D1 lineage identity.

    A lineage is not a branch and not a directory. It is the chain of persistent
    state digests, each carrying the digest before it, so that a machine cannot
    be silently swapped for another that merely looks similar. Any gap in the
    chain is a reset, whether or not it was intended as one.
    """

    lineage_id: str
    genesis_digest: str
    links: tuple[tuple[str, str, str], ...] = ()   # (stage, prev_digest, digest)

    def extend(self, stage: str, digest: str) -> "LineageIdentity":
        prev = self.links[-1][2] if self.links else self.genesis_digest
        return LineageIdentity(self.lineage_id, self.genesis_digest,
                               self.links + ((stage, prev, digest),))

    @property
    def continuous(self) -> bool:
        prev = self.genesis_digest
        for _stage, p, d in self.links:
            if p != prev:
                return False
            prev = d
        return True

    def chain_digest(self) -> str:
        body = json.dumps([self.lineage_id, self.genesis_digest,
                           [list(l) for l in self.links]], sort_keys=True)
        return hashlib.sha256(body.encode()).hexdigest()


@dataclass(frozen=True)
class TransitionCoverage:
    """What the existing receipts do and do not supply for one transition."""

    source_stage: str
    target_stage: str
    fields_present: tuple[str, ...]
    fields_missing: tuple[str, ...]
    arms_present: tuple[str, ...]
    arms_missing: tuple[str, ...]
    supporting_receipts: tuple[str, ...]
    complete: bool
    blocking_reason: str


def _receipt(name: str) -> dict | None:
    p = LADDER / "results" / name
    if not p.is_file():
        return None
    return json.loads(p.read_text())


#: What each existing receipt contributes toward a developmental transition.
#: Deliberately conservative: a receipt counts toward a field only if it measured
#: that field for a machine that CARRIED STATE ACROSS the boundary, which is what
#: makes a measurement developmental rather than merely repeated.
EVIDENCE_MAP = {
    "SCALING_PILOT_V1.json": dict(
        stage="D0", supplies=("persistent_bytes", "active_k", "total_N", "query_cost",
                              "maintenance_cost", "strongest_parent_result", "terminal"),
        arms=("STRONG_ADAPTIVE_PARENT",),
        note="carries state across scales without reset, so its k and byte measurements are "
             "lineage measurements. It has no reset arm and no acquisition of new competence, "
             "so it is stage evidence, not transition evidence."),
    "SUBSPACE_E1_V1.json": dict(
        stage="D0", supplies=("query_cost", "maintenance_cost", "persistent_bytes",
                              "strongest_parent_result", "terminal"),
        arms=("STRONG_ADAPTIVE_PARENT",),
        note="same lineage discipline; adds the relevance-key degradation measurement."),
    "REINDEX_E9_V1.json": dict(
        stage="D0", supplies=("maintenance_cost", "strongest_parent_result", "terminal"),
        arms=("STRONG_ADAPTIVE_PARENT",),
        note="an engineering fix to one coordinate; contributes maintenance cost only."),
    "DEPEND_E3_V1.json": dict(
        stage="D0", supplies=("revision_cost", "ablation_result", "terminal"),
        arms=("STRONG_ADAPTIVE_PARENT",),
        note="revocation across a growing store; supplies revision cost."),
    "FAILURE_PILOT_V1.json": dict(
        stage="D1", supplies=("negative_transfer", "harmful_transfer_refusals", "terminal",
                              "strongest_parent_result"),
        arms=("STRONG_ADAPTIVE_PARENT",),
        note="scope and failure knowledge, which is D1 material, but each world is independent "
             "so nothing is carried from D0."),
    "DIAGNOSIS_E2_V1.json": dict(
        stage="D2", supplies=("verification_cost", "terminal", "strongest_parent_result"),
        arms=("STRONG_ADAPTIVE_PARENT",),
        note="probe selection under hidden cause, which is D2 material."),
    "ESCALATION_INDEPENDENT_E4_V1.json": dict(
        stage="D2", supplies=("terminal", "strongest_parent_result"),
        arms=("STRONG_ADAPTIVE_PARENT",),
        note="obstruction versus search-more, which is D2 material."),
    "DEV1_D0_TO_D1_V1.json": dict(
        stage="D1", transition=("D0", "D1"), supplies=TRANSITION_FIELDS,
        arms=tuple(REQUIRED_ARMS),
        note="the first receipt in the repository written for a TRANSITION rather than a "
             "stage: one lineage carries its D0 store across the boundary, a reset arm with "
             "the same architecture and the same D1 stream does not, a clairvoyant parent "
             "bounds the claim, and a task-specific arm bounds how much of the gain is "
             "generality. It counts only for D0 to D1, and its own terminal is CONDITIONAL: "
             "the lineage wins at 1024 bits and loses at 256, so this transition is complete "
             "in the sense of being MEASURED, not in the sense of being won everywhere. "
             "SUPERSEDED ON THE CARRY CLAIM by DEV2_CONTINUAL_PARENTS_V1: a plain experience "
             "replay parent, at the same budget on the same streams, beats the lineage at "
             "five of six settings and by 1.57x at the loose budget where DEV-1 reported its "
             "only positive. The transition is still measured and its four arms still ran; "
             "what is withdrawn is the claim that carrying an ABSTRACTED store was the best "
             "use of the budget."),
}


def coverage_for(source: str, target: str) -> TransitionCoverage:
    """What the receipts on disk supply for one transition.

    A receipt marked with a ``transition`` counts ONLY for that exact pair. A
    stage receipt counts toward either endpoint. The distinction matters because
    a stage receipt can never supply a lineage identity or a reuse witness: those
    exist only if a machine actually crossed the boundary carrying state, which
    is what ``coverage_for`` was written to refuse to pretend.
    """
    receipts = []
    for n, m in EVIDENCE_MAP.items():
        if _receipt(n) is None:
            continue
        if "transition" in m:
            if tuple(m["transition"]) == (source, target):
                receipts.append(n)
        elif m["stage"] in (source, target):
            receipts.append(n)
    present: set[str] = set()
    arms: set[str] = set()
    for n in receipts:
        present.update(EVIDENCE_MAP[n]["supplies"])
        arms.update(EVIDENCE_MAP[n]["arms"])
    # identity and reuse fields are never supplied by a stage receipt: they exist
    # only if a machine actually crossed the boundary carrying state.
    missing = tuple(f for f in TRANSITION_FIELDS if f not in present)
    arms_missing = tuple(a for a in REQUIRED_ARMS if a not in arms)
    if arms_missing:
        blocking = (f"no {', '.join(arms_missing)} arm exists for this transition; without a reset "
                    "arm a cost difference cannot be distinguished from the later tasks simply "
                    "being easier")
    elif missing:
        blocking = f"{len(missing)} required fields have no evidence: {', '.join(missing[:4])}..."
    else:
        blocking = ""
    return TransitionCoverage(
        source_stage=source, target_stage=target,
        fields_present=tuple(sorted(present)), fields_missing=missing,
        arms_present=tuple(sorted(arms)), arms_missing=arms_missing,
        supporting_receipts=tuple(sorted(receipts)),
        complete=not missing and not arms_missing,
        blocking_reason=blocking)


def build() -> dict:
    transitions = [coverage_for(STAGES[i][0], STAGES[i + 1][0]) for i in range(len(STAGES) - 1)]
    complete = [t for t in transitions if t.complete]
    return {
        "schema": "orion.developmental-spine.v1",
        "issue": "SzeChunYiu/ORION-OCM#151",
        "discharges": ["DEV-D1 transition schema and lineage identity",
                       "DEV-D8 continued/reset/task-specific/strong-parent controls"],
        "authority": (
            "This defines a receipt shape and reports coverage. It runs no experiment, produces no "
            "evidence and upgrades nothing. Existing pilots remain E1/E2 per #151 section 12."),
        "stages": [{"stage": s, "description": d} for s, d in STAGES],
        "required_arms": REQUIRED_ARMS,
        "transition_fields": list(TRANSITION_FIELDS),
        "field_added_beyond_151": {
            "cheaper_because": (
                "#151 section 3 states the decisive question is not whether the older machine "
                "scores higher but whether prior experience causally made the next competence "
                "cheaper. A receipt recording only the score would satisfy the listed fields and "
                "still not answer that, so the causal attribution is a required field here.")
        },
        "evidence_map": {k: dict(v, supplies=list(v["supplies"]), arms=list(v["arms"]),
                                 **({"transition": list(v["transition"])}
                                    if "transition" in v else {}))
                         for k, v in EVIDENCE_MAP.items()},
        "transitions": [{
            "source_stage": t.source_stage, "target_stage": t.target_stage,
            "complete": t.complete,
            "supporting_receipts": list(t.supporting_receipts),
            "arms_present": list(t.arms_present), "arms_missing": list(t.arms_missing),
            "fields_present": list(t.fields_present), "fields_missing": list(t.fields_missing),
            "blocking_reason": t.blocking_reason,
        } for t in transitions],
        "complete_transitions": len(complete),
        "transitions_total": len(transitions),
        "headline": (
            f"{len(complete)} of {len(transitions)} developmental transitions are complete. D0 to "
            "D1 is measured: DEV1_D0_TO_D1_V1 runs a lineage that carries its D0 store across the "
            "boundary, a reset arm with the same architecture and the same D1 stream that does "
            "not, a clairvoyant parent, and a task-specific arm. Its verdict is CONDITIONAL, not "
            "a win -- the lineage beats reset at 1024 bits and loses at 256 -- and 'complete' here "
            "means MEASURED WITH ALL FOUR ARMS AND ALL REQUIRED FIELDS, never 'succeeded'. The "
            "remaining five are still blocked on the same two things: no lane has run a CONTINUED "
            "arm across those boundaries and no lane has run a RESET arm to compare it with. The "
            "existing receipts for them are stage evidence, not transition evidence, and that "
            "difference is the whole of #151."),
        "the_one_complete_transition_lost_to_a_parent": (
            "DEV-2 ran the continual-learning parents DEV-1 never ran. Experience replay -- "
            "keep the answers, never abstract -- beats the lineage at the budget where DEV-1 "
            "reported its win, and its margin GROWS with D1 length (1.19, 1.40, 1.57 at "
            "lengths 250, 1000, 4000), which is the opposite shape from the decaying head "
            "start DEV-1 described. The mechanism is priced rather than asserted: a held "
            "rule licenses a scope check, so using one costs VERIFY + APPLY where a stored "
            "answer costs LOOKUP, and a sweep over the check price flips the sign between 10 "
            "and 25 with replay's own work constant throughout. DEV-1's comparison against "
            "RESET_OCM stands and answers the question it asked; the carry advantage is "
            "PARENT_SUFFICIENT."),
        "complete_does_not_mean_succeeded": (
            "A transition counts as complete when all four DEV-D8 arms ran and every required "
            "field has evidence behind it. D0 to D1 qualifies and its own terminal is "
            "D0_TO_D1_TRANSITION_CONDITIONAL. Reading this count as a score would be exactly the "
            "error #151 section 6 warns about, so the count is reported beside the terminal and "
            "never alone."),
        "what_is_actually_missing": [
            "Four more machines that acquire competence at one stage and meet the next carrying "
            "it. D0 to D1 now has one; D1 to D2 onward have none, and their current receipts "
            "either hold one stage's tasks with no acquisition across a boundary or draw their "
            "tasks independently so nothing is carried.",
            "Reset arms for those transitions. Without one, a lower cost at the later stage is "
            "equally explained by that stage being easier, which #151 section 6 names as the "
            "thing not to claim development from.",
            "A transition that holds at every store budget. The one that exists does not: at 256 "
            "bits the D0 store saturates and the lineage loses, which is a real limit on the "
            "claim rather than a gap in the evidence.",
        ],
        "cheapest_first_transition": (
            "D0 to D1 on the exact game families already built. D0 acquires periodic-rule methods; "
            "D1 requires composing two of them, which the SUBNIM family in games.py already "
            "supports because neither the one-heap nor the Nim training family contains the "
            "combined solution. That is DEV-D10 and it needs no new domain."),
    }


def main() -> int:
    doc = build()
    (HERE / "DEVELOPMENTAL_SPINE_V1.json").write_text(json.dumps(doc, indent=2) + "\n")
    L = ["# DEVELOPMENTAL_SPINE_V1\n",
         "**GENERATED FILE — edit `spine.py`, then run `python spine.py`.**\n",
         f"DEV-D1 and DEV-D8 of [#151](https://github.com/SzeChunYiu/ORION-OCM/issues/151).\n",
         f"> {doc['headline']}\n",
         "| transition | complete | receipts | arms present | blocking |",
         "|---|---|---|---|---|"]
    for t in doc["transitions"]:
        L.append(f"| {t['source_stage']} → {t['target_stage']} | {t['complete']} | "
                 f"{len(t['supporting_receipts'])} | {', '.join(t['arms_present']) or '—'} | "
                 f"{t['blocking_reason'][:80]}… |")
    L += ["", "## Required arms (DEV-D8)\n"]
    for a, d in REQUIRED_ARMS.items():
        L.append(f"- **{a}** — {d}")
    L += ["", "## What is actually missing\n"]
    for x in doc["what_is_actually_missing"]:
        L.append(f"- {x}")
    L += ["", f"## Cheapest first transition\n\n{doc['cheapest_first_transition']}\n",
          "## The field added beyond #151's list\n",
          f"`cheaper_because` — {doc['field_added_beyond_151']['cheaper_because']}\n",
          "## Evidence map\n",
          "| receipt | stage | supplies | note |", "|---|---|---|---|"]
    for k, v in doc["evidence_map"].items():
        L.append(f"| `{k}` | {v['stage']} | {len(v['supplies'])} fields | {v['note']} |")
    (HERE / "DEVELOPMENTAL_SPINE_V1.md").write_text("\n".join(L))
    print(f"wrote DEVELOPMENTAL_SPINE_V1: {doc['complete_transitions']}/"
          f"{doc['transitions_total']} transitions complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
