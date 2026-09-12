from __future__ import annotations

"""Concrete post-freeze worlds for the K4-D developmental-acquisition successor.

Every generator is deterministic in (family_id, seed, scale), JSON-serializable, and exposes:
  * development: information available before final serving;
  * queries: protected serve-time inputs;
  * expected / verifier: the protected answer constitution;
  * authority: optional serve-time external state;
  * target_information_source: the preregistered legal source set;
  * entropy_bits_lower_bound: finite-scope lower bound on protected-world distinctions.

The generators contain no historical architecture implementation.  They instantiate obligations.
Candidate mechanisms/search live elsewhere.
"""

from dataclasses import dataclass, asdict
import collections, hashlib, itertools, json, math, random

FAMILY_IDS = tuple(f"K4-A{i:02d}" for i in range(1,23))


def _rng(fid, seed):
    h=hashlib.sha256(f"K4D:{fid}:{seed}".encode()).digest()
    return random.Random(int.from_bytes(h[:8],"big"))

def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _xvec(rng,d): return [rng.choice((-1,0,1)) for _ in range(d)]
def _fp(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _bits_entropy(n): return math.log2(max(1,n))

def _base(fid,seed,scale,source,entropy,development,queries,expected,authority=None,verifier=None,meta=None):
    body={"schema":"GMIK4DWorldV1","family_id":fid,"seed":int(seed),"scale":int(scale),
          "target_information_source":list(source),"entropy_bits_lower_bound":float(entropy),
          "development":development,"queries":queries,"expected":expected,"authority":authority,
          "verifier":verifier,"meta":meta or {}}
    body["world_fingerprint"]=_fp(body)
    return body


def a01(seed,scale):
    r=_rng("K4-A01",seed);d=min(6,2+scale);grid=(-2,-1,0,1,2);w=[r.choice(grid) for _ in range(d)]
    xs=[_xvec(r,d) for _ in range(24+8*scale)];cut=12+4*scale
    dev=[{"x":x,"y":_dot(w,x)} for x in xs[:cut]];qs=xs[cut:];ex=[_dot(w,x) for x in qs]
    return _base("K4-A01",seed,scale,("DEVELOPMENT","QUERY"),d*math.log2(len(grid)),dev,qs,ex,meta={"target_family":"finite_linear_coefficients","dimension":d})

def a02(seed,scale):
    r=_rng("K4-A02",seed);m=3+scale;grid=(-2,-1,0,1,2);coef=[r.choice(grid) for _ in range(m)];centers=list(range(m))
    def phi(x,c): return max(0,3-abs(x-c))
    def f(x): return sum(a*phi(x,c) for a,c in zip(coef,centers))
    xs=list(range(0,4*m));r.shuffle(xs);cut=2*m
    return _base("K4-A02",seed,scale,("DEVELOPMENT","QUERY"),m*math.log2(len(grid)),[{"x":x,"y":f(x)} for x in xs[:cut]],xs[cut:],[f(x) for x in xs[cut:]],meta={"basis_centers":centers})

def a03(seed,scale):
    r=_rng("K4-A03",seed);n=8*scale;vals=[r.randrange(4) for _ in range(n)];dev=[{"key":i,"value":v} for i,v in enumerate(vals)];qs=list(range(n));r.shuffle(qs)
    return _base("K4-A03",seed,scale,("DEVELOPMENT","QUERY"),2*n,dev,qs,[vals[k] for k in qs],meta={"independent_records":n})

def a04(seed,scale):
    r=_rng("K4-A04",seed);M=3;h=r.randrange(M);like=((0.75,0.20,0.05),(0.15,0.70,0.15),(0.05,0.20,0.75));obs=[]
    for _ in range(6+2*scale):
        u=r.random();acc=0
        for o,p in enumerate(like[h]):
            acc+=p
            if u<=acc:obs.append(o);break
    post=[]
    for hh in range(M):
        p=1/M
        for o in obs:p*=like[hh][o]
        post.append(p)
    z=sum(post);post=[p/z for p in post];utilities=[[1 if a==hh else 0 for hh in range(M)] for a in range(M)]
    best=max(range(M),key=lambda a:sum(utilities[a][hh]*post[hh] for hh in range(M)))
    return _base("K4-A04",seed,scale,("DEVELOPMENT","QUERY"),math.log2(M),[{"observation":o} for o in obs],[{"utility":utilities}], [best],meta={"posterior":post})

def _sat(clauses,a): return all(any((a[v] if sign else 1-a[v]) for v,sign in cl) for cl in clauses)
def a05(seed,scale):
    r=_rng("K4-A05",seed);n=3+scale;plant=[r.randrange(2) for _ in range(n)];clauses=[]
    for _ in range(5+3*scale):
        vs=r.sample(range(n),2);signs=[bool(r.randrange(2)) for _ in vs]
        if not any((plant[v] if s else 1-plant[v]) for v,s in zip(vs,signs)):signs[0]=bool(plant[vs[0]])
        clauses.append([[v,s] for v,s in zip(vs,signs)])
    q={"n_vars":n,"clauses":clauses}
    return _base("K4-A05",seed,scale,("QUERY",),0,[],[q],[None],verifier={"kind":"assignment_satisfies_all_clauses"},meta={"one_valid_assignment":plant})

def a06(seed,scale):
    r=_rng("K4-A06",seed);n=6+2*scale;edges={i:set() for i in range(n)}
    for i in range(n-1):edges[i].add(i+1);edges[i+1].add(i)
    for _ in range(n):
        a,b=r.sample(range(n),2);edges[a].add(b);edges[b].add(a)
    start,goal=0,n-1;prev={start:None};dq=collections.deque([start])
    while dq:
        x=dq.popleft()
        if x==goal:break
        for y in sorted(edges[x]):
            if y not in prev:prev[y]=x;dq.append(y)
    path=[];x=goal
    while x is not None:path.append(x);x=prev[x]
    path=path[::-1];q={"nodes":n,"edges":[[i,j] for i in edges for j in sorted(edges[i]) if i<j],"start":start,"goal":goal}
    return _base("K4-A06",seed,scale,("QUERY",),0,[],[q],[path],verifier={"kind":"valid_shortest_path"})

def a07(seed,scale):
    r=_rng("K4-A07",seed);p=7;a=r.randrange(1,p);b=r.randrange(1,p);c=r.randrange(p)
    def runseq(xs):
        h=0;ys=[]
        for x in xs:h=(a*h+b*x+c)%p;ys.append(h)
        return ys
    dev=[]
    for _ in range(8):
        x=[r.randrange(p) for _ in range(4+scale)];dev.append({"x":x,"y":runseq(x)})
    qs=[[r.randrange(p) for _ in range(6+scale)] for _ in range(6)]
    return _base("K4-A07",seed,scale,("DEVELOPMENT","QUERY"),math.log2((p-1)*(p-1)*p),dev,qs,[runseq(x) for x in qs])

def a08(seed,scale):
    r=_rng("K4-A08",seed);p=11;a=r.randrange(1,p);b=r.randrange(1,p)
    def traj(us):
        s=0;out=[]
        for u in us:s=(a*s+b*u)%p;out.append(s)
        return out
    dev=[]
    for _ in range(8):
        u=[r.randrange(p) for _ in range(5+scale)];dev.append({"u":u,"y":traj(u)})
    qs=[[r.randrange(p) for _ in range(7+scale)] for _ in range(6)]
    return _base("K4-A08",seed,scale,("DEVELOPMENT","QUERY"),2*math.log2(p-1),dev,qs,[traj(q) for q in qs])

def a09(seed,scale):
    r=_rng("K4-A09",seed);n=8+2*scale;k=[r.choice((-1,0,1)) for _ in range(3)]
    def conv(x):return [sum(k[j]*x[(i+j-1)%n] for j in range(3)) for i in range(n)]
    xs=[[r.randrange(2) for _ in range(n)] for _ in range(18)];return _base("K4-A09",seed,scale,("DEVELOPMENT","QUERY"),3*math.log2(3),[{"x":x,"y":conv(x)} for x in xs[:10]],xs[10:],[conv(x) for x in xs[10:]],meta={"cyclic":True})

def a10(seed,scale):
    r=_rng("K4-A10",seed);p=7;a,b=r.randrange(1,p),r.randrange(1,p)
    def make_graph():
        n=5+scale;edges=set()
        for i in range(n-1):edges.add((i,i+1))
        for _ in range(n):
            x,y=sorted(r.sample(range(n),2));edges.add((x,y))
        feat=[r.randrange(p) for _ in range(n)];adj={i:[] for i in range(n)}
        for x,y in edges:adj[x].append(y);adj[y].append(x)
        out=[(a*feat[i]+b*sum(feat[j] for j in adj[i]))%p for i in range(n)]
        return {"feat":feat,"edges":[list(e) for e in sorted(edges)]},out
    pairs=[make_graph() for _ in range(14)];return _base("K4-A10",seed,scale,("DEVELOPMENT","QUERY"),2*math.log2(p-1),[{"graph":q,"y":y} for q,y in pairs[:8]],[q for q,_ in pairs[8:]],[y for _,y in pairs[8:]])

def a11(seed,scale):
    r=_rng("K4-A11",seed);mask=r.randrange(8)
    def ex():
        keys=list(range(8));r.shuffle(keys);vals=[r.randrange(16) for _ in keys];cue=r.randrange(8);want=cue^mask;return {"keys":keys,"values":vals,"cue":cue},vals[keys.index(want)]
    pairs=[ex() for _ in range(24)];return _base("K4-A11",seed,scale,("DEVELOPMENT","QUERY"),3,[{"q":q,"y":y} for q,y in pairs[:14]],[q for q,_ in pairs[14:]],[y for _,y in pairs[14:]])

def a12(seed,scale):
    r=_rng("K4-A12",seed);radius=r.randrange(1,1+min(4,scale+1));offset=r.randrange(-radius,radius+1)
    def ex():
        n=10+2*scale;v=[r.randrange(16) for _ in range(n)];i=r.randrange(radius,n-radius);return {"values":v,"index":i,"radius":radius},v[i+offset]
    pairs=[ex() for _ in range(24)];return _base("K4-A12",seed,scale,("DEVELOPMENT","QUERY"),math.log2(sum(2*r+1 for r in range(1,1+min(4,scale+1)))),[{"q":q,"y":y} for q,y in pairs[:14]],[q for q,_ in pairs[14:]],[y for _,y in pairs[14:]])

def a13(seed,scale):
    r=_rng("K4-A13",seed);m=3+scale;sl=[r.choice((-3,-2,-1,1,2,3)) for _ in range(m)]
    def ex():mode=r.randrange(m);x=r.randrange(-4,5);return {"mode":mode,"x":x},sl[mode]*x
    pairs=[ex() for _ in range(30)];return _base("K4-A13",seed,scale,("DEVELOPMENT","QUERY"),m*math.log2(6),[{"q":q,"y":y} for q,y in pairs[:18]],[q for q,_ in pairs[18:]],[y for _,y in pairs[18:]])

def a14(seed,scale):
    r=_rng("K4-A14",seed);n=12*scale;corpus={str(i):r.randrange(256) for i in range(n)};qs=[str(r.randrange(n)) for _ in range(16)]
    return _base("K4-A14",seed,scale,("QUERY","EXTERNAL_AUTHORITY"),0,[],qs,[corpus[k] for k in qs],authority={"records":corpus,"version":1})

def a15(seed,scale):
    r=_rng("K4-A15",seed);d=3+scale;u=[r.choice((-1,0,1)) for _ in range(d)];v=[r.choice((-1,0,1)) for _ in range(d)]
    def f(x):return [x[i]+u[i]*_dot(v,x) for i in range(d)]
    xs=[_xvec(r,d) for _ in range(28)];return _base("K4-A15",seed,scale,("DEVELOPMENT","QUERY"),(2*d)*math.log2(3),[{"x":x,"y":f(x)} for x in xs[:16]],xs[16:],[f(x) for x in xs[16:]],meta={"base_map":"identity","revision_rank":1})

def a16(seed,scale):
    r=_rng("K4-A16",seed);d=3;w=[r.choice((-2,-1,1,2)) for _ in range(d)];xs=[_xvec(r,d) for _ in range(40)];dev=[]
    for x in xs[:24]:
        truth=_dot(w,x);dev.append({"x":x,"members":[truth+r.choice((-2,-1,0,0,1,2)) for _ in range(5)]})
    return _base("K4-A16",seed,scale,("DEVELOPMENT","QUERY"),d*2,dev,xs[24:],[_dot(w,x) for x in xs[24:]],meta={"noise":"weakly_correlated_member_noise"})

def a17(seed,scale):
    r=_rng("K4-A17",seed);p=r.choice((3,5,7,11));q=r.choice((13,17,19,23));n=p*q;query={"composite":n,"candidate_domain":[2,n-1]}
    return _base("K4-A17",seed,scale,("QUERY",),0,[],[query],[None],verifier={"kind":"proper_factor","condition":"1 < answer < n and n % answer == 0"},meta={"one_factor":p})

def _mdp(seed,scale,fixed_goal):
    r=_rng("K4-A19" if fixed_goal else "K4-A18",seed);n=4+scale;A=2;trans=[[r.randrange(n) for _ in range(A)] for _ in range(n)];goal=r.randrange(n);dev=[]
    for s in range(n):
        for a in range(A):dev.append({"s":s,"a":a,"s2":trans[s][a]})
    goals=[goal] if fixed_goal else list(range(n));qs=[{"state":s,"goal":g} for g in goals for s in range(n)]
    # expected gives optimal distance-to-goal action by brute-force value iteration on deterministic transitions.
    def action(s,g):
        dist=[10**6]*n;dist[g]=0
        for _ in range(n):
            for x in range(n):dist[x]=min(dist[x],0 if x==g else 1+min(dist[trans[x][a]] for a in range(A)))
        return min(range(A),key=lambda a:dist[trans[s][a]])
    ex=[action(q["state"],q["goal"]) for q in qs];fid="K4-A19" if fixed_goal else "K4-A18"
    return _base(fid,seed,scale,("DEVELOPMENT","QUERY"),n*A*math.log2(n),dev,qs,ex,meta={"n_states":n,"fixed_goal":fixed_goal})
def a18(seed,scale):return _mdp(seed,scale,False)
def a19(seed,scale):return _mdp(seed,scale,True)

def a20(seed,scale):
    r=_rng("K4-A20",seed);p00=r.choice((0.2,0.4,0.6,0.8));p10=r.choice((0.2,0.4,0.6,0.8))
    def seq(n):
        x=r.randrange(2);o=[x]
        for _ in range(n-1):x=1 if r.random()<(p00 if x==0 else p10) else 0;o.append(x)
        return o
    train=[seq(20) for _ in range(20)];qs=[s[:10] for s in (seq(11) for _ in range(12))];ex=[p00 if q[-1]==0 else p10 for q in qs]
    return _base("K4-A20",seed,scale,("DEVELOPMENT","QUERY"),math.log2(16),train,qs,ex,meta={"answer":"next_bit_probability_of_1"})

def a21(seed,scale):
    r=_rng("K4-A21",seed);states=list(itertools.product((0,1),repeat=3));weights=[r.randrange(1,8) for _ in states];z=sum(weights);pmf=[w/z for w in weights]
    def sample():
        u=r.random();a=0
        for s,p in zip(states,pmf):
            a+=p
            if u<=a:return list(s)
        return list(states[-1])
    dev=[sample() for _ in range(80+20*scale)]
    return _base("K4-A21",seed,scale,("DEVELOPMENT",),math.log2(7**8),dev,[{"request":"joint_sample_distribution"}],[pmf],meta={"states":[list(s) for s in states]})

def a22(seed,scale):
    r=_rng("K4-A22",seed);latent=2+min(scale,3);outdim=4+scale;M=[[r.randrange(2) for _ in range(latent)] for _ in range(outdim)]
    def dec(z):return [sum(row[j]*z[j] for j in range(latent))%2 for row in M]
    zs=[[r.randrange(2) for _ in range(latent)] for _ in range(40)];dev=[{"z":z,"x":dec(z)} for z in zs[:24]];qs=zs[24:]
    return _base("K4-A22",seed,scale,("DEVELOPMENT","QUERY"),latent*outdim,dev,qs,[dec(z) for z in qs],meta={"latent_dim":latent,"output_dim":outdim})

GEN={f"K4-A{i:02d}":globals()[f"a{i:02d}"] for i in range(1,23)}


def generate(family_id:str,seed:int,scale:int=1):
    if family_id not in GEN:raise KeyError(family_id)
    if scale<1:raise ValueError("scale must be >=1")
    return GEN[family_id](int(seed),int(scale))


def validate_all(seed=12345,scale=1):
    rows=[]
    for fid in FAMILY_IDS:
        a=generate(fid,seed,scale);b=generate(fid,seed,scale);c=generate(fid,seed+1,scale)
        if a!=b:raise AssertionError((fid,"nondeterministic"))
        if a["world_fingerprint"]==c["world_fingerprint"]:raise AssertionError((fid,"seed did not change world"))
        if not isinstance(a["target_information_source"],list):raise AssertionError((fid,"source"))
        if a["entropy_bits_lower_bound"]<0:raise AssertionError((fid,"entropy"))
        rows.append({"family_id":fid,"fingerprint":a["world_fingerprint"],"next_seed_fingerprint":c["world_fingerprint"],"development_events":len(a["development"]),"queries":len(a["queries"]),"source":a["target_information_source"],"entropy_bits_lower_bound":a["entropy_bits_lower_bound"]})
    return rows

if __name__=="__main__":print(json.dumps({"schema":"GMIK4DWorldValidationV1","rows":validate_all()},indent=1,sort_keys=True))
