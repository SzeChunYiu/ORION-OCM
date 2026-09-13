"""Deterministic full payload for the supplied finite witnesses."""
import json
import sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
from transfer_witnesses_v1 import (proper_error,trap_and_rescue,history_control,
                                  selected_policy_control,terminal_control,countable_control,
                                  observation_control,certification_control,data_average_control)

def run():
    return dict(schema="WTT_STATIC_RECEIPT_V1", status="PASS",
                scope="exact supplied arithmetic; no ecology or general-quantifier enumeration",
                trap_and_rescue=trap_and_rescue(),
                proper_error_sequence=[proper_error(e) for e in (F(1,2),F(1,4),F(1,8))],
                common_histories=history_control(),
                data_selected_policy=selected_policy_control(),
                terminal_identity=terminal_control(),
                complete_observation=observation_control(),
                coverage_versus_certification=certification_control(),
                data_averaged_integrability=data_average_control(),
                countable_symbolic_control=countable_control())

def encoded(value):
    return json.dumps(value,default=lambda x:str(x) if isinstance(x,F) else x,
                      sort_keys=True,indent=2)+"\n"

if __name__ == "__main__":
    print(encoded(run()),end="")
