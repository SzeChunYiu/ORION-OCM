"""Research adapters: bounded failure certificates and operation-bound quotients.

No certificate below asserts global impossibility. Polynomial primitives and the
final checker are imported from the unchanged OCM learner. All controller choices
and feature menus are declared priors in PROTOCOL.md.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from fractions import Fraction
from itertools import product
from pathlib import Path
from collections import deque
from typing import Any, Iterable
import hashlib
import io
import json
import sys
import zipfile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'src'))
from ocm.learning import methods as M

SCHEMA = 'ocm.g3.scoped-development.v1'
MACRO = ('square', 'dec', 'square')
FEATURES = ('degree', 'value0', 'value1', 'leading')
REPRESENTATIONS = ('value0', 'value01', 'coefficients', 'coefficients-last')
RECORDED_RESULT = '896b39429a4fd520cfc7517e73cdd0efb27518a83d7e31f9e6cf99560401db49'


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def encoded(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def digest(x: Any) -> str:
    return hashlib.sha256(encoded(x)).hexdigest()


def raw_digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> Any:
    def unique(items):
        out = {}
        for k, v in items:
            require(k not in out, 'DUPLICATE_JSON_KEY')
            out[k] = v
        return out
    def refuse(x):
        raise ValueError('NONFINITE_JSON_' + x)
    return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=refuse)


def coefficients(values: Iterable[Any]) -> tuple[Fraction, ...]:
    vals = tuple(Fraction(v) for v in values)
    require(bool(vals) and len(vals) <= 257, 'COEFFICIENT_SHAPE')
    require(all(abs(v.numerator).bit_length() <= 4096 and v.denominator.bit_length() <= 4096
                for v in vals), 'COEFFICIENT_BOUND')
    while len(vals) > 1 and not vals[-1]:
        vals = vals[:-1]
    return vals


def wire(poly) -> list[str]:
    return [str(v) for v in coefficients(poly)]


def feature(poly, name: str) -> str:
    p = coefficients(poly)
    require(name in FEATURES, 'UNREGISTERED_FEATURE')
    return str({'degree': len(p) - 1, 'value0': p[0], 'value1': sum(p), 'leading': p[-1]}[name])


def step(poly, token: str) -> tuple[Fraction, ...]:
    """Incremental algebra, cross-checked against the existing whole-program checker."""
    p = list(coefficients(poly))
    if token == 'inc': p[0] += 1
    elif token == 'dec': p[0] -= 1
    elif token == 'double': p = [2 * v for v in p]
    elif token == 'square':
        q = [Fraction(0)] * (2 * len(p) - 1)
        for i, a in enumerate(p):
            for j, b in enumerate(p): q[i + j] += a * b
        p = q
    else: raise ValueError('UNREGISTERED_PRIMITIVE')
    return coefficients(p)


def scalar_check(program, poly) -> bool:
    """A second arithmetic path: degree+1 exact point evaluations certify identity.

    The degree bound follows by induction from x and the declared four operators.
    This is finite polynomial identity checking, not empirical spot checking.
    """
    if len(program) > 8 or any(t not in M.PRIMITIVES for t in program): return False
    p = coefficients(poly)
    degree_bound = max(2 ** tuple(program).count('square'), len(p) - 1)
    for x in range(degree_bound + 1):
        y = Fraction(x)
        for t in program:
            if t == 'inc': y += 1
            elif t == 'dec': y -= 1
            elif t == 'double': y *= 2
            else: y *= y
        z = Fraction(0)
        for v in reversed(p): z = z * x + v
        if y != z: return False
    return True


@dataclass(frozen=True)
class MethodScope:
    prefix: tuple[str, ...] = MACRO
    grammar: tuple[str, ...] = M.PRIMITIVES
    max_length: int = 5
    attempts: int = 200_000
    environment: str = 'polynomial-integers.v1'
    checker: str = M.CHECKER
    source: str = ''

    def __post_init__(self):
        require(type(self.prefix) is tuple and 1 <= len(self.prefix) <= 8 and
                all(t in M.PRIMITIVES for t in self.prefix), 'PREFIX')
        require(type(self.grammar) is tuple and 0 < len(self.grammar) <= 4 and
                len(set(self.grammar)) == len(self.grammar) and
                all(t in M.PRIMITIVES for t in self.grammar), 'GRAMMAR')
        require(type(self.max_length) is int and len(self.prefix) <= self.max_length <= 8, 'LENGTH')
        require(type(self.attempts) is int and 0 < self.attempts <= 200_000, 'ATTEMPTS')
        require(type(self.environment) is str and bool(self.environment), 'ENVIRONMENT')
        require(self.checker == M.CHECKER, 'CHECKER')
        require(type(self.source) is str and len(self.source) == 64 and
                all(c in '0123456789abcdef' for c in self.source), 'SOURCE')

    def data(self): return json.loads(encoded(asdict(self)))

    @classmethod
    def parse(cls, data):
        require(type(data) is dict and set(data) == set(cls.__dataclass_fields__), 'SCOPE_FIELDS')
        d = dict(data)
        require(type(d['prefix']) is list and type(d['grammar']) is list, 'SCOPE_LISTS')
        d['prefix'], d['grammar'] = tuple(d['prefix']), tuple(d['grammar'])
        return cls(**d)


def candidate_programs(scope: MethodScope):
    for length in range(scope.max_length - len(scope.prefix) + 1):
        for suffix in product(scope.grammar, repeat=length):
            yield scope.prefix + suffix


def prefix_search(target, scope: MethodScope, occurrence: str) -> dict:
    target = coefficients(target)
    require(type(occurrence) is str and bool(occurrence), 'OCCURRENCE')
    visited = []
    terminal = 'BOUNDED_METHOD_EXHAUSTED'
    winner = None
    for p in candidate_programs(scope):
        if len(visited) >= scope.attempts:
            terminal = 'RESOURCE_BOUND'
            break
        poly = M.normal_form(p)
        visited.append({'program': list(p), 'coefficients': wire(poly)})
        if poly == target:
            terminal, winner = 'VERIFIED_POLYNOMIAL_IDENTITY', list(p)
            break
    record = {'schema': SCHEMA + '.attempt', 'occurrence': occurrence,
              'scope': scope.data(), 'target': wire(target), 'terminal': terminal,
              'program': winner, 'visited': visited, 'checked_programs': len(visited),
              'failure_kind': 'METHOD_FAILURE' if winner is None else None,
              'task_impossibility': False}
    return record


def validate_attempt(record: dict) -> int:
    """Independent queue enumeration, not the producer's Cartesian-product iterator."""
    require(type(record) is dict and set(record) == {'schema','occurrence','scope','target','terminal',
            'program','visited','checked_programs','failure_kind','task_impossibility'}, 'ATTEMPT_FIELDS')
    require(record['schema'] == SCHEMA + '.attempt' and record['task_impossibility'] is False,
            'ATTEMPT_CLAIM')
    require(type(record['occurrence']) is str and bool(record['occurrence']), 'ATTEMPT_OCCURRENCE')
    s = MethodScope.parse(record['scope'])
    target = coefficients(record['target'])
    queue = deque([s.prefix]); expected = []; winner = None
    terminal = 'BOUNDED_METHOD_EXHAUSTED'
    while queue:
        if len(expected) >= s.attempts:
            terminal = 'RESOURCE_BOUND'; break
        p = queue.popleft()
        poly = M.normal_form(p)
        require(scalar_check(p, poly), 'INDEPENDENT_COEFFICIENT_CHECK')
        expected.append({'program': list(p), 'coefficients': wire(poly)})
        if poly == target:
            terminal, winner = 'VERIFIED_POLYNOMIAL_IDENTITY', list(p); break
        if len(p) < s.max_length:
            queue.extend(p + (t,) for t in s.grammar)
    require(record['visited'] == expected and type(record['checked_programs']) is int and
            record['checked_programs'] == len(expected), 'INCOMPLETE_OR_FORGED_SEARCH')
    require(record['terminal'] == terminal and record['program'] == winner and
            record['failure_kind'] == ('METHOD_FAILURE' if winner is None else None), 'FALSE_TERMINAL')
    return len(expected)


def learn_guard(record: dict) -> dict | None:
    validate_attempt(record)
    if record['terminal'] != 'BOUNDED_METHOD_EXHAUSTED': return None
    for f in FEATURES:
        values = sorted({feature(row['coefficients'], f) for row in record['visited']})
        if feature(record['target'], f) not in values:
            return {'schema': SCHEMA + '.guard', 'scope': record['scope'], 'feature': f,
                    'reachable_values': values, 'origin_attempt': digest(record),
                    'meaning': 'SKIP_THIS_COMPLETE_BOUNDED_PREFIX_ONLY'}
    return None


def validate_guard(guard: dict, attempt: dict) -> int:
    require(type(guard) is dict and set(guard) == {'schema','scope','feature','reachable_values',
            'origin_attempt','meaning'}, 'GUARD_FIELDS')
    count = validate_attempt(attempt)
    require(attempt['terminal'] == 'BOUNDED_METHOD_EXHAUSTED', 'FAILURE_NOT_COMPLETE')
    require(guard['schema'] == SCHEMA + '.guard' and guard['scope'] == attempt['scope'] and
            guard['origin_attempt'] == digest(attempt) and
            guard['meaning'] == 'SKIP_THIS_COMPLETE_BOUNDED_PREFIX_ONLY', 'GUARD_BINDING')
    f = guard['feature']; require(f in FEATURES, 'GUARD_FEATURE')
    values = sorted({feature(row['coefficients'], f) for row in attempt['visited']})
    require(guard['reachable_values'] == values and feature(attempt['target'], f) not in values,
            'GUARD_GENERALIZATION')
    return count


def guard_applies(guard: dict, target, scope: MethodScope) -> bool:
    """Caller must have validated and currently authorized the certificate."""
    require(guard['schema'] == SCHEMA + '.guard' and guard['feature'] in FEATURES, 'GUARD_UNCHECKED')
    return guard['scope'] == scope.data() and feature(target, guard['feature']) not in guard['reachable_values']


def primitive_search(target, max_length: int = 5, key_name: str | None = None,
                     observer: str = 'coefficients', max_checks: int = 200_000) -> dict:
    require(type(max_length) is int and 0 <= max_length <= 8, 'SEARCH_BOUND')
    require(type(max_checks) is int and max_checks > 0, 'SEARCH_BUDGET')
    require(key_name is None or key_name in REPRESENTATIONS, 'SEARCH_KEY')
    require(observer in ('coefficients', 'coefficients-last'), 'OBSERVER')
    target = coefficients(target)
    queue = deque([((), (Fraction(0), Fraction(1)))])
    seen = set(); checked = expanded = dropped = 0
    while queue:
        if checked >= max_checks:
            return {'terminal':'RESOURCE_BOUND','program':None,'checked_programs':checked,
                    'generated_edges':expanded,'duplicate_states_dropped':dropped}
        p, poly = queue.popleft()
        if key_name:
            key = representation_key(p, poly, key_name)
            if key in seen: dropped += 1; continue
            seen.add(key)
        checked += 1
        if poly == target:
            return {'terminal':'VERIFIED_POLYNOMIAL_IDENTITY','program':list(p),
                    'checked_programs':checked,'generated_edges':expanded,
                    'duplicate_states_dropped':dropped}
        if len(p) < max_length:
            for t in M.PRIMITIVES:
                queue.append((p+(t,), step(poly,t))); expanded += 1
    return {'terminal':'EXHAUSTED_DECLARED_GRAMMAR','program':None,'checked_programs':checked,
            'generated_edges':expanded,'duplicate_states_dropped':dropped}


def solve_with_guard(target, scope: MethodScope, guard: dict | None, occurrence: str) -> dict:
    skipped = guard is not None and guard_applies(guard, target, scope)
    attempt = None if skipped else prefix_search(target, scope, occurrence)
    if attempt and attempt['terminal'] == 'VERIFIED_POLYNOMIAL_IDENTITY':
        result = {'terminal': attempt['terminal'], 'program': attempt['program'],
                  'checked_programs': 0, 'generated_edges':0, 'duplicate_states_dropped':0}
    else:
        result = primitive_search(target, scope.max_length)
    return {'result': result, 'prefix_attempt': attempt, 'guard_consumed': digest(guard) if skipped else None,
            'guard_lookups': int(guard is not None),
            'prefix_checks': 0 if skipped else attempt['checked_programs'],
            'fallback_checks': result['checked_programs'],
            'method_used': bool(attempt and attempt['program']), 'task_impossibility':False}


def representation_key(program, poly, name: str):
    require(name in REPRESENTATIONS, 'REPRESENTATION')
    p = coefficients(poly); depth = len(program)
    if name == 'value0': return (depth, p[0])
    if name == 'value01': return (depth, p[0], sum(p))
    if name == 'coefficients': return (depth, p)
    return (depth, p, program[-1] if program else None)


def observation(program, poly, observer: str):
    require(observer in ('coefficients','coefficients-last'), 'OBSERVATION_INVENTORY')
    return (wire(poly), program[-1] if program else None) if observer.endswith('-last') else wire(poly)


def all_states(bound: int):
    require(type(bound) is int and 0 <= bound <= 7, 'VALIDATION_BOUND')
    rows = [((), (Fraction(0),Fraction(1)))]; layer = list(rows)
    for _ in range(bound):
        layer = [(p+(t,),step(poly,t)) for p,poly in layer for t in M.PRIMITIVES]
        rows.extend(layer)
    return rows


def validate_representation(name: str, observer: str, bound: int, states=None) -> dict:
    require(name in REPRESENTATIONS and observer in ('coefficients','coefficients-last'), 'REP_CONTRACT')
    rows = all_states(bound) if states is None else states
    groups = {}; comparisons = transitions = 0
    for p, poly in rows:
        key = representation_key(p,poly,name)
        if key not in groups: groups[key]=(p,poly); continue
        q, other = groups[key]; comparisons += 1
        if observation(p,poly,observer) != observation(q,other,observer):
            return {'valid':False,'name':name,'observer':observer,'bound':bound,
                    'checked_states':comparisons+len(groups),'transition_checks':transitions,
                    'witness':{'left':list(q),'right':list(p),'left_observation':observation(q,other,observer),
                               'right_observation':observation(p,poly,observer),'reason':'OBSERVATION_ALIAS'}}
        if len(p)<bound:
            for t in M.PRIMITIVES:
                transitions += 1
                if representation_key(p+(t,),step(poly,t),name) != representation_key(q+(t,),step(other,t),name):
                    return {'valid':False,'name':name,'observer':observer,'bound':bound,
                            'checked_states':comparisons+len(groups),'transition_checks':transitions,
                            'witness':{'left':list(q),'right':list(p),'action':t,'reason':'SUCCESSOR_ALIAS'}}
    return {'valid':True,'name':name,'observer':observer,'bound':bound,'states':len(rows),
            'groups':len(groups),'comparisons':comparisons,'transition_checks':transitions,'witness':None}


def select_representation(observer: str, bound: int) -> dict:
    trials=[]
    for name in REPRESENTATIONS:
        trial=validate_representation(name,observer,bound); trials.append(trial)
        if trial['valid']:
            return {'schema':SCHEMA+'.representation','name':name,'observer':observer,'bound':bound,
                    'grammar':list(M.PRIMITIVES),'trials':trials,'contract':'current-observation+depth+ordered-successors'}
    raise ValueError('NO_VALID_REPRESENTATION')


def validate_representation_certificate(cert:dict, observer: str, bound: int) -> None:
    require(encoded(cert) == encoded(select_representation(observer,bound)), 'STALE_OR_FORGED_REPRESENTATION')


def diagnose(packet: dict) -> dict:
    from diagnosis import diagnose as checked_diagnosis
    return checked_diagnosis(packet)


def recover_method() -> dict:
    path=REPO/'research/g2-macro-source-reconciliation-v1/RAW.zip'
    with zipfile.ZipFile(path) as z:
        with zipfile.ZipFile(io.BytesIO(z.read('reconciliation/aggregate-artifact.zip'))) as inner:
            raw=inner.read('result.json')
    require(raw_digest(raw)==RECORDED_RESULT,'IMPORTED_RESULT_IDENTITY')
    data=json.loads(raw); require(tuple(data['selected_macro'])==MACRO,'IMPORTED_MACRO_IDENTITY')
    return {'macro':list(MACRO),'source_result':RECORDED_RESULT,'source_atom':data['ocm']['atom_id'],
            'origin':'IMPORTED_PREVIOUSLY_ACQUIRED_NOT_NEW_ACQUISITION','historical_acquisition_paid_back':False,
            'historical_terminal':data['terminal'],'historical_lifetime_terminal':data['lifetime_terminal']}


def census() -> list[dict]:
    first={}
    for p,poly in all_states(5): first.setdefault(poly,p)
    return [{'coefficients':wire(poly),'minimum_length':len(p),'identity':digest(wire(poly))}
            for poly,p in sorted(first.items(),key=lambda item:wire(item[0])) if 3<=len(p)<=5]
