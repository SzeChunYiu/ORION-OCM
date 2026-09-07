"""Toy third-layer custody; no controller, source fixture or native execution."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import resource_exitcode_evidence as target
from test_resource_successor_fixture import binding,freeze,make_fixture,put_archive,raw,seal

class ExitcodeEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
        self.prior,self.old,self.current,self.oldpin=make_fixture(self.base)
        self.priorpin=seal(self.prior,"ocm.f1.resource-successor-seal.v1")
        self.root=self.base/"resource-exitcode-records";self.root.mkdir()
        history=self.root/"prior-source";history.mkdir()
        (history/"a.py").write_bytes((self.current/"a.py").read_bytes())
        changed=b"raise SystemExit('correction source must never execute')\n"
        (self.current/"a.py").write_bytes(changed);fr=freeze(changed)
        result=raw({"terminal":"AUTHORED_CONTROL_DATA"});host=raw({"path":"/never/open/host/input"})
        row=put_archive(self.root,{"SOURCE_FREEZE.json":fr,"source/a.py":changed})
        for name,data in {"SOURCE_FREEZE.json":fr,"RESULT.json":result,"HOST-INPUTS.json":host}.items():
            (self.root/name).write_bytes(data)
        index={"schema":"ocm.f1.resource-exitcode-index.v1","historical":{"seal_sha256":self.priorpin,
               "source_dir":"prior-source","source_count":1},"source_freeze":binding(fr),"result":binding(result),
               "archives":[row],"omissions":{"file":"HOST-INPUTS.json",**binding(host),"scope":"not revalidated"}}
        (self.root/"INDEX.json").write_bytes(raw(index));self.rebind()
    def rebind(self):self.pin=seal(self.root,"ocm.f1.resource-successor-seal.v1")
    def run_audit(self):
        return target.audit_exitcode(self.root,self.pin,self.current,self.prior,self.old,self.priorpin,self.oldpin)
    def edit_index(self,fn):
        p=self.root/"INDEX.json";value=json.loads(p.read_bytes());fn(value);p.write_bytes(raw(value));self.rebind()
    def test_three_distinct_source_layers_pass_without_dispatch(self):
        result=self.run_audit()
        self.assertEqual(result["terminal"],"RESOURCE_EXITCODE_CUSTODY_PASS")
        self.assertEqual((result["historical_sources"],result["prior_successor_sources"],result["current_sources"]),(1,1,1))
        self.assertEqual(result["correction_archive_members"],2)
        self.assertFalse(result["omitted_host_inputs_revalidated"])
    def test_current_source_drift_refuses(self):
        (self.current/"a.py").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"CURRENT_SUCCESSOR_SOURCE"):self.run_audit()
    def test_previous_source_drift_refuses(self):
        (self.root/"prior-source/a.py").write_bytes(b"changed");self.rebind()
        with self.assertRaisesRegex(ValueError,"CURRENT_SUCCESSOR_SOURCE"):self.run_audit()
    def test_original_source_history_still_authoritative(self):
        (self.prior/"historical-source/a.py").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"SUCCESSOR_FILE_HASH"):self.run_audit()
    def test_previous_seal_cannot_be_changed(self):
        self.edit_index(lambda j:j["historical"].update(seal_sha256="0"*64))
        with self.assertRaisesRegex(ValueError,"PRIOR_AUTHORITY"):self.run_audit()
    def test_extra_prior_snapshot_refuses(self):
        (self.root/"prior-source/extra.py").write_bytes(b"extra");self.rebind()
        with self.assertRaisesRegex(ValueError,"PRIOR_SOURCE_SET"):self.run_audit()
    def test_boolean_prior_count_refuses(self):
        self.edit_index(lambda j:j["historical"].update(source_count=True))
        with self.assertRaisesRegex(ValueError,"PRIOR_SOURCE_COUNT"):self.run_audit()
    def test_corrected_snapshot_must_match_current_freeze(self):
        row=put_archive(self.root,{"SOURCE_FREEZE.json":(self.root/"SOURCE_FREEZE.json").read_bytes(),"source/a.py":b"wrong"})
        self.edit_index(lambda j:j.update(archives=[row]))
        with self.assertRaisesRegex(ValueError,"SNAPSHOT_BINDING"):self.run_audit()
    def test_omitted_host_binding_refuses(self):
        self.edit_index(lambda j:j["omissions"].update(sha256="0"*64))
        with self.assertRaisesRegex(ValueError,"OMISSION_BINDING"):self.run_audit()
    def test_noncanonical_previous_source_path_refuses(self):
        self.edit_index(lambda j:j["historical"].update(source_dir="../outside"))
        with self.assertRaisesRegex(ValueError,"PATH"):self.run_audit()
    def test_unbound_guard_is_not_executed(self):
        with patch.object(target.Path,"read_bytes",return_value=b"unbound"):
            with patch.object(target,"compile",side_effect=AssertionError("must not execute"),create=True):
                with self.assertRaisesRegex(ValueError,"HELPER_IDENTITY"):target.helper()

if __name__=="__main__":unittest.main()
