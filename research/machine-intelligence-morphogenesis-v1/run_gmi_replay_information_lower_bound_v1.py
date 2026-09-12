import itertools, json
N=6
rows=[]
for m in range(N):
    total_pairs=0
    subset_count=0
    for S in itertools.combinations(range(N),m):
        subset_count+=1
        groups={}
        for y in itertools.product([0,1], repeat=N):
            key=tuple(y[i] for i in S)
            groups[key]=groups.get(key,0)+1
        total_pairs += sum(v*(v-1)//2 for v in groups.values())
    rows.append({"replay_size":m,"subsets":subset_count,
                 "indistinguishable_unordered_pairs":total_pairs})
print(json.dumps({
 "artifact":"GMI_REPLAY_INFORMATION_LOWER_BOUND_RECEIPT_V1",
 "N":N,
 "rows":rows,
 "all_proper_subsets_have_collisions":all(r["indistinguishable_unordered_pairs"]>0 for r in rows),
 "terminal":"REPLAY_INFORMATION_LOWER_BOUND_EXACT_GREEN"
},indent=2,sort_keys=True))
