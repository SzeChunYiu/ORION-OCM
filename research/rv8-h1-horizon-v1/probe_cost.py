"""Post-preflight cost probe: measured wall-seconds per task per arm per family, on the
REAL libraries. Sizing only (SLURM --time and launch order); touches no frozen design
constant and files no result. Uses a probe salt disjoint from the scored stream.

WARNING, and the reason this file is not evidence about any arm: the probe seeds its
draws from the LIBRARY KEY as well as the family, so every arm sees DIFFERENT tasks.
Its numbers are per-arm absolute costs for sizing --time, and cross-arm comparisons
drawn from them are unpaired and meaningless. The scored cells are the opposite:
stream_task() hashes (SALT_RV8, mix_idx, composition, seed, pos) with NO arm term, so
every arm solves the identical task at the identical position and the surface is
strictly paired."""
import json, pickle, sys, time, hashlib, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rv8_horizon as H
from fna4 import Work, gen_task
from fna4_solver import solve_task, MisfireRegistry
import fna4_learners as L

out = Path(sys.argv[1]).resolve()
libs = pickle.loads((out / "RV8_LIBRARIES.pkl").read_bytes())
NPROBE = int(sys.argv[2]) if len(sys.argv) > 2 else 12
rows = {}
for key, (macros, registry) in sorted(libs.items()):
    arm = key.split("#")[0]
    _l, gran, use_cegis, _n = H.ARM_SPEC[arm]
    row = {}
    for fam in ("F1", "F2", "F3"):
        rng = random.Random(int.from_bytes(
            hashlib.sha256(("COSTPROBE|%s|%s" % (key, fam)).encode()).digest()[:8], "big"))
        tasks = [gen_task(rng, fam, "CP-%s-%s-%d" % (key, fam, i)) for i in range(NPROBE)]
        reg = pickle.loads(pickle.dumps(registry)) if registry is not None else None
        lib = list(macros)
        t0 = time.time(); units = 0; capped = 0
        for t in tasks:
            w = Work()
            r = solve_task(t, macros=lib, registry=reg, work=w)
            if use_cegis:
                for att in r["macro_attempts"]:
                    if att["misfires"] > 0 and not att["hit"] and att["first_failed_assignment"] is not None:
                        m = next((m for m in lib if m.macro_id == att["macro_id"]), None)
                        if m is not None:
                            m2, ok = L.specialize(m, tuple(att["first_failed_assignment"]), w)
                            if ok:
                                lib[lib.index(m)] = m2
                r["work"] = w.as_dict()
            units += r["work"]["total_units"]; capped += 1 if r["capped"] else 0
        dt = time.time() - t0
        row[fam] = {"sec_per_task": dt / len(tasks), "units_per_task": units / len(tasks),
                    "capped": capped, "n": len(tasks)}
    rows[key] = row
# projected worst-case cell wall-seconds at each mix, balanced and f1_only
proj = {}
for key, row in rows.items():
    worst = 0.0
    arm = key.split("#")[0]
    n = H.N_REDUCED if arm in H.REDUCED_ARMS else H.N_FULL
    for mix in H.MIX_GRID:
        for comp in H.COMPOSITIONS:
            t = H.mix_targets(mix, comp)
            s = sum(t[f] * row[f]["sec_per_task"] for f in ("F1", "F2", "F3"))
            worst = max(worst, s * n)
    proj[key] = {"worst_cell_sec": worst, "worst_cell_hours": worst / 3600.0, "n": n}
print(json.dumps({"per_task": rows, "projected": proj}, indent=1, sort_keys=True))
