"""Functional smoke: reference arm evaluates, deterministic, census enumerable."""
import sys, time, json, random
root = sys.argv[1]
sys.path.insert(0, root)
from morphology.direct_genome import reference_kso_genome, census_size, random_genome, enumerate_census
from evaluation.evaluate import evaluate_genome

t0 = time.time()
ref = reference_kso_genome()
r = evaluate_genome(ref)
assert r["feasible"], ("reference KSO arm must pass hard gates", r["gates"])
r2 = evaluate_genome(reference_kso_genome())
assert json.dumps(r, sort_keys=True) == json.dumps(r2, sort_keys=True), "non-deterministic evaluation"
print("REF gates:", json.dumps(r["gates"], sort_keys=True))
ev = r["evaluation"]
print("REF solved %d/%d work=%.1f bytes=%.1f probes=%d expansions=%d reuse=%.2f" % (
    ev["solved"], ev["total_tasks"], ev["work_total"], ev["persistent_bytes"],
    ev["probes"], ev["expansions"], ev["method_reuse_fraction"]))
print("REF families:", json.dumps(ev["per_family"], sort_keys=True))

# determinism + feasibility variety over random genomes
rng = random.Random(7)
feas = 0
for i in range(50):
    g = random_genome(rng)
    rr = evaluate_genome(g)
    feas += 1 if rr["feasible"] else 0
print("random feasible: %d/50" % feas)

t1 = time.time()
n = 0
for g in enumerate_census():
    n += 1
print("census size: %d (enumerate %.1fs)" % (n, time.time() - t1))

# throughput pilot denominator (single eval cost)
t2 = time.time()
for i in range(200):
    evaluate_genome(random_genome(rng), use_cache=False)
per_eval_ms = (time.time() - t2) / 200 * 1000
print("per-eval: %.2f ms" % per_eval_ms)
print("SMOKE_OK total %.1fs" % (time.time() - t0))
