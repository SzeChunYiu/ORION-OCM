"""Real-record controls; no ecology runs and no mutation of saved artifacts."""
import copy
import gzip
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_mechanism_record import check

UNIT = Path(__file__).resolve().parent
RECORD = json.loads(gzip.decompress((UNIT / "evidence/RECEIPT_V1.json.gz").read_bytes()))
PRIOR = json.loads((UNIT.parent / "gmi-witness-recovery-v1/evidence/s1-recovery-20260913/INDEPENDENT_VERIFICATION_V1.json").read_text())


class RecordChecks(unittest.TestCase):
    def test_real_record(self):
        self.assertTrue(check(RECORD, PRIOR)["verified"])

    def rejected(self, mutate):
        record = copy.deepcopy(RECORD)
        mutate(record)
        with self.assertRaises(ValueError):
            check(record, PRIOR)

    def test_missing_context(self):
        self.rejected(lambda r: r["outcomes"]["zero_vector"].pop("control:standard"))

    def test_changed_zero_trace(self):
        self.rejected(lambda r: r["outcomes"]["zero_vector"]["control:standard"]["native_response"]["trace"][0].__setitem__(0, 99))

    def test_unreported_error(self):
        self.rejected(lambda r: r["outcomes"]["variable_key"]["probe:E_wit1"].__setitem__("error", "test failure"))

    def test_baseline_ledger_drift(self):
        self.rejected(lambda r: r["outcomes"]["original"]["control:standard"]["native_response"]["R"].__setitem__("exec", 0))

    def test_fake_varying_key(self):
        def mutate(r):
            for row in r["outcomes"]["variable_key"].values():
                for obs in row["passive_capture"]["insert_observations"]:
                    if obs["node"] == "insert1":
                        obs["key"] = [0]
        self.rejected(mutate)

    def test_intermediate_store_drift(self):
        self.rejected(lambda r: r["outcomes"]["zero_vector"]["control:standard"]["passive_capture"]["insert_observations"][0]["stores_after"].clear())

    def test_uncharged_call(self):
        self.rejected(lambda r: r.__setitem__("calls", 32))


if __name__ == "__main__":
    unittest.main()
