#!/usr/bin/env python3
"""E2R alternative-accounting audit witness (REV-L49-L53-SEARCHER-ACCOUNTING).

Runs the frozen E2 searchers' cost vectors under the five accountings declared
in ACCOUNTING_AUDIT_FREEZE_E2R.md (committed before this file was executed)
and re-adjudicates the E2 over/under-cap verdicts. Imports the frozen witness;
search mechanics are not duplicated. Exact rationals only; no Monte Carlo.

Trace schema per searcher (accounting-independent activity facts):
  cached_unique    discrete masks actually verified under a cache accounting
  no_cache_events  discrete verification events with no cache (re-visits charged)
  relaxed_evals    full relaxed 32-example loss evaluations
  final_verify     True iff the last discrete verification is the SHARED final
                   exact verifier (exemptible under A4); search-intrinsic
                   verifications (random slots, strict/drift proposals) are
                   never flagged
A0 touch check: 32*(cached_unique + relaxed_evals) must equal the frozen
truth_example_touches of RESULTS_AND_PROOF_E2.md for every searcher.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import argparse
from fractions import Fraction
from pathlib import Path

import section_e_searcher_comparison_witness as w

N = w.N
TARGET = w.TARGET
EX = w.VERIFY_EXAMPLES          # 32, frozen
A0_CAP = w.TRUTH_TOUCH_CAP      # 320, frozen


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------- mechanics
# per-example arithmetic cost of the cheapest registered routine (loss-only
# forward), DERIVED by instrumentation and cross-checked against the frozen
# law "26 arithmetic ops/example" (ACCOUNTING_FREEZE_E2.md). Not hardcoded.
def per_example_ops() -> Fraction:
    _, ops = w.relaxed_loss([Fraction(1, 2)] * N, w.target_y())
    per = Fraction(ops, EX)
    assert per == 26, f"derived per-example ops {per} != frozen law 26"
    return per


# strict evolution under a NO-CACHE accounting: every proposal attempt
# executes one discrete verification. The parent's own error is internal
# state, never re-charged. Deterministic bit cycle exactly as in the frozen
# witness (bit = i % N).
def strict_no_cache_events(proposals: int = 10) -> int:
    ys = w.target_y()
    current = 0
    events = 0
    err_current = w.discrete_error(current, ys)
    for i in range(proposals):
        bit = i % N
        cand = current ^ (1 << bit)
        events += 1                      # verification executed, no cache
        err_cand = w.discrete_error(cand, ys)
        if err_cand < err_current:
            current, err_current = cand, err_cand
        if current == TARGET:
            break
    assert current != TARGET, "no-cache strict run must remain plateau-blocked"
    return events


# neutral drift: verification events == proposal attempts (every proposal is
# verified before acceptance), recomputed inside the 3125-path enumeration.
def drift_events_exact(target: int = TARGET, T: int = 5) -> Fraction:
    total = N ** T
    events = 0
    for choices in itertools.product(range(N), repeat=T):
        state = 0
        props = 0
        for bit in choices:
            props += 1
            state ^= 1 << bit
            if state == target:
                break
        events += props
    return Fraction(events, total)


# ---------------------------------------------------------------- traces
def build_traces() -> dict:
    strict = w.strict_evolution()
    strict_nc = strict_no_cache_events()
    neutral5 = w.neutral_drift_exact(T=5)
    drift_events = drift_events_exact()
    nas = w.ablation_nas()
    darts = w.darts()

    # mechanics cross-checks against frozen numbers
    assert strict['truth_example_touches'] == 192
    assert strict['unique_discrete_candidates_verified'] == 6
    assert strict_nc == 10
    assert Fraction(neutral5['expected_proposal_or_mutation_attempts']) == Fraction(613, 125)
    assert drift_events == Fraction(613, 125), f"drift events {drift_events} != 613/125"
    assert Fraction(neutral5['expected_unique_discrete_candidates_verified']) == Fraction(15622, 3125)
    assert nas['truth_example_touches'] == 352 and nas['arithmetic_update_ops'] == 8320
    assert darts['truth_example_touches'] == 64 and darts['arithmetic_update_ops'] == 2122

    traces = {
        'random': {'cached_unique': Fraction(10), 'no_cache_events': Fraction(10),
                   'relaxed_evals': Fraction(0), 'final_verify': False, 'ops': 0},
        'strict': {'cached_unique': Fraction(strict['unique_discrete_candidates_verified']),
                   'no_cache_events': Fraction(strict_nc),
                   'relaxed_evals': Fraction(0), 'final_verify': False, 'ops': 0},
        'drift':  {'cached_unique': Fraction(neutral5['expected_unique_discrete_candidates_verified']),
                   'no_cache_events': drift_events,
                   'relaxed_evals': Fraction(0), 'final_verify': False, 'ops': 0},
        'nas':    {'cached_unique': Fraction(1), 'no_cache_events': Fraction(1),
                   'relaxed_evals': Fraction(10), 'final_verify': True,
                   'ops': nas['arithmetic_update_ops']},
        'darts':  {'cached_unique': Fraction(1), 'no_cache_events': Fraction(1),
                   'relaxed_evals': Fraction(1), 'final_verify': True,
                   'ops': darts['arithmetic_update_ops']},
    }
    # A0 touch reproduction from the trace itself
    a0_touches = {s: EX * (t['cached_unique'] + t['relaxed_evals']) for s, t in traces.items()}
    assert a0_touches['random'] == 320 and a0_touches['strict'] == 192
    assert a0_touches['drift'] == Fraction(499904, 3125)
    assert a0_touches['nas'] == 352 and a0_touches['darts'] == 64
    return traces


# ---------------------------------------------------------------- accountings
def cost_a1(t):   # EVAL-COUNT: 1 unit per complete evaluation; cache kept; final verify charged
    return t['cached_unique'] + t['relaxed_evals']


def cost_a2(t):   # EXEC-B: 1 exec per single-example execution; no cache discount
    return EX * (t['no_cache_events'] + t['relaxed_evals'])


def cost_a3(t, per_ex):   # OP-PRICE: per_example_ops*touches + ops, cache as A0
    return per_ex * EX * (t['cached_unique'] + t['relaxed_evals']) + t['ops']


def cost_a3b(t, per_ex):  # OP-PRICE-NOCACHE: verification events, not unique masks
    return per_ex * EX * (t['no_cache_events'] + t['relaxed_evals']) + t['ops']


def cost_a4(t):   # VERIFIER-EXEMPT: A1 minus the shared final verification
    return t['cached_unique'] + t['relaxed_evals'] - (1 if t['final_verify'] else 0)


CAP_A1 = Fraction(10)              # frozen derivation: ten full candidate evaluations
CAP_A2 = Fraction(A0_CAP)          # 320 single-example executions
CAP_A4 = Fraction(10)

A0_STATES = {'random': 'at', 'strict': 'within', 'drift': 'within', 'nas': 'over', 'darts': 'within'}

# frozen prediction tables (ACCOUNTING_AUDIT_FREEZE_E2R.md)
PREDICTED_COSTS = {
 'A1': {'random': '10', 'strict': '6', 'drift': '15622/3125', 'nas': '11', 'darts': '2'},
 'A2': {'random': '320', 'strict': '320', 'drift': '19616/125', 'nas': '352', 'darts': '64'},
 'A3': {'random': '8320', 'strict': '4992', 'drift': '12997504/3125', 'nas': '17472', 'darts': '3786'},
 'A3B': {'random': '8320', 'strict': '8320', 'drift': '510016/125', 'nas': '17472', 'darts': '3786'},
 'A4': {'random': '10', 'strict': '6', 'drift': '15622/3125', 'nas': '10', 'darts': '1'},
}
PREDICTED_STATES = {
 'A1': {'random': 'at', 'strict': 'within', 'drift': 'within', 'nas': 'over', 'darts': 'within'},
 'A2': {'random': 'at', 'strict': 'at', 'drift': 'within', 'nas': 'over', 'darts': 'within'},
 'A3': {'random': 'at', 'strict': 'within', 'drift': 'within', 'nas': 'over', 'darts': 'within'},
 'A3B': {'random': 'at', 'strict': 'at', 'drift': 'within', 'nas': 'over', 'darts': 'within'},
 'A4': {'random': 'at', 'strict': 'within', 'drift': 'within', 'nas': 'at', 'darts': 'within'},
}


def adjudicate(cost: Fraction, cap: Fraction) -> str:
    if cost > cap:
        return 'over'
    if cost == cap:
        return 'at'
    return 'within'


def build_audit():
    per_ex = per_example_ops()
    cap_a3 = per_ex * A0_CAP      # 26*320 = 8320, frozen identity
    assert cap_a3 == 8320
    traces = build_traces()

    accountings = {
        'A1_EVAL_COUNT': (cost_a1, CAP_A1),
        'A2_EXEC_B': (cost_a2, CAP_A2),
        'A3_OP_PRICE': (lambda t: cost_a3(t, per_ex), cap_a3),
        'A3B_OP_PRICE_NOCACHE': (lambda t: cost_a3b(t, per_ex), cap_a3),
        'A4_VERIFIER_EXEMPT': (cost_a4, CAP_A4),
    }
    short = {k: k.split('_')[0] for k in accountings}

    rows = {}
    all_ok = True
    for name, (fn, cap) in accountings.items():
        rows[name] = {}
        for searcher, t in traces.items():
            cost = fn(t)
            state = adjudicate(cost, cap)
            a0 = A0_STATES[searcher]
            ok = (str(cost) == PREDICTED_COSTS[short[name]][searcher]
                  and state == PREDICTED_STATES[short[name]][searcher])
            rows[name][searcher] = {
                'cost': str(cost), 'cap': str(cap), 'state': state,
                'a0_state': a0,
                'relation_to_a0': 'HOLD' if state == a0 else 'FLIP',
                'prediction_match': ok,
            }
            all_ok = all_ok and ok

    # ---- claim-level adjudication (rules frozen in ACCOUNTING_AUDIT_FREEZE_E2R.md)
    v_nas = {name: rows[name]['nas']['state'] for name in accountings}
    flips = {name: {'from': A0_STATES['nas'], 'to': rows[name]['nas']['state']}
             for name in accountings if rows[name]['nas']['relation_to_a0'] == 'FLIP'}
    nas_sensitive = bool(flips)
    nas_at_or_over = all(rows[name]['nas']['state'] in ('over', 'at') for name in accountings)
    nas_never_strictly_within = nas_at_or_over
    nas_dominated = all(
        (rows[name]['darts']['state'] in ('within', 'at'))
        and Fraction(rows[name]['darts']['cost']) < Fraction(rows[name]['nas']['cost'])
        for name in accountings)

    # C-ORDERING robust: recovery outcomes pairwise distinct in the
    # (cost_state, success) projection under every accounting
    successes = {
        'random': '5/16', 'strict': '0', 'drift': '12/125',
        'nas': 'exact(21)', 'darts': 'exact(21)',
    }
    ordering_robust = True
    ordering_detail = {}
    for name in accountings:
        proj = {s: (rows[name][s]['state'], successes[s]) for s in traces}
        items = list(proj.items())
        distinct = all(a[1] != b[1] for i, a in enumerate(items) for b in items[i + 1:])
        ordering_detail[name] = {'projection': {k: list(v) for k, v in proj.items()},
                                 'pairwise_distinct': distinct}
        ordering_robust = ordering_robust and distinct

    # accounting-independence of successes (reproduce frozen values exactly)
    rand = w.random_parent()
    strict = w.strict_evolution()
    neutral5 = w.neutral_drift_exact(T=5)
    nas = w.ablation_nas()
    darts = w.darts()
    indep_ok = (rand['success_prob_at_10'] == '5/16'
                and strict['success_probability_or_exact_success'] is False
                and strict['terminal'] == w.STRICT_TERMINAL
                and neutral5['success_probability'] == '12/125'
                and w.neutral_hit_dp(T=10) == Fraction(72696, 390625)
                and nas['hard_mask'] == 21 and nas['exact_error'] == 0
                and darts['hard_mask'] == 21 and darts['exact_error'] == 0
                and darts['arithmetic_update_ops'] == 2122)

    claims = {
        'C-NAS-OVER': {
            'disposition': 'ACCOUNTING_SENSITIVE' if nas_sensitive else 'ACCOUNTING_ROBUST',
            'flip_witnesses': flips,
            'per_accounting_state': v_nas,
        },
        'C-NAS-AT-OR-OVER': {
            'disposition': 'REVIVED' if (nas_at_or_over and nas_dominated) else 'NOT_EARNED',
            'statement': ('the ablation method consumes the entire evaluation budget or '
                          'more under every declared accounting; it is never strictly '
                          'within budget; the DARTS representative is strictly cheaper '
                          'under every declared accounting'),
            'at_or_over_everywhere': nas_at_or_over,
            'never_strictly_within': nas_never_strictly_within,
            'darts_strictly_cheaper_everywhere': nas_dominated,
        },
        'C-ORDERING': {
            'disposition': 'ACCOUNTING_ROBUST' if ordering_robust else 'SENSITIVE',
            'per_accounting': {k: v['pairwise_distinct'] for k, v in ordering_detail.items()},
        },
    }

    return {
        'authority': {
            'revival_ticket': 'REV-L49-L53-SEARCHER-ACCOUNTING',
            'issue': 833,
            'section_e_issue': 715,
            'freeze_doc': 'ACCOUNTING_AUDIT_FREEZE_E2R.md',
            'e2r_freeze_commit': '9be2bf38 (pre-outcome scaffold commit of ACCOUNTING_AUDIT_FREEZE_E2R.md)',
            'frozen_e2_freeze_commit': '773bebb5b7851c72a0a80e4ff22381406d9cac99',
            'frozen_e2_accounting_commit': 'd437442367b7314a8ef453c0c1d4630e86b579c4',
        },
        'pins': {p: sha256_file(Path(__file__).resolve().parent / p)
                 for p in ('FREEZE_E2.md', 'ACCOUNTING_FREEZE_E2.md',
                           'section_e_searcher_comparison_witness.py',
                           'ACCOUNTING_AUDIT_FREEZE_E2R.md')},
        'derived_constants': {
            'per_example_ops_loss_only_forward': str(per_ex),
            'cap_a3_op_equivalents': str(cap_a3),
            'derivation': ('per-example ops derived by instrumented run of the frozen '
                           'relaxed_loss at the symmetric point (832 ops / 32 examples); '
                           'A3 cap = per_example_ops * 320 = 8320 (frozen identity)'),
        },
        'traces': {k: {kk: str(vv) for kk, vv in v.items()} for k, v in traces.items()},
        'accountings': rows,
        'claims': claims,
        'ordering_detail': ordering_detail,
        'success_independence_reproduced': indep_ok,
        'all_frozen_predictions_match': all_ok,
        'exit_green': bool(all_ok and indep_ok and nas_sensitive and nas_at_or_over
                           and nas_dominated and ordering_robust),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path,
                    default=Path(__file__).with_name('ACCOUNTING_AUDIT_RESULT_E2R.json'))
    a = ap.parse_args()
    r = build_audit()
    a.output.write_text(json.dumps(r, indent=2, sort_keys=True) + '\n')
    print(json.dumps({
        'per_accounting_states': {n: {s: row['state'] for s, row in rows.items()}
                                  for n, rows in r['accountings'].items()},
        'claims': {c: v['disposition'] for c, v in r['claims'].items()},
        'flip_witnesses': r['claims']['C-NAS-OVER']['flip_witnesses'],
        'all_frozen_predictions_match': r['all_frozen_predictions_match'],
        'success_independence_reproduced': r['success_independence_reproduced'],
        'exit_green': r['exit_green']}, indent=2, sort_keys=True))
    raise SystemExit(0 if r['exit_green'] else 1)


if __name__ == '__main__':
    main()
