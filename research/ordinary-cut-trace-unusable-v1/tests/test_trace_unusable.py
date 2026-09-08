"""Confirm the 57 TRACE_UNUSABLE roots are complete and outside the declared interface."""
import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(PACKAGE)]

import load_frozen as frozen  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FrozenCustody(unittest.TestCase):
    def test_frozen_archives_are_not_rewritten_by_this_package(self):
        self.assertTrue(frozen.NATIVE_RAW.is_file())
        self.assertTrue(frozen.OPP_RAW.is_file())
        self.assertEqual(frozen.sha256(frozen.NATIVE_RAW.read_bytes()), frozen.NATIVE_RAW_SHA256)
        self.assertEqual(frozen.sha256(frozen.OPP_RAW.read_bytes()), frozen.OPP_RAW_SHA256)


class PopulationAndHistogram(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custodian = frozen.load_custodian()
        cls.packet = frozen.load_packet()
        cls.p1 = {row["label"]: row for row in frozen.load_p1()["contracts"]}
        cls.opportunity = frozen.load_opportunity_result()

    def test_exact_57_match_packet_authority_and_opportunity(self):
        packet_unusable = {row["label"] for row in self.packet["roots"]
                           if row["trace_disposition"] == "TRACE_UNUSABLE"}
        opp_unusable = {row["label"] for row in self.opportunity["roots"]
                        if row.get("status") == "TRACE_UNUSABLE"}
        self.assertEqual(len(self.custodian), 57)
        self.assertEqual(packet_unusable, set(self.custodian))
        self.assertEqual(opp_unusable, set(self.custodian))
        self.assertTrue(all(row["trace"] is None and row["contracts"] == {}
                            for row in self.packet["roots"]
                            if row["trace_disposition"] == "TRACE_UNUSABLE"))

    def test_subtype_histogram_is_53_3_1(self):
        reasons = Counter(row["reason"] for row in self.custodian.values())
        self.assertEqual(dict(reasons), {
            "OUTSIDE_NO_DV_INTERFACE": 53,
            "OUTSIDE_USED_CONTRACT_NO_DV_INTERFACE": 3,
            "OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE": 1,
        })
        self.assertEqual(sorted(lab for lab, row in self.custodian.items()
                                if row["reason"] == "OUTSIDE_USED_CONTRACT_NO_DV_INTERFACE"),
                         ["dfnul4", "eq0f", "notab"])
        self.assertEqual([lab for lab, row in self.custodian.items()
                          if row["reason"] == "OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE"],
                         ["vn0ALT"])

    def test_independent_reclassification_matches_export_reasons(self):
        for label, row in self.custodian.items():
            self.assertEqual(frozen.independent_reason(row["trace"], self.p1), row["reason"], label)

    def test_predecessor_transport_reproduces_the_same_reasons(self):
        transport = _load("trace_transport", frozen.TRANSPORT)

        class Contracts:
            @staticmethod
            def contract(row):
                return {k: row[k] for k in ("label", "kind", "statement", "floating", "essential", "dv")}

        rows = {}
        for row in self.p1.values():
            rows[row["label"]] = {**row, "span": [0, 1]}
        for entry in self.custodian.values():
            source = entry["trace"]["source"]
            for node in entry["trace"]["nodes"]:
                if node.get("kind") not in ("floating_hypothesis", "essential_hypothesis"):
                    continue
                label = node["label"]
                rows.setdefault(label, {
                    "label": label,
                    "kind": "$f" if node["kind"] == "floating_hypothesis" else "$e",
                    "statement": node["output"],
                    "span": [0, 1],
                    "floating": [], "essential": [], "dv": [],
                })
            self.assertGreater(source["span"][0], 0, source["label"])
        for label, entry in self.custodian.items():
            _trace, _contracts, reason = transport.prepare(entry["trace"], rows, Contracts)
            self.assertEqual(reason, entry["reason"], label)


class CompletenessNotAdapterDefect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custodian = frozen.load_custodian()
        cls.p1 = {row["label"]: row for row in frozen.load_p1()["contracts"]}

    def test_all_57_are_complete_native_dags(self):
        for label, row in self.custodian.items():
            trace = row["trace"]
            self.assertEqual(trace["terminal"], "NATIVE_VERIFIED", label)
            self.assertEqual(trace["label"], label)
            self.assertTrue(frozen.graph_ok(trace), label)
            self.assertTrue(trace["events"])

    def test_not_a_missing_node_or_native_format_failure(self):
        node_counts = [len(row["trace"]["nodes"]) for row in self.custodian.values()]
        self.assertEqual(min(node_counts), 6)
        self.assertEqual(max(node_counts), 174)
        self.assertFalse(any(reason == "OUTSIDE_NODE_INTERFACE" or reason == "OBSERVER_DID_NOT_PRODUCE_TRACE"
                             for reason in (row["reason"] for row in self.custodian.values())))

    def test_used_assertion_dv_cases_are_vacuous_but_still_outside_no_dv(self):
        for label in ("dfnul4", "eq0f", "notab"):
            trace = self.custodian[label]["trace"]
            self.assertEqual(trace["source"]["dv"], [])
            self.assertEqual(trace["source"]["active_dv"], [])
            pairs = sum(frozen.required_active_pairs(node) for node in trace["nodes"])
            self.assertEqual(pairs, 0, label)
            used = {node["label"] for node in trace["nodes"] if "label" in node}
            self.assertTrue(any(self.p1[lab]["dv"] for lab in used if lab in self.p1), label)

    def test_vn0ALT_uses_an_extra_setvar_float_and_has_no_mandatory_hyps(self):
        trace = self.custodian["vn0ALT"]["trace"]
        self.assertEqual(trace["source"]["floating"], [])
        self.assertEqual(trace["source"]["essential"], [])
        self.assertEqual(frozen.extra_hypotheses(trace), ["vx", "vx"])
        self.assertEqual(len(trace["nodes"]), 6)

    def test_none_of_the_57_satisfy_ordinary_trace_ready_prerequisites(self):
        revived = []
        for label, row in self.custodian.items():
            blockers = frozen.ordinary_ready_blockers(row["trace"], self.p1)
            self.assertTrue(blockers, label)
            if not blockers:
                revived.append(label)
        self.assertEqual(revived, [])

    def test_sslin_is_the_closest_non_revival_not_a_wff_guard_bug(self):
        """3 homogeneous class floats, empty source $d, unused inherited active $d.

        The declared first boundary still refuses any active_dv. That is not the
        class-packet wff-parser defect: the rest of the ordinary stack also
        requires empty active_dv.
        """
        closest = []
        for label, row in self.custodian.items():
            blockers = set(frozen.ordinary_ready_blockers(row["trace"], self.p1))
            if blockers == {"source_or_active_dv"}:
                closest.append(label)
        self.assertEqual(closest, ["sslin"])
        source = self.custodian["sslin"]["trace"]["source"]
        self.assertEqual(source["dv"], [])
        self.assertEqual(source["active_dv"], [["A", "x"], ["B", "x"], ["C", "x"]])
        self.assertEqual([h["statement"][0] for h in source["floating"]], ["class", "class", "class"])
        self.assertEqual(sum(frozen.required_active_pairs(n) for n in self.custodian["sslin"]["trace"]["nodes"]), 0)


class PredecessorStackStillRefuses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custodian = frozen.load_custodian()
        donor = frozen.CONSUMER / "donor"
        sys.path[:0] = [str(frozen.CONSUMER), str(donor)]
        cls.constructor = _load("typed_constructor", donor / "typed_constructor.py")
        cls.context = _load("typed_context", donor / "typed_context.py")

    def test_constructor_refuses_source_or_active_dv(self):
        trace = self.custodian["sslin"]["trace"]
        with self.assertRaises(ValueError) as ctx:
            self.constructor.construct(trace, {}, {}, [], max_tokens=4096)
        self.assertEqual(str(ctx.exception), "DV outside first boundary")

    def test_context_refuses_vn0ALT_and_used_dv_roots_as_not_three_floats(self):
        for label in ("vn0ALT", "dfnul4", "eq0f", "notab"):
            with self.assertRaises(ValueError) as ctx:
                self.context.from_source(self.custodian[label]["trace"]["source"])
            self.assertEqual(str(ctx.exception), "three mandatory floats", label)


if __name__ == "__main__":
    unittest.main()
