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
}


def coverage_for(source: str, target: str) -> TransitionCoverage:
    receipts = [n for n, m in EVIDENCE_MAP.items()
                if m["stage"] in (source, target) and _receipt(n) is not None]
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
        "evidence_map": {k: dict(v, supplies=list(v["supplies"]), arms=list(v["arms"]))
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
            f"{len(complete)} of {len(transitions)} developmental transitions are complete. Every "
            "one is blocked on the same two things: no lane has run a CONTINUED arm that carried "
            "state across a stage boundary, and no lane has run a RESET arm to compare it with. "
            "The existing receipts are stage evidence, not transition evidence, and the difference "
            "is the whole of #151."),
        "what_is_actually_missing": [
            "A machine that acquires competence at D0 and then meets D1 carrying it. Every current "
            "receipt either holds one stage's tasks with no acquisition across a boundary, or draws "
            "its tasks independently so nothing is carried.",
            "A reset arm. Without it a lower cost at D1 is equally explained by D1 being easier, "
            "which #151 section 6 names as the thing not to claim development from.",
            "Reuse execution witnesses across a boundary. No object identity in the repository is "
            "currently observed being acquired at one stage and invoked at the next.",
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
