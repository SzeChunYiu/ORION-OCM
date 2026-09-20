"""Strict finite contracts for immutable V8 and V15 specializations."""
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / "gmi-1068-resource-attainability-v21/core_v21.py"
NAME = "_gmi_permission_parent_v21"
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = module
    spec.loader.exec_module(module)
parent = sys.modules[NAME]
if Path(parent.__file__).resolve() != SOURCE.resolve():
    raise ValueError("immutable source binding mismatch")
Context, checked, observe = parent.Context, parent.checked, parent.observe
LegacyMachine, legacy = parent.LegacyMachine, parent.legacy
need, nat, subset, word_checked = parent.need, parent.nat, parent.subset, parent.word_checked


@dataclass(frozen=True)
class PermissionMachine:
    base: LegacyMachine
    permission_count: int
    requirements: tuple

    def __post_init__(self):
        parent.machine_checked(self.base)
        nat(self.permission_count)
        need(type(self.requirements) is tuple, "requirement tuple rows required")
        need(len(self.requirements) == len(self.base.transitions), "state dimension")
        for row, edges in zip(self.requirements, self.base.transitions):
            need(type(row) is tuple and len(row) == len(edges), "action dimension")
            for required, edge in zip(row, edges):
                if edge is None:
                    need(required is None, "absent edge must have None requirements")
                else:
                    subset(required, self.permission_count)


def spec_checked(spec):
    need(type(spec) is PermissionMachine, "validated PermissionMachine required")
    return spec


def permissions(spec, values):
    spec_checked(spec)
    subset(values, spec.permission_count)
    return set(values)


def records_checked(records, permission_count):
    nat(permission_count)
    need(type(records) is tuple, "witness record tuple required")
    ids = []
    for record in records:
        need(type(record) is tuple and len(record) == 2, "witness record pair")
        nat(record[0])
        subset(record[1], permission_count)
        ids.append(record[0])
    need(len(set(ids)) == len(ids), "duplicate witness identity")
    return records
