"""Conventional prefix continuation of the checked #205 failure-point memory.

Every candidate, counterexample and final proof is still decided by methods.solve.
Only exact point interpretation is substituted. This is a research adapter, not
an OCM core or a source of authority for its own admission.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations, product
from pathlib import Path
import time
from types import MappingProxyType
from typing import Any

import experiment as E

KINDS = ('P0', 'P1', 'P2')
SCHEMA = 'g3.prefix-representation.v1'
SCOPE = E.Scope.of(SCHEMA)


@dataclass(frozen=True)
class TrieNode:
    edges: Any
    values: Any


@dataclass(frozen=True)
class PrefixIndex:
    context_bytes: bytes
    nodes: tuple[TrieNode, ...]
    certificates: int

    def __len__(self):
        return self.certificates

    def longest(self, program, x, counts):
        """Return (prefix length, exact value, certificate); count actual lookups."""
        node = 0
        counts['terminal_lookups'] += 1
        value = self.nodes[0].values.get(x)
        best = (0, *value) if value is not None else None
        for length, instruction in enumerate(program, 1):
            counts['edge_lookups'] += 1
            next_node = self.nodes[node].edges.get(instruction)
            if next_node is None:
                break
            node = next_node
            counts['terminal_lookups'] += 1
            value = self.nodes[node].values.get(x)
            if value is not None:
                best = (length, *value)
        return best


def build(records, kind, requested_context=None):
    E.require(kind in KINDS, 'unknown representation')
    if kind == 'P0':
        return None, {}
    ctx = E.context() if requested_context is None else requested_context
    point, meters = E.index_records(records, ctx)
    if kind == 'P1':
        return point, meters
    edges = [{}]
    values = [{}]
    counts = Counter(meters)
    for (program, x), (value, certificate) in point.entries.items():
        node = 0
        for instruction in program:
            counts['build_edge_lookups'] += 1
            child = edges[node].get(instruction)
            if child is None:
                child = len(edges)
                edges[node][instruction] = child
                edges.append({}); values.append({})
                counts['build_edges'] += 1
            node = child
        E.require(x not in values[node], 'duplicate terminal')
        values[node][x] = (value, certificate)
        counts['build_terminals'] += 1
    nodes = tuple(TrieNode(MappingProxyType(dict(e)), MappingProxyType(dict(v)))
                  for e, v in zip(edges, values))
    counts['trie_nodes'] = len(nodes)
    return PrefixIndex(E.encoded(ctx), nodes, len(point)), dict(counts)


def point_value(program, x, index, counts, used):
    """Compute E(program,x), possibly using a checked value for a prefix."""
    counts['point_calls'] += 1
    if index:
        if isinstance(index, E.PointIndex):
            counts['lookups'] += 1
            found = index.get((tuple(program), x))
            if found is not None:
                value, certificate = found
                counts['hits'] += 1
                counts['full_hits'] += 1
                counts['avoided_interpreter_steps'] += len(program)
                used[certificate] += 1
                return value
        elif isinstance(index, PrefixIndex):
            found = index.longest(program, x, counts)
            if found is not None:
                length, value, certificate = found
                counts['hits'] += 1
                counts['full_hits' if length == len(program) else 'proper_prefix_hits'] += 1
                counts['avoided_interpreter_steps'] += length
                if length > 0 and length < len(program):
                    counts['positive_proper_prefix_hits'] += 1
                used[certificate] += 1
                suffix = program[length:]
                if suffix:
                    counts['interpreter_calls'] += 1
                    counts['interpreter_steps'] += len(suffix)
                    return E.REAL_EXECUTE(suffix, value)
                return value
        else:
            raise ValueError('unqualified representation')
    counts['interpreter_calls'] += 1
    counts['interpreter_steps'] += len(program)
    return E.REAL_EXECUTE(program, x)


def solve(task, budget=E.BUDGET, index=None, environment='rational-total.v1'):
    counts, used = Counter(), Counter()
    ctx = E.context(budget, environment)
    if index is not None:
        E.require(isinstance(index, (E.PointIndex, PrefixIndex)), 'unqualified representation')
        if index.context_bytes != E.encoded(ctx):
            counts['context_reopens'] += 1
            index = None
    original = E.M.execute
    E.require(original is E.REAL_EXECUTE, 'nested/concurrent interpreter substitution')
    def point(program, x):
        return point_value(program, x, index, counts, used)
    wall, cpu = time.perf_counter(), time.process_time()
    E.M.execute = point
    try:
        result = E.M.solve(task, budget)
    finally:
        E.M.execute = original
    return {'result': result.as_dict(), 'counts': dict(counts), 'used': dict(used),
            'wall_seconds': time.perf_counter() - wall,
            'cpu_seconds': time.process_time() - cpu}


def totals(rows):
    c = Counter()
    for row in rows:
        c.update(row['counts'])
    return dict(c)


def selection_key(kind, rows):
    c = totals(rows)
    return (c.get('interpreter_steps', 0),
            sum(c.get(k, 0) for k in ('lookups', 'edge_lookups', 'terminal_lookups')),
            KINDS.index(kind))


def choose(validation):
    E.require(list(validation) == list(KINDS), 'incomplete selection population')
    reference = None
    for kind, rows in validation.items():
        E.require(type(rows) is list and len(rows) > 0, 'empty validation')
        results = [r['result'] for r in rows]
        identities = [r['task_fingerprint'] for r in results]
        E.require(len(set(identities)) == len(identities), 'duplicate validation task')
        if reference is None:
            reference = results
        E.require(results == reference, 'selection changes solver semantics')
    return min(KINDS, key=lambda k: selection_key(k, validation[k]))


def observer_certificate(programs, points):
    """Finite all-pairs adequacy for Q0's proposed EVAL(0) quotient.

This is a proof of the declared finite observation table only. It does not
assert adequacy for all future operations, states, or input points.
"""
    ps = tuple(sorted({E.M.checked_program(p) for p in programs}))
    E.require(len(ps) > 1 and points and all(type(x) is int for x in points), 'observer population')
    points = tuple(sorted(set(points)))
    for a, b in combinations(ps, 2):
        # Independent symbolic evaluation rather than candidate interpreter.
        ca, cb = E.M.normal_form(a), E.M.normal_form(b)
        if E.M.evaluate_polynomial(ca, 0) != E.M.evaluate_polynomial(cb, 0):
            continue
        for x in points:
            va = E.M.evaluate_polynomial(ca, x)
            vb = E.M.evaluate_polynomial(cb, x)
            if va != vb:
                return {'terminal': 'REPRESENTATION_INSUFFICIENT',
                        'observer_points': list(points), 'programs_digest': E.digest(ps),
                        'witness': {'left': list(a), 'right': list(b), 'point': x,
                                    'common_at_zero': str(E.M.evaluate_polynomial(ca, 0)),
                                    'left_value': str(va), 'right_value': str(vb)},
                        'reason': 'same proposed block, distinct protected observation'}
    return {'terminal': 'ADEQUATE_FOR_DECLARED_FINITE_OBSERVATIONS',
            'observer_points': list(points), 'programs_digest': E.digest(ps),
            'witness': None}


def certificate_applicable(receipt, programs, points):
    # Receipts are checked again, not trusted as authority.
    recomputed = observer_certificate(programs, points)
    return receipt == recomputed and recomputed['witness'] is None


def diagnose(*, observation_witness=None, solver_status=None):
    """Only two justified diagnostics; this is NOT the full G3.4 classifier."""
    if observation_witness is not None:
        E.require(observation_witness.get('terminal') == 'REPRESENTATION_INSUFFICIENT', 'not a representation witness')
        w = observation_witness['witness']
        left, right = E.M.checked_program(w['left']), E.M.checked_program(w['right'])
        x = w['point']
        E.require(type(x) is int, 'invalid diagnostic point')
        a = E.M.evaluate_polynomial(E.M.normal_form(left), x)
        b = E.M.evaluate_polynomial(E.M.normal_form(right), x)
        E.require(E.M.evaluate_polynomial(E.M.normal_form(left), 0) ==
                  E.M.evaluate_polynomial(E.M.normal_form(right), 0) and a != b and
                  str(a) == w['left_value'] and str(b) == w['right_value'], 'invalid diagnostic witness')
        return 'REPRESENTATION_INSUFFICIENT'
    if solver_status in ('BUDGET_EXHAUSTED', 'UNKNOWN', 'TIMEOUT'):
        return 'RESOURCE_BOUND'
    return 'CANNOT_CHECK'


def representation_source():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def admit(root, memory, selected, selection_digest, qualification_digest):
    """External research controller admits selection with conjunctive support."""
    E.require(selected in KINDS, 'unknown selected representation')
    records, state = E.load_ocm(root, memory)
    E.require(state['live'], 'cannot admit from withdrawn memory')
    build(records, selected)
    rt = E.OCMRuntime(root)
    payload = {'kind': SCHEMA, 'selected': selected, 'context': E.context(),
               'memory': memory, 'selection_digest': selection_digest,
               'qualification_digest': qualification_digest,
               'representation_source': representation_source(),
               'authority_scope': 'external authored research-controller adoption; not autonomous self-certification'}
    _, assurance = rt.admit_evidence(payload, E.Channel.PROOF, SCHEMA, scope=SCOPE)
    warrant = E.WarrantProfile.of({assurance, memory['evidence']})
    oid = 'prefix-representation:' + E.content_hash(payload)
    edge = E.Hyperedge('support:' + oid, (memory['object_id'],), (oid,), 'SUPPORT', warrant=warrant)
    rt.admit_object(E.Atom(oid, 'procedure', warrant, scope=SCOPE,
                          content_ref=E.content_hash(payload), meta=tuple(payload.items())),
                    (edge,), 'OBSERVATION')
    rt.persist()
    return {'object_id': oid, 'assurance': assurance, 'payload_digest': E.digest(payload)}


def load(root, memory, representation):
    records, memory_state = E.load_ocm(root, memory)
    rt = E.OCMRuntime(root)
    atom = rt.state.ks.atom_map().get(representation['object_id'])
    E.require(atom is not None and atom.atom_type == 'procedure', 'missing representation')
    payload = dict(atom.meta)
    E.require(E.digest(payload) == representation['payload_digest'] and
              E.content_hash(payload) == atom.content_ref, 'representation identity')
    E.require(payload['kind'] == SCHEMA and payload['memory'] == memory and
              payload['context'] == E.context() and
              payload['representation_source'] == representation_source(), 'representation source/context binding')
    # Check actual warrant shape, not merely a state flag or callback decision.
    expected = E.WarrantProfile.of({representation['assurance'], memory['evidence']})
    E.require(atom.warrant == expected, 'missing conjunctive dependency')
    live = atom.liveness(rt.state.revoked) is E.Liveness.LIVE
    selected = payload['selected'] if live else ('P1' if memory_state['live'] else 'P0')
    E.require(not live or memory_state['live'], 'representation live without memory')
    return records, selected, {'memory_live': memory_state['live'], 'representation_live': live,
                               'field_hash': rt.state.kso_state_hash,
                               'evidence_epoch': rt.state.evidence_epoch,
                               'event_count': len(rt.trace())}
