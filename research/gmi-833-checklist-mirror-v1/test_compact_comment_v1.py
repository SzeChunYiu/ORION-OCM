import io, json, os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import compact_comment_v1 as cc
import checklist_core_v1 as core
SEP = core.SEP
SMALL = u"\n".join([u"## AE — title", u"", u"### AE1 — first", u"",
    u"- [x] Alpha row. — ✅ `gmi-833-ae-ae1-x-v1` AE1-1/AE1-2: alpha evidence with 3/4 and 0 violations.",
    u"- [ ] Beta row.", u"", u"### AE2 — second", u"",
    u"- [x] Gamma row. — ✅ PR #1033 / #1038 `gmi-833-ae-ae2-x-v1` AE2-3: gamma evidence.",
    u"```", u"- [x] inside a fence must be ignored — ✅ nope", u"```",
    u"- [ ] Delta row."])
class T(unittest.TestCase):
    def test_parse_skips_fences_and_reads_sections(self):
        r = cc.parse(SMALL); self.assertEqual(len(r), 4)
        self.assertEqual([x["checked"] for x in r], [True, False, True, False])
        self.assertEqual(r[2]["section"], u"### AE2 — second")
    def test_compaction_preserves_rows_and_ledger_holds_real_evidence(self):
        new, led = cc.compact(SMALL, 1, prior_ledger={"entries": []})
        self.assertEqual(cc.signature(cc.parse(new)), cc.signature(cc.parse(SMALL)))
        ev = {e["key"]: e["evidence"] for e in led["entries"] if e["checked"]}
        self.assertEqual(len(ev), 2)
        for k, v in ev.items(): self.assertFalse(cc._is_pointer(v, k))
        self.assertLess(len(new), len(SMALL))
    def test_recompaction_never_degrades_ledger(self):
        once, led1 = cc.compact(SMALL, 1, prior_ledger={"entries": []})
        twice, led2 = cc.compact(once, 1, prior_ledger=led1)
        e1 = {e["key"]: e["evidence"] for e in led1["entries"]}
        e2 = {e["key"]: e["evidence"] for e in led2["entries"]}
        self.assertEqual(e1, e2)
    def test_hostile_recompaction_without_prior_ledger_is_refused(self):
        once, _ = cc.compact(SMALL, 1, prior_ledger={"entries": []})
        self.assertRaises(SystemExit, cc.compact, once, 1, {"entries": []})
    def test_hostile_duplicate_row_refused(self):
        bad = SMALL.replace(u"- [ ] Beta row.", u"- [ ] Beta row.\n- [ ] Beta row.")
        self.assertRaises(SystemExit, cc.compact, bad, 1, {"entries": []})
    def test_pointer_is_short_and_resolvable(self):
        r = cc.parse(SMALL)[0]; p = cc.pointer(r["evidence"], r["key"])
        self.assertIn(u"L:" + r["key"][:12], p); self.assertLess(len(p), 120)
    def test_real_mirrored_ae_comment_compacts_under_ceiling(self):
        p = os.path.join(HERE, "comments", "comment_5692689542.md")
        if not os.path.exists(p): self.skipTest("mirror absent")
        body = core.read_text(p); new, led = cc.compact(body, 5692689542, prior_ledger={"entries": []})
        self.assertLess(len(new), cc.LIMIT - 20000)
        self.assertEqual(cc.signature(cc.parse(new)), cc.signature(cc.parse(body)))
if __name__ == "__main__": unittest.main(verbosity=1)
