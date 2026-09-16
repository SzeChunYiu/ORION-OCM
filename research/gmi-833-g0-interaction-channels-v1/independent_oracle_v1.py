from itertools import permutations,product
import json
A=(0,1,2);M=(0,1);CH=tuple((a,b) for a in A for b in A if a!=b);TOOLS={'DOUBLE':lambda x:(2*x)%3,'ROT':lambda x:(x+1)%3}
def empty():return ((0,0,0),tuple(() for _ in CH))
def idx(a,b):return CH.index((a,b))
def send(st,a,b,m):
 loc,qs=st;z=[*qs];z[idx(a,b)]=z[idx(a,b)]+(m,);return (loc,tuple(z))
def recv(st,a,b):
 loc,qs=st;z=[*qs];q=z[idx(a,b)];val=q[0] if q else 'NO_MESSAGE';z[idx(a,b)]=q[1:] if q else q;return (loc,tuple(z)),val
def trans(st,p):
 loc,qs=st;nl=[0]*3
 for old,new in enumerate(p):nl[new]=loc[old]
 nq=[() for _ in CH]
 for i,(a,b) in enumerate(CH):nq[idx(p[a],p[b])]=qs[i]
 return (tuple(nl),tuple(nq))
def main():
 rem=rf=dest=bcast=0
 for a,b in CH:
  for m in M:
   base=((0,1,2),tuple(() for _ in CH));s=send(base,a,b,m)
   if [i for i,(x,y) in enumerate(zip(base[1],s[1])) if x!=y]!=[idx(a,b)]:dest+=1
   if sum(map(len,s[1]))!=1:bcast+=1
   for p in permutations(A):
    rem+=1
    if trans(s,p)!=send(trans(base,p),p[a],p[b],m):rf+=1
 fc=ff=0
 for a,b in CH:
  for m1,m2 in product(M,repeat=2):
   st=send(send(empty(),a,b,m1),a,b,m2);st,x=recv(st,a,b);st,y=recv(st,a,b);fc+=1
   if (x,y)!=(m1,m2):ff+=1
 table={t:[TOOLS[t](x) for x in range(3)] for t in sorted(TOOLS)}
 out={'schema':'GMI833InteractionChannelsIndependentOracleV1','remint_checks':rem,'remint_failures':rf,'destination_isolation_failures':dest,'implicit_broadcast_failures':bcast,'fifo_checks':fc,'fifo_failures':ff,'tool_table':table,'tool_compositions':{'ROT->DOUBLE':[TOOLS['DOUBLE'](TOOLS['ROT'](x)) for x in range(3)],'DOUBLE->ROT':[TOOLS['ROT'](TOOLS['DOUBLE'](x)) for x in range(3)]},'terminal':'GREEN' if not any((rf,dest,bcast,ff)) else 'RED'}
 print(json.dumps(out,indent=2,sort_keys=True,separators=(',',': ')))
if __name__=='__main__':main()
