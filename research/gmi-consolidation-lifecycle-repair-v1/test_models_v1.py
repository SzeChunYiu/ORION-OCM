import unittest
from fractions import Fraction as F
from itertools import product
from finite_machine_v1 import Machine, refine, quotient, execute, preserving_update
from independent_oracle_v1 import distinguishing_word
from cost_controls_v1 import total, bounds_decision, round_cost, convert, decode, controls
from check_v1 import future_control, update_control

class ModelTests(unittest.TestCase):
    def test_future_teach_and_constructive_quotient(self):
        r = future_control()
        self.assertEqual((r["current_classes"], r["future_classes"]), (2, 3))
        self.assertNotEqual(*r["teach_query_traces"])

    def test_equal_capacity_does_not_restore_destroyed_state(self):
        self.assertFalse(update_control()["destructive_decodable"])
        self.assertIsNone(preserving_update((0, 1), (0, 0)))

    def test_duplicate_future_state_is_legally_removed(self):
        m = Machine((1, 1), ((0,), (1,)), ((3,), (3,)))
        small, e = quotient(m, refine(m))
        self.assertEqual(len(small.q), 1)
        self.assertIsNone(distinguishing_word(m, 0, 1))
        self.assertEqual(execute(m, 1, (0,)*10)[0], execute(small, e[1], (0,)*10)[0])

    def test_emission_conflict_rejected_even_when_current_labels_equal(self):
        m = Machine((0, 0), ((0,), (1,)), ((0,), (1,)))
        with self.assertRaises(ValueError):
            quotient(m, (0, 0))
        self.assertEqual(distinguishing_word(m, 0, 1), (0,))

    def test_incomplete_or_illegal_register_refused(self):
        with self.assertRaises(ValueError):
            Machine((), (), ())
        with self.assertRaises(ValueError):
            Machine((0,), ((1,),), ((0,),))
        with self.assertRaises(ValueError):
            Machine((0,), ((0,),), ((),))
        with self.assertRaises(ValueError):
            Machine((True,), ((0,),), ((0,),))
        with self.assertRaises(ValueError):
            execute(Machine((0,), ((0,),), ((0,),)), 0, (1,))

    def test_paid_horizon_loss_and_revival(self):
        r = controls()
        self.assertEqual(r["horizons"][1]["compact_minus_raw"], "1")
        self.assertEqual(r["horizons"][2]["compact_minus_raw"], "-1")
        self.assertEqual(r["same_width_saving_added_replay"]["compact"], "27")

    def test_replay_and_terminal_work_cannot_disappear(self):
        a = total(7, [round_cost(2, 2)], 3)
        b = total(7, [round_cost(2, 2, replay=5)], 3)
        self.assertEqual((a, b), (14, 19))
        with self.assertRaises(ValueError):
            total(7, [{"service": 2}], 0)

    def test_interval_certificate_needs_feasible_upper_bound(self):
        self.assertEqual(bounds_decision((24, 24), (0, 30)), "UNRESOLVED")
        self.assertEqual(bounds_decision((24, 24), (22, 23)), "COMPACT_STRICT")
        self.assertEqual(bounds_decision((24, 24), (24, 24)), "TIE")
        self.assertEqual(bounds_decision((24, 24), (25, 26)), "RAW_STRICT")
        for bad in ((2, 1), (-1, 2), (float("nan"), 2), (True, 2)):
            with self.assertRaises(ValueError):
                bounds_decision(bad, (0, 1))

    def test_converter_rejects_unregistered_answer_vector(self):
        with self.assertRaises(ValueError):
            convert((0, 0, 1, 1, 0))
        with self.assertRaises(ValueError):
            decode((0, 0), 5)
        for a, b in product((0, 1), repeat=2):
            raw = (a, b, a^b, 1-a, a|b)
            self.assertEqual(tuple(decode(convert(raw), i) for i in range(5)), raw)

    def test_aggregate_inequality_all_small_authored_prices(self):
        cases = 0
        for setup, r, c, h in product(range(4), repeat=4):
            actual = total(setup, [round_cost(c, 0)]*h, 0) - total(0, [round_cost(r, 0)]*h, 0)
            self.assertEqual(actual, setup-h*(r-c))
            self.assertEqual(actual < 0, h*(r-c) > setup)
            cases += 1
        self.assertEqual(cases, 256)

if __name__ == "__main__":
    unittest.main()
