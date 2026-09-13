"""Full original records plus repaired exact controls, with no projection."""
import json
import sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_evidence_v1 import verify_sources,original
from witnesses_v1 import prefix_checks,concept_checks,future_control


def run():
    source=verify_sources();old=original(source)
    return dict(schema='GMI_CONCEPT_SUBGOAL_REPAIR_V1',status='PASS',original=old,
                prefix=prefix_checks(old),concept=concept_checks(),future=future_control(),
                native_or_protected_campaign_calls=0)


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,default=lambda x:
                      {'numerator':x.numerator,'denominator':x.denominator}
                      if isinstance(x,Fraction) else (_ for _ in ()).throw(TypeError(type(x))),
                      allow_nan=False)+'\n').encode()


if __name__=='__main__':sys.stdout.buffer.write(encoded(run()))
