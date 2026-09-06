"""Strict, data-only FLT benchmark preparation. Never a theorem truth authority.

The recognized wrapper language is deliberately smaller than Lean. Unsupported
syntax is a CANNOT_CHECK, not a guessed signature. All nodes must pass before a
whole-source coverage receipt can be emitted. Import edges are a syntactic
superset, NOT elaborated proof dependencies. Staging is NOT process sealing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

PINS = {
    'anthropic_repository': 'anthropics/fermats-last-theorem',
    'anthropic_commit': 'aa2d8b34692b16c70f699536de0d8e75b9a3e9ef',
    'lean': '4.33.1',
    'mathlib_tag': 'v4.33.0',
    'mathlib_commit': 'db584cd6d46c92f209a44c0f1c829460d327499d',
}
IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9'.]*\Z")
KEY = re.compile(r"[A-Za-z_0-9']+\Z")


class Refusal(ValueError):
    def __init__(self, terminal: str, detail: str = '') -> None:
        self.terminal = terminal
        super().__init__(terminal + (': ' + detail if detail else ''))


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_json(value: Any) -> str:
    return sha256(encoded(value))


def mask_comments(text: str) -> str:
    """Preserve positions/newlines; recognize nested comments and quoted strings."""
    out = list(text)
    i, nesting, string = 0, 0, False
    while i < len(text):
        if nesting:
            if text.startswith('/-', i):
                out[i:i+2] = '  '; nesting += 1; i += 2
            elif text.startswith('-/', i):
                out[i:i+2] = '  '; nesting -= 1; i += 2
            else:
                if text[i] != '\n': out[i] = ' '
                i += 1
        elif string:
            if text[i] == '\\': i += 2
            elif text[i] == '"': string = False; i += 1
            else: i += 1
        elif text[i] == '"':
            string = True; i += 1
        elif text.startswith('/-', i):
            nesting = 1; out[i:i+2] = '  '; i += 2
        elif text.startswith('--', i):
            end = text.find('\n', i)
            end = len(text) if end < 0 else end
            out[i:end] = ' ' * (end-i); i = end
        else: i += 1
    if nesting or string:
        raise Refusal('CANNOT_CHECK_LEXICAL_LAYOUT', 'unterminated comment/string')
    return ''.join(out)


TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|:=|[A-Za-z_][A-Za-z_0-9\'.]*|\s+|.', re.S)


def tokens(text: str):
    clean = mask_comments(text)
    return clean, [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(clean)
                   if not m.group().isspace()]


def _header(clean, toks):
    imports, i = [], 0
    while i < len(toks) and toks[i][0] == 'import':
        line_end = clean.find('\n', toks[i][2])
        line_end = len(clean) if line_end < 0 else line_end
        i += 1; start = i
        while i < len(toks) and toks[i][1] < line_end:
            value = toks[i][0]
            if not IDENT.fullmatch(value):
                raise Refusal('CANNOT_CHECK_IMPORT_HEADER', value)
            imports.append(value); i += 1
        if i == start: raise Refusal('CANNOT_CHECK_IMPORT_HEADER', 'empty import')
    if not imports: raise Refusal('CANNOT_CHECK_IMPORT_HEADER', 'no recognized imports')
    if any(t[0] == 'import' for t in toks[i:]):
        raise Refusal('CANNOT_CHECK_IMPORT_HEADER', 'non-header import')
    return tuple(imports), i


def import_header(text: str) -> tuple[str, ...]:
    clean, toks = tokens(text)
    result, i = _header(clean, toks)
    if i < len(toks) and toks[i][0] not in {
        'theorem', 'namespace', 'set_option', 'open', 'section', 'variable',
        'def', 'instance', 'attribute', 'universe', 'noncomputable', 'end', '#',
    }:
        raise Refusal('CANNOT_CHECK_IMPORT_HEADER', 'unsupported command after imports')
    return result


def extract_wrapper(text: str, key: str) -> dict[str, Any]:
    if not KEY.fullmatch(key): raise Refusal('CANNOT_CHECK_WRAPPER_LAYOUT', 'module identity')
    clean, toks = tokens(text)
    imports, i = _header(clean, toks)
    expected = 'P2M.Sol.S_' + key
    if imports != ('Mathlib', 'P2M.Util', expected):
        raise Refusal('CANNOT_CHECK_WRAPPER_IMPORTS', key)
    if [t[0] for t in toks[i:i+3]] != ['set_option', 'autoImplicit', 'false']:
        raise Refusal('CANNOT_CHECK_WRAPPER_LAYOUT', 'unsupported preamble')
    i += 3
    if i+2 >= len(toks) or toks[i][0] != 'theorem' or not IDENT.fullmatch(toks[i+1][0]):
        raise Refusal('CANNOT_CHECK_WRAPPER_LAYOUT', 'expected one named theorem')
    name = toks[i+1][0]
    start = toks[i+1][2]
    i += 2; stack = []; colon = False; end = None
    pairs = {')':'(', ']':'[', '}':'{', '⦄':'⦃'}
    while i < len(toks):
        value, pos, _ = toks[i]
        if value == ':=' and not stack:
            end = pos; break
        if value in ('by', 'where', 'axiom', 'sorry', 'native_decide', 'let', 'match',
                     'macro', 'syntax', 'theorem', '#', ':=') or value.startswith('"'):
            raise Refusal('CANNOT_CHECK_SIGNATURE_LANGUAGE', value)
        if value in pairs.values(): stack.append(value)
        elif value in pairs:
            if not stack or stack.pop() != pairs[value]:
                raise Refusal('CANNOT_CHECK_SIGNATURE_LANGUAGE', 'unbalanced binder')
        elif value == ':' and not stack: colon = True
        i += 1
    if end is None or stack or not colon:
        raise Refusal('CANNOT_CHECK_WRAPPER_LAYOUT', 'missing complete signature')
    expected_body = [':=', 'by', 'p2m_exact_reverting', '@', '_root_.P2MW.S_' + key + '.solution']
    if [t[0] for t in toks[i:]] != expected_body:
        raise Refusal('CANNOT_CHECK_WRAPPER_LAYOUT', 'unsupported body/trailing declaration')
    signature = clean[start:end].strip()
    if any(word in signature for word in ('P2M', 'Theorems.', '.solution', 'html/')):
        raise Refusal('SOLUTION_LEAKAGE_DETECTED', 'signature mentions private module')
    return {'name': name, 'signature': signature,
            'signature_sha256': sha256(signature.encode()),
            'wrapper_sha256': sha256(text.encode()),
            'semantic_correspondence': 'CANNOT_CHECK_LEAN_ELABORATION_NOT_RUN'}


def build_graph(files: Mapping[str, str], expected_count: int = 29511) -> dict[str, Any]:
    wrappers, solutions = {}, {}
    for path, text in files.items():
        if path.startswith('Theorems/Thm_') and path.endswith('.lean'):
            key = path[len('Theorems/Thm_'):-5]; wrappers[key] = text
        elif path.startswith('P2M/Sol/S_') and path.endswith('.lean'):
            key = path[len('P2M/Sol/S_'):-5]; solutions[key] = text
    if set(wrappers) != set(solutions) or len(wrappers) != expected_count:
        raise Refusal('CANNOT_CHECK_SOURCE_COVERAGE',
                      f'wrappers={len(wrappers)}, solutions={len(solutions)}, expected={expected_count}')
    nodes, names = {}, set()
    for key in sorted(wrappers):
        row = extract_wrapper(wrappers[key], key)
        if row['name'] in names: raise Refusal('DUPLICATE_THEOREM_NAME', row['name'])
        names.add(row['name'])
        imports = import_header(solutions[key])
        deps = sorted({s[len('Theorems.Thm_'):] for s in imports if s.startswith('Theorems.Thm_')})
        if any(s.startswith(('P2M.Sol.', 'Theorems.')) and not s.startswith('Theorems.Thm_') for s in imports):
            raise Refusal('CANNOT_CHECK_IMPORT_GRAPH', 'unexpected theorem/solution import')
        if any(d not in wrappers for d in deps): raise Refusal('DANGLING_DEPENDENCY', key)
        nodes[key] = {**row, 'dependencies': deps, 'solution_sha256': sha256(solutions[key].encode())}
    # Iterative Kahn traversal avoids recursion limits on long theorem DAGs.
    import heapq
    degree = {k: len(v['dependencies']) for k,v in nodes.items()}
    users = {k: [] for k in nodes}
    for key, row in nodes.items():
        for dep in row['dependencies']: users[dep].append(key)
    ready = [k for k in nodes if not degree[k]]; heapq.heapify(ready)
    order = []
    while ready:
        key = heapq.heappop(ready); order.append(key)
        for nxt in sorted(users[key]):
            degree[nxt] -= 1
            if degree[nxt] == 0: heapq.heappush(ready, nxt)
    if len(order) != len(nodes): raise Refusal('IMPORT_GRAPH_CYCLE')
    return {'schema':'ocm.flt.import-graph.v1', 'environment':dict(PINS),
            'count':len(nodes), 'nodes':nodes, 'topological_order':order,
            'graph_kind':'SYNTACTIC_IMPORT_GRAPH_NOT_PROOF_DEPENDENCY_CERTIFICATE',
            'bytes_examined':sum(len(s.encode()) for s in wrappers.values()) + sum(len(s.encode()) for s in solutions.values()),
            'source_coverage':'ALL_SUPPLIED_PAIRS', 'source_acquisition':'CALLER_MUST_BIND_GIT_OBJECTS'}


def select_holes(graph, size: int, seed: str):
    if type(size) is not int or size < 1 or not seed:
        raise Refusal('INVALID_SELECTION_CONTRACT')
    nodes = graph['nodes']
    rank = lambda key: sha256((seed + '\0' + key).encode())
    root = min(nodes, key=rank)
    holes, queue = [], [root]
    while queue and len(holes) < size:
        key = queue.pop(0)
        if key in holes: continue
        holes.append(key)
        queue.extend(sorted(nodes[key]['dependencies'], key=rank))
    return root, holes  # Fewer than size is reported, never replaced by a favorable root.


def _clean_destination(path: Path) -> Path:
    path = path.absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise Refusal('UNSAFE_PACKAGE_PATH', 'symlink')
    if path.exists(): raise Refusal('IMMUTABLE_DESTINATION_EXISTS', str(path))
    return path


def validate_public(pub: dict[str, Any]) -> None:
    expected = {'schema','environment','regime','target','obligations','boundary',
                'allowed_imports','status','remaining_gates','budget'}
    if type(pub) is not dict or set(pub) != expected: raise Refusal('PUBLIC_SCHEMA_MISMATCH')
    if pub['schema']!='ocm.flt.public-staging.v1': raise Refusal('PUBLIC_SCHEMA_MISMATCH')
    budget=pub['budget']
    if (type(budget) is not dict or set(budget)!={'proof_state_expansions','checker_calls','wall_seconds'}
        or any(type(v) is not int or not 1<=v<=10**6 for v in budget.values())):
        raise Refusal('INVALID_BUDGET')
    if type(pub['obligations']) is not list or type(pub['boundary']) is not list:
        raise Refusal('PUBLIC_SCHEMA_MISMATCH')
    if pub['environment'] != PINS: raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH')
    if pub['regime'] not in ('R2','R3'): raise Refusal('UNREGISTERED_INFORMATION_REGIME')
    if pub['status'] != 'STAGED_NOT_EXECUTABLE' or pub['allowed_imports'] != ['Mathlib']:
        raise Refusal('UNQUALIFIED_PACKAGE_PROMOTION')
    if pub['remaining_gates'] != ['LEAN_STATEMENT_ELABORATION','BOUNDARY_CERTIFICATES','OS_PROCESS_ISOLATION']:
        raise Refusal('UNQUALIFIED_PACKAGE_PROMOTION')
    rows = pub['obligations'] + pub['boundary']
    for row in rows:
        if type(row) is not dict or set(row) != {'id','name','signature','signature_sha256','status'} or any(type(v) is not str for v in row.values()):
            raise Refusal('PUBLIC_SCHEMA_MISMATCH', 'statement row')
        if row['status'] != 'OPEN' or row['signature_sha256'] != sha256(row['signature'].encode()):
            raise Refusal('UNQUALIFIED_STATEMENT_PROMOTION')
    text = json.dumps(pub, ensure_ascii=False)
    if any(s in text for s in ('P2M.', 'Theorems.', '.solution', 'html/', 'solution_sha256')):
        raise Refusal('SOLUTION_LEAKAGE_DETECTED')
    ids = [r['id'] for r in rows]
    if len(set(ids)) != len(ids) or pub['target'] not in {r['id'] for r in pub['obligations']}:
        raise Refusal('PUBLIC_IDENTITY_MISMATCH')


def stage_challenge(graph, holes, target, regime, public_dir: Path, private_dir: Path):
    if regime not in ('R2','R3'): raise Refusal('UNREGISTERED_INFORMATION_REGIME')
    if not holes or len(set(holes)) != len(holes) or target not in holes:
        raise Refusal('INVALID_HOLES')
    if any(k not in graph['nodes'] for k in holes): raise Refusal('UNKNOWN_HOLE')
    public_dir, private_dir = _clean_destination(public_dir), _clean_destination(private_dir)
    if public_dir == private_dir or public_dir in private_dir.parents or private_dir in public_dir.parents:
        raise Refusal('PRIVATE_PUBLIC_PATH_OVERLAP')
    boundary = sorted({d for k in holes for d in graph['nodes'][k]['dependencies']} - set(holes))
    # Boundary rows are unresolved certificate requirements, NEVER emitted as Lean axioms.
    def public_row(key):
        row=graph['nodes'][key]
        return {'id':key, 'name':row['name'], 'signature':row['signature'],
                'signature_sha256':row['signature_sha256'], 'status':'OPEN'}
    pub = {'schema':'ocm.flt.public-staging.v1','environment':dict(PINS), 'regime':regime,
           'target':target, 'obligations':[public_row(k) for k in sorted(holes)],
           'boundary':[public_row(k) for k in boundary], 'allowed_imports':['Mathlib'],
           'status':'STAGED_NOT_EXECUTABLE',
           'remaining_gates':['LEAN_STATEMENT_ELABORATION','BOUNDARY_CERTIFICATES','OS_PROCESS_ISOLATION'],
           'budget':{'proof_state_expansions':256,'checker_calls':16,'wall_seconds':60}}
    validate_public(pub)
    private = {'schema':'ocm.flt.private-evaluator.v1','environment':dict(PINS),
               'graph_sha256':digest_json(graph), 'public_sha256':digest_json(pub),
               'nodes':{k:graph['nodes'][k] for k in sorted(set(holes)|set(boundary))},
               'target':target,'holes':sorted(holes), 'regime':regime}
    for path, value, name, mode in ((private_dir,private,'PRIVATE.json',0o700),(public_dir,pub,'PUBLIC.json',0o755)):
        path.mkdir(mode=mode)
        with (path/name).open('xb') as out: out.write(encoded(value))
    return pub, private
