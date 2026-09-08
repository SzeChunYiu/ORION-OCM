"""Author a fixed fixture proposal; import no OCM, learner or native checker."""
from pathlib import Path
import hashlib
import itertools
import json

ROOT = Path('/home/billy/orion-director-work/20260908/native-typed-wff-fixtures-v1')
BUNDLE = Path('/home/billy/orion-director-work/20260908/native-ocm-adoption-v1/bundle')
PINS = {
    'PARENT.json': (1691014, '4812f96617ca3f33d6db4489979b3bc1b6a1f9d6b20528379cd17214301f2d8b'),
    'PREFIX.mm': (1757205, '9fbdc890cb89ad6805ced1fac23a1e9942775d5a7f60296bc0e064102806e411'),
}


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def write(name, value):
    raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    with (ROOT / name).open('xb') as stream:
        stream.write(raw)
    return identity(raw)


ROOT.mkdir(exist_ok=False)
loaded = {}
for name, (size, digest) in PINS.items():
    raw = (BUNDLE / name).read_bytes()
    if identity(raw) != {'bytes': size, 'sha256': digest}:
        raise ValueError('Original input changed: ' + name)
    loaded[name] = raw
catalogue = json.loads(loaded['PARENT.json'])
labels = {'syl', 'jca', 'simpr', 'jaoi', 'wa'}
contracts = [r for r in catalogue if r['label'] in labels]
if len(contracts) != 5 or {r['label'] for r in contracts} != labels:
    raise ValueError('Named ordinary contracts do not match')

premises = [['|-', '(', 'ph', '->', 'ps', ')'], ['|-', '(', 'ps', '->', 'ch', ')']]
queries = [
    ['|-', '(', 'ph', '->', 'ch', ')'],
    ['|-', '(', '(', 'ph', '\\/', 'ps', ')', '->', 'ch', ')'],
]
# These authored proof recipes are prospective inputs, not learned bodies.
common = 'wph wps wch H0 wph wps wch H0 H1 syl jca'.split()
first = 'wph wps wch wa wch'.split() + common + 'wps wch simpr syl'.split()
second = 'wph wch wps'.split() + first + ['H1', 'jaoi']
fixtures = []
suffix = []
for i, recipe in enumerate((first, second)):
    name = 'typed-wff-training-' + str(i)
    holes = [name + '-h' + str(j) for j in range(2)]
    proof = [dict(zip(('H0', 'H1'), holes)).get(t, t) for t in recipe]
    fixtures.append({'label': name, 'premises': premises, 'query': queries[i],
                     'holes': holes, 'proof': proof})
    suffix.append('${')
    suffix.extend(h + ' $e ' + ' '.join(p) + ' $.' for h, p in zip(holes, premises))
    suffix.append(name + ' $p ' + ' '.join(queries[i]) + ' $= ' + ' '.join(proof) + ' $.')
    suffix.append('$}')

value = {'schema': 'authored.typed-wff.fixture-proposal.v1',
         'status': 'NATIVE_AND_BRIDGE_QUALIFICATION_PENDING',
         'authoring': 'Explicit engineer-authored inputs; no acquired-method or corpus claim.',
         'parameters': [{'variable': v, 'type': 'wff', 'floating_label': f}
                        for v, f in zip(('ph', 'ps', 'ch'), ('wph', 'wps', 'wch'))],
         'dv': [], 'fixtures': fixtures,
         'candidate_policy': 'Enumerate all generic proper fragments; retain all outcomes and exact aliases. No expected candidate ID/body or utility selector.',
         'binding': {k: identity(v) for k, v in loaded.items()}}
files = {'FIXTURES.json': write('FIXTURES.json', value),
         'ASSERTIONS.json': write('ASSERTIONS.json', contracts)}
suffix_raw = ('\n'.join(suffix) + '\n').encode('ascii')
with (ROOT / 'TRAINING-SUFFIX.mm').open('xb') as stream:
    stream.write(suffix_raw)
files['TRAINING-SUFFIX.mm'] = identity(suffix_raw)

# Propositional authoring arithmetic only; this does not invoke the registered bridge.
table = []
for ph, ps, ch in itertools.product((False, True), repeat=3):
    table.append({'valuation': [ph, ps, ch], 'premises': [not ph or ps, not ps or ch],
                  'queries': [not ph or ch, not (ph or ps) or ch]})
files['AUTHOR-TRUTH-TABLE.json'] = write('AUTHOR-TRUTH-TABLE.json', {
    'scope': 'Boolean functions of the authored prose meanings; no parser, bridge or native proof qualification.',
    'variable_order': ['ph', 'ps', 'ch'], 'rows': table})
report = {'schema': 'authored.typed-wff.fixture-authoring.v1', 'files': files,
          'source': identity(Path(__file__).read_bytes()), 'native_calls': 0,
          'learner_calls': 0, 'bridge_calls': 0, 'protected_corpus_records_read': 0,
          'catalogue_rows_scanned_to_select_five_named_contracts': len(catalogue),
          'proof_token_counts': [len(x['proof']) for x in fixtures],
          'intended_new_proved_assertions': 2, 'intended_new_axioms': 0,
          'qualification': 'NOT_EXECUTED; exact native, typed trace and registered bridge checks remain pending.'}
write('AUTHORING.json', report)
print(json.dumps({'root': str(ROOT), 'proof_token_counts': report['proof_token_counts'],
                  'status': report['qualification']}))
