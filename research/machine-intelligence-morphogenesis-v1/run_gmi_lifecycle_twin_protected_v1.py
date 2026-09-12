import argparse, json, random, statistics

NOM={
 "sL":1.0,"sQ":0.08,"sU":0.18,
 "iN":0.8,"iQ":0.05,"iU":0.3,
 "hL":1.2,"hN":0.5,"hQ":0.06,"hU":0.7,
 "vL":1.25,"vN":0.55,"vQ":0.065,"vU":0.75,"vM":1.0
}

def strategy_costs(p,c):
    N,L,Q,U,dep,ret,lineage=[p[k] for k in ("N","L","Q","U","dep","ret","lineage")]
    risk=(250 if lineage else 0)+(100 if ret else 0)
    return {
      "shared":c["sL"]*L+c["sQ"]*Q+c["sU"]*U*N*(0.15+dep)+risk,
      "indexed":c["iN"]*N+c["iQ"]*Q+c["iU"]*U+(150 if lineage else 0),
      "hybrid":c["hL"]*L+c["hN"]*N*dep+c["hQ"]*Q+c["hU"]*U*(1+4*dep)+(80 if lineage else 0),
      "versioned":c["vL"]*L+c["vN"]*N*dep+c["vQ"]*Q+c["vU"]*U*(1+3*dep)+c["vM"]*N*(ret+lineage)*0.2
    }

def choose(costs):
    return min(costs,key=costs.get)

def current_only(p):
    q=dict(p); q["U"]=0; q["ret"]=0; q["lineage"]=0
    return q

def main(freeze_sha):
    seed=int(freeze_sha[:16],16)%(2**63)
    rng=random.Random(seed)
    rows=[]
    optimal_pair_flips=0
    for pair in range(32):
        base={"N":rng.choice([32,48,64,96,128]),"L":rng.randint(4,20),
              "Q":rng.randint(20,200),"dep":rng.choice([0.05,0.1,0.2,0.4,0.7]),
              "U":0,"ret":0,"lineage":0}
        low=dict(base); low["U"]=rng.randint(0,2)
        high=dict(base); high["U"]=rng.randint(5,20); high["ret"]=rng.randint(0,1); high["lineage"]=rng.randint(0,1)
        if not high["ret"] and not high["lineage"]: high["lineage"]=1
        realized={k:v*rng.uniform(0.9,1.1) for k,v in NOM.items()}
        pair_opts=[]
        for cell,p in (("low",low),("high",high)):
            g=choose(strategy_costs(p,NOM))
            b=choose(strategy_costs(current_only(p),NOM))
            rc=strategy_costs(p,realized)
            opt=choose(rc); pair_opts.append(opt)
            optc=rc[opt]
            rg=(rc[g]-optc)/optc
            rb=(rc[b]-optc)/optc
            rows.append({"pair":pair,"cell":cell,"params":p,"gmi":g,"current_only":b,
                         "realized_optimum":opt,"gmi_regret":rg,"current_only_regret":rb})
        if pair_opts[0]!=pair_opts[1]: optimal_pair_flips+=1

    wins=sum(r["gmi_regret"]<r["current_only_regret"]-1e-12 for r in rows)
    ties=sum(abs(r["gmi_regret"]-r["current_only_regret"])<=1e-12 for r in rows)
    losses=len(rows)-wins-ties
    mg=statistics.mean(r["gmi_regret"] for r in rows)
    mb=statistics.mean(r["current_only_regret"] for r in rows)
    improvement=mb-mg
    passed=(improvement>0 and losses<=0.20*len(rows))
    out={
      "artifact":"GMI_LIFECYCLE_TWIN_PROTECTED_RECEIPT_V1",
      "freeze_commit":freeze_sha,"seed":seed,"worlds":len(rows),"pairs":32,
      "mean_gmi_normalized_regret":mg,
      "mean_current_only_normalized_regret":mb,
      "primary_regret_improvement":improvement,
      "gmi_wins":wins,"ties":ties,"gmi_losses":losses,
      "optimal_pair_flips":optimal_pair_flips,
      "gate_pass":passed,
      "rows":rows,
      "terminal":"LIFECYCLE_TWIN_PROTECTED_SYNTHETIC_GREEN" if passed else "LIFECYCLE_TWIN_PROTECTED_SYNTHETIC_RED"
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--freeze-sha",required=True)
    main(ap.parse_args().freeze_sha)
