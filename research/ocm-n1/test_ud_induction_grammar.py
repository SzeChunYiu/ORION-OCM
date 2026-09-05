from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ud_induction import (  # noqa: E402
    UDCannotCheck,
    clause_skeleton,
    induce_lexicon,
    parse_conllu,
    past_morphology,
    verify_custody_file,
)
from ud_grammar import coverage, gold_tree, induce_grammar, is_projective, parse_forms  # noqa: E402


TRAIN = """# sent_id = train-1
# text = I saw her.
1\tI\ti\tPRON\tPRP\tCase=Nom|Number=Sing|Person=1\t2\tnsubj\t_\t_
2\tsaw\tsee\tVERB\tVBD\tMood=Ind|Tense=Past|VerbForm=Fin\t0\troot\t_\t_
3\ther\tshe\tPRON\tPRP\tCase=Acc|Gender=Fem|Number=Sing|Person=3\t2\tobj\t_\t_
4\t.\t.\tPUNCT\t.\t_\t2\tpunct\t_\t_

# sent_id = train-2
# text = She saw me.
1\tShe\tshe\tPRON\tPRP\tCase=Nom|Gender=Fem|Number=Sing|Person=3\t2\tnsubj\t_\t_
2\tsaw\tsee\tVERB\tVBD\tMood=Ind|Tense=Past|VerbForm=Fin\t0\troot\t_\t_
3\tme\ti\tPRON\tPRP\tCase=Acc|Number=Sing|Person=1\t2\tobj\t_\t_
4\t.\t.\tPUNCT\t.\t_\t2\tpunct\t_\t_
"""

SOV = """# sent_id = sov-1
# text = I her saw.
1\tI\ti\tPRON\tPRP\tCase=Nom\t3\tnsubj\t_\t_
2\ther\tshe\tPRON\tPRP\tCase=Acc\t3\tobj\t_\t_
3\tsaw\tsee\tVERB\tVBD\tTense=Past|VerbForm=Fin\t0\troot\t_\t_
4\t.\t.\tPUNCT\t.\t_\t3\tpunct\t_\t_
"""

NONPROJECTIVE = """# sent_id = nonproj-1
# text = a b c d
1\ta\ta\tNOUN\tNN\t_\t3\tdep\t_\t_
2\tb\tb\tNOUN\tNN\t_\t4\tdep\t_\t_
3\tc\tc\tVERB\tVB\t_\t0\troot\t_\t_
4\td\td\tNOUN\tNN\t_\t3\tobj\t_\t_
"""


class UDInductionGrammarTests(unittest.TestCase):
    def test_conllu_parser_skips_multiword_rows_but_keeps_basic_tokens(self):
        text = """# sent_id = mwt
1-2\tcan't\t_\t_\t_\t_\t_\t_\t_\t_
1\tca\tcan\tAUX\tMD\tVerbForm=Fin\t3\taux\t_\t_
2\tn't\tnot\tPART\tRB\tPolarity=Neg\t3\tadvmod\t_\t_
3\tgo\tgo\tVERB\tVB\tVerbForm=Inf\t0\troot\t_\t_
"""
        sentences = parse_conllu(text)
        self.assertEqual([t.token_id for t in sentences[0].tokens], [1, 2, 3])
        self.assertEqual(sentences[0].roots[0].lemma, "go")

    def test_induced_lexicon_and_past_morphology_are_evidence_backed(self):
        sentences = parse_conllu(TRAIN)
        lexicon = induce_lexicon(sentences)
        self.assertEqual(lexicon.tokens, 6)
        self.assertIn(("see", "VERB"), lexicon.lemma_upos_counts)
        self.assertTrue(all(a.evidence_id.startswith("ud-ewt:r2.14:") for a in lexicon.attestations))
        morph = past_morphology(sentences)
        self.assertIn(("see", "saw"), {(lemma, form) for lemma, form, _ in morph.irregular_or_non_ed})

    def test_same_dependency_family_retains_conflicting_svo_and_sov_orders(self):
        sentences = parse_conllu(TRAIN) + parse_conllu(SOV)
        grammar = induce_grammar(sentences)
        root_families = {
            family: orders
            for family, orders in grammar.family_order_counts.items()
            if family.startswith("ROOT:VERB<-") and "nsubj:PRON" in family and "obj:PRON" in family
        }
        self.assertEqual(len(root_families), 1)
        orders = next(iter(root_families.values()))
        self.assertEqual(len(orders), 2)
        self.assertTrue(any(order.index("HEAD:VERB") < order.index("CHILD:obj:PRON") for order in orders))
        self.assertTrue(any(order.index("HEAD:VERB") > order.index("CHILD:obj:PRON") for order in orders))

    def test_packed_ud_parser_recovers_seen_projective_structure(self):
        sentences = parse_conllu(TRAIN)
        lexicon = induce_lexicon(sentences)
        grammar = induce_grammar(sentences)
        result = parse_forms(["I", "saw", "her"], lexicon, grammar)
        self.assertIn(result.status, {"PARSED", "AMBIGUOUS"})
        self.assertGreaterEqual(result.derivations, 1)
        self.assertGreaterEqual(result.structural_ambiguity, 1)
        cov = coverage(sentences, sentences)
        self.assertEqual(cov.projective_sentences, 2)
        self.assertEqual(cov.parsed_projective_sentences, 2)
        self.assertEqual(cov.exact_gold_structure_sentences, 2)

    def test_gold_tree_identity_distinguishes_head_surface_position(self):
        svo = gold_tree(parse_conllu(TRAIN)[0])
        sov = gold_tree(parse_conllu(SOV)[0])
        self.assertNotEqual(svo.surface_order, sov.surface_order)
        self.assertNotEqual(svo.digest(), sov.digest())

    def test_nonprojective_dependency_tree_is_explicitly_outside_cfg_bridge(self):
        sentence = parse_conllu(NONPROJECTIVE)[0]
        self.assertFalse(is_projective(sentence))
        grammar = induce_grammar((sentence,))
        self.assertEqual(grammar.projective_sentences, 0)
        self.assertEqual(grammar.nonprojective_sentences, 1)

    def test_test_split_requires_explicit_protected_evaluator_before_hash_check(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "en_ewt-ud-test.conllu"
            path.write_text(TRAIN, encoding="utf-8")
            with self.assertRaisesRegex(UDCannotCheck, "protected"):
                verify_custody_file(path, "test")

    def test_clause_skeleton_is_order_sensitive(self):
        svo = clause_skeleton(parse_conllu(TRAIN)[0]).key()
        sov = clause_skeleton(parse_conllu(SOV)[0]).key()
        self.assertNotEqual(svo, sov)


if __name__ == "__main__":
    unittest.main()
