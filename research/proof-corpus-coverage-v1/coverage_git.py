"""Revalidate current Git metadata using the qualified corpus reader; never read proofs."""
from pathlib import Path
import subprocess
from corpus_git import Snapshot
from env_inputs import canonical, digest, verify_file, write_bytes
from coverage_population import require


def verify_git(source, bare, evidence):
    bare = Path(bare).absolute()
    require(bare.resolve(strict=True) == bare and bare.is_dir(), 'canonical Git store')
    files = source['files']; evidence = Path(evidence).absolute()
    require(evidence.resolve(strict=True) == evidence and evidence.is_dir(), 'canonical evidence directory')
    outputs = [evidence / ('git-objects.' + kind) for kind in ('stdin', 'stdout', 'stderr')]
    process_path = evidence / 'git-process.json'
    require(all(not p.exists() and not p.is_symlink() for p in [*outputs, process_path]), 'Git evidence already exists')
    artifacts = {}
    def persist(path, raw):
        record = {'path': str(path), 'sha256': digest(raw), 'bytes': len(raw)}
        write_bytes(path, raw); verify_file(record)
        artifacts[path.name] = record
    with Snapshot(bare, source['commit']) as snapshot:
        require(snapshot.tree == source['tree'], 'Git tree differs')
        require(snapshot.tree_objects == source['verified_tree_objects'], 'Git tree payloads differ')
        require(len(snapshot.entries) == len(files) and {x['path'] for x in snapshot.entries} == set(files), 'Git file membership')
        for entry in snapshot.entries:
            require(all(entry[k] == files[entry['path']][k] for k in ('path', 'mode', 'oid')), 'Git entry differs')
        sizes = {}
        for row in files.values():
            require(row['oid'] not in sizes or sizes[row['oid']] == row['bytes'], 'shared blob size differs')
            sizes[row['oid']] = row['bytes']
        ids = sorted(sizes); request = ''.join(oid + '\n' for oid in ids).encode('ascii')
        argv = snapshot._command('cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)')
        persist(outputs[0], request)
        try:
            result = subprocess.run(argv, input=request, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=snapshot.env, timeout=60, check=False)
        except BaseException as exc:
            partial = [getattr(exc, 'stdout', None), getattr(exc, 'stderr', None)]
            available = [type(raw) is bytes for raw in partial]
            for path, raw, present in zip(outputs[1:], partial, available):
                persist(path, raw if present else b'')
            persist(process_path, canonical({'argv': argv, 'error': type(exc).__name__, 'evidence_complete': False,
                       'stdout_available': available[0], 'stderr_available': available[1], 'returncode': None}))
            raise
        persist(outputs[1], result.stdout); persist(outputs[2], result.stderr)
        persist(process_path, canonical({'argv': argv, 'error': None, 'returncode': result.returncode,
                                 'evidence_complete': True, 'stdout_available': True, 'stderr_available': True}))
        require(result.returncode == 0 and result.stderr == b'', 'Git batch process')
        lines = result.stdout.decode('ascii').splitlines()
        require(len(lines) == len(ids), 'Git object count')
        for oid, line in zip(ids, lines):
            require(line == oid + ' blob ' + str(sizes[oid]), 'Git blob identity/size')
        metrics = dict(snapshot.metrics)
        metrics['git_commands'] += 1; metrics['metadata_bytes_read'] += len(result.stdout)
        return {'scope': 'Current Git metadata and historically authorized blob hashes; proof bytes not reopened.',
                'commit': source['commit'], 'tree': snapshot.tree, 'files': len(files), 'unique_blobs': len(ids),
                'tree_objects': snapshot.tree_objects, 'metrics': metrics, 'argv': argv,
                'returncode': result.returncode, 'metadata_stdout_sha256': digest(result.stdout), 'artifacts': artifacts}
