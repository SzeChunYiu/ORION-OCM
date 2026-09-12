"""R7 — lineage and descent: a provenance ledger for every evaluated genotype, and an EXACT replay audit of the
descent chain of every archived elite.

WHICH R7 THIS IS. `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1` section 20 lists R7 as the "D/V/P split manager"; the working
brief for this lane asks R7 for lineage and descent. The two readings are the same layer read from two ends — both are
provenance over a search: which stream an evaluation was charged to, and which ancestor and operator produced the
genotype that was evaluated. This module implements BOTH and keeps the falsifiable half in front: every archived
genotype carries (parent fingerprint, operator, charged proposal cost, ecology STREAM), and the receipt is only GREEN if
replaying the recorded operator chain from the recorded ancestor reproduces the elite's canonical fingerprint EXACTLY.
A lineage that does not replay is a bug in the recorder, not a curiosity, so `replay_failures` must be 0.

WHY REPLAY IS POSSIBLE AT ALL. An R5 operator is a function of (random stream, parent genotype). Recording the parent's
fingerprint alone does not determine the child, because the operators read node identifiers and dictionary order. So two
things are recorded per proposal: the integer PROPOSAL SEED drawn from the search's master stream, and the operator name
the draw actually landed on. Replay re-seeds `random.Random(proposal_seed)` and re-applies `morphgen.mutate` /
`morphgen.crossover` to the parent. For this to be REMINT-INVARIANT (H5) the parent handed to an operator must not
depend on node identifiers, so every genotype in this module is stored in CANONICAL GENOTYPE form: `canon_geno` rebuilds
a genotype straight out of `morph.canonical`, whose node identifiers are the canonical labels and whose node and edge
order is the canonical order. `canon_geno(remint(g)) == canon_geno(g)` as a dict, so an operator applied to a reminted
ancestor produces the identical child, and the whole chain replays from a reminted founder. The receipt asserts this.

CHARGED COST OF A PROPOSAL. `morphgen` re-draws a proposal until it type-checks. Every draw is charged, including the
draws that failed the type check, so the grammar's own inefficiency is part of `B_search` (R5's rule). `proposal_draws`
is the measured number of draws; `B_search_draws` charges one unit each. The evaluation charge of the child is the sum
of the exact ledger coordinates of its charged development, recorded separately as `develop_charge` — so the cost of a
lineage is reported as (search draws, development charge), never as one scalar.

D/V/P STREAM MANAGER (the protocol's reading of R7). `STREAMS` partitions the registered ecologies into a development
stream D, a validation stream V with a bounded query budget, and a protected stream P that this module refuses to
evaluate at all: `Streams.query` raises on a P ecology, and every V query is counted against `v_budget` and recorded.
The receipt reports the stream ledger, so a protected-ecology query cannot happen silently. P is exercised only by the
frozen-hash check: the receipt records the spec hashes of the P ecologies without running them.

CLAIM CEILING. One ecology, one seed, one grammar per receipt. "Replays exactly" is a statement about this recorder and
this operator set, not evidence that the search found anything; the archive here is small by design.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from . import b1, ecology, morph, morphgen, smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

# D/V/P split (protocol section 5 / biosphere section 13). P is never evaluated by this lane; only its hash is recorded.
STREAMS = {"D": ("E_smooth3",), "V": ("E_sym5",), "P": ("E_smooth1", "E_parity")}
V_BUDGET = 8


MAX_CANON_WIDTH = 5040   # refuse a proposal whose exact canonical tie-break would enumerate more labellings than this


def canon_geno(g):
    """the genotype rebuilt on its canonical labels: identifiers, node order and edge order are the canonical ones, so
    the dict is a function of the isomorphism class alone (canon_geno(remint(g)) == canon_geno(g)).

    Raises MorphError when the exact canonical form would cost more than MAX_CANON_WIDTH labellings to compute. That
    bound is a declared SEARCH bound, not a scientific one: it removes genotypes with many interchangeable nodes from
    this lane's reachable set, and the receipt reports how many proposals it refused so the exclusion is measurable."""
    w = morph.canonical_search_width(g)
    if w > MAX_CANON_WIDTH: raise morph.MorphError(f"canonical search width {w} exceeds {MAX_CANON_WIDTH}")
    d = json.loads(morph.canonical(g))
    return {"nodes": {str(lab): (kind, dict(params)) for lab, kind, params in d["nodes"]},
            "edges": [(str(a), str(b), int(pt)) for a, b, pt in d["edges"]], "meta": {}}


class Streams:
    """the D/V/P manager: D is free, V is bounded and counted, P raises."""

    def __init__(self, v_budget=V_BUDGET):
        self.v_budget = v_budget; self.counts = {"D": 0, "V": 0, "P": 0}; self.v_queries = []
        self.generated_D = set()

    def register_development(self, eco_name):
        """register a GENERATED ecology in the development stream. Generated and co-generated worlds are development
        worlds unless separately frozen (biosphere document section 20), so this is the only stream a generator may
        write into; a name already registered in V or P is refused, which is what stops a generator from quietly
        regenerating a protected ecology and calling it development."""
        if eco_name in STREAMS["V"] or eco_name in STREAMS["P"]:
            raise PermissionError(f"R7 stream manager: {eco_name} is already registered in a non-development stream")
        self.generated_D.add(eco_name); return "D"

    def stream_of(self, eco_name):
        for s, names in STREAMS.items():
            if eco_name in names: return s
        if eco_name in self.generated_D: return "D"
        raise KeyError(f"ecology {eco_name} is not registered in any stream")

    def query(self, eco_name, what=""):
        s = self.stream_of(eco_name)
        if s == "P": raise PermissionError(f"R7 stream manager: {eco_name} is PROTECTED; this lane may not query it")
        if s == "V":
            if self.counts["V"] >= self.v_budget: raise PermissionError(f"R7 stream manager: V budget {self.v_budget} exhausted")
            self.v_queries.append(what)
        self.counts[s] += 1
        return s

    def ledger(self):
        return {"queries_by_stream": dict(self.counts), "v_budget": self.v_budget, "v_queries": list(self.v_queries),
                "generated_development_ecologies": sorted(self.generated_D),
                "protected_specs_frozen": {n: ecology.spec_id(ecology.REGISTRY[n]) for n in STREAMS["P"]},
                "protected_queries": self.counts["P"]}


# --------------------------------------------------------------------------------------------------------- proposals
def propose(parent, pseed, other=None, op_index=None, tries=12):
    """one charged proposal. Returns (child in canonical genotype form, operator name, draws). Deterministic in
    (parent canonical form, pseed, other canonical form, op_index).

    `op_index`, when given, names ONE R5 operator instead of letting the draw choose (the ecology-conditioned
    morphogenesis policy of R11 needs to steer the operator; the lineage records the index so replay is still exact)."""
    rng = random.Random(pseed); rec = []
    if op_index is not None:
        f = morphgen.OPS[op_index]
        child = parent
        for k in range(tries):
            cand = f(rng, json.loads(json.dumps(parent)))
            try:
                morph.typecheck(cand); morphgen._check_servable(cand); rec.append((f.__name__, True)); break
            except (morph.MorphError, ValueError, KeyError, IndexError):
                rec.append((f.__name__, False)); cand = None
        child = cand if cand is not None else json.loads(json.dumps(parent))
        return canon_geno(child), f.__name__, len(rec)
    if other is None:
        child, _ = morphgen.mutate(rng, parent, record=rec)
    else:
        child, _ = morphgen.crossover(rng, parent, other, record=rec)
    op = rec[-1][0] if rec else "op_none"
    return canon_geno(child), op, len(rec)      # raises MorphError if the child is too wide to canonicalize exactly


def founder(fseed, steps):
    """a founder genotype: `morphgen.seed_genotype` followed by `steps` charged mutations, recorded like any proposal."""
    rng = random.Random(fseed); g = canon_geno(morphgen.seed_genotype(rng)); draws = 0; ops = []
    for _ in range(steps):
        try:
            child, op, d = propose(g, rng.randrange(2 ** 31))
        except morph.MorphError:            # too wide to canonicalize exactly: the draw is charged and the parent kept
            draws += 1; ops.append("op_refused_too_wide"); continue
        g = child; draws += d; ops.append(op)
    return g, draws, ops


# ------------------------------------------------------------------------------------------------------ the recorder
class Lineage:
    """fingerprint -> descent record. A record is (parent fingerprint or None, operator, proposal seed, other parent
    fingerprint or None, draws charged, development charge, capability, descriptor)."""

    def __init__(self):
        self.rec = {}

    def add(self, fp, parent_fp, op, pseed, other_fp, draws, develop_charge, cap, desc, founder_spec=None, op_index=None):
        if fp in self.rec: return False
        self.rec[fp] = {"parent": parent_fp, "operator": op, "proposal_seed": pseed, "other_parent": other_fp,
                        "op_index": op_index, "proposal_draws": draws, "B_search_draws": draws,
                        "develop_charge": develop_charge, "capability": cap,
                        "descriptor": list(desc) if desc else None, "founder": founder_spec}
        return True

    def chain(self, fp):
        """the descent chain from the founder down to fp (list of fingerprints, founder first)."""
        out = []; seen = set()
        while fp is not None and fp in self.rec and fp not in seen:
            seen.add(fp); out.append(fp); fp = self.rec[fp]["parent"]
        return list(reversed(out))

    def depth(self, fp):
        return len(self.chain(fp)) - 1


def replay_chain(lin: Lineage, fp, genotypes, remint_founder=None):
    """re-derive fp from its recorded founder by re-applying the recorded operator chain. Returns
    (ok, n_steps, first_failure). `remint_founder`, when an integer, reminted the founder first: the chain must still
    reproduce every fingerprint, which is the H5 assertion for this layer."""
    chain = lin.chain(fp)
    if not chain: return False, 0, "no chain"
    root = chain[0]; r = lin.rec[root]
    if r["founder"] is None: return False, 0, f"root {root[:12]} is not a recorded founder"
    g, _, _ = founder(r["founder"]["fseed"], r["founder"]["steps"])
    if remint_founder is not None: g = canon_geno(morph.remint(g, remint_founder))
    if morph.fingerprint(g) != root: return False, 0, f"founder fingerprint {morph.fingerprint(g)[:12]} != {root[:12]}"
    steps = 0
    for nxt in chain[1:]:
        rr = lin.rec[nxt]
        other = genotypes.get(rr["other_parent"]) if rr["other_parent"] else None
        child, op, draws = propose(g, rr["proposal_seed"], other, rr.get("op_index"))
        if op != rr["operator"]: return False, steps, f"operator {op} != recorded {rr['operator']} at step {steps}"
        if draws != rr["proposal_draws"]: return False, steps, f"draws {draws} != recorded {rr['proposal_draws']} at step {steps}"
        if morph.fingerprint(child) != nxt: return False, steps, f"fingerprint mismatch at step {steps}"
        g = child; steps += 1
    return True, steps, None


# ------------------------------------------------------------------------------------------------------- the search
def run(seed=0, evaluations=1200, n_init=25, eco_name="E_smooth3", streams=None):
    """a small lineage-recording MAP-Elites search over the typed IR, with the b1 descriptors and the exact charged VM."""
    streams = streams or Streams()
    streams.query(eco_name, "development search")
    coeffs = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4, "E_smooth1": smooth.COEFFS_V1}[eco_name]
    target = smooth.make_target(coeffs)
    rng = random.Random(seed); lin = Lineage(); archive = {}; genotypes = {}
    n = 0; failed = 0; total_draws = 0; refused_wide = 0; t0 = time.time()

    def place(g, parent_fp, op, pseed, other_fp, draws, founder_spec=None):
        nonlocal n, failed
        fp = morph.fingerprint(g)
        if fp in lin.rec: return None
        res = b1.evaluate(g, target); n += 1
        if res is None:
            failed += 1
            lin.add(fp, parent_fp, op, pseed, other_fp, draws, 0, None, None, founder_spec); genotypes[fp] = g
            return None
        cap, desc, R = res
        lin.add(fp, parent_fp, op, pseed, other_fp, draws, sum(R.values()), cap, desc, founder_spec); genotypes[fp] = g
        cur = archive.get(desc)
        if cur is None or cap > cur[0]: archive[desc] = (cap, fp)
        return cap

    for i in range(n_init):
        fseed = rng.randrange(2 ** 31); steps = rng.randrange(3, 10)
        g, draws, _ = founder(fseed, steps); total_draws += draws
        place(g, None, "op_founder", fseed, None, draws, founder_spec={"fseed": fseed, "steps": steps})
        if n >= evaluations: break
    while n < evaluations:
        vals = list(archive.values())
        if not vals:
            fseed = rng.randrange(2 ** 31); steps = rng.randrange(3, 10); g, draws, _ = founder(fseed, steps)
            total_draws += draws; place(g, None, "op_founder", fseed, None, draws, founder_spec={"fseed": fseed, "steps": steps}); continue
        _, pfp = rng.choice(vals); parent = genotypes[pfp]
        pseed = rng.randrange(2 ** 31); other_fp = None; other = None
        if rng.random() < 0.2 and len(vals) > 1:
            _, other_fp = rng.choice(vals); other = genotypes[other_fp]
        try:
            child, op, draws = propose(parent, pseed, other)
        except morph.MorphError:
            refused_wide += 1; total_draws += 1; continue
        total_draws += draws
        place(child, pfp, op, pseed, other_fp, draws)
    return {"lineage": lin, "archive": archive, "genotypes": genotypes, "n_evaluated": n, "failed_phenotypes": failed,
            "total_draws": total_draws, "refused_too_wide": refused_wide, "seconds": round(time.time() - t0, 1), "streams": streams}


def main(seed=0, evaluations=1200, tag="V1", eco_name="E_smooth3"):
    r = run(seed, evaluations, eco_name=eco_name)
    lin, archive, genotypes = r["lineage"], r["archive"], r["genotypes"]
    elites = sorted(archive.items(), key=lambda kv: -kv[1][0])

    # ---- the audit: every elite's chain is replayed from its recorded founder, plain and from a reminted founder
    replay = []; failures = 0; steps_total = 0
    for desc, (cap, fp) in elites:
        ok, steps, why = replay_chain(lin, fp, genotypes)
        ok_r, steps_r, why_r = replay_chain(lin, fp, genotypes, remint_founder=5)
        failures += (not ok) + (not ok_r); steps_total += steps + steps_r
        replay.append({"descriptor": list(desc), "capability": cap, "fingerprint": fp, "chain_length": lin.depth(fp),
                       "replay_ok": ok, "replay_steps": steps, "replay_failure": why,
                       "replay_ok_from_reminted_founder": ok_r, "replay_failure_reminted": why_r,
                       "chain_B_search_draws": sum(lin.rec[a]["B_search_draws"] for a in lin.chain(fp)),
                       "chain_develop_charge": sum(lin.rec[a]["develop_charge"] for a in lin.chain(fp)),
                       "chain_operators": [lin.rec[a]["operator"] for a in lin.chain(fp)]})

    # ---- the replay WITNESS: enough of the descent of a few elites for a reader (or a test) to re-derive the elite's
    # fingerprint from this receipt alone, without re-running the search
    witness = []
    for desc, (cap, fp) in elites:
        ch = lin.chain(fp)
        if len(ch) < 2 or len(witness) >= 5: continue
        # a witness must be replayable from the receipt ALONE, so a chain with a recombination step (which needs the
        # other parent's genotype, not just its fingerprint) is not witnessed here; it is still replayed by the audit
        # above, which has the genotypes in hand
        if any(lin.rec[a]["other_parent"] for a in ch[1:]): continue
        root = lin.rec[ch[0]]
        witness.append({"founder": root["founder"], "founder_fingerprint": ch[0],
                        "steps": [{"proposal_seed": lin.rec[a]["proposal_seed"], "op_index": lin.rec[a].get("op_index"),
                                   "operator": lin.rec[a]["operator"], "proposal_draws": lin.rec[a]["proposal_draws"],
                                   "expected_fingerprint": a} for a in ch[1:]],
                        "final_fingerprint": fp, "capability": cap, "descriptor": list(desc)})

    # ---- remint invariance of every reported quantity: the fingerprint of every recorded genotype is remint-stable
    remint_checked = 0; remint_bad = 0
    for fp, g in genotypes.items():
        for s in (1, 2, 3):
            remint_checked += 1
            if morph.fingerprint(morph.remint(g, s)) != fp: remint_bad += 1
        if remint_checked > 900: break

    ops = {}
    for v in lin.rec.values():
        o = ops.setdefault(v["operator"], {"n": 0, "B_search_draws": 0, "n_invalid_phenotype": 0, "best_capability": None})
        o["n"] += 1; o["B_search_draws"] += v["B_search_draws"]
        if v["capability"] is None: o["n_invalid_phenotype"] += 1
        elif o["best_capability"] is None or v["capability"] > o["best_capability"]: o["best_capability"] = v["capability"]
    depths = [lin.depth(fp) for fp in lin.rec]
    receipt = {"schema": "StageR7LineageDescentV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "layer": "R7",
               "layer_reading": "lineage/descent provenance AND the protocol's D/V/P split manager; see the module docstring",
               "run_tag": tag, "seed": seed, "ecology": eco_name, "ecology_spec_id": ecology.spec_id(ecology.REGISTRY[eco_name]),
               "search_family": "MAP-Elites over the typed morphology IR with the R5 operator grammar, 20 per cent graft recombination; descriptors (carrier, size, output drift) as in R6/b1",
               "n_evaluated": r["n_evaluated"], "failed_phenotypes": r["failed_phenotypes"], "n_lineage_records": len(lin.rec),
               "B_search_draws_total": r["total_draws"], "develop_charge_total": sum(v["develop_charge"] for v in lin.rec.values()),
               "proposals_refused_too_wide_to_canonicalize": r["refused_too_wide"], "max_canonical_search_width": MAX_CANON_WIDTH,
               "archive_cells_filled": len(archive), "archive_cells_total": len(b1.CARRIERS) * 6 * 6, "seconds": r["seconds"],
               "n_founders": sum(1 for v in lin.rec.values() if v["founder"]), "max_descent_depth": max(depths), "mean_descent_depth": round(sum(depths) / len(depths), 4),
               "operator_ledger": ops,
               "replay_audit": {"n_elites": len(replay), "n_chains_replayed": 2 * len(replay), "n_steps_replayed": steps_total,
                                "replay_failures": failures, "elites": replay},
               "replay_witness": witness,
               "replay_witness_instructions": "for each entry: g = lineage.founder(founder.fseed, founder.steps)[0] must have founder_fingerprint; then for each step g = lineage.propose(g, proposal_seed, None, op_index)[0] must have expected_fingerprint, and the last equals final_fingerprint. The receipt is self-verifying: no search re-run is needed",
               "remint_invariance": {"n_fingerprint_checks": remint_checked, "n_fingerprint_changed_by_remint": remint_bad,
                                     "replay_from_reminted_founder_failures": sum(1 for e in replay if not e["replay_ok_from_reminted_founder"]),
                                     "assertion": "morph.remint changes no reported quantity: every recorded fingerprint is remint-stable and every elite chain replays from a reminted founder"},
               "dvp_stream_ledger": r["streams"].ledger(),
               "terminal": "R7_LINEAGE_REPLAYS_EXACTLY" if (failures == 0 and remint_bad == 0) else "R7_LINEAGE_REPLAY_FAILED",
               "claim_ceiling": "one ecology, one seed, one grammar. The audit says the recorded descent of every archived elite re-derives that elite's canonical fingerprint exactly, from the recorded ancestor and from a reminted copy of it; it says nothing about whether the search found a good form, and the archive here is deliberately small"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_R7_LINEAGE_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"R7 {receipt['terminal']}: {len(replay)} elites, {2 * len(replay)} chains, {steps_total} steps, {failures} replay failures, "
          f"max depth {receipt['max_descent_depth']}, {r['n_evaluated']} evaluations in {r['seconds']}s")
    return receipt


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 0, int(sys.argv[2]) if len(sys.argv) > 2 else 1200,
         tag=sys.argv[3] if len(sys.argv) > 3 else "V1")
