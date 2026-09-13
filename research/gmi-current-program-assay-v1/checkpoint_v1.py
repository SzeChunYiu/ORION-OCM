"""Joint in-memory checkpoint of the exact, quiescent, exposed PROGRAM apparatus."""
from collections import defaultdict
import copy
import hashlib
import json
import math

FIELDS = {
    "VM": "M abstained audit_initial_state clabel evidence_nodes g grammars initial_dense inputs "
          "kinds_by_class n_prog_ops nodes order output rng_seed state update_nodes",
    "Machine": "L basis cell_types cells lfsr prog_ops stores tape",
    "Ledger": "c emulated_ops event_write_fracs native_ops ops_by_kind phase writes_in_event",
    "ProgramGrammar": "gid progs width",
    "Basis": "_desc cost desc_per_op desc_store_entry desc_store_header name native note write_cost",
}


def graph(vm, native):
    """Encode the entire allowed graph, including references, types and mutable identities."""
    classes = {native.vm.VM: "VM", native.core.Machine: "Machine",
               native.core.Ledger: "Ledger", native.vm.ProgramGrammar: "ProgramGrammar",
               native.bases.Basis: "Basis"}
    seen, mutable = {}, set()

    def encode(obj):
        typ = type(obj)
        if obj is None or typ in (bool, int, str):
            return [typ.__name__, obj]
        if typ is float:
            if not math.isfinite(obj):
                raise ValueError("nonfinite state")
            return ["float", obj.hex()]
        if typ not in (dict, list, tuple, set, defaultdict) and typ not in classes:
            raise ValueError("unregistered state type (including observer/callback/subclass)")
        if id(obj) in seen:
            return ["ref", seen[id(obj)]]
        index = len(seen)
        seen[id(obj)] = index
        if typ is not tuple:
            mutable.add(id(obj))
        if typ in classes:
            label = classes[typ]
            if set(vars(obj)) != set(FIELDS[label].split()):
                raise ValueError("unregistered fields in " + label)
            payload = [[key, encode(value)] for key, value in sorted(vars(obj).items())]
        elif typ in (dict, defaultdict):
            label = typ.__name__
            if typ is defaultdict and obj.default_factory is not int:
                raise ValueError("unregistered default factory")
            payload = [[encode(k), encode(v)] for k, v in sorted(obj.items(), key=lambda x: repr(x[0]))]
        else:
            label = typ.__name__
            payload = [encode(x) for x in (sorted(obj, key=repr) if typ is set else obj)]
        return [label, index, payload]

    encoded = encode(vm)
    return encoded, mutable


def require_program(vm, native):
    if type(vm) is not native.vm.VM or type(vm.M) is not native.core.Machine:
        raise ValueError("exact native VM/Machine required")
    if vm.M.tape is not None or vm.M.L.writes_in_event:
        raise ValueError("checkpoint requires completed event and quiescent tape")
    programs = [k for k, (kind, _) in vm.nodes.items() if kind == "PROGRAM"]
    searches = [p for kind, p in vm.nodes.values() if kind == "SEARCH"]
    if len(programs) != 1 or len(searches) != 1:
        raise ValueError("one explicit PROGRAM/SEARCH template required")
    node = programs[0]
    grammar = vm.nodes[node][1]["grammar"]
    budget = searches[0]["budget"]
    if vm.g != native.zoo.program_search(budget=budget, grammar=grammar):
        raise ValueError("only exact exposed program_search; no materialized/cache bypass")
    if vm.nodes is not vm.g["nodes"] or vm.grammars[node].gid != grammar:
        raise ValueError("broken graph/state links")
    gr = vm.grammars[node]
    if gr.width != 4 or gr.progs != native.vm.ProgramGrammar(grammar).progs:
        raise ValueError("altered grammar")
    if type(vm.state[node]) is not tuple or any(type(x) is not int for x in vm.state[node]):
        raise ValueError("untyped program body")
    if vm.state[node] not in gr.progs:
        raise ValueError("body outside registered grammar")
    graph(vm, native)
    return node


def checkpoint(vm, native):
    require_program(vm, native)
    before, original_ids = graph(vm, native)
    clone = copy.deepcopy(vm)
    require_program(clone, native)
    after, copied_ids = graph(clone, native)
    if before != after or original_ids & copied_ids:
        raise ValueError("joint graph/alias-preservation failure")
    return clone


def digest(vm, native):
    encoded, _ = graph(vm, native)
    return hashlib.sha256(json.dumps(encoded, separators=(",", ":")).encode()).hexdigest()


def substitute(vm, body, native):
    """External typed experimental assignment; no native/physical zero-cost claim."""
    node = require_program(vm, native)
    if type(body) is not tuple or any(type(x) is not int for x in body):
        raise ValueError("body must be exact integer tuple")
    if body not in vm.grammars[node].progs:
        raise ValueError("body outside grammar")
    before = digest(vm, native)
    vm.state[node] = body
    return {"operation": "external_PROGRAM_assignment", "node": node, "body": list(body),
            "serialized_body_bytes": len(json.dumps(body).encode()),
            "before": before, "after": digest(vm, native),
            "host_and_physical_cost": "UNMEASURED; no native setter is claimed"}
