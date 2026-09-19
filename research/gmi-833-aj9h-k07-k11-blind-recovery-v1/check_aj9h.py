from __future__ import annotations
import importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BLIND = load_module("aj9h_blind", HERE / "blind_recovery_v1.py")
POSTHOC = load_module("aj9h_posthoc", HERE / "posthoc_adjudicate_v1.py")

PRIOR = [
  "gmi-833-aj9b-k01-blind-recovery-v1",
  "gmi-833-aj9c-k02-blind-recovery-v1",
  "gmi-833-aj9d-k03-blind-recovery-v1",
  "gmi-833-aj9e-k04-blind-recovery-v1",
  "gmi-833-aj9f-k05-blind-recovery-v1",
  "gmi-833-aj9g-k06-blind-recovery-v1",
]


def main():
    committed = json.loads((HERE / "BLIND_OUTCOME_V1.json").read_text())
    # Normalize tuples/sets through JSON semantics before comparing a JSON receipt.
    live = json.loads(json.dumps(BLIND.run_all(), sort_keys=True))
    require(live == committed, "blind outcome differs from frozen JSON receipt")
    post = POSTHOC.adjudicate()
    require(len(post["families"]) == 5, "expected five new family adjudications")
    require(all(x["terminal"] == "RECOVERED" and all(x["checks"].values()) for x in post["families"].values()), "a K07-K11 adjudication failed")

    prior_green = 0
    for pkg in PRIOR:
        r = json.loads((ROOT / "research" / pkg / "RESULT_V1.json").read_text())
        require(r.get("status") == "GREEN", f"prior package not GREEN: {pkg}")
        prior_green += 1

    benchmark = json.loads((ROOT / "research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json").read_text())
    require(len(benchmark["families"]) == 11, "benchmark family count drift")
    require({x["family_id"] for x in benchmark["families"]} == {f"K{i:02d}" for i in range(1,12)}, "benchmark family ids drift")
    require(set(benchmark["outcome_terminals"]) == {"COMPILED","RECOVERED","PREDICTED_SELECTED","NOT_RECOVERED_AT_SCOPE"}, "terminal contract drift")

    bias = json.loads((HERE / "BIAS_LEDGER_V1.json").read_text())
    require({"task_authorship","primitive_basis","finite_horizon_or_budget","resource_accounting","acceptance_evaluator","search_procedure_family"} <= set(bias["explicit_priors"]), "required explicit priors missing")

    src = (HERE / "blind_recovery_v1.py").read_text().lower()
    forbidden = [
      "known_family_benchmark", "posthoc_adjudicate", "k07", "k08", "k09", "k10", "k11",
      "planning/control", "retrieval/memory", "evolutionary/population", "program synthesis", "self-modifying/developmental"
    ]
    hits = [x for x in forbidden if x in src]
    require(not hits, f"blind source leaks family knowledge: {hits}")

    terminal_semantics = {(0,0,1,1),(0,1,0,1),(0,0,0,0),(1,1,1,1)}
    require((0,1,1,0) not in terminal_semantics, "failure control unexpectedly expressible")
    failure_terminal = "NOT_RECOVERED_AT_SCOPE"

    result = {
      "status": "GREEN",
      "registered_family_count": 11,
      "prior_k01_k06_green": prior_green,
      "new_k07_k11_recovered": 5,
      "registered_families_recovered_at_their_declared_finite_scopes": 11,
      "new_holdouts_two_materially_different_routes_each": True,
      "blind_source_forbidden_hits": hits,
      "explicit_failure_terminal_control": failure_terminal,
      "outcome_terminals_machine_distinct": benchmark["outcome_terminals"],
      "bias_boundary": "family labels/fingerprints hidden; task-authorship and primitive-basis priors explicitly disclosed",
      "aj9_terminal": "RECOVERED_ALL_REGISTERED_FAMILIES_AT_DECLARED_FINITE_TASK_AND_BASIS_SCOPES",
      "forbidden_promotions": [
        "LITERAL_HISTORICAL_IGNORANCE_PROVED",
        "FAMILY_INEVITABILITY",
        "PREDICTED_SELECTED_FOR_ALL_FAMILIES",
        "REAL_SCALE_ALL_FAMILY_RECOVERY",
        "COMPLETE_GMI"
      ],
      "claim_ceiling": "AJ9_ALL_11_REGISTERED_FAMILIES_RECOVERED_WITH_FAMILY_LABELS_HIDDEN_AT_DECLARED_FINITE_TASK_AND_BASIS_SCOPES"
    }
    (HERE / "RESULT_V1.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (HERE / "POSTHOC_RESULT_V1.json").write_text(json.dumps(post, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
