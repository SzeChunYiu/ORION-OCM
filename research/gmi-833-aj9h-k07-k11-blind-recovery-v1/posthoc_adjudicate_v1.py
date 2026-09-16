from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def adjudicate():
    blind = json.loads((HERE / "BLIND_OUTCOME_V1.json").read_text())
    bench = json.loads((ROOT / "research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json").read_text())
    ids = {x["family_id"] for x in bench["families"]}
    assert {"K07","K08","K09","K10","K11"} <= ids

    a, b, c, d, e = (blind[x] for x in "ABCDE")
    checks = {
      "K07": {
        "terminal": "RECOVERED",
        "checks": {
          "future_consequence_evaluated": a["route_enumeration"]["total"] == 5 and a["route_recursive"]["total"] == 5,
          "choice_not_immediate_greedy": a["future_consequence_changes_choice"] and a["selected_first_action"] != a["immediate_greedy_first_action"],
          "multistep_transition_trace": len(a["trace"]) == 2
        }
      },
      "K08": {
        "terminal": "RECOVERED",
        "checks": {
          "multiple_persistent_records": len(b["route_exact_scan"]["indices"]) == 3,
          "query_changes_selected_record": b["different_queries_select_different_records"],
          "retrieved_record_causes_output": b["alter_selected_record_changes_output"],
          "two_routes_agree": b["route_exact_scan"] == b["route_distance"]
        }
      },
      "K09": {
        "terminal": "RECOVERED",
        "checks": {
          "population_required_at_registered_budget": c["single_retained_fails"] and c["two_retained_succeeds"] and c["minimum_successful_retained_count"] == 2,
          "heritable_component_information": all(bit in {p[i] for p in c["selected_parents"]} for i, bit in enumerate(c["descendant"])),
          "variation_creates_new_descendant": c["descendant"] not in c["selected_parents"],
          "evaluation_changes_persistent_membership": c["descendant"] in c["next_members"],
          "two_routes_agree": c["route_factorized_inheritance"]["best"] == c["route_capacity_enumeration"]["2"]["best"]
        }
      },
      "K10": {
        "terminal": "RECOVERED",
        "checks": {
          "legal_executable_expression_space": d["returned_artifact_executable"] and d["multiple_legal_programs_present"],
          "semantic_specification_accepts": d["route_expression"]["outputs"] == [0,1,1,0] and d["route_cube_cover"]["outputs"] == [0,1,1,0],
          "returned_artifact_is_expression": isinstance(d["route_expression"]["expression"], str),
          "two_materially_different_routes": d["route_expression"]["cost"] != d["route_cube_cover"]["cube_count"] or d["route_expression"]["expression"] != str(d["route_cube_cover"]["cubes"])
        }
      },
      "K11": {
        "terminal": "RECOVERED",
        "checks": {
          "persistent_mechanism_change": e["library_before"] != e["library_after"],
          "change_used_later": e["persistent_change_used_later"] and e["later_uses"] > 0,
          "causally_linked_cost_improvement": e["strict_cumulative_improvement"] and e["baseline_cumulative_cost"] > e["route_substring_enumeration"]["cumulative_cost"],
          "two_routes_agree": e["route_substring_enumeration"]["chosen"] == e["route_frequency_gain"]["chosen"]
        }
      }
    }
    for row in checks.values():
        assert all(row["checks"].values())
    return {
      "schema": "AJ9H_POSTHOC_RESULT_V1",
      "benchmark_role": "POSTHOC_ONLY",
      "families": checks,
      "scope_boundary": "RECOVERED conditional on frozen task ecology and generic primitive basis; task-authorship and primitive-basis priors remain disclosed"
    }


if __name__ == "__main__":
    out = adjudicate()
    (HERE / "POSTHOC_RESULT_V1.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))
