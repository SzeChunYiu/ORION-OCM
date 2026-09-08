"""Render the theory-to-empirics registry of #145 (GUO-D1).

Emits ``THEORY_EMPIRICAL_REGISTRY_V1.json`` and its human twin.  Both are
generated from ``registry_data.py``; neither is edited by hand.

Run: ``python registry.py``
"""

from __future__ import annotations

import json
import pathlib

from registry_data import ROUTES, STATUS, THEORIES

HERE = pathlib.Path(__file__).parent

HEADER = """# THEORY_EMPIRICAL_REGISTRY_V1

**GENERATED FILE — edit `registry_data.py`, then run `python registry.py`.**

GUO-D1 of [#145](https://github.com/SzeChunYiu/ORION-OCM/issues/145). No theory claim may enter
manuscript prose without a row here, and every row names a concrete rung of #143 able to kill it.

This registry is written the unusual way round. Most are populated with statements someone hopes to
prove, and the status column stays `OPEN` for years. This one leads with the statements the
programme has already **refuted**, because those were the load-bearing ones and they turned out not
to be. A registry whose refuted rows are missing is a wish list.

Verification routes, per #145 §5: `V1_FORMAL_PROOF`, `V2_EXACT_COMPUTATION` over a complete finite
universe, `V3_PROSPECTIVE_EMPIRICAL`. Each row declares exactly one primary route.

"""


def build_json() -> dict:
    return {
        "schema": "orion.theory-empirical-registry.v1",
        "issue": "SzeChunYiu/ORION-OCM#145",
        "empirical_parent": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "authority": (
            "This registry records theory statements, their falsifiers and their current status. It "
            "grants no scientific status to anything it lists. A row marked SUPPORTED_AT_SCOPE is "
            "supported at that scope and nowhere else."
        ),
        "verification_routes": list(ROUTES),
        "status_vocabulary": list(STATUS),
        "row_count": len(THEORIES),
        "theories": [
            {k: (list(v) if isinstance(v, tuple) else v) for k, v in t.items()} for t in THEORIES
        ],
    }


def build_md() -> str:
    out = [HEADER, "## Status board\n",
           "| theory | status | route | falsifying rung |", "|---|---|---|---|"]
    order = {"REFUTED": 0, "PARENT_SUFFICIENT": 1, "PARENT_OWNED": 2, "SUPPORTED_AT_SCOPE": 3,
             "OPEN": 4, "NOT_YET_TESTABLE": 5}
    rows = sorted(THEORIES, key=lambda t: (order.get(t["status"], 9), t["theory_id"]))
    for t in rows:
        out.append(f"| {t['theory_id']} | **{t['status']}** | {t['verification_route'].split('_')[0]} "
                   f"| {t['empirical_rung']} |")
    out.append("")
    out.append("## Rows\n")
    for t in rows:
        out.append(f"### {t['theory_id']} — {t['status']}\n")
        out.append(f"> {t['statement']}\n")
        out.append(f"**Scope.** {t['scope']}\n")
        if t["assumptions"]:
            out.append("**Assumptions.** " + "; ".join(t["assumptions"]) + "\n")
        out.append(f"**Field.** {t['field_identity']} · **Operator basis.** "
                   f"{t['operator_basis_identity']}\n")
        out.append(f"**Resource model.** {t['resource_model']}\n")
        out.append(f"**Predicted observable.** {t['predicted_observable']} — "
                   f"**direction:** {t['predicted_direction']}\n")
        out.append(f"**Route.** {t['verification_route']} · **Falsifying rung.** "
                   f"{t['empirical_rung']}\n")
        out.append(f"**Strongest parent.** {t['strongest_parent']}\n")
        out.append(f"**Causal ablation.** {t['causal_ablation']} · **Negative twin.** "
                   f"{t['negative_twin']}\n")
        out.append(f"**Falsifier.** {t['falsifier']}\n")
        out.append(f"**Evidence.** {t['evidence']}\n")
        out.append(f"**Reopen condition.** {t['reopen_condition']}\n")
    return "\n".join(out)


def main() -> int:
    for t in THEORIES:
        assert t["verification_route"] in ROUTES, t["theory_id"]
        assert t["status"] in STATUS, t["theory_id"]
        assert t["falsifier"], t["theory_id"]
        assert t["empirical_rung"], t["theory_id"]
    (HERE / "THEORY_EMPIRICAL_REGISTRY_V1.json").write_text(
        json.dumps(build_json(), indent=2) + "\n")
    (HERE / "THEORY_EMPIRICAL_REGISTRY_V1.md").write_text(build_md())
    from collections import Counter
    counts = Counter(t["status"] for t in THEORIES)
    print(f"wrote THEORY_EMPIRICAL_REGISTRY_V1.json and .md: {len(THEORIES)} rows, "
          f"{dict(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
