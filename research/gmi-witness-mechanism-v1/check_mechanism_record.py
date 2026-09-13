"""Read-only verification of the fixed ablation record; executes zero ecology calls."""
import gzip
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(record, prior):
    arms = {"original", "zero_vector", "variable_key"}
    controls = {"standard", "no_revoke", "double_revoke", "half_events", "shuffled_events", "extra_unseen_feedback"}
    probes = {"E_smooth1", "E_smooth3", "E_sym3", "E_sym5", "E_wit1"}
    contexts = {"control:" + x for x in controls} | {"probe:" + x for x in probes}
    require(record["calls"] == 33 and set(record["outcomes"]) == arms, "call/arm coverage")
    baseline = prior["versions"]["atrophied"]
    require(record["graphs"]["original"]["fingerprint"] == baseline["fingerprint"], "baseline identity")
    for arm in arms:
        rows = record["outcomes"][arm]
        require(set(rows) == contexts, "context coverage")
        for name, row in rows.items():
            require(row["error"] is None, "evaluation exception")
            native = row["native_response"]; capture = row["passive_capture"]
            original = record["outcomes"]["original"][name]
            if arm == "original":
                family, context = name.split(":")
                require(native == baseline["controls" if family == "control" else "probes"][context], "clean baseline drift")
            if arm == "zero_vector":
                require(native["trace"] == original["native_response"]["trace"], "zero trace drift")
                require(native["capability"] == original["native_response"]["capability"], "zero capability drift")
                require(capture["final_stores"] == original["passive_capture"]["final_stores"], "zero final store drift")
                old = original["passive_capture"]["insert_observations"]
                current = capture["insert_observations"]
                require(len(current) == len(old), "insert count drift")
                for a, b in zip(current, old):
                    require(all(a[k] == b[k] for k in ("node", "phase", "key", "stores_after")), "intermediate store drift")
            if arm == "variable_key":
                require(native["trace"] != original["native_response"]["trace"], "varying control is inert")
            if arm != "original":
                require(capture["final_cells"] == {} and native["init_audit"]["dense_cells"] == 0, "dense cell remains")
            keys = {tuple(obs["key"]) for obs in capture["insert_observations"] if obs["node"] == "insert1"}
            require(keys == ({(0,), (1,)} if arm == "variable_key" else {(0,)}), "key control failed")
        caps = [rows["control:" + name]["native_response"]["capability"] for name in controls]
        answer_vectors = {tuple(rows["probe:" + name]["native_response"]["trace"][-1]) for name in probes}
        require(min(caps) >= .85 and (min(caps) - .8125) * 24 >= 1, "historical capability/margin failed")
        require(len(answer_vectors) == 5, "probe diversity failed")
    for coord in ("exec", "upd", "rev", "ver"):
        original = record["outcomes"]["original"]["control:standard"]["native_response"]
        zero = record["outcomes"]["zero_vector"]["control:standard"]["native_response"]
        require(zero["R"][coord] > original["R"][coord], "measured cost tradeoff changed")
    return {"verified": True, "ecology_calls_executed_by_checker": 0, "retained_ecology_calls": 33,
            "baseline_full_matches": 11, "zero_full_trace_matches": 11, "variable_trace_differences": 11}


def main():
    unit = Path(__file__).resolve().parent
    registration = json.loads((unit / "REGISTRATION_V1.json").read_text())
    witness = unit.parent / "gmi-witness-recovery-v1"
    for root, bindings in ((unit, registration["unit_bindings"]), (witness, registration["witness_bindings"])):
        for name, expected in bindings.items():
            require(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, "registered binding drift")
    record = json.loads(gzip.decompress((unit / "evidence/RECEIPT_V1.json.gz").read_bytes()))
    prior = json.loads((witness / "evidence/s1-recovery-20260913/INDEPENDENT_VERIFICATION_V1.json").read_text())
    require(record["registration_sha256"] == hashlib.sha256((unit / "REGISTRATION_V1.json").read_bytes()).hexdigest(), "receipt registration")
    print(json.dumps(check(record, prior), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
