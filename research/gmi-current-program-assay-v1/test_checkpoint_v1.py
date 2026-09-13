import copy
import unittest
from call_capture_v1 import validate_charges
from checkpoint_v1 import checkpoint, digest, graph, require_program, substitute
from native_source_v1 import load
from program_controls_v1 import acquire, run


class CheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = load()
        cls.original, _ = acquire(cls.native)

    def setUp(self):
        self.vm = checkpoint(self.original, self.native)

    def test_native_sham_restoration_exact(self):
        result = run(self.native)
        for label in ("acquired", "sham", "restored"):
            arm = result["arms"][label]
            self.assertEqual(arm["post_assignment_sha256"], result["checkpoint_sha256"])
            self.assertEqual(arm["served"], result["arms"]["acquired"]["served"])
        events = [event for step in result["acquisition_history"] for event in step["native_charge_events"]]
        self.assertTrue(validate_charges({"charge_events": events, "final_ledger": result["acquisition_ledger"]}))
        self.assertGreater(result["acquisition_ledger"]["upd"], 0)
        self.assertEqual(result["same_input_zero_label_control"]["served"]["program"], [0, 0])

    def test_joint_alias_rng_ledger_store_isolation(self):
        other = checkpoint(self.vm, self.native)
        self.assertIs(other.nodes, other.g["nodes"])
        self.assertFalse(graph(other, self.native)[1] & graph(self.vm, self.native)[1])
        saved = digest(self.vm, self.native)
        other.M.lfsr ^= 1
        other.M.L.c["exec"] += 1
        next(iter(other.M.stores.values())).append(((0, 0, 0, 0), 16))
        self.assertEqual(digest(self.vm, self.native), saved)
        self.assertNotEqual(digest(other, self.native), saved)

    def test_active_tape_and_unfinished_event_refused(self):
        self.vm.M.tape = []
        with self.assertRaises(ValueError):
            checkpoint(self.vm, self.native)
        self.vm.M.tape = None
        self.vm.M.L.writes_in_event.add("uncompleted")
        with self.assertRaises(ValueError):
            checkpoint(self.vm, self.native)

    def test_observer_closure_extra_fields_and_subclass_refused(self):
        self.vm.observer = lambda: self.original.M
        with self.assertRaises(ValueError):
            checkpoint(self.vm, self.native)
        del self.vm.observer
        observed = type("Observed", (self.native.vm.VM,), {})
        self.vm.__class__ = observed
        with self.assertRaises(ValueError):
            checkpoint(self.vm, self.native)

    def test_invalid_program_bodies_refused(self):
        for bad in (None, (True, 0), (32, 0), [1, 0], (1,)):
            with self.subTest(body=bad), self.assertRaises(ValueError):
                substitute(self.vm, bad, self.native)

    def test_compiled_search_typed_but_not_same_intervention(self):
        g = self.native.zoo.compiled_search()
        self.native.morph.typecheck(g)
        machine = self.native.core.Machine(copy.deepcopy(self.native.bases.B0))
        compiled = self.native.vm.VM(g, machine)
        compiled.init()
        with self.assertRaisesRegex(ValueError, "template|cache"):
            checkpoint(compiled, self.native)

    def test_grammar_and_graph_links_not_silently_accepted(self):
        node = require_program(self.vm, self.native)
        self.vm.grammars[node].progs.append((99, 99))
        with self.assertRaises(ValueError):
            checkpoint(self.vm, self.native)


if __name__ == "__main__":
    unittest.main()
