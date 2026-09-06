"""Engineering hostiles; these are not Lean or scientific-success receipts."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from substrate import (Refusal, extract_wrapper, import_header, build_graph,
                       stage_challenge, digest_json, validate_public, PINS)


def wrapper(key='a', signature='(P : Prop) : P → P'):
    return ('import Mathlib\nimport P2M.Util\nimport P2M.Sol.S_' + key +
            '\nset_option autoImplicit false\ntheorem T_' + key + ' ' + signature +
            ' := by p2m_exact_reverting @_root_.P2MW.S_' + key + '.solution\n')


def fixture():
    return {'Theorems/Thm_a.lean': wrapper(),
            'P2M/Sol/S_a.lean': 'import Mathlib\ntheorem solution := secret_a\n',
            'Theorems/Thm_b.lean': wrapper('b'),
            'P2M/Sol/S_b.lean': 'import Mathlib\nimport Theorems.Thm_a\ntheorem solution := secret_b\n'}


class SubstrateHostiles(unittest.TestCase):
    def test_multiline_signature_and_nested_comments(self):
        text = wrapper(signature='(P : Prop)\n /- outer /- inner -/ secret -/ :\n P → P')
        row = extract_wrapper(text, 'a')
        self.assertIn('P → P', row['signature'])
        self.assertNotIn('secret', row['signature'])
        self.assertNotIn('solution', row['signature'])

    def test_nested_assignment_is_not_theorem_body(self):
        with self.assertRaises(Refusal):
            extract_wrapper(wrapper(signature='(P : Prop := True) : P'), 'a')

    def test_unterminated_comment_fails(self):
        with self.assertRaises(Refusal): import_header('import Mathlib /- unfinished')

    def test_wrapper_import_identity_mismatch(self):
        with self.assertRaises(Refusal): extract_wrapper(wrapper('a'), 'b')

    def test_unsupported_preamble_not_silently_discarded(self):
        with self.assertRaises(Refusal): extract_wrapper('axiom forged : False\n' + wrapper(), 'a')

    def test_second_declaration_not_silently_discarded(self):
        with self.assertRaises(Refusal): extract_wrapper(wrapper() + 'axiom hidden : False\n', 'a')

    def test_imports_are_not_found_in_comments_or_proof_strings(self):
        imports = import_header('/- import Theorems.Thm_leak -/\nimport Mathlib\ntheorem x : True := by\n  exact True.intro\n')
        self.assertEqual(imports, ('Mathlib',))

    def test_graph_direction_and_exact_pairing(self):
        graph = build_graph(fixture(), expected_count=2)
        self.assertEqual(graph['nodes']['b']['dependencies'], ['a'])
        self.assertEqual(graph['topological_order'], ['a', 'b'])
        self.assertEqual(graph['count'], 2)

    def test_count_mismatch_refused(self):
        with self.assertRaisesRegex(Refusal, 'SOURCE_COVERAGE'):
            build_graph(fixture(), expected_count=29511)

    def test_missing_pair_refused(self):
        f = fixture(); del f['Theorems/Thm_a.lean']
        with self.assertRaises(Refusal): build_graph(f, expected_count=2)

    def test_dangling_dependency_refused(self):
        f = fixture(); f['P2M/Sol/S_a.lean'] = 'import Theorems.Thm_missing\n'
        with self.assertRaises(Refusal): build_graph(f, expected_count=2)

    def test_cycle_refused(self):
        f = fixture(); f['P2M/Sol/S_a.lean'] = 'import Theorems.Thm_b\n'
        with self.assertRaisesRegex(Refusal, 'CYCLE'): build_graph(f, expected_count=2)

    def test_hidden_proofs_and_edges_not_in_public_package(self):
        graph = build_graph(fixture(), expected_count=2)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pub, private = stage_challenge(graph, ['a','b'], 'b', 'R3', root/'pub', root/'private')
            text = json.dumps(pub)
            for forbidden in ('secret_', 'dependencies', 'P2M', 'solution_sha256', 'topological_order'):
                self.assertNotIn(forbidden, text)
            self.assertEqual(private['nodes']['b']['dependencies'], ['a'])
            self.assertEqual(pub['status'], 'STAGED_NOT_EXECUTABLE')
            self.assertEqual(set(p.name for p in (root/'pub').iterdir()), {'PUBLIC.json'})

    def test_overlap_of_private_and_public_refused(self):
        graph = build_graph(fixture(), expected_count=2)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(Refusal): stage_challenge(graph, ['b'], 'b', 'R2', Path(tmp)/'a', Path(tmp)/'a/private')

    def test_existing_destination_not_overwritten(self):
        graph = build_graph(fixture(), expected_count=2)
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp); (r/'pub').mkdir()
            with self.assertRaises(Refusal): stage_challenge(graph, ['b'], 'b', 'R2', r/'pub', r/'private')

    def test_public_extra_field_fails_closed(self):
        graph=build_graph(fixture(),expected_count=2)
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp); pub,_=stage_challenge(graph,['b'],'b','R2',r/'pub',r/'private')
            pub['hidden_proof']='answer'
            with self.assertRaises(Refusal): validate_public(pub)

    def test_changed_environment_identity_refused(self):
        graph=build_graph(fixture(),expected_count=2)
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp); pub,_=stage_challenge(graph,['b'],'b','R2',r/'pub',r/'private')
            pub['environment']['lean']='4.19.0'
            with self.assertRaises(Refusal): validate_public(pub)

    def test_canonical_hash_rejects_nan(self):
        with self.assertRaises(ValueError): digest_json({'cost': float('nan')})

class AdditionalSchemaHostiles(unittest.TestCase):
    def test_reject_invalid_schema_budget_and_row_types(self):
        # Build through the production constructor before hostile mutation.
        files={"Theorems/Thm_A.lean": wrapper('A'),"P2M/Sol/S_A.lean":"import Mathlib\nnamespace P2MW.S_A\n"}
        graph=build_graph(files,expected_count=1)
        with tempfile.TemporaryDirectory() as d:
            public,_=stage_challenge(graph,['A'],'A','R2',Path(d)/'public',Path(d)/'private')
        mutations=[('schema','invented'),('budget',{'proof_state_expansions':True,'checker_calls':16,'wall_seconds':60}),
                   ('budget',{'proof_state_expansions':-1,'checker_calls':16,'wall_seconds':60}),
                   ('obligations',{'not':'a list'})]
        for key,value in mutations:
            with self.subTest(key=key,value=value):
                changed=copy.deepcopy(public);changed[key]=value
                with self.assertRaises(Refusal):validate_public(changed)

if __name__ == '__main__': unittest.main()
