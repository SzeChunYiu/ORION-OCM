"""Complete portable membership and immutable before/after replay anchor.

Adapted from the existing external_unit_bindings_v1 strict traversal contract.
"""
from pathlib import Path
import hashlib
import json
import os
import stat
import subprocess
import sys

class CustodyError(ValueError): pass

def require(condition, message):
    if not condition: raise CustodyError(message)

def digest(data): return hashlib.sha256(data).hexdigest()

def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(value): raise CustodyError('nonfinite JSON')
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    json.dumps(value, allow_nan=False)
    return value

def local_name(name):
    require(type(name) is str and bool(name) and '\\' not in name, 'invalid local name')
    path = Path(name)
    require(not path.is_absolute() and path.as_posix() == name and
            all(p not in ('.','..') for p in path.parts), 'nonlocal path')
    return path

def regular_files(root):
    require(root.is_dir() and not root.is_symlink(), 'unit root must be a real directory')
    pending, files = [root], set()
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                path = Path(entry.path)
                mode = entry.stat(follow_symlinks=False).st_mode
                require(not stat.S_ISLNK(mode), 'symlink in unit')
                if stat.S_ISDIR(mode): pending.append(path)
                else:
                    require(stat.S_ISREG(mode), 'nonregular unit entry')
                    files.add(path.relative_to(root).as_posix())
    return files

def verify_manifest(root):
    root = Path(root)
    names = regular_files(root)
    require('MANIFEST_V1.json' in names, 'manifest missing')
    raw = (root/'MANIFEST_V1.json').read_bytes()
    manifest = strict_json(raw)
    require(type(manifest) is dict and set(manifest) == {'schema','files','receipt'}, 'manifest schema')
    require(manifest['schema'] == 'GMI_NATIVE_ADJOINT_UNIT_MANIFEST_V1', 'manifest version')
    require(manifest['receipt'] == 'RECEIPT_V1.json', 'receipt identity')
    files = manifest['files']
    require(type(files) is dict and set(files) | {'MANIFEST_V1.json'} == names
            and 'MANIFEST_V1.json' not in files and manifest['receipt'] in files, 'membership drift')
    for name, row in files.items():
        path = root/local_name(name)
        require(type(row) is dict and set(row) == {'sha256','bytes'}, 'file row schema')
        require(type(row['bytes']) is int and row['bytes'] >= 0, 'invalid file size')
        data = path.read_bytes()
        require(len(data) == row['bytes'] and digest(data) == row['sha256'], 'file content drift: '+name)
    return raw, manifest

def isolated_worker(root):
    command = [sys.executable] + (['-O'] if sys.flags.optimize else [])
    run = subprocess.run(command + ['-I','-B',str(root/'check_v1.py')], capture_output=True, timeout=60)
    require(run.returncode == 0 and not run.stderr, 'isolated checker failed')
    return run.stdout

def replay(root, worker=None):
    root = Path(root)
    initial_raw, initial = verify_manifest(root)
    expected = (root/initial['receipt']).read_bytes()
    expected_payload = strict_json(expected)
    actual = (worker or isolated_worker)(root)
    require((root/'MANIFEST_V1.json').read_bytes() == initial_raw, 'manifest changed during checker')
    final_raw, final = verify_manifest(root)
    require(final_raw == initial_raw and final == initial, 'unit changed during checker')
    require(type(actual) is bytes and actual == expected, 'full payload replay differs')
    require(strict_json(actual) == expected_payload, 'full payload differs')
    return {'status':'FULL_NATIVE_ADJOINT_PAYLOAD_REPLAY_PASS', 'manifest_sha256':digest(initial_raw),
            'receipt_sha256':digest(expected), 'payload_files':len(initial['files']),
            'finite_control_counts':expected_payload['counts']}
