"""Passive, scoped capture of every native ledger write and exposed VM call, including failure."""
import copy

V2 = ("standard", "no_revoke", "double_revoke", "half_events",
      "shuffled_events", "extra_unseen_feedback_v2")


class InjectedFailure(RuntimeError):
    pass


class Charges(dict):
    def __init__(self, initial, events, fail_at=None):
        super().__init__(initial)
        self.events, self.fail_at = events, fail_at

    def __setitem__(self, key, value):
        before = self[key]
        super().__setitem__(key, value)
        self.events.append({"coordinate": key, "before": before, "after": value})
        if self.fail_at == len(self.events):
            raise InjectedFailure("predeclared interruption after ledger write")


def validate_charges(record):
    running = dict.fromkeys(record["final_ledger"], 0)
    for event in record["charge_events"]:
        key = event["coordinate"]
        if key not in running or running[key] != event["before"] or event["after"] < event["before"]:
            raise ValueError("nonconserving native charge trace")
        running[key] = event["after"]
    if running != record["final_ledger"]:
        raise ValueError("missing incurred charge")
    return True


def capture(native, spec, genotype, intervention, fail_at=None):
    """Runs exactly one parent ecology call; observer is never used for checkpoints."""
    ecology = native.ecology
    if intervention not in V2 or tuple(ecology.INTERVENTION_FAMILY_V2) != V2:
        raise ValueError("explicit V2 intervention required")
    charges, calls, machines, vms = [], [], [], []
    original_machine, original_vm = ecology.Machine, ecology.VM

    def machine_factory(*args, **kwargs):
        machine = native.core.Machine(*args, **kwargs)
        machines.append(machine)
        machine.L.c = Charges(machine.L.c, charges, fail_at)
        return machine

    def observe(method):
        def wrapped(self, *args, **kwargs):
            call = {"method": method, "args": list(args), "charge_start": len(charges)}
            calls.append(call)
            try:
                result = getattr(native.vm.VM, method)(self, *args, **kwargs)
                call.update(status="RETURNED", result=copy.deepcopy(result))
                if method == "query":
                    call["abstained"] = self.abstained
                return result
            except Exception as exc:
                call.update(status="ERROR", error={"type": type(exc).__name__, "message": str(exc)})
                raise
            finally:
                call["charge_end"] = len(charges)
        return wrapped

    observed = type("ObservedVM", (native.vm.VM,),
                    {method: observe(method) for method in ("init", "query", "feedback", "revoke")})

    def vm_factory(*args, **kwargs):
        instance = observed(*args, **kwargs)
        vms.append(instance)
        return instance

    record = {"intervention": intervention, "status": "ERROR", "response": None,
              "error": None, "fault_injection_after_charge": fail_at,
              "charge_events": charges, "calls": calls}
    ecology.Machine, ecology.VM = machine_factory, vm_factory
    try:
        response = ecology.run_genotype(spec, genotype, native.bases.B0, intervention)
        record["response"] = response
        final = response["trace"][-1]
        complete = len(final) == 16 and all(type(v) is int for v in final)
        record["status"] = "ANSWER" if complete else "INCOMPLETE"
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        ecology.Machine, ecology.VM = original_machine, original_vm
    if len(machines) != 1:
        raise ValueError("unregistered machine multiplicity")
    machine = machines[0]
    record.update(final_ledger=dict(machine.L.c), native_ops=machine.L.native_ops,
                  emulated_ops=machine.L.emulated_ops, ops_by_kind=dict(machine.L.ops_by_kind),
                  final_machine_state={"cells": copy.deepcopy(machine.cells),
                                       "stores": copy.deepcopy(machine.stores),
                                       "lfsr": machine.lfsr, "tape_quiescent": machine.tape is None},
                  final_program_state=copy.deepcopy(vms[0].state) if vms else None)
    validate_charges(record)
    return record


def summarize(records, family):
    if tuple(family) != V2 or len(records) != len(V2):
        raise ValueError("exact ordered six-member V2 family required")
    if [r["intervention"] for r in records] != list(V2):
        raise ValueError("missing, duplicate or reordered intervention")
    for row in records:
        validate_charges(row)
        if row["status"] not in ("ANSWER", "INCOMPLETE", "ERROR"):
            raise ValueError("unknown response status")
        if row["status"] == "ANSWER":
            response = row["response"]
            final = response["trace"][-1]
            if row["error"] is not None or len(final) != 16 or any(type(x) is not int for x in final):
                raise ValueError("malformed claimed answer")
            if response["R"] != row["final_ledger"]:
                raise ValueError("returned resource ledger differs")
    complete = all(row["status"] == "ANSWER" and row["error"] is None for row in records)
    answers = {tuple(row["response"]["trace"][-1]) for row in records
               if row["status"] == "ANSWER" and row["error"] is None}
    return {"status": "COMPLETE_EXPOSED_ASSAY" if complete else "UNRESOLVED_INCOMPLETE",
            "distinct_answer_vectors": len(answers),
            "all_calls_retained": len(records),
            "family": list(V2), "architecture_or_learning_verdict": "NOT_ASSESSED"}
