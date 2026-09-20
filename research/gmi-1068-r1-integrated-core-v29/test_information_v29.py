"""Fixed-interface exhaustive families and explicit missing-premise revivals."""
from itertools import product
import unittest
from support_v29 import information, oracle, check_report, exact
COVERAGE = {}
CODEC_COSTS = {"family_reports": []}
F = information.Family


class InformationTests(unittest.TestCase):
    def test_registered_ninety_families(self):
        CODEC_COSTS["family_reports"].clear()
        families = reports = decisions = full_decisions = 0
        recovered_source = recovered_restricted = recovered_full = 0
        for seed_width in (2,1):
            for entries in product((None,0,1),repeat=2*seed_width):
                seed = (entries[:seed_width],entries[seed_width:])
                source_rows = seed if seed_width == 2 else tuple(row*2 for row in seed)
                target_rows = oracle.mapped(seed,(1,0))
                source,target = F(2,2,2,source_rows),F(2,seed_width,2,target_rows)
                query_map = (0,1) if seed_width == 2 else (0,0)
                for codes in ((0,0),(0,1)):
                    result = check_report(self,source,target,query_map,(1,0),codes)
                    self.assertTrue(result['commutes']);self.assertTrue(result['output_injective'])
                    sizes = {}
                    for label,key,width in (('source','source_recovery',2),
                                            ('restricted','restricted_target_recovery',2),
                                            ('full','full_target_recovery',seed_width)):
                        rec = result[key];book = rec['response_codebook']
                        sizes[label] = [len(book),width,sum(len(row) for row in book),
                                        len(rec['response_labels']),
                                        None if rec['decoder'] is None else len(rec['decoder'])]
                    CODEC_COSTS['family_reports'].append({
                        'source_dimensions':[2,2,2],'target_dimensions':[2,seed_width,2],
                        'query_map':list(query_map),'output_map':[1,0],'codes':list(codes),
                        'attained_code_count':len(set(codes)),'recovery_sizes':sizes})
                    exact(self,result['source_recoverable'],result['restricted_target_recoverable'])
                    reports += 1;decisions += 2;full_decisions += 1
                    recovered_source += result['source_recoverable']
                    recovered_restricted += result['restricted_target_recoverable']
                    recovered_full += result['full_target_recoverable']
                families += 1
        self.assertEqual((families,reports,decisions,full_decisions),(90,180,360,180))
        COVERAGE.update(constructed_families=families,transport_reports=reports,
                        source_and_restricted_decisions=decisions,full_target_decisions=full_decisions,
                        recoverable_source_reports=recovered_source,
                        recoverable_restricted_reports=recovered_restricted,
                        recoverable_full_reports=recovered_full)

    def test_fixed_varying_and_missing_interface_controls(self):
        count = 0
        source,target = F(2,1,2,((0,),(1,))),F(2,1,2,((0,),(0,)))
        for model in range(2):
            single_source = F(1,1,2,(source.responses[model],))
            single_target = F(1,1,2,(target.responses[model],))
            result = check_report(self,single_source,single_target,(0,),
                                  tuple(x^model for x in range(2)),(0,))
            self.assertTrue(result['commutes']); count += 1
        self.assertFalse(oracle.attained_decoders((0,0),source.responses))
        self.assertTrue(oracle.attained_decoders((0,0),target.responses));count += 1
        retained = tuple(((0,0)[m],tuple(x^m for x in range(2))) for m in range(2))
        self.assertTrue(oracle.attained_decoders(retained,source.responses))
        retained_codes = tuple(tuple(dict.fromkeys(retained)).index(row) for row in retained)
        revival = information.attained_recovery(retained_codes,source.responses)
        exact(self,revival['recoverable'],True)
        exact(self,tuple(revival['response_codebook'][revival['decoder'][code]]
                         for code in retained_codes),source.responses)
        count += 1
        result = check_report(self,source,target,(0,),(0,0),(0,0))
        self.assertTrue(result['commutes']);self.assertFalse(result['output_injective'])
        self.assertFalse(result['source_recoverable']);self.assertTrue(result['restricted_target_recoverable']);count += 1
        source,target = F(2,1,2,((0,),(0,))),F(2,2,2,((0,0),(0,1)))
        result = check_report(self,source,target,(0,),(0,1),(0,0))
        self.assertTrue(result['restricted_target_recoverable']);self.assertFalse(result['full_target_recoverable']);count += 1
        result = check_report(self,F(2,1,2,((0,),(1,))),F(2,1,2,((0,),(0,))),
                              (0,),(0,1),(0,0))
        self.assertFalse(result['commutes']);count += 1
        empty_cases = ((F(0,2,2,()),F(0,2,2,()),(0,1),(1,0),()),
                       (F(2,0,2,((),())),F(2,0,2,((),())),(),(1,0),(0,0)),
                       (F(2,1,0,((None,),(None,))),F(2,1,0,((None,),(None,))),(0,),(),(0,0)))
        for args in empty_cases:
            result = check_report(self,*args)
            self.assertTrue(result['commutes']);self.assertTrue(result['source_recoverable']);count += 1
        COVERAGE['information_boundary_controls'] = count
