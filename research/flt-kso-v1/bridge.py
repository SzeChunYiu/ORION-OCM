"""Math subview of the existing runtime, not a second truth database.

Obligations and attempts are stored in the OCM ledger. This tranche deliberately
leaves theorem admission disabled: checking a candidate is not yet a reviewed
arbitrary-proof admission adapter. A later tranche must earn that boundary.
"""
from __future__ import annotations
from pathlib import Path
import time
from native import EqualityTask, construct, identity, render, statement
from ocm.kso.space import Atom
from ocm.kso.warrant import WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime import solve as SV
from ocm.runtime.operator_index import SolveOperatorIndex


def run_ocm(task: EqualityTask, environment: dict, store: str, checker=None, budget=64):
    started = time.monotonic()
    runtime = OCMRuntime(store)
    key = identity({'statement': task.as_dict(), 'environment': environment})
    goal = 'math:goal:' + key
    if goal in runtime.state.ks.ids:
        raise ValueError('FRESH_OBLIGATION_STORE_REQUIRED')
    runtime.admit_object(Atom(goal, 'goal', quarantined=True,
        content_ref=identity(statement(task)), meta=(('role', 'ProofObligation'),
        ('task', task.as_dict()), ('environment', environment),
        ('desired_certificate', 'Lean kernel proof'), ('truth_warrant', WarrantProfile.partial(()).as_dict()))), (), 'INSTRUCTION')
    construction = {}
    checked = {}
    def backend(ks, operator_id, inputs):
        data = dict(ks.atom(goal).meta)
        if data['environment'] != environment:
            raise ValueError('ENVIRONMENT_DRIFT')
        actual = EqualityTask(**data['task'])
        candidate = construct(actual, budget)
        construction.update(candidate)
        return candidate
    def check(candidate):
        if candidate != construction or candidate['statement_id'] != task.statement_id:
            return SV.Status.FAIL
        if candidate['terminal'] != 'CANDIDATE_CONSTRUCTED':
            return SV.Status.FAIL
        if checker is None:
            checked.update(terminal='CANNOT_CHECK_KERNEL_UNAVAILABLE')
            return SV.Status.CANNOT_CHECK
        receipt = checker(task, candidate['proof'])
        checked.update(receipt)
        if receipt.get('environment_id') != identity(environment) or receipt.get('statement_id') != task.statement_id or receipt.get('source_sha256') != identity_source(render(task, candidate['proof'])):
            checked['terminal'] = 'CHECKER_OR_ENVIRONMENT_MISMATCH'
            return SV.Status.CANNOT_CHECK
        return SV.Status.PASS if receipt['terminal'] == 'KERNEL_ACCEPTED' else SV.Status.CANNOT_CHECK
    operators = SolveOperatorIndex((SV.OperatorSpec('math.equality.bfs', 'v1', backend,
                                   (goal,), output_type='proof', checker=check),))
    outcome = runtime.solve(SV.Task(key, (SV.QueryPart(statement(task), 'goal', (goal,)),),
                                   targets=(goal,)), operators)
    # Keep the exact attempt as ordinary governed observation, never theorem warrant.
    runtime.admit_evidence({'role': 'ProofAttempt', 'statement_id': task.statement_id,
                           'construction': construction, 'checker': checked},
                          'observation', 'flt-kso-v1:attempt:' + key)
    before = runtime.state.kso_state_hash
    runtime.persist()
    reloaded = OCMRuntime(store)
    terminal = checked.get('terminal', construction.get('terminal', 'CANNOT_CHECK_SOLVE_PATH'))
    if terminal == 'KERNEL_ACCEPTED' and not SV.committed(outcome):
        terminal = 'CANNOT_CHECK_CANONICAL_COMMITMENT'
    return {'terminal': terminal, 'task_identity': key, 'statement_id': task.statement_id,
            'environment': environment, 'construction': construction, 'checker': checked,
            'canonical_solve': outcome.as_dict(), 'operator_index_build': operators.build_work,
            'N': len(runtime.state.ks.atoms), 'k': None, 'k_over_N': None,
            'active_count_limitation': 'Full canonical navigation scans global field; k is not instrumented end-to-end',
            'truth_liveness': WarrantProfile.partial(()).liveness(runtime.state.revoked).value,
            'new_theorems_admitted': 0, 'proof_admission': 'CANNOT_CHECK_ADMISSION_ADAPTER_NOT_QUALIFIED',
            'restart_identical': reloaded.state.kso_state_hash == before,
            'runtime_resource_vector': runtime.state.meter.as_dict(),
            'persistent_bytes': sum(p.stat().st_size for p in Path(store).rglob('*') if p.is_file()),
            'wall_seconds': time.monotonic() - started, 'LLM_CALLS': 0, 'LLM_TOKENS': 0}


def identity_source(source):
    import hashlib
    return hashlib.sha256(source.encode()).hexdigest()
