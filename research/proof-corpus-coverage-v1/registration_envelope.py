"""Create-only process observations; a zero exit alone never authorizes registration."""
from hashlib import sha256
import json
from pathlib import Path
import resource
import subprocess
import sys
import time


def bound(path):
    path = Path(path).absolute()
    if path.resolve(strict=True) != path or not path.is_file(): raise ValueError('canonical regular file required')
    value = sha256(); size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block); size += len(block)
    return {'path': str(path), 'sha256': value.hexdigest(), 'bytes': size}


def write(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode())


def main():
    if len(sys.argv) != 5 or not sys.flags.isolated or not sys.flags.no_site:
        raise SystemExit('usage: pinned-python -I -S registration_envelope.py INVENTORY BARE_GIT NEW_RUN NEW_ENVELOPE')
    package = Path(__file__).resolve(strict=True).parent
    out = Path(sys.argv[4]).absolute()
    if out.parent.resolve(strict=True) != out.parent: raise ValueError('canonical envelope parent required')
    out.mkdir(exist_ok=False)
    command = [sys.executable, '-I', '-S', str(package / 'register.py'), *sys.argv[1:4]]
    write(out / 'PRELAUNCH.json', {'schema': 'ocm.f1.registration-envelope.v1', 'argv': command,
          'recorder': bound(__file__), 'entry': bound(package / 'register.py'), 'python': bound(sys.executable),
          'environment': {}, 'measurement': 'Child registration including its final seal; no proof workload.'})
    before = resource.getrusage(resource.RUSAGE_CHILDREN); start = time.monotonic()
    with (out / 'stdout').open('xb') as stdout, (out / 'stderr').open('xb') as stderr:
        process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                 env={}, check=False)
    wall = time.monotonic() - start; after = resource.getrusage(resource.RUSAGE_CHILDREN)
    write(out / 'PROCESS.json', {'schema': 'ocm.f1.registration-process.v1', 'returncode': process.returncode,
          'wall_seconds': wall, 'user_seconds': after.ru_utime - before.ru_utime,
          'system_seconds': after.ru_stime - before.ru_stime,
          'children_peak_rss_kib_nonaggregate': after.ru_maxrss,
          'stdout': bound(out / 'stdout'), 'stderr': bound(out / 'stderr'),
          'verdict': 'PROCESS_OBSERVATIONS_ONLY; independently verify registration seal and contents.'})
    print(json.dumps({'process': bound(out / 'PROCESS.json'), 'returncode': process.returncode}))
    return process.returncode


if __name__ == '__main__': raise SystemExit(main())
