"""Trusted fixed-target staging for the exposed F0 commissioning experiment."""
from hashlib import sha256
import json
from pathlib import Path

from lean_transport import render_term

HERE = Path(__file__).resolve().parent
TARGET_SHA256 = '0694094c1851d5fb72827f4af8a5de0e7d5fd14b646ad9926319f573206273ce'
FOUNDATION_SHA256 = '172665be0c68fd60ea0dfd7fbee3e4558f4df2325f637a91f3ed49875822bc87'


def source_bytes(candidate):
    term = render_term(candidate)
    # Generated binder names and the infer-before-check helper trigger only these
    # two style linters. Kernel checking and the strict axiom audit stay enabled.
    return ('import Target\n\nset_option linter.unusedVariables false\n'
            'set_option linter.defProp false\n\nnamespace OCMMechanicalProof\n'
            'def proposed :=\n  ' + term + '\n\n'
            'theorem constructed : F0Target.statement := @proposed\n'
            'end OCMMechanicalProof\n\n'
            '#print axioms OCMMechanicalProof.constructed\n').encode()


def stage_candidate(candidate, destination, root=HERE):
    """Render closed data against independent source; compilation happens later.

    A staged candidate can be ill-typed. Only the kernel can accept it. No
    candidate-supplied type, target name, dependency or code becomes authority.
    """
    source = source_bytes(candidate)
    root = Path(root)
    target_path = root / 'Target.lean'
    if target_path.is_symlink() or not target_path.is_file():
        raise ValueError('independent target must be a regular source file')
    target = target_path.read_bytes()
    if sha256(target).hexdigest() != TARGET_SHA256:
        raise ValueError('independent target identity differs')
    foundation_path = root.parent / 'proof-replay-v1' / 'Foundation.lean'
    if foundation_path.is_symlink() or not foundation_path.is_file():
        raise ValueError('Foundation dependency must be a regular source file')
    foundation = foundation_path.read_bytes()
    if sha256(foundation).hexdigest() != FOUNDATION_SHA256:
        raise ValueError('Foundation source identity differs')
    data = (json.dumps(candidate, separators=(',', ':')) + '\n').encode()
    files = {'Foundation.lean': foundation, 'Target.lean': target,
             'Candidate.lean': source, 'candidate.json': data}
    destination = Path(destination)
    destination.mkdir(parents=False, exist_ok=False)
    for name, content in files.items():
        (destination / name).write_bytes(content)
    return {'directory': str(destination.resolve()), 'target_sha256': TARGET_SHA256,
            'files': {name: sha256(content).hexdigest() for name, content in files.items()},
            'terminal': 'STAGED_UNCHECKED', 'formal_target': 'F0Target.statement'}
