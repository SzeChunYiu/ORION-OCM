"""RV-377-133 registered re-test of V3 at (m=4,k=4,r=32): continuation draws d=60..2059 under the
same cell key (independent of the 60 registered draws), plus the machine at the same draws."""
import random, statistics, math, json, sys
import gmi_channel_laws as cl
L=64; m=4; k=4; r=32; cell_key=f"m={m}|k={k}|r={r}"
closed=cl.ceiling6(L,r,m,k)
vals=[]; pairs=[]
mfn=cl.make_m6("verifier_search", k)
for d in range(60, 2060):
    w=cl.world6(L, r, m, random.Random(cl.draw_seed("CL6", cell_key, d)))
    c=statistics.fmean(min(1.0, k/2**b["u"]) for b in w["blocks"]); vals.append(c)
    rng=random.Random(cl.draw_seed("CL6", cell_key+"|verifier_search", d) ^ 0x5EED)
    pairs.append((cl.evaluate(w, mfn, rng, 8, list(range(L//m))), c))
n=len(vals); mean=statistics.fmean(vals); sd=statistics.stdev(vals); se=sd/math.sqrt(n)
out={"cell":{"m":m,"k":k,"r":r},"closed_form":closed,"continuation_draws":[60,2059],"n":n,
     "mean_per_draw_ceiling":round(mean,6),"sd":round(sd,6),"se":round(se,6),"z_vs_closed":round((mean-closed)/se,3),
     "machine_vs_per_draw_ceiling":cl.summarize(pairs)}
print(json.dumps(out,indent=1))
json.dump(out, open("microscopes/results/CHANNEL_LAW_VERIFIER_RV_377_133_V3_RETEST.json","w"), indent=1, sort_keys=True)
