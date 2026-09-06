from dataclasses import replace
from itertools import product
import unittest

from finite_views import PackedView, ViewRefusal, compile_view, select_view, verify_view


class FiniteViewTests(unittest.TestCase):
    def setUp(self):
        self.names = ("bulk", "spectrum", "indexed_response")
        self.rows = tuple(tuple(map(str, row)) for row in product(range(2), repeat=3))

    def test_incomparable_views_and_joint_refinement(self):
        a = compile_view(self.rows, self.names, ("bulk",))
        b = compile_view(self.rows, self.names, ("spectrum",))
        joint = compile_view(self.rows, self.names, ("bulk", "spectrum"))
        full = compile_view(self.rows, self.names, self.names)
        self.assertEqual([len(v.signatures) for v in (a, b, joint, full)], [2, 2, 4, 8])
        self.assertEqual(a.signature_at(0), a.signature_at(2))
        self.assertNotEqual(b.signature_at(0), b.signature_at(2))
        self.assertEqual(b.signature_at(0), b.signature_at(4))
        self.assertNotEqual(a.signature_at(0), a.signature_at(4))
        for v in (a, b, joint, full):
            self.assertTrue(verify_view(iter(self.rows), iter(self.names), v))
        for key, expected in (("bulk", a), ("spectrum", b), ("indexed_response", full)):
            self.assertIs(select_view((full, joint, b, a), (key,), current_source_digest=a.source_digest), expected)

    def test_finer_question_cannot_be_answered_from_coarse_view(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        with self.assertRaisesRegex(ViewRefusal, "REFINE_REQUIRED"):
            view.answer(0, "indexed_response", current_source_digest=view.source_digest)

    def test_revocation_observation_must_survive_compression(self):
        names = ("now", "after_left_withdrawal")
        rows = (("LIVE", "DEAD"), ("LIVE", "LIVE"), ("LIVE", "UNKNOWN"))
        coarse = compile_view(rows, names, ("now",))
        lifecycle = compile_view(rows, names, names)
        self.assertEqual(len(coarse.signatures), 1)
        self.assertEqual(len(lifecycle.signatures), 3)
        with self.assertRaises(ViewRefusal):
            coarse.answer(0, names[1], current_source_digest=coarse.source_digest)
        self.assertEqual(lifecycle.answer(2, names[1], current_source_digest=lifecycle.source_digest), "UNKNOWN")

    def test_source_drift_in_an_unretained_column_invalidates_binding(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        changed = list(self.rows)
        changed[0] = ("0", "0", "changed")
        newer = compile_view(changed, self.names, ("bulk",))
        self.assertFalse(verify_view(changed, self.names, view))
        with self.assertRaisesRegex(ViewRefusal, "STALE_SOURCE"):
            view.answer(0, "bulk", current_source_digest=newer.source_digest)

    def test_forged_dictionary_rejected_by_source_checker(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        forged = replace(view, signatures=(("wrong",), ("1",)))
        self.assertFalse(verify_view(self.rows, self.names, forged))

    def test_valid_but_wrong_membership_rejected(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        forged = replace(view, codes=bytes([1]) + view.codes[1:])
        self.assertFalse(verify_view(self.rows, self.names, forged))

    def test_source_reordering_and_length_change_rejected(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        for bad in (self.rows[::-1], self.rows[:-1], self.rows + self.rows[:1]):
            self.assertFalse(verify_view(bad, self.names, view))

    def test_one_shot_inputs(self):
        view = compile_view((iter(r) for r in self.rows), iter(self.names), iter(("bulk",)))
        self.assertTrue(verify_view((iter(r) for r in self.rows), iter(self.names), view))

    def test_caller_mutations_do_not_change_view(self):
        rows = [list(r) for r in self.rows]
        names = list(self.names)
        selected = ["bulk"]
        view = compile_view(rows, names, selected)
        rows[0][0] = "wrong"
        names[0] = "wrong"
        selected[0] = "wrong"
        self.assertEqual(view.answer(0, "bulk", current_source_digest=view.source_digest), "0")

    def test_unsigned_width_boundaries(self):
        for n, width in ((1, 1), (256, 1), (257, 2), (65536, 2), (65537, 4)):
            with self.subTest(n=n):
                view = compile_view(((str(i),) for i in range(n)), ("x",), ("x",))
                self.assertEqual(view.code_width, width)
                self.assertEqual(view.answer(n - 1, "x", current_source_digest=view.source_digest), str(n - 1))

    def test_bad_inputs_fail(self):
        for names, rows, retained in (((), (("x",),), ("x",)), (("x", "x"), (("a", "b"),), ("x",)), (("x",), (), ("x",)), (("x",), ((1,),), ("x",)), (("x",), (("a", "b"),), ("x",)), (("x",), (("a",),), ("y",))):
            with self.subTest(names=names, rows=rows):
                with self.assertRaises(ValueError):
                    compile_view(rows, names, retained)

    def test_bad_binary_view_fails(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        for fields in ({"codes": b"\xff"}, {"codes": b""}, {"code_width": 3}, {"code_width": True}, {"source_digest": "not-a-digest"}):
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    replace(view, **fields)

    def test_out_of_range_and_boolean_row_ids_refused(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        for i in (-1, 8, True, "0"):
            with self.subTest(i=i):
                with self.assertRaises(ViewRefusal):
                    view.signature_at(i)

    def test_no_route_is_not_an_answer(self):
        view = compile_view(self.rows, self.names, ("bulk",))
        with self.assertRaises(ViewRefusal):
            select_view((view,), ("spectrum",), current_source_digest=view.source_digest)
        with self.assertRaises(ViewRefusal):
            select_view((view,), ("bulk",), current_source_digest="0" * 64)

    def test_payload_byte_count_matches_concrete_encoding(self):
        view = compile_view(self.rows, self.names, self.names)
        self.assertEqual(view.encoded_payload_bytes, len(view.to_bytes()))
        changed = replace(view, signatures=tuple(tuple("longer:" + x for x in r) for r in view.signatures))
        self.assertGreater(changed.encoded_payload_bytes, view.encoded_payload_bytes)
        self.assertEqual(changed.encoded_payload_bytes, len(changed.to_bytes()))

    def test_exhaustive_two_bit_finite_tables(self):
        # All 256 four-row tables over a two-bit alphabet; independent equality
        # oracle checks that dictionary codes merge iff selected responses agree.
        alphabet = tuple(product("01", repeat=2))
        checked = 0
        for rows in product(alphabet, repeat=4):
            for selected in (("a",), ("b",), ("a", "b")):
                view = compile_view(iter(rows), ("a", "b"), selected)
                self.assertTrue(verify_view(rows, ("a", "b"), view))
                indices = tuple(("a", "b").index(s) for s in selected)
                self.assertEqual(len(view.signatures), len({tuple(r[j] for j in indices) for r in rows}))
                for i, row in enumerate(rows):
                    for j, key in zip(indices, selected):
                        self.assertEqual(view.answer(i, key, current_source_digest=view.source_digest), row[j])
                checked += 1
        self.assertEqual(checked, 768)


if __name__ == "__main__":
    unittest.main()
