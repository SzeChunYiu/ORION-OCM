"""Source-only registration launcher. Run pinned Python -I -S; never dispatch a proof."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from types import ModuleType


def record(path, raw=None):
    path = Path(path).absolute()
    if path.resolve(strict=True) != path or not path.is_file(): raise ValueError('canonical launcher input required')
    raw = path.read_bytes() if raw is None else raw
    return {'path': str(path), 'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def write(path, value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    with path.open('xb') as stream: stream.write(raw)
    return record(path, raw)


def main():
    if len(sys.argv) != 4 or not sys.flags.isolated or not sys.flags.no_site or sys.version_info[:3] != (3, 11, 14):
        raise SystemExit('usage: pinned-python -I -S register.py INVENTORY BARE_GIT NEW_OUTPUT')
    started = time.monotonic(); out = Path(sys.argv[3]).absolute()
    if out.parent.resolve(strict=True) != out.parent: raise ValueError('canonical output parent required')
    out.mkdir(exist_ok=False); verified_seal_returned = False
    try:
        started_record = write(out / 'STARTED.json', {'schema': 'ocm.f1.registration-start.v1', 'argv': sys.argv,
              'python': sys.version, 'isolated': True, 'no_site': True, 'state': 'NO_DISPATCH'})
        entry = record(__file__); package = Path(entry['path']).parent
        boot_path = package / 'coverage_boot.py'; raw = boot_path.read_bytes(); boot_record = record(boot_path, raw)
        module = ModuleType('coverage_boot'); module.__file__ = str(boot_path)
        exec(compile(raw, str(boot_path), 'exec', dont_inherit=True), module.__dict__)
        registrar, sources = module.boot(package)
        sources.update(register=entry, coverage_boot=boot_record)
        seal = registrar.register(sys.argv[1], sys.argv[2], out, package, sources, record(sys.executable), started_record)
        verified_seal_returned = True
        print(json.dumps({'state': 'REGISTERED_NO_DISPATCH', 'seal': seal,
                          'launcher_wall_seconds_including_seal': time.monotonic() - started}))
    except BaseException as exc:
        if not verified_seal_returned:
            write(out / 'FAILURE.json', {'schema': 'ocm.f1.registration-failure.v1',
                  'state': 'CANNOT_REGISTER', 'error': type(exc).__name__, 'detail': str(exc),
                  'launcher_wall_seconds': time.monotonic() - started, 'dispatches': 0})
        raise


if __name__ == '__main__': main()
