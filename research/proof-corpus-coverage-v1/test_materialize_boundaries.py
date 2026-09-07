"""Falsifying controls for post-launch selector failure and final custody deadline."""
import json
import os
from pathlib import Path
import signal
import time
import types
import pytest
from test_materialize_git import fixture, subject


@pytest.mark.parametrize('failure', ['initialize', 'register'])
def test_failed_selector_setup_reaps_real_git_and_closes_streams(tmp_path, monkeypatch, failure):
    subject()
    import materialize_objects as o
    repo, _, _, _ = fixture(tmp_path)
    records = tmp_path / 'records'; records.mkdir()
    g = o.Git(repo, records, time.monotonic() + 20, [])
    real_start = g.start; started = []; selectors = []
    def start(*args, **kwargs):
        value = real_start(*args, **kwargs); started.append(value); return value
    monkeypatch.setattr(g, 'start', start)
    actual_selector = o.selectors.DefaultSelector
    def selected():
        if failure == 'initialize': raise OSError('authored selector initialization')
        selector = actual_selector(); selectors.append(selector)
        def fail_register(*args, **kwargs): raise OSError('authored selector registration')
        monkeypatch.setattr(selector, 'register', fail_register)
        return selector
    monkeypatch.setattr(o.selectors, 'DefaultSelector', selected)
    try:
        with pytest.raises(OSError, match='authored selector'):
            with o.Objects(g): pytest.fail('selector failure must prevent entry')
        assert len(started) == 1
        p, command, streams, _ = started[0]
        observed = {'returncode': p.poll(), 'stdin_closed': p.stdin.closed,
                    'stdout_closed': p.stdout.closed, 'spools_closed': all(s.closed for s in streams),
                    'result_exists': (Path(command['record']) / 'RESULT.json').is_file()}
        (records / 'OBSERVED-BEFORE-TEST-CLEANUP.json').write_text(json.dumps(observed) + '\n')
        assert observed['returncode'] is not None, 'failed __enter__ left the actual Git child running'
        assert all(observed[k] is True for k in ['stdin_closed', 'stdout_closed', 'spools_closed', 'result_exists'])
        saved = json.loads((Path(command['record']) / 'RESULT.json').read_bytes())
        assert saved['reaped'] is True and saved['group_absent'] is True
        assert 'authored selector' in saved['error']
        assert saved['stdout_complete'] is True
        assert all(selector.get_map() is None for selector in selectors)
    finally:
        # Safe teardown also runs against the defective predecessor; never leak its child.
        for p, _, streams, _ in started:
            if not p.stdin.closed: p.stdin.close()
            try: p.wait(timeout=2)
            except Exception:
                os.killpg(p.pid, signal.SIGKILL); p.wait(timeout=2)
            p.stdout.close()
            for stream in streams: stream.close()
        for selector in selectors: selector.close()


@pytest.mark.parametrize('expire', [False, True])
def test_final_metadata_hash_cannot_report_success_past_deadline(tmp_path, monkeypatch, expire):
    m = subject()
    import materialize_objects as o
    repo, commit, tree, _ = fixture(tmp_path)
    expected = m.file_map(repo); deadline = time.monotonic() + 20
    actual = m.file_map; final_hashes = []
    def hashed(root, *args, **kwargs):
        value = actual(root, *args, **kwargs)
        if Path(root).name == '.git' and Path(root).parent.name == 'workspace':
            final_hashes.append(value)
            if expire: monkeypatch.setattr(o, 'time', types.SimpleNamespace(monotonic=lambda: deadline + 1))
        return value
    monkeypatch.setattr(m, 'file_map', hashed)
    result = m.materialize(repo, commit, tree, expected, tmp_path / 'out',
                           deadline_monotonic=deadline, acquisition_reference={'scope': 'AUTHORED'})
    assert len(final_hashes) == 1, 'control must reach final metadata hashing'
    if expire:
        assert result['terminal'] == 'MATERIALIZE_REFUSED'
        assert result['error'] == 'TimeoutError:MATERIALIZE_DEADLINE'
    else: assert result['terminal'] == 'MATERIALIZED', result
