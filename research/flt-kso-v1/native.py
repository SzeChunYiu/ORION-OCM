"""Small explicit equality proof operator. No checker authority, IO or model calls.

Only a candidate constructor. The same constructor is the conventional parent:
this first microscope does not claim a search advantage over that parent.
"""
from __future__ import annotations
from collections import deque
from dataclasses import asdict, dataclass
import hashlib
import json
import re


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class EqualityTask:
    variables: tuple[str, ...]
    hypotheses: tuple[tuple[str, str], ...]
    target: tuple[str, str]

    def __post_init__(self):
        object.__setattr__(self, 'variables', tuple(self.variables))
        object.__setattr__(self, 'hypotheses', tuple(tuple(h) for h in self.hypotheses))
        object.__setattr__(self, 'target', tuple(self.target))
        if not 1 <= len(self.variables) <= 32 or len(set(self.variables)) != len(self.variables):
            raise ValueError('VARIABLE_IDENTITY_COLLISION_OR_BOUND')
        if any(type(v) is not str or re.fullmatch(r'[a-z][a-z0-9_]{0,31}', v) is None
               for v in self.variables):
            raise ValueError('INVALID_VARIABLE')
        if len(self.hypotheses) > 256:
            raise ValueError('HYPOTHESIS_BOUND')
        for pair in (*self.hypotheses, self.target):
            if len(pair) != 2 or any(v not in self.variables for v in pair):
                raise ValueError('UNKNOWN_VARIABLE')

    def as_dict(self):
        return asdict(self)

    @property
    def statement_id(self):
        return identity(self.as_dict())


def endpoints(task, proof, depth=0):
    """Independent total verifier for the tiny AST; NOT a Lean kernel receipt."""
    if depth > 64 or type(proof) not in (list, tuple) or not proof:
        raise ValueError('INVALID_PROOF_AST')
    op, *args = proof
    if op == 'hyp' and len(args) == 1:
        i = args[0]
        if type(i) is not int or not 0 <= i < len(task.hypotheses):
            raise ValueError('INVALID_HYPOTHESIS')
        return task.hypotheses[i]
    if op == 'refl' and len(args) == 1 and args[0] in task.variables:
        return (args[0], args[0])
    if op == 'symm' and len(args) == 1:
        a, b = endpoints(task, args[0], depth + 1)
        return (b, a)
    if op == 'trans' and len(args) == 2:
        a, b = endpoints(task, args[0], depth + 1)
        c, d = endpoints(task, args[1], depth + 1)
        if b != c:
            raise ValueError('MIDDLE_TERM_MISMATCH')
        return (a, d)
    raise ValueError('UNREGISTERED_PROOF_OPERATOR')


def validate_proof(task, proof):
    try:
        return endpoints(task, proof) == task.target
    except (ValueError, TypeError, IndexError, RecursionError):
        return False


def statement(task):
    # User-supplied labels are never interpolated into executable Lean source.
    names = {v: f'v{i}' for i, v in enumerate(task.variables)}
    binders = ' '.join(names.values())
    hyps = ''.join(f' (h{i} : {names[a]} = {names[b]})'
                   for i, (a, b) in enumerate(task.hypotheses))
    a, b = task.target
    return f'theorem ocm_candidate ({binders} : Nat){hyps} : {names[a]} = {names[b]}'


def render(task, proof):
    if not validate_proof(task, proof):
        raise ValueError('INVALID_CANDIDATE')
    names = {v: f'v{i}' for i, v in enumerate(task.variables)}
    def term(p):
        if p[0] == 'hyp': return f'h{p[1]}'
        if p[0] == 'refl': return f'(Eq.refl {names[p[1]]})'
        if p[0] == 'symm': return f'(Eq.symm {term(p[1])})'
        return f'(Eq.trans {term(p[1])} {term(p[2])})'
    return statement(task) + ' :=\n  ' + term(proof) + '\n#print axioms ocm_candidate\n'


def construct(task, budget=64):
    if type(budget) is not int or not 0 <= budget <= 100000:
        raise ValueError('INVALID_BUDGET')
    adjacency = {v: [] for v in task.variables}
    for i, (a, b) in enumerate(task.hypotheses):
        adjacency[a].append((b, ['hyp', i], i))
        adjacency[b].append((a, ['symm', ['hyp', i]], i))
    start, goal = task.target
    proofs = {start: ['refl', start]}
    queue = deque([start])
    events = []
    duplicates = 0
    terminal = 'NO_ROUTE_IN_REGISTERED_FRAGMENT'
    proof = None
    while queue:
        at = queue.popleft()
        if at == goal:
            terminal, proof = 'CANDIDATE_CONSTRUCTED', proofs[at]
            break
        for to, step, dependency in adjacency[at]:
            if len(events) >= budget:
                terminal = 'FAILED_UNDER_BUDGET'
                queue.clear()
                break
            duplicate = to in proofs
            candidate = step if at == start else ['trans', proofs[at], step]
            events.append({'operator': 'Eq.trans' if at != start else step[0],
                           'edge_operator': step[0], 'input_state': [start, at],
                           'goal': list(task.target), 'result_state': [start, to],
                           'candidate_dependency': f'h{dependency}', 'resource_cost': 1,
                           'duplicate': duplicate, 'checker_outcome': 'NOT_CHECKED'})
            if duplicate:
                duplicates += 1
            else:
                proofs[to] = candidate
                if to == goal:
                    terminal, proof = 'CANDIDATE_CONSTRUCTED', candidate
                    queue.clear()
                    break
                queue.append(to)
    return {'terminal': terminal, 'statement_id': task.statement_id, 'proof': proof,
            'events': events, 'metrics': {'edge_examinations': len(events),
            'unique_states': len(proofs), 'duplicate_states_avoided': duplicates,
            'cold_index_input_hypotheses': len(task.hypotheses),
            'cold_index_postings': 2 * len(task.hypotheses),
            'lean_checker_calls': 0, 'LLM_CALLS': 0, 'LLM_TOKENS': 0}}
