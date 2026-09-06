"""Offline evaluator inventory. Lexical signatures are NOT elaborated types.

Never pass wrappers, prefixes or solution imports to the solver. Unsupported
syntax is an explicit refusal, not a guessed signature or dropped dependency.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from native import identity


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int


def tokens(text):
    result = []
    i = 0
    while i < len(text):
        if text[i].isspace(): i += 1; continue
        if text.startswith('--', i):
            end = text.find('\n', i); i = len(text) if end < 0 else end + 1; continue
        if text.startswith('/-', i):
            depth = 1; i += 2
            while i < len(text) and depth:
                if text.startswith('/-', i): depth += 1; i += 2
                elif text.startswith('-/', i): depth -= 1; i += 2
                else: i += 1
            if depth: raise ValueError('UNTERMINATED_COMMENT')
            continue
        start = i
        if text[i] in ('"', '«'):
            closer = '"' if text[i] == '"' else '»'
            i += 1
            while i < len(text) and text[i] != closer:
                if closer == '"' and text[i] == '\\': i += 1
                i += 1
            if i >= len(text): raise ValueError('UNTERMINATED_QUOTE')
            i += 1
        elif text.startswith(':=', i): i += 2
        elif text[i].isalpha() or text[i] == '_':
            i += 1
            while i < len(text) and (text[i].isalnum() or text[i] in "_'."): i += 1
        else: i += 1
        result.append(Token(text[start:i], start, i))
    return result


def imports(text):
    ts = tokens(text)
    found = []
    for i, token in enumerate(ts):
        if token.text != 'import': continue
        # The corpus contract supports ordinary header import commands only.
        line_start = text.rfind('\n', 0, token.start) + 1
        preceding = [t for t in ts[:i] if t.start >= line_start]
        if preceding: raise ValueError('UNSUPPORTED_IMPORT_MODIFIER_OR_POSITION')
        j = i + 1
        while j < len(ts) and '\n' not in text[token.end:ts[j].start]:
            name = ts[j].text
            if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_\']*(?:\.[A-Za-z_][A-Za-z0-9_\']*)*', name) is None:
                raise ValueError('UNSUPPORTED_IMPORT_SYNTAX')
            found.append(name); j += 1
        if j == i + 1: raise ValueError('EMPTY_IMPORT')
    return tuple(found)


def signature(text):
    ts = tokens(text)
    candidates = [i for i, t in enumerate(ts) if t.text in ('theorem', 'lemma')]
    if len(candidates) != 1: raise ValueError('CANNOT_CHECK_DECLARATION_COUNT')
    i = candidates[0]
    if i + 1 >= len(ts): raise ValueError('CANNOT_CHECK_DECLARATION_NAME')
    name = ts[i + 1].text
    stack = []
    close = {')': '(', ']': '[', '}': '{', '⦄': '⦃'}
    for token in ts[i + 2:]:
        t = token.text
        if t in ('(', '[', '{', '⦃'): stack.append(t)
        elif t in close:
            if not stack or stack.pop() != close[t]: raise ValueError('UNBALANCED_SIGNATURE')
        elif not stack and t in ('let', 'where', 'match', 'by'):
            raise ValueError('CANNOT_CHECK_COMPLEX_SIGNATURE_SYNTAX')
        elif not stack and t == ':=':
            exact = text[ts[i].start:token.start].rstrip()
            return {'name': name, 'signature': exact, 'signature_sha256': hashlib.sha256(exact.encode()).hexdigest(),
                    'prefix_sha256': hashlib.sha256(text[:ts[i].start].encode()).hexdigest(),
                    'context_status': 'CANNOT_CHECK_ELABORATED_TYPE_AND_DEFINITION_CLOSURE'}
    raise ValueError('CANNOT_CHECK_SIGNATURE_DELIMITER')


def read_regular(path):
    if path.is_symlink() or not path.is_file(): raise ValueError('NON_REGULAR_SOURCE')
    return path.read_text(encoding='utf-8')


def inventory(root: Path, expected_count=29511):
    root = root.resolve()
    for name in ('Theorems', 'P2M', 'P2M/Sol'):
        if (root / name).is_symlink(): raise ValueError('SYMLINK_SOURCE_TREE')
    wrappers = {p.stem[4:]: p for p in (root / 'Theorems').glob('Thm_*.lean')}
    solutions = {p.stem[2:]: p for p in (root / 'P2M/Sol').glob('S_*.lean')}
    if set(wrappers) != set(solutions) or len(wrappers) != expected_count:
        raise ValueError('CANNOT_CHECK_CORPUS_COVERAGE')
    nodes = {}; errors = {}
    bytes_read = 0
    for key in sorted(wrappers):
        try:
            wrapper, proof = read_regular(wrappers[key]), read_regular(solutions[key])
            bytes_read += len(wrapper.encode()) + len(proof.encode())
            wi, si = imports(wrapper), imports(proof)
            if f'P2M.Sol.S_{key}' not in wi: raise ValueError('WRAPPER_SOLUTION_MISMATCH')
            if any(x.startswith('P2M.Sol.') for x in si): raise ValueError('DIRECT_SOLUTION_DEPENDENCY')
            deps = [x[len('Theorems.Thm_'):] for x in si if x.startswith('Theorems.Thm_')]
            if not set(deps) <= wrappers.keys(): raise ValueError('UNRESOLVED_DEPENDENCY')
            try: sig = signature(wrapper)
            except ValueError as exc: sig = {'context_status': str(exc)}
            nodes[key] = {'solution_sha256': hashlib.sha256(proof.encode()).hexdigest(),
                          'wrapper_sha256': hashlib.sha256(wrapper.encode()).hexdigest(),
                          'dependencies': sorted(set(deps)), 'signature': sig}
        except ValueError as exc:
            errors[key] = str(exc)
    indegree = {k: len(v['dependencies']) for k, v in nodes.items()}
    children = {k: [] for k in nodes}
    for k, row in nodes.items():
        for d in row['dependencies']:
            if d in children: children[d].append(k)
    queue = deque(k for k in nodes if not indegree[k]); visited = 0
    while queue:
        visited += 1
        for k in children[queue.popleft()]:
            indegree[k] -= 1
            if not indegree[k]: queue.append(k)
    complete = not errors and visited == expected_count
    return {'schema': 'ocm.flt.private.inventory.v1',
            'terminal': 'SOURCE_DAG_INVENTORIED' if complete else 'CANNOT_CHECK_GRAPH_COVERAGE',
            'wrapper_count': len(wrappers), 'solution_count': len(solutions),
            'nodes': nodes, 'errors': errors, 'acyclic_nodes_visited': visited,
            'source_bytes_read': bytes_read, 'global_scan': True,
            'public_export_terminal': 'CANNOT_CHECK_ELABORATED_TYPE_AND_DEFINITION_CLOSURE',
            'graph_identity': identity(nodes)}
