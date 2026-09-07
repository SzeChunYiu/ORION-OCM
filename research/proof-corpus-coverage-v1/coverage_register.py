"""Freeze complete metadata and four identity-only assignments before any dispatch."""
from pathlib import Path
import resource
import time
from env_inputs import (canonical, digest, file_record, inventory, parse_json, regular, snapshot,
                        verify_file, verify_inventory, write_bytes)
from coverage_population import ordered_population, require, validate_population
from coverage_git import verify_git
import coverage_policy as policy


def _bound(path):
    return {'path': str(regular(path)), **file_record(path)}


def freeze_inputs(directory, out):
    directory = Path(directory).absolute()
    require(directory.resolve(strict=True) == directory and directory.is_dir(), 'canonical inventory directory')
    destination = out / 'inputs'; destination.mkdir()
    original, copied = {}, {}
    for name, (sha, size) in policy.INPUTS.items():
        record = {'path': str(directory / name), 'sha256': sha, 'bytes': size}
        original[name] = record
        copied[name] = snapshot(record, destination / name)
    values = [parse_json(Path(copied[name]['path']).read_bytes())
              for name in ('CORPUS_SOURCE.json', 'GRAPH.json', 'SOLUTIONS.json')]
    # WRAPPERS is bound byte-for-byte but neither parsed nor used for assignment.
    return original, copied, values


def freeze_sources(package, sources, out):
    destination = out / 'sources'; destination.mkdir()
    frozen = {}
    for name, record in sorted(sources.items()):
        require(name.replace('_', '').isalnum(), 'source label')
        frozen[name] = snapshot(record, destination / (name + '.py'))
    documents = {}
    for name, sha in policy.DOCUMENTS.items():
        record = _bound(package / name)
        require(record['sha256'] == sha, 'prospective document differs: ' + name)
        documents[name] = record
        frozen['document_' + name] = snapshot(record, destination / name)
    return frozen, documents


def _usage():
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'self_user_seconds': own.ru_utime, 'self_system_seconds': own.ru_stime,
            'children_user_seconds': child.ru_utime, 'children_system_seconds': child.ru_stime,
            'self_peak_rss_kib': own.ru_maxrss, 'children_peak_rss_kib_nonaggregate': child.ru_maxrss}


def register(directory, bare, out, package, sources, interpreter, started_record):
    """Output root is created by the launcher; no workload is ever dispatched here."""
    out = Path(out); package = Path(package); started = time.monotonic(); before = _usage()
    require(out.is_absolute() and out.resolve(strict=True) == out, 'canonical registration output')
    require(set(p.name for p in out.iterdir()) == {'STARTED.json'}, 'registration output must be fresh')
    require(started_record['path'] == str(out / 'STARTED.json'), 'launcher start record path')
    verify_file(started_record)
    expected = {'STARTED.json': started_record}
    def persist(name, value):
        raw = canonical(value)
        record = {'path': str(out / name), 'sha256': digest(raw), 'bytes': len(raw)}
        write_bytes(out / name, raw); verify_file(record); expected[name] = record
    require(interpreter['sha256'] == policy.PYTHON_SHA256, 'qualified Python identity')
    verify_file(interpreter)
    frozen, documents = freeze_sources(package, sources, out)
    original, copied, (source, graph, solutions) = freeze_inputs(directory, out)
    require(source['commit'] == policy.COMMIT and source['tree'] == policy.TREE, 'prospective source identity')
    require(len(source['files']) == policy.FILES and graph['edge_count'] == policy.EDGES, 'prospective denominator')
    population = validate_population(source, graph, solutions, policy.PAIRS)
    git_dir = out / 'git'; git_dir.mkdir()
    git_evidence = verify_git(source, bare, git_dir)
    require(git_evidence['unique_blobs'] == policy.FILES, 'prospective unique blobs')
    persist('GIT.json', git_evidence)
    persist('POLICY.json', policy.POLICY)
    for record in [*sources.values(), *documents.values(), *original.values(), *copied.values(),
                   *frozen.values(), *git_evidence['artifacts'].values(), *expected.values(), interpreter]: verify_file(record)
    ordered = ordered_population(population, source['commit'])
    persist('POPULATION.json', {'schema': 'ocm.f1.population.v1', 'rows': ordered,
                                        'count': len(ordered), 'commit': source['commit'], 'tree': source['tree']})
    rows = []
    for rank, row in enumerate(ordered[:policy.ASSIGNED]):
        rows.append(dict(row, assignment_rank=rank, state='ASSIGNED_NO_DISPATCH', stages=[
            {'stage': stage, 'state': 'NOT_DISPATCHED', 'cause': 'REGISTRATION_ONLY', 'measured_cost': None}
            for stage in policy.STAGES]))
    require(len(rows) == policy.ASSIGNED, 'four assignments required')
    persist('ASSIGNMENTS.json', {'schema': 'ocm.f1.assignments.v1', 'rows': rows,
                                         'denominator': policy.ASSIGNED, 'continuation_cursor': policy.ASSIGNED,
                                         'population': expected['POPULATION.json']})
    persist('SOURCE-FREEZE.json', {'schema': 'ocm.f1.registration-source.v1',
               'loaded_sources': sources, 'snapshots': frozen, 'documents': documents,
               'inputs': original, 'input_snapshots': copied, 'interpreter': interpreter})
    for record in [*sources.values(), *documents.values(), *original.values(), *copied.values(),
                   *frozen.values(), *git_evidence['artifacts'].values(), *expected.values(), interpreter]: verify_file(record)
    after = _usage()
    persist('REGISTRATION.json', {'schema': 'ocm.f1.registration.v1', 'state': 'PROVISIONAL_UNTIL_SEAL',
               'assignment_count': len(rows), 'population_count': len(ordered), 'continuation_cursor': policy.ASSIGNED,
               'semantic_checks_reached': 0, 'git_proof_blob_bodies_read': 0, 'wrapper_source_parsed': False,
               'input_bytes_snapshotted_including_wrapper_source': sum(r['bytes'] for r in copied.values()),
               'input_scope': 'Historical lexical metadata; WRAPPERS bytes bound without source parsing.',
               'registration_wall_seconds_before_seal': time.monotonic() - started,
               'cpu_seconds': {key: after[key] - before[key] for key in after if key.endswith('_seconds')},
               'rss': {key: after[key] for key in after if not key.endswith('_seconds')},
               'nested_costs_not_additive': True, 'claim': policy.POLICY['claim']})
    files = inventory(out)
    artifact_records = [*copied.values(), *frozen.values(), *git_evidence['artifacts'].values(), *expected.values()]
    require(set(files) == {Path(r['path']).relative_to(out).as_posix() for r in artifact_records}, 'unexpected registration artifact')
    for record in artifact_records:
        name = Path(record['path']).relative_to(out).as_posix()
        require(files[name] == {k: record[k] for k in ('sha256', 'bytes')}, 'artifact differs before seal: ' + name)
    verify_inventory(out, files)
    persist('SEAL.json', {'schema': 'ocm.f1.registration-seal.v1', 'state': 'REGISTERED_NO_DISPATCH',
               'files': files, 'scope': 'Exact pre-seal directory bytes. Seal excludes itself and external launch receipt.'})
    return expected['SEAL.json']
