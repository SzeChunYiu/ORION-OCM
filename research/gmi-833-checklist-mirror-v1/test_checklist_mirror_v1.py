"""Tests for the #833 checklist custody mirror, safe-write and compaction.

Every invariant in FREEZE_V1.md ships with a hostile that must be DETECTED,
not merely absent. Run:

    python3 -I -B  test_checklist_mirror_v1.py -v
    python3 -I -O -B test_checklist_mirror_v1.py -v
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import checklist_core_v1 as core
import compact_body_v1 as comp
import issue_body_safe_write_v1 as safe

MIRROR = os.path.join(HERE, "ISSUE_833_BODY_MIRROR.md")

SMALL = u"\n".join([
    u"# Title",
    u"",
    u"# A. Section one",
    u"",
    u"- [x] Alpha row. — ✅ #100 `gmi-pkg-a-v1` A-1: alpha evidence with numbers 1/2.",
    u"- [ ] Beta row.",
    u"",
    u"# B. Section two",
    u"",
    u"- [ ] Gamma row.",
    u"- [x] Delta row. — ✅ PR #200 / #201 D-1: delta evidence.",
])


def rep(anchor, old, new):
    return {"anchor": anchor, "old": old, "new": new, "_source": "test"}


class TestParse(unittest.TestCase):
    def test_small_body_parses_exactly(self):
        rows, defect = core.parse(SMALL)
        self.assertEqual(len(rows), 4)
        self.assertIsNone(defect)
        self.assertEqual([r["checked"] for r in rows], [True, False, False, True])
        self.assertEqual(rows[0]["text"], u"Alpha row.")
        self.assertEqual(rows[0]["section"], u"# A. Section one")
        self.assertEqual(rows[3]["section"], u"# B. Section two")

    def test_keys_are_section_scoped_and_stable(self):
        rows, _ = core.parse(SMALL)
        self.assertEqual(len(set(r["key"] for r in rows)), 4)
        again, _ = core.parse(SMALL)
        self.assertEqual([r["key"] for r in rows], [r["key"] for r in again])

    def test_hostile_checked_row_without_evidence_is_detected(self):
        bad = SMALL.replace(
            u"- [x] Alpha row. — ✅ #100 `gmi-pkg-a-v1` A-1: alpha evidence with numbers 1/2.",
            u"- [x] Alpha row.")
        self.assertRaises(core.ChecklistError, core.parse, bad)

    def test_hostile_unchecked_row_with_evidence_is_detected(self):
        bad = SMALL.replace(u"- [ ] Beta row.", u"- [ ] Beta row. — ✅ #999 fake.")
        self.assertRaises(core.ChecklistError, core.parse, bad)

    def test_truncation_defect_is_detected(self):
        rows, defect = core.parse(SMALL + u"\n- [")
        self.assertEqual(defect, u"- [")
        self.assertEqual(len(rows), 4)

    def test_no_false_alarm_on_clean_body(self):
        _, defect = core.parse(SMALL)
        self.assertIsNone(defect)


class TestSafeWrite(unittest.TestCase):
    def test_declared_replacement_applies_and_verifies(self):
        old = u"- [ ] Beta row."
        new = u"- [x] Beta row. — ✅ #300 `gmi-pkg-b-v1` B-1: beta evidence."
        body2, intended = safe.apply_replacements(SMALL, [rep(u"# A. Section one", old, new)])
        a, b = safe.verify(SMALL, body2, intended)
        self.assertEqual(sum(1 for r in a if r["checked"]), 2)
        self.assertEqual(sum(1 for r in b if r["checked"]), 3)

    def test_hostile_wrong_section_anchor_is_refused(self):
        # "Beta row." lives in section A; declaring it under B must refuse
        self.assertRaises(
            safe.RefusedWrite, safe.apply_replacements, SMALL,
            [rep(u"# B. Section two", u"- [ ] Beta row.", u"- [x] Beta row. — ✅ #1 x.")])

    def test_hostile_stale_old_line_is_refused(self):
        # a concurrent lane already closed the row; our stale 'old' no longer matches
        live = SMALL.replace(u"- [ ] Beta row.",
                             u"- [x] Beta row. — ✅ #400 `other-lane-v1` O-1: their evidence.")
        self.assertRaises(
            safe.RefusedWrite, safe.apply_replacements, live,
            [rep(u"# A. Section one", u"- [ ] Beta row.", u"- [x] Beta row. — ✅ #1 ours.")])

    def test_hostile_ambiguous_old_line_is_refused(self):
        live = SMALL.replace(u"- [ ] Beta row.", u"- [ ] Beta row.\n- [ ] Beta row.")
        self.assertRaises(
            safe.RefusedWrite, safe.apply_replacements, live,
            [rep(u"# A. Section one", u"- [ ] Beta row.", u"- [x] Beta row. — ✅ #1 x.")])

    def test_hostile_undeclared_collateral_edit_is_refused(self):
        old = u"- [ ] Beta row."
        new = u"- [x] Beta row. — ✅ #300 `gmi-pkg-b-v1` B-1: beta evidence."
        body2, intended = safe.apply_replacements(SMALL, [rep(u"# A. Section one", old, new)])
        # simulate a second, undeclared line change slipping into the same write
        smuggled = body2.replace(u"- [ ] Gamma row.", u"- [ ] Gamma row EDITED.")
        self.assertRaises(safe.RefusedWrite, safe.verify, SMALL, smuggled, intended)

    def test_hostile_row_text_rewrite_is_refused(self):
        old = u"- [ ] Beta row."
        new = u"- [x] Beta row RENAMED. — ✅ #300 B-1: evidence."
        body2, intended = safe.apply_replacements(SMALL, [rep(u"# A. Section one", old, new)])
        self.assertRaises(safe.RefusedWrite, safe.verify, SMALL, body2, intended)

    def test_hostile_un_checking_a_closed_row_is_refused(self):
        old = u"- [x] Alpha row. — ✅ #100 `gmi-pkg-a-v1` A-1: alpha evidence with numbers 1/2."
        new = u"- [ ] Alpha row."
        body2, intended = safe.apply_replacements(SMALL, [rep(u"# A. Section one", old, new)])
        self.assertRaises(safe.RefusedWrite, safe.verify, SMALL, body2, intended)

    def test_hostile_over_limit_body_is_refused(self):
        filler = u"x" * core.BODY_LIMIT
        old = u"- [ ] Beta row."
        new = u"- [x] Beta row. — ✅ #300 B-1: " + filler
        body2, intended = safe.apply_replacements(SMALL, [rep(u"# A. Section one", old, new)])
        self.assertRaises(safe.RefusedWrite, safe.verify, SMALL, body2, intended)

    def test_plan_schema_is_enforced(self):
        import json, tempfile
        fd, p = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(p, "w") as fh:
            json.dump({"schema": "WRONG", "issue": 833, "replacements": []}, fh)
        self.assertRaises(safe.RefusedWrite, safe.load_plan, [p])
        os.unlink(p)


class TestCompaction(unittest.TestCase):
    def setUp(self):
        self.body = core.read_text(MIRROR)

    def test_mirror_is_self_consistent_with_the_committed_receipt(self):
        """The mirror, the ledger and the receipt must describe the same body.

        Asserting hardcoded lengths would break every time the live body moves;
        asserting mutual consistency catches the thing that actually matters -
        a mirror refreshed without regenerating the ledger beside it.
        """
        import json, io as _io
        res = json.load(_io.open(os.path.join(HERE, "RESULT_V1.json"), encoding="utf-8"))
        led = json.load(_io.open(os.path.join(HERE, "EVIDENCE_LEDGER_V1.json"), encoding="utf-8"))
        rows, defect = core.parse(self.body)
        ob = res["observed_body"]
        self.assertEqual(len(self.body), ob["chars"])
        self.assertEqual(core.body_sha256(self.body), ob["sha256"])
        self.assertEqual(len(rows), ob["rows"])
        self.assertEqual(sum(1 for r in rows if r["checked"]), ob["checked"])
        self.assertEqual(sum(1 for r in rows if not r["checked"]), ob["unchecked"])
        self.assertEqual(led["row_count"], ob["rows"])
        self.assertEqual(led["checked"], ob["checked"])
        self.assertEqual(led["source_body_sha256"], ob["sha256"])
        self.assertEqual(core.BODY_LIMIT - len(self.body), ob["headroom_chars"])

    def test_the_D1_truncation_defect_is_still_present_and_recorded(self):
        _, defect = core.parse(self.body)
        import json, io as _io
        res = json.load(_io.open(os.path.join(HERE, "RESULT_V1.json"), encoding="utf-8"))
        self.assertEqual(defect, u"- [")
        self.assertTrue(res["defect_D1_truncation"]["detected"])
        self.assertEqual(res["defect_D1_truncation"]["verbatim_tail_token"], defect)
        self.assertFalse(res["defect_D1_truncation"]["recovered"])
        self.assertTrue(res["defect_D1_truncation"]["reconstruction_refused"])

    def test_freeze_time_measurement_is_retained_immutably(self):
        import json, io as _io
        res = json.load(_io.open(os.path.join(HERE, "RESULT_V1.json"), encoding="utf-8"))
        ft = res["freeze_time_measurement"]
        self.assertEqual(ft["chars"], 64031)
        self.assertEqual(ft["headroom_chars"], 1505)
        self.assertEqual(ft["checked"], 167)
        self.assertEqual(ft["unchecked"], 92)

    def test_compaction_preserves_signature_and_recovers_headroom(self):
        rows, _ = core.parse(self.body)
        new, ledger = comp.compact(self.body)
        rows2, _ = core.parse(new)
        self.assertEqual(core.signature(rows), core.signature(rows2))
        self.assertEqual([r["text"] for r in rows], [r["text"] for r in rows2])
        self.assertLess(len(new), len(self.body))
        self.assertGreater(ledger["compaction"]["chars_reclaimed"], 35000)
        self.assertGreater(ledger["compaction"]["headroom_after"], 37000)

    def test_every_removed_annotation_is_recoverable_byte_exact(self):
        rows, _ = core.parse(self.body)
        _, ledger = comp.compact(self.body)
        by_key = dict((e["key"], e["evidence"]) for e in ledger["entries"])
        checked = [r for r in rows if r["checked"]]
        self.assertEqual(len(checked), sum(1 for r in rows if r["checked"]))
        self.assertGreaterEqual(len(checked), 167)
        for r in checked:
            self.assertEqual(by_key[r["key"]], r["evidence"])

    def test_compaction_is_idempotent_on_signature(self):
        once, _ = comp.compact(self.body)
        twice, _ = comp.compact(once)
        a, _ = core.parse(once)
        b, _ = core.parse(twice)
        self.assertEqual(core.signature(a), core.signature(b))
        self.assertEqual([r["text"] for r in a], [r["text"] for r in b])

    def test_hostile_duplicate_row_key_is_refused(self):
        rows, _ = core.parse(self.body)
        first = rows[0]["raw"]
        bad = self.body.replace(first, first + u"\n" + first, 1)
        self.assertRaises(SystemExit, comp.compact, bad)

    def test_pointer_keeps_a_resolvable_reference(self):
        rows, _ = core.parse(self.body)
        for r in rows:
            if not r["checked"]:
                continue
            p = comp.pointer(r["evidence"], r["key"])
            self.assertIn(u"L:" + r["key"][:12], p)
            self.assertLess(len(p), 140)


if __name__ == "__main__":
    unittest.main(verbosity=2)
