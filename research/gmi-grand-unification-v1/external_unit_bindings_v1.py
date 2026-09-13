"""Bind complete immutable research units, including their transitive raw files."""
from pathlib import Path
import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_name(name):
    require(type(name) is str and bool(name), 'nonempty unit path required')
    p = Path(name)
    require(bool(p.parts) and not p.is_absolute() and p.as_posix() == name
            and all(part not in ('.', '..') for part in p.parts), 'nonlocal unit path')
    return p


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_object(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate manifest key')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite manifest value: ' + value)
    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    json.dumps(result, allow_nan=False)  # Reject overflowing exponents too.
    return result



def regular_files(unit):
    import os
    import stat
    pending, result = [unit], set()
    while pending:
        # scandir/stat errors propagate; incomplete traversal never means complete.
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                path = Path(entry.path)
                mode = entry.stat(follow_symlinks=False).st_mode
                require(not stat.S_ISLNK(mode), 'symlink in external unit')
                if stat.S_ISDIR(mode):
                    pending.append(path)
                else:
                    require(stat.S_ISREG(mode), 'unsupported external unit entry')
                    result.add(path.relative_to(unit).as_posix())
    return result


def verify_unit(repository, name, record):
    repository = Path(repository).resolve()
    relative = local_name(name)
    require(type(record) is dict and set(record) == {'manifest', 'sha256'},
            'malformed external unit record')
    unit = repository / relative
    require(unit.is_dir(), 'external unit missing')
    for part in (unit, *unit.parents):
        if part == repository:
            break
        require(not part.is_symlink(), 'symlink in external unit path')
    require(unit.resolve().is_relative_to(repository), 'external unit escaped repository')
    manifest_name = local_name(record['manifest']).as_posix()
    actual = regular_files(unit)
    require(manifest_name in actual, 'external unit manifest missing')
    raw = (unit / manifest_name).read_bytes()
    require(digest(raw) == record['sha256'], 'external unit manifest changed')
    manifest = strict_object(raw)
    require(type(manifest) is dict and type(manifest.get('files')) is dict,
            'external unit file map missing')
    files = manifest['files']
    require(manifest_name not in files, 'unit manifest cannot bind itself')
    require(actual == set(files) | {manifest_name}, 'external unit membership changed')
    total = 0
    for filename, row in files.items():
        local_name(filename)
        require(type(row) is dict and set(row) == {'bytes', 'sha256'},
                'malformed external unit file row')
        require(type(row['bytes']) is int and row['bytes'] >= 0, 'invalid external unit size')
        content = (unit / filename).read_bytes()
        require(len(content) == row['bytes'] and digest(content) == row['sha256'],
                'external unit content changed: ' + filename)
        total += len(content)
    if 'payload_files' in manifest:
        require(type(manifest['payload_files']) is int and manifest['payload_files'] == len(files),
                'external unit payload count differs')
    if 'payload_bytes' in manifest:
        require(type(manifest['payload_bytes']) is int and manifest['payload_bytes'] == total,
                'external unit payload size differs')
    return {'manifest_sha256': record['sha256'], 'payload_files': len(files),
            'payload_bytes': total}
