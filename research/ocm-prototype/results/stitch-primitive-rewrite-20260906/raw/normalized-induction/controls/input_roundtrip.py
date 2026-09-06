"""Pure source/serialization control; no donor or native solver is callable."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source'))
import generation_clia as G
import generation_stitch as S
import clia_process
from clia_tasks import signatures, validate_task

def forbidden(*args, **kwargs):
    raise RuntimeError('NATIVE_CALL_FORBIDDEN_IN_HARMLESS_CONTROL')
clia_process.invoke = forbidden
S.donor = forbidden

data = json.loads((ROOT / 'experiences.json').read_text())
old = json.loads((ROOT / 'predecessor/original-induction-experiences.json').read_text())
normalized = json.loads((ROOT / 'predecessor/normalization-train-qualification.json').read_text())
if S.SETTINGS != {'iterations': 1, 'max_arity': 2, 'threads': 1, 'silent': True}:
    raise ValueError('SETTINGS_DRIFT')
if not (len(data['experiences']) == len(old['experiences']) == len(normalized['rows']) == 2):
    raise ValueError('ASSIGNMENT_DRIFT')
records = []
for current, prior, sealed in zip(data['experiences'], old['experiences'], normalized['rows']):
    if current['task'] != prior['task'] or current['task']['task_id'] != sealed['id']:
        raise ValueError('TASK_DRIFT')
    if current['candidate'] != sealed['decoded']['candidate']:
        raise ValueError('NORMALIZED_CANDIDATE_DRIFT')
    if current['historical_check'] != sealed['fixed_spec']:
        raise ValueError('HISTORICAL_CHECK_DRIFT')
    validate_task(current['task'])
    sigs = signatures(current['task'])
    encoded = G.encode(current['candidate'], sigs)
    if len(encoded) != 1:
        raise ValueError('EXPECTED_ONE_FUNCTION')
    restored = G.decode(encoded[0]['program'], encoded[0]['name'], sigs)
    if restored['candidate'] != current['candidate'] or restored['macro_calls_in_input']:
        raise ValueError('ROUNDTRIP_OR_MACRO_DRIFT')
    records.append({'task_id': sealed['id'], 'status': 'PASS',
                    'encoded': encoded, 'restored': restored,
                    'candidate_sha256': hashlib.sha256(current['candidate'].encode()).hexdigest()})
loaded = [x for x in sys.modules if x in ('stitch_core', 'z3', 'cvc5') or x.startswith(('stitch_core.', 'z3.', 'cvc5.'))]
if loaded:
    raise ValueError('UNEXPECTED_NATIVE_MODULE_IMPORT: ' + repr(loaded))
print(json.dumps({'status': 'PASS', 'rows': records,
                  'native_calls': 0, 'native_modules_loaded': loaded,
                  'scope': 'Exact saved input and pure encode/decode only'}, indent=2))
