"""Authored durable-record/copy falsifiers; no registered stream."""
import importlib,time
import pytest
from assay_test_support import authored_only
from unary_contract import InputRefused

def api():return importlib.import_module("unary_assay_ledger")

def test_exact_copy_and_bound_record(tmp_path):
    m=api();source=tmp_path/"source";source.mkdir();(source/"nested").mkdir()
    (source/"nested/data").write_bytes(b"complete\\x00payload")
    source_before=m.inventory(source)
    copied=m.copy_store(source,tmp_path/"copy",deadline=time.monotonic()+10)
    assert copied["before"]==copied["after"]==copied["copied"]==source_before
    ledger=m.Ledger(tmp_path/"evidence",deadline=time.monotonic()+10)
    ref=ledger.append("EXPECTED",{"slot":"A/conventional"})
    assert m.read(tmp_path/"evidence",ref)["body"]=={"slot":"A/conventional"}
    assert len(m.replay(tmp_path/"evidence"))==1
    (tmp_path/"evidence"/ref["path"]).write_bytes(b"{}")
    with pytest.raises(InputRefused,match="RECORD_HASH"):m.read(tmp_path/"evidence",ref)

@pytest.mark.parametrize("kind",["symlink","hardlink"])
def test_copy_refuses_metadata_alias(tmp_path,kind):
    m=api();src=tmp_path/"source";src.mkdir();(src/"data").write_bytes(b"data")
    if kind=="symlink":(src/"alias").symlink_to("data")
    else:
        import os
        os.link(src/"data",src/"alias")
    with pytest.raises(InputRefused,match="STORE_ENTRY"):m.copy_store(src,tmp_path/"dest",deadline=time.monotonic()+10)
    assert not (tmp_path/"dest").exists()

def test_copy_refuses_overlap_expiry_and_existing_target(tmp_path):
    m=api();src=tmp_path/"source";src.mkdir();(src/"data").write_bytes(b"data")
    with pytest.raises(InputRefused,match="COPY_OVERLAP"):m.copy_store(src,src/"child",deadline=time.monotonic()+10)
    with pytest.raises(InputRefused,match="DEADLINE"):m.copy_store(src,tmp_path/"late",deadline=time.monotonic()-1)
    with pytest.raises(FileExistsError):m.copy_store(src,src,deadline=time.monotonic()+10)

def test_record_replay_refuses_extra_and_missing_entry(tmp_path):
    m=api();ledger=m.Ledger(tmp_path/"records",deadline=time.monotonic()+10)
    ledger.append("EXPECTED",{"slot":"B"});ledger.append("DONE",{"slot":"B"})
    (ledger.root/"junk").write_bytes(b"junk")
    with pytest.raises(InputRefused,match="LEDGER_MEMBERSHIP"):m.replay(ledger.root)
    (ledger.root/"junk").unlink();(ledger.root/"00000000.json").unlink()
    with pytest.raises(InputRefused,match="LEDGER_MEMBERSHIP"):m.replay(ledger.root)
