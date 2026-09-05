from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from ocm.kso.warrant import WarrantProfile  # noqa: E402
from ocm.language.bootstrap import microworld_lexicon  # noqa: E402
from ocm.language.constructions import Construction, Slot, seed_constructions  # noqa: E402
from ocm.language.interpret import Verdict, interpret  # noqa: E402
from ocm.language.lexicon import Category, Lexeme, Lexicon, Sense  # noqa: E402
from ocm.language.meaning import MNode, MeaningGraph, canonical  # noqa: E402
from ocm.language.microworld import generate  # noqa: E402

from packed_chart import ChartCannotCheck, interpret_packed, packed_matches, packed_phrase_table  # noqa: E402


def catalan(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)


class PackedChartTests(unittest.TestCase):
    def test_agrees_with_historical_interpreter_on_frozen_microworld(self):
        lexicon = microworld_lexicon()
        constructions = seed_constructions()
        for example in generate():
            old = interpret(example.utterance, lexicon, constructions)
            new = interpret_packed(example.utterance, lexicon, constructions).interpretation
            self.assertEqual(new.verdict, old.verdict, example.utterance)
            if old.verdict is Verdict.INTERPRETED:
                self.assertEqual(
                    canonical(new.meaning)[1],
                    canonical(old.meaning)[1],
                    example.utterance,
                )
            else:
                self.assertEqual(
                    [canonical(c.meaning)[1] for c in new.candidates],
                    [canonical(c.meaning)[1] for c in old.candidates],
                    example.utterance,
                )

    def test_duplicate_clause_derivations_are_counted_not_mistaken_for_semantic_ambiguity(self):
        lexicon = microworld_lexicon()
        constructions = list(seed_constructions())
        transitive = next(c for c in constructions if c.construction_id == "en:transitive")
        constructions.append(transitive)
        utterance = "the robot opened the door"
        packed = interpret_packed(utterance, lexicon, constructions)
        self.assertEqual(packed.interpretation.verdict, Verdict.INTERPRETED)
        self.assertEqual(packed.stats.semantic_candidates, 1)
        self.assertEqual(packed.stats.clause_derivations, 2)

    def test_catalan_attachment_ambiguity_is_packed_with_exact_integer_multiplicity(self):
        lexicon = Lexicon()
        lexicon.add(
            Lexeme(
                "robot",
                Category.NOUN,
                (Sense("robot", "robot", "entity", WarrantProfile.one()),),
            )
        )
        lexicon.add(Lexeme("and", Category.CONJ, ()))

        def atom(binding):
            r = binding["n"]
            return MeaningGraph((MNode("x", "entity", r.lemma),), (), root="x")

        def combine(binding):
            # The test deliberately gives every bracketing the same semantics so
            # packing can aggregate all derivations into one exact forest node.
            return binding["left"].meaning

        atom_c = Construction(
            "toy:atom",
            "toy_atom",
            (Slot("n", Category.NOUN),),
            atom,
            WarrantProfile.one(),
            produces="X",
            head_slot="n",
            head_node="x",
            language="toy",
        )
        chain_c = Construction(
            "toy:coord",
            "toy_coord",
            (
                Slot("left", Category.NOUN, phrase="X"),
                Slot("and", Category.CONJ, lemma="and"),
                Slot("right", Category.NOUN, phrase="X"),
            ),
            combine,
            WarrantProfile.one(),
            produces="X",
            head_slot="left",
            head_node="x",
            language="toy",
        )

        nouns = 8
        words = ["robot" if i % 2 == 0 else "and" for i in range(2 * nouns - 1)]
        token_readings = [list(lexicon.analyse(word).readings) for word in words]
        table, _ = packed_phrase_table((atom_c, chain_c), token_readings)
        final = table[(0, len(words))]
        self.assertEqual(len(final), 1)
        self.assertEqual(final[0].derivations, catalan(nouns - 1))
        # Packing is quadratic-size here while represented derivations grow
        # Catalan-fast; no derivation tree list is materialized.
        self.assertLess(sum(len(cell) for cell in table.values()), final[0].derivations)

    def test_phrase_cycles_without_lexical_progress_fail_closed(self):
        c = Construction(
            "toy:bad-unary",
            "bad",
            (Slot("x", Category.NOUN, phrase="X"),),
            lambda b: b["x"].meaning,
            WarrantProfile.one(),
            produces="X",
            head_slot="x",
            language="toy",
        )
        with self.assertRaises(ChartCannotCheck):
            packed_phrase_table((c,), [[]])

    def test_unknown_lexeme_matches_historical_terminal(self):
        lexicon = microworld_lexicon()
        constructions = seed_constructions()
        r = interpret_packed("the robot splorked the door", lexicon, constructions)
        self.assertEqual(r.interpretation.verdict, Verdict.UNKNOWN_LEXEME)


if __name__ == "__main__":
    unittest.main()
