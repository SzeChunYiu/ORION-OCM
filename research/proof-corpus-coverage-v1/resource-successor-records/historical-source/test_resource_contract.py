from pathlib import Path
import importlib.util
import pytest

def subject():
    spec=importlib.util.find_spec("resource_contract")
    assert spec is not None, "aggregate resource contract not implemented"
    return __import__("resource_contract")

def limits(**changes):
    value=dict(memory_bytes=64*1024**2,memsw_bytes=64*1024**2,cpu_quota_us=25000,
               cpu_period_us=100000,pids=16,wall_s=3,term_grace_s=.2,reap_s=2,
               poll_s=.05,max_file_bytes=8*1024**2,min_available_bytes=0,
               min_free_bytes=0,stop_free_bytes=0,max_owned_bytes=16*1024**2)
    return {**value,**changes}

def test_exact_limits_validate_and_memsw_is_aggregate():
    assert subject().validate_limits(limits()) == limits()
    with pytest.raises(ValueError): subject().validate_limits(limits(memsw_bytes=1))
    with pytest.raises(ValueError): subject().validate_limits(limits(memory_bytes=21*1024**3,memsw_bytes=21*1024**3))

@pytest.mark.parametrize("key,value",[("pids",0),("cpu_quota_us",200001),("poll_s",0),
 ("wall_s",float("inf")),("max_file_bytes",9*1024**3),("pids",True)])
def test_invalid_or_unbounded_limits_refuse(key,value):
    with pytest.raises(ValueError):subject().validate_limits(limits(**{key:value}))

def test_missing_or_added_setting_refuses():
    c=subject()
    with pytest.raises(ValueError):c.validate_limits({**limits(),"extra":1})
    value=limits();value.pop("pids")
    with pytest.raises(ValueError):c.validate_limits(value)
