"""Static audit of first hosted V4 packet; never execute candidates or timers."""
from __future__ import annotations

import dis
import hashlib
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
COMMIT = 'd6147f95e48b2e4e4afc2c3bd1dee8551527c2fc'
RUN = '34749100254'
HARNESS = 'nn_nonnn_point_parity3_experiment_v4.py'
PREREG = 'NN_NONNN_POINT_PARITY3_PREREG_V4.json'
PACKET = 'NN_NONNN_POINT_PARITY3_HOSTED_RESULT_V4.json'
PROVENANCE = 'NN_NONNN_POINT_PARITY3_HOSTED_PROVENANCE_V4.json'
DIGESTS = {
    HARNESS: 'd39961ffa6fe81a978c9d9a45e91be500e7dc52178de183f7699b9fec31a256e',
    PREREG: '7d0b4bc0cf6c2655694a08c9c1261f354519e005e92ed3ecfc435e97cedac54b',
}
IDS = ('N_THRESHOLD_DNF4_V1', 'X_XOR2_V1', 'N_SUM_THRESHOLD3_V3', 'X_LOOKUP8_V3')
FAMILIES = dict(zip(IDS, ('NEURAL', 'NON_NEURAL', 'NEURAL', 'NON_NEURAL')))
KEYS = ('python_opcode_count_per_full_domain_sweep', 'wall_block_ns', 'process_block_ns')
EXPECTED = [sum((a, b, c)) % 2 for a in (0, 1) for b in (0, 1) for c in (0, 1)]


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise AuditError('Invalid finite JSON') from exc


def same(actual, expected, message):
    require(canonical(actual) == canonical(expected), message)


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'Duplicate JSON key')
            out[key] = value
        return out
    def constant(value):
        raise AuditError('Non-finite JSON')
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    canonical(value)
    return value


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def validate(packet, provenance, packet_bytes):
    expected_fields = {'candidate_expansion_attack', 'candidate_universe', 'capability',
        'claim_ceiling', 'dominated_by', 'environment', 'environment_gate_failures',
        'environment_gate_pass', 'expansion_expectation_passed', 'expansion_lineage',
        'experiment_id', 'frontier_candidate_ids', 'frontier_families',
        'independent_prospective_prediction', 'instrumentation', 'instrumentation_gate_pass',
        'measurement_schedule', 'measurements', 'null_baseline', 'opcode_counts',
        'preregistration_status_seen', 'protected_resource_measurement_executed',
        'protected_timing_measurement_executed', 'registered_expansion_expectation',
        'resource_boxes', 'resource_uncertainty_semantics', 'schema', 'terminal', 'winner_candidate_id'}
    require(type(packet) is dict and set(packet) == expected_fields, 'Packet field set differs')
    for name, expected in DIGESTS.items():
        require(sha((HERE / name).read_bytes()) == expected, 'Frozen source drift: ' + name)
    prereg = strict_json((HERE / PREREG).read_text())
    source = HERE / HARNESS
    spec = importlib.util.spec_from_file_location('static_v4_source', source)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source.read_bytes(), str(source), 'exec'), module.__dict__)
    # Importing definitions/disassembling their code does not call candidate bodies.
    module.validate_preregistration(prereg)
    same(packet, strict_json(packet_bytes.decode()), 'Packet bytes differ from parsed evidence')
    require(provenance['packet_sha256'] == sha(packet_bytes), 'Packet digest differs')
    excerpt = provenance['source_log_excerpt']
    require(provenance['source_log_excerpt_sha256'] == sha(excerpt.encode()), 'Log excerpt digest differs')
    stripped = '\n'.join(re.sub(r'^\ufeff?\d{4}-\d\d-\d\dT\S+Z\s?', '', line)
                         for line in excerpt.splitlines()) + '\n'
    require(stripped.encode() == packet_bytes, 'Hosted stdout differs byte-for-byte')
    same(provenance['tested_github_sha'], COMMIT, 'Wrong hosted source')
    same(provenance['run_id'], int(RUN), 'Wrong first run')
    same(provenance['job_id'], 103702229052, 'Wrong first job')
    same(provenance['run_attempt'], 1, 'Rerun is not the registered first attempt')
    require(provenance['event'] == 'push' and provenance['job_conclusion'] == 'success',
            'Missing successful first main-push custody')
    run = provenance['run_metadata']
    same([run['id'], run['run_attempt'], run['head_sha'], run['head_branch'], run['event'], run['conclusion']],
         [int(RUN), 1, COMMIT, 'main', 'push', 'success'], 'Run metadata differs')
    env = packet['environment']
    require(env['github_sha'] == COMMIT and env['github_run_id'] == RUN
            and env['github_run_attempt'] == '1' and env['github_ref'] == 'refs/heads/main'
            and env['github_event_name'] == 'push', 'Execution identity differs')
    require(env['python_implementation'] == 'CPython'
            and re.fullmatch(r'3\.12\.\d+', env['python_version']) is not None
            and env['runner_os'] == 'Linux', 'Wrong registered substrate')
    same(env['python_version_info'], [int(x) for x in env['python_version'].split('.')], 'Version metadata differs')
    require(env['harness_sha256'] == DIGESTS[HARNESS]
            and env['preregistration_sha256'] == DIGESTS[PREREG], 'Hosted source hashes differ')
    same(env['candidate_ast_sha256'], {c['candidate_id']: c['ast_sha256'] for c in prereg['candidates']},
         'Hosted candidate identity differs')
    require(packet['schema'] == 'NN_NONNN_POINT_PARITY3_RESULT_V4'
            and packet['experiment_id'] == prereg['experiment_id'], 'Wrong packet identity')
    for key in ('environment_gate_pass', 'instrumentation_gate_pass',
                'protected_timing_measurement_executed', 'protected_resource_measurement_executed'):
        require(packet[key] is True, 'Missing measurement gate: ' + key)
    same(packet['environment_gate_failures'], [], 'Environment failures present')
    require(packet['independent_prospective_prediction'] is False, 'Independent prediction falsely claimed')
    for key in ('measurement_schedule', 'claim_ceiling', 'expansion_lineage', 'registered_expansion_expectation'):
        same(packet[key], prereg[key], 'Registered metadata drift: ' + key)
    require(packet['preregistration_status_seen'] == 'PREREGISTERED_NOT_EXECUTED'
            and packet['candidate_expansion_attack'] == 'EXECUTED_AT_REGISTERED_FOUR_CANDIDATE_SCOPE',
            'Wrong registration/expansion status')
    same(packet['candidate_universe'], [{'candidate_id': cid, 'family': FAMILIES[cid]} for cid in IDS],
         'Candidate universe differs')
    require(set(packet['capability']) == set(IDS), 'Incomplete capability register')
    for cid in IDS:
        same(packet['capability'][cid], {'candidate_id': cid, 'family': FAMILIES[cid],
             'outputs': EXPECTED, 'expected': EXPECTED, 'correct': 8, 'total': 8, 'exact_gate_pass': True},
             'Capability mismatch: ' + cid)
    same(packet['null_baseline'], {'outputs': [0] * 8, 'correct': 4, 'total': 8}, 'Null differs')
    same(packet['resource_uncertainty_semantics'],
         'finite observed block envelope for this registered run; no population-confidence or cross-run generalization claim',
         'Resource uncertainty scope changed')

    instrument = packet['instrumentation']
    require(set(instrument) == {'status', 'opcode_counts', 'forward_witnesses', 'reverse_witnesses'},
            'Instrument fields differ')
    require(instrument['status'] == 'COMPLETE_OPCODE_WITNESSES_AND_ORDER_INVARIANCE_GREEN', 'Invalid instrument')
    counts = {}
    for cid in IDS:
        fn = module.CANDIDATES[cid]['fn']
        instructions = list(dis.get_instructions(fn, adaptive=False, show_caches=False))
        require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel for i in instructions),
                'Registered candidate is not straight-line')
        offsets = [i.offset for i in instructions if i.opname != 'RESUME']
        counts[cid] = 8 * len(offsets)
        witness = {'count': counts[cid], 'calls': [
            {'opcode_offsets': offsets, 'output': y, 'returned': True} for y in EXPECTED]}
        for order in ('forward_witnesses', 'reverse_witnesses'):
            require(set(instrument[order]) == set(IDS), 'Incomplete trace universe')
            same(instrument[order][cid], witness, 'Incomplete or altered trace: ' + cid)
    same(packet['opcode_counts'], counts, 'Packet opcode counts differ')
    same(instrument['opcode_counts'], counts, 'Instrument opcode counts differ')

    require(set(packet['measurements']) == set(IDS), 'Incomplete timing register')
    boxes = {}
    for cid in IDS:
        rows = packet['measurements'][cid]
        require(type(rows) is list and len(rows) == 32, 'Missing or extra timing blocks')
        for block_index, row in enumerate(rows):
            order = list(IDS) if (block_index // 4) % 2 == 0 else list(reversed(IDS))
            offset = block_index % 4
            order = order[offset:] + order[:offset]
            require(set(row) == {'block_index', 'order_index', 'candidate_id', 'checksum',
                                 'wall_block_ns', 'process_block_ns'}, 'Timing row fields differ')
            same([row['block_index'], row['order_index'], row['candidate_id'], row['checksum']],
                 [block_index, order.index(cid), cid, 80000], 'Schedule/checksum mismatch')
            for key in KEYS[1:]:
                require(type(row[key]) is int and row[key] > 0, 'Invalid measured duration')
        boxes[cid] = {KEYS[0]: [counts[cid], counts[cid]], **{
            k: [min(row[k] for row in rows), max(row[k] for row in rows)] for k in KEYS[1:]}}
    same(packet['resource_boxes'], boxes, 'Observed resource envelopes differ')
    dominates = lambda a, b: (all(a[k][1] <= b[k][0] for k in KEYS)
                              and any(a[k][1] < b[k][0] for k in KEYS))
    parents = {cid: [other for other in IDS if other != cid and dominates(boxes[other], boxes[cid])]
               for cid in IDS}
    frontier = [cid for cid in IDS if not parents[cid]]
    families = sorted({FAMILIES[cid] for cid in frontier})
    terminal = {('NEURAL',): 'DERIVED_NEURAL_AT_REGISTERED_SCOPE',
                ('NON_NEURAL',): 'DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE'}.get(
                    tuple(families), 'UNDECIDED_FROM_CURRENT_EVIDENCE')
    same(packet['dominated_by'], parents, 'Domination graph differs')
    same(packet['frontier_candidate_ids'], frontier, 'Frontier differs')
    same(packet['frontier_families'], families, 'Family support differs')
    same(packet['terminal'], terminal, 'Terminal differs')
    same(packet['winner_candidate_id'], frontier[0] if len(frontier) == 1 else 'NONE', 'False unique winner')
    same(packet['expansion_expectation_passed'], terminal == 'DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE',
         'Expectation result differs')
    return {'status': 'STATIC_HOSTED_V4_PACKET_AUDIT_PASS', 'source_commit': COMMIT,
            'run_id': RUN, 'candidate_count': 4, 'capability_cases': 32, 'complete_traces': 64,
            'timed_blocks': 128, 'timed_candidate_calls': 20480000, 'opcode_counts': counts,
            'resource_boxes': boxes, 'frontier_candidate_ids': frontier, 'frontier_families': families,
            'terminal': terminal, 'timing_rerun': False, 'independent_scientific_replication': False}


def audit():
    raw = (HERE / PACKET).read_bytes()
    return validate(strict_json(raw.decode()), strict_json((HERE / PROVENANCE).read_text()), raw)


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
