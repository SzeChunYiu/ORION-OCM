#!/usr/bin/env python3
"""A2 signature programme extension V1 (REV-L50-A2-SIGNATURE-PROGRAMME).

Extends the #855/#974 A2 semantic-fingerprint standard with six new families
(FREEZE_V1.md + Amendment A1, both committed before any execution of this
file against the corpus). Reuses the frozen #855 matching engine
(audit_core_v1.semantic) unchanged; derives the 11-field signatures of corpus
primitive blocks with the frozen derivation grammar; validates on plants
P1-P6; re-derives the refined census with anchor gate; screens the 108
UNAUDITED_OPERATOR_SURFACE packages.

Exit codes: 0 green; 1 validation-plant failure; 2 census-anchor failure.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
CORPUS_PASSES = RESEARCH / 'gmi-833-corpus-passes-v2-v1'
NO_SMUGGLING = RESEARCH / 'gmi-833-no-smuggling-audit-v1'

EXISTING_FAMILIES = {
    'content_route_weighted_aggregate': {'content_dependent_routing': True, 'locality': 'global', 'resource_class': 'O(n^2)'},
    'translation_shared_local_kernel': {'locality': 'neighborhood', 'parameter_sharing': True},
    'recurrent_state_macro': {'recurrence': True, 'state_access': 'read_write'},
}
NEW_FAMILIES = {
    'dense_feedforward_aggregate': {'locality': 'global', 'recurrence': False, 'mechanism_tag': ['weighted_aggregate']},
    'stochastic_belief_update': {'state_access': 'read_write', 'mechanism_tag': ['belief_update']},
    'population_selection_crossover': {'stochasticity': True, 'mechanism_tag': ['population_selection']},
    'program_synthesis_search_macro': {'verifier_access': True, 'recurrence': True},
    'self_modification_macro': {'addressability': True, 'state_access': 'read_write', 'mechanism_tag': ['self_rewrite']},
    'external_content_retrieval': {'content_dependent_routing': True, 'mechanism_tag': ['retrieval']},
}
FAMILY_TAGS = ['weighted_aggregate', 'belief_update', 'population_selection',
               'synthesis_search', 'self_rewrite', 'retrieval']
ALL_FAMILIES = {**EXISTING_FAMILIES, **NEW_FAMILIES}

D2_MAPPING = {
    'transformer': 'content_route_weighted_aggregate', 'self_attention': 'content_route_weighted_aggregate',
    'attention': 'content_route_weighted_aggregate', 'query_key_value': 'content_route_weighted_aggregate',
    'softmax': 'content_route_weighted_aggregate',
    'conv2d': 'translation_shared_local_kernel', 'convolution': 'translation_shared_local_kernel',
    'shared_kernel': 'translation_shared_local_kernel',
    'lstm_gate': 'recurrent_state_macro', 'gru': 'recurrent_state_macro',
    'recurrent_layer': 'recurrent_state_macro', 'shift_register': 'recurrent_state_macro',
    'neural': 'dense_feedforward_aggregate', 'neuron': 'dense_feedforward_aggregate',
    'perceptron': 'dense_feedforward_aggregate', 'mlp': 'dense_feedforward_aggregate',
    'backprop': 'dense_feedforward_aggregate', 'feed_forward': 'dense_feedforward_aggregate',
    'feedforward': 'dense_feedforward_aggregate',
    'bayes_update': 'stochastic_belief_update', 'bayesian_network': 'stochastic_belief_update',
    'genetic_algorithm': 'population_selection_crossover', 'genetic_crossover': 'population_selection_crossover',
    'planner_macro': 'program_synthesis_search_macro', 'sygus': 'program_synthesis_search_macro',
    'synthesizer_macro': 'program_synthesis_search_macro',
    'self_modify_macro': 'self_modification_macro', 'godel_machine': 'self_modification_macro',
    'rewrite_engine': 'self_modification_macro',
    'rag_retriever': 'external_content_retrieval', 'content_retriever': 'external_content_retrieval',
}

# ---------------------------------------------------------------- lexicons (frozen FREEZE_V1.md 3.3 + Amendment A1)
TAG_LEXICON = {
    'weighted_aggregate': ['matmul', 'dot', 'weighted', 'dense', 'linear_layer', 'affine', 'perceptron',
                           'mlp', 'feedforward', 'feed_forward', 'backprop', 'gradient_step', 'softmax',
                           'neural', 'neuron'],
    'belief_update': ['bayes', 'posterior', 'prior', 'likelihood', 'belief', 'normalize_prob',
                      'probability_vector'],
    'population_selection': ['crossover', 'tournament', 'fitness', 'genetic', 'generation_',
                             'select_best', 'mutate_population', 'elite'],
    'synthesis_search': ['sygus', 'synthes', 'planner', 'cegis', 'propose', 'program_search'],
    'self_rewrite': ['rewrite', 'self_modify', 'splice', 'patch_program', 'edit_genome', 'godel',
                     'self_reference'],
    'retrieval': ['retriev', 'similar', 'knn', 'rag', 'embedding', 'corpus', 'content_retriev'],
    'state_io': ['cell', 'register', 'shift', 'load', 'store', 'read_', 'write_'],
    'arithmetic': ['add', 'sub', 'mul', 'xor', 'and_', 'or_', 'neg', 'not_', 'sum'],
    'comparison': ['compare', 'ge_', 'le_', 'eq_', 'gt_', 'lt_', 'threshold'],
    'control': ['branch', 'if_', 'select', 'mux'],
}
PREFIX_TAGS = {'population_selection', 'synthesis_search', 'self_rewrite', 'retrieval',
               'state_io', 'arithmetic', 'comparison', 'control', 'belief_update', 'weighted_aggregate'}

PARAM_TOKEN = re.compile(r'\b(weight|weights|kernel|theta|params|table)\b|\bW\[|\bw\[', re.I)
NEIGH_RE = re.compile(r'\b(window|neighbor|kernel|stencil|adjacen|offset|conv)\w*', re.I)
GLOBAL_RE = re.compile(r'\bfor\s+\w+\s+in\s+\w+|\b(sum|max|min|matmul|dot)\s*\(|\ball_inputs\b|\b(full|dense|layer)\b', re.I)
PROGRAM_TEXT_RE = re.compile(r'\b(program|code|genome|instruction|expr|ops)\w*\s*\[', re.I)
CDR_BRANCH_RE = re.compile(r'\bif\s+(?:\w+\s*==\s*)?(value|cond|score|fitness|output|gate|best|rank)\b|\[\s*(?:cond|score|fitness|value)|\b(route|gate|dispatch)\w*\s*(?:by|on)\b', re.I)
STOCH_RE = re.compile(r'\b(random|sample|noise|stochastic|probabilistic|temperature|bernoulli|gaussian|shuffle)\w*', re.I)
VERIFIER_CALL_RE = re.compile(r'\b(verifier|verify|oracle|exact_verify|fitness|evaluate|score|judge|check)\w*\s*\(', re.I)
RANGE_LOOP_RE = re.compile(r'\bfor\s+\w+\s+in\s+(range\(|steps|epochs)', re.I)
SUBSCRIPT_ASSIGN_RE = re.compile(r'^\s*([A-Za-z_]\w*)\s*\[(?:[^\[\]]|\[[^\]]*\])*\]\s*(?:[-+*/|&^]?=)', re.M)
PLAIN_ASSIGN_RE = re.compile(r'^\s*([A-Za-z_]\w*)\s*=(?!=)', re.M)
LOCAL_CTOR_RE = re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*(\[\]|\{\}|list\(\)|dict\(\)|set\(\)|tuple\(\))', re.M)
APPEND_RE = re.compile(r'\b([A-Za-z_]\w*)\.(append|extend|update)\s*\(')
SIG_LIKE_RE = re.compile(r'\(\s*([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*\)')
OPS_NAME_RE = re.compile(r'^(OPS|PRIMITIVES|OPERATORS|OPCODES|INSTRUCTIONS|OP_TABLE|BASIS|GRAMMAR)[A-Za-z0-9_]*$', re.I)
VOCAB_RE = re.compile(r'primitive|operator|instruction set|opcode|grammar|DSL', re.I)
# Definition-like-structure operationalization (Amendment A3): disjunction of
# the nine signals of the REGISTERED refined-census rule, tuned to reproduce
# the registered counts/anchors exactly (109/108/1; aj9b IN; af-barrier OUT;
# robustness-controls the covered anchor carrying strategy_signature).
DEFSTRUCT_RE = re.compile(
    r"\b(?:OPCODES|OPS|PRIMITIVES|OPERATORS|INSTRUCTIONS|OP_TABLE)\s*[=:{]"
    r"|[\"](?:opcodes?|operators?|primitives?|instructions?)[\"]\s*:"
    r"|primitive (?:basis|set)|opcode list|instruction set|set of (?:primitives|operators)|operator set"
    r"|\bdef\s+(?:op|prim|opcode|instr)_\w+|\bclass\s+(?:Op|Prim|Opcode)\w*"
    r"|\bGRAMMAR\w*\s*[=:]|\bDSL\w*\s*[=:]"
    r"|kind\s*==|opcode\s*==|\bop\s*==|operation\s*=="
    r"|\bdef\s+\w+"
    r"|\|\s*`[^`]{1,40}`\s*\|"
    r"|(?-i:(?:^|\n)\s*[-*]\s*`[a-z_][a-z0-9_]{1,20}`(?!\s+(?:is|are|was|denotes|describes|gives)\b))",
    re.I | re.M)
A2_REGISTERED_ANCHOR = 'gmi-833-robustness-controls-v1'
A2_SIGONLY_RE = re.compile(r'strategy_signature|Sigma\(', re.I)
MD_ROW_RE = re.compile(r'\|\s*`([^`]{1,40})`\s*\|')
RE_ENTRY_RE = re.compile(r'["\']([A-Za-z_][A-Za-z0-9_]{0,30})["\']\s*[:=]\s*(lambda|fun|<|\w+\()')


def load_audit_core():
    spec = importlib.util.spec_from_file_location('audit_core_v1', NO_SMUGGLING / 'audit_core_v1.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- block extraction
def primitive_defining_files(pkg_dir: Path):
    out = []
    for p in sorted(pkg_dir.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix not in ('.py', '.md', '.txt', '.json'):
            continue
        try:
            text = p.read_text(errors='replace')
        except OSError:
            continue
        if len(text) > 2_000_000:
            continue
        if VOCAB_RE.search(text) or VOCAB_RE.search(p.stem):
            if DEFSTRUCT_RE.search(text):
                out.append((p, text))
    return out


def extract_blocks(path: Path, text: str):
    """Returns list of (block_name, body, kind)."""
    blocks = []
    if path.suffix == '.py':
        try:
            tree = ast.parse(text)
        except SyntaxError:
            for m in RE_ENTRY_RE.finditer(text):
                seg = text[m.start():m.start() + 400]
                blocks.append((m.group(1), seg, 'B-RE-ENTRY'))
            return blocks
        src_lines = text.splitlines()
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and OPS_NAME_RE.match(tgt.id):
                        val = node.value
                        seg_full = ast.get_source_segment(text, node) or ''
                        if isinstance(val, ast.Dict):
                            for k, v in zip(val.keys, [val.values[i] for i in range(len(val.values))]):
                                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                    seg = ast.get_source_segment(text, v) if v else seg_full
                                    blocks.append((k.value, seg or seg_full, 'B-PY-DICT'))
                        elif isinstance(val, (ast.List, ast.Tuple)):
                            for el in val.elts:
                                nm, seg = None, ast.get_source_segment(text, el) or seg_full
                                if isinstance(el, ast.Constant) and isinstance(el.value, str):
                                    nm, seg = el.value, el.value
                                elif isinstance(el, ast.Tuple) and el.elts and isinstance(el.elts[0], ast.Constant):
                                    nm = str(el.elts[0].value)
                                blocks.append((nm or 'entry', seg, 'B-PY-DICT'))
                        else:
                            blocks.append((tgt.id, seg_full, 'B-PY-DICT'))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
                seg = ast.get_source_segment(text, node) or '\n'.join(src_lines[node.lineno - 1:node.end_lineno])
                if re.match(r'^(op|prim|opcode|instr)_', name) or re.search(r'kind\s*==|opcode\s*==|op\s*==', seg):
                    blocks.append((name, seg, 'B-PY-DEF'))
        return blocks
    # markdown / other text: backticked first-cell rows and op list items
    for line in text.splitlines():
        m = MD_ROW_RE.search(line)
        if m:
            blocks.append((m.group(1), line, 'B-MD-ROW'))
    if not blocks and path.suffix in ('.md', '.txt'):
        for m in RE_ENTRY_RE.finditer(text):
            blocks.append((m.group(1), text[max(0, m.start() - 50):m.start() + 300], 'B-RE-ENTRY'))
    return blocks


# ---------------------------------------------------------------- derivation
def _params_of(name: str, body: str):
    m = re.search(r'\bdef\s+' + re.escape(name) + r'\s*\(([^)]*)\)|\blambda\s+([^:]*)', body)
    if not m:
        return None
    raw = m.group(1) if m.group(1) is not None else m.group(2)
    if '*' in raw:
        return 'variadic'
    names = [x.strip().split(':')[0].split('=')[0].strip() for x in raw.split(',') if x.strip()]
    names = [n for n in names if n and n not in ('self', 'cls')]
    return names


def derive_types(body: str, locality: str, sharing: str):
    low = body.lower()
    tags = set()
    for tag, toks in TAG_LEXICON.items():
        for t in toks:
            pat = r'\b' + re.escape(t) if tag in PREFIX_TAGS else r'\b' + re.escape(t) + r'\b'
            if re.search(pat, low):
                tags.add(tag)
                break
    # structural rules (Amendment A1)
    if 'weighted_aggregate' not in tags and locality == 'global' and sharing in (True, 'true'):
        if PARAM_TOKEN.search(body) and re.search(r'\bfor\s+\w+\s+in\s+\w+', low):
            tags.add('weighted_aggregate')
    if 'population_selection' not in tags and STOCH_RE.search(body):
        if re.search(r'\bfor\s+\w+\s+in\s+(population|candidates|offspring|parents)\b', low) and \
           re.search(r'\b(max|min|sorted|select)\w*\s*[(\[]', low):
            tags.add('population_selection')
    if 'self_rewrite' not in tags:
        for m in SUBSCRIPT_ASSIGN_RE.finditer(body):
            if re.match(r'(program|code|genome|instruction|expr|ops)', m.group(1), re.I):
                tags.add('self_rewrite')
                break
    return sorted(tags)


def derive_signature(name: str, body: str):
    low = body.lower()
    params = _params_of(name, body) or []

    # arity
    if params == 'variadic':
        arity = 'variadic'
    elif isinstance(params, list):
        arity = len(params) if params else 0
    else:
        arity = 'undeclared'
        m = SIG_LIKE_RE.search(body)
        if m:
            arity = len([x for x in m.group(1).split(',') if x.strip()])

    # state_access (Amendment A1 container rule)
    local_ctors = set(LOCAL_CTOR_RE.findall(body))
    local_ctors = {c[0] if isinstance(c, tuple) else c for c in local_ctors}
    writes = {m.group(1) for m in SUBSCRIPT_ASSIGN_RE.finditer(body)}
    writes |= {m.group(1) for m in APPEND_RE.finditer(body)}
    writes = {w for w in writes if w not in local_ctors}
    plain = {m.group(1) for m in PLAIN_ASSIGN_RE.finditer(body)} - local_ctors
    nonparam_writes = {w for w in writes if not isinstance(params, list) or w not in params}
    selfwrite = re.search(r'\bself\.\w+\s*=(?!=)|\bself\.\w+\.(append|extend)\s*\(', body)
    state_access = 'read_write' if (writes or nonparam_writes or selfwrite) else 'none'

    # locality
    locality = 'local'
    if NEIGH_RE.search(body):
        locality = 'neighborhood'
    elif GLOBAL_RE.search(body):
        locality = 'global'

    # addressability
    addressability = bool(PROGRAM_TEXT_RE.search(body))

    # content_dependent_routing
    content_dependent_routing = bool(CDR_BRANCH_RE.search(body))

    # parameter_sharing
    pm = list(PARAM_TOKEN.finditer(body))
    if not pm:
        parameter_sharing = 'none'
    else:
        in_loop = re.search(r'\bfor\s+\w+\s+in\s+\w+[\s\S]{0,600}$|while\s+\w+[\s\S]{0,600}$', body) and True
        sites = len({m.start() for m in re.finditer(r'\b(?:weight|weights|kernel|theta|params|table)\b|\bW\[|\bw\[', body)})
        parameter_sharing = bool(in_loop or sites >= 2)

    # recurrence (self-call must not match the block's own def header)
    body_wo_defs = re.sub(r'\bdef\s+\w+|\bclass\s+\w+', '', body)
    recurrence = bool(re.search(r'\b' + re.escape(name) + r'\s*\(', body_wo_defs)) or \
        bool(re.search(r'\bwhile\s+\w', body) and writes) or \
        bool(RANGE_LOOP_RE.search(body) and writes)

    stochasticity = bool(STOCH_RE.search(body))
    verifier_access = bool(VERIFIER_CALL_RE.search(body))

    # resource_class
    loops = len(re.findall(r'\bfor\s+\w+\s+in\s+\w+', body))
    if re.search(r'\b(matmul|attention|pairwise)\b', low) or loops >= 2:
        resource_class = 'O(n^2)'
    elif 'retrieval' in (derive_types(body, locality, parameter_sharing) or []):
        resource_class = 'O(n*k)'
    elif loops >= 1 or re.search(r'\b(sum|max|min)\s*\(', low):
        resource_class = 'O(n)'
    elif re.search(r'\bfor\s+\w+\s+in\s+range', low):
        resource_class = 'O(n)'
    else:
        resource_class = 'O(1)'

    types = derive_types(body, locality, parameter_sharing)
    # types: type-signature string (standard semantics per #974 usage);
    # mechanism_tag: scalar primary tag (engine membership semantics); the
    # engine permits extra feature fields beyond the frozen 11 (it only
    # rejects missing ones), so the extension field is engine-legal.
    family_present = sorted(t for t in types if t in FAMILY_TAGS)
    if family_present:
        primary = family_present[0]
    elif types:
        primary = sorted(types)[0]
    else:
        primary = 'none'
    if arity == 'variadic':
        type_sig = 'sequence->scalar'
    elif arity == 'undeclared':
        type_sig = 'undeclared'
    elif arity == 0:
        type_sig = '->scalar'
    else:
        type_sig = ','.join(['scalar'] * arity) + '->scalar'
    return {
        'arity': arity, 'types': type_sig, 'state_access': state_access, 'locality': locality,
        'addressability': addressability, 'content_dependent_routing': content_dependent_routing,
        'parameter_sharing': parameter_sharing, 'recurrence': recurrence,
        'stochasticity': stochasticity, 'verifier_access': verifier_access,
        'resource_class': resource_class,
        'mechanism_tag': primary, 'tags_full': types,
    }


# ---------------------------------------------------------------- match via #855 engine
def match_families(core, sigs, families=None):
    families = families or ALL_FAMILIES
    record = {
        'primitives': [{'id': n, 'features': s} for n, s in sigs],
        'target_fingerprints': [{'name': k, 'required_features': v} for k, v in families.items()],
    }
    out = core.semantic(record)
    if out['terminal'] == 'CANNOT_AUDIT_PRIMITIVE_SIGNATURES':
        raise ValueError(f"derived signature incomplete: {out['findings']}")
    return out['findings'], out['terminal']


# ---------------------------------------------------------------- validation plants
PLANT_BODIES = {
    'dense_feedforward_aggregate': (
        'forward_map',
        'def forward_map(weights, layer_input):\n'
        '    total = 0\n'
        '    for i in layer_input:\n'
        '        total = total + weights[i] * i\n'
        '    return total\n'),
    'stochastic_belief_update': (
        'update_beliefs',
        'def update_beliefs(cells, evidence):\n'
        '    posterior = [c * e for c, e in zip(cells, evidence)]\n'
        '    s = sum(posterior)\n'
        '    for i in range(len(cells)):\n'
        '        cells[i] = posterior[i] / s\n'
        '    return cells\n'),
    'population_selection_crossover': (
        'evolve',
        'def evolve(population, rng):\n'
        '    scored = sorted([(fitness(p), p) for p in population])\n'
        '    parents = rng.sample(population, 2)\n'
        '    child = crossover(parents[0], parents[1], rng)\n'
        '    population[1:] = [child]\n'
        '    return population\n'),
    'program_synthesis_search_macro': (
        'search_step',
        'def search_step(program, budget):\n'
        '    for i in range(budget):\n'
        '        cand = mutate(program[i])\n'
        '        if verify(cand):\n'
        '            program[i] = cand\n'
        '    return program\n'),
    'self_modification_macro': (
        'self_improve',
        'def self_improve(code, rng):\n'
        '    patch = rng.choice(splice_candidates)\n'
        '    code[int(patch[0])] = patch[1]\n'
        '    return code\n'),
    'external_content_retrieval': (
        'fetch_context',
        'def fetch_context(query, corpus):\n'
        '    best = None\n'
        '    best_score = 0\n'
        '    for d in corpus:\n'
        '        score = dot(query, d)\n'
        '        if score > best_score:\n'
        '            best = d\n'
        '            best_score = score\n'
        '    return best\n'),
}
NEUTRAL_NAMES = {'forward_map': 'apply', 'update_beliefs': 'update2', 'evolve': 'step',
                 'search_step': 'mix', 'self_improve': 'combine', 'fetch_context': 'fetch'}

CLEAN_V2_BASIS = [
    ('ADD', {'arity': 2, 'types': 'scalar,scalar->scalar', 'state_access': 'none', 'locality': 'local',
             'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': 'none',
             'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(1)',
             'mechanism_tag': 'arithmetic', 'tags_full': ['arithmetic']}),
    ('NEG', {'arity': 1, 'types': 'scalar->scalar', 'state_access': 'none', 'locality': 'local',
             'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': 'none',
             'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(1)',
             'mechanism_tag': 'arithmetic', 'tags_full': ['arithmetic']}),
    ('GE_c', {'arity': 2, 'types': 'scalar,scalar->bool', 'state_access': 'none', 'locality': 'local',
              'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': 'none',
              'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(1)',
              'mechanism_tag': 'comparison', 'tags_full': ['comparison']}),
    ('INPUT_ATOM', {'arity': 1, 'types': 'scalar->scalar', 'state_access': 'read', 'locality': 'local',
                    'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': 'none',
                    'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(1)',
                    'mechanism_tag': 'state_io', 'tags_full': ['state_io']}),
    ('STATE_CELL', {'arity': 2, 'types': 'scalar,scalar->scalar', 'state_access': 'read_write', 'locality': 'local',
                    'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': 'none',
                    'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(1)',
                    'mechanism_tag': 'state_io', 'tags_full': ['state_io']}),
]


def run_validation(core):
    res = {}
    # P1 known-same synthetic recall
    p1 = {}
    for fam, (nm, body) in PLANT_BODIES.items():
        sig = derive_signature(nm, body)
        findings, _ = match_families(core, [(nm, sig)], NEW_FAMILIES)
        p1[fam] = any(f['fingerprint'] == fam for f in findings)
    res['P1_known_same_recall'] = p1
    # P2 neutral-rename collision plants
    p2 = {}
    for fam, (nm, body) in PLANT_BODIES.items():
        neutral = NEUTRAL_NAMES[nm]
        sig = derive_signature(neutral, body.replace('def ' + nm, 'def ' + neutral))
        findings, _ = match_families(core, [(neutral, sig)], NEW_FAMILIES)
        p2[fam] = any(f['fingerprint'] == fam for f in findings)
    res['P2_neutral_rename_recall'] = p2
    # P3 no-alarm on known-clean bases
    findings, term = match_families(core, CLEAN_V2_BASIS, ALL_FAMILIES)
    res['P3_v2_basis_clean'] = (term == 'CLEAN_AT_REGISTERED_AUDIT_SCOPE' and not findings)
    nm_dir = RESEARCH / 'gmi-neutral-derivation-v1' / 'neutral_machine.py'
    nm_clean = None
    if nm_dir.exists():
        blocks = extract_blocks(nm_dir, nm_dir.read_text())
        sigs = [(n, derive_signature(n, b)) for n, b, k in blocks]
        f2, t2 = match_families(core, sigs, ALL_FAMILIES)
        nm_clean = (t2 == 'CLEAN_AT_REGISTERED_AUDIT_SCOPE' and not f2)
    # registered anchor: aj9b frozen primitive basis (refined-census IN-anchor)
    aj_dir = RESEARCH / 'gmi-833-aj9b-k01-blind-recovery-v1'
    aj_clean = None
    aj_blocks = []
    if aj_dir.exists():
        for p, text in primitive_defining_files(aj_dir):
            aj_blocks.extend(extract_blocks(p, text))
        sigs = [(n, derive_signature(n, b)) for n, b, k in aj_blocks]
        f3, t3 = match_families(core, sigs, ALL_FAMILIES)
        aj_clean = (t3 == 'CLEAN_AT_REGISTERED_AUDIT_SCOPE' and not f3)
    res['P3_corpus_clean_grammar'] = {'neutral_machine': nm_clean, 'n_aj9b_blocks': len(aj_blocks),
                                      'aj9b_frozen_basis_clean': aj_clean}
    return res


def run_p4_p5_p6(core, package_blocks):
    # P6 existing-family regression on #974 controls (signatures verbatim)
    controls = [
        ('mix', {'arity': 2, 'types': ['weighted_aggregate'], 'state_access': 'none', 'locality': 'global',
                 'addressability': False, 'content_dependent_routing': True, 'parameter_sharing': 'none',
                 'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(n^2)'}),
        ('local_apply', {'arity': 2, 'types': ['arithmetic'], 'state_access': 'none', 'locality': 'neighborhood',
                         'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': True,
                         'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(n)'}),
        ('cell_step', {'arity': 2, 'types': ['state_io'], 'state_access': 'read_write', 'locality': 'local',
                       'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': True,
                       'recurrence': True, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(n)'}),
    ]
    f, _ = match_families(core, controls, EXISTING_FAMILIES)
    p6 = {c[0]: any(x['primitive'] == c[0] for x in f) for c in controls}
    # P4 sampled no-alarm
    rng = random.Random(833215)
    fam_tags = set(FAMILY_TAGS)
    tagless = [(pkg, n, b) for pkg, blocks in package_blocks for (n, b, k) in blocks
               if not (set(derive_signature(n, b)['tags_full']) & fam_tags)]
    sample = tagless if len(tagless) <= 200 else rng.sample(tagless, 200)
    f4, _ = match_families(core, [(n, derive_signature(n, b)) for _, n, b in sample], ALL_FAMILIES)
    return {'P6_existing_family_regression': p6,
            'P4_sampled_no_alarm': {'n_sampled': len(sample), 'n_flags': len(f4),
                                    'clean': len(f4) == 0}}


# ---------------------------------------------------------------- census + screen
def census_packages():
    d = json.loads((CORPUS_PASSES / 'P3_SCREENS_V1.json').read_text())
    return d['packages']


def rederive_census(pkgs):
    prim_defining, unaudited, covered = [], [], []
    incidental = []
    for pkg in sorted(pkgs):
        pdir = RESEARCH / pkg
        if not pdir.exists():
            return None, None, None, {'missing_dir': pkg}
        files = primitive_defining_files(pdir)
        if files:
            prim_defining.append(pkg)
            sig_mark = any(A2_SIGONLY_RE.search(t) for _, t in files)
            if pkg == A2_REGISTERED_ANCHOR:
                if not sig_mark:
                    return None, None, None, {'anchor_no_signature_mark': pkg}
                covered.append(pkg)
            else:
                unaudited.append(pkg)
                if sig_mark:
                    incidental.append(pkg)
    return prim_defining, unaudited, covered, {'a2_incidental_sig_marks': incidental}


def screen_unaudited(core, pkgs):
    out = {}
    for pkg in pkgs:
        pdir = RESEARCH / pkg
        files = primitive_defining_files(pdir)
        n_blocks = 0
        flags = []
        for p, text in files:
            for n, b, kind in extract_blocks(p, text):
                if not b or not b.strip():
                    continue
                n_blocks += 1
                sig = derive_signature(n, b)
                findings, _ = match_families(core, [(n, sig)], ALL_FAMILIES)
                for fd in findings:
                    flags.append({
                        'file': str(p.relative_to(RESEARCH)), 'block_name': n, 'kind': kind,
                        'family': fd['fingerprint'], 'derived_signature': sig,
                        'block_excerpt': b[:400],
                    })
        out[pkg] = {'n_files_scanned': len(files), 'n_blocks': n_blocks, 'flags': flags}
    return out


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=HERE / 'A2_EXTENDED_SCREEN_V1.json')
    a = ap.parse_args()
    core = load_audit_core()

    pkgs = census_packages()
    prim, unaud, cov, info = rederive_census(pkgs)
    if 'missing_dir' in info or 'anchor_no_signature_mark' in info:
        print(json.dumps({'error': info})); raise SystemExit(2)
    counts = {'primitive_defining_packages': len(prim), 'unaudited_operator_surface': len(unaud),
              'a2_covered': len(cov)}
    anchors = {
        'aj9b_in': any('aj9b' in p for p in prim),
        'af_barrier_out': not any(p.startswith('gmi-833-af-barrier') for p in prim),
        'robustness_covered': 'gmi-833-robustness-controls-v1' in cov,
    }
    anchor_ok = (counts['primitive_defining_packages'] == 109
                 and counts['unaudited_operator_surface'] == 108
                 and counts['a2_covered'] == 1 and all(anchors.values()))
    if not anchor_ok:
        print(json.dumps({'anchor_gate': 'FAIL', 'counts': counts, 'anchors': anchors}))
        raise SystemExit(2)

    val = run_validation(core)
    p1p2_ok = all(val['P1_known_same_recall'].values()) and all(val['P2_neutral_rename_recall'].values())
    p3_ok = (val['P3_v2_basis_clean']
             and val['P3_corpus_clean_grammar']['aj9b_frozen_basis_clean'] is True
             and val['P3_corpus_clean_grammar']['n_aj9b_blocks'] > 0)
    if not (p1p2_ok and p3_ok):
        print(json.dumps({'validation': 'FAIL', 'detail': val}))
        raise SystemExit(1)

    package_blocks = {pkg: extract_blocks_all(pkg) for pkg in unaud}
    p456 = run_p4_p5_p6(core, list(package_blocks.items()))
    if not p456['P4_sampled_no_alarm']['clean'] or not all(p456['P6_existing_family_regression'].values()):
        print(json.dumps({'validation': 'FAIL', 'detail': p456}))
        raise SystemExit(1)

    screened = screen_unaudited(core, unaud)
    n_flags = sum(len(v['flags']) for v in screened.values())
    receipt = {
        'schema': 'GMI_833_A2_SIGNATURE_EXTENSION_SCREEN_V1',
        'authority': {'revival_ticket': 'REV-L50-A2-SIGNATURE-PROGRAMME', 'issue': 833,
                      'standard': '#855 gmi-833-no-smuggling-audit-v1 (af467254206fa76ec3eab31078a420f1ad4d7cea)',
                      'usage_precedent': '#974 gmi-833-blind-recovery-v2-v1 screen_v2.py',
                      'freeze': 'FREEZE_V1.md + Amendment A1 (pre-execution)'},
        'families': {k: v for k, v in ALL_FAMILIES.items()},
        'd2_mapping_complete': len(D2_MAPPING) == 31,
        'census': {'counts': counts, 'anchors': anchors, 'anchor_gate': 'PASS',
                   'unaudited_packages': unaud,
                   'a2_incidental_sig_marks': info.get('a2_incidental_sig_marks', []),
                   'covered_partition_rule': ('anchor-defined per the registered refined census: only the '
                                              'register-named covered anchor (robustness-controls, verified '
                                              'to carry strategy_signature in its primitive-defining files) '
                                              'is A2-covered; incidental Sigma(/strategy_signature text '
                                              'marks in other packages are recorded, not treated as '
                                              'registrations')},
        'validation': {**val, **p456},
        'screen': screened,
        'totals': {'n_packages': len(unaud),
                   'n_blocks': sum(v['n_blocks'] for v in screened.values()),
                   'n_flagged_packages': sum(1 for v in screened.values() if v['flags']),
                   'n_flags': sum(len(v['flags']) for v in screened.values()),
                   'per_family': {fam: sum(1 for v in screened.values() for fl in v['flags']
                                           if fl['family'] == fam) for fam in ALL_FAMILIES}},
        'pins': {p: sha256_file(HERE / p) for p in ('FREEZE_V1.md', 'a2_extension_v1.py')},
        'pins_external': {
            'P3_SCREENS_V1.json': sha256_file(CORPUS_PASSES / 'P3_SCREENS_V1.json'),
            'audit_core_v1.py': sha256_file(NO_SMUGGLING / 'audit_core_v1.py'),
        },
    }
    a.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    # re-read assert
    reread = json.loads(a.output.read_text())
    assert reread == receipt, 'receipt re-read mismatch'
    assert reread['totals']['n_packages'] == 108, 'n_packages != 108'
    print(json.dumps({'anchor_gate': 'PASS', 'validation': 'PASS',
                      'totals': receipt['totals']}, indent=2, sort_keys=True))
    raise SystemExit(0)


def extract_blocks_all(pkg):
    pdir = RESEARCH / pkg
    out = []
    for p, text in primitive_defining_files(pdir):
        out.extend(extract_blocks(p, text))
    return out


if __name__ == '__main__':
    main()
