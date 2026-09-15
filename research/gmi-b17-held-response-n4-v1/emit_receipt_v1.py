from __future__ import annotations

import json
import held_response_n4_v1 as witness


def compact_receipt():
    raw = witness.build_receipt()
    ar = {}
    for name, value in raw["ar"].items():
        histogram = {}
        for row in value["orders"]:
            key = str(row["cost"])
            histogram[key] = histogram.get(key, 0) + 1
        ar[name] = {
            "min": value["min"],
            "max": value["max"],
            "stabilizer": value["stabilizer"],
            "cost_histogram": dict(sorted(histogram.items(), key=lambda kv: int(kv[0]))),
        }
        if name == "AND_GRAPH":
            min_orders = [row["order"] for row in value["orders"] if row["cost"] == value["min"]]
            ar[name]["min_orders"] = min_orders
            ar[name]["all_min_orders_output_last"] = all(order[-1] == 3 for order in min_orders)

    flow = {}
    for target_name, row in raw["flow"].items():
        flow[target_name] = {}
        for base_name, cell in row.items():
            compact = {
                "predicted": cell["predicted"],
                "measured": cell["measured"],
                "certificate_verified": cell["certificate_verified"],
            }
            if cell["mapping"] is not None:
                compact["mapping"] = cell["mapping"]
            flow[target_name][base_name] = compact

    return {
        "schema": raw["schema"],
        "issue": raw["issue"],
        "parent_issue": raw["parent_issue"],
        "freeze_commit": raw["freeze_commit"],
        "claim_ceiling": raw["claim_ceiling"],
        "domain": raw["domain"],
        "target_support_sizes": raw["target_support_sizes"],
        "ar": ar,
        "latent": raw["latent"],
        "flow": flow,
        "local_refinement": raw["local_refinement"],
        "old_false_converse_guard": raw["old_false_converse_guard"],
        "claim_guards": raw["claim_guards"],
    }


def main() -> int:
    print(json.dumps(compact_receipt(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
