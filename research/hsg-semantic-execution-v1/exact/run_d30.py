'''D30 -- delta-dial frontier: total_cost(delta) vs direct on the frozen D20
machinery.

Protocol: ECONOMY_FRONTIER_PROTOCOLS_V1.json (D30_delta_dial), frozen at 75f032fe
before this file ran. Registered prediction under test: some delta in (0, 0.25]
beats direct on total cost at n in the upper grid half; delta=0 reproduces the
filed D20 negative everywhere (boundary of the family).

Machinery discipline: every frozen D20 module is IMPORTED UNCHANGED (worlds,
counters, op metrics, direct arm). The only new code is the frozen delta dial
on the abstract answer plus the study sweep around it. cegar_dial below is a
line-for-line copy of d20.cegar with ONE inserted branch between abstract_bfs
and validate; abstract_bfs_seen / validate_rec are line-for-line copies of
d20.abstract_bfs / d20.validate that additionally EXPOSE sets those functions
already compute internally (the BFS 'seen' blocks and the concrete
prefix-reachable set). Counters are charged identically to the frozen
functions; the dial's own bookkeeping is charged to dial_bookkeeping_ops and
exists ONLY when delta > 0, so delta = 0 is identical to the frozen exact path
(asserted against the committed D20_RESULTS.json numbers).

delta dial semantics (frozen):
  - The served answer object is the BLOCK-LEVEL REACHABILITY CLASSIFICATION:
    every state of an abstractly-reachable block is answered 'reachable'
    (served set U), all others 'unreachable'. The direct arm's answer is the
    exact reachable set (BFS seen), error 0.
  - CERTIFIED ERROR BOUND (sound, no new mechanism): the may-abstraction
    satisfies R_true inside U (induction: every concrete path projects to an
    abstract path, so the block of any reachable state is abstractly
    reachable), and L inside R_true where L = {init} union every concrete
    prefix-reachable set validate certifies along the run. Serving U then
    misclassifies at most |U minus L| states (worst case): every wrong 'yes'
    lies in U outside R_true, and every wrong 'no' lies in R_true outside U,
    which is empty. certified_bound = |U minus L| / n. U is the FULL abstract
    closure (the frozen BFS stops at the first Bad block, so its 'seen' is
    only a prefix; the dial computes the closure of the already-charged at
    relation and pays dial_bookkeeping_ops for it). All integer set
    arithmetic; delta enters as an exact Fraction.
  - Serve rule: at a point where the frozen path has an abstract
    counterexample, the relaxed arm may serve U WITHOUT paying validation or
    refinement when delta > 0 and certified_bound <= delta. delta = 0 never
    takes the branch (identical loop to d20.cegar). The safety verdict served
    alongside the classification at a relaxed stop is REPORTED against ground
    truth, never certified: a single misclassified Bad state can flip a
    verdict bit, so no verdict-bit claim is made at delta > 0. Only the
    state-mass bound is certified.
  - Soundness checker (independent of the arm): for every served row, actual
    error |U minus R_true| must be <= certified bound <= delta, and R_true
    must lie inside U. Hostile plants P1 (bound silently halved) and P2 (bound
    claimed zero) must be CAUGHT; the sound bound on the whole grid is the
    clean no-alarm control (RC3: both alarm and no-alarm directions).
  - Envelope arm delta=1.0 (auxiliary, not a grid arm): total_cost(delta) is
    monotone non-increasing in delta (a weaker serve condition can only serve
    no later), so the delta=1.0 run -- serve at the first abstract
    counterexample -- is the infimum of structural total cost over ALL delta
    in (0, 1]. It is measured so the registered falsifier, which is posed
    over delta in (0, 1), can be decided on the full interval and not only on
    the swept grid.

Hostiles P1/P2 are bound-checker plants, in the H-D20b spirit (unsound
certificate): P1 halves the certified bound, P2 claims 0. Both run at
delta=0.25 and at the envelope delta=1.0. Each must produce at least one
served row whose actual error exceeds the planted bound (checker alarm); if a
plant cannot be exercised the run reports hostile-did-not-flip and the
measurement path is unvalidated in the alarm direction (CANNOT_CHECK per RC3).

Python 3.8 compatible, stdlib only. Runs on a disjoint host, never Mac mini.
'''
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from fractions import Fraction

from exact.worlds_d19d20 import ow5s_worlds
from exact.d20 import (_abstract_ops, _canon, _direct_ops, _new_counters,
                       apply_split, build_abstraction, cegar, direct_bfs)

DELTA_GRID = (Fraction(0), Fraction(1, 100), Fraction(1, 20),
              Fraction(1, 10), Fraction(1, 4))
DELTA_ENVELOPE = Fraction(1)          # auxiliary infimum arm, not a grid arm
N_GRID = (8, 12, 16, 20, 24)
UPPER_HALF = (20, 24)                 # pre-registered 'upper grid half'
PLANT_DELTAS = (Fraction(1, 4), Fraction(1))
PLANTS = ('half', 'zero')

HERE = os.path.dirname(os.path.abspath(__file__))


def _delta_tag(d):
    if d == 0:
        return '0'
    if d == 1:
        return '1'
    return '%d/%d' % (d.numerator, d.denominator)


# ------------------------------------------- line-for-line copies ----
def abstract_bfs_seen(w, blk_of, at, ctr):
    '''d20.abstract_bfs UNCHANGED except the abstractly-reachable block set
    ('seen') is exposed for the certified bound. Counter charges identical.'''
    bad_blocks = set(blk_of[s] for s in w['bad'])
    start = blk_of[w['init']]
    ctr['verification_calls'] += 1
    if start in bad_blocks:
        return 'UNSAFE', [start], {start}
    seen, parent, q, qi = {start}, {start: None}, [start], 0
    while qi < len(q):
        u = q[qi]
        qi += 1
        ctr['abstract_states_expanded'] += 1
        for v in at[u]:
            ctr['abstract_transitions_examined'] += 1
            if v in seen:
                continue
            seen.add(v)
            parent[v] = u
            ctr['verification_calls'] += 1
            if v in bad_blocks:
                path = [v]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                return 'UNSAFE', list(reversed(path)), set(seen)
            q.append(v)
    return 'SAFE', None, set(seen)


def validate_rec(w, blocks, path, ctr):
    '''d20.validate UNCHANGED except the final concrete prefix-reachable set
    (certified reachable states) is exposed for L. Counter charges identical.
    On SPURIOUS the set at the failure point is returned (still certified:
    every state in it is reached from init by real transitions only).'''
    R = set([w['init']])
    for i in range(len(path) - 1):
        nxt = set()
        for s in sorted(R):
            for t in w['trans'][s]:
                ctr['validation_ops'] += 1
                if t in blocks[path[i + 1]]:
                    nxt.add(t)
        if not nxt:
            B, Bn = blocks[path[i]], blocks[path[i + 1]]
            has = set()
            for s in sorted(B):
                for t in w['trans'][s]:
                    ctr['validation_ops'] += 1
                    if t in Bn:
                        has.add(s)
                        break
            return ('SPURIOUS', (path[i], frozenset(has),
                                 frozenset(B) - frozenset(has))), R
        R = nxt
    if R & set(w['bad']):
        return ('VALID', None), R
    B = frozenset(blocks[path[-1]])
    inbad = B & frozenset(w['bad'])
    return ('SPURIOUS', (path[-1], inbad, B - inbad)), R


# ------------------------------------------------- the delta dial ----
def cegar_dial(w, blocks0, delta, plant=None):
    '''d20.cegar UNCHANGED except the frozen delta dial: between abstract_bfs
    and validate, when delta > 0 and the certified error bound of serving the
    current block-level classification is <= delta, the relaxed arm serves
    immediately (skipping validation and refinement for this counterexample).
    plant in ('half','zero') plants an UNSOUND bound for the serve DECISION and
    the recorded certificate (checker hostile control); the sound-set
    bookkeeping is unchanged, so a plant only ever UNDER-claims uncertainty.
    dial_bookkeeping_ops charges the dial's own capital: maintaining L,
    materialising U, evaluating the bound, materialising the served answer.
    It exists only at delta > 0, keeping delta = 0 byte-identical to frozen.'''
    ctr = _new_counters()
    ctr['dial_bookkeeping_ops'] = 0
    blocks = _canon(blocks0)
    k0, n = len(blocks), w['n']
    ceiling = n - k0
    rounds, spurious = 0, 0
    L = set([w['init']]) if delta > 0 else None
    served = None
    while True:
        blk_of, at = build_abstraction(w, blocks, ctr)
        verdict, path, seen = abstract_bfs_seen(w, blk_of, at, ctr)
        if verdict == 'SAFE':
            term = 'SAFE'
            break
        if delta > 0:
            ctr['dial_bookkeeping_ops'] += len(seen) + len(L) + 1
            # U must CONTAIN R_true for the bound to be sound. The frozen
            # abstract_bfs STOPS at the first Bad-meeting block, so `seen` is
            # only a discovery prefix, NOT the abstract closure. The dial
            # therefore computes the FULL closure of the already-built (and
            # already charged) `at` relation and pays for it itself.
            clos, q2, qi2 = set([blk_of[w['init']]]), [blk_of[w['init']]], 0
            while qi2 < len(q2):
                u = q2[qi2]
                qi2 += 1
                ctr['dial_bookkeeping_ops'] += 1
                for v in at[u]:
                    ctr['dial_bookkeeping_ops'] += 1
                    if v not in clos:
                        clos.add(v)
                        q2.append(v)
            U = set()
            for i in clos:
                U |= blocks[i]
            bound_num = len(U - L)
            claimed = bound_num
            if plant == 'half':
                claimed = bound_num // 2
            elif plant == 'zero':
                claimed = 0
            if Fraction(claimed, n) <= delta:
                ctr['dial_bookkeeping_ops'] += len(U)
                served = {'U': frozenset(U), 'L': frozenset(L),
                          'certified_bound_num': claimed,
                          'true_bound_num': bound_num,
                          'blocks_at_serve': len(blocks)}
                term = 'UNSAFE_DELTA_RELAXED'
                break
        (status, spec), R_cert = validate_rec(w, blocks, path, ctr)
        if delta > 0:
            ctr['dial_bookkeeping_ops'] += len(R_cert - L) + 1
            L |= R_cert
        if status == 'VALID':
            term = 'UNSAFE'
            break
        spurious += 1
        nb = apply_split(blocks, spec, strict=True)
        if len(nb) != len(blocks) + 1:
            term = 'NO_PROGRESS_DETECTED'
            break
        blocks = nb
        rounds += 1
        if rounds > ceiling:
            term = 'CEILING_VIOLATED'
            break
    ops = _abstract_ops(ctr) + (ctr['dial_bookkeeping_ops'] if delta > 0 else 0)
    return {'verdict': term, 'rounds': rounds, 'ceiling': ceiling,
            'k0': k0, 'final_blocks': len(blocks),
            'states_distinguished': len(blocks) - k0,
            'spurious_counterexamples': spurious,
            'ops': ops, 'counters': ctr,
            'conclusive': term in ('SAFE', 'UNSAFE'),
            'relaxed_served': served,
            'served_classification': (sorted(served['U'])
                                      if served is not None else None)}


def reachable_truth(w):
    '''Independent exhaustive recomputation of the reachable set (instrument
    side; charged to NEITHER arm). Must equal the frozen world field.'''
    seen, stack = set([w['init']]), [w['init']]
    while stack:
        s = stack.pop()
        for t in w['trans'][s]:
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return seen


def check_served_rows(rows, worlds_by_id):
    '''Independent soundness checker over every served row (alarm direction is
    exercised by the planted rows, no-alarm by the sound grid rows).
    Violations: (a) served U does not cover R_true (soundness break of the
    may-abstraction claim), (b) actual error exceeds the certified bound,
    (c) certified bound exceeds delta (serve condition violated).'''
    violations = []
    for r in rows:
        if r.get('served_U_size') is None:
            continue
        w = worlds_by_id[r['world']]
        r_true = set(w['concrete_reachable'])
        assert r_true == reachable_truth(w), 'frozen reachable field drift'
        U = set(r['served_classification'])
        actual_err = len(U - r_true) + len(r_true - U)
        certified = r['certified_bound_num']
        if not r_true <= U:
            violations.append([r['world'], r['delta_tag'], 'U_UNSOUND',
                               len(r_true - U)])
        if actual_err > certified:
            violations.append([r['world'], r['delta_tag'],
                               'ACTUAL_EXCEEDS_CERTIFIED', actual_err,
                               certified])
        if Fraction(certified, r['n']) > Fraction(r['delta_frac']):
            violations.append([r['world'], r['delta_tag'],
                               'CERTIFIED_EXCEEDS_DELTA', certified])
        if actual_err != r.get('actual_error_num'):
            violations.append([r['world'], r['delta_tag'],
                               'REPORTED_ERROR_MISMATCH', actual_err,
                               r.get('actual_error_num')])
    return violations


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _retained_bytes(blocks):
    '''MEASURED auxiliary HDI-14 bytes/state family: the partition the
    structural arm retains at termination, deterministic serialization.
    NOT added to the frozen op metric; charging it can only increase the
    dial arm's cost, so measured comparisons are conservative for direct.'''
    obj = {'blocks': sorted(sorted(b) for b in blocks)}
    return len(json.dumps(obj, sort_keys=True).encode('utf-8'))


# HDI-14 cost ledger: every family charged-or-justified for BOTH arms.
HDI14_LEDGER = {
    'acquisition': {
        'dial': ['abstraction_build_ops'],
        'direct': 'STRUCTURAL_ZERO: the direct arm acquires no capital; '
                  'direct_bfs holds no state'},
    'retrieval': {
        'dial': ['abstract_states_expanded',
                 'abstract_transitions_examined'],
        'direct': ['states_expanded', 'transitions_examined']},
    'rejected_candidates': {
        'dial': ['validation_ops'],
        'direct': 'STRUCTURAL_ZERO: direct search proposes no candidate '
                  'answer to reject'},
    'verification': {
        'dial': ['verification_calls'],
        'direct': ['verification_calls']},
    'adaptation': {
        'dial': ['dial_bookkeeping_ops'],
        'direct': 'STRUCTURAL_ZERO: no capital to adapt',
        'note': 'dial_bookkeeping_ops is the delta dial itself (L '
                'maintenance, full abstract closure for a sound serve, '
                'bound evaluation, served-answer materialisation). '
                'STRUCTURAL_ZERO_EXACTLY_AT delta=0: the dial branch never '
                'executes, so the counter is identically 0 and the arm is '
                'byte-identical to frozen d20.cegar (asserted per world '
                'against committed D20_RESULTS.json)'},
    'bytes_state': {
        'dial': 'MEASURED: retained_state_bytes (auxiliary, deterministic '
                'serialization of the final partition)',
        'direct': 'MEASURED: 0 (nothing retained)'}
}


def ledger_complete():
    '''HDI-14 rule: a family with neither a charged counter nor a justified
    structural zero emits CANNOT_CHECK (never silently 0).'''
    missing = []
    for fam, arms in sorted(HDI14_LEDGER.items()):
        for arm in ('dial', 'direct'):
            v = arms[arm]
            if not (isinstance(v, list) and v) and not (
                    isinstance(v, str) and ('STRUCTURAL_ZERO' in v
                                            or 'MEASURED' in v)):
                missing.append([fam, arm])
    return (not missing), missing


# ---------------------------------------------------------------- run ----
def run_d30(freeze_commit, host_label):
    t0w, t0c = time.time(), time.process_time()
    worlds = sorted(ow5s_worlds(), key=lambda w: w['id'])
    worlds_by_id = dict((w['id'], w) for w in worlds)
    receipts = []
    instrument_defects = []
    led_ok, led_missing = ledger_complete()
    if not led_ok:
        instrument_defects.append('HDI14_LEDGER_INCOMPLETE:'
                                  + json.dumps(led_missing))

    # committed frozen numbers for the delta=0 boundary cross-check
    committed_path = os.path.join(HERE, 'results', 'D20_RESULTS.json')
    committed = {}
    committed_per_n = {}
    if os.path.exists(committed_path):
        with open(committed_path, encoding='utf-8') as f:
            cj = json.load(f)
        committed = dict((r['world'], r) for r in cj['per_world'])
        committed_per_n = cj['secondary_endpoints']['per_n']
    else:
        instrument_defects.append('COMMITTED_D20_RESULTS_ABSENT')

    # control 0: frozen world field vs independent recomputation
    for w in worlds:
        if set(w['concrete_reachable']) != reachable_truth(w):
            instrument_defects.append('FROZEN_REACHABLE_DRIFT:' + w['id'])

    scored_deltas = tuple(d for d in DELTA_GRID) + (DELTA_ENVELOPE,)
    # cells[(delta, n)] -> totals over that n-band's 6 worlds
    cells = {}
    for d in scored_deltas:
        for n in N_GRID:
            cells[(d, n)] = {'direct_ops': 0, 'dial_ops': 0, 'worlds': 0,
                             'served': 0, 'rounds_total': 0,
                             'spurious_total': 0, 'final_blocks_total': 0,
                             'dial_bookkeeping_ops': 0,
                             'actual_error_fracs': [],
                             'certified_frac_at_serve': []}
    # per-delta compression/cost totals over ALL 30 worlds (Pareto input)
    pareto_inputs = {}
    served_rows = []      # sound rows for the checker (clean no-alarm control)
    hostile_rows = []     # planted rows (alarm control)
    boundary_failures = []
    truth_mismatches = []
    strict_run_defects = []

    for w in worlds:
        cw = committed.get(w['id'])
        dctr = _new_counters()
        truth = direct_bfs(w, dctr)
        d_ops = _direct_ops(dctr)
        if cw is not None and cw['direct_ops'] != d_ops:
            instrument_defects.append(
                'DIRECT_OPS_DIVERGE_FROM_COMMITTED:%s:%d:%d'
                % (w['id'], d_ops, cw['direct_ops']))

        # ---- boundary arm delta=0: live frozen cegar AND committed numbers
        cg = cegar(w, w['start_blocks'], strict=True)
        z0 = cegar_dial(w, w['start_blocks'], Fraction(0))
        for k in ('verdict', 'rounds', 'ops', 'final_blocks',
                  'spurious_counterexamples'):
            if z0[k] != cg[k]:
                boundary_failures.append([w['id'], k, z0[k], cg[k]])
        if cw is not None:
            committed_final_blocks = (cw['k']
                                      + cw['cegar_states_distinguished'])
            if (z0['ops'] != cw['cegar_ops']
                    or z0['rounds'] != cw['cegar_rounds']
                    or z0['verdict'] != cw['cegar_verdict']
                    or z0['final_blocks'] != committed_final_blocks):
                boundary_failures.append(
                    [w['id'], 'committed', z0['ops'], cw['cegar_ops'],
                     z0['rounds'], cw['cegar_rounds']])
        if z0['verdict'] != truth:
            truth_mismatches.append([w['id'], 'delta0', z0['verdict'],
                                     truth])
        if z0['verdict'] not in ('SAFE', 'UNSAFE'):
            strict_run_defects.append([w['id'], 'delta0', z0['verdict']])
        if z0['ops'] <= d_ops:
            # the filed negative IS cegar > direct per world; losing it here
            # would mean the frozen machinery moved
            boundary_failures.append(
                [w['id'], 'negative_lost', z0['ops'], d_ops])

        receipts.append({
            'row_type': 'boundary', 'job': 'D30', 'world': w['id'],
            'n': w['n'], 'delta_tag': '0', 'concrete_verdict': truth,
            'direct_ops': d_ops, 'dial_ops': z0['ops'],
            'cegar_ops_live_frozen': cg['ops'],
            'committed_cegar_ops': cw['cegar_ops'] if cw else None,
            'dial_bookkeeping_ops': 0,
            'rounds': z0['rounds'], 'verdict': z0['verdict'],
            'final_blocks': z0['final_blocks'],
            'retained_state_bytes': _retained_bytes(
                _canon(w['start_blocks']))})

        # ---- dial arms (scored grid + envelope)
        for delta in scored_deltas:
            if delta == 0:
                r = z0
            else:
                r = cegar_dial(w, w['start_blocks'], delta)
            if r['verdict'] in ('SAFE', 'UNSAFE') and r['verdict'] != truth:
                truth_mismatches.append([w['id'], _delta_tag(delta),
                                         r['verdict'], truth])
            if r['verdict'] in ('CEILING_VIOLATED', 'NO_PROGRESS_DETECTED'):
                strict_run_defects.append([w['id'], _delta_tag(delta),
                                           r['verdict']])
            key = (delta, w['n'])
            c = cells[key]
            c['direct_ops'] += d_ops
            c['dial_ops'] += r['ops']
            c['worlds'] += 1
            c['rounds_total'] += r['rounds']
            c['spurious_total'] += r['spurious_counterexamples']
            c['final_blocks_total'] += r['final_blocks']
            c['dial_bookkeeping_ops'] += \
                r['counters'].get('dial_bookkeeping_ops', 0)
            served = r['relaxed_served'] is not None
            if served:
                c['served'] += 1
                sv = r['relaxed_served']
                actual_err = len(set(sv['U'])
                                 - set(w['concrete_reachable'])) \
                    + len(set(w['concrete_reachable']) - set(sv['U']))
                c['actual_error_fracs'].append(actual_err / float(w['n']))
                c['certified_frac_at_serve'].append(
                    float(Fraction(sv['certified_bound_num'], w['n'])))
            pi = pareto_inputs.setdefault(
                _delta_tag(delta),
                {'delta': delta, 'ops_total': 0, 'compression_total': 0.0,
                 'direct_total': 0, 'worlds': 0, 'served': 0})
            pi['ops_total'] += r['ops']
            pi['compression_total'] += w['n'] / float(r['final_blocks'])
            pi['direct_total'] += d_ops
            pi['worlds'] += 1
            pi['served'] += int(served)

            row = {
                'row_type': 'cell', 'job': 'D30', 'world': w['id'],
                'n': w['n'], 'delta_tag': _delta_tag(delta),
                'delta_frac': '%d/%d' % (delta.numerator, delta.denominator)
                if delta != 0 and delta != 1 else str(delta.numerator),
                'concrete_verdict': truth,
                'direct_ops': d_ops, 'dial_ops': r['ops'],
                'dial_bookkeeping_ops':
                    r['counters'].get('dial_bookkeeping_ops', 0),
                'rounds': r['rounds'], 'spurious':
                    r['spurious_counterexamples'],
                'verdict': r['verdict'],
                'final_blocks': r['final_blocks'],
                'served': served,
                'blocks_at_serve':
                    r['relaxed_served']['blocks_at_serve'] if served
                    else None,
                'certified_bound_num':
                    r['relaxed_served']['certified_bound_num'] if served
                    else None,
                'true_bound_num':
                    r['relaxed_served']['true_bound_num'] if served
                    else None,
                'served_U_size': len(r['relaxed_served']['U']) if served
                    else None,
                'served_classification': r['served_classification'],
                'actual_error_num': (
                    len(set(r['relaxed_served']['U'])
                        - set(w['concrete_reachable']))
                    + len(set(w['concrete_reachable'])
                          - set(r['relaxed_served']['U']))) if served
                    else None,
                'retained_state_bytes':
                    _retained_bytes(_canon(w['start_blocks'])),
                'dial_wins_world': r['ops'] < d_ops}
            if delta == DELTA_ENVELOPE:
                row['row_type'] = 'envelope'
            receipts.append(row)
            if served:
                served_rows.append(row)

        # ---- hostile plants (alarm direction of the bound checker)
        for pd in PLANT_DELTAS:
            for p in PLANTS:
                hr = cegar_dial(w, w['start_blocks'], pd, plant=p)
                hserved = hr['relaxed_served'] is not None
                hrow = {
                    'row_type': 'hostile', 'job': 'D30', 'world': w['id'],
                    'n': w['n'], 'plant': p,
                    'delta_tag': _delta_tag(pd),
                    'delta_frac': '%d/%d' % (pd.numerator, pd.denominator),
                    'served': hserved,
                    'certified_bound_num':
                        hr['relaxed_served']['certified_bound_num']
                        if hserved else None,
                    'true_bound_num':
                        hr['relaxed_served']['true_bound_num']
                        if hserved else None,
                    'served_U_size':
                        len(hr['relaxed_served']['U']) if hserved else None,
                    'served_classification': hr['served_classification'],
                    'actual_error_num': (
                        len(set(hr['relaxed_served']['U'])
                            - set(w['concrete_reachable']))
                        + len(set(w['concrete_reachable'])
                              - set(hr['relaxed_served']['U'])))
                    if hserved else None,
                    'concrete_verdict': truth,
                    'dial_ops': hr['ops']}
                receipts.append(hrow)
                if hserved:
                    hostile_rows.append(hrow)

    # ---- delta=0 aggregate boundary: per-n totals vs committed D20 numbers
    for n in N_GRID:
        cp = committed_per_n.get(str(n))
        if cp is None:
            boundary_failures.append(['per_n', n, 'absent'])
            continue
        if cells[(Fraction(0), n)]['dial_ops'] != cp['cegar_ops'] \
                or cells[(Fraction(0), n)]['direct_ops'] != cp['direct_ops']:
            boundary_failures.append(
                ['per_n', n, cells[(Fraction(0), n)]['dial_ops'],
                 cp['cegar_ops'], cells[(Fraction(0), n)]['direct_ops'],
                 cp['direct_ops']])
    if boundary_failures:
        instrument_defects.append(
            'DELTA0_BOUNDARY_DIVERGES:' + json.dumps(boundary_failures[:5]))
    if truth_mismatches:
        instrument_defects.append(
            'VERDICT_MISMATCH_VS_TRUTH:' + json.dumps(truth_mismatches[:5]))
    if strict_run_defects:
        instrument_defects.append(
            'STRICT_RUN_TERMINAL:' + json.dumps(strict_run_defects[:5]))

    # ---- soundness checker: alarm direction (plants) + no-alarm (sound rows)
    sound_violations = check_served_rows(served_rows, worlds_by_id)
    hostile_violations = check_served_rows(hostile_rows, worlds_by_id)
    if sound_violations:
        instrument_defects.append(
            'CHECKER_FALSE_ALARM_ON_SOUND_ROWS:'
            + json.dumps(sound_violations[:5]))
    plant_report = {}
    for p in PLANTS:
        for pd in PLANT_DELTAS:
            rows_p = [r for r in hostile_rows
                      if r['plant'] == p and r['delta_tag'] == _delta_tag(pd)]
            alarms = [v for v in hostile_violations
                      if v[2] == 'ACTUAL_EXCEEDS_CERTIFIED'
                      and any(r['plant'] == p and r['delta_tag'] == v[1]
                              for r in rows_p)]
            flipped = len(alarms) >= 1
            plant_report['%s@%s' % (p, _delta_tag(pd))] = {
                'served_rows': len(rows_p), 'alarms': len(alarms),
                'flipped': flipped,
                'reason_if_silent': (
                    'plant never exercised (no served row)' if not rows_p
                    else 'every served row has actual error <= planted '
                         'bound: alarm direction unvalidated') if not flipped
                    else None}
            if not flipped:
                instrument_defects.append(
                    'HOSTILE_DID_NOT_FLIP:%s@%s' % (p, _delta_tag(pd)))

    # ---- monotonicity of total cost in delta over (0, 1] (envelope
    # soundness premise). delta = 0 is EXCLUDED: it is a different arm
    # family (the dial never engages, so dial_bookkeeping_ops is never
    # charged); a grid delta that never serves costs exact cost PLUS
    # bookkeeping, which legitimately exceeds the delta = 0 cost -- that is
    # a measured property of the curve, not an instrument defect. Within
    # (0, 1]: every full intermediate round (validate + refine + rebuild)
    # costs >= n + 1 > len(U) <= n ops, so serving earlier (larger delta)
    # never costs more among serving arms, and a non-serving arm terminates
    # exact, costing >= the delta = 0 exact arm which already loses to
    # direct everywhere -- so it cannot flip the falsifier either.
    monotone_violations = []
    dial_only = [d for d in scored_deltas if d > 0]
    for n in N_GRID:
        seq = [cells[(d, n)]['dial_ops'] for d in dial_only]
        for i in range(1, len(seq)):
            if seq[i] > seq[i - 1]:
                monotone_violations.append(
                    [n, _delta_tag(scored_deltas[i - 1]),
                     _delta_tag(scored_deltas[i]),
                     seq[i - 1], seq[i]])
    if monotone_violations:
        instrument_defects.append(
            'COST_NOT_MONOTONE_IN_DELTA:' + json.dumps(
                monotone_violations[:5]))

    # ---- per-(delta, n) primary table
    table = {}
    for d in scored_deltas:
        per_n = {}
        for n in N_GRID:
            c = cells[(d, n)]
            per_n[str(n)] = {
                'direct_ops_total': c['direct_ops'],
                'dial_ops_total': c['dial_ops'],
                'ratio_dial_over_direct':
                    round(c['dial_ops'] / max(1, c['direct_ops']), 4),
                'dial_beats_direct': c['dial_ops'] < c['direct_ops'],
                'worlds': c['worlds'], 'worlds_served': c['served'],
                'dial_bookkeeping_ops_total': c['dial_bookkeeping_ops'],
                'rounds_total': c['rounds_total'],
                'mean_blocks_final': round(
                    c['final_blocks_total'] / float(c['worlds']), 3),
                'mean_actual_error_frac_at_serve': round(
                    sum(c['actual_error_fracs'])
                    / max(1, len(c['actual_error_fracs'])), 4)
                if c['actual_error_fracs'] else None,
                'mean_certified_frac_at_serve': round(
                    sum(c['certified_frac_at_serve'])
                    / max(1, len(c['certified_frac_at_serve'])), 4)
                if c['certified_frac_at_serve'] else None}
        table[_delta_tag(d)] = {'delta_frac': '%s/%s' % (
            d.numerator, d.denominator), 'grid_arm':
            d in DELTA_GRID, 'envelope_arm': d == DELTA_ENVELOPE,
            'per_n': per_n}

    # ---- (delta, compression, cost) Pareto frontier over all 30 worlds
    pareto_points = []
    for tag, pi in pareto_inputs.items():
        pareto_points.append({
            'arm': tag, 'kind': 'dial',
            'delta': pi['delta'] if not isinstance(pi['delta'], Fraction)
            else float(pi['delta']),
            'compression_total': round(pi['compression_total'], 4),
            'cost_ops_total': pi['ops_total'],
            'mean_compression': round(
                pi['compression_total'] / float(pi['worlds']), 4),
            'worlds_served': pi['served']})
    tot_direct = sum(cells[(Fraction(0), n)]['direct_ops'] for n in N_GRID)
    pareto_points.append({
        'arm': 'direct', 'kind': 'direct', 'delta': 0.0,
        'compression_total': float(len(worlds)),
        'cost_ops_total': tot_direct,
        'mean_compression': 1.0, 'worlds_served': 0})
    for a in pareto_points:
        a['pareto_optimal'] = not any(
            b is not a
            and b['compression_total'] >= a['compression_total']
            and b['cost_ops_total'] <= a['cost_ops_total']
            and (b['compression_total'] > a['compression_total']
                 or b['cost_ops_total'] < a['cost_ops_total'])
            for b in pareto_points)
    pareto_frontier = [a['arm'] for a in pareto_points if a['pareto_optimal']]

    # ---- falsifier over delta in (0, 1), decided with the envelope arm
    grid_beat_points = [
        [_delta_tag(d), n] for d in DELTA_GRID if d > 0 for n in N_GRID
        if cells[(d, n)]['dial_ops'] < cells[(d, n)]['direct_ops']]
    envelope_beat_points = [
        n for n in N_GRID
        if cells[(DELTA_ENVELOPE, n)]['dial_ops']
        < cells[(DELTA_ENVELOPE, n)]['direct_ops']]
    # bound_num <= n-1 always (init lies in U AND in L), so every envelope
    # serve fires already at delta = bound_num/n < 1: an envelope win proves
    # a win at some delta strictly inside (0, 1)
    falsifier_fired = (not grid_beat_points) and (not envelope_beat_points)

    upper_half_grid_beats = [
        [_delta_tag(d), n] for d in DELTA_GRID
        if Fraction(0) < d <= Fraction(1, 4) for n in UPPER_HALF
        if cells[(d, n)]['dial_ops'] < cells[(d, n)]['direct_ops']]
    boundary_reproduced = not boundary_failures

    clauses = {
        'delta0_reproduces_filed_negative_everywhere': boundary_reproduced,
        'some_grid_delta_beats_direct_at_upper_half':
            bool(upper_half_grid_beats),
        'grid_beat_points': grid_beat_points,
        'envelope_beat_points': envelope_beat_points,
        'upper_half_grid_beat_points': upper_half_grid_beats,
        'cost_monotone_nondecreasing_in_delta_over_open_interval':
            not monotone_violations}

    if instrument_defects:
        terminal = {'verdict': 'CANNOT_CHECK',
                    'reason': '; '.join(instrument_defects[:3]),
                    'defects_total': len(instrument_defects)}
    elif falsifier_fired:
        terminal = {'verdict': 'SELF_DEFEAT_EXTENDS_TO_RELAXED',
                    'statement':
                        'No delta in (0, 1) at ANY grid point makes '
                        'structural capital strictly beat direct on total '
                        'cost: the self-defeat law extends to the relaxed '
                        'regime; the admissible claim shape narrows to '
                        'rho-conditioned only.'}
    else:
        terminal = {'verdict': 'DELTA_FRONTIER_MEASURED',
                    'statement':
                        'total_cost(delta) vs total_cost_direct(n) measured '
                        'on the 30 frozen D20 worlds; see the per-(delta, n) '
                        'table and the Pareto frontier.'}

    if instrument_defects:
        prediction_verdict = 'CANNOT_CHECK'
    elif boundary_reproduced and upper_half_grid_beats:
        prediction_verdict = 'CONFIRMED'
    elif boundary_reproduced:
        prediction_verdict = 'REFUTED'
    else:
        prediction_verdict = 'CANNOT_CHECK'

    out = {
        'experiment': 'D30', 'study': 'delta_dial',
        'protocol': 'ECONOMY_FRONTIER_PROTOCOLS_V1.json#D30_delta_dial',
        'protocol_section': 'D30_delta_dial',
        'registered_prediction_source':
            'ECONOMY_FRONTIER_PROTOCOLS_V1.json#D30_delta_dial.'
            'registered_prediction',
        'freeze_commit': freeze_commit,
        'machinery': 'research/hsg-semantic-execution-v1/exact/d20.py '
                     'IMPORTED UNCHANGED; cegar_dial is a line-for-line '
                     'copy of d20.cegar with the frozen delta dial branch '
                     'between abstract_bfs and validate; worlds, seeds, '
                     'counters and the op metric untouched',
        'dial_semantics': {
            'served_object': 'block-level reachability classification '
                             '(U = union of the FULL abstract closure; '
                             'wrong-no set empty by may-abstraction '
                             'induction)',
            'certified_bound': '|U - L| / n with L = {init} joined with '
                               'every certified concrete prefix-reachable '
                               'set; all arithmetic exact (Fraction)',
            'serve_rule': 'at an abstract counterexample, serve U when '
                          'delta > 0 and certified_bound <= delta; '
                          'delta = 0 never takes the branch',
            'verdict_at_relaxed_stop': 'REPORTED against ground truth, '
                                       'never certified (no verdict-bit '
                                       'claim at delta > 0)',
            'bound_num_leq_n_minus_1': 'init lies in U and in L, so '
                                       'bound_num <= n-1: every envelope '
                                       'serve already fires at delta = '
                                       'bound_num/n < 1'},
        'grid': {'delta': [str(d) for d in DELTA_GRID],
                 'n': list(N_GRID),
                 'envelope_delta': str(DELTA_ENVELOPE)},
        'worlds': len(worlds),
        'total_cost_table': table,
        'pareto': {'points': pareto_points,
                   'frontier_arms': pareto_frontier,
                   'compression_definition':
                       'mean over worlds of n / final_blocks (direct = 1.0: '
                       'per-state exact classification, nothing compressed)'},
        'primary_endpoint': {
            'rule': 'total_cost(delta) vs total_cost_direct(n), totals '
                    'summed over the 6 frozen worlds of each n; dial beats '
                    'direct iff dial_ops_total < direct_ops_total',
            'grid_beat_points': grid_beat_points,
            'envelope_beat_points': envelope_beat_points},
        'registered_prediction': {
            'text': 'delta=0 reproduces the filed negative everywhere '
                    '(boundary of the family); some delta in (0, 0.25] '
                    'beats direct on total cost at n in the upper grid '
                    'half',
            'clauses': clauses,
            'verdict': prediction_verdict},
        'falsifier': {
            'text': 'no delta in (0, 1) at which structural capital '
                    'strictly beats direct on total cost at ANY grid point',
            'fired': falsifier_fired,
            'decision_rule': 'grid deltas decide (0, 0.25]; the delta=1.0 '
                             'envelope arm decides (0.25, 1): within (0,1] '
                             'cost is non-increasing in delta (every full '
                             'intermediate round costs >= n+1 > len(U) <= '
                             'n ops, asserted at run time), and a non-'
                             'serving delta terminates exact, costing at '
                             'least the delta=0 arm which already loses to '
                             'direct everywhere'},
        'terminal': terminal,
        'cost_ledger_hdi14': {
            'families': HDI14_LEDGER,
            'ledger_complete': led_ok,
            'missing': led_missing,
            'note': 'the frozen D20 op metric IS the charged ledger '
                    '(identical counter families both arms); the dial '
                    'adds dial_bookkeeping_ops (adaptation) at delta > 0 '
                    'only; retained-state bytes are measured additionally '
                    'and NOT added to the op metric (charging them can '
                    'only increase dial cost, so measured comparisons are '
                    'conservative for direct)'},
        'controls': {
            'delta0_identity_vs_live_frozen_cegar':
                not any(f[1] != 'per_n' and f[1] != 'negative_lost'
                        for f in boundary_failures),
            'delta0_negative_retained_per_world':
                not any(f[1] == 'negative_lost' for f in boundary_failures),
            'delta0_per_n_totals_vs_committed_D20':
                not any(f[0] == 'per_n' for f in boundary_failures),
            'soundness_checker': {
                'checked_rows': len(served_rows),
                'violations_on_sound_rows': sound_violations,
                'no_alarm_control_silent': not sound_violations},
            'hostile_plants': plant_report,
            'frozen_reachable_field_drift':
                [d for d in instrument_defects
                 if d.startswith('FROZEN_REACHABLE_DRIFT')],
            'shuffle_equal_n_null': {
                'applicable': False,
                'reason': 'no random element anywhere in the measured '
                          'comparison: frozen worlds and seeds, '
                          'deterministic arms, no query stream, no draw, '
                          'no adaptive selection over a sample; the only '
                          '1-bit quantities (relaxed vs truth verdicts) '
                          'are REPORTED, never scored, so no '
                          'draw-invariance control attaches'}},
        'instrument_defects': instrument_defects,
        'wall_s': round(time.time() - t0w, 4),
        'cpu_s': round(time.process_time() - t0c, 4),
        'host': host_label,
        'python': platform.python_version(),
        'claim_ceiling': 'P2 finite certificate over the 30 frozen D20 '
                         'worlds and the swept grid; no universal claim'}
    return out, receipts


def prediction_line(out):
    rp = out['registered_prediction']
    c = rp['clauses']
    return ('%s (boundary=%s, upper_half_beats=%s, grid_beats=%d, '
            'envelope_beats=%s)') % (
        rp['verdict'],
        c['delta0_reproduces_filed_negative_everywhere'],
        c['some_grid_delta_beats_direct_at_upper_half'],
        len(c['grid_beat_points']),
        c['envelope_beat_points'])


def main():
    freeze_commit = os.environ.get('D30_FREEZE_COMMIT', 'UNSET')
    host_label = os.environ.get('D30_HOST_LABEL', platform.node())
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'receipts'), exist_ok=True)
    out, rec = run_d30(freeze_commit, host_label)

    res_path = os.path.join(HERE, 'results', 'D30_DELTA_DIAL_RESULTS.json')
    rec_path = os.path.join(HERE, 'receipts', 'D30_receipts.jsonl')
    with open(res_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, sort_keys=True, default=repr)
        f.write('\n')
    with open(rec_path, 'w', encoding='utf-8') as f:
        for row in rec:
            f.write(json.dumps(row, sort_keys=True, default=repr) + '\n')

    # host receipt binds code + protocol + outputs (byte-repro chain)
    research = os.path.dirname(os.path.dirname(HERE))
    proto = os.path.join(research, 'top-tier-atomic-closure-v1',
                         'ECONOMY_FRONTIER_PROTOCOLS_V1.json')
    amend = os.path.join(research, 'top-tier-atomic-closure-v1',
                         'QUERY_ECOLOGY_AMENDMENT_V1.json')
    host_rec = {
        'job': 'D30', 'host': host_label, 'hostname': platform.node(),
        'python': platform.python_version(),
        'system': '; '.join(platform.uname()),
        'freeze_commit': freeze_commit,
        'run_d30_sha256': _sha256_file(os.path.join(HERE, 'run_d30.py')),
        'd20_sha256': _sha256_file(os.path.join(HERE, 'd20.py')),
        'worlds_sha256': _sha256_file(os.path.join(HERE, 'worlds.py')),
        'worlds_d19d20_sha256': _sha256_file(
            os.path.join(HERE, 'worlds_d19d20.py')),
        'committed_d20_results_sha256':
            _sha256_file(os.path.join(HERE, 'results', 'D20_RESULTS.json')),
        'economy_frontier_protocol_sha256':
            _sha256_file(proto) if os.path.exists(proto) else 'ABSENT',
        'query_ecology_amendment_sha256':
            _sha256_file(amend) if os.path.exists(amend) else 'ABSENT',
        'results_sha256': _sha256_file(res_path),
        'receipts_sha256': _sha256_file(rec_path),
        'host_swap_note': 'billy-laptop used because billy-old is occupied '
                          'by another lane; per ECONOMY_FRONTIER_PROTOCOLS '
                          'common_rules (disjoint host, never Mac mini)',
        'rng_draws': 'none: fully deterministic machinery, frozen seeds '
                     'unchanged'}
    hr_path = os.path.join(HERE, 'receipts',
                           'D30_HOST_RECEIPT_%s.json' % host_label)
    with open(hr_path, 'w', encoding='utf-8') as f:
        json.dump(host_rec, f, indent=1, sort_keys=True)
        f.write('\n')

    print('D30 terminal:', out['terminal']['verdict'])
    print('  per-(delta, n) dial-vs-direct ratio table:')
    for tag in ['0', '1/100', '1/20', '1/10', '1/4', '1']:
        t = out['total_cost_table'][tag]
        for n in [str(x) for x in N_GRID]:
            d = t['per_n'][n]
            print('    delta=%-5s n=%-2s dial=%-6d direct=%-6d ratio=%-7s '
                  'beats=%-5s served=%d/%d'
                  % (tag, n, d['dial_ops_total'], d['direct_ops_total'],
                     d['ratio_dial_over_direct'], d['dial_beats_direct'],
                     d['worlds_served'], d['worlds']))
    print('  Pareto frontier arms:', out['pareto']['frontier_arms'])
    print('  prediction verdict:', prediction_line(out))
    print('  plants:', json.dumps(
        dict((k, v['flipped']) for k, v in
             out['controls']['hostile_plants'].items()), sort_keys=True))
    print('  instrument defects:', len(out['instrument_defects']))
    print('  wall_s', out['wall_s'], 'cpu_s', out['cpu_s'],
          'host', host_label)
    if out['terminal']['verdict'] == 'CANNOT_CHECK':
        return 5
    return 0


if __name__ == '__main__':
    sys.exit(main())
