from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('grammar_bias_v1_under_test', ROOT / 'grammar_bias_v1.py')
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('cannot load grammar_bias_v1')
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class TestGrammarBiasV1(unittest.TestCase):
    def test_freeze_and_parent_pins(self):
        self.assertEqual(M.FREEZE_COMMIT, 'f5195a8ae04cce0d96d0e005f5cd39c38a4717ef')
        self.assertEqual(M.PARENT_MANIFEST_BLOB, 'cfe890b276cef0bdb2424877de878b9173547cf2')
        self.assertEqual(M.PARENT_RECEIPT_BLOB, '5d2948b9c04c84a46f6625e043753a489895478f')

    def test_instruction_option_counts(self):
        self.assertEqual(len(M.instruction_options(('L0',))), 5)
        self.assertEqual(len(M.instruction_options(('L0','L1'))), 11)

    def test_presentation_census(self):
        p = M.enumerate_presentations()
        self.assertEqual(len(p), 126)
        self.assertEqual(sum(json.loads(k)[0] == 1 for k in p), 5)
        self.assertEqual(sum(json.loads(k)[0] == 2 for k in p), 121)

    def test_semantic_signature_is_protected_only(self):
        p = M.PARENT.Program(('r',),'L0',{'L0':M.PARENT.Halt()})
        self.assertEqual(M.semantic_signature(p), (('HALTED',()),('HALTED',()),('HALTED',())))

    def test_graph_edge_count(self):
        p=M.enumerate_presentations(); a=M.build_adjacency(p)
        self.assertEqual(sum(map(len,a.values()))//2,1275)

    def test_bfs_wave_agree(self):
        p=M.enumerate_presentations(); a=M.build_adjacency(p); s=M.start_node(p)
        self.assertEqual(M.bfs_distances(a,(s,)), M.wave_distances(a,(s,)))

    def test_presentation_distance_histogram(self):
        c=M.registered_census()
        self.assertEqual(c['presentation_distance_histogram'], {'0':1,'1':15,'2':110})
        self.assertTrue(c['all_presentations_reachable'])

    def test_semantic_class_count(self):
        self.assertEqual(M.registered_census()['semantic_class_count'],18)

    def test_multiplicity_histogram(self):
        self.assertEqual(M.registered_census()['class_multiplicity_histogram'], {'1':10,'2':2,'3':1,'4':1,'14':1,'15':1,'23':1,'53':1})

    def test_shortest_length_histogram(self):
        self.assertEqual(M.registered_census()['class_shortest_length_histogram'], {'1':4,'2':14})

    def test_class_distance_histogram(self):
        self.assertEqual(M.registered_census()['class_distance_histogram'], {'0':1,'1':3,'2':14})

    def test_reachable_class_counts(self):
        self.assertEqual(M.registered_census()['reachable_class_count_by_radius'], {'0':1,'1':4,'2':18})

    def test_syntax_mass_normalizes_B1(self):
        rows=M.registered_census()['class_rows']
        nums=[]
        for r in rows:
            n,d=map(int,r['Q_B1'].split('/')); nums.append((n,d))
        from fractions import Fraction
        self.assertEqual(sum((Fraction(n,d) for n,d in nums),Fraction(0,1)), Fraction(1,1))

    def test_syntax_mass_normalizes_B2(self):
        rows=M.registered_census()['class_rows']
        from fractions import Fraction
        total=sum((Fraction(*map(int,r['Q_B2'].split('/'))) for r in rows),Fraction(0,1))
        self.assertEqual(total,Fraction(1,1))

    def test_all_24_isometric_remints(self):
        cert=M.remint_exhaustive_certificate()
        self.assertEqual(cert['permutations'],24)
        self.assertEqual(cert['certified'],24)
        self.assertEqual(cert['certification_failures'],0)
        self.assertEqual(cert['invariant_failures'],0)

    def test_non_bijective_remint_rejected(self):
        self.assertEqual(M.hostile_remint_results()['non_bijective'],'NON_BIJECTIVE_NODE_MAP')

    def test_semantic_corruption_rejected(self):
        self.assertEqual(M.hostile_remint_results()['semantic'],'SEMANTIC_MAP_CORRUPTION')

    def test_length_corruption_rejected(self):
        self.assertEqual(M.hostile_remint_results()['length'],'DESCRIPTION_LENGTH_CORRUPTION')

    def test_edge_corruption_rejected(self):
        self.assertEqual(M.hostile_remint_results()['edge'],'EDGE_CORRUPTION')

    def test_start_corruption_rejected(self):
        self.assertEqual(M.hostile_remint_results()['start'],'START_SET_CORRUPTION')

    def test_semantic_only_map_not_isometric(self):
        self.assertEqual(M.hostile_remint_results()['semantic_only'],'DESCRIPTION_LENGTH_CORRUPTION')

    def test_same_semantics_hostile_reverses_selection(self):
        ga,gb=M.nonisometric_hostile_pair()
        self.assertEqual(set(ga.semantic.values()),set(gb.semantic.values()))
        self.assertEqual(M.selection(ga,('A','B')),'A')
        self.assertEqual(M.selection(gb,('A','B')),'B')

    def test_same_semantics_hostile_changes_bias(self):
        ga,gb=M.nonisometric_hostile_pair()
        a=M.grammar_bias_rows(ga); b=M.grammar_bias_rows(gb)
        self.assertEqual((a['A']['L'],a['A']['d']),(1,1))
        self.assertEqual((a['B']['L'],a['B']['d']),(2,2))
        self.assertEqual((b['A']['L'],b['A']['d']),(2,2))
        self.assertEqual((b['B']['L'],b['B']['d']),(1,1))

    def test_invalid_grammar_fails_closed(self):
        g=M.FiniteGrammar(nodes=('a',),semantic={},length={'a':0},edges=frozenset(),starts=frozenset({'a'}))
        with self.assertRaises(ValueError): M.grammar_bias_rows(g)

    def test_empty_selection_rejected(self):
        with self.assertRaises(ValueError): M.selection(M.remint_fixture(),())

    def test_missing_semantic_candidate_rejected(self):
        with self.assertRaises(ValueError): M.selection(M.remint_fixture(),('NOPE',))

    def test_receipt_green(self):
        r=M.build_receipt()
        self.assertEqual(r['terminal'],'GMI_833_G0_GRAMMAR_BIAS_V1_ALL_GREEN')
        self.assertEqual(r['claim_ceiling'],M.CLAIM_CEILING)

    def test_no_float_evidence(self):
        self.assertTrue(M._no_floats(M.build_receipt()))

    def test_committed_receipt_byte_exact(self):
        committed=(ROOT/'RESULT_V1.json').read_text()
        self.assertEqual(M.canonical_json(M.build_receipt()),committed)

    def test_independent_oracle_matches_summary(self):
        cp=subprocess.run([sys.executable,'-I','-B',str(ROOT/'independent_oracle_v1.py')],check=True,text=True,capture_output=True)
        o=json.loads(cp.stdout); r=M.build_receipt()['registered_slice']
        for key in ('presentation_count','semantic_class_count','undirected_edge_count','presentation_distance_histogram','class_multiplicity_histogram','class_shortest_length_histogram','class_distance_histogram'):
            self.assertEqual(o[key],r[key])
        self.assertEqual(o['terminal'],'GREEN')

    def test_forbidden_promotions_are_exact(self):
        self.assertEqual(len(M.FORBIDDEN_PROMOTIONS),8)
        self.assertIn('COMPLETE_GMI',M.FORBIDDEN_PROMOTIONS)
        self.assertNotIn('GMI_FINITE_GRAMMAR_BIAS_AND_REMINT_BOUNDARY_AT_REGISTERED_G0_SCOPE',M.FORBIDDEN_PROMOTIONS)


if __name__=='__main__':
    unittest.main()
