"""Regression for the observed frozen-helper RESOURCE_SETUP refusal; no host dispatch."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import types
import pytest
from test_acquisition_phase import phase


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('drift', [False, True])
def test_frozen_helper_consumer_and_post_dispatch_byte_binding(phase, tmp_path, monkeypatch, drift):
    m, reg, lock, out, state = phase; calls = []
    protected = tmp_path / 'protected-helper'; protected.mkdir()
    for name in ('resource_setup.py', 'resource_contract.py'):
        shutil.copyfile(m.HERE / name, protected / name)
    original_stat = Path.stat
    def stat(path, *args, **kwargs):
        result = original_stat(path, *args, **kwargs)
        if path.parent == protected:
            fields = list(result); fields[4] = 0; return os.stat_result(fields)
        return result
    monkeypatch.setattr(Path, 'stat', stat)
    def probe(root):
        frozen = root / 'sources'
        contract = load(frozen / 'resource_contract.py', 'helper_contract_fixture')
        monkeypatch.setitem(sys.modules, 'resource_contract', contract)
        group = load(frozen / 'resource_cgroup.py', 'helper_group_fixture')
        group.HELPER = protected / 'resource_setup.py'
        def no_dispatch(argv, **kwargs):
            calls.append(argv)
            value = {'source_stamps': {name: group.record(protected / name)
                     for name in ('resource_setup.py', 'resource_contract.py')}, 'result': {'fixture': True}}
            return types.SimpleNamespace(returncode=0, stdout=json.dumps(value).encode(), stderr=b'')
        group.subprocess = types.SimpleNamespace(run=no_dispatch, PIPE=-1)
        assert group.helper('remove', 'fixture-probe')['fixture'] is True
        if drift:
            helper = frozen / 'resource_setup.py'; helper.write_bytes(helper.read_bytes() + b' ')
    state['mutation'] = probe
    result = m.run(reg, lock, out)
    assert len(calls) == 1, 'actual helper preflight must reach the mocked privileged boundary'
    assert calls[0][:4] == ['/usr/bin/sudo', '-n', '/usr/bin/python3', '-I']
    freeze = json.loads((out / 'SOURCE-FREEZE.json').read_bytes())
    bound = freeze['sources']['resource_setup']['frozen']
    if drift:
        assert result['terminal'] == 'CANNOT_CHECK'
        assert 'source drift after acquisition' in result['error']['message']
        assert m.contract.record(bound['path']) != bound
    else:
        assert result['terminal'] == 'MATERIAL_READY'
        assert m.contract.record(bound['path']) == bound
    assert result['semantic_checks_reached'] == 0
