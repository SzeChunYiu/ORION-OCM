"""R6 — quality-diversity (MAP-Elites) search over the neutral blind-recovery grammar, and the revival of the standing
negative result RV-377-023 / RV-377-028 (neutral search plateaus at a context-conditioned memory and never assembles the
certified dense learner).

DIAGNOSIS that justifies this instrument (executed before the change, recorded in RV-377-057):
  * the planted dense learner (score 0.9196, size 47) is NOT an isolated peak: of 400 single Koza subtree mutations,
    22 match or beat it, 21.7% stay at or above theta = 0.85, and 73.5% stay above the evolved plateau;
  * the evolved plateau elite (size 12) sits in a CLOSED basin: of 400 single mutations, none reaches 0.85 and the best
    is 0.7312;
  * the two basins differ by a factor of four in program size, and regularized evolution as run in RV-028 breaks score
    ties by PREFERRING THE SMALLER program, so the search is under a parsimony pressure that points away from the only
    region where the target lives.
The minimal justified change is therefore not a bigger budget (RV-028 spent 10^6 evaluations per seed) but an archive
that makes structural size a niche coordinate instead of a tie-break: MAP-Elites (Mouret & Clune 2015; Cully, Clune,
Tarapore & Mouret 2015) illuminates the (size x output-drift x output-spread) space and keeps a large, currently
mediocre structure alive in its own cell instead of letting a small one out-compete it.

Descriptors (label-free, behavioural or structural; no target information):
  d1 SIZE        program size of (f, g) in {<=8, 9-14, 15-22, 23-34, 35-50, >50}
  d2 OUTDRIFT    number of inputs whose served output at the end differs from its output at the midpoint of development
                 (how much the machine's behaviour is changed BY EXPERIENCE - the behavioural signature of a learner,
                 computed without any target information), in {0, 1, 2, 3-4, 5-8, >8}
  d3 OUTSPREAD   number of distinct served outputs over the 16 inputs at the end, in {1, 2, 3-4, 5-8, 9-16, >16}
Archive: 6 x 6 x 6 = 216 cells, each holding the best-scoring genotype seen in it.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from . import blind
from .core import clamp, fx, sha256_of
from .fast import ONE, _bits, compile_candidate, cand_size

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
SIZE_EDGES = (8, 14, 22, 34, 50)
SPREAD_EDGES = (1, 2, 4, 8, 16)
DRIFT_EDGES = (0, 1, 2, 4, 8)


def _bucket(v, edges):
    for i, e in enumerate(edges):
        if v <= e: return i
    return len(edges)


def score_and_desc(cand, eco, n_bits=8):
    """one replay per target; returns (mean score, descriptor tuple). Descriptors come from the FIRST target's replay."""
    fc = compile_candidate(cand); f, writes = fc
    targets = eco["targets"] if eco.get("kind") == "smooth_div" else [eco["target"]]
    train, all_x, events = eco["train"], eco["all_x"], eco["events"]
    total = 0.0; desc = None
    for ti, target in enumerate(targets):
        cells = [0, 0, 0, 0]; st = {}; mid_outs = None
        for t in range(events):
            if t == events // 2:
                mid_outs = [f(cells, {"x": xx, "bits": _bits(xx, n_bits), "st": st}) for xx in all_x]
            x = train[t % len(train)]; y = target[x]
            env = {"x": x, "bits": _bits(x, n_bits), "st": st}
            out = f(cells, env); env["y"] = y; env["out"] = out; env["e"] = clamp(out - y)
            for tc, ex in writes:
                val = ex(cells, env)
                if tc == "INSERT": st[x] = val
                else: cells[int(tc[1])] = clamp(val)
        outs = [f(cells, {"x": x, "bits": _bits(x, n_bits), "st": st}) for x in all_x]
        err = sum(abs(o - target[x]) for o, x in zip(outs, all_x))
        total += max(0.0, 1.0 - err / 16 / len(all_x) / 1.5)
        if ti == 0:
            drift = sum(1 for a, b in zip(outs, mid_outs or outs) if a != b)
            desc = (_bucket(cand_size(cand), SIZE_EDGES), _bucket(drift, DRIFT_EDGES), _bucket(len(set(outs)), SPREAD_EDGES))
    return round(total / len(targets), 4), desc


IDX_LEAVES = {f"{p}{i}": (p, i) for p in ("x", "c") for i in range(4)}


def _shift_leaves(t, d):
    """consistently re-index the input and cell leaves of a subtree by d (mod 4): x_i -> x_{(i+d)%4}, c_i -> c_{(i+d)%4}.
    Every other leaf is untouched. This is the symmetry of the four input bits and the four state cells."""
    if isinstance(t, str):
        pi = IDX_LEAVES.get(t)
        return f"{pi[0]}{(pi[1] + d) % 4}" if pi else t
    return [t[0]] + [_shift_leaves(x, d) for x in t[1:]]


def duplicate_reindex(rng, cand):
    """R5 morphogenesis operator 'clone / specialize factor' (GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1 section 8): clone an
    update rule or a served-computation term and shift its input/cell indices, i.e. gene duplication with divergence.
    This is the operator whose ABSENCE blocked neutral recovery in RV-377-023/028: the path to the certified learner
    needs whole coordinated rules added one at a time, and no point mutation can add one."""
    child = json.loads(json.dumps(cand)); d = rng.choice((1, 2, 3))
    if child["g"] and rng.random() < 0.6:
        tc, ex = child["g"][rng.randrange(len(child["g"]))]
        if tc == "INSERT": new_tc = "INSERT"
        else: new_tc = f"c{(int(tc[1]) + d) % 4}"
        child["g"] = [w for w in child["g"] if w[0] != new_tc] + [[new_tc, _shift_leaves(ex, d)]]
        if len(child["g"]) > 4: child["g"] = child["g"][-4:]
    else:
        paths = list(blind._paths(child["f"]))
        if not paths: return child
        _, sub = rng.choice(paths)
        child["f"] = ["ADD", child["f"], _shift_leaves(json.loads(json.dumps(sub)), d)]
    return child


def crossover(rng, a, b):
    """R5 recombination: swap one random subtree of a with one random subtree of b (typed by leaf set), or swap one
    write-expression of g. Structural jumps that single-point mutation cannot make."""
    child = json.loads(json.dumps(a))
    if rng.random() < 0.5 or not b["g"] or not child["g"]:
        pa = list(blind._paths(child["f"])); pb = list(blind._paths(b["f"]))
        if pa and pb: child["f"] = blind._replace(child["f"], rng.choice(pa)[0], json.loads(json.dumps(rng.choice(pb)[1])))
    else:
        i = rng.randrange(len(child["g"])); j = rng.randrange(len(b["g"]))
        child["g"][i] = [child["g"][i][0], json.loads(json.dumps(b["g"][j][1]))]
    return child


def map_elites(eco, seed, evaluations=1000000, n_init=2000, log_every=25000, ckpt_path=None, ckpt_every=100000, log=None, use_dup=True):
    rng = random.Random(seed)
    archive = {}          # descriptor -> (score, candidate, size)
    geno_cache = {}       # canonical genotype -> score (the RV-028 caches, kept)
    n = 0; t0 = time.time(); hits = 0; history = []
    def place(cand):
        nonlocal n, hits
        key = json.dumps(cand, sort_keys=True)
        if key in geno_cache: hits += 1; return None
        s, d = score_and_desc(cand, eco); geno_cache[key] = s; n += 1
        cur = archive.get(d)
        if cur is None or s > cur[0]: archive[d] = (s, cand, cand_size(cand))
        return s
    for _ in range(n_init):
        place(blind.rand_candidate(rng))
        if n >= evaluations: break
    while n < evaluations:
        vals = list(archive.values())
        _, parent, _ = rng.choice(vals)
        u = rng.random()
        if u < 0.20 and len(vals) > 1:
            _, other, _ = rng.choice(vals); child = crossover(rng, parent, other)
        elif use_dup and u < 0.45:
            child = duplicate_reindex(rng, parent)
        else:
            child = blind.mutate_gp(rng, parent)
        place(child)
        if n % log_every == 0:
            best = max(archive.values(), key=lambda v: v[0])
            rec = {"n_eval": n, "best": best[0], "best_size": best[2], "cells_filled": len(archive), "geno_hits": hits, "sec": round(time.time() - t0, 1)}
            history.append(rec)
            print(json.dumps(rec), flush=True)
            if log: open(log, "a").write(json.dumps(rec) + "\n")
        if ckpt_path and n % ckpt_every == 0:
            json.dump({"n": n, "archive": [[list(k), v[0], v[1], v[2]] for k, v in archive.items()]}, open(ckpt_path, "w"))
    return archive, n, hits, history


def main(seed=5, evaluations=1000000, tag="RUN10_QD_MAPELITES", log=None, use_dup=True):
    eco = blind.ecology_div()
    planted = blind.PLANTED_LEARNER_SMOOTH8_LR4
    planted_score, planted_desc = score_and_desc(planted, eco)
    archive, n, hits, history = map_elites(eco, seed, evaluations, ckpt_path=os.path.join(RES, f"CKPT_{tag}_S{seed}.json"), log=log, use_dup=use_dup)
    elites = sorted(archive.items(), key=lambda kv: -kv[1][0])
    top = [{"descriptor": list(k), "score": v[0], "size": v[2], "class": blind.classify_locality_v2({"used_store": k[1] >= 1, "n_fx_cells_written": k[1], "max_writes": k[1]}, v[1]) if hasattr(blind, "classify_locality_v2") else "", "f": json.dumps(v[1]["f"]), "g": json.dumps(v[1]["g"])} for k, v in elites[:12]]
    winners = [e for e in top if e["score"] >= blind.THETA_SMOOTH]
    receipt = {"schema": "StageFBlindRecoveryQDV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "revival_record": "RV-377-057", "run_tag": tag, "seed": seed,
               "duplicate_and_reindex_operator_enabled": use_dup, "search_family": "MAP-Elites quality diversity (Mouret & Clune 2015) over the neutral grammar: descriptors (program size bucket, plasticity 0-5, output-spread bucket), 6x6x6 = 216 cells, uniform elite selection, Koza subtree mutation, genotype cache; NO fitness-proportional selection and NO size tie-break",
               "ecology": {"kind": eco.get("kind"), "events": eco["events"], "n_targets": len(eco.get("targets", [1]))}, "n_evaluations": n, "genotype_cache_hits": hits,
               "planted_learner_score_in_this_ecology": planted_score, "planted_learner_descriptor": list(planted_desc), "planted_learner_size": cand_size(planted),
               "theta": blind.THETA_SMOOTH, "archive_cells_filled": len(archive), "archive_cells_total": 216,
               "best_score": elites[0][1][0] if elites else None, "n_winners_at_theta": len(winners), "winner_classes": sorted({w["class"] for w in winners}),
               "top_elites": top, "history": history,
               "score_by_size_bucket": {str(b): max([v[0] for k, v in archive.items() if k[0] == b] or [None]) for b in range(6)},
               "claim_ceiling": "exact charged-grammar replay; one ecology (four sign-flipped smooth targets); one seed per receipt"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_F_BLIND_RECOVERY_{tag}_S{seed}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("best", receipt["best_score"], "planted", planted_score, "cells", len(archive), "winners", len(winners))
    return receipt


if __name__ == "__main__":
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    ev = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
    nodup = "--nodup" in sys.argv
    main(s, ev, tag="RUN10B_QD_NODUP_ABLATION" if nodup else "RUN10_QD_MAPELITES",
         log=next((a for a in sys.argv[3:] if not a.startswith("--")), None), use_dup=not nodup)
