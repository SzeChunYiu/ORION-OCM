"""Real certificates first; malformed descendants and coupled semantic corruption."""
from copy import deepcopy
from dataclasses import replace
import unittest
from hostile_cases_v29 import changed, foreign, malformed_cases
from support_v29 import adapter, fixture, core, named, presentation, information, oracle, check_report
COVERAGE = {}


class HostileTests(unittest.TestCase):
    def test_inputs_and_returned_certificates(self):
        malformed = 0
        for fn,args in malformed_cases():
            with self.subTest(function=fn.__name__,args=repr(args)[:100]),self.assertRaises(ValueError):fn(*args)
            malformed += 1
        category,mapping = fixture(); good = presentation.dag_presentation(mapping)
        self.assertTrue(presentation.verify_presentation(mapping,good))
        bad = [replace(good,paths=good.paths[:-1]),
               replace(good,class_of=(0,)*len(good.class_of)),
               replace(good,representatives=tuple(reversed(good.representatives))),
               replace(good,generates=False),replace(good,generates=1),
               replace(good,category=foreign(good.category)),
               replace(good,category=changed(good.category,'table',foreign(good.category.table))),
               replace(good,lower=foreign(good.lower)),
               replace(good,quote=foreign(good.quote)),
               replace(good,lower=changed(good.lower,'arrow_map',tuple(reversed(good.lower.arrow_map)))),
               replace(good,category=changed(good.category,'identities',(0,0,0))),
               replace(good,category=changed(good.category,'source',tuple(reversed(good.category.source)))),
               replace(good,category=changed(good.category,'table',core.partial.Table(tuple((None,)*6 for _ in range(6)))))]
        split = list(good.class_of)
        split[good.paths.index((0,(2,)))] = max(split)+1
        bad.append(replace(good,class_of=tuple(split)))
        semantic = 0
        for result in bad:
            with self.assertRaises(ValueError):presentation.verify_presentation(mapping,result)
            semantic += 1
        current = adapter();named.checked_adapter(current)
        wrong_named = changed(current.named,'identities',tuple(reversed(current.named.identities)))
        bad = [changed(current,'named',foreign(current.named)),
               changed(current,'named',wrong_named),changed(current,'category',foreign(current.category)),
               changed(current,'local_to_presented',tuple(reversed(current.local_to_presented))),
               changed(current,'presented_to_local',tuple(reversed(current.presented_to_local))),
               changed(current,'ambient_to_local',(0,)*7),
               changed(current,'named',changed(current.named,'model',foreign(current.named.model))),
               changed(current,'named',changed(current.named,'model',
                       changed(current.named.model,'table',foreign(current.named.model.table))))]
        for result in bad:
            with self.assertRaises(ValueError):named.checked_adapter(result)
            semantic += 1
        F = information.Family;source = F(2,1,2,((0,),(1,)));target = F(2,1,2,((1,),(0,)))
        args = (source,target,(0,),(1,0),(0,1))
        good_report = check_report(self,*args)
        report_mutations = []
        for key in ('commutes','output_injective','source_recoverable','restricted_target_recoverable','full_target_recoverable'):
            for replacement in (False,1):
                result = deepcopy(good_report);result[key]=replacement;report_mutations.append(result)
        for key in ('source_recovery','restricted_target_recovery','full_target_recovery'):
            for field,value in (('decoder',None),('decoder',{0:0,1:0}),('code_labels',(0,0)),
                                ('response_labels',(0,0)),('response_codebook',((None,),(None,))),('recoverable',1)):
                result=deepcopy(good_report);result[key][field]=value;report_mutations.append(result)
        result=deepcopy(good_report);result['extra']=True;report_mutations.append(result)
        result=deepcopy(good_report);del result['full_target_recovery'];report_mutations.append(result)
        for result in report_mutations:
            with self.assertRaises(ValueError):information.verify_transport_report(*args,result)
            semantic += 1
        fake_observations = ((0,),(0,))
        with self.assertRaises(ValueError):oracle.certify(fake_observations,source.responses)
        semantic += 1
        COVERAGE.update(malformed_input_rejections=malformed,semantic_certificate_rejections=semantic,
                        valid_certificate_baselines=3,foreign_nested_certificate_rejections=8)
