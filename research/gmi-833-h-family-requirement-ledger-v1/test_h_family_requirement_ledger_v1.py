"""Tests for gmi-833-h-family-requirement-ledger-v1.

Run: python3 -I -O -B test_h_family_requirement_ledger_v1.py
Python 3.8 compatible, stdlib only, no floating point.
"""
from __future__ import print_function

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import family_evidence_map_v1 as kmap          # noqa: E402
import h_family_requirement_ledger_v1 as L     # noqa: E402
import route_a_rowfirst_v1 as route_a          # noqa: E402
import route_b_artifactfirst_v1 as route_b     # noqa: E402


class Fixture(object):
    built = None

    @classmethod
    def get(cls):
        if cls.built is None:
            a, b, km, absence, row_index, row_id_by_text = L.build_matrix()
            recon = L.reconcile(a, b)
            cells = L.merge(a, b, recon)
            cls.built = (a, b, km, absence, row_index, recon, cells)
        return cls.built


MODULES = ("h_family_requirement_ledger_v1.py", "route_a_rowfirst_v1.py",
           "route_b_artifactfirst_v1.py", "family_evidence_map_v1.py",
           "test_h_family_requirement_ledger_v1.py")


def executable_source(name):
    """Source with the module docstring and every comment line removed."""
    import ast as _ast
    with open(os.path.join(HERE, name)) as handle:
        body = handle.read()
    tree = _ast.parse(body)
    doc = _ast.get_docstring(tree)
    if doc:
        body = body.replace(doc, "", 1)
    kept = [line for line in body.splitlines() if not line.strip().startswith("#")]
    return "\n".join(kept)


class TestSourceDiscipline(unittest.TestCase):
    def test_no_float_constants_anywhere(self):
        import ast as _ast
        for name in MODULES:
            with open(os.path.join(HERE, name)) as handle:
                tree = _ast.parse(handle.read())
            for node in _ast.walk(tree):
                if isinstance(node, _ast.Constant) and isinstance(node.value, float):
                    self.fail("float constant in %s at line %d" % (name, node.lineno))

    def test_no_float_cast_and_no_rng_and_no_third_party(self):
        for name in MODULES:
            body = executable_source(name)
            self.assertNotIn("f" + "loat(", body, name)
            self.assertNotIn("import " + "random", body, name)
            self.assertNotIn("num" + "py", body, name)

    def test_routes_do_not_import_each_other(self):
        a_src = executable_source("route_a_rowfirst_v1.py")
        b_src = executable_source("route_b_artifactfirst_v1.py")
        self.assertNotIn("route_b", a_src)
        self.assertNotIn("route_a", b_src)
        # Route B must not read Route A's frozen rule table or the issue mirror.
        self.assertNotIn("ADJUDICATION_RULES", b_src)
        self.assertNotIn("SECTION_H_MIRROR", b_src)


class TestRows(unittest.TestCase):
    def test_exactly_43_open_and_2_closed_section_h_rows(self):
        open_rows, closed_rows = route_a.read_rows()
        self.assertEqual(len(open_rows), 43)
        self.assertEqual(len(closed_rows), 2)
        self.assertEqual(len(set(open_rows)), 43)

    def test_mirror_rows_match_the_frozen_census_registry_verbatim(self):
        open_rows, _ = route_a.read_rows()
        registry = route_b.read_json(os.path.join(
            L.RESEARCH, "gmi-833-h-obstruction-census-v1", "FROZEN_FAMILY_REGISTRY_V1.json"))
        self.assertEqual(open_rows, [f["row"] for f in registry["families"]])


class TestExtractorValidation(unittest.TestCase):
    """Validate the extractor on REAL data before any count is believed."""

    def test_hand_read_rows_reproduced_exactly(self):
        _, _, _, _, row_index, _, cells = Fixture.get()
        report = L.validate_extractor(cells, row_index)
        self.assertTrue(report["all_ok"], json.dumps(report, indent=1))

    def test_planted_positive_recall_is_total(self):
        _, _, _, _, row_index, _, cells = Fixture.get()
        report = L.validate_extractor(cells, row_index)
        self.assertEqual(report["planted_positive_recall"], report["planted_positive_total"])
        self.assertGreater(report["planted_positive_total"], 0)

    def test_no_alarm_case_is_clean(self):
        """Rows with no four-family evidence must produce no SIGMA_4F cell at all."""
        _, _, _, _, row_index, _, cells = Fixture.get()
        report = L.validate_extractor(cells, row_index)
        self.assertEqual(report["no_alarm_cases_clean"], report["no_alarm_total"])
        self.assertGreater(report["no_alarm_total"], 0)
        sigma_4f_rows = set(c["row"] for c in cells if c["sigma"] == "SIGMA_4F")
        self.assertEqual(len(sigma_4f_rows), 4)
        self.assertNotIn("Attention mechanisms.", sigma_4f_rows)
        self.assertNotIn("Feed-forward neural networks.", sigma_4f_rows)


class TestTwoRoutes(unittest.TestCase):
    def test_routes_agree_on_every_cell(self):
        _, _, _, _, _, recon, _ = Fixture.get()
        self.assertTrue(recon["agreement_is_total"], json.dumps(recon, indent=1)[:2000])
        self.assertEqual(recon["cells_route_a"], recon["cells_route_b"])

    def test_round_one_disagreement_is_preserved_on_disk(self):
        path = os.path.join(HERE, "ROUTE_RECONCILIATION_ROUND1_V1.json")
        self.assertTrue(os.path.exists(path))
        record = route_b.read_json(path)
        self.assertEqual(record["status"], "DISAGREEMENT_FOUND_AND_RECORDED_BEFORE_RESOLUTION")
        self.assertEqual(len(record["cells_only_route_a"]), 43)
        self.assertEqual(record["status_disagreements"], 0)


class TestScopeDiscipline(unittest.TestCase):
    def test_every_non_missing_cell_carries_a_scope(self):
        _, _, _, _, _, _, cells = Fixture.get()
        for cell in cells:
            self.assertIn(cell["sigma"], ("SIGMA_4F", "SIGMA_CENSUS", "SIGMA_K"))

    def test_every_met_at_narrower_scope_cell_carries_a_citation_and_a_gap(self):
        _, _, _, _, _, _, cells = Fixture.get()
        for cell in cells:
            if cell["status"] == "MET_AT_NARROWER_SCOPE":
                self.assertTrue(cell.get("citation"), cell)
                self.assertTrue(cell.get("scope_gap"), cell)

    def test_every_missing_buildable_cell_names_the_build(self):
        _, _, _, _, _, _, cells = Fixture.get()
        for cell in cells:
            if cell["status"] == "MISSING_BUILDABLE":
                self.assertTrue(cell.get("build"), cell)

    def test_no_row_is_complete_at_any_single_scope(self):
        _, _, _, _, _, _, cells = Fixture.get()
        rows, _ = route_a.read_rows()
        counts = L.per_sigma_counts(cells, rows)
        for row in rows:
            for sigma, mapping in counts[row].items():
                met = [r for r in L.REQUIREMENTS if mapping.get(r) in L.MET_STATUSES]
                self.assertLess(len(met), len(L.REQUIREMENTS), (row, sigma))


class TestNonPromotion(unittest.TestCase):
    def test_no_unqualified_met_cell_exists(self):
        _, _, _, _, _, _, cells = Fixture.get()
        self.assertEqual([c for c in cells if c["status"] == "MET"], [])

    def test_real_scale_is_never_structural_and_never_met(self):
        _, _, _, _, _, _, cells = Fixture.get()
        for cell in cells:
            if cell["requirement"] == "R11":
                self.assertNotIn(cell["status"], ("MET", "MET_AT_NARROWER_SCOPE", "MISSING_STRUCTURAL"), cell)

    def test_every_sigma_k_cell_is_screened(self):
        _, _, _, _, _, _, cells = Fixture.get()
        k_cells = [c for c in cells if c["sigma"] == "SIGMA_K"]
        self.assertGreater(len(k_cells), 0)
        for cell in k_cells:
            self.assertEqual(cell["status"], "SCREENED_NOT_ADJUDICATED")

    def test_screened_is_never_folded_into_missing(self):
        _, _, _, _, _, _, cells = Fixture.get()
        totals, _ = L.status_totals(cells)
        self.assertGreater(totals["SCREENED_NOT_ADJUDICATED"], 0)
        self.assertNotEqual(totals["SCREENED_NOT_ADJUDICATED"], 0)

    def test_section_h_is_not_reported_uniformly_impossible(self):
        _, _, _, _, _, _, cells = Fixture.get()
        totals, _ = L.status_totals(cells)
        self.assertEqual(totals["MISSING_STRUCTURAL"], 0)
        self.assertGreater(totals["MET_AT_NARROWER_SCOPE"], 0)


class TestKBinding(unittest.TestCase):
    def test_k_binding_absence_is_verified_two_ways_with_a_control(self):
        _, _, _, absence, _, _, _ = Fixture.get()
        self.assertTrue(absence["absence_established"])
        self.assertEqual(absence["way1_verbatim_row_text_hits"], [])
        self.assertEqual(absence["way2_section_h_mention_hits"], [])
        # the control proves the scan actually reads bytes: a grep that can never hit is
        # not an absence proof
        self.assertGreater(absence["control_pattern_hits"], 0)
        self.assertGreater(absence["files_scanned"], 50)

    def test_every_k_edge_is_labelled_agent_constructed(self):
        _, _, km, _, _, _, _ = Fixture.get()
        for edge in km["edges"]:
            self.assertEqual(edge["provenance"], "AGENT_CONSTRUCTED_UNADJUDICATED")

    def test_rows_without_any_k_family_are_reported(self):
        _, _, km, _, _, _, _ = Fixture.get()
        self.assertGreater(len(km["rows_without_any_k"]), 0)
        self.assertGreater(len(km["rows_with_multiple_k"]), 0)


class TestCensusContractMap(unittest.TestCase):
    def test_43_rows_resolve_to_only_10_distinct_contracts(self):
        registry = route_b.read_json(os.path.join(
            L.RESEARCH, "gmi-833-h-obstruction-census-v1", "FROZEN_FAMILY_REGISTRY_V1.json"))
        contracts = set(f["contract"] for f in registry["families"])
        self.assertEqual(len(registry["families"]), 43)
        self.assertEqual(len(contracts), 10)


class TestHostilesAndNull(unittest.TestCase):
    def test_all_hostiles_detected(self):
        _, _, km, _, _, _, cells = Fixture.get()
        rows, _ = route_a.read_rows()
        report = L.hostiles(rows, cells, km)
        self.assertTrue(report["all_detected"], json.dumps(report, indent=1)[:3000])
        self.assertEqual(report["count"], 8)

    def test_null_beats_zero_of_two_hundred(self):
        _, _, km, _, _, _, cells = Fixture.get()
        rows, _ = route_a.read_rows()
        report = L.null_controls(rows, cells, km)
        self.assertEqual(report["controls_accepted"], 0)
        self.assertTrue(report["true_ledger_accepted"])

    def test_true_ledger_is_accepted(self):
        _, _, km, _, _, _, cells = Fixture.get()
        rows, _ = route_a.read_rows()
        self.assertEqual(L.check(rows, cells, km), [])


class TestFrozenPredictions(unittest.TestCase):
    def test_result_reports_every_frozen_prediction(self):
        path = os.path.join(HERE, "RESULT_V1.json")
        if not os.path.exists(path):
            self.skipTest("RESULT_V1.json not generated yet")
        result = route_b.read_json(path)
        self.assertEqual(len(result["frozen_predictions"]), 5)
        for name, record in result["frozen_predictions"].items():
            self.assertIn("held", record, name)
            self.assertIn("observed", record, name)

    def test_no_reconciliation_artifact_is_emitted(self):
        names = [n for n in os.listdir(HERE) if n.startswith("ISSUE_833_RECONCILIATION")]
        self.assertEqual(names, [])


class TestCustody(unittest.TestCase):
    def test_freeze_exists_and_pins_source_main(self):
        with open(os.path.join(HERE, "FREEZE_V1.md")) as handle:
            body = handle.read()
        self.assertIn(L.SOURCE_MAIN, body)
        self.assertIn("No neighboring row is earned here.", body)
        self.assertIn("SECTION_H_UNIFORMLY_IMPOSSIBLE", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
