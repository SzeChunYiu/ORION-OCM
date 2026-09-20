#!/usr/bin/env python3
"""Recompute exact witnesses; --write records them, default verifies the receipt."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    """Keep evidence checks active under optimized Python execution."""
    if not condition:
        raise AssertionError(message)


def load_sibling(filename, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


model = load_sibling("control_model_v2.py", "r11_control_model_v2")
oracle = load_sibling("independent_oracle_v2.py", "r11_independent_oracle_v2")
fixture, noncollapse_fixture, optimal_value = model.fixture, model.noncollapse_fixture, model.optimal_value
policy_value, residuals, validate = model.policy_value, model.residuals, model.validate
conditional_bit_rewards, enumerate_return = oracle.conditional_bit_rewards, oracle.enumerate_return
finite_horizon_value, trace_law = oracle.finite_horizon_value, oracle.trace_law

REGISTRY = ROOT.parent / "gmi-1068-r12-ai-findings-registry-v1/AI_FINDING_REGISTRY_V1.json"
STATUS = {
    "DERIVED_AT_REGISTERED_SCOPE": "FINITE_PROXY_ONLY_REOPENED",
    "CONDITIONALLY_EXPLAINED": "CONDITIONAL_EXPLANATION_NEEDS_EXPLICIT_DERIVATION",
    "ACCOMMODATED_NOT_DERIVED": "ACCOMMODATED_NOT_DERIVED",
    "EMPIRICAL_LAW_NOT_DERIVED": "SOURCE_EMPIRICAL_NOT_GMI_DERIVED",
    "PARENT_OWNED_LIMIT": "PARENT_IMPORT_REQUIRES_ASSUMPTION_MATCH",
    "PROSPECTIVELY_PREDICTED": "PROSPECTIVE_CUSTODY_NOT_VERIFIED",
    "UNRESOLVED": "UNRESOLVED",
}


def reject(function, label):
    try:
        function()
    except (AssertionError, ValueError):
        return label
    raise AssertionError("hostile accepted: " + label)


def audit_registry(audit, original):
    rows = audit["rows"]
    require(len(rows) == 52 and len({r["id"] for r in rows}) == 52, "check failed: len(rows) == 52 and len({r['id'] for r in rows}) == 52")
    require(audit["programme_completeness"] is False and audit["inherited_green_used"] is False, "check failed: audit['programme_completeness'] is False and audit['inherited_green_used'] is False")
    require(audit["original_registry_sha256"] == hashlib.sha256(REGISTRY.read_bytes()).hexdigest(), "check failed: audit['original_registry_sha256'] == hashlib.sha256(REGISTRY.read_bytes()).hexdigest()")
    by_id = {r["id"]: r for r in original["rows"]}
    require(set(by_id) == {r["id"] for r in rows}, "check failed: set(by_id) == {r['id'] for r in rows}")
    for row in rows:
        old = by_id[row["id"]]
        require(row["finding"] == old["finding"] and row["source_id"] == old["source_id"], "check failed: row['finding'] == old['finding'] and row['source_id'] == old['source_id']")
        require(row["original_verdict"] == old["verdict"], "check failed: row['original_verdict'] == old['verdict']")
        require(row["original_boundary"] == old["boundary"], "check failed: row['original_boundary'] == old['boundary']")
        require(row["successor_status"] == STATUS[old["verdict"]], "check failed: row['successor_status'] == STATUS[old['verdict']]")
        require(row["programme_round_earned"] is False and row["gmi_derivation_certified"] is False, "check failed: row['programme_round_earned'] is False and row['gmi_derivation_certified'] is False")
        require(row["source_finding_rejected"] is False, "check failed: row['source_finding_rejected'] is False")
        require(len(row["needed_evidence"]) >= 60, "check failed: len(row['needed_evidence']) >= 60")
        require(row["original_missing_evidence_fields"], "check failed: row['original_missing_evidence_fields']")
        require(all(key not in old for key in row["original_missing_evidence_fields"]), "check failed: all((key not in old for key in row['original_missing_evidence_fields']))")
    return dict(sorted(Counter(r["successor_status"] for r in rows).items()))


def malformed_model_controls():
    """Run in a child interpreter so -O really exercises each model check."""
    ground, abstract, phi = fixture()
    rejected = []
    for discount in (F(-1, 2), F(1), F(3, 2)):
        malformed = list(ground)
        malformed[4] = discount
        rejected.append(reject(lambda: validate(tuple(malformed)), "GAMMA_" + str(discount)))
    malformed = list(ground)
    malformed[2] = tuple(tuple((F(0),) * 4 for _ in range(2)) for _ in range(4))
    rejected.append(reject(lambda: validate(tuple(malformed)), "NON_NORMALIZED_KERNEL"))
    malformed[2] = tuple(tuple((F(-1), F(2), F(0), F(0)) for _ in range(2)) for _ in range(4))
    rejected.append(reject(lambda: validate(tuple(malformed)), "NEGATIVE_TRANSITION_PROBABILITY"))
    one_action = list(abstract)
    one_action[1] = 1
    one_action[2] = tuple((row[0],) for row in abstract[2])
    one_action[3] = tuple((row[0],) for row in abstract[3])
    rejected.append(reject(lambda: residuals(ground, tuple(one_action), phi, F(1)), "ACTION_SET_MISMATCH"))
    rejected.append(reject(lambda: residuals(ground, abstract, (0,) * 4, F(1)), "NON_SURJECTIVE_PHI"))
    rejected.append(reject(lambda: residuals(ground, abstract, phi, F(0)), "GROUND_REWARD_BOUND"))
    excessive_abstract = list(abstract)
    excessive_abstract[3] = ((F(2), F(2)),) * 2
    rejected.append(reject(lambda: residuals(ground, tuple(excessive_abstract), phi, F(1)), "ABSTRACT_REWARD_BOUND"))
    rejected.append(reject(lambda: policy_value(ground, (9,) * 4), "POLICY_ACTION_OUT_OF_RANGE"))
    require(len(rejected) == 10, "malformed control count")
    return {"optimization": sys.flags.optimize, "rejected": rejected}


def check_interpreter_modes():
    reports = []
    for optimized in (False, True):
        args = [sys.executable, "-I", "-B"]
        if optimized:
            args.append("-O")
        args.extend([str(Path(__file__).resolve()), "--preconditions-only"])
        completed = subprocess.run(args, text=True, capture_output=True, timeout=15)
        require(completed.returncode == 0, "interpreter hostile checks failed: " + completed.stderr)
        report = json.loads(completed.stdout)
        require(report["optimization"] == int(optimized), "wrong child optimization mode")
        reports.append(report)
    require(reports[0]["rejected"] == reports[1]["rejected"], "optimization changed model rejection")
    return reports


def run():
    interpreter_reports = check_interpreter_modes()
    cases, fixed_policy_checks, direct_return_checks, trace_checks = [], 0, 0, 0
    for gamma in (F(0), F(1, 2), F(3, 4)):
        for eps in (F(0), F(1, 16), F(1, 8)):
            ground, abstract, phi = fixture(eps, gamma)
            er, ep, bound = residuals(ground, abstract, phi, F(1))
            require(er == ep == eps, 'check failed: er == ep == eps')
            gv, gp = optimal_value(ground)
            av, ap = optimal_value(abstract)
            value_gap = max(abs(gv[s]-av[phi[s]]) for s in range(4))
            require(value_gap <= bound, 'check failed: value_gap <= bound')
            for pi in product(range(2), repeat=2):
                lifted = tuple(pi[z] for z in phi)
                pv, qv = policy_value(ground, lifted), policy_value(abstract, pi)
                require(max(abs(pv[s]-qv[phi[s]]) for s in range(4)) <= bound, 'check failed: max((abs(pv[s] - qv[phi[s]]) for s in range(4))) <= bound')
                fixed_policy_checks += 1
            regrets = []
            for pi in ap:
                lv = policy_value(ground, tuple(pi[z] for z in phi))
                regret = max(gv[s]-lv[s] for s in range(4))
                require(0 <= regret <= 2*bound, 'check failed: 0 <= regret <= 2 * bound')
                regrets.append(regret)
            approx = finite_horizon_value(ground, 32)
            require(max(abs(gv[s]-approx[s]) for s in range(4)) <= gamma**32/(1-gamma), 'check failed: max((abs(gv[s] - approx[s]) for s in range(4))) <= gamma ** 32 / (1 - gamma)')
            cases.append({"gamma": str(gamma), "residual": str(eps), "value_bound": str(bound),
                          "actual_value_gap": str(value_gap), "max_lifted_policy_regret": str(max(regrets))})

    ground, abstract, phi = fixture()
    for pi in product(range(2), repeat=4):
        pv = policy_value(ground, pi)
        for s in range(4):
            require(enumerate_return(ground, pi, s, 4, pv) == pv[s], 'check failed: enumerate_return(ground, pi, s, 4, pv) == pv[s]')
            direct_return_checks += 1
    for length in range(4):
        for actions in product(range(2), repeat=length):
            for s in range(4):
                left = trace_law(ground, s, actions, phi)
                right = trace_law(abstract, phi[s], actions, (0, 1))
                require(left == right, 'check failed: left == right')
                trace_checks += 1
    perturbed, _, _ = fixture(F(1, 16))
    require(any(trace_law(perturbed, s, (a,), phi) != trace_law(abstract, phi[s], (a,), (0, 1))
               for s in range(4) for a in range(2)), "transition perturbation not detected")

    bad, coarse, mapping = noncollapse_fixture()
    vv, pp = optimal_value(bad)
    require(vv == (F(2),)*4, 'check failed: vv == (F(2),) * 4')
    er, ep, bb = residuals(bad, coarse, mapping, F(1))
    require((er, ep, bb) == (F(1, 2), F(0), F(1)), 'check failed: (er, ep, bb) == (F(1, 2), F(0), F(1))')
    latent_returns = []
    for pi in product(range(2), repeat=2):
        value = policy_value(bad, tuple(pi[z] for z in mapping))
        latent_returns.append(sum(value)/4)
    require(set(latent_returns) == {F(1)}, 'check failed: set(latent_returns) == {F(1)}')
    embeddings = (-1, -1, 1, 1)
    latent_loss = sum(bad[2][s][a][t]*F((embeddings[t]-embeddings[s])**2, 8)
                      for s in range(4) for a in range(2) for t in range(4))
    mean = F(sum(embeddings), 4)
    variance = sum(F((z-mean)**2, 4) for z in embeddings)
    require(latent_loss == 0 and mean == 0 and variance == 1, 'check failed: latent_loss == 0 and mean == 0 and (variance == 1)')
    history_checks = sum(conditional_bit_rewards(h) for h in range(7))

    # Half-L1 total variation needs the factor two for general signed values.
    signed_values = (F(2), F(-2))
    p, q = (F(1), F(0)), (F(0), F(1))
    tv = sum(abs(x-y) for x,y in zip(p,q))/2
    expectation_difference = abs(sum((x-y)*v for x,y,v in zip(p,q,signed_values)))
    require(tv == 1 and expectation_difference == 4 and expectation_difference > 2*tv, 'check failed: tv == 1 and expectation_difference == 4 and (expectation_difference > 2 * tv)')

    hostiles = []
    broken = copy.deepcopy(list(ground))
    broken[2] = tuple(tuple(tuple(F(0) for _ in range(4)) for _ in range(2)) for _ in range(4))
    hostiles.append(reject(lambda: validate(tuple(broken)), "NON_NORMALIZED_KERNEL"))
    broken = list(ground); broken[4] = F(1)
    hostiles.append(reject(lambda: validate(tuple(broken)), "UNDISCOUNTED_MODEL"))
    hostiles.append(reject(lambda: residuals(ground, abstract, (0,0,0,0), F(1)), "NON_SURJECTIVE_MAP"))
    hostiles.append(reject(lambda: residuals(ground, abstract, phi, F(0)), "UNDECLARED_REWARD_RANGE"))
    broken_abstract = list(abstract); broken_abstract[1] = 1
    broken_abstract[2] = tuple((row[0],) for row in abstract[2])
    broken_abstract[3] = tuple((row[0],) for row in abstract[3])
    hostiles.append(reject(lambda: residuals(ground, tuple(broken_abstract), phi, F(1)), "DIFFERENT_ACTION_SETS"))
    # This arithmetic invalidates the attempted zero-error promotion when reward
    # sufficiency is omitted, even though transition and latent-loss tests pass.
    require(max(vv) > max(latent_returns) and ep == 0 and latent_loss == 0, 'check failed: max(vv) > max(latent_returns) and ep == 0 and (latent_loss == 0)')
    hostiles.append("PREDICTION_NONCOLLAPSE_WITHOUT_REWARD_SUFFICIENCY")
    hostiles.append("HALF_L1_TV_FACTOR_TWO_OMITTED")
    hostiles.append("PERTURBED_CONTROL_TRANSITION_TRACE")

    rollout_checks = 0
    for lam in (F(0), F(1, 2), F(1), F(2)):
        state, d = F(0), F(1, 3)
        for horizon in range(1, 9):
            state = lam*state+d
            require(state == d*sum(lam**j for j in range(horizon)), 'check failed: state == d * sum((lam ** j for j in range(horizon)))')
            rollout_checks += 1
    # Floating corroboration only; the exact trig counterexample is proved in T3.
    endpoint_gap = math.hypot(3*(math.cos(2*math.pi)-1), 3*math.sin(2*math.pi))
    require(endpoint_gap < 1e-12 and 3*2*math.pi > 18, 'check failed: endpoint_gap < 1e-12 and 3 * 2 * math.pi > 18')
    hostiles.append("LOCAL_JACOBIAN_MIN_SINGULAR_VALUE_IS_NOT_GLOBAL_EXPANSION")

    audit = json.loads((ROOT/"AI_FINDING_AUDIT_V2.json").read_text())
    original = json.loads(REGISTRY.read_text())
    counts = audit_registry(audit, original)
    forged = copy.deepcopy(audit); forged["rows"][42]["gmi_derivation_certified"] = True
    hostiles.append(reject(lambda: audit_registry(forged, original), "FORGED_TRANSFORMER_DERIVATION"))
    forged = copy.deepcopy(audit); forged["rows"][0]["needed_evidence"] = ""
    hostiles.append(reject(lambda: audit_registry(forged, original), "EMPTY_EVIDENCE_OBLIGATION"))

    sources = json.loads((ROOT/"SOURCES_V2.json").read_text())
    reductions = json.loads((ROOT/"FAMILY_REDUCTION_SCOPE_V2.json").read_text())
    require(len(sources["entries"]) == 14 and sources["not_all_52_sources_reread"] is True, "check failed: len(sources['entries']) == 14 and sources['not_all_52_sources_reread'] is True")
    require(len(reductions["rows"]) == 9 and reductions["universal_architecture_claim"] is False, "check failed: len(reductions['rows']) == 9 and reductions['universal_architecture_claim'] is False")
    require(all(row["imported_assumptions"] and row["not_established"] for row in reductions["rows"]), "check failed: all((row['imported_assumptions'] and row['not_established'] for row in reductions['rows']))")
    files = [p for p in ROOT.iterdir() if p.is_file() and p.name != "RESULT_V2.json"]
    input_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    input_hashes["../gmi-1068-r12-ai-findings-registry-v1/AI_FINDING_REGISTRY_V1.json"] = hashlib.sha256(REGISTRY.read_bytes()).hexdigest()
    return {"schema":"GMI_R11_CONTROL_REPAIR_RESULT_V2", "status":"PASS_LOCAL_EXACT_WITNESSES_AND_SCOPE_AUDIT",
            "programme_completeness":False, "r11_earned":False, "r12_earned":False,
            "inherited_green_used":False, "general_theorems_lean_verified":False,
            "interpreter_precondition_controls":interpreter_reports,
            "finite_mdp_cases":cases,"fixed_policy_checks":fixed_policy_checks,
            "independent_direct_return_checks":direct_return_checks,"exact_trace_checks":trace_checks,
            "noncollapse":{"latent_prediction_loss":str(latent_loss),"latent_variance":str(variance),
                           "gamma":"1/2","full_initial_expected_value":"2","latent_initial_expected_value":"1",
                           "past_bit_conditioning_checks":history_checks},
            "rollout_affine_checks":rollout_checks,"hostiles_caught":sorted(hostiles),
            "audited_rows":52,"adjudication_counts":counts,"input_sha256":input_hashes,
            "remaining":["General proofs not machine checked", "Uniform learned-model residuals unmeasured",
                         "No JEPA benchmark reproduced", "Parent lineage not re-earned",
                         "52 findings not established as GMI consequences", "Source nonlinear lower-bound proof needs repair"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--preconditions-only", action="store_true")
    options = parser.parse_args()
    if options.preconditions_only:
        print(json.dumps(malformed_model_controls(), sort_keys=True))
        sys.exit(0)
    result = run()
    path = ROOT/"RESULT_V2.json"
    if options.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        require(json.loads(path.read_text()) == result, "stale or altered receipt; rerun --write after review")
    print(json.dumps({k:v for k,v in result.items() if k not in {"input_sha256", "finite_mdp_cases"}}, sort_keys=True))
