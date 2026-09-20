"""Current authority uses actual scientific evidence, never submitted totals."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ledger_test_support_v16',HERE/'ledger_test_support_v16.py')
support=importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
COVERAGE={}


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=support.contract()
        cls.receipt,cls.review=support.actual_evidence()
        cls.ledger=support.attested(cls.contract,cls.receipt,cls.review)

    def check(self,ledger,contract=None,predecessor=None):
        return support.evidence.validate_evidence(ledger,contract or self.contract,
                                                 self.receipt,self.review,predecessor)

    def test_actual_evidence_and_retraction(self):
        original=json.loads((HERE/'AMENDMENT_LEDGER_V16.json').read_text())
        result=self.check(original)
        self.assertEqual(result['original_fulfilled'],18)
        self.assertEqual(result['original_unresolved'],204)
        self.assertEqual(result['refuted_reading_with_verified_active_replacement'],2)
        self.assertEqual(result['active_unresolved'],202)
        self.assertEqual(result['overall_closure'],'OPEN')
        self.assertIs(result['scientific_truth_certified'],False)
        self.assertEqual(self.check(self.ledger),result)
        withdrawn=support.successor(self.ledger)
        support.retract(withdrawn,'attest-0')
        reduced=self.check(withdrawn,predecessor=self.ledger)
        self.assertEqual(reduced['active_unresolved'],203)
        self.assertEqual(reduced['original_unresolved'],204)
        self.assertEqual(withdrawn['targets'],self.ledger['targets'])
        restored=support.successor(withdrawn)
        revision=self.contract['permitted_revisions'][0]
        support.append(restored,'ATTEST','new-attestation',support.attestation(revision,self.receipt,self.review))
        self.assertEqual(self.check(restored,predecessor=withdrawn)['active_unresolved'],202)
        COVERAGE['valid_evidence_controls']=4

    def test_attestation_mutations(self):
        bads=[]
        for field,value in (('science_sha256','0'*64),('review_sha256','0'*64),
                            ('statement_ids',[]),('kind','ORIGINAL_CLOSED'),('verdict','PASS'),
                            ('revision_id','unknown'),('science_sha256',True),('review_sha256','')):
            bad=deepcopy(self.ledger);bad['events'][2]['payload'][field]=value;bads.append(support.rebind(bad))
        bad=deepcopy(self.ledger)
        support.append(bad,'ATTEST','ambiguous',bad['events'][2]['payload']);bads.append(bad)
        for aid in ('unknown','revision-0'):
            bad=deepcopy(self.ledger);support.retract(bad,aid);bads.append(bad)
        bad=deepcopy(self.ledger);support.retract(bad,'attest-0');support.retract(bad,'attest-0','twice');bads.append(bad)
        for field,value in (('reason',''),('evidence_sha256','invalid')):
            bad=deepcopy(self.ledger);support.retract(bad,'attest-0');bad['events'][-1]['payload'][field]=value;bads.append(bad)
        for bad in bads:
            with self.assertRaises((ValueError,TypeError)):
                self.check(bad)
        # Coupled receipt+attestation hashes cannot alter a contracted statement.
        coupled=0
        for field,value in (('status','PENDING'),('contract',{'scope':'all possible intelligence'})):
            receipt=deepcopy(self.receipt)
            sid=self.contract['permitted_revisions'][0]['required_statements'][0]
            receipt['statements'][sid][field]=value
            ledger=support.attested(self.contract,receipt,self.review)
            with self.assertRaises(ValueError):
                support.evidence.validate_evidence(ledger,self.contract,receipt,self.review)
            coupled+=1
        COVERAGE.update(attestation_mutation_rejections=len(bads),coupled_evidence_rejections=coupled)

    def test_failed_successor_and_dependencies(self):
        count=0
        first=self.contract['permitted_revisions'][0]
        contract=deepcopy(self.contract)
        future=deepcopy(first)
        future.update(revision_id=first['revision_id'].replace('@r1','@r2'),supersedes=first['revision_id'])
        contract['permitted_revisions'].append(future)
        for verdict in (None,'FAILED','CANNOT_CHECK','VERIFIED'):
            ledger=support.successor(self.ledger)
            support.append(ledger,'REVISION','future-revision',future)
            if verdict:
                support.append(ledger,'ATTEST','future-evidence',support.attestation(future,self.receipt,self.review,verdict))
            result=self.check(ledger,contract,self.ledger)
            self.assertEqual(result['active_unresolved'],202 if verdict=='VERIFIED' else 203)
            self.assertNotIn(first['revision_id'],result['qualified_revision_ids'])
            if verdict=='VERIFIED':
                support.retract(ledger,'future-evidence','withdraw-future')
                self.assertEqual(self.check(ledger,contract,self.ledger)['active_unresolved'],203)
            count+=1
        # Inactive historical evidence is retained, but never rebound to the latest receipt.
        ledger=support.successor(self.ledger)
        support.append(ledger,'REVISION','future-revision',future)
        ledger['events'][2]['payload']['science_sha256']='2'*64
        support.rebind(ledger)
        # This independently trusted predecessor carries the same historical binding.
        predecessor=deepcopy(self.ledger);predecessor['events'][2]['payload']['science_sha256']='2'*64
        support.rebind(predecessor)
        ledger['previous_ledger']={'sha256':support.digest(predecessor),'event_count':len(predecessor['events'])}
        self.assertEqual(self.check(ledger,contract,predecessor)['active_unresolved'],203)
        # A dependent replacement loses authority when its exact dependency is superseded.
        dependent=deepcopy(self.contract)
        dependent['permitted_revisions'][1]['dependency_revision_ids']=[first['revision_id']]
        base=support.attested(dependent,self.receipt,self.review)
        self.assertEqual(self.check(base,dependent)['active_unresolved'],202)
        dependent['permitted_revisions'].append(future)
        stale=support.successor(base);support.append(stale,'REVISION','supersedes-dependency',future)
        support.append(stale,'ATTEST','verified-new-dependency',support.attestation(future,self.receipt,self.review))
        result=self.check(stale,dependent,base)
        self.assertEqual(result['active_unresolved'],203)
        self.assertNotIn(dependent['permitted_revisions'][1]['revision_id'],result['qualified_revision_ids'])
        withdrawn=support.successor(base);support.retract(withdrawn,'attest-0')
        self.assertEqual(self.check(withdrawn,dependent,base)['active_unresolved'],204)
        COVERAGE.update(successor_authority_controls=count+1,dependency_authority_controls=3)


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
