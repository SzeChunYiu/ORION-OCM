"""Execute preregistered calibration or held-graph controls on laptop."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from factor_cases import direct_value, make_case
from factor_compile import eliminate
from factor_model import serialize_value
from factor_search import search_orders


FROZEN_REGISTRATION = "1fab06ba8380973ec5e5a4f04a8e3b6ef23064c1b2dd49d7b5459f5257bf9252"


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(stage):
    raw = Path(__file__).with_name("factor_registration.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    check(digest == FROZEN_REGISTRATION, "registration changed after freeze")
    registration = json.loads(raw)
    specs = (registration["calibration"] + registration["heldout"] if stage == "all"
             else registration[stage])
    records = []
    for spec in specs:
        n, q = spec["variables"], spec["domain_size"]
        for name in registration["algebras"]:
            sizes, factors, algebra = make_case(spec, name)
            reference = direct_value(sizes, factors, algebra)
            result = search_orders(sizes, factors, algebra)
            check(result["best"]["value"] == reference, "enumeration mismatch")
            check(result["search"]["candidates"] == math.factorial(n), "missed orders")
            check(len({tuple(c["order"]) for c in result["candidates"]}) == math.factorial(n),
                  "duplicate or missing order")
            for candidate in result["candidates"]:
                bound = (2 * len(factors) + 3 * n) * q ** (candidate["width"] + 1)
                check(candidate["work"] <= bound + 2 * (len(factors) + n), "width bound")
            witnesses = {}
            if spec["graph"] == "chain":
                trial = eliminate(sizes, factors, algebra, tuple(range(n)))
                check(trial["profile"]["work"] == (5*n-7)*q*q + 3*q + 2, "chain law")
                check(trial["profile"]["width"] == 1, "chain width")
                witnesses["left_to_right"] = trial["profile"]
            if spec["graph"] == "star":
                first = eliminate(sizes, factors, algebra, tuple(range(n)))
                last = eliminate(sizes, factors, algebra, tuple(range(1, n)) + (0,))
                check(last["profile"]["work"] == 3*(n-1)*q*q+(2*n-1)*q+2, "star last")
                expected = (2*n-1)*q**n + 3*sum(q**j for j in range(1, n)) + 2
                check(first["profile"]["work"] == expected, "star first")
                check(first["profile"]["work"] > last["profile"]["work"], "negative order")
                witnesses.update(center_first=first["profile"], center_last=last["profile"])
            if spec["graph"] == "clique":
                check(len(result["ties"]) == math.factorial(n), "clique ties lost")
                check(all(p["width"] == n-1 for p in result["candidates"]), "clique width")
            if spec["graph"] == "cycle":
                check(min(p["width"] for p in result["candidates"]) == 2, "cycle witness")
            record = dict(case=spec["id"], algebra=name, value=serialize_value(reference),
                          selected_order=list(result["best"]["order"]),
                          selected_profile=result["best"]["profile"],
                          tie_count=len(result["ties"]), search=result["search"],
                          witnesses=witnesses)
            records.append(record)
    return dict(status="CHECKED", schema="GMI_FACTOR_REPLAY_V1", stage=stage,
                registration_sha256=digest, cases=len(records), records=records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("calibration", "heldout", "all"), default="all")
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.stage), sort_keys=True, indent=2))
