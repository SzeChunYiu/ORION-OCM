from __future__ import annotations

import json
import unittest
from pathlib import Path

from physical_resource_metering_v1 import (
    PHYSICAL_IDS,
    ScopeRegistration,
    load_contract,
    run_metered,
    sibling_ledger_gaps,
    validate_contract,
)


HERE = Path(__file__).resolve().parent


class PhysicalMeteringTests(unittest.TestCase):
    def test_contract_matches_ids_and_sibling_gaps(self):
        contract = load_contract()
        self.assertEqual(tuple(r["id"] for r in contract["physical_coordinates"]), PHYSICAL_IDS)
        gaps = sibling_ledger_gaps()
        self.assertEqual(gaps["physical_metering"], "OPEN")
        self.assertEqual(gaps["energy_metering"], "OPEN")
        validated = validate_contract()
        self.assertEqual(validated["coordinates"], 7)

    def test_scope_must_be_registered_before_outcomes(self):
        with self.assertRaises(ValueError):
            ScopeRegistration("x", "y", False).freeze()

    def test_metering_receipt_is_honest_about_missing_energy_and_zeros(self):
        scope = ScopeRegistration(
            "unit-test-scope",
            "physical metering unit test",
            registered_before_outcomes=True,
        )
        receipt = run_metered(scope)
        by_id = {s.coordinate: s for s in receipt.statuses}
        self.assertEqual(by_id["wall_s"].status, "AVAILABLE")
        self.assertEqual(by_id["cpu_user_s"].status, "AVAILABLE")
        self.assertGreater(by_id["wall_s"].value or 0.0, 0.0)
        # Energy must not be forged on hosts without RAPL.
        if by_id["energy_j"].status == "AVAILABLE":
            self.assertEqual(by_id["energy_j"].source, "intel-rapl:energy_uj")
        else:
            self.assertEqual(by_id["energy_j"].status, "OPEN")
            self.assertIsNone(by_id["energy_j"].value)
        # UNAVAILABLE IO/GPU must not appear as numeric zero.
        for coord in ("io_read_bytes", "io_write_bytes", "gpu_time_s"):
            status = by_id[coord]
            if status.status in {"UNAVAILABLE", "UNCALIBRATED", "OPEN"}:
                self.assertIsNone(status.value)
        self.assertTrue(receipt.claim_ceiling.startswith("PHYSICAL_COUNTERS_CLOSED_AT_SCOPE"))
        self.assertEqual(receipt.sibling_ledger_physical, "OPEN")

    def test_sibling_ledger_file_not_rewritten(self):
        ledger = HERE.parent / "gmi-resource-lifecycle-ledger-v1" / "RESOURCE_LIFECYCLE_LEDGER_V1.json"
        payload = json.loads(ledger.read_text(encoding="utf-8"))
        self.assertEqual(payload["physical_metering"]["status"], "OPEN")
        self.assertEqual(payload["energy_metering"]["status"], "OPEN")
        self.assertEqual(len(payload["coordinates"]), 14)


if __name__ == "__main__":
    unittest.main()
