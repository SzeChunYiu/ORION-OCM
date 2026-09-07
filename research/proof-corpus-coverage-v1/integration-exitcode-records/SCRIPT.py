"""One portable integration run on billy-laptop; preserve commands and raw evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET

BASE = Path('/home/billy/orion-director-work/20260907')
REPO = BASE / 'ocm-proof-corpus-coverage'
PACKAGE = REPO / 'research/proof-corpus-coverage-v1'
OUT = BASE / 'coverage-portable-integration-20260907-v3'
PYTHON = str(BASE / 'proof-runtime-engineering-env/bin/python')
NATIVE_SEAL = '523531c5bb7ca79b4f3ff5d5e6316960cef38dcddcd82dc335421341280ffe2e'

def save(name, value):
    (OUT / name).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')

def digest(path):
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

def source_map():
    raw = subprocess.check_output(['/usr/bin/git', 'ls-files', '--cached', '--others',
        '--exclude-standard', '-z', '--', 'research/proof-corpus-coverage-v1',
        '.github/workflows/proof-corpus-coverage.yml'], cwd=REPO)
    names = sorted(set(raw.decode().split('\x00')) - {''})
    return {name: digest(REPO / name) for name in names if Path(name).suffix in {'.py', '.lean', '.yml'}}

OUT.mkdir()
(OUT / 'SCRIPT.py').write_bytes(Path(__file__).read_bytes())
before = source_map()
save('SOURCE_FREEZE.json', before)
prefix = 'research/proof-corpus-coverage-v1/'
tests = sorted(str(p.relative_to(REPO)) for p in PACKAGE.glob('test_*.py'))
commands = [
    ('tests', [PYTHON, '-B', '-m', 'pytest', *tests, prefix + 'tests/',
        '--deselect=' + prefix + 'tests/test_registration_cli.py::test_cli_failure_is_retained_with_no_assignments_and_no_reuse',
        '--deselect=' + prefix + 'tests/test_registration_cli.py::test_cli_ignores_harmless_matching_header_policy_cache',
        '--junitxml=' + str(OUT / 'tests.xml'), '-q']),
    ('registration', [PYTHON, '-I', '-S', prefix + 'registration_evidence.py']),
    ('native', [PYTHON, '-I', '-S', prefix + 'native_evidence.py', '--seal-sha256', NATIVE_SEAL]),
    ('resource', [PYTHON, '-I', '-S', prefix + 'resource_exitcode_evidence.py']),
]
environment = dict(os.environ)
environment['OCM_RESOURCE_HOST_QUALIFICATION'] = '0'
environment['PYTHONDONTWRITEBYTECODE'] = '1'
save('PRELAUNCH.json', {'commands': commands, 'cwd': str(REPO),
    'environment_overrides': {'OCM_RESOURCE_HOST_QUALIFICATION': '0', 'PYTHONDONTWRITEBYTECODE': '1'},
    'python': {'path': str(Path(PYTHON).resolve()), **digest(Path(PYTHON).resolve())},
    'scope': 'Portable engineering checks only; no registration/native/resource/corpus dispatch'})
records = []
for name, argv in commands:
    start = time.monotonic()
    result = subprocess.run(argv, cwd=REPO, env=environment, capture_output=True, timeout=180)
    elapsed = time.monotonic() - start
    (OUT / (name + '.stdout')).write_bytes(result.stdout)
    (OUT / (name + '.stderr')).write_bytes(result.stderr)
    record = {'name': name, 'returncode': result.returncode, 'wall_s': elapsed,
        'stdout': digest(OUT / (name + '.stdout')), 'stderr': digest(OUT / (name + '.stderr'))}
    records.append(record)
    save('PROCESSES.json', records)
    if result.returncode:
        save('FAILURE.json', record)
        raise SystemExit('Integration refused: ' + name)
after = source_map()
save('SOURCE_POSTCHECK.json', after)
if before != after:
    raise SystemExit('Source changed during integration')
suites = list(ET.parse(OUT / 'tests.xml').getroot().iter('testsuite'))
counts = {k: sum(int(s.attrib.get(k, 0)) for s in suites) for k in ['tests', 'failures', 'errors', 'skipped']}
assert counts['errors'] == counts['failures'] == 0
result = {'terminal': 'PORTABLE_INTEGRATION_PASS', 'counts': counts,
    'source_files': len(before), 'source_changed': False,
    'guards': {name: json.loads((OUT / (name + '.stdout')).read_bytes()) for name in ['registration', 'native', 'resource']},
    'scope': 'Engineering controls and retained evidence custody; no new native or real-corpus execution'}
save('RESULT.json', result)
save('FILES.json', {p.name: digest(p) for p in sorted(OUT.iterdir()) if p.is_file()})
print(json.dumps(result, sort_keys=True))
