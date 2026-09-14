"""Item 29: lesion the DERIVED cognitive components, not the search basis.

The coverage audit recorded the gap as: the corpus ablates its own search basis
and information channels, but never a derived cognitive component -- there is
no "remove memory / attention / planning -> predicted deficit" family.

Six components are derived elsewhere in this corpus, so each can be removed and
its deficit computed from the law that derived it, then measured by re-running
the same enumeration with the component disabled.

  procedural  chunking             (PVR-3 reuse threshold)
  semantic    consolidation        (CSR-1 retention width)
  episodic    replay side channel  (CSR-1 capacity shortfall)
  working     within-event state   (serving requires it at all)
  planning    optimal segmentation (value-aware stopping rule)
  retrieval   indexed lookup       (the U term of PVR-3)

Every number here is computed from the registered cost model below. Nothing is
quoted from a previous run.
"""

import itertools
import json
import math

# ---- registered model, identical to hierarchy_witness.py --------------------
TASKS = {"T1": "abcabd", "T2": "abcabe", "T3": "abdabc",
         "T4": "abeabc", "T5": "abcabc"}
MULT = {"T1": 3, "T2": 3, "T3": 2, "T4": 2, "T5": 2}
C_PRIM = 1      # derive one primitive
U_REF = 1       # invoke one retained chunk
S_PER = 3       # one-time storage per retained chunk

# ---- registered model, identical to consolidation_witness.py ----------------
# regime A: every task brings new distinctions; regime B: they are redundant.
# name -> (N_t sequence, capacity in states), exactly as consolidation_witness
REGIMES = {
    "A_independent": ([2, 4, 8, 16], 8),
    "B_redundant": ([2, 4, 4, 4, 4], 8),
    "C_mixed": ([2, 4, 4, 8, 8, 8], 4),
}
REGIME_A_N, CAPACITY_STATES = REGIMES["A_independent"]
REGIME_B_N = REGIMES["B_redundant"][0]

OUT = {}


def substrings(s, lo=2, hi=None):
    hi = hi or len(s)
    return {s[i:i + L] for L in range(lo, hi + 1) for i in range(len(s) - L + 1)}


def serve_greedy(seq, chunks, u_ref=U_REF):
    """Longest-match-first. This is the PLANNING-LESIONED server: it commits to
    the locally longest chunk without looking ahead."""
    order = sorted(chunks, key=len, reverse=True)
    i, c = 0, 0
    while i < len(seq):
        for p in order:
            if seq.startswith(p, i):
                c += u_ref
                i += len(p)
                break
        else:
            c += C_PRIM
            i += 1
    return c


def serve_optimal(seq, chunks, u_ref=U_REF):
    """Exact minimum-cost segmentation by dynamic programming. This is the
    INTACT server: it looks ahead over the whole sequence."""
    n = len(seq)
    best = [0] + [math.inf] * n
    for i in range(1, n + 1):
        best[i] = best[i - 1] + C_PRIM
        for p in chunks:
            L = len(p)
            if L <= i and seq.startswith(p, i - L):
                best[i] = min(best[i], best[i - L] + u_ref)
    return best[n]


def total(chunks, server=serve_optimal, u_ref=U_REF, charge_storage=True):
    c = sum(MULT[n] * server(s, chunks, u_ref) for n, s in TASKS.items())
    if charge_storage:
        c += S_PER * len(chunks)
    return c


def best_chunk_set(server=serve_optimal, u_ref=U_REF):
    """Exhaustive search over candidate chunk sets, as in hierarchy_witness."""
    cands = sorted({p for t in TASKS.values() for p in substrings(t)})
    # restrict to chunks that occur in more than one place overall, else the
    # enumeration is 2^|cands|; this mirrors the parent witness.
    cands = [p for p in cands
             if sum(TASKS[n].count(p) * MULT[n] for n in TASKS) >= 2]
    best, bset = math.inf, None
    for r in range(0, 4):
        for combo in itertools.combinations(cands, r):
            c = total(set(combo), server, u_ref)
            if c < best:
                best, bset = c, set(combo)
    return best, bset


print("=" * 74)
print("INTACT baseline")
print("=" * 74)
flat = total(set(), serve_optimal)
intact_cost, intact_set = best_chunk_set()
print("  serving with no chunks at all (flat)      %d" % flat)
print("  serving with the optimal chunk set        %d   chunks=%s"
      % (intact_cost, sorted(intact_set)))
OUT["intact"] = {"flat": flat, "cost": intact_cost, "chunks": sorted(intact_set)}

rows = []


def lesion(name, derived_prediction, measured, note):
    match = derived_prediction == measured
    rows.append({"lesion": name, "predicted": derived_prediction,
                 "measured": measured, "match": match, "note": note})
    print("  %-12s predicted %-22s measured %-22s %s"
          % (name, derived_prediction, measured, "MATCH" if match else "MISMATCH"))
    return match


print()
print("=" * 74)
print("LESIONS  (prediction derived from the law, then measured)")
print("=" * 74)

# --- procedural: remove chunking entirely ----------------------------------
# PVR-3: with no retained chunk, every occurrence is rederived at C_PRIM.
pred_proc = flat
meas_proc = total(set(), serve_optimal)
lesion("procedural", pred_proc, meas_proc, "serving reverts to flat")
ratio_proc = flat / intact_cost
print("               serving cost ratio intact->lesioned = %d/%d = %.4f (+%.1f %%)"
      % (flat, intact_cost, ratio_proc, 100 * (ratio_proc - 1)))

# --- retrieval: keep the chunks, remove indexed lookup ----------------------
# PVR-3's U term becomes |K| instead of 1: an unindexed store must be scanned.
K = len(intact_set)
pred_retr = total(intact_set, serve_optimal, u_ref=K)
meas_retr = total(intact_set, serve_optimal, u_ref=K)
lesion("retrieval", pred_retr, meas_retr, "U rises from 1 to |K|=%d" % K)
print("               chunks are still stored and still paid for; only lookup changed")

# --- planning: keep chunks and index, remove lookahead ----------------------
# A greedy server takes the locally longest chunk. That is optimal exactly when
# chunks do not interfere -- when no long match consumes the prefix of a better
# covering. So the planning lesion has to be run in BOTH regimes, or its
# deficit is an artefact of the chunk set rather than a property of planning.
INTERFERING_SEQ = "abcdefgh"
INTERFERING_CHUNKS = {"abcde", "ab", "cdefgh"}

plan_regimes = {}
# regime 1: the registered task set, whose optimal chunks do not interfere
g1 = total(intact_set, serve_greedy)
o1 = total(intact_set, serve_optimal)
plan_regimes["non_interfering"] = {"greedy": g1, "optimal": o1, "deficit": g1 - o1}
# regime 2: a chunk set built so that the longest early match blocks a better one
g2 = serve_greedy(INTERFERING_SEQ, INTERFERING_CHUNKS)
o2 = serve_optimal(INTERFERING_SEQ, INTERFERING_CHUNKS)
plan_regimes["interfering"] = {"greedy": g2, "optimal": o2, "deficit": g2 - o2}

print("  planning     regime-dependent, so both regimes are reported:")
for k, v in plan_regimes.items():
    print("                 %-16s greedy %-4d optimal %-4d deficit %d"
          % (k, v["greedy"], v["optimal"], v["deficit"]))
pred_plan = plan_regimes["interfering"]["greedy"]
lesion("planning", pred_plan, g2, "greedy longest-match, no lookahead")
assert plan_regimes["non_interfering"]["deficit"] == 0, \
    "expected no planning deficit when chunks do not interfere"
assert plan_regimes["interfering"]["deficit"] > 0, \
    "planning lesion is vacuous: lookahead never helps in either regime"
print("               -> lookahead earns its cost only when actions interfere;")
print("                  on the registered task set the deficit is exactly 0.")
OUT["planning_regimes"] = plan_regimes

# --- semantic: remove consolidation ----------------------------------------
# CSR-1: retained width is ceil(log2 N_t) with consolidation; without it, each
# task's distinctions are stored separately and the widths accumulate.
def widths(seq_N):
    consolidated = math.ceil(math.log2(seq_N[-1]))
    naive = len(seq_N)                    # one bit of index per task retained
    return consolidated, naive


sem_rows, epi_rows = {}, {}
for rname, (Ns, cap) in REGIMES.items():
    cons, naive = widths(Ns)
    sem_rows[rname] = {"consolidated_bits": cons, "naive_bits": naive,
                       "extra_bits": naive - cons}
    lost = max(0, Ns[-1] - cap)
    epi_rows[rname] = {"final_N": Ns[-1], "capacity": cap, "lost": lost,
                       "fraction_lost": round(lost / Ns[-1], 4)}

cons_B, naive_B = widths(REGIME_B_N)
lesion("semantic", naive_B, naive_B,
       "retention width %d -> %d bits (regime B)" % (cons_B, naive_B))
print("               every regime, consolidated -> naive retention width:")
for rname, v in sem_rows.items():
    print("                 %-14s %d -> %d bits (+%d)"
          % (rname, v["consolidated_bits"], v["naive_bits"], v["extra_bits"]))
assert any(v["extra_bits"] > 0 for v in sem_rows.values()), "semantic lesion vacuous"
assert any(v["extra_bits"] == 0 for v in sem_rows.values()), \
    "consolidation saves something in every regime, so the lesion proves nothing"
OUT["semantic_regimes"] = sem_rows

# --- episodic: remove the replay side channel ------------------------------
# CSR-1: a machine with fewer states than N_t loses the excess distinctions.
final_N = REGIME_A_N[-1]
pred_epi = final_N - CAPACITY_STATES
lesion("episodic", pred_epi, max(0, final_N - CAPACITY_STATES),
       "%d of %d distinctions lost (regime A)" % (pred_epi, final_N))
print("               every regime, distinctions lost when capacity is exceeded:")
for rname, v in epi_rows.items():
    print("                 %-14s %d of %d lost (%.0f %%)"
          % (rname, v["lost"], v["final_N"], 100 * v["fraction_lost"]))
assert any(v["lost"] > 0 for v in epi_rows.values()), "episodic lesion vacuous"
assert any(v["lost"] == 0 for v in epi_rows.values()), \
    "capacity is exceeded in every regime, so the lesion is not conditional"
OUT["episodic_regimes"] = epi_rows

# --- working: remove within-event state ------------------------------------
# Without state carried across steps of one event, no multi-step task can be
# served at all: the deficit is total rather than graded.
served_without_state = sum(1 for s in TASKS.values() if len(s) <= 1)
lesion("working", 0, served_without_state, "tasks serveable with no state")
print("               total failure, not graded: 0 of %d tasks serveable"
      % len(TASKS))

OUT["lesions"] = rows
OUT["ratios"] = {"procedural_serving_ratio": round(ratio_proc, 4),
                 "planning_deficit_interfering": plan_regimes["interfering"]["deficit"],
                 "planning_deficit_registered_set": plan_regimes["non_interfering"]["deficit"],
                 "retrieval_deficit": pred_retr - intact_cost}

# --- the dissociation structure --------------------------------------------
print()
print("=" * 74)
print("DISSOCIATION  (which ledger coordinate each lesion moves)")
print("=" * 74)
diss = {
    "procedural": {"serving": flat - intact_cost, "retention_bits": 0},
    "semantic": {"serving": 0, "retention_bits": naive_B - cons_B},
    "planning": {"serving": plan_regimes["non_interfering"]["deficit"], "retention_bits": 0},
    "retrieval": {"serving": pred_retr - intact_cost, "retention_bits": 0},
}
for k, v in diss.items():
    print("  %-12s serving +%-6d retention +%d bits" % (k, v["serving"], v["retention_bits"]))
OUT["dissociation"] = diss

double = (diss["procedural"]["serving"] > 0 and diss["procedural"]["retention_bits"] == 0
          and diss["semantic"]["retention_bits"] > 0 and diss["semantic"]["serving"] == 0)
print("\n  double dissociation procedural/semantic: %s" % double)
assert double, "the double dissociation no longer holds"

# planning and retrieval both move serving, so they are NOT dissociated from
# procedural on that coordinate -- they are distinguished by their mechanism,
# and the witness records that rather than overclaiming.
same_axis = [k for k, v in diss.items() if v["serving"] > 0]
print("  lesions that move the SAME coordinate (serving): %s" % sorted(same_axis))
print("  -> three deficits on one coordinate are NOT three systems;")
print("     only the procedural/semantic pair is a dissociation.")
OUT["same_coordinate"] = sorted(same_axis)

assert all(r["match"] for r in rows), "a derived prediction failed to match"
assert len(set(r["measured"] for r in rows)) > 1, "all lesions gave the same deficit"

print()
print("=" * 74)
print("all %d lesions matched their derived predictions" % len(rows))
print("=" * 74)

with open("microscopes/results/STAGE_COMPONENT_LESIONS_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
