import os,pytest
pytestmark=pytest.mark.skipif(os.environ.get("OCM_RESOURCE_HOST_QUALIFICATION")!="1",reason="explicit scoped laptop controller qualification required")
import importlib.util, os, uuid
from test_resource_contract import limits

def subject():
    assert importlib.util.find_spec("resource_cgroup") is not None, "scoped cgroup controller missing"
    return __import__("resource_cgroup")

def test_owned_v1_controller_has_exact_readback_and_no_tasks():
    m=subject();c=m.Controller.create("test-"+uuid.uuid4().hex,limits())
    try:
        r=c.snapshot()
        assert r["memory.limit_in_bytes"]==64*1024**2
        assert r["memory.memsw.limit_in_bytes"]==64*1024**2
        assert r["cpu.cfs_quota_us"]==25000
        assert r["pids.max"]==16
        assert r["members"]==[]
        assert c.root_owned_limits()
    finally:c.remove()

def test_unsafe_group_name_is_rejected_before_sudo():
    import pytest
    with pytest.raises(ValueError):subject().Controller.create("../user.slice",limits())
