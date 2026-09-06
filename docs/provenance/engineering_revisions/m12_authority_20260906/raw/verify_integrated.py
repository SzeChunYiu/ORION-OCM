"""Read-only integrated wrapper/source/custody verification after recorder completion."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/home/billy/orion-director-work/20260906/ocm-v5-authority')
DIAG = ROOT.parent / 'v5-authority-integration'
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'src')]
import engineering_receipts as E
import engineering_predecessor as P

before = json.loads((DIAG / 'before-execution.json').read_text())
completed = json.loads((DIAG / 'recorder-command-completed.json').read_text())
assert completed['exit_code'] == 0
assert E.V4.source_inventory(ROOT) == before['source_inventory']
verified = E.verify(ROOT)
assert verified['receipt_path'] != before['prior_selection']['receipt_path']
assert P.verify(ROOT) == before['historical_custody']
for path, expected in before['evidence_sha256_excluding_mutable_selector'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
# Compare every tracked document/research file against the merge index, not only V5.
staged = subprocess.check_output(['/usr/bin/git', 'ls-files', '--stage', '-z', 'docs', 'research'], cwd=ROOT).decode().split('\0')
expected_blobs = {}
for entry in staged:
    if entry:
        metadata, path = entry.split('\t', 1)
        if path != E.CURRENT:
            assert metadata.split()[2] == '0'
            expected_blobs[path] = metadata.split()[1]
paths = sorted(expected_blobs)
actual_blobs = subprocess.check_output(['/usr/bin/git', 'hash-object', '--stdin-paths'], cwd=ROOT, input='\n'.join(paths)+'\n', text=True).splitlines()
assert len(actual_blobs) == len(paths)
assert all(expected_blobs[p] == h for p, h in zip(paths, actual_blobs))
env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'))
env.pop('OCM_V5_PREDECESSOR_ROOT', None)
results = []
for name in [f'm{i}_receipt.py' for i in range(1, 13)] + ['m12_paired_v5_receipt.py']:
    argv = [sys.executable, 'tools/' + name, '--verify']
    cp = subprocess.run(argv, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (DIAG / (name + '.log')).write_text(cp.stdout)
    results.append(dict(wrapper=name, argv=argv, exit_code=cp.returncode, output=cp.stdout))
    print(name, cp.returncode, flush=True)
report = dict(status='INTEGRATED_ENGINEERING_VERIFIED' if all(r['exit_code'] == 0 for r in results) else 'WRAPPER_VERIFICATION_FAILED',
              source_id=verified['source_id'], source_files=len(before['source_inventory']), source_unchanged=True,
              prior_selection=before['prior_selection'], current_selection=json.loads((ROOT / E.CURRENT).read_text()),
              predecessor=P.verify(ROOT), engineering_verification=verified,
              unchanged_checkpoint_evidence_files=len(before['evidence_sha256_excluding_mutable_selector']),
              unchanged_all_tracked_docs_research_files=len(paths),
              all_tracked_docs_research_scope='Every file under docs and research tracked at merge HEAD, except the expressly mutable CURRENT_ENGINEERING selector; exact Git blob equality',
              wrapper_results=results, provider_override='UNSET', protected_reevaluation='NOT_RUN',
              current_scientific_promotion='NOT_ESTABLISHED')
(DIAG / 'integrated-verification.json').write_text(json.dumps(report, indent=2)+'\n')
assert report['status'] == 'INTEGRATED_ENGINEERING_VERIFIED'
print(json.dumps({k:report[k] for k in ('status','source_id','source_files','unchanged_all_tracked_docs_research_files')},indent=2))
