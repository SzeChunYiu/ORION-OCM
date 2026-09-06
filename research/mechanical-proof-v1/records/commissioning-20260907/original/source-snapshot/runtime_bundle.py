"""Copy and bind runtime files; hashes attest identity, not mechanism correctness."""
from hashlib import sha256
from pathlib import Path
import shutil


def file_hash(path):
    digest = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def tree_manifest(root):
    root = Path(root).resolve(strict=True)
    records = {}
    for path in sorted(root.rglob('*')):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            target = path.readlink()
            if target.is_absolute() or not path.resolve(strict=True).is_relative_to(root):
                raise ValueError('runtime link escapes registered root')
            records[name] = {'kind': 'link', 'target': str(target)}
        elif path.is_dir():
            records[name] = {'kind': 'directory'}
        elif path.is_file():
            records[name] = {'kind': 'file', 'sha256': file_hash(path), 'bytes': path.stat().st_size}
        else:
            raise ValueError('nonregular runtime entry')
    return records


def verify_tree(root, expected):
    if tree_manifest(root) != expected:
        raise ValueError('registered runtime tree differs')


def copy_python(prefix, destination):
    """Copy one CPython3.11 executable and stdlib, excluding installed packages.

    No claim is made about an arbitrary supplied interpreter; its exact executable
    and copied tree must enter the independent episode's reviewed runtime manifest.
    """
    prefix = Path(prefix).resolve(strict=True)
    destination = Path(destination)
    source = prefix / 'lib/python3.11'
    excluded = {'site-packages', '__pycache__'}
    for path in source.rglob('*'):
        if any(part in excluded for part in path.relative_to(source).parts):
            continue
        if path.is_symlink() and not path.resolve(strict=True).is_relative_to(source):
            raise ValueError('stdlib source has escaping link')
        if not (path.is_file() or path.is_dir()):
            raise ValueError('nonregular stdlib source entry')
    binary = prefix / 'bin/python3.11'
    if binary.is_symlink() or not binary.is_file():
        raise ValueError('registered Python executable must be a regular file')
    destination.mkdir(exist_ok=False)
    (destination / 'bin').mkdir()
    (destination / 'lib').mkdir()
    shutil.copy2(binary, destination / 'bin/python3.11')
    shutil.copytree(source, destination / 'lib/python3.11',
                    ignore=shutil.ignore_patterns(*excluded))
    return {'source_prefix': str(prefix), 'directory': str(destination.resolve()),
            'python_sha256': file_hash(destination / 'bin/python3.11'),
            'excluded': sorted(excluded), 'files': tree_manifest(destination)}
