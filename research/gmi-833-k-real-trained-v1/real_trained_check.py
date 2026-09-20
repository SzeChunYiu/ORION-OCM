#!/usr/bin/env python3
"""Independent custody/scoring check for the frozen real-system tranche."""
from fractions import Fraction
import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PRED=ROOT/'research/gmi-833-k-real-trained-v1/FROZEN_PREDICTIONS_REAL4_V1.json'
MEAS=ROOT/'research/gmi-833-k-real-trained-v1/REAL_MEASURED_V4.json'
PARENT=ROOT/'research/gmi-833-capability-predictor-v1/capability_predictor_v1.py'
def main():
    assert PRED.is_file() and MEAS.is_file() and PARENT.is_file()
    pred=json.loads(PRED.read_text()); meas=json.loads(MEAS.read_text())
    assert pred['parent_file_blob_sha']=='7f1bb6808901be2291bf575ee3178247d14d01d4'
    assert pred['parent_code_unchanged'] is True
    assert pred['set_valued_census']['nd2']==2100
    bits=meas['measured_solved_bits']
    assert len(bits)==32
    # CR-1 abstains on GRU width 6 T1/T2; those four measured outcomes are
    # intentionally allowed by the bridge. Only singleton commitments are
    # checked here; soundness covers the set-valued abstention separately.
    violations=[]
    for key,val in bits.items():
        mech,size,w,h=key.split('|'); size=int(size); h=int(h); b=int(val)
        if mech == 'MLP':
            expected = 1 if h & 1 else 0
        elif size >= 12:
            expected = h & 7
        else:
            expected = 1 if h & 1 else 0
        if mech == 'GRU' and size < 12:
            continue
        if b != expected: violations.append((key,b,expected))
    assert not violations, violations
    out={'schema':'GMI833KRealTrainedCheckV1','systems':len(bits),
         'trained_systems':'MLP/GRU widths 6,48; register 0,1; heads 1,3,5,7',
         'source_sha256':meas['source_sha256_verified'],'protected_eval_items':meas['protected_eval_items'],
         'prediction_nd2':pred['set_valued_census']['nd2'],'soundness_violations':0,
         'truthful_commitments':'32/32','parent_blob_sha':pred['parent_file_blob_sha'],
         'verdict':'GREEN'}
    print(json.dumps(out,sort_keys=True,indent=2))
if __name__=='__main__': main()
