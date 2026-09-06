"""One exact exposed task and sealed primitive specialization; no native calls."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from sexpdata import Symbol as S
from clia_grammar import forms, dump, validate
from clia_tasks import load_task, signatures
import generation_clia as G

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT/'results/stitch-primitive-rewrite-20260906/raw/normalized-induction/capture-v1'
ADAPTER = PRIOR/'calls/adapter-return.json'
ADAPTER_SHA = 'a82caf571767fc87113aa51455e1708b59ad120749e8eaf676184a64fee0a887'
SEAL_SHA = '275012f6e1429c08bd481631ff821f20dff8e3ee02393294241cbf2f8181e5e8'
TASK_ID = 'public_absdiff2_v1'
ROUTES = ('C', 'E0', 'B')
CHECKS = ('C-spec', 'E0-spec', 'B-expansion', 'B-spec')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_library():
    if sha(ADAPTER) != ADAPTER_SHA or sha(PRIOR/'seal.json') != SEAL_SHA:
        raise ValueError('sealed library binding drift')
    seal = json.loads((PRIOR/'seal.json').read_text())
    if seal['calls/adapter-return.json'] != {'bytes': ADAPTER.stat().st_size, 'sha256': ADAPTER_SHA}:
        raise ValueError('predecessor member binding drift')
    saved = json.loads(ADAPTER.read_text())
    expected = {'fn_0': {'name': 'fn_0', 'body': '(not (>= #0 1))', 'sorts': ['Int'], 'result': 'Bool'}}
    if saved['status'] != 'PROPOSED_ABSTRACTIONS' or saved['library'] != expected:
        raise ValueError('exact acquired library required')
    library = G.admit_macros([{'name':'fn_0', 'body':saved['library']['fn_0']['body'], 'arity':1}])
    if json.loads(json.dumps({k:asdict(v) for k,v in library.items()})) != expected:
        raise ValueError('typed acquired library binding mismatch')
    return library


def requests():
    task, library = load_task(TASK_ID), load_library()
    return {'C': task['original_sygus'], 'E0': G.request(task, {}), 'B': G.request(task, library)}


def helper_definition(library):
    macro = library['fn_0']
    body = G.substitute(G.one(macro.body), {'#0': S('h0')})
    return [S('define-fun'), S('fn_0'), [[S('h0'), S('Int')]], S('Bool'), body]


def _expand_with_lets(node, library, depth=0, used=None, count=None):
    count = [0] if count is None else count
    count[0] += 1
    if depth > 160 or count[0] > 20000:
        raise ValueError('expansion exceeds operational bound')
    if not isinstance(node, list):
        return node
    if node and node[0] == S('let'):
        if len(node) != 3 or not isinstance(node[1], list):
            raise ValueError('invalid let structure')
        bindings = []
        for entry in node[1]:
            if not isinstance(entry, list) or len(entry) != 2 or not isinstance(entry[0], S):
                raise ValueError('invalid let binding')
            if str(entry[0]) in library:
                raise ValueError('let cannot shadow acquired global helper')
            bindings.append([entry[0], _expand_with_lets(entry[1],library,depth+1,used,count)])
        return [node[0], bindings, _expand_with_lets(node[2],library,depth+1,used,count)]
    rebuilt = [_expand_with_lets(x, library, depth+1, used, count) for x in node]
    if rebuilt and isinstance(rebuilt[0], S) and str(rebuilt[0]) == 'fn_0':
        return G.expand(rebuilt, library, used)
    return rebuilt


def prepare_return(candidate, route):
    """Inspect returned absdiff2 only; an offered helper/GEN production is not use.

    Current unchanged worker exposes no :gterm derivation. Unsupported tags refuse;
    no annotation option is added. Let dependencies are validated before unletting.
    """
    if route not in ROUTES:
        raise ValueError('unknown route')
    task, library = load_task(TASK_ID), load_library()
    sigs = signatures(task)
    nodes = forms(candidate)
    if len(nodes) == 1 and isinstance(nodes[0], list) and nodes[0] and isinstance(nodes[0][0], list):
        nodes = nodes[0]
    if route != 'B':
        definition = validate(candidate, sigs)[0]
        return {'expanded_candidate':dump(definition), 'observed_calls':[], 'equivalence_smt2':None}
    helper = helper_definition(library)
    definitions = []
    helper_seen = False
    for node in nodes:
        if isinstance(node, list) and len(node) == 5 and node[:2] == helper[:2]:
            if helper_seen or node != helper:
                raise ValueError('returned helper declaration differs from acquired definition')
            helper_seen = True
        else:
            definitions.append(node)
    if len(definitions) != 1 or not isinstance(definitions[0], list) or len(definitions[0]) != 5:
        raise ValueError('one returned target definition required')
    original = definitions[0]
    full = [*original[:4], _expand_with_lets(original[4], library)]
    validate(dump(full), sigs)  # Includes unused lets; no validation bypass.
    used = []
    body = G.unlet(original[4])
    expanded = [*original[:4], _expand_with_lets(body, library, used=used)]
    validate(dump(expanded), sigs)
    left = [S('define-fun'), S('left'), original[2], original[3], body]
    right = [S('define-fun'), S('right'), expanded[2], expanded[3], expanded[4]]
    smt = '\n'.join(dump(x) for x in (helper, left, right))
    smt += '\n(declare-const x Int)\n(declare-const y Int)\n'
    smt += '(assert (not (= (left x y) (right x y))))\n'
    return {'expanded_candidate':dump(expanded), 'observed_calls':used,
            'equivalence_smt2':smt, 'library_sha256':ADAPTER_SHA,
            'use_scope':'Syntactic returned-body dependency only; no causal search or runtime-benefit claim.'}
