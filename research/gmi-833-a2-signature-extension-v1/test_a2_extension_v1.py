import unittest

import a2_extension_v1 as x


class FamilyDefinitionTests(unittest.TestCase):
    def test_nine_families_three_existing_six_new(self):
        self.assertEqual(len(x.EXISTING_FAMILIES), 3)
        self.assertEqual(len(x.NEW_FAMILIES), 6)
        self.assertEqual(len(x.ALL_FAMILIES), 9)

    def test_every_d2_class_mapped_to_a_family(self):
        self.assertEqual(len(x.D2_MAPPING), 30)
        for cls, fam in x.D2_MAPPING.items():
            self.assertIn(fam, x.ALL_FAMILIES)

    def test_new_family_conjunct_counts(self):
        # each new family requires >= 2 conjuncts (no single-feature fire)
        for fam, req in x.NEW_FAMILIES.items():
            self.assertGreaterEqual(len(req), 2, fam)


class DerivationTests(unittest.TestCase):
    def setUp(self):
        self.core = x.load_audit_core()

    def test_p1_known_same_recall(self):
        for fam, (nm, body) in x.PLANT_BODIES.items():
            sig = x.derive_signature(nm, body)
            findings, _ = x.match_families(self.core, [(nm, sig)], x.NEW_FAMILIES)
            self.assertTrue(any(f['fingerprint'] == fam for f in findings),
                            f'{fam}: sig={sig} findings={findings}')

    def test_p2_neutral_rename_recall(self):
        for fam, (nm, body) in x.PLANT_BODIES.items():
            neutral = x.NEUTRAL_NAMES[nm]
            sig = x.derive_signature(neutral, body.replace('def ' + nm, 'def ' + neutral))
            findings, _ = x.match_families(self.core, [(neutral, sig)], x.NEW_FAMILIES)
            self.assertTrue(any(f['fingerprint'] == fam for f in findings),
                            f'{fam} renamed {neutral}: sig={sig} findings={findings}')

    def test_p3_v2_basis_clean(self):
        findings, term = x.match_families(self.core, x.CLEAN_V2_BASIS, x.ALL_FAMILIES)
        self.assertEqual(term, 'CLEAN_AT_REGISTERED_AUDIT_SCOPE')
        self.assertEqual(findings, [])

    def test_p6_existing_family_regression_controls_fire(self):
        controls = [
            ('mix', {'arity': 2, 'types': ['weighted_aggregate'], 'state_access': 'none', 'locality': 'global',
                     'addressability': False, 'content_dependent_routing': True, 'parameter_sharing': 'none',
                     'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(n^2)'}),
            ('local_apply', {'arity': 2, 'types': ['arithmetic'], 'state_access': 'none', 'locality': 'neighborhood',
                             'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': True,
                             'recurrence': False, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(n)'}),
            ('cell_step', {'arity': 2, 'types': ['state_io'], 'state_access': 'read_write', 'locality': 'local',
                           'addressability': False, 'content_dependent_routing': False, 'parameter_sharing': True,
                           'recurrence': True, 'stochasticity': False, 'verifier_access': False, 'resource_class': 'O(n)'}),
        ]
        findings, _ = x.match_families(self.core, controls, x.EXISTING_FAMILIES)
        fired = {f['primitive'] for f in findings}
        self.assertEqual(fired, {'mix', 'local_apply', 'cell_step'})

    def test_derivation_is_name_blind(self):
        # identical bodies under different names derive identical signatures
        _, body = x.PLANT_BODIES['stochastic_belief_update']
        a = x.derive_signature('update_beliefs', body)
        b = x.derive_signature('zzz', body.replace('def update_beliefs', 'def zzz'))
        self.assertEqual(a, b)

    def test_clean_decomposed_body_stays_clean(self):
        body = ('def op_add(a, b):\n'
                '    return a + b\n')
        sig = x.derive_signature('op_add', body)
        findings, _ = x.match_families(self.core, [('op_add', sig)], x.ALL_FAMILIES)
        self.assertEqual(findings, [])
        self.assertEqual(sig['locality'], 'local')
        self.assertEqual(sig['state_access'], 'none')


if __name__ == '__main__':
    unittest.main()
