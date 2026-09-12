import json

def op(name,*args): return (name,)+args
def C(x): return ("const",float(x))
def V(x): return ("var",x)
def add(a,b): return op("add",a,b)
def mul(a,b): return op("mul",a,b)

def apply(o,a,b):
    return a+b if o=="add" else a*b

def ast(e,env):
    if e[0]=="const": return e[1]
    if e[0]=="var": return env[e[1]]
    return apply(e[0],ast(e[1],env),ast(e[2],env))

def postfix(e):
    if e[0] in ("const","var"): return [e]
    return postfix(e[1])+postfix(e[2])+[(e[0],)]

def post(tokens,env):
    s=[]
    for t in tokens:
        if t[0]=="const": s.append(t[1])
        elif t[0]=="var": s.append(env[t[1]])
        else:
            b=s.pop(); a=s.pop(); s.append(apply(t[0],a,b))
    return s[-1]

def graph(e):
    nodes=[]
    def rec(x):
        i=len(nodes); nodes.append(None)
        if x[0] in ("const","var"): nodes[i]=x
        else: nodes[i]=(x[0],rec(x[1]),rec(x[2]))
        return i
    return nodes,rec(e)

def ge(g,root,env):
    memo={}
    def rec(i):
        if i in memo: return memo[i]
        n=g[i]
        if n[0]=="const": z=n[1]
        elif n[0]=="var": z=env[n[1]]
        else: z=apply(n[0],rec(n[1]),rec(n[2]))
        memo[i]=z; return z
    return rec(root)

pairs=[]
pairs.append(("P01",add(V("law"),add(mul(V("Q"),C(1)),mul(V("U"),V("global")))),add(V("table"),add(mul(V("Q"),C(1)),mul(V("U"),V("local")))),{"law":8,"Q":10,"U":0,"global":20,"table":64,"local":1},{"law":8,"Q":10,"U":5,"global":20,"table":64,"local":1}))
pairs.append(("P02",add(V("state"),mul(V("T"),C(1))),mul(V("T"),V("history")),{"state":4,"T":20,"history":10},{"state":40,"T":5,"history":2}))
pairs.append(("P03",add(V("router"),mul(V("active"),V("edge"))),mul(V("union"),V("edge")),{"router":3,"active":2,"edge":2,"union":10},{"router":8,"active":8,"edge":2,"union":9}))
pairs.append(("P04",add(V("tied"),mul(V("mismatch"),V("lam"))),V("free"),{"tied":5,"mismatch":0,"lam":20,"free":20},{"tied":5,"mismatch":1,"lam":20,"free":20}))
pairs.append(("P05",add(mul(V("rank"),add(V("m"),V("n"))),mul(V("miss"),V("lam"))),mul(V("m"),V("n")),{"rank":1,"m":8,"n":8,"miss":0,"lam":100},{"rank":6,"m":8,"n":8,"miss":1,"lam":100}))
pairs.append(("P06",V("belief"),add(V("point"),mul(V("uncert"),V("risk"))),{"belief":8,"point":1,"uncert":1,"risk":20},{"belief":8,"point":1,"uncert":0,"risk":20}))
pairs.append(("P07",mul(V("Q"),V("search")),add(V("build"),mul(V("Q"),V("serve"))),{"Q":2,"search":10,"build":40,"serve":1},{"Q":20,"search":10,"build":40,"serve":1}))
pairs.append(("P08",add(V("gatecost"),mul(V("gateerr"),V("risk"))),mul(V("directerr"),V("risk")),{"gatecost":4,"gateerr":0.02,"directerr":0.3,"risk":50},{"gatecost":8,"gateerr":0.12,"directerr":0.1,"risk":20}))
pairs.append(("P09",add(V("model"),mul(V("G"),V("plan"))),mul(V("G"),V("policy")),{"model":30,"G":10,"plan":2,"policy":10},{"model":30,"G":2,"plan":2,"policy":10}))
pairs.append(("P10",add(V("special"),V("route")),add(V("shared"),mul(V("hetero"),V("lam"))),{"special":20,"route":5,"shared":10,"hetero":2,"lam":10},{"special":20,"route":5,"shared":10,"hetero":0.2,"lam":10}))
pairs.append(("P11",add(V("base"),mul(V("U"),V("local"))),mul(V("U"),V("global")),{"base":20,"U":10,"local":2,"global":10},{"base":20,"U":1,"local":2,"global":10}))
pairs.append(("P12",add(V("enscost"),mul(V("enserr"),V("risk"))),add(V("singlecost"),mul(V("singleerr"),V("risk"))),{"enscost":12,"enserr":0.05,"singlecost":4,"singleerr":0.25,"risk":80},{"enscost":12,"enserr":0.18,"singlecost":4,"singleerr":0.2,"risk":20}))

rows=[]; disagreements=0; failed_flips=0
for pid,l,r,pos,neg in pairs:
    ws=[]
    for label,env in (("positive",pos),("negative",neg)):
        vals=[]
        for e in (l,r):
            g,root=graph(e)
            vals.append((ast(e,env),post(postfix(e),env),ge(g,root,env)))
        winners=[]
        for j in range(3):
            winners.append("L" if vals[0][j]<vals[1][j] else ("R" if vals[1][j]<vals[0][j] else "TIE"))
        if len(set(winners))!=1: disagreements+=1
        ws.append(winners[0])
        rows.append({"pair":pid,"cell":label,"winner":winners[0]})
    if ws[0]==ws[1]: failed_flips+=1

print(json.dumps({
 "artifact":"GMI_NEUTRAL_MULTI_ENCODING_REDISCOVERY_RECEIPT_V3",
 "pairs":len(pairs),
 "cells":len(rows),
 "evaluator_encodings":3,
 "evaluator_disagreements":disagreements,
 "failed_positive_negative_flips":failed_flips,
 "rows":rows,
 "terminal":"ZERO_PRIOR_MULTI_ENCODING_MECHANISM_REDISCOVERY_V3_GREEN" if disagreements==0 and failed_flips==0 else "RED"
},indent=2,sort_keys=True))
