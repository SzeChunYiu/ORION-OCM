"""Portable custody for the existing goal-only bridge. Hashes are not authority."""
from __future__ import annotations
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BRIDGE = REPO / 'research/ordinary-goal-native-bridge-v1'

class Refusal(ValueError):
    pass

def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)

def encoded(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def raw_id(raw: bytes) -> dict:
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def identity(value) -> dict:
    return raw_id(encoded(value))

def parse(raw: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def constant(value):
        raise Refusal('NONFINITE_JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)

def checked_read(path: Path, pin: dict) -> bytes:
    require(type(pin) is dict and set(pin) == {'bytes', 'sha256'}, 'PIN_FIELDS')
    require(type(pin['bytes']) is int and 0 <= pin['bytes'] <= 64_000_000, 'PIN_SIZE')
    require(type(pin['sha256']) is str and len(pin['sha256']) == 64, 'PIN_DIGEST')
    require(not path.is_symlink() and path.is_file(), 'REGULAR_INPUT_REQUIRED')
    with path.open('rb') as stream:
        raw = stream.read(pin['bytes'] + 1)
    require(raw_id(raw) == pin, 'CONTENT_PIN: ' + path.name)
    return raw

def store(path: Path, raw: bytes) -> None:
    # Exclusive writes preserve failed attempts; no overwrite or implicit retry.
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def checked_sources(repo: Path = REPO) -> dict:
    manifest = parse((HERE / 'SOURCE_PINS.json').read_bytes())
    require(manifest['schema'] == 'ordinary.cold-native.sources.v1', 'SOURCE_SCHEMA')
    for relative, pin in manifest['files'].items():
        path = Path(relative)
        require(not path.is_absolute() and '..' not in path.parts, 'SOURCE_PATH')
        checked_read(repo / path, pin)
    native = {p.relative_to(repo).as_posix(): raw_id(p.read_bytes())
              for p in sorted((repo / 'src/ocm').rglob('*.py')) if p.is_file()}
    require({'files': len(native), 'canonical_manifest': identity(native)}
            == manifest['ocm_python_tree'], 'OCM_SOURCE_TREE_DRIFT')
    return manifest

def adapter_sources() -> dict:
    return {name: raw_id((HERE / name).read_bytes()) for name in
            ('custody.py', 'worker.py', 'ocm_route.py', 'qualify.py', 'SOURCE_PINS.json')}

def execution_identity(upstream: dict) -> dict:
    return identity({'upstream': upstream, 'adapter': adapter_sources()})

def load_bridge(runtime_dir: Path, *, include_fixture: bool = False):
    manifest = checked_sources()
    # Never run in a process containing another generation of these modules.
    source = BRIDGE / 'source'
    names = {p.stem for p in (source / 'vendor').glob('*.py')}
    names |= {'goal_library', 'goal_solve', 'goal_native', 'authored_fixture', 'lark'}
    require(not names.intersection(sys.modules), 'PRELOADED_BRIDGE_MODULE')
    runtime_dir.mkdir(exist_ok=False)
    archive = BRIDGE / 'runtime/LARK-1.3.1.tar.gz'
    # The archive identity was checked above. Only regular, contained files are accepted.
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        require(all(m.isfile() and not Path(m.name).is_absolute()
                    and '..' not in Path(m.name).parts for m in members), 'RUNTIME_ARCHIVE_MEMBER')
        tar.extractall(runtime_dir, filter='data')
    runtime = runtime_dir / 'lark-runtime'
    original = parse((BRIDGE / 'runtime/ORIGINAL-RUNTIME.json').read_bytes())
    require({p.relative_to(runtime).as_posix() for p in runtime.rglob('*') if p.is_file()}
            == set(original['files']), 'RUNTIME_FILE_POPULATION')
    for path, pin in original['files'].items():
        checked_read(runtime / path, pin)
    sys.path[:0] = [str(source), str(source / 'vendor'), str(runtime)]
    library = importlib.import_module('goal_library')
    solve = importlib.import_module('goal_solve')
    native = importlib.import_module('goal_native')
    fixture = importlib.import_module('authored_fixture') if include_fixture else None
    return library, solve, native, fixture, manifest

BUNDLE_NAMES = {'base.mm', 'joined.mm', 'manifest.json', 'qualification.json'}

def write_bundle(directory: Path, bundle: dict) -> dict:
    directory.mkdir(exist_ok=False)
    files = {'base.mm': bundle['base'], 'joined.mm': bundle['joined'],
             'manifest.json': encoded(bundle['manifest']), 'qualification.json': bundle['receipt']}
    for name, raw in files.items():
        store(directory / name, raw)
    return {name: raw_id(raw) for name, raw in files.items()}

def read_bundle(directory: Path, pins: dict, library_module):
    require(type(pins) is dict and set(pins) == BUNDLE_NAMES, 'BUNDLE_POPULATION')
    require({p.name for p in directory.iterdir()} == BUNDLE_NAMES, 'EXTRA_OR_MISSING_BUNDLE_INPUT')
    values = {name: checked_read(directory / name, pin) for name, pin in pins.items()}
    manifest = parse(values['manifest.json'])
    return library_module.Library(values['base.mm'], values['joined.mm'], manifest,
                                  library_module.identity(manifest), values['qualification.json'],
                                  pins['qualification.json'])

def validate_request(request: dict) -> None:
    require(type(request) is dict and set(request) == {'schema', 'task', 'mode', 'bundle',
            'label', 'holes', 'nonce', 'route', 'state'}, 'REQUEST_FIELDS')
    require(request['schema'] == 'ordinary.cold-native.request.v1', 'REQUEST_SCHEMA')
    require(type(request['nonce']) is str and len(request['nonce']) == 32
            and all(c in '0123456789abcdef' for c in request['nonce']), 'INVOCATION_NONCE')
    require(request['mode'] in ('enabled', 'resident-disabled', 'restored'), 'REQUEST_MODE')
    require(type(request['bundle']) is dict and set(request['bundle']) == BUNDLE_NAMES, 'BUNDLE_POPULATION')
    require(type(request['holes']) is list and type(request['label']) is str, 'CLAIM_NAMES')

    require(request['route'] in ('ordinary', 'ocm'), 'REQUEST_ROUTE')
    require((request['route'] == 'ordinary' and request['state'] is None)
            or (request['route'] == 'ocm' and type(request['state']) is dict
                and set(request['state']) == {'binding', 'lease'}), 'REQUEST_STATE')
