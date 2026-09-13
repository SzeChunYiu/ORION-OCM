from fractions import Fraction as F
from math import comb
from functools import lru_cache
import json,subprocess,hashlib
repo='/home/billy/ocm-verify/gmi-probabilistic-acquisition-20260913';b='research/machine-intelligence-morphogenesis-v1/';r='9cae3f95b5f38ee2547f56f6a11d8998d257c932'
old=json.loads(subprocess.check_output(['/usr/bin/git','-C',repo,'show',r+':'+b+'GEOMETRY_PHASE_SCALING_RESULT_V1.json']))
def closed(m,a):
 A=2*a/(2-a);B=(2-3*a)/(2-a)
 return m*sum((-1)**(j+1)*comb(m,j)*sum(F(comb(j,k))*A**k*B**(j-k)/(k*a/2+j-k) for k in range(j+1)) for j in range(1,m+1))
def dp(m,a):
 @lru_cache(None)
 def T(c,h):
  if c==m:return F(0)
  z=m-c-h;u=a*z/m;v=a*h/(2*m);w=(1-a)*z/m
  return (1+(u*T(c,h+1) if u else 0)+(v*T(c+1,h-1) if v else 0)+(w*T(c+1,h) if w else 0))/(u+v+w)
 return T(0,0)
rows=[]
for m in [7,8,9,10]:
 x,y=closed(m,F(9,10)),closed(m,F(1,10))
 if x!=dp(m,F(9,10)) or y!=dp(m,F(1,10)):raise RuntimeError('independent exact disagreement')
 H=sum((F(1,j)for j in range(1,m+1)),F(0));lc=m*H/F(1,10);cc=m*H/F(9,10)
 o=next(v for v in old['rows']if v['m']==m)
 rows.append({'m':m,'additive_LOCAL':str(x),'additive_CHUNK':str(y),'LOCAL_wins':x<y,'CHUNK_LOCAL':str(lc),'CHUNK_CHUNK':str(cc),'chunk_ratio':str(lc/cc),'largest_archived_decimal_error':max(abs(float(x)-o['additive']['LOCAL']),abs(float(y)-o['additive']['CHUNK']),abs(float(lc)-o['chunk']['LOCAL']),abs(float(cc)-o['chunk']['CHUNK']))})
qs=[]
for k,H in [(100,1),(100,2),(2,2)]:
 t=1
 while F(1,2)*F(k-1,k)**(2*t)>F(1,1000):t+=1
 x=[F(1)]*20;A=[F(1)]+[F(k)]*19;grad=[a*z for a,z in zip(A,x)];final=[z-g/a for a,z,g in zip(A,x,grad)]
 if any(final):raise RuntimeError('Newton failed')
 qs.append({'kappa':k,'H':H,'gd_steps':t,'GD':20*t*H,'dense':20**3+H*20**2,'diagonal_touch_parent':20*H,'all20_coordinates_zero':not any(final)})
print(json.dumps({'geometry':rows,'quadratic':qs,'bayes_strong_MAP':str(F(81,100)+F(9,100))},indent=2))
