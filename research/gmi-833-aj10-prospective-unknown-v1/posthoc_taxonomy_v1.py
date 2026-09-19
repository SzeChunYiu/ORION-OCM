from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main_result():
    evaluated = json.loads((HERE / "EVALUATED_CANDIDATES_V1.json").read_text())
    benchmark = json.loads((ROOT / "research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json").read_text())
    assert len(benchmark["families"]) == 11
    by_id = {c["candidate_id"]: c for c in evaluated["candidates"]}
    assert set(by_id) == {"T232", "E4"}
    assert set(evaluated["pareto_frontier"]) == {"T232", "E4"}

    e = by_id["E4"]
    t = by_id["T232"]

    # K10 match is evaluated only now, after pre-taxonomy capability/resource freeze.
    e_k10 = (
        isinstance(e.get("expression"), str)
        and e["truth"] == evaluated["capability"] and False
    )
    # The capability object is intentionally not a truth vector; use the protected output directly.
    env = json.loads((HERE / "HELDOUT_ENV_V1.json").read_text())
    e_k10 = isinstance(e.get("expression"), str) and e["truth"] == env["protected_outputs"]
    assert e_k10

    # T232 is not represented as an expression/program in the frozen expression language.
    t_registered_match = False

    candidates = {
      "E4": {
        "registered_taxonomy": "KNOWN_REGISTERED_FAMILY",
        "registered_family": "K10",
        "strongest_parent_review": "finite Boolean expression/program synthesis from a complete protected specification",
        "novelty": {
          "implementation": "NOT_ESTABLISHED",
          "morphology_architecture": "NOT_ESTABLISHED",
          "algorithmic_mechanism": "PARENT_REDUCED_KNOWN",
          "computational_class": "PARENT_REDUCED_KNOWN",
          "capability_profile": "TASK_SPECIFIC_NOT_NOVEL"
        }
      },
      "T232": {
        "registered_taxonomy": "UNKNOWN_MORPHOLOGY" if not t_registered_match else "KNOWN_REGISTERED_FAMILY",
        "registered_family": None,
        "strongest_parent_review": "classical finite truth-table / lookup-table representation of a Boolean function",
        "post_parent_terminal": "PARENT_REDUCED_KNOWN",
        "novelty": {
          "implementation": "NOT_ESTABLISHED",
          "morphology_architecture": "PARENT_REDUCED_KNOWN",
          "algorithmic_mechanism": "PARENT_REDUCED_KNOWN",
          "computational_class": "PARENT_REDUCED_KNOWN",
          "capability_profile": "TASK_SPECIFIC_NOT_NOVEL"
        }
      }
    }

    assert candidates["T232"]["registered_taxonomy"] == "UNKNOWN_MORPHOLOGY"
    assert candidates["T232"]["post_parent_terminal"] == "PARENT_REDUCED_KNOWN"
    assert all(v != "NOVEL_AT_REGISTERED_SCOPE" for c in candidates.values() for v in c["novelty"].values())

    return {
      "schema": "AJ10_POSTHOC_TAXONOMY_AND_PARENT_REDUCTION_V1",
      "taxonomy_ran_after_pre_taxonomy_evaluation": True,
      "candidates": candidates,
      "overall_morphology_disposition": "CANNOT_IDENTIFY_UNIQUE_MORPHOLOGY_FROM_CAPABILITY_AND_RAW_PARETO_RESOURCES",
      "unknown_channel_exercised": True,
      "strongest_parent_reduction_ran_after_generation_and_evaluation": True,
      "novel_form_claimed": False,
      "novel_replication_gate": "NOT_TRIGGERED_NO_NOVEL_CLAIM",
      "unknown_policy": "UNKNOWN is preserved through registered-family matching; strongest-parent evidence may subsequently reduce it to known without retroactively changing the pre-taxonomy record"
    }


if __name__ == "__main__":
    out = main_result()
    (HERE / "POSTHOC_RESULT_V1.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))
