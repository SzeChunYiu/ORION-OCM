"""Load the pinned parent readers and current registrar source, ignoring bytecode caches."""
from hashlib import sha256
from pathlib import Path
import sys
from types import ModuleType

PARENTS = {
    'env_inputs': ('proof-environment-v1/env_inputs.py', 'c920500fab1b01885355dc97d54b63e50a2b9e7b7bce84a6342628040754d77c'),
    'corpus_contract': ('proof-corpus-v1/corpus_contract.py', '768bf2cfdb6895ace0aa626119a27cc2e8b7b3a5549c8f4c91ebf6c4c05d1a04'),
    'corpus_tree': ('proof-corpus-v1/corpus_tree.py', '3a13774aef77bfc5504592b0914774dad040627f11792396bc3af68dc59d912e'),
    'corpus_git': ('proof-corpus-v1/corpus_git.py', '4c34d8dcc8f60c43fa08008601995c1e5e6710623bd17986f0fdc7a80b774fa9'),
}


def load_module(name, path, expected=None):
    path = Path(path).absolute()
    if path.resolve(strict=True) != path or not path.is_file(): raise ValueError('noncanonical source')
    raw = path.read_bytes(); actual = sha256(raw).hexdigest()
    if expected is not None and actual != expected: raise ValueError('parent source differs: ' + name)
    module = ModuleType(name); module.__file__ = str(path)
    module.__source_record__ = {'path': str(path), 'sha256': actual, 'bytes': len(raw)}
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def boot(package):
    package = Path(package).resolve(strict=True); sources = {}
    for name, (relative, expected) in PARENTS.items():
        sources[name] = load_module(name, package.parent / relative, expected).__source_record__
    for name in ('coverage_population', 'coverage_git', 'coverage_policy', 'coverage_register'):
        sources[name] = load_module(name, package / (name + '.py')).__source_record__
    return sys.modules['coverage_register'], sources
