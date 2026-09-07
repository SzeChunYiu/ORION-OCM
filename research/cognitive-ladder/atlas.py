"""Render the ORION concept validation atlas from its single source of truth.

Emits ``ORION_CONCEPT_VALIDATION_ATLAS_V1.json`` and the human twin
``ORION_CONCEPT_VALIDATION_ATLAS_V1.md``.  Both are generated; neither is edited
by hand, so the machine-readable and human-readable views cannot drift.

Run: ``python atlas.py``
"""

from __future__ import annotations

import json
import pathlib

from atlas_data import CONCEPTS, DISPOSITIONS, SCIENTIFIC_STATUS, SIGNATURES

HERE = pathlib.Path(__file__).parent
JSON_PATH = HERE / "ORION_CONCEPT_VALIDATION_ATLAS_V1.json"
MD_PATH = HERE / "ORION_CONCEPT_VALIDATION_ATLAS_V1.md"

HEADER = """# ORION_CONCEPT_VALIDATION_ATLAS_V1

**GENERATED FILE — edit `atlas_data.py`, then run `python atlas.py`.**

Every ORION concept that could materially affect cognition is recorded here as a
*hypothesis under test*, never as a feature requirement. Three rules govern the table.

1. **Implementation is never scientific support.** `implementation_status` and
   `scientific_status` are separate columns. A concept may be fully built and still sit at
   `THEORY_ONLY` or `PARENT_SUFFICIENT`.
2. **Existing negative results survive.** `preserved_terminals` carries exact terminal strings
   already recorded elsewhere in the ORION repositories. New work may open a *new*
   pre-registered study. It may not reinterpret an old receipt.
3. **Every concept can die.** `falsifier` and `disposition` are mandatory. A concept a parent
   explains is merged. A concept with no measurable incremental value is dropped.

## Vocabulary discipline

`PARENT_SUFFICIENT` is a **successful** terminal, not a failure and not a statement that prior
published work suffices. In several ORION studies the parent federation holds ORION's own typed
modules, and its comparator class is recorded there as a ceiling control rather than prior work.

Saturation in ORION V1 and V2 always means **search coverage of a declared literature or donor
universe**. Cognitive saturation, meaning an agent's own reasoning ceasing to yield new
decision-relevant structure, is unclaimed in both repositories. It is introduced here as a new
concept and is not attributed to ORION.

"""


def _fmt_list(xs) -> str:
    return "; ".join(str(x) for x in xs) if xs else "none"


def build_json() -> dict:
    return {
        "schema": "orion.concept-validation-atlas.v1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "authority": (
            "This atlas records hypotheses, dispositions and preserved terminals. It grants no "
            "scientific status, no field status and no novelty. Implementation status is never "
            "evidence of scientific support."
        ),
        "scientific_status_ladder": list(SCIENTIFIC_STATUS),
        "dispositions": list(DISPOSITIONS),
        "machine_epistemics_signatures": list(SIGNATURES),
        "concept_count": len(CONCEPTS),
        "concepts": [
            {k: (list(v) if isinstance(v, tuple) else v) for k, v in c.items()}
            for c in CONCEPTS
        ],
    }


def build_md() -> str:
    out = [HEADER]
    by_disp: dict[str, list] = {}
    for c in CONCEPTS:
        by_disp.setdefault(c["disposition"], []).append(c)

    out.append("## Summary\n")
    out.append("| disposition | concepts |")
    out.append("|---|---|")
    for d in DISPOSITIONS:
        ids = [c["concept_id"] for c in by_disp.get(d, [])]
        if ids:
            out.append(f"| **{d}** | {', '.join(ids)} |")
    out.append("")

    out.append("| concept | disposition | scientific status | implementation | paper role |")
    out.append("|---|---|---|---|---|")
    for c in sorted(CONCEPTS, key=lambda c: (c["disposition"], c["concept_id"])):
        out.append(
            f"| {c['concept_id']} | {c['disposition']} | {c['scientific_status']} | "
            f"{c['implementation_status']} | {c['paper_role'] or 'none'} |"
        )
    out.append("")

    pilots = sorted([c for c in CONCEPTS if c["pilot_rank"]], key=lambda c: c["pilot_rank"])
    out.append("## Immediately testable in the current exact-game apparatus\n")
    for c in pilots:
        out.append(f"{c['pilot_rank']}. **{c['concept_id']}** — strongest parent: "
                   f"{c['strongest_parents'][0] if c['strongest_parents'] else 'none named'}.")
    out.append("")

    out.append("## Concepts\n")
    for c in CONCEPTS:
        out.append(f"### {c['concept_id']}\n")
        out.append(f"*{c['disposition']}* · scientific status **{c['scientific_status']}** · "
                   f"implementation `{c['implementation_status']}` · paper role: "
                   f"{c['paper_role'] or 'none'}\n")
        out.append(f"**Definition.** {c['formal_definition']}\n")
        out.append(f"**Explicitly not.** {c['explicit_nondefinition']}\n")
        out.append(f"**Strongest parents.** {_fmt_list(c['strongest_parents'])}\n")
        out.append(f"**Observable state.** {c['ocm_observable_state']} "
                   f"**Trigger.** {c['trigger']}\n")
        out.append(f"**Mechanism.** {c['proposed_ocm_mechanism']} "
                   f"**Information available.** {c['information_available_to_mechanism']}\n")
        out.append(f"**Positive family.** {c['positive_case_family']}\n")
        out.append(f"**Negative twin.** {c['negative_twin']}\n")
        out.append(f"**Hostile.** {c['hostile_case']}\n")
        out.append(f"**Ablation.** {c['ablation']}\n")
        out.append(f"**Resource coordinates.** {_fmt_list(c['resource_coordinates'])}\n")
        out.append(f"**Cross-family test.** {c['cross_family_test']} "
                   f"**Cross-domain test.** {c['cross_domain_test']}\n")
        out.append(f"**Interactions.** {_fmt_list(c['interaction_dependencies'])}\n")
        out.append(f"**Falsifier.** {c['falsifier']}\n")
        out.append(f"**Disposition reason.** {c['disposition_reason']}\n")
        if c["preserved_terminals"]:
            out.append("**Preserved terminals (do not re-litigate).**\n")
            for t in c["preserved_terminals"]:
                out.append(f"- `{t}`")
            out.append("")
        out.append(f"**Signatures.** {_fmt_list(c['signatures'])}\n")
        out.append(f"**Reopen condition.** {c['reopen_condition'] or 'none'}\n")
    return "\n".join(out)


def main() -> int:
    JSON_PATH.write_text(json.dumps(build_json(), indent=2, sort_keys=False) + "\n")
    MD_PATH.write_text(build_md())
    print(f"wrote {JSON_PATH.name} and {MD_PATH.name}: {len(CONCEPTS)} concepts, "
          f"{sum(len(c['preserved_terminals']) for c in CONCEPTS)} preserved terminals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
