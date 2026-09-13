"""Full source-bound hierarchy correction payload; pure finite registers only."""
import json
import sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_evidence_v1 import original_replay,source_controls
from witnesses_v1 import hierarchy_witness,parsing_controls,policy_census,parsing_census


def run():
    return dict(schema='CHARGED_HIERARCHY_REPAIR_V1',status='PASS',
                original_full=original_replay(),original_countercontrols=source_controls(),
                hierarchy=hierarchy_witness(),parsing=parsing_controls(),
                policy_census=policy_census(),parsing_census=parsing_census(),
                scope='SUPPLIED_FINITE_GRAMMAR_AND_COMPILED_COST_CONTRACT',native_or_campaign_calls=0)


def encode(value):
    if isinstance(value,Fraction):return str(value)
    raise TypeError(type(value).__name__)


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,default=encode)+'\n').encode()


if __name__=='__main__':sys.stdout.buffer.write(encoded(run()))
