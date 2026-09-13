"""Predeclared, exposed native acquisition/typed-removal/restoration controls."""
import copy
from call_capture_v1 import Charges
from checkpoint_v1 import checkpoint, digest, graph, require_program, substitute

EXPERIENCE = ((1, 16), (2, 0))


def acquire(native, experience=EXPERIENCE):
    machine = native.core.Machine(copy.deepcopy(native.bases.B0), seed=0)
    vm = native.vm.VM(native.zoo.program_search(grammar=1, budget=32), machine, seed=0)
    machine.phase("exec")
    events = []
    machine.L.c = Charges(machine.L.c, events)
    try:
        vm.init()
    finally:
        machine.L.c = dict(machine.L.c)
    history = [{"stage": "initialized", "native_charge_events": events, "native_ledger": dict(machine.L.c),
                "state": graph(vm, native)[0]}]
    for x, y in experience:
        machine.phase("upd")
        events = []
        machine.L.c = Charges(machine.L.c, events)
        try:
            vm.feedback(x, y)
            machine.end_event()
        finally:
            machine.L.c = dict(machine.L.c)
        history.append({"stage": "feedback", "input": x, "target": y,
                        "native_charge_events": events, "native_ledger": dict(machine.L.c),
                        "state": graph(vm, native)[0]})
    return vm, history


def serve(vm, native):
    require_program(vm, native)
    node = require_program(vm, native)
    body, stores = vm.state[node], copy.deepcopy(vm.M.stores)
    before = dict(vm.M.L.c)
    outputs = []
    vm.M.phase("exec")
    for x in range(16):
        start = dict(vm.M.L.c)
        value = vm.query(x)
        outputs.append({"x": x, "value": value, "abstained": vm.abstained,
                        "native_charge": {k: vm.M.L.c[k] - start[k] for k in start}})
    if vm.state[node] != body or vm.M.stores != stores:
        raise ValueError("query altered acquired program/evidence")
    return {"outputs": outputs, "program": list(body),
            "native_serving_delta": {k: vm.M.L.c[k] - before[k] for k in before},
            "final_state": graph(vm, native)[0], "final_state_sha256": digest(vm, native)}


def run(native):
    acquired, history = acquire(native)
    node = require_program(acquired, native)
    body = acquired.state[node]
    if body != (1, 0):
        raise ValueError("predeclared experience no longer selects the source-predicted body")
    baseline = digest(acquired, native)
    arms = {}
    for label in ("acquired", "initial_body", "sham", "restored"):
        vm = checkpoint(acquired, native)
        start = digest(vm, native)
        changes = []
        if label in ("initial_body", "restored"):
            changes.append(substitute(vm, vm.grammars[node].initial(), native))
        if label in ("sham", "restored"):
            changes.append(substitute(vm, body, native))
        if label in ("acquired", "sham", "restored") and digest(vm, native) != baseline:
            raise ValueError("restored/sham pre-query state differs")
        arms[label] = {"cloned_start_sha256": start, "assignments": changes,
                       "post_assignment_sha256": digest(vm, native), "served": serve(vm, native)}
    if digest(acquired, native) != baseline:
        raise ValueError("arm execution mutated checkpoint parent")
    reference = arms["acquired"]["served"]
    for label in ("sham", "restored"):
        if arms[label]["served"] != reference:
            raise ValueError("restoration/sham not exactly equal")
    disabled_values = [x["value"] for x in arms["initial_body"]["served"]["outputs"]]
    acquired_values = [x["value"] for x in reference["outputs"]]
    changed = [x for x in range(16) if disabled_values[x] != acquired_values[x]]
    if changed != list(range(1, 16, 2)):
        raise ValueError("initial-body answer control did not discriminate on odd inputs")
    control, control_history = acquire(native, ((1, 0), (2, 0)))
    experience_control = serve(control, native)
    return {"experience": [list(x) for x in EXPERIENCE], "acquisition_history": history,
            "checkpoint_sha256": baseline, "changed_answer_inputs": changed, "acquisition_ledger": dict(acquired.M.L.c),
            "arms": arms, "same_input_zero_label_control": {
                "history": control_history, "served": experience_control},
            "external_control_operations": {"joint_checkpoints": 4, "typed_body_assignments": 4,
                                            "host_and_physical_work": "UNMEASURED"},
            "scope": "exposed finite-grammar state use; no new method or protected transfer"}
