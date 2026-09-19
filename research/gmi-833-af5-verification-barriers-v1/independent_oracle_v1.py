from __future__ import annotations
import argparse,itertools,json
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main_result():
    states={'s0','s1','s2','bad'};edges={('s0','s1'),('s1','s2')};reach={'s0'}
    while True:
        nxt=reach|{b for a,b in edges if a in reach}
        if nxt==reach:break
        reach=nxt
    cert={'s0','s1','s2'};cert_ok='s0' in cert and 'bad' not in cert and all(a not in cert or b in cert for a,b in edges)
    combos=list(itertools.combinations(range(8),3));bits=(1,1,1,1,0,0,0,0);reject=sum(any(bits[i] for i in c) for c in combos);p=Fraction(reject,len(combos))
    sel=[]
    for w in (Fraction(1,10),Fraction(1),Fraction(2)):
        d=Fraction(3)+w*8;c=Fraction(5)+w*6;m=min(d,c);sel.append({'w':str(w),'winners':(['DIRECT_REPLAY'] if d==m else [])+(['CERTIFICATE_EMITTER'] if c==m else [])})
    return {'status':'GREEN','safe_reachable':sorted(reach),'certificate_valid':cert_ok,'property_reject_probability':f'{p.numerator}/{p.denominator}','selection':sel,'false_alarm_is_bug':False,'bounded_no_bug_is_unbounded_proof':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(HERE/'ORACLE_RESULT_V1.json'));a=ap.parse_args();r=main_result();Path(a.output).write_text(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(r,sort_keys=True))
if __name__=='__main__':main()
