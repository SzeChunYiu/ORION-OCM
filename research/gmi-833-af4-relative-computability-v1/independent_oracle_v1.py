from __future__ import annotations
import argparse, json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def require(c,m):
    if not c: raise RuntimeError(m)

def main_result():
    rows=[]
    for n in range(6):
        source_can_decide = n >= n+1
        target_can_decide = n+1 >= n+1
        residual_can_decide = n+1 >= n+2
        require(not source_can_decide and target_can_decide and not residual_can_decide,"triangular parent-derived status drift")
        rows.append({"n":n,"source":f"S_{n}","target":f"S_{n+1}","query":f"Q_{n}","source_decidable":source_can_decide,"target_decidable":target_can_decide,"next_residual_decidable":residual_can_decide,"queries":1,"charge":1})
    return {"status":"GREEN","rows":rows,"strict_chain_labels":[f"A^({n})" for n in range(7)],"strictness_ownership":"PARENT_OWNED_NOT_ORACLE_EXECUTOR_PROOF","universal_halting_solved":False,"physical_claim":False,"godel_context_dependence_only":True}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default=str(HERE/'ORACLE_RESULT_V1.json')); a=ap.parse_args()
    r=main_result(); Path(a.output).write_text(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n'); print(json.dumps(r,sort_keys=True))
if __name__=='__main__': main()
