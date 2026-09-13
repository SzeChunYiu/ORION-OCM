import json
from pathlib import Path
from types import SimpleNamespace as N
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_instrument import TraceCapture, VerifierCapture
from recover_witness import run


class CaptureTests(unittest.TestCase):
    def test_explicit_opt_in_precedes_execution(self):
        self.assertEqual(run("absent", "absent", 3827)["search_launched"], False)

    def test_trace_preserves_objects_and_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"trace.jsonl"
            trace = TraceCapture(path)
            row = {"genotype": "{}", "origin": ["seed", 38]}
            trace.append(row)
            trace.close()
            self.assertIs(trace[0], row)
            self.assertEqual(json.loads(path.read_text()), row)
            self.assertGreaterEqual(trace.io_seconds, 0)
            with self.assertRaises(FileExistsError):
                TraceCapture(path)

    def test_capture_returns_original_verdict_and_counts_actual_calls(self):
        events = []
        def evaluate(*args):
            events.append(args)
            return {"capability": 1, "trace": [[1]]}
        eco = N(run_genotype=evaluate)
        morph = N(to_json=lambda g: json.dumps(g), fingerprint=lambda g: "fp")
        def prune(g, spec, basis):
            eco.run_genotype(spec, g, basis, "standard")
            return g, {"capabilities": {"standard": 1}, "evaluations_charged": 1}
        atrophy = N(prune_all_interventions=prune)
        last = []
        def verify(g, spec, bc):
            eco.run_genotype(spec, g, None, "standard")
            small, info = atrophy.prune_all_interventions(g, spec, None)
            v = {"pass": True, "carrier_atrophied": "DENSE", "min_over_six": 1,
                 "atrophied_min_over_six": 1, "atrophied_genotype": json.dumps(small)}
            last.append(v)
            return v, 2
        dev = N(ecology=eco, morph=morph, atrophy_ir=atrophy, verify_candidate=verify, THETA=.8, FX_UNIT=.1)
        with tempfile.TemporaryDirectory() as tmp:
            with VerifierCapture(dev, tmp) as capture:
                result, charged = dev.verify_candidate({"node": 1}, {"name": "test"}, .8)
                self.assertIs(result, last[-1])
                self.assertEqual((charged, capture.charged, capture.actual_calls), (2, 2, 2))
            self.assertIs(dev.verify_candidate, verify)
            self.assertIs(eco.run_genotype, evaluate)
            self.assertIs(atrophy.prune_all_interventions, prune)
            saved = json.loads((Path(tmp)/"witness.json").read_text())
            self.assertEqual(len(saved["evaluation_outputs"]), 2)
            self.assertEqual(saved["atrophy_outputs"][0]["info"]["capabilities"], {"standard": 1})
            self.assertEqual(len(events), 2)

    def test_exception_restores_original_functions(self):
        def bad(*args): raise RuntimeError("expected control")
        eco, atrophy = N(run_genotype=bad), N(prune_all_interventions=bad)
        dev = N(ecology=eco, atrophy_ir=atrophy, verify_candidate=bad,
                morph=N(to_json=json.dumps))
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                with VerifierCapture(dev, tmp):
                    dev.verify_candidate({}, {}, 0)
            self.assertIs(dev.verify_candidate, bad)
            self.assertIs(eco.run_genotype, bad)


if __name__ == "__main__":
    unittest.main()
