"""Materialize historical training records; no target imports or native execution."""
from pathlib import Path
import collections, hashlib, io, json, os, subprocess, sys, zipfile
BASE = Path('/home/billy/orion-director-work/20260908')
WORKTREE = BASE / 'native-typed-lifecycle-publication-v1/worktree'
OUT = Path(__file__).resolve().parent
COMMIT = '448a54b851d0a188f76543a876bb963c315d0c6e'
PREVIOUS = '55495939dc4682ac027c44ff1cb62cb3cb94e204'
PATHS = {
    'extract': 'research/g2-causal-lemma-reuse-v1/extract.py',
    'admit': 'research/g2-causal-lemma-reuse-v1/records/admit-01/ADMIT.json',
    'screen': 'research/ordinary-cut-syntax-revival-v1/records/replay-01/RESULT.json',
    'archive': 'research/ordinary-cut-opportunity-result-v1/RAW.zip',
}
MEMBER = 'prospective-run-01/opportunity-01/RESULT.json'
def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
def identity(data): return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
def git(*args): return subprocess.check_output(['/usr/bin/git', '-C', str(WORKTREE), *args])
def save(name, data):
    p = OUT / name; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f: f.write(data)
def save_json(name, obj): save(name, json.dumps(obj, sort_keys=True, indent=2).encode() + b'\n')
# Preserve pinned extract.py's first-occurrence/remove traversal.
def select(screen, released):
    wanted, seen = [], set()
    for row in screen['screens']:
        if row['status'] != 'SCREENED_NEGATIVE_IN_DOMAIN': continue
        cid = row['canonical_id']
        if cid not in seen: seen.add(cid); wanted.append(cid)
    remaining, selected = wanted.copy(), []
    for ri, root in enumerate(released['roots']):
        for ci, cut in enumerate(root.get('cuts') or []):
            cid = cut.get('canonical_id')
            if cid not in remaining: continue
            selected.append((ri, ci, root, cut)); remaining.remove(cid)
    if remaining: raise ValueError('Missing historical IDs: ' + repr(remaining))
    return wanted, selected

def emit_suffix(lemma, label):
    # Same tokens, spaces and newlines as pinned emit_suffix; chr avoids shell interpolation.
    mark = chr(36); lines = [mark + '{']
    for hyp in lemma['hypotheses']:
        lines.append(hyp['label'] + ' ' + mark + 'e ' + ' '.join(hyp['statement']) + ' ' + mark + '.')
    lines.append(label + ' ' + mark + 'p ' + ' '.join(lemma['target']) + ' ' + mark + '= ' + ' '.join(lemma['proof']) + ' ' + mark + '.')
    lines.append(mark + '}')
    return '\n'.join(lines) + '\n'

script_before = identity(Path(__file__).read_bytes())
inputs, raw = {}, {}
for key, path in PATHS.items():
    raw[key] = git('show', COMMIT + ':' + path)
    previous_blob = git('rev-parse', PREVIOUS + ':' + path).decode().strip()
    current_blob = git('rev-parse', COMMIT + ':' + path).decode().strip()
    inputs[key] = {'commit': COMMIT, 'path': path, 'git_blob': current_blob, **identity(raw[key]),
        'previous_commit': PREVIOUS, 'previous_git_blob': previous_blob, 'unchanged_from_previous': current_blob == previous_blob}
    assert current_blob == previous_blob
with zipfile.ZipFile(io.BytesIO(raw['archive'])) as z: released_bytes = z.read(MEMBER)
inputs['released_result_member'] = {'archive_key': 'archive', 'member': MEMBER, **identity(released_bytes)}
admit, screen, released = json.loads(raw['admit']), json.loads(raw['screen']), json.loads(released_bytes)
wanted, chosen = select(screen, released)
assert len(wanted) == len(chosen) == len(admit['rows']) == 22
assert len({r['canonical_id'] for r in admit['rows']}) == 22
admission_by_id = {r['canonical_id']: (i, r) for i, r in enumerate(admit['rows'])}
rows, comparisons, discrepancies, suffix_parts, suffix_index = [], [], [], [], []
for ei, (ri, ci, root, cut) in enumerate(chosen):
    cid = cut['canonical_id']; ai, admission = admission_by_id[cid]; proposed = cut['proposal']
    mapping = {p['id']: p['variable'] for p in cut['context']['parameters']}
    translate = lambda seq: [mapping.get(token, token) for token in seq]
    observed = {'target': proposed['target'], 'n_hypotheses': len(proposed['hypotheses']),
        'n_proof': len(proposed['proof']), 'source_label': root['label'], 'zero_premise': len(proposed['hypotheses']) == 0}
    checks = {key: admission[key] == value for key, value in observed.items()}
    checks.update({'admission_order': ai == ei, 'issued_label_order': admission['label'] == f'cut-lemma-{ei:02d}',
        'query_to_target': translate(cut['body']['query']) == proposed['target'],
        'premises_to_ordered_hypotheses': [translate(p) for p in cut['body']['premises']] == [h['statement'] for h in proposed['hypotheses']]})
    if not all(checks.values()): discrepancies.append({'canonical_id': cid, 'checks': checks, 'observed': observed, 'admission': admission})
    screens = [{'row_index': j, 'row': r} for j, r in enumerate(screen['screens']) if r.get('canonical_id') == cid]
    rows.append({'canonical_id': cid, 'label': admission['label'], 'extraction_index': ei, 'admission_index': ai,
        'source_root': {'label': root['label'], 'ordinal': root['ordinal'], 'root_index': ri, 'cut_index': ci},
        'historical_cut': cut, 'historical_admission': admission, 'historical_screen_rows': screens,
        'record_identities': {'cut': identity(canonical(cut)), 'body': identity(canonical(cut['body'])),
            'proposal': identity(canonical(proposed)), 'admission_row': identity(canonical(admission))}})
    comparisons.append({'canonical_id': cid, 'label': admission['label'], 'checks': checks})
    data = emit_suffix(proposed, admission['label']).encode()
    suffix_index.append({'canonical_id': cid, 'label': admission['label'], 'offset': sum(map(len, suffix_parts)), **identity(data)})
    suffix_parts.append(data)
# Preserve any discrepancy; proposed bytes never confer admission or eligibility.
save_json('RECONCILIATION.json', {'schema': 'ordinary.goal.historical-reconciliation.v1', 'comparisons': comparisons,
    'discrepancies': discrepancies, 'screen_order_equals_extraction_order': wanted == [r['canonical_id'] for r in rows],
    'encoding_for_record_identities': 'JSON sort_keys=True,separators=(comma,colon),ensure_ascii=True; no trailing newline; not a redefinition of source canonical IDs'})
cohort = {'schema': 'ordinary.goal.historical-cohort.v1', 'status': 'HISTORICAL_TRAINING_MATERIALIZATION_ONLY',
    'source_commit': COMMIT, 'prefix_identity_reported_by_admit': {'bytes': admit['prefix_bytes'], 'sha256': admit['prefix_sha256']}, 'rows': rows}
save('COHORT.json', canonical(cohort) + b'\n'); save('PROPOSED-SUFFIX.mm', b''.join(suffix_parts))
save_json('SUFFIX-INDEX.json', {'schema': 'ordinary.goal.proposed-suffix-index.v1', 'rows': suffix_index,
    'whole': identity(b''.join(suffix_parts)), 'status': 'DETERMINISTIC_PROPOSED_BYTES_NOT_JOINED_LIBRARY_QUALIFICATION'})
save('inputs/ADMIT.json', raw['admit']); save('inputs/extract.py.reference', raw['extract'])
for name in ['ADMISSION-METADATA.json', 'PREFIX-RESOLUTION.json']:
    p = BASE / 'ordinary-goal-cohort-binding-v1' / name; data = p.read_bytes()
    inputs[name] = {'path': str(p), **identity(data)}; save('inputs/' + name, data)
save_json('INPUTS.json', {'schema': 'ordinary.goal.historical-inputs.v1', 'commit': COMMIT,
    'tree': git('rev-parse', COMMIT + '^{tree}').decode().strip(), 'inputs': inputs})
# Object and byte-slice readback only; do not interpret proofs.
reread = json.loads((OUT / 'COHORT.json').read_bytes()); suffix = (OUT / 'PROPOSED-SUFFIX.mm').read_bytes()
assert reread == cohort
for row, expected, part in zip(reread['rows'], chosen, suffix_index):
    assert row['historical_cut'] == expected[3]
    assert row['historical_admission'] == admit['rows'][row['admission_index']]
    chunk = suffix[part['offset']:part['offset'] + part['bytes']]
    assert identity(chunk) == {k: part[k] for k in ['bytes','sha256']}
    assert chunk == emit_suffix(row['historical_cut']['proposal'], row['label']).encode()
assert identity(Path(__file__).read_bytes()) == script_before
save_json('MATERIALIZATION.json', {'schema': 'ordinary.goal.historical-materialization.v1', 'pid': os.getpid(),
    'cwd': str(Path.cwd()), 'python_executable': sys.executable, 'python_version': sys.version,
    'script': {'path': str(Path(__file__).resolve()), **script_before}, 'script_unchanged': True,
    'cohort': identity((OUT/'COHORT.json').read_bytes()), 'rows': len(rows),
    'negative_screen_occurrences': sum(r['status']=='SCREENED_NEGATIVE_IN_DOMAIN' for r in screen['screens']),
    'selected_source_roots': len({r['source_root']['label'] for r in rows}),
    'zero_premise': sum(r['historical_admission']['zero_premise'] for r in rows),
    'parameter_type_counts': dict(collections.Counter(p['type'] for r in rows for p in r['historical_cut']['body']['parameters'])),
    'discrepancies': len(discrepancies), 'readback': 'All 22 cut/admission objects and exact suffix slices agree.',
    'scope': 'Published historical training records only; no target import/native/index/search/learner execution, heldout or evaluation file read; no runtime gate or current eligibility claim.'})
print(json.dumps({'cohort':identity((OUT/'COHORT.json').read_bytes()),'suffix':identity(suffix),'rows':len(rows),'discrepancies':len(discrepancies)}))
