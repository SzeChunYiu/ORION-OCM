"""Thin goal-only adapter over the existing OCM registry, solve and evidence lifecycle."""
from fractions import Fraction
from pathlib import Path
import sys
from custody import REPO, encoded, identity, parse, require
sys.path.insert(0, str(REPO / 'src'))
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime import solve as SV
from ocm.operators.registry import OperatorSpec, BackendKind
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope

SCOPE = Scope.of('cold-native.authored.v1')
METHOD = 'cold-native:resident-cohort'


def lease(rt):
    return {'head': rt.events[-1].event_hash if rt.events else None,
            'state': rt.state.kso_state_hash, 'evidence': rt.state.evidence_epoch,
            'registry': rt.state.registry_revision}


def live(rt, warrant):
    w = rt.state.evidence.nogoods.filter_interval(rt.state.nogoods.filter_interval(warrant))
    return w.liveness(rt.state.revoked | rt.state.evidence.revoked).value


def add_atom(rt, name, kind, body, warrant):
    anchor = Atom(name + ':input', 'observation', warrant, scope=SCOPE, quarantined=True)
    atom = Atom(name, kind, warrant, scope=SCOPE, content_ref=identity(body)['sha256'],
                meta=(('data', encoded(body).decode()),))
    edge = Hyperedge(name + ':support', (anchor.atom_id,), (name,), 'SUPPORT',
                     warrant=warrant, scope=SCOPE, head_weights=(Fraction(1),))
    rt.admit_batch(((anchor, (), 'OBSERVATION'), (atom, (edge,), 'OBSERVATION')))


def produce(root, bundle_pins, source_pin):
    rt = OCMRuntime(root)
    require(not rt.events, 'NONEMPTY_PRODUCER_STATE')
    # These are authored import/permission records, NOT learned or proved knowledge.
    _, env = rt.admit_evidence({'sources': source_pin, 'bundle': bundle_pins}, 'instruction',
                              'cold-native:environment', scope=SCOPE)
    body = {'bundle': bundle_pins, 'attribution': 'AUTHORED_SYNTHETIC_IMPORT_NOT_LEARNING'}
    _, method = rt.admit_evidence(body, 'instruction', 'cold-native:cohort-permission', scope=SCOPE)
    w = rt.state.evidence.citation_warrant([env, method])
    add_atom(rt, METHOD, 'procedure', body, w)
    rt.persist()
    return {'environment': env, 'method': method, 'body': body,
            'sources': source_pin, 'initial_lease': lease(rt)}


def restore(root, binding, bundle_pins, source_pin):
    rt = OCMRuntime(root)
    require(binding['body']['bundle'] == bundle_pins and binding['sources'] == source_pin,
            'OCM_SOURCE_OR_BUNDLE_BINDING')
    atom = rt.state.ks.atom_view.get(METHOD)
    require(atom is not None and atom.content_ref == identity(binding['body'])['sha256']
            and atom.meta == (('data', encoded(binding['body']).decode()),), 'OCM_METHOD_DATA')
    w = rt.state.evidence.citation_warrant([binding['environment'], binding['method']])
    require(atom.warrant == w and atom.scope == SCOPE, 'OCM_METHOD_WARRANT')
    return rt


def revise(root, binding, bundle_pins, source_pin, expected, operation):
    rt = restore(root, binding, bundle_pins, source_pin)
    require(lease(rt) == expected, 'STALE_OCM_LEASE')
    if operation == 'revoke':
        rt.revoke([binding['method']])
    elif operation == 'reinstate':
        rt.reinstate([binding['method']])
    else:
        require(False, 'REVISION_OPERATION')
    rt.persist()
    return {'lease': lease(rt), 'method_liveness': live(rt, rt.state.ks.atom_view[METHOD].warrant)}


def solve(root, binding, request, library, source_pin, generate, check):
    rt = restore(root, binding, request['bundle'], source_pin)
    require(lease(rt) == request['state']['lease'], 'STALE_OCM_LEASE')
    env_w = rt.state.evidence.citation_warrant([binding['environment']])
    require(live(rt, env_w) == 'LIVE', 'OCM_ENVIRONMENT_NOT_LIVE')
    method_w = rt.state.ks.atom_view[METHOD].warrant
    eligible = live(rt, method_w) == 'LIVE'
    require(eligible == (request['mode'] != 'resident-disabled'), 'MODE_LIVENESS_MISMATCH')
    _, eid = rt.admit_evidence(request, 'instruction', 'cold-native:issued-goal', scope=SCOPE)
    query_w = rt.state.evidence.citation_warrant([binding['environment'], eid])
    answer_w = (rt.state.evidence.citation_warrant([binding['environment'], eid, binding['method']])
                if eligible else query_w)
    qid = 'cold-native:query:' + request['nonce']
    add_atom(rt, qid, 'query_seed', request, query_w)
    stats = {'dispatches': 0, 'checks': 0, 'native': None, 'solver': None}
    issued = None
    op = None
    key = None
    def current():
        require(rt.state.operators.operators.get(key) is op, 'OCM_DISPATCHER_REBOUND')
        require(live(rt, query_w) == 'LIVE' and (live(rt, method_w) == 'LIVE') == eligible,
                'OCM_WARRANT_CHANGED')
    def backend(ks, inputs):
        nonlocal issued
        current()
        require(inputs == {'qid': qid}, 'OCM_DISPATCH_INPUT')
        stats['dispatches'] += 1
        result = generate()
        issued = encoded(result)
        stats['solver'] = result
        return parse(issued)
    def checker(packet):
        stats['checks'] += 1
        try:
            current()
            require(issued is not None and encoded(packet) == issued, 'OCM_UNISSUED_PACKET')
            if packet['terminal'] != 'GENERATED_PROOF_PENDING_NATIVE':
                return SV.Status.CANNOT_CHECK
            native = check(packet)
            stats['native'] = native
            current()
            require(native['terminal'] == 'GENERATED_PROOF_NATIVE_VERIFIED', 'OCM_NATIVE_REFUSAL')
            require(not native['selected_cohort_labels'] or eligible, 'OCM_DISABLED_COHORT')
            return SV.Status.PASS
        except Exception as exc:
            stats['checker_error'] = str(exc)
            return SV.Status.CANNOT_CHECK
    op = OperatorSpec('cold-native:goal-dispatch', source_pin['sha256'], BackendKind.PROGRAMMATIC,
                      backend, (), output_type='proof', warrant=env_w, scope=SCOPE, checker=checker)
    key = rt.register_operator(op)
    wrapper = SV.OperatorSpec(op.operator_id, op.version,
        lambda ks, name, context: op.backend(ks, {'qid': qid}), (qid,), output_type='proof',
        warrant=answer_w, scope=SCOPE, checker=op.checker)
    outcome = rt.solve(SV.Task(qid, (SV.QueryPart(qid, 'query_seed', (qid,)),),
                              context='cold-native.authored.v1'), (wrapper,))
    rt.persist()
    trace = outcome.trace.as_dict()
    # Trace objects may contain legitimate +/- infinity for universal diagnostic
    # ranges. Encode those explicitly; never alter the actual mathematical packet.
    def diagnostic(x):
        if isinstance(x, float) and not __import__('math').isfinite(x):
            return {'extended_real': str(x)}
        if isinstance(x, dict): return {str(k): diagnostic(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [diagnostic(v) for v in x]
        if isinstance(x, Fraction): return str(x)
        return x
    return {**stats, 'committed': SV.committed(outcome), 'trace': diagnostic(trace),
            'lease': lease(rt), 'method_liveness': live(rt, method_w),
            'runtime_meter': rt.state.meter.as_dict(), 'event_count': len(rt.events),
            'answer_support': [binding['environment'], eid] + ([binding['method']] if eligible else [])}
