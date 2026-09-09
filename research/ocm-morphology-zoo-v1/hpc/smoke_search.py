"""Search-arm smoke: each P01-P07 arm runs 300 evals, returns sane metrics."""
import sys, json, time
root = sys.argv[1]
sys.path.insert(0, root)
import random
from search import random_search, nsga, novelty, nslc, map_elites, cvt_map_elites, mome, lexicase

BUD = int(sys.argv[2]) if len(sys.argv) > 2 else 300
arms = {
    "P01": lambda: random_search.run(budget=BUD, seed=0),
    "P02": lambda: nsga.run(budget=BUD, seed=0),
    "P03": lambda: novelty.run(budget=BUD, seed=0),
    "P04": lambda: nslc.run(budget=BUD, seed=0),
    "P05": lambda: map_elites.run(budget=BUD, seed=0),
    "P06": lambda: cvt_map_elites.run(budget=BUD, seed=0, k=16),
    "P07": lambda: mome.run(budget=BUD, seed=0),
    "P11": lambda: lexicase.run(budget=BUD, seed=0),
}
for name, fn in arms.items():
    t0 = time.time()
    try:
        r = fn()
        keys = {k: r.get(k) for k in ("feasible_found", "n_elites", "coverage",
                                      "qd_score", "unique_feasible_phenotypes",
                                      "best_dev_score", "occupied_cells")}
        print(name, json.dumps(keys, sort_keys=True), "wall=%.1fs" % (time.time() - t0))
    except Exception as e:
        print(name, "FAIL", type(e).__name__, str(e)[:120])
print("SEARCH_SMOKE_DONE")
