"""Thin program-data → registered callable → existing SV.solve adapter; no new executive."""
from dataclasses import replace
import time
from ocm.kso.ids import content_hash
from ocm.kso.warrant import WarrantProfile
from ocm.operators.registry import BackendKind, OperatorSpec
from ocm.runtime import solve as SV
from ocm.store.evidence import Channel
import g1_vessel
from g1_field import CLIA, MODEL, SCOPE, encode, payload, put
import clia_reuse_descriptor as D
from clia_reuse_apply import CompiledProgram, check_value, validate_request
from clia_reuse_support import assumptions, decode, encode as encode_support

PREFIX = 'clia:executable:'


def atom_id(key):
    if not isinstance(key, str) or len(key) != 64 or any(c not in '0123456789abcdef' for c in key): raise ValueError('invalid descriptor identity')
    return PREFIX + key


def load(runtime, key):
    aid = atom_id(key); stored = payload(runtime.state.ks, aid)
    desc = D.validate(stored['descriptor'])
    if desc['id'] != key or encode_support(runtime.state.ks.atom_map()[aid].warrant) != desc['support']:
        raise ValueError('descriptor/support field binding mismatch')
    return desc


def adopt(runtime, proof_atom, *, history=()):
    """Import the actual admitted G1 program; one universal recheck, no acquisition invention."""
    atom = runtime.state.ks.atom_map()[proof_atom]; record = payload(runtime.state.ks, proof_atom)
    if not atom.is_live(runtime.state.revoked) or record.get('claim') != 'SPECIFICATION_VERIFIED_PROGRAM': raise ValueError('live admitted program required')
    if atom.atom_type != 'proof' or not atom.scope.covers('g1-pilot'): raise ValueError('proof type/scope mismatch')
    support = assumptions(runtime, atom.warrant)
    for eid in history:
        e = runtime.state.evidence.records.get(eid)
        if e is None or not e.is_assumption or eid in support.evidence: raise ValueError('history must be separate known assumption provenance')
    desc = D.create(record['query']['task'], record['output'], encode_support(support), history=history)
    put(runtime, atom_id(desc['id']), {'descriptor': desc, 'proof_atom': proof_atom}, support,
        (proof_atom,), 'EXACT_CHECKER', 'procedure')
    runtime.persist()
    return desc


def bind(runtime, key):
    """Explicit trusted-host rebind. Only data/contract survives a fresh runtime process."""
    start = time.perf_counter(); desc = load(runtime, key); aid = atom_id(key)
    if not runtime.state.ks.atom_map()[aid].is_live(runtime.state.revoked): raise ValueError('program is not live')
    compiled = CompiledProgram(desc)
    def backend(ks, request): return compiled.apply(request)
    operator = OperatorSpec('apply:' + key, D.digest(desc['checker_prior']), BackendKind.PROGRAMMATIC,
                            backend, (aid,), output_type='proof', warrant=decode(desc['support']), scope=SCOPE,
                            checker=lambda output: 'CANNOT_CHECK', lineage=(desc['program_sha256'],))
    registered = runtime.register_operator(operator); runtime.persist()
    return {'registry_key': registered, 'program_id': key, 'bind_wall_s': time.perf_counter() - start}


def catalogue(runtime, qid, request, checks, counters):
    # Full old syntax/synthesis catalogue remains visible; apply is NOT_APPLICABLE there.
    result = []
    for spec in g1_vessel.catalogue(runtime, qid, request, checks):
        def visit(ks, name, context, original=spec):
            counters['catalogue_visits'].append(original.operator_id)
            if original.operator_id == 'procedure:cvc5' and request['kind'] == 'clia': counters['synthesis_dispatches'] += 1
            return original.backend(ks, name, context)
        result.append(replace(spec, backend=visit))
    for key, manifest in sorted(runtime.state.operator_manifests.items()):
        if not manifest['operator_id'].startswith('apply:'): continue
        descriptor_key = manifest['operator_id'].split(':', 1)[1]
        desc = load(runtime, descriptor_key); bound = runtime.state.operators.operators.get(key)
        def backend(ks, name, context, desc=desc, bound=bound):
            counters['catalogue_visits'].append(name)
            if request.get('program_id') != desc['id']: return {'status': 'NOT_APPLICABLE'}
            if bound is None: return {'status': 'CANNOT_CHECK', 'reason': 'HOST_CALLABLE_UNBOUND'}
            counters['application_calls'] += 1
            return bound.backend(ks, request)
        def checker(output, desc=desc):
            if output.get('status') == 'CANNOT_CHECK': receipt = {'status': 'CANNOT_CHECK', 'reason': output.get('reason')}
            elif request.get('program_id') != desc['id']: receipt = {'status': 'FAIL', 'reason': 'NOT_APPLICABLE'}
            else:
                counters['pointwise_checks'] += 1; receipt = check_value(desc, request, output)
            checks.append({'operator': 'apply:' + desc['id'], 'phase': 'solve', **receipt})
            return SV.Status(receipt['status'])
        result.append(SV.OperatorSpec(manifest['operator_id'], manifest['version'], backend,
            (qid, atom_id(desc['id'])), scope=SCOPE, warrant=decode(desc['support']), checker=checker))
    return tuple(result)


def apply(runtime, request):
    start = time.perf_counter(); checks = []
    counters = {'catalogue_visits': [], 'application_calls': 0, 'pointwise_checks': 0, 'synthesis_dispatches': 0}
    admitted = None; output = None
    try:
        desc = load(runtime, request['program_id']); validate_request(desc, request)
        qid = 'clia:application:' + content_hash(request)
        put(runtime, qid, request, WarrantProfile.one(), (atom_id(desc['id']),), kind='query_seed')
        specs = catalogue(runtime, qid, request, checks, counters)
        refs = (qid, MODEL, CLIA, *(x for x in runtime.state.ks.ids if x.startswith(PREFIX)))
        task = SV.Task(qid, (SV.QueryPart(encode(request), 'query_seed', refs),), context='g1-pilot')
        before = runtime.state.ks.digest(); outcome = runtime.solve(task, specs)
        if SV.committed(outcome) and before == runtime.state.ks.digest():
            op, candidate, _ = outcome.candidate
            counters['pointwise_checks'] += 1; checked = check_value(desc, request, candidate)
            checks.append({'operator': op.operator_id, 'phase': 'admission', **checked})
            support = runtime.state.ks.atom_map()[atom_id(desc['id'])].warrant
            if checked['status'] == 'PASS' and support.is_live(runtime.state.revoked):
                record = {'claim': 'SPECIFICATION_VERIFIED_APPLICATION', 'request': request, 'output': candidate,
                          'check': checked, 'reused_object': atom_id(desc['id']), 'program_sha256': desc['program_sha256']}
                _, proof = runtime.admit_evidence(record, Channel.PROOF, 'fixed-host-pointwise-z3', scope=SCOPE, derived_from=support)
                admitted = 'clia:application-answer:' + content_hash(record)
                put(runtime, admitted, record, support.meet(WarrantProfile.of({proof})),
                    (qid, atom_id(desc['id'])), 'EXACT_CHECKER', 'proof')
                output = candidate
        runtime.persist()
        return {'status': 'ADMITTED' if admitted else 'NOT_ADMITTED', 'admitted_id': admitted, 'answer': output,
                'catalogue': [s.operator_id for s in specs], 'checks': checks, 'counters': counters,
                'trace': outcome.trace.as_dict(), 'apply_wall_s': time.perf_counter() - start}
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {'status': 'CANNOT_CHECK_APPLICATION', 'admitted_id': None, 'answer': None, 'reason': str(exc), 'counters': counters}


def audit(runtime):
    """Inspect current support only; no query, registration, rebinding or authority repair."""
    programs, answers = {}, {}
    for atom in runtime.state.ks.atoms:
        if atom.atom_id.startswith(PREFIX):
            key = atom.atom_id[len(PREFIX):]; desc = load(runtime, key)
            programs[key] = {'liveness': atom.liveness(runtime.state.revoked).value, 'support': desc['support'],
                'history_only': desc['history_only'], 'program_sha256': desc['program_sha256'],
                'host_bound': any(op.operator_id == 'apply:' + key for op in runtime.state.operators.operators.values())}
        elif atom.atom_id.startswith('clia:application-answer:'):
            answers[atom.atom_id] = {'liveness': atom.liveness(runtime.state.revoked).value}
    return {'programs': programs, 'answers': answers, 'revoked': sorted(runtime.state.revoked)}


def query(runtime, request, fault=None):
    """Extend only catalogue construction; existing G1 owns syntax/synthesis admission."""
    if isinstance(request, dict) and request.get('kind') == 'clia_apply': return apply(runtime, request)
    counters = {'catalogue_visits': [], 'application_calls': 0, 'pointwise_checks': 0, 'synthesis_dispatches': 0}
    def expanded(runtime, qid, request, checks, fault):
        if fault is not None: raise ValueError('reuse catalogue does not expose fault injection')
        return catalogue(runtime, qid, request, checks, counters)
    result = g1_vessel.query(runtime, request, fault, catalogue_builder=expanded)
    result['reuse_counters'] = counters
    return result
