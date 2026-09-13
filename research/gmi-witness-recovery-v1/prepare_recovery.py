"""Prepare a source-bound retrospective run; never invokes search or VM evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, expected):
    data = Path(path).read_bytes()
    if digest(data) != expected:
        raise ValueError("input binding mismatch: "+str(path))
    return data


def source_bytes(repo, binding):
    result = {}
    for row in binding["source_files"]:
        ref = binding["source_commit"]+":"+binding["source_prefix"]+row["path"]
        data = subprocess.check_output(["/usr/bin/git", "-C", str(repo), "show", ref])
        if digest(data) != row["sha256"]:
            raise ValueError("historical source mismatch: "+row["path"])
        result[row["path"]] = data
    return result


def prepare(repo, packet, output):
    binding_path = Path(__file__).with_name("RECOVERY_BINDINGS_V1.json")
    binding = json.loads(binding_path.read_text())
    sources = source_bytes(repo, binding)
    raw = [checked(Path(packet)/row["path"], row["sha256"]) for row in binding["input_files"]]
    arm, source = map(json.loads, raw)
    cells = {row["fingerprint"]: row for row in source["cells"].values()}
    seeds = [cells[fp] for fp in arm["seeding"]["seed_fingerprints"]]
    if len(seeds) != 61 or [s["capability"] for s in seeds] != arm["seeding"]["seed_source_capabilities"]:
        raise ValueError("recorded seed population does not match source receipt")
    if source["receipt_sha256"] != arm["seeding"]["source_receipt_sha256"]:
        raise ValueError("source receipt reference mismatch")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in sources.items():
        path = output/"source"/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (output/"historical_arm.json").write_bytes(raw[0])
    (output/"historical_source.json").write_bytes(raw[1])
    population = (json.dumps(seeds, sort_keys=True, indent=2)+"\n").encode()
    (output/"seed_population.json").write_bytes(population)
    (output/"RECOVERY_BINDINGS_V1.json").write_bytes(binding_path.read_bytes())
    result = {"schema": "B6WitnessRecoveryPreparationV1", "source_files_verified": len(sources),
              "input_files_verified": len(raw), "ordered_seed_count": len(seeds),
              "seed_population_sha256": digest(population), "binding_sha256": digest(binding_path.read_bytes()),
              "search_launched": False, "historical_execution_identity_proven": False}
    (output/"PREPARATION.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    return result


def validate_prepared(path):
    path = Path(path)
    prep = json.loads((path/"PREPARATION.json").read_text())
    binding = json.loads(checked(path/"RECOVERY_BINDINGS_V1.json", prep["binding_sha256"]))
    for row in binding["source_files"]:
        checked(path/"source"/row["path"], row["sha256"])
    checked(path/"seed_population.json", prep["seed_population_sha256"])
    for name, row in zip(("historical_arm.json", "historical_source.json"), binding["input_files"]):
        checked(path/name, row["sha256"])
    return binding


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.repository, args.packet, args.output), indent=2, sort_keys=True))
