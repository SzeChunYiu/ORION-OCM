"""Frozen-boundary drift controls, using manual donors only."""
import json
from pathlib import Path

import pytest
from test_later_consumption_protocol import prepared, fake_capture, PRIMITIVE


def test_post_dispatch_drift_has_one_row_and_never_reaches_semantic_check(tmp_path, monkeypatch):
    C, A, manifest = prepared(tmp_path)
    events = []
    monkeypatch.setattr(C, 'capture_one', fake_capture(PRIMITIVE, events))
    original_verify = C.verify
    verifies = 0
    def drift_after_capture(value):
        nonlocal verifies
        verifies += 1
        if verifies == 3:
            raise ValueError('simulated post-dispatch source drift')
        return original_verify(value)
    monkeypatch.setattr(C, 'verify', drift_after_capture)
    raw = C.run(manifest)
    assert [row['route'] for row in raw['rows']] == ['C','E0','B']
    assert len(events) == 1
    first = raw['rows'][0]
    assert first['capture']['exit_code'] == 0
    assert first['boundary_failure']['phase'] == 'post_dispatch'
    assert 'post-dispatch source drift' in first['boundary_failure']['reason']
    assert all(row['status'] == 'NOT_RUN_FROZEN_BOUNDARY_FAILURE' for row in raw['rows'][1:])
    monkeypatch.setattr(A, 'native_verify', lambda *a: pytest.fail('failed boundary reached semantic check'))
    got = A.run(manifest)
    assert got['reached_obligations'] == []
    assert len(got['rows']) == 3
    assert all(row['status'] == 'CANNOT_CHECK' for row in got['rows'])
    assert got['consumption'] == 'CANNOT_CHECK_CONSUMPTION'


@pytest.mark.parametrize('indices', [(0,0,1,2), (0,2), (1,0,2)])
def test_invalid_sealed_assignment_sequence_refuses_before_assessment(tmp_path,monkeypatch,indices):
    C, A, manifest = prepared(tmp_path)
    monkeypatch.setattr(C,'capture_one',fake_capture(PRIMITIVE,[]))
    C.run(manifest)
    output = Path(json.loads(manifest.read_text())['output'])
    raw = output/'candidates'
    path = raw/'receipt.json'
    receipt = json.loads(path.read_text())
    receipt['rows'] = [receipt['rows'][i] for i in indices]
    path.write_text(json.dumps(receipt))
    (raw/'seal.json').unlink()
    C.seal(raw)  # Deliberately well-sealed hostile structure, not a source/custody claim.
    monkeypatch.setattr(A,'native_verify',lambda *a:pytest.fail('invalid assignments reached semantic checks'))
    with pytest.raises(ValueError,match='assignment'):
        A.run(manifest)
    assert not (output/'assessment').exists()
