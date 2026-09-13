#!/usr/bin/env python3
"""Replay one pinned crossover; no Git, search, ecology evaluation or network."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def produce(package, source):
    manifest = json.loads((package / "MANIFEST.json").read_text())
    for row in manifest["files"]:
        data = (package / row["path"]).read_bytes()
        require(sha(data) == row["sha256"], "packet binding mismatch: " + row["path"])
    bindings = json.loads((package / "SOURCE_BINDINGS.json").read_text())
    with zipfile.ZipFile(package / "PINNED_SOURCE.zip") as archive:
        require(set(archive.namelist()) == set(bindings["files"]), "source member mismatch")
        for name, expected in bindings["files"].items():
            require(".." not in Path(name).parts and not Path(name).is_absolute(), "unsafe member")
            data = archive.read(name)
            require(sha(data) == expected, "source digest mismatch: " + name)
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(source))
    b1, morph, morphgen, zoo = [
        importlib.import_module("gmi_microscope." + name)
        for name in ("b1", "morph", "morphgen", "zoo")]
    for module in (b1, morph, morphgen, zoo):
        require(Path(module.__file__).resolve().is_relative_to(source), "unexpected module cache")
    class Tape:
        def __init__(self):
            self.values, self.log = iter(("1", ("2", 1))), []
        def choice(self, options):
            selected = next(self.values)
            require(selected in options, "choice tape is not a legal outcome")
            self.log.append({"selected": selected, "option_count": len(options)})
            return selected
    a, b = zoo.exemplar_table(), zoo.constant_emitter()
    before = morph.to_json(a), morph.to_json(b)
    tape, record = Tape(), []
    child, tries = morphgen.crossover(tape, a, b, tries=1, record=record)
    require((morph.to_json(a), morph.to_json(b)) == before, "parent changed")
    require(morph.typecheck(child) and record == [("op_graft_recombine", True)], "graft failed")
    require([b1.carrier_of(g) for g in (a, b, child)] == ["TABLE", "DENSE", "DENSE"],
            "carrier countercontrol failed")
    origins = {id(a): ["seed", 0], id(b): ["seed", 1]}
    origin = origins.get(id(a))  # b1.search's literal primary-parent origin assignment.
    def parent(g):
        return {"carrier": b1.carrier_of(g), "fingerprint": morph.fingerprint(g),
                "genotype": morph.to_json(g), "origin": origins[id(g)]}
    return {
        "schema": "B6PrimaryLineageCrossoverCountercontrolV1",
        "source_commit": bindings["source_commit"],
        "source_sha256": {name: bindings["files"][name] for name in (
            "gmi_microscope/b1.py", "gmi_microscope/morph.py",
            "gmi_microscope/morphgen.py", "gmi_microscope/zoo.py")},
        "primitive_calls": 1, "search_calls": 0, "ecology_calls": 0,
        "admissibility_claim": False, "choice_tape": tape.log,
        "operator_record": record, "tries_returned": tries,
        "primary": parent(a), "secondary": parent(b),
        "child": {"carrier": b1.carrier_of(child), "fingerprint": morph.fingerprint(child),
                  "genotype": morph.to_json(child), "literal_primary_origin": origin},
        "positive_control": "Recorded primary ancestry is present; only secondary ancestry is lost.",
        "claim": "A non-DENSE primary-lineage root does not imply absence of a DENSE donor ancestor."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected", type=Path,
                        help="Alternate expected receipt, used only for the negative control")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    require(not args.output.exists(), "output must be new")
    with tempfile.TemporaryDirectory(prefix="b6-lineage-replay-") as temporary:
        result = produce(package, Path(temporary).resolve())
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    with args.output.open("xb") as handle:
        handle.write(encoded)
    expected = (args.expected or package / "COUNTERCONTROL.json").read_bytes()
    if encoded != expected:
        print("COUNTERCONTROL_MISMATCH: replay differs from expected receipt", file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({"replay": "EXACT_BYTES", "sha256": sha(encoded),
                      "primitive_calls": 1, "search_calls": 0, "ecology_calls": 0}))


if __name__ == "__main__":
    main()
