from pathlib import Path
import hashlib,json,shutil,datetime
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.event import StaleStateHash
original=Path('/home/billy/orion-director-work/20260906/clia-reuse-capture-v2/arm-state/ocm/ledger.jsonl')
if not original.is_file():
 original=Path('/home/billy/orion-director-work/20260906/clia-reuse-capture-v2/state/ocm/ledger.jsonl')
assert original.is_file(),str(original)
d=Path('/home/billy/orion-director-work/20260906/clia-reuse-replay-repair')
copy=d/'v2-state-copy';copy.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(original);shutil.copyfile(original,copy/'ledger.jsonl')
try: OCMRuntime(copy)
except StaleStateHash as exc:
 result={'status':'EXPECTED_HISTORICAL_REFUSAL','exception':type(exc).__name__,'reason':str(exc)}
else: raise AssertionError('historical inconsistent ledger unexpectedly accepted')
assert before==sha(original)==sha(copy/'ledger.jsonl')=='f0f39dea71d13e1c37390d2f3ae810b3e863fc2e811123c27b77989af83a1a17'
assert '8c235b497adf46fe3d29e32c98f33c5dac70d176ae8a30f964feb67e7ae379e3' in result['reason']
assert '372ab7dfd446bed5531d8a2cc81f266da8e41778466f1da113b9b54c7a0e0226' in result['reason']
result.update(original=str(original),ledger_sha256=before,copy_sha256=sha(copy/'ledger.jsonl'),
 source_sha256=sha(Path('src/ocm/runtime/ocm_runtime.py')),recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 scope='Copied ledger only; constructor performs replay, no model, no solver, no events appended; original untouched')
(d/'historical-v2-refusal.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
