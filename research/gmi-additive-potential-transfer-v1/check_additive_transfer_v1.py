import json
import sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
from countable_models_v1 import polynomial_controls,envelope_controls
from finite_witnesses_v1 import history_control,selected_control,terminal_control

def run():
    return dict(schema="APT_STATIC_RECEIPT_V1",status="PASS",
                scope="exact supplied arithmetic; analytic countable proofs are separate",
                polynomial_revival=polynomial_controls(),
                nonvanishing_envelope=envelope_controls(),
                common_histories=history_control(),selection=selected_control(),
                terminal_identity=terminal_control())

def encoded(value):
    return json.dumps(value,default=lambda x:str(x) if isinstance(x,F) else x,
                      sort_keys=True,indent=2)+"\n"

if __name__=="__main__":
    print(encoded(run()),end="")
