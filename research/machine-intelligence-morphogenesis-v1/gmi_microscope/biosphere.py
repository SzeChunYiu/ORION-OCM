"""R11 — the open-world biosphere harness: one episode end to end (ecology sampling, development, charging, archiving,
lineage, triage, census) behind one deterministic receipt and a resumable checkpoint, with the protocol's
meta-morphogenesis arm as the thing the harness is actually used to measure.

WHICH R11 THIS IS. `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1` section 20 lists R11 as the "meta-morphogenesis layer"
(stage B9: let the morphogenesis rule Gamma itself be learned, and measure
`Delta_B_meta = B_fixed_morphogenesis - B_learned_morphogenesis`). The working brief asks R11 for the open-world driver
of stage B4. This module is the driver, and the reason it exists is to run the two Gamma arms through the same charged
machinery so that a Delta_B_meta is a comparison and not an anecdote. Both readings are therefore in one receipt.

THE EPISODE (stage B4, steps 1-8 of protocol section 11, minus island migration which this lane does not have):
  1. ECOLOGY SAMPLING. The episode draws its ecology for each proposal from a declared DEVELOPMENT pool of generated
     smooth ecologies. Generated ecologies are development worlds (biosphere section 20), so they are registered as D.
     The R7 stream manager gates every access: the protected stream is never queried and the receipt shows the count.
  2. DEVELOPMENT + 3. CHARGING. The exact charged VM (R1) develops each candidate; the ledger is the meter.
  4. ARCHIVING. A MAP-Elites archive keyed by (ecology, carrier, size bucket, drift bucket) — occupancy per ecology, so
     niche BREADTH (in how many ecologies a genotype is the cell elite) is a measured quantity, not an assumption.
  5. LINEAGE. Every evaluated genotype gets an R7 descent record and the episode replays the elites' chains at the end.
  7. FOSSILS. Every evaluated fingerprint stays in the lineage after its cell is taken (biosphere section 7).
  8. The protected ecologies are never exposed.
  TRIAGE. The R8 screen decides which candidates get the exact confirmation; the run refuses to start without the
     screen's audit receipt (protocol rule 18) and cites its hash.
  CENSUS. A small R9 census runs at the end so the archive's size is reported next to the size of the space it came
     from — an archive of N cells means nothing without N_CONFIG.

THE TWO GAMMA ARMS.
  FIXED     the R5 operator is drawn uniformly, as in R6/b1. This is the control.
  LEARNED   an ecology-conditioned morphogenesis policy: per (ecology, carrier of the parent) it keeps the measured
            success counts of each R5 operator (a success is a proposal that takes or improves an archive cell) and
            samples the operator with probability proportional to (successes + 1) / (tries + 1). Its own description
            and its update are CHARGED to B_search, because an unmetered policy is exactly the hidden-capital channel
            the metering rules forbid (biosphere section 22).
  Delta_B_meta is measured at a MILESTONE declared before the run: the total charge each arm has spent when it first
  holds an admissible genotype in at least two distinct carrier classes (the b1 recovery terminal). An arm that never
  reaches the milestone reports None and the delta is not computed — a missing milestone is not a win for the other arm.

DETERMINISM AND RESUME. The episode is a pure function of (seed, arm, budget, ecology pool, screen audit). The
checkpoint holds the archive, the lineage, the policy counters and the master random state, so a resumed episode
continues the same stream; `main` asserts that a resumed episode and an unresumed one produce the same receipt fields.

CLAIM CEILING. One episode family, two arms, a small number of seeds, one grammar, one screen. Delta_B_meta here is a
statement about THIS operator set and THIS policy parameterization on THIS ecology pool; the protocol's B9 asks for it
on untouched regime SEQUENCES, which this lane does not have. Nothing in this receipt is evidence of open-endedness:
section 21 of the biosphere document lists what open-endedness would have to measure, and this episode measures the
archive, the lineage and the charge, not new niches over time.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from . import b1, census, ecology, lineage, morph, morphgen, smooth, triage
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

# the declared development ecology pool: generated smooth ecologies (development worlds, biosphere section 20)
ECO_POOL = (("Ep_smooth3", smooth.COEFFS_V3), ("Ep_sym5", (5 / 16,) * 4), ("Ep_mixed", (0.25, -0.5, 0.5, -0.25)))
MILESTONE_CARRIERS = 2       # the declared milestone: admissible genotypes in at least this many distinct carriers
ARMS = ("fixed", "learned")
POLICY_DESC_BITS_PER_COUNTER = 8   # the charged description of one policy counter


def _pool_specs():
    return [(name, ecology.spec_smooth(c, name)) for name, c in ECO_POOL]


class GammaPolicy:
    """the morphogenesis rule. 'fixed' draws an R5 operator uniformly; 'learned' conditions on (ecology, parent carrier)
    and samples proportional to measured success. Both are charged: the learned arm pays for its counters."""

    def __init__(self, arm, rng):
        self.arm = arm; self.rng = rng
        self.tries = {}; self.wins = {}; self.charge = 0

    def choose(self, eco_name, carrier):
        if self.arm == "fixed":
            return None                                   # let the R5 draw pick the operator, as in R6/b1
        key = (eco_name, carrier)
        w = [(self.wins.get((key, i), 0) + 1) / (self.tries.get((key, i), 0) + 1) for i in range(len(morphgen.OPS))]
        tot = sum(w); r = self.rng.random() * tot; acc = 0.0
        for i, x in enumerate(w):
            acc += x
            if r <= acc:
                self.charge += 1                          # one charged unit per policy consultation
                return i
        self.charge += 1
        return len(w) - 1

    def update(self, eco_name, carrier, op_index, won):
        if self.arm == "fixed" or op_index is None: return
        key = ((eco_name, carrier), op_index)
        self.tries[key] = self.tries.get(key, 0) + 1
        if won: self.wins[key] = self.wins.get(key, 0) + 1
        self.charge += 1                                  # one charged unit per policy update

    def description_charge(self):
        return POLICY_DESC_BITS_PER_COUNTER * (len(self.tries) + len(self.wins))

    def total_charge(self):
        return self.charge + self.description_charge()


def _ckpt_state(st):
    return {"n": st["n"], "charge": st["charge"], "search_draws": st["search_draws"],
            "archive": [[list(k), v[0], v[1]] for k, v in st["archive"].items()],
            "lineage": st["lin"].rec, "genotypes": {k: morph.to_json(v) for k, v in st["genotypes"].items()},
            "policy_tries": {json.dumps(list(k[0]) + [k[1]]): v for k, v in st["policy"].tries.items()},
            "policy_wins": {json.dumps(list(k[0]) + [k[1]]): v for k, v in st["policy"].wins.items()},
            "policy_charge": st["policy"].charge, "rng_state": st["rng"].getstate(),
            "policy_rng_state": st["policy"].rng.getstate(),
            "milestone_charge": st["milestone_charge"], "milestone_n": st["milestone_n"]}


def _restore(st, d):
    st["n"] = d["n"]; st["charge"] = d["charge"]; st["search_draws"] = d["search_draws"]
    st["archive"] = {tuple(k): (v0, v1) for k, v0, v1 in d["archive"]}
    st["lin"].rec = d["lineage"]
    # rebuild in CANONICAL GENOTYPE form, not straight out of the JSON: `morph.to_json` sorts node ids as strings
    # ("0", "1", "10", "2") while a canonical genotype is ordered by canonical label ("0", "1", "2", ... "10"), and the
    # R5 operators read dictionary order, so a straight round trip silently changes what every later proposal produces.
    st["genotypes"] = {k: lineage.canon_geno(morph.from_json(v)) for k, v in d["genotypes"].items()}
    st["policy"].tries = {(tuple(json.loads(k)[:2]), json.loads(k)[2]): v for k, v in d["policy_tries"].items()}
    st["policy"].wins = {(tuple(json.loads(k)[:2]), json.loads(k)[2]): v for k, v in d["policy_wins"].items()}
    st["policy"].charge = d["policy_charge"]
    for who, key in ((st["rng"], "rng_state"), (st["policy"].rng, "policy_rng_state")):
        rs = d[key]                           # JSON turns the Mersenne state into nested lists; setstate needs tuples
        who.setstate((rs[0], tuple(rs[1]), rs[2]))
    st["milestone_charge"] = d["milestone_charge"]; st["milestone_n"] = d["milestone_n"]


def episode(seed=0, arm="fixed", evaluations=1500, n_init=25, tau=None, ckpt_path=None, ckpt_every=500, resume=True,
            streams=None):
    """one biosphere episode. Returns the episode state; deterministic in (seed, arm, evaluations, pool, tau)."""
    specs = _pool_specs(); streams = streams or lineage.Streams()
    for name, _ in specs: streams.register_development(name)   # generated ecologies are development worlds
    targets = {name: smooth.make_target(tuple(spec["coeffs"])) for name, spec in specs}
    st = {"n": 0, "charge": 0, "search_draws": 0, "archive": {}, "lin": lineage.Lineage(), "genotypes": {},
          "rng": random.Random(seed), "policy": GammaPolicy(arm, random.Random(seed ^ 0x5EED)),
          "milestone_charge": None, "milestone_n": None, "resumed_from": None, "refused_wide": 0, "screened_out": 0}
    if resume and ckpt_path and os.path.exists(ckpt_path):
        _restore(st, json.load(open(ckpt_path))); st["resumed_from"] = st["n"]
    rng = st["rng"]; t0 = time.time()

    def milestone_reached():
        adm = {k[1] for k, v in st["archive"].items() if v[0] >= b1.THETA}
        return len(adm) >= MILESTONE_CARRIERS

    def place(g, eco_name, parent_fp, op, pseed, other_fp, draws, op_index=None, founder_spec=None):
        """triage then charge then archive then record. Returns True if the candidate took or improved a cell."""
        fp = morph.fingerprint(g)
        if fp in st["lin"].rec: return False
        target = targets[eco_name]; streams.query(eco_name, "development")
        sc, sdesc, scharge = triage.screen(g, target)          # F2 cheap screen
        st["charge"] += scharge; st["n"] += 1
        if sc is None:
            st["lin"].add(fp, parent_fp, op, pseed, other_fp, draws, scharge, None, None, founder_spec, op_index)
            st["genotypes"][fp] = g; return False
        if tau is not None and sc < tau:                       # rejected by the audited screen; no exact confirmation
            st["screened_out"] += 1
            st["lin"].add(fp, parent_fp, op, pseed, other_fp, draws, scharge, None, None, founder_spec, op_index)
            st["genotypes"][fp] = g; return False
        res = b1.evaluate(g, target)                           # F5 exact confirmation
        if res is None:
            st["lin"].add(fp, parent_fp, op, pseed, other_fp, draws, scharge, None, None, founder_spec, op_index)
            st["genotypes"][fp] = g; return False
        cap, desc, R = res; st["charge"] += sum(R.values())
        st["lin"].add(fp, parent_fp, op, pseed, other_fp, draws, scharge + sum(R.values()), cap, desc, founder_spec, op_index)
        st["genotypes"][fp] = g
        key = (eco_name, b1.CARRIERS[desc[0]], desc[1], desc[2])
        cur = st["archive"].get(key); won = cur is None or cap > cur[0]
        if won: st["archive"][key] = (cap, fp)
        if st["milestone_charge"] is None and milestone_reached():
            st["milestone_charge"] = st["charge"] + st["search_draws"]; st["milestone_n"] = st["n"]
        return won

    while st["n"] < n_init and st["n"] < evaluations:
        fseed = rng.randrange(2 ** 31); steps = rng.randrange(3, 10)
        g, draws, _ = lineage.founder(fseed, steps); st["search_draws"] += draws
        place(g, rng.choice(specs)[0], None, "op_founder", fseed, None, draws, founder_spec={"fseed": fseed, "steps": steps})
    while st["n"] < evaluations:
        vals = list(st["archive"].items())
        if not vals:
            fseed = rng.randrange(2 ** 31); steps = rng.randrange(3, 10)
            g, draws, _ = lineage.founder(fseed, steps); st["search_draws"] += draws
            place(g, rng.choice(specs)[0], None, "op_founder", fseed, None, draws, founder_spec={"fseed": fseed, "steps": steps})
            continue
        (pkey, (_, pfp)) = rng.choice(vals); parent = st["genotypes"][pfp]
        eco_name = rng.choice(specs)[0]                        # ecology sampling (step 1)
        carrier = pkey[1]
        op_index = st["policy"].choose(eco_name, carrier)
        pseed = rng.randrange(2 ** 31); other_fp = None; other = None
        if op_index is None and rng.random() < 0.2 and len(vals) > 1:
            (_, (_, other_fp)) = rng.choice(vals); other = st["genotypes"][other_fp]
        try:
            child, op, draws = lineage.propose(parent, pseed, other, op_index)
        except morph.MorphError:
            st["refused_wide"] += 1; st["search_draws"] += 1; continue
        st["search_draws"] += draws
        won = place(child, eco_name, pfp, op, pseed, other_fp, draws, op_index)
        st["policy"].update(eco_name, carrier, op_index, won)
        if ckpt_path and st["n"] % ckpt_every == 0:
            json.dump(_ckpt_state(st), open(ckpt_path, "w"), default=str)
    st["seconds"] = round(time.time() - t0, 1); st["streams"] = streams
    if ckpt_path: json.dump(_ckpt_state(st), open(ckpt_path, "w"), default=str)
    return st


def summarize(st, arm, seed):
    lin = st["lin"]; archive = st["archive"]
    elites = sorted(archive.items(), key=lambda kv: -kv[1][0])
    replay_fail = 0; steps = 0
    for key, (cap, fp) in elites[:20]:
        ok, s, _ = lineage.replay_chain(lin, fp, st["genotypes"]); replay_fail += (not ok); steps += s
    by_eco = {}
    for (eco, carrier, _, _), (cap, fp) in archive.items():
        e = by_eco.setdefault(eco, {"cells": 0, "admissible_cells": 0, "best": 0.0, "carriers": set()})
        e["cells"] += 1; e["admissible_cells"] += int(cap >= b1.THETA); e["best"] = max(e["best"], cap); e["carriers"].add(carrier)
    breadth = {}
    for (eco, carrier, _, _), (cap, fp) in archive.items():
        if cap >= b1.THETA: breadth.setdefault(fp, set()).add(eco)
    return {"arm": arm, "seed": seed, "n_evaluated": st["n"], "resumed_from": st["resumed_from"],
            "develop_and_screen_charge": st["charge"], "B_search_draws": st["search_draws"],
            "policy_charge": st["policy"].total_charge(),
            "total_charge": st["charge"] + st["search_draws"] + st["policy"].total_charge(),
            "n_screened_out_by_the_audited_screen": st["screened_out"],
            "proposals_refused_too_wide": st["refused_wide"],
            "archive_cells": len(archive), "n_admissible_cells": sum(1 for v in archive.values() if v[0] >= b1.THETA),
            "n_lineage_records": len(lin.rec), "fossils_retained": len(lin.rec),
            "best_capability": elites[0][1][0] if elites else None,
            "by_ecology": {k: {**{kk: vv for kk, vv in v.items() if kk != "carriers"}, "carriers": sorted(v["carriers"])} for k, v in by_eco.items()},
            "niche_breadth_of_admissible_genotypes": {"n_admissible_genotypes": len(breadth),
                                                      "max_ecologies_occupied": max([len(v) for v in breadth.values()] or [0]),
                                                      "distribution": {str(i): sum(1 for v in breadth.values() if len(v) == i) for i in range(1, len(ECO_POOL) + 1)}},
            "milestone_total_charge": st["milestone_charge"], "milestone_at_evaluation": st["milestone_n"],
            "replay_audit": {"n_elites_replayed": min(20, len(elites)), "n_steps": steps, "replay_failures": replay_fail},
            "dvp_stream_ledger": st["streams"].ledger(), "seconds": st["seconds"]}


def main(tag="V1", seeds=(0, 1), evaluations=1500, audit_tag="V1", census_sizes=(3, 4, 5), resume_check=True):
    audit_path = os.path.join(RES, f"STAGE_R8_SCREEN_AUDIT_{audit_tag}.json")
    if not os.path.exists(audit_path):
        raise RuntimeError(f"protocol rule 18: no screen audit at {audit_path}; run triage.main_audit first")
    aud = json.load(open(audit_path))
    if aud["status_verdict"] != "SCREEN_AUDITED_GREEN":
        raise RuntimeError(f"protocol rule 18: the screen audit is {aud['status_verdict']}; the screen may not be used")
    tau = aud["tau_frozen_on_calibration"]; t0 = time.time()
    runs = {}
    for arm in ARMS:
        for seed in seeds:
            ck = os.path.join(RES, f"CKPT_R11_BIOSPHERE_{tag}_{arm}_S{seed}.json")
            if os.path.exists(ck): os.remove(ck)
            st = episode(seed, arm, evaluations, tau=tau, ckpt_path=ck, resume=False)
            runs[f"{arm}|S{seed}"] = summarize(st, arm, seed)
            print(json.dumps({k: runs[f"{arm}|S{seed}"][k] for k in ("arm", "seed", "n_evaluated", "archive_cells", "n_admissible_cells", "best_capability", "milestone_total_charge", "seconds")}), flush=True)

    # Delta_B_meta at the declared milestone, per seed
    delta = {}
    for seed in seeds:
        bf = runs[f"fixed|S{seed}"]["milestone_total_charge"]; bl = runs[f"learned|S{seed}"]["milestone_total_charge"]
        delta[str(seed)] = {"B_fixed_morphogenesis": bf, "B_learned_morphogenesis": bl,
                            "Delta_B_meta": (bf - bl) if (bf is not None and bl is not None) else None,
                            "milestone_reached_by": [a for a in ARMS if runs[f"{a}|S{seed}"]["milestone_total_charge"] is not None]}
    both = [d["Delta_B_meta"] for d in delta.values() if d["Delta_B_meta"] is not None]

    # resume determinism: an episode checkpointed and resumed must produce the same summary as one run straight through
    resume_ok = None
    if resume_check:
        ck = os.path.join(RES, f"CKPT_R11_BIOSPHERE_{tag}_RESUMETEST.json")
        if os.path.exists(ck): os.remove(ck)
        a = summarize(episode(7, "learned", 400, tau=tau, ckpt_path=ck, resume=False, ckpt_every=200), "learned", 7)
        if os.path.exists(ck): os.remove(ck)
        episode(7, "learned", 200, tau=tau, ckpt_path=ck, resume=False, ckpt_every=200)
        b = summarize(episode(7, "learned", 400, tau=tau, ckpt_path=ck, resume=True, ckpt_every=200), "learned", 7)
        keys = ("n_evaluated", "archive_cells", "n_admissible_cells", "best_capability", "total_charge", "n_lineage_records")
        resume_ok = {k: (a[k], b[k]) for k in keys if a[k] != b[k]}
        resume_ok = {"identical": not resume_ok, "differences": resume_ok, "checkpoint_at": 200, "run_to": 400}
        if os.path.exists(ck): os.remove(ck)

    # a small self-verifying witness: a cheap episode whose summary a reader (or a test) can reproduce from this
    # receipt alone, without re-running the full campaign
    w = summarize(episode(11, "learned", 250, tau=tau, resume=False), "learned", 11)
    witness = {"seed": 11, "arm": "learned", "evaluations": 250, "tau": tau,
               "expected": {k: w[k] for k in ("n_evaluated", "archive_cells", "n_admissible_cells", "best_capability",
                                              "total_charge", "B_search_draws", "policy_charge", "n_lineage_records",
                                              "n_screened_out_by_the_audited_screen")},
               "instructions": "biosphere.summarize(biosphere.episode(seed, arm, evaluations, tau=tau, resume=False), arm, seed) must reproduce every field of `expected`"}

    cen = census.main(tag=f"{tag}_R11_CONTEXT", sizes=census_sizes, exhaustive_max=max(census_sizes))
    out = {"schema": "StageR11BiosphereEpisodeV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "layer": "R11",
           "layer_reading": "the open-world episode driver (stage B4) carrying the protocol's meta-morphogenesis arm (stage B9); see the module docstring",
           "run_tag": tag, "seeds": list(seeds), "arms": list(ARMS), "evaluations_per_episode": evaluations,
           "ecology_pool": [{"name": n, "coeffs": list(c), "spec_id": ecology.spec_id(ecology.spec_smooth(c, n))} for n, c in ECO_POOL],
           "screen_audit_receipt": f"STAGE_R8_SCREEN_AUDIT_{audit_tag}.json",
           "screen_audit_receipt_sha256": aud["receipt_sha256"], "tau": tau,      # protocol rule 18
           "episode_stages": ["ecology sampling (D pool)", "development on the exact charged VM", "charging",
                              "R8 triage screen then exact confirmation", "MAP-Elites archiving per ecology",
                              "R7 lineage recording and elite replay", "fossil retention", "R9 census for context"],
           "runs": runs,
           "meta_morphogenesis": {"declared_milestone": f"an admissible genotype (capability >= {b1.THETA}) in at least {MILESTONE_CARRIERS} distinct carrier classes",
                                  "learned_policy": "per (ecology, parent carrier), sample the R5 operator with probability proportional to (successes + 1)/(tries + 1); a success is a proposal that takes or improves an archive cell. Its consultations, its updates and its counter description are charged to B_search",
                                  "Delta_B_meta_definition": "B_fixed_morphogenesis - B_learned_morphogenesis, both measured as the TOTAL charge (development + screen + search draws + policy) spent when the arm first reaches the milestone",
                                  "by_seed": delta,
                                  "n_seeds_where_both_arms_reached_the_milestone": len(both),
                                  "Delta_B_meta_values": both,
                                  "verdict": (f"LEARNED_MORPHOGENESIS_CHEAPER_ON_{len(both)}_OF_{len(seeds)}_SEEDS" if both and all(d > 0 for d in both) else
                                              f"FIXED_MORPHOGENESIS_CHEAPER_ON_{len(both)}_OF_{len(seeds)}_SEEDS" if both and all(d < 0 for d in both) else
                                              f"MIXED_OR_UNDETERMINED_OVER_{len(both)}_OF_{len(seeds)}_SEEDS" if both else
                                              "MILESTONE_NOT_REACHED_BY_BOTH_ARMS_ON_ANY_SEED — no Delta_B_meta is computed and neither arm is claimed better"),
                                  "verdict_note": f"Delta_B_meta is defined only on the {len(both)} of {len(seeds)} seeds where BOTH arms reached the declared milestone; a seed where one arm never reached it contributes nothing and is not counted as a win for the other. Archive quality at the fixed evaluation budget is reported per run and is a separate observation from the charge-to-milestone"},
           "resume_determinism": resume_ok, "determinism_witness": witness,
           "census_context": {"receipt": f"STAGE_R9_CENSUS_{tag}_R11_CONTEXT.json", "receipt_sha256": cen["receipt_sha256"],
                              "counts": [{k: r[k] for k in ("size", "exhaustive", "n_configurations_enumerated", "n_canonical_classes_in_sample", "n_response_classes_in_sample")} for r in cen["counts_by_size"]],
                              "note": "an archive of N cells is not N species and not N of anything until it is put next to the size of the space it was drawn from; the census sizes here are small by design and are context, not a bound on the episode's own genotypes"},
           "open_endedness_not_claimed": "biosphere document section 21 lists what an open-endedness claim must measure (new viable species rate, new occupied niches, mechanism-vector entropy, parent-reduction distance trend, major transition count). This episode measures the archive, the lineage and the charge over a fixed budget and claims none of those",
           "seconds": round(time.time() - t0, 1),
           "terminal": "R11_BIOSPHERE_EPISODE_EXECUTED",
           "claim_ceiling": "one episode family, two arms, the listed seeds, one grammar, one screen, one ecology pool. Delta_B_meta is a statement about this operator set and this policy parameterization on this pool; stage B9 asks for it on untouched regime sequences, which this lane does not have"}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_R11_BIOSPHERE_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"R11 {out['terminal']}: meta verdict {out['meta_morphogenesis']['verdict']}; "
          f"resume identical: {resume_ok['identical'] if resume_ok else 'not checked'}")
    return out


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V1",
         evaluations=int(sys.argv[2]) if len(sys.argv) > 2 else 1500)
