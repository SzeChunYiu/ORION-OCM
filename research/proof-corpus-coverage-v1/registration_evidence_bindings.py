"""Bind current registrar sources and explicitly identify the four external inputs."""
from pathlib import Path, PurePosixPath
from registration_evidence_archive import checked_file, decode, identity, require

MAPPING = {name: "proof-corpus-coverage-v1/" + name + ".py" for name in
           ["coverage_boot", "coverage_git", "coverage_policy", "coverage_population", "coverage_register", "register"]}
MAPPING.update({name: "proof-corpus-v1/" + name + ".py" for name in ["corpus_contract", "corpus_git", "corpus_tree"]})
MAPPING["env_inputs"] = "proof-environment-v1/env_inputs.py"
DOCS = ["F1-CORPUS-COVERAGE-DESIGN.md", "F1-CORPUS-COVERAGE-EXECUTION.md"]
INPUTS = {"CORPUS_SOURCE.json", "GRAPH.json", "SOLUTIONS.json", "WRAPPERS.json"}
PRIOR = {"sha256": "c1177f5a3725b21d91f74a52faf6c98839800052ababa254cc173bff154d27fb", "bytes": 61338019}


def digest_record(record):
    return {k: record[k] for k in ("sha256", "bytes")}


def checked_source(path, expected, research_root):
    require(Path(path).resolve().is_relative_to(Path(research_root).resolve()), "current source escapes research tree")
    return checked_file(path, expected)


def verify_source_bindings(files, package):
    source = decode(files["SOURCE-FREEZE.json"])
    require(set(source["loaded_sources"]) == set(MAPPING), "loaded source keyset differs")
    require(set(source["documents"]) == set(DOCS), "document keyset differs")
    expected = set(MAPPING) | {"document_" + n for n in DOCS}
    require(set(source["snapshots"]) == expected, "source snapshot keyset differs")
    for key in sorted(expected):
        if key in MAPPING:
            rel = MAPPING[key]; record = source["loaded_sources"][key]
            path = Path(package).parent / rel
        else:
            name = key.removeprefix("document_"); record = source["documents"][name]
            rel = "proof-corpus-coverage-v1/" + name; path = Path(package) / name
        require(record["path"].endswith("/research/" + rel), "registered source path differs")
        wanted = digest_record(record)
        require(digest_record(source["snapshots"][key]) == wanted, "source snapshot identity differs")
        require(identity(files["sources/" + path.name]) == wanted, "archived source bytes differ")
        checked_source(path, wanted, Path(package).parent)
    return len(expected)


def verify_omissions(files, omitted, expected_seal_sha):
    require(identity(files["SEAL.json"])["sha256"] == expected_seal_sha, "original seal identity differs")
    seal = decode(files["SEAL.json"])
    require(seal["schema"] == "ocm.f1.registration-seal.v1" and seal["state"] == "REGISTERED_NO_DISPATCH", "original seal state")
    expected = {"inputs/" + n for n in INPUTS}
    require(omitted["schema"] == "ocm.f1.registration-omissions.v1" and set(omitted["files"]) == expected, "omission keyset differs")
    require(set(files) == (set(seal["files"]) - expected) | {"SEAL.json"}, "derived archive membership differs")
    for name, raw in files.items():
        if name != "SEAL.json": require(identity(raw) == seal["files"][name], "derived member differs from original seal")
    require(digest_record(omitted["prior_archive"]) == PRIOR, "external prior archive identity differs")
    source = decode(files["SOURCE-FREEZE.json"])
    require(set(source["inputs"]) == INPUTS and set(source["input_snapshots"]) == INPUTS, "frozen input keyset differs")
    for rel, item in omitted["files"].items():
        name = PurePosixPath(rel).name; registered = source["inputs"][name]; snapshot = source["input_snapshots"][name]
        require(digest_record(item) == seal["files"][rel] == digest_record(registered) == digest_record(snapshot), "omitted input identity differs")
        require(item["original"] == registered["path"] and item["sealed_copy"] == snapshot["path"], "omitted input custody pointers differ")
        require(item["sealed_copy"] == omitted["original_root"] + "/" + rel, "omitted snapshot root differs")
        require(PurePosixPath(item["prior_archive_member"]).name == name, "prior archive member name differs")
    return len(expected)
