"""Malformed inputs must fail before any early return or filtering."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core_v22 as core
import execution_v22 as e
import contexts_v22 as c
import families_v22 as f
COVERAGE={}


class HostileTests(unittest.TestCase):
    def test_malformed(self):
        live=core.LegacyMachine((0,),(((0,0,0),),))
        dead=core.LegacyMachine((0,),((None,),))
        spec=core.PermissionMachine(live,2,(((0,),),))
        absent=core.PermissionMachine(dead,2,((None,),))
        context=core.Context(1,1,(False,),(True,),(0,),((True,),))
        roster=((0,(0,)),); selected=()
        checks=[]
        bad_sets=[None,[],{},'0',(True,),(0.0,),(-1,),(2,),(0,0)]
        for q in (True,False,1.0,-1,None,'2'):
            checks.append(lambda q=q:core.PermissionMachine(live,q,(((),),)))
            checks.append(lambda q=q:f.survivors((),(),q))
        for requirements in (None,[],(),((),),([()],),((None,),),(((True,),),),(((0,0),),),(((2,),),)):
            checks.append(lambda r=requirements:core.PermissionMachine(live,2,r))
        checks.extend([lambda:core.PermissionMachine(dead,2,(((),),)),lambda:core.PermissionMachine(None,2,((None,),))])
        for bad in (None,live,object()):
            checks.extend([lambda b=bad:e.gate(b,()),lambda b=bad:e.support(b,0,())])
        for enabled in bad_sets:
            checks.extend([lambda x=enabled:e.gate(spec,x),
                           lambda x=enabled:c.restricted_context(absent,x,context,roster,())])
        for state in (True,0.0,-1,1,None):checks.append(lambda x=state:e.support(absent,x,()))
        for word in (None,[],(True,),(0.0,),(-1,),(1,),(0,1),(0,True),(0,None)):
            checks.append(lambda x=word:e.support(absent,0,x))
            checks.append(lambda x=word:c.target_witnesses(absent,context,((0,x),),(),()))
        for histories in (None,[],(),((0,),),((True,()),),((0,[]),),((0,(0,)),(0,(0,)))):
            checks.append(lambda x=histories:c.target_witnesses(spec,context,x,(),()))
        two=core.Context(2,1,(False,False),(True,True),(0,0),((True,),))
        checks.append(lambda:c.target_witnesses(spec,two,((0,(0,)),(0,(0,))),(),()))
        for bad in bad_sets:
            checks.append(lambda x=bad:c.target_witnesses(spec,context,roster,x,()))
            checks.append(lambda x=bad:c.target_witnesses(spec,context,roster,(),x))
        bad_records=[None,[],((0,),),((True,()),),((0.0,()),),((-1,()),),((0,()),(0,(0,))),((0,[]),),((0,(0,0)),),((0,(True,)),),((0,(2,)),)]
        for records in bad_records:
            checks.extend([lambda r=records:f.survivors(r,(),2),lambda r=records:f.minimal_additions(r,(),(),2),
                lambda r=records:f.minimal_blockers(r,(),2),lambda r=records:f.blocks(r,(),(),2),
                lambda r=records:f.blocker_certificate(r,(),(),2),lambda r=records:f.minimal_supports(r,2)])
        for bad in bad_sets:
            checks.extend([lambda x=bad:f.survivors((),x,2),lambda x=bad:f.minimal_additions((),x,(0,1),2),
                lambda x=bad:f.minimal_additions((),(),x,2),lambda x=bad:f.minimal_blockers((),x,2),
                lambda x=bad:f.blocks((),(0,1),x,2),lambda x=bad:f.blocker_certificate((),(0,1),x,2)])
        checks.extend([lambda:f.minimal_additions((),(1,),(0,),2),lambda:f.blocks((),(0,),(1,),2),
                       lambda:f.blocker_certificate((),(0,),(1,),2)])
        unused=core.LegacyMachine((0,1),(((0,0,0),),((0,0,1),)))
        checks.extend([lambda:core.PermissionMachine(unused,2,(((),),((2,),))),
                       lambda:core.PermissionMachine(unused,2,(((),),(None,)))])
        empty=core.Context(0,0,(),(),(),())
        checks.extend([lambda:c.target_witnesses(absent,empty,(),(),(0,)),
                       lambda:c.restricted_context(absent,(2,),empty,(),())])
        count=0
        for index,check in enumerate(checks):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):check()
                count+=1
        COVERAGE['malformed_rejections']=count

    def test_result_corruptions(self):
        records=((5,(0,)),(7,(1,)))
        cert=f.blocker_certificate(records,(0,1),(0,1),2)
        def valid(candidate):
            return (type(candidate) is tuple and len(candidate)==2 and
                    {x[0] for x in candidate}=={0,1} and
                    all(any(i==h and set(s)&{0,1}=={b} for i,s in records) for b,h in candidate))
        self.assertTrue(valid(cert));count=0
        for mutant in ((),((0,5),),((0,7),(1,5)),((0,5),(1,99)),((0,5),(0,5))):
            self.assertFalse(valid(mutant));count+=1
        self.assertIsNone(f.blocker_certificate(records,(0,1),(0,),2))
        self.assertIsNone(f.blocker_certificate(records,(0,1),(),2))
        COVERAGE['corrupt_private_certificates']=count


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
