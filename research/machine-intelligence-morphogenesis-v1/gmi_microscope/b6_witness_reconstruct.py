"""RV-377-180-Z: produce an EXHIBITABLE witness for one coefficient-cell recovery.

first_of_class records the machine's carrier, capability, margin, lineage and trace index
but discards the genotype, so the campaign's coefficient recoveries are reported rather
than exhibited. This reconstructs one of them and writes it out in full.

Method, and why it is a reconstruction rather than a new search:

  * the seeded population is rebuilt from the SAME source receipts the arm used, via the
    same matched_populations call -- no renaming, no synthetic provenance;
  * b1.search is deterministic in (target, seed, evaluations, seed_population), so re-running
    it regenerates the arm's own trace;
  * the run then ASSERTS that trace[trace_index] carries the fingerprint the arm recorded.
    That assertion is what makes this a witness for the campaign's object rather than for a
    similar one found nearby. If it fails, nothing is written.

Writes STAGE_B6_DENSE_WITNESS_<pair>_<arm>_S<seed>_<host>.json. It never writes any
STAGE_B6_DEV_* path, so it cannot disturb the running campaign.

    python3 b6_witness.py SAME CONTINUED 1 billy
"""
import json, os, sys, time

from gmi_microscope import b6_development as B
from gmi_microscope import b1, eco_axis, morph, smooth

pair, arm, seed, host = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
RES = B.RES

src_receipt = os.path.join(RES, f"STAGE_B6_DEV_{pair}_{arm}_S{seed}_{host}.json")
d = json.load(open(src_receipt))
fd = d["first_dense_admissible"]
assert fd.get("found"), "that arm reports no coefficient recovery"
idx, want_fp = fd["trace_index"], None
tc = d.get("trace_compact") or []
want_fp = tc[idx]["fingerprint"] if idx < len(tc) else None
assert want_fp, "no fingerprint recorded at the trace index"
print(f"target: {pair}|{arm}|S{seed}  trace_index={idx}  fingerprint={want_fp[:16]}", flush=True)

ea, eb = B.PAIRS[pair]; ea = ea.replace("<s>", str(seed))
spec = B.spec_of(eb); target = B.ecology.target_of(spec)
bc, cval = eco_axis.best_constant(target, smooth.UNSEEN)

pop = None
if arm in ("CONTINUED", "TWIN"):
    src_a = B.load_source(ea, seed, host); src_t = B.load_source(B.twin_name(seed), seed, host)
    cont, twin, k, sizes = B.matched_populations(src_a, src_t)
    chosen = cont if arm == "CONTINUED" else twin
    pop = [morph.from_json(v["genotype"]) for v in chosen]
    # the population must be the one the arm used, or the trace will not match
    assert [v["fingerprint"] for v in chosen] == d["seeding"]["seed_fingerprints"], \
        "rebuilt seed population differs from the arm's; aborting"
    print(f"seed population rebuilt and matched: {len(pop)} elites", flush=True)

t0 = time.time(); trace = []
b1.search(target, seed, d.get("n_evaluations", 20000), seed_population=pop, trace=trace)
print(f"search replayed in {round(time.time()-t0)}s, trace length {len(trace)}", flush=True)

assert idx < len(trace), f"trace too short: {len(trace)} <= {idx}"
rec = trace[idx]
got_fp = rec.get("fingerprint") or morph.fingerprint(morph.from_json(rec["genotype"]))
if got_fp != want_fp:
    raise SystemExit(f"REPLAY MISMATCH at index {idx}: got {got_fp[:16]} want {want_fp[:16]} -- nothing written")
print("fingerprint matches the campaign receipt: this is the same object", flush=True)

g = morph.from_json(rec["genotype"])
v, charged = B.verify_candidate(g, spec, bc)
small = morph.from_json(v["atrophied_genotype"]) if v.get("atrophied_genotype") else None
out = {
    "schema": "StageB6DenseWitnessV1", "revival_record": "RV-377-180-Z", "host": host,
    "reconstructed_from": os.path.basename(src_receipt), "trace_index": idx,
    "fingerprint_recorded_by_arm": want_fp, "fingerprint_replayed": got_fp,
    "replay_identity_verified": True,
    "target_ecology": eb, "source_ecology": ea, "best_constant": bc, "theta": B.THETA,
    "arm_reported": {k2: fd.get(k2) for k2 in ("min_over_six", "capability_standard", "B_morph", "origin", "carrier_atrophied")},
    "reverified": {"pass": bool(v.get("pass")), "min_over_six": v.get("min_over_six"),
                   "atrophied_min_over_six": v.get("atrophied_min_over_six"),
                   "atrophied_margin_fx": v.get("atrophied_margin_fx"),
                   "carrier_raw": v.get("carrier_raw"), "carrier_atrophied": v.get("carrier_atrophied"),
                   "caps_over_six": v.get("caps"), "evaluations_charged": charged},
    "genotype_raw": rec["genotype"], "n_nodes_raw": len(g["nodes"]),
    "kinds_raw": sorted({k2 for k2, _ in g["nodes"].values()}),
    "genotype_atrophied": v.get("atrophied_genotype"),
    "n_nodes_atrophied": len(small["nodes"]) if small else None,
    "kinds_atrophied": sorted({k2 for k2, _ in small["nodes"].values()}) if small else None,
}
p = os.path.join(RES, f"STAGE_B6_DENSE_WITNESS_{pair}_{arm}_S{seed}_{host}.json")
json.dump(out, open(p, "w"), indent=1, sort_keys=True, default=str)
print("reverified pass:", out["reverified"]["pass"], "| atrophied carrier:", out["reverified"]["carrier_atrophied"],
      "| min6:", out["reverified"]["min_over_six"], "| margin:", out["reverified"]["atrophied_margin_fx"])
print("kinds atrophied:", out["kinds_atrophied"])
print("written", p)
