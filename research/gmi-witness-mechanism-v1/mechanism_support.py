"""Source-bound, passive observation support for the fixed three-arm ablation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tarfile


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def load_source(witness_unit, output):
    witness_unit, output = Path(witness_unit), Path(output)
    binding = json.loads((witness_unit / "RECOVERY_BINDINGS_V1.json").read_text())
    expected = {r["path"]: r["sha256"] for r in binding["source_files"]}
    with tarfile.open(witness_unit / "HISTORICAL_SOURCE_V1.tar.gz", "r:gz") as archive:
        members = archive.getmembers()
        if len(members) != len(expected) or {m.name for m in members} != set(expected):
            raise ValueError("archive member coverage mismatch")
        for member in members:
            if not member.isfile() or Path(member.name).is_absolute() or ".." in Path(member.name).parts:
                raise ValueError("unsafe or non-regular source member")
            raw = archive.extractfile(member).read()
            if hashlib.sha256(raw).hexdigest() != expected[member.name]:
                raise ValueError("source content binding mismatch")
            target = output / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    sys.path.insert(0, str(output.resolve()))
    from gmi_microscope import b6_development as dev
    if Path(dev.__file__).resolve() != output.resolve() / "gmi_microscope/b6_development.py":
        raise ValueError("wrong imported source")
    if list(dev.ecology.INTERVENTIONS) != binding["registered_interventions"]:
        raise ValueError("intervention bar changed")
    return dev, binding


def observe(ecology, spec, genotype, basis, intervention):
    original_vm, instances = ecology.VM, []

    class ObservedVM(original_vm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.insert_observations = []
            instances.append(self)

        def _update(self, node, kind, params, values, target):
            record = None
            if kind == "INSERT":
                vector = self._in(node, 1, values)
                record = {"node": node, "phase": self.M.L.phase,
                          "key": [int(getattr(v, "v", 0) > 0) for v in vector],
                          "vector_types": [type(v).__name__ for v in vector]}
            result = super()._update(node, kind, params, values, target)
            if record is not None:
                record["stores_after"] = copy.deepcopy(self.M.stores)
                self.insert_observations.append(record)
            return result

    ecology.VM = ObservedVM
    try:
        response = ecology.run_genotype(spec, genotype, basis, intervention)
    finally:
        ecology.VM = original_vm
    if len(instances) != 1:
        raise ValueError("expected exactly one native VM")
    vm = instances[0]; machine = vm.M
    capture = {"order": vm.order, "final_cells": machine.cells, "cell_types": machine.cell_types,
               "final_stores": machine.stores, "final_vm_state": vm.state,
               "initial_dense": vm.initial_dense, "insert_observations": vm.insert_observations,
               "event_write_fracs": machine.L.event_write_fracs,
               "ops_by_kind": dict(machine.L.ops_by_kind), "program_ops": machine.prog_ops}
    return {"native_response": response, "passive_capture": copy.deepcopy(capture)}
