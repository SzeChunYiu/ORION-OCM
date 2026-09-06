"""Fail-closed boundary for staged R2/R3 data; not a claimed OS sandbox.

This tranche has no registered isolated R2/R3 launcher. Even clean staging data
is refused. A textual import check is defense in depth, never process isolation.
"""
import json
from pathlib import Path
from substrate import Refusal, import_header, tokens, validate_public


def check_imports(source, allowed=('Init',)):
    imports=import_header(source)
    if any(name not in allowed for name in imports):
        raise Refusal('SOLUTION_LEAKAGE_DETECTED','unregistered import')
    forbidden={'axiom','sorry','admit','native_decide','#'}
    if any(t[0] in forbidden or t[0].startswith(('P2M.','Theorems.')) for t in tokens(source)[1]):
        raise Refusal('DISALLOWED_PROOF_SHORTCUT_OR_PRIVATE_REFERENCE')


def _pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise Refusal('PUBLIC_SCHEMA_MISMATCH','duplicate JSON key')
        result[key]=value
    return result


def require_executable_package(public_dir, private_roots=()):
    public=Path(public_dir)
    if any(p.is_symlink() for p in (public,*public.parents)):
        raise Refusal('SOLUTION_LEAKAGE_DETECTED','symlinked package')
    public=public.resolve(strict=True)
    for root in private_roots:
        root=Path(root).resolve()
        if public==root or root in public.parents or public in root.parents:
            raise Refusal('SOLUTION_LEAKAGE_DETECTED','private/public overlap')
    if sorted(p.name for p in public.iterdir())!=['PUBLIC.json']:
        raise Refusal('SOLUTION_LEAKAGE_DETECTED','undeclared file in public staging package')
    path=public/'PUBLIC.json'
    if path.is_symlink() or path.stat().st_size>2**20:
        raise Refusal('PUBLIC_SCHEMA_MISMATCH','manifest type or budget')
    with path.open(encoding='utf-8') as source:
        def invalid_constant(value): raise Refusal('PUBLIC_SCHEMA_MISMATCH',value)
        pub=json.load(source,object_pairs_hook=_pairs,parse_constant=invalid_constant)
    validate_public(pub)
    # No boolean switch, caller attestation, or executable fallback bypasses this.
    raise Refusal('CANNOT_CHECK_ISOLATION_AND_BOUNDARY',
                  'R2/R3 OS confinement, definition closure, boundary certificates and elaboration are unearned')
