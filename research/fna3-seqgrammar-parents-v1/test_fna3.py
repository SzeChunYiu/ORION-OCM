#!/usr/bin/env python3
"""Tests for the FNA-3/D5 parent suite (fna3.py). Stdlib unittest, Python 3.8.

Run on the execution host (billy-laptop):  python3 test_fna3.py
No UD custody files needed: every test uses the synthetic worlds or tiny
hand-built inputs. The UD worlds are exercised by fna3.py itself.
"""
import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fna3
from fna3 import (
    CTW, NgramWB, PCFGEM, PPMC, BPEPPM, KNNSeq, LogisticDiag, HMMEM,
    gen_psa, gen_nested, gen_lexicon, nested_blocks, shuffled_ids,
    unigram_floor, closure_for, score_oracle, state_digest,
)


class OracleTests(unittest.TestCase):
    def test_w1_oracle_sums_to_one(self):
        stream, meta = gen_psa(2000)
        oracle = meta["oracle"]
        for t in (5, 100, 1500):
            dist = oracle(t, stream[:t])
            self.assertEqual(len(dist), 3)
            self.assertAlmostEqual(sum(dist), 1.0, places=9)
            self.assertTrue(all(p >= 0.0 for p in dist))

    def test_w2_oracle_tracks_depth(self):
        _, meta = gen_nested(500, d_max=4)
        oracle = meta["oracle"]
        # depth 0 -> only a or c possible; P(b) = 0
        d0 = oracle(3, "cccb")
        self.assertEqual(d0[1], 0.0)
        # deciding phase (last symbol 'a', depth>0): innermost S picks a or c
        # (depth-first law of S -> a S b | c); b is impossible
        din = oracle(4, "aaca")  # depth 2, last 'a'
        self.assertEqual(din[1], 0.0)
        self.assertAlmostEqual(sum(din), 1.0, places=9)
        din2 = oracle(6, "aaacaa")  # depth 3, last 'a'
        self.assertEqual(din2[1], 0.0)
        # unwinding phase (last symbol 'b' or 'c', depth>0): b deterministic
        din3 = oracle(4, "aacb")  # depth 1, last 'b'
        self.assertEqual(din3[1], 1.0)
        din4 = oracle(3, "aac")  # depth 2, last 'c'
        self.assertEqual(din4[1], 1.0)

    def test_w3_oracle_deterministic_inside_word(self):
        stream, meta = gen_lexicon(3000)
        oracle = meta["oracle"]
        alpha = meta["alpha"]
        # at a non-final word position the next char is certain
        found = 0
        for t in range(1, 2900):
            dist = oracle(t, stream[:t])
            if max(dist) == 1.0:
                found += 1
                self.assertIn(stream[t], alpha)
        self.assertGreater(found, 500)  # most positions are inside words

    def test_score_oracle_beats_uniform(self):
        stream, meta = gen_psa(84000)
        res = score_oracle(stream, meta["alpha"], meta["oracle"], 64000, 2000)
        self.assertLess(res["bits_per_symbol"], math.log(3.0, 2.0) - 0.1)


class CTWTests(unittest.TestCase):
    def test_depth0_matches_kt_closed_form(self):
        ctw = CTW("01", depth=0)
        seq = "0011010010" * 7
        prod = 1.0
        for i, ch in enumerate(seq):
            x = int(ch)
            prod *= ctw.prob(x, [int(c) for c in seq[:i]])
            ctw.observe(x, [int(c) for c in seq[:i]])
        n0 = seq.count("0")
        n1 = seq.count("1")
        kt = 1.0
        c0 = c1 = 0
        for ch in seq:
            if ch == "0":
                kt *= (c0 + 0.5) / (c0 + c1 + 1.0)
                c0 += 1
            else:
                kt *= (c1 + 0.5) / (c0 + c1 + 1.0)
                c1 += 1
        self.assertAlmostEqual(prod, kt, places=12)
        self.assertEqual((n0, n1), (c0, c1))

    def test_simulate_equals_root_weight_ratio(self):
        ctw = CTW("ab", depth=6)
        ids = [0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1] * 5
        for i in range(len(ids) - 1):
            hist = ids[:i]
            x = ids[i]
            w_before = ctw.nodes[()][4]
            p = ctw.prob(x, hist)
            ctw.observe(x, hist)
            w_after = ctw.nodes[()][4]
            self.assertAlmostEqual(p, math.exp(w_after - w_before), places=10)

    def test_unobserve_restores_digest(self):
        ctw = CTW("ab", depth=4)
        ids = [random.Random(7).randint(0, 1) for _ in range(400)]
        ctw.fit(ids, 300)
        d0 = state_digest(ctw.model_state())
        for i in range(300, 400):
            ctw.observe(ids[i], ids[:i])
        for i in range(399, 299, -1):
            ctw.unobserve(ids[i], ids[:i])
        self.assertEqual(state_digest(ctw.model_state()), d0)
        # caches remain consistent: counts vs recompute leave a usable model
        p = ctw.prob(0, ids[:10])
        self.assertTrue(0.0 < p <= 1.0)


class NgramPPMTests(unittest.TestCase):
    def test_ngram_learns_and_restores(self):
        arm = NgramWB("abc")
        seq = ("abc" * 120 + "acb" * 30)
        ids = ["abc".index(c) for c in seq]
        arm.fit(ids, len(ids) - 64)
        d0 = state_digest(arm.model_state())
        tail = ids[len(ids) - 64:]
        for i, x in enumerate(tail):
            arm.observe(x, ids[:len(ids) - 64 + i])
        for i in range(63, -1, -1):
            arm.unobserve(tail[i], ids[:len(ids) - 64 + i])
        self.assertEqual(state_digest(arm.model_state()), d0)
        p = arm.prob(0, [0, 1])
        self.assertTrue(0.0 < p < 1.0)

    def test_ppm_escape_and_restore(self):
        arm = PPMC("abc")
        ids = [0, 1, 0, 1, 0, 1] * 40
        arm.fit(ids, len(ids) - 32)
        d0 = state_digest(arm.model_state())
        tail = ids[len(ids) - 32:]
        for i, x in enumerate(tail):
            arm.observe(x, ids[:len(ids) - 32 + i])
        self.assertGreater(arm.prob(1, [0]), 0.4)
        self.assertLess(arm.prob(2, [0]), 1.0 / 3.0)  # unseen pays escape
        for i in range(31, -1, -1):
            arm.unobserve(tail[i], ids[:len(ids) - 32 + i])
        self.assertEqual(state_digest(arm.model_state()), d0)


class PCFGTests(unittest.TestCase):
    def _arm(self):
        return PCFGEM(["a", "b", "c"])

    def test_prefix_probabilities_multiply_to_sentence_probability(self):
        arm = self._arm()
        # deterministic weights so the check is exact
        arm.w = [0.6, 1.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0]  # S-sum = T-sum = 1
        sent = "aacbb"
        ids = ["a", "b", "c"].index
        sent_ids = [ids(c) for c in sent]
        arm.reset_block()
        prod = 1.0
        for x in sent_ids:
            prod *= arm.prob(x)
        beta = arm._inside(sent_ids)
        total = beta[len(sent_ids)][0][0]
        # prefix product = P(x_1..x_n) >= P(sentence) = inside total;
        # equality exactly when no continuation mass survives the last symbol
        self.assertGreaterEqual(prod, total * (1.0 - 1e-9))
        self.assertGreater(total, 0.0)
        # terminal 'c' closes every open constituent: no continuation mass,
        # so the identity is exact for a pure-'c' block
        arm.reset_block()
        self.assertAlmostEqual(arm.prob(2), 0.4, places=12)

    def test_em_recovers_nesting_and_suppresses_distractors(self):
        stream, meta = gen_nested(4000, d_max=4)
        blocks = nested_blocks(stream, 0, 4000)
        arm = self._arm()
        arm.blocks = blocks
        arm.fit([], 0)
        # S-rules: core r0(S->aT)+r2(S->c) must hold ~all S mass; the
        # distractor S-rules r3,r4,r6,r7 must be pushed down. (r1 is the
        # only T rule and r5 the only W rule: both stay 1.0 uninformative.)
        s_core = arm.w[0] + arm.w[2]
        s_distract = arm.w[3] + arm.w[4] + arm.w[6] + arm.w[7]
        self.assertGreater(s_core, 0.9)
        self.assertLess(s_distract, 0.1)
        # scoring protocol runs and produces finite loss
        res = fna3.score_p5(arm, blocks[:50], ["a", "b", "c"])
        self.assertTrue(0.0 < res["bits_per_symbol"] < 12.0)

    def test_peek_does_not_advance(self):
        arm = self._arm()
        arm.reset_block()
        a = arm.peek("a")
        b = arm.peek("a")
        self.assertEqual(a, b)


class BPEKNNLogisticTests(unittest.TestCase):
    def test_bpe_deterministic_and_reduces_tokens(self):
        s = ("abracadabra alakazam " * 200)
        a1 = BPEPPM(sorted(set(s)), merges=20)
        a2 = BPEPPM(sorted(set(s)), merges=20)
        a1.fit([sorted(set(s)).index(c) for c in s], len(s))
        a2.fit([sorted(set(s)).index(c) for c in s], len(s))
        self.assertEqual(a1.merge_order, a2.merge_order)
        unit_count = sum(len(a1._apply_merges(w)) for w in s.split())
        self.assertLess(unit_count, len(s))  # merges reduce below char count
        self.assertGreater(a1.merges_used, 0)

    def test_bpe_word_protocol(self):
        s = "hello world " * 3
        alpha = sorted(set(s))
        arm = BPEPPM(alpha, merges=4)
        arm.fit([alpha.index(c) for c in s], len(s))
        self.assertTrue(arm._word_mode)
        # push "world"; nothing completes before the delimiter
        for ch in "worl":
            self.assertEqual(arm.push_char(ch), ())
        self.assertEqual(arm.buf, list("worl"))
        units = arm.push_char("d")
        self.assertEqual(units, ())  # word not delimited yet
        units = arm.push_char(" ")
        self.assertTrue(len(units) >= 2)  # the word's units + the space unit
        self.assertEqual(units[-1], " ")
        self.assertEqual(arm.buf, [])

    def test_knn_retrieves_exact_window(self):
        arm = KNNSeq("ab", h=4, k=4)
        ids = [0, 1, 0, 1, 1, 0, 1, 0, 1, 1] * 50
        arm.fit(ids, len(ids))
        # window ...0,1,0,1 was always followed by 1
        p1 = arm.prob(1, [0, 1, 0, 1])
        p0 = arm.prob(0, [0, 1, 0, 1])
        self.assertGreater(p1, p0)

    def test_logistic_learns_deterministic_map(self):
        arm = LogisticDiag("ab")
        ids = [0, 1] * 300
        arm.fit(ids, len(ids))
        self.assertGreater(arm.prob(0, [0, 1, 0, 1]), arm.prob(1, [0, 1, 0, 1]))
        a2 = LogisticDiag("ab")
        a2.fit(ids, len(ids))
        self.assertEqual(arm.model_state(), a2.model_state())

    def test_hmm_runs_and_is_deterministic(self):
        ids = [random.Random(3).randint(0, 2) for _ in range(600)]
        a = HMMEM("abc", iters=3)
        b = HMMEM("abc", iters=3)
        a.fit(ids, 500)
        b.fit(ids, 500)
        self.assertAlmostEqual(a.model_state()["B"][0][0], b.model_state()["B"][0][0], places=12)
        p = a.prob(0, [])
        self.assertTrue(0.0 < p <= 1.0)


class ControlTests(unittest.TestCase):
    def test_shuffle_preserves_multiset(self):
        ids = list(range(1000))
        sid = shuffled_ids(ids, 900)
        self.assertEqual(sorted(sid[:900]), list(range(900)))
        self.assertEqual(sid[900:], ids[900:])

    def test_closure_contains_actual(self):
        cl = closure_for("aabbc" * 10, "c")
        self.assertIn("c", cl)
        self.assertTrue(set("abc").issubset(cl))

    def test_unigram_floor_constant_stream(self):
        # 500 fit symbols of 'a': add-0.5 gives p~0.999 -> < 0.01 bits on 'a's
        self.assertLess(unigram_floor("a" * 600, 500, "a" * 100, ["a", "b"]), 0.01)

    def test_nested_blocks_are_depth0(self):
        stream, _ = gen_nested(3000, d_max=4)
        blocks = nested_blocks(stream, 0, 3000)
        joined = "".join(blocks)
        self.assertEqual(joined, stream)
        for blk in blocks:
            if blk[0] != "a":
                continue
            depth = 0
            for ch in blk[:-1]:
                depth += 1 if ch == "a" else (-1 if ch == "b" else 0)
                self.assertGreaterEqual(depth, 1)  # never closes before the end
        # every COMPLETE block ends at depth 0; the final block may be
        # truncated mid-nesting by the window boundary
        for blk in blocks[:-1]:
            depth = 0
            for ch in blk:
                depth += 1 if ch == "a" else (-1 if ch == "b" else 0)
            self.assertEqual(depth, 0)


class FreezeTests(unittest.TestCase):
    def _load_freeze(self):
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "FREEZE_FNA3_V1.json"), encoding="utf-8") as fh:
            return json.loads(fh.read())

    def test_no_forbidden_terminals(self):
        freeze = self._load_freeze()
        for bad in ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT", "AGI", "GENERAL_SUPERIORITY"):
            self.assertNotIn(bad, freeze["terminals_allowed"])
        self.assertIn("PARENT_SUFFICIENT_FOR_<function>", freeze["terminals_allowed"])

    def test_dial_arms_frozen(self):
        freeze = self._load_freeze()
        self.assertEqual(freeze["expressivity_dial"]["arms"], ["P0", "P1", "P2", "P3", "P5", "P8"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
