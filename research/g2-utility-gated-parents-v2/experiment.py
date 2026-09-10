"""G2.5 v2: utility-gated library admission. Does not retune v1."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))
V1 = REPO / "research" / "g2-strong-parents-v1"

from ocm.learning import methods as M

import importlib.util

_spec = importlib.util.spec_from_file_location("g2_strong_parents_v1_experiment", V1 / "experiment.py")
V1E = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(V1E)

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-g2-ugate-train-v2"
VAL_SALT = "orion-ocm-g2-ugate-val-v2"
TEST_SALT = "orion-ocm-g2-ugate-test-v2"
TRAIN_N = 16
VAL_N = 16
TEST_N = 16
TRAIN_LEN = 4
VAL_LEN = 5
TEST_LEN = 5
CANDIDATE_CAP = 8
V1_FROZEN_TERMINAL = "HARMFUL_TRANSFER_LIMIT"
V1_FREQUENCY_FRAGMENT = ("inc", "double")


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def main(out: Path) -> dict:
    blob = git_blob_sha1(SRC / "ocm" / "learning" / "methods.py")
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    pop = V1E.population(TEST_LEN)
    train = V1E.take(pop, TRAIN_LEN, TRAIN_SALT, TRAIN_N)
    # Length-5 val/test share a pool; different salts still overlap on top-N.
    # Rank once on VAL_SALT, take val, then rank the remainder on TEST_SALT.
    length5 = [(task, program) for _fp, (minimum, task, program) in pop.items() if minimum == VAL_LEN]
    length5.sort(key=lambda item: (V1E.stable_rank(VAL_SALT, item[0].fingerprint), item[0].fingerprint))
    if len(length5) < VAL_N + TEST_N:
        raise RuntimeError(f"length-{VAL_LEN} pool too small: {len(length5)}")
    val = tuple(length5[:VAL_N])
    remainder = length5[VAL_N:]
    remainder.sort(key=lambda item: (V1E.stable_rank(TEST_SALT, item[0].fingerprint), item[0].fingerprint))
    test = tuple(remainder[:TEST_N])
    train_fp = {t.fingerprint for t, _ in train}
    val_fp = {t.fingerprint for t, _ in val}
    test_fp = {t.fingerprint for t, _ in test}
    if train_fp & val_fp or train_fp & test_fp or val_fp & test_fp:
        raise RuntimeError("stratum overlap")
    train_programs = tuple(p for _, p in train)
    val_tasks = tuple(t for t, _ in val)
    test_tasks = tuple(t for t, _ in test)

    cands, support = V1E.mine(train)
    frequency_selected = cands[0] if cands else None

    primitive = V1E.build_index((), TEST_LEN)
    _, prim_val = V1E.aggregate(val_tasks, primitive)
    _, prim_test = V1E.aggregate(test_tasks, primitive)

    val_scores = []
    for frag in cands:
        idx = V1E.build_index((frag,), TEST_LEN)
        _, att = V1E.aggregate(val_tasks, idx)
        val_scores.append({"fragment": list(frag), "val_attempts": att, "beats_primitive": att < prim_val})

    useful = [row for row in val_scores if row["beats_primitive"]]
    if useful:
        best = min(useful, key=lambda r: (r["val_attempts"], r["fragment"]))
        admitted = tuple(best["fragment"])
    else:
        admitted = ()

    freq_idx = V1E.build_index((frequency_selected,) if frequency_selected else (), TEST_LEN)
    _, freq_val = V1E.aggregate(val_tasks, freq_idx)
    _, freq_test = V1E.aggregate(test_tasks, freq_idx)

    gated_idx = V1E.build_index((admitted,) if admitted else (), TEST_LEN)
    _, gated_test = V1E.aggregate(test_tasks, gated_idx)

    placebo = V1E.placebo_fragment(admitted or frequency_selected or ("inc", "double"))
    _, placebo_test = V1E.aggregate(test_tasks, V1E.build_index((placebo,), TEST_LEN))
    flood = tuple(cands[:CANDIDATE_CAP])
    _, flood_test = V1E.aggregate(test_tasks, V1E.build_index(flood, TEST_LEN))

    frequency_harmful_on_test = freq_test > prim_test
    gated_not_worse = gated_test <= prim_test
    gate_refused_frequency = frequency_selected is not None and admitted != frequency_selected

    if frequency_harmful_on_test and gated_not_worse and (not admitted or admitted != frequency_selected):
        terminal = "HARMFUL_FREQUENCY_REFUSED_BY_UTILITY_GATE"
    elif admitted and gated_test < prim_test:
        terminal = "UTILITY_GATED_LIBRARY_BEATS_PRIMITIVE"
    elif not admitted:
        terminal = "UTILITY_GATE_SELECTS_NO_METHOD"
    else:
        terminal = "UTILITY_GATE_DID_NOT_PREVENT_HARM"

    donors = V1E.donor_ledger(train_programs, admitted or frequency_selected)
    for row in donors:
        if row["donor"] in {"domain-native-induction", "grammar-induction", "conventional-same-library"}:
            row["object"] = admitted
            row["residual"] = "utility-gate-on-disjoint-validation"

    controls = {
        "reset_OCM": {"attempts": prim_test, "equals_primitive": True},
        "persistent_exemplar_memory": {
            "held_out_fingerprint_hits": sum(1 for t in test_tasks if t.fingerprint in train_fp),
            "excluded_as_answer_cache": True,
        },
        "persistent_method_library": {"attempts": gated_test, "selected": list(admitted) if admitted else []},
        "same_library_conventional_search": {"attempts": gated_test, "parent_tied": True},
        "domain_native_synthesis": {"attempts": gated_test, "parent": "methods.py-BFS"},
        "structural_placebo": {
            "fragment": list(placebo),
            "attempts": placebo_test,
            "worse_or_equal_to_gated": placebo_test >= gated_test,
        },
        "method_removed": {"attempts": prim_test, "equals_primitive": True},
        "scope_conflicting_method": {"note": "placebo admitted as if in-scope", "attempts": placebo_test},
        "harmful_transfer": {
            "frequency_library_worse_than_primitive": frequency_harmful_on_test,
            "frequency_delta": freq_test - prim_test,
            "gated_library_worse_than_primitive": gated_test > prim_test,
            "gated_delta": gated_test - prim_test,
        },
        "unrelated_method_growth": {
            "flood_attempts": flood_test,
            "interference": flood_test > gated_test,
            "n_macros": len(flood),
        },
    }

    result = {
        "schema": "ocm.g2.utility-gated-parents.v2",
        "terminal": terminal,
        "v1_frozen": {
            "capsule": "research/g2-strong-parents-v1/",
            "terminal": V1_FROZEN_TERMINAL,
            "frequency_fragment": list(V1_FREQUENCY_FRAGMENT),
            "not_retuned": True,
        },
        "root_cause": (
            "Frequency ranking admits high-support infixes without measuring held-out "
            "search cost. Utility gating requires a disjoint validation win before admission."
        ),
        "methods_blob": blob,
        "salts": {"train": TRAIN_SALT, "val": VAL_SALT, "test": TEST_SALT},
        "train_n": TRAIN_N,
        "val_n": VAL_N,
        "test_n": TEST_N,
        "frequency_selected": list(frequency_selected) if frequency_selected else [],
        "admitted": list(admitted) if admitted else [],
        "gate_refused_frequency": gate_refused_frequency,
        "support": {str(k): v for k, v in support.items()},
        "validation": {
            "primitive_attempts": prim_val,
            "frequency_attempts": freq_val,
            "candidates": val_scores,
        },
        "test": {
            "primitive_attempts": prim_test,
            "frequency_attempts": freq_test,
            "gated_attempts": gated_test,
        },
        "controls": controls,
        "donors": [
            {**d, "object": list(d["object"]) if isinstance(d["object"], tuple) else d["object"]}
            for d in donors
        ],
        "claim_ceiling": (
            "v2 refuses frequency-harmful transfer via validation utility. "
            "Not a new G2.4 positive. Library search remains parent-owned."
        ),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal": terminal,
        "frequency": frequency_selected,
        "admitted": admitted,
        "prim_test": prim_test,
        "freq_test": freq_test,
        "gated_test": gated_test,
    }, default=list))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
