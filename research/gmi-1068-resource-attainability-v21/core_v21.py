"""Immutable context/transition types and strict finite input contracts."""
import importlib.util
from pathlib import Path
import sys

RESEARCH = Path(__file__).resolve().parents[1]
SOURCE = RESEARCH / "gmi-1068-frontier-simulation-v20/core_v20.py"
NAME = "_gmi_frontier_bridge_v20"
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = module
    spec.loader.exec_module(module)
base = sys.modules[NAME]
if Path(base.__file__).resolve() != SOURCE.resolve():
    raise ValueError("immutable source binding mismatch")
Context, checked, observe = base.Context, base.checked, base.observe
LegacyMachine, legacy, budget_lift = base.LegacyMachine, base.legacy, base.budget_lift
need, nat, index, subset, order = base.need, base.nat, base.index, base.subset, base.order


def machine_checked(machine):
    need(type(machine) is LegacyMachine, "actual validated V8 machine required")
    return machine


def word_checked(machine, start, word):
    machine_checked(machine)
    index(start, len(machine.observations))
    need(type(word) is tuple, "canonical action tuple required")
    for action in word:
        index(action, len(machine.transitions[0]))
    return word


def nat_set(values):
    need(type(values) is tuple, "canonical finite set tuple required")
    for value in values:
        nat(value)
    need(len(set(values)) == len(values), "duplicate set member")
    return values
