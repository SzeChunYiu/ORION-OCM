"""R3 — ecology DSL: declarative ecology specifications e = (O, Xi_obl, P, J, H_dev, C_eval) over the registered exact
protocols, and the intervention registry J used by the species-equivalence harness (R2/R9).

An ecology spec is a small dict; run_genotype(spec, genotype, basis, intervention) executes the protocol on the charged
Machine and returns the developmental RESPONSE: the full served trace (every query answer after every event), the final
capability under the spec's criterion, the ledger, and the lifecycle vector. Two genotypes are exactly equivalent on (E, J)
iff their responses are identical on every (e, j) (GMI_BIOSPHERE_SPECIES_EQUIVALENCE_HARDENING_V1 section 2; rho_M excluded
and reported separately).

Families: "smooth" (D'/E' linear-target ecology with revocation; targets by coefficient vector or explicit table),
"parity" (balanced-parity target), "xor" (XOR-linear target). Interventions: "standard" (the registered protocol),
"no_revoke", "double_revoke", "half_events", "shuffled_events" (a fixed alternative order), "extra_unseen_feedback".
Every spec and intervention is frozen text; the protected split manager (R7) hashes them.
"""
from __future__ import annotations

import json

from . import bases, smooth
from .core import Machine, clamp, sha256_of
from .vm import VM, lifecycle_vector

INTERVENTIONS = {"standard": {}, "no_revoke": {"revoke": False}, "double_revoke": {"revoke": "double"}, "half_events": {"n_events": 8},
                 "shuffled_events": {"order": [5, 0, 7, 2, 6, 1, 4, 3]}, "extra_unseen_feedback": {"extra": True}}


def spec_smooth(coeffs, name=None, n_events=16, criterion="unseen"):
    return {"family": "smooth", "coeffs": list(coeffs), "n_events": n_events, "criterion": criterion, "theta": 0.85, "name": name or f"E_smooth{coeffs}"}


def spec_table(table, name, n_events=16, criterion="unseen"):
    return {"family": "table", "table": [int(v) for v in table], "n_events": n_events, "criterion": criterion, "theta": 0.85, "name": name}


# RV-377-103: E_wit1 is the witness-bearing DISCRIMINATING ecology established by RV-377-102's complete enumeration.
# It is registered here, before the recovery run, because G15 step two has never been asked on an ecology where the
# thing being looked for demonstrably exists. Facts from STAGE_ECO_V32_ECO_AXIS.json, not from this run:
#   best constant 0.7083 (DISCRIMINATING, theta 0.85); gradient_net(3,1) scores 0.8646 under ALL SIX interventions;
#   margin 3.751 fx units of mean absolute error -- nearly four quantization steps.
# Every previous coefficient-recovery trial was held on an ecology with either no witness (E_smooth3, E_sym5), a
# standard-intervention-only witness (E_smooth1, E_parity), or a non-discriminating threshold (E_sym3).
WITNESS_COEFFS_V1 = (-0.5, -0.5, -0.5, -0.25)

# RV-377-140: the four FRESH ecologies of the class-rate morphology law, chosen by the deterministic coverage walk of
# gmi_microscope/class_rate.select_fresh over RV-377-102's discriminating enumeration (receipt
# STAGE_CLASSRATE_SELECTION_V43_CLASSRATE_SELECT.json, sha 0156dc16...). Registered BEFORE any search on them. Their
# closed forms (from that receipt): E_cr1 best constant 0.6667, memory closed form 0.8333 (< theta), witness-free;
# E_cr2 0.7292 / 0.8646 (within one fx unit of theta), witness-bearing; E_cr3 0.7917 / 0.8958, witness-bearing;
# E_cr4 0.8125 / 0.9062, witness-free. None of these had ever been B1-searched.
CLASS_RATE_COEFFS_V1 = {"E_cr1": (-0.5, -0.5, -0.5, -0.5), "E_cr2": (-0.5, -0.5, -0.5, -0.125),
                        "E_cr3": (-0.5, -0.5, -0.5, 0.25), "E_cr4": (-0.5, -0.5, -0.5, 0.375)}

REGISTRY = {"E_wit1": spec_smooth(WITNESS_COEFFS_V1, "E_wit1"),
            **{n: spec_smooth(c, n) for n, c in CLASS_RATE_COEFFS_V1.items()}, "E_smooth3": spec_smooth(smooth.COEFFS_V3, "E_smooth3"), "E_sym3": spec_smooth((3 / 16,) * 4, "E_sym3"), "E_sym5": spec_smooth((5 / 16,) * 4, "E_sym5"),
            "E_parity": spec_table(smooth.make_parity_target(), "E_parity"), "E_smooth1": spec_smooth(smooth.COEFFS_V1, "E_smooth1")}


def spec_id(spec):
    return sha256_of(spec)[:16]


def target_of(spec):
    if spec["family"] == "smooth": return smooth.make_target(tuple(spec["coeffs"]))
    if spec["family"] == "table": return {x: v for x, v in enumerate(spec["table"])} if isinstance(spec["table"], list) else spec["table"]
    raise ValueError(spec["family"])


def run_genotype(spec, genotype, basis, intervention="standard", seed=0):
    """execute the registered protocol under the intervention; return the exact developmental response."""
    J = INTERVENTIONS[intervention]; target = target_of(spec); n_events = J.get("n_events", spec["n_events"])
    train = list(smooth.TRAIN); order = J.get("order")
    if order: train = [train[i] for i in order]
    revoke_at = n_events // 2 + 1 if n_events != smooth.H else smooth.REVOKE_AT
    M = Machine(basis, seed=seed); vm = VM(genotype, M, seed)
    M.phase("exec"); vm.init(); trace = []; abst = 0; nq = 0
    for t in range(1, n_events + 1):
        x = train[(t - 1) % len(train)]; y = target[x]
        M.phase("exec"); row = []
        for xx in smooth.ALL_X:
            v = vm.query(xx); row.append(None if vm.abstained else v); nq += 1; abst += vm.abstained
        trace.append(row)
        M.phase("upd"); vm.feedback(x, y); M.end_event()
        M.phase("ver")
        for xx in smooth.ALL_X: M.op("EQ", vm.query(xx), target[xx])
        if J.get("revoke", True) and t == revoke_at:
            M.phase("rev"); vm.revoke(train[1]); M.end_event()
            if J.get("revoke") == "double": vm.revoke(train[2]); M.end_event()
    if J.get("extra"):
        for xx in smooth.UNSEEN[:4]:
            M.phase("upd"); vm.feedback(xx, target[xx]); M.end_event()
    M.phase("exec"); final = []
    for xx in smooth.ALL_X:
        v = vm.query(xx); final.append(None if vm.abstained else v); nq += 1
    trace.append(final)
    eval_x = smooth.UNSEEN if spec["criterion"] == "unseen" else smooth.ALL_X
    err = sum(abs((final[xx] if final[xx] is not None else 0) - target[xx]) for xx in eval_x) / smooth.FX_ONE / len(eval_x)
    cap = round(max(0.0, 1 - err / 1.5), 4)
    return {"spec": spec["name"], "spec_id": spec_id(spec), "intervention": intervention, "basis": basis.name, "trace": trace, "capability": cap, "admissible": cap >= spec["theta"],
            "R": dict(M.L.c), "lifecycle": lifecycle_vector(M, n_events, nq, abstentions=abst), "init_audit": vm.audit_initial_state}


def response_signature(resp):
    """the exact semantic/developmental part of a response (rho_M excluded): served trace and capability."""
    return sha256_of({"trace": resp["trace"], "capability": resp["capability"]})
