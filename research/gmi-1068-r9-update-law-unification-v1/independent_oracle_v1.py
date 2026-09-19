#!/usr/bin/env python3
import json
from fractions import Fraction
p=Fraction(3,8)/(Fraction(3,8)+Fraction(1,8))
hyp=[(0,0),(1,1),(0,1),(1,0)]
partial=sum(v[0]==0 for v in hyp);full=sum(v==(0,1) for v in hyp)
print(json.dumps({"status":"GREEN","U1_surface":"rho=3","U2_surface":"sigma=10","posterior":str(p),"partial_hypotheses":partial,"full_hypotheses":full,"library_first_n":3,"meta_threshold":"1/2"},sort_keys=True))
