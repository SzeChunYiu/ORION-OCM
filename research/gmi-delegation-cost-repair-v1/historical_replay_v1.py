"""Byte-exact positive historical replay before scientific countercontrols."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from typed_program_v1 import require

ROOT = Path(__file__).resolve().parent

def verify_raw():
    binding = json.loads((ROOT / 'RAW_BINDINGS_V1.json').read_text())
    raw = ROOT / 'raw'
    require({p.name for p in raw.iterdir()} == set(binding['files']), 'raw membership drift')
    for name, expected in binding['files'].items():
        path = raw / name
        require(path.is_file() and not path.is_symlink(), 'raw file kind drift')
        data = path.read_bytes()
        require(len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256'],
                'raw content drift: ' + name)
    return binding

def replay_historical():
    binding = verify_raw()
    rows = {}
    for script, expected in [('grand_gmi_delegation_invariant_cost_checks_v1.py',
                              'GRAND_GMI_DELEGATION_INVARIANT_COST_RECEIPT_V1.json'),
                             ('countercontrols_v1.py', 'COUNTERCONTROLS_V1.json')]:
        command = [sys.executable] + (['-O'] if sys.flags.optimize else [])
        process = subprocess.run(command + ['-I', '-B', str(ROOT / 'raw' / script)],
                                 capture_output=True, timeout=30)
        wanted = (ROOT / 'raw' / expected).read_bytes()
        require(process.returncode == 0 and not process.stderr and process.stdout == wanted,
                'historical full-payload replay failed: ' + script)
        rows[script] = {'byte_equal': True, 'payload_sha256': hashlib.sha256(wanted).hexdigest(),
                        'full_payload': json.loads(wanted)}
    require(verify_raw() == binding, 'raw binding drift during historical replay')
    return rows
