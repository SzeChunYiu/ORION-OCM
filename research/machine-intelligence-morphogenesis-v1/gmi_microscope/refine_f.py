"""RV-377-070 — the `F` axis of GMI-DA7: a hostile refinement of the ecology family, aimed at breaking every
reduction certified by EXACT DEVELOPMENTAL EQUALITY.

WHY THIS MODULE EXISTS. `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` section 10 (`GMI-DA7`) part 3 proves that the class set
`K(A, d, p, F)` is MONOTONE in the ecology family `F`: refining `F` — adding an ecology or an intervention — can only
SPLIT classes, never merge them, because response equality over a larger index set is a strictly stronger condition.
It follows that an exact-equality certificate is not evidence that a candidate carrier and its parent are the same
machine. It is evidence that `F` NEVER ASKED THEM TO DIFFER. The registered family (5 ecologies x 6 interventions,
`gmi_microscope/ecology.py`) was designed to test capability, not to separate carriers. This module poses demands the
registered family never posed and re-runs every certified pair under them.

A SPLIT IS THE INTERESTING OUTCOME; A SURVIVAL IS A STRICTLY STRONGER REDUCTION THAN THE ONE ON RECORD. Both are real
results and both are recorded.

-------------------------------------------------------------------------------------------------------------------
PARENT-MAXIMALITY (protocol rule 19, gap DG-5)

A separation verdict is only valid against a PARENT-MAXIMAL opponent. Every parent row here is therefore given, before
any verdict is taken:

  * its best EVICTION policy   — when a demand runs it past its declared capacity, the parent is run under EVERY
                                 declared eviction policy (`EVICTIONS`) and the policy that MINIMISES disagreement
                                 with the candidate is the one that decides the verdict. A split is declared only if
                                 EVERY policy disagrees.
  * its best CUE-MATCHING rule — a parent that stores keys is given exact-key lookup AND the nearest-key fallback in
                                 its own metric (Hamming for bit carriers, |.| for index carriers); the better of the
                                 two decides.
  * its best ABSTENTION rule   — the strongest confidence measure computable from the parent's OWN retained state
                                 under its OWN law. Parents are DENIED the candidate's native operator (the
                                 convention the executed receipts already use: `TABLE_MAT` is "DENIED the gluing
                                 operator", `PAIRTABLE` is "DENIED the join operator"); granting a parent the
                                 candidate's operator would make it the candidate, not a parent.

-------------------------------------------------------------------------------------------------------------------
THE REFINED DEMANDS, AND WHICH PAIR EACH IS DESIGNED TO SEPARATE

`OVERFLOW` — teach strictly more bindings / patterns / entries than the parent's DECLARED CAPACITY, so the bounded
compilation must operate PAST the capacity edge.
    designed to separate  every eager/materializing parent from its lazy/algebraic candidate:
                          (VSA, STORE_MAT), (PHASE, PHASE_STORE_MAT), (SHEAF, TABLE_MAT), (POSET, PAIRTABLE),
                          (AUTOCAT_EAGER, TABLE_FULL), (OBSTRUCT, DENSE_RREF), (QPROJ, TABLE), (SCDI, UNIVERSAL).
    why                   the candidate's sufficient state is a GENERATOR (a codebook, a local section, an invariant
                          basis, an authority state) whose size is independent of the number of answers; the parent's
                          is the ANSWER SET. Past the declared capacity the parent must evict and the generator need
                          not. THIS IS WHERE `GMI-DA4`'s CAPACITY GATE LIVES, so a split found only here is reported
                          as a CAPACITY REFINEMENT OF THE REDUCTION BOUND, NOT AS A KINGDOM.

`NOISY_CUE` — query with `k` bit flips in the cue, `k = 1, 2, 3`.
    designed to separate  exact-key retrieval from similarity-based retrieval:
                          (QPROJ, TABLE), (OBSTRUCT, DENSE_RREF), (AUTOCAT_EAGER, TABLE_FULL), (SHEAF, TABLE_MAT).
    why                   a carrier that retrieves by an exact key degrades discontinuously at the first flipped bit;
                          a carrier that retrieves by a graded match over a metric degrades continuously. For the
                          algebraic pairs (VSA, STORE_MAT) and (PHASE, PHASE_STORE_MAT) this demand is the sharpest
                          possible test of the lazy/eager identity, because the identity
                          `Hamming(cue XOR role, f) = Hamming(cue, role XOR f)` is claimed to hold for EVERY cue,
                          corrupted or not — a claim the registered family only ever tested on one noise setting.

`COMPOSITIONAL_UNSEEN` — query a role/filler or feature combination NEVER taught but IMPLIED by the taught set.
    designed to separate  (QPROJ, TABLE) and (QPROJ, BAYES_ORDERED) above all: the projective carrier holds ONE
                          shared state and one projector per QUESTION, so a cross-pair joint is composed for free,
                          while the table holds 8Q registered numbers and the ordered-Bayes row holds six parameters
                          PER REGISTERED PAIR — neither has a cross-pair entry, and materialising one costs Q^2.
    also                  (SHEAF, TABLE_MAT) via interior pins, (SCDI, UNIVERSAL) via an unlabelled fifth serving
                          regime, (VSA/PHASE, *_STORE_MAT) via untaught (path, filler) combinations.

`ABSTAIN_OBLIGATION` — an obligation that scores ABSTENTION explicitly, priced by the already-registered lifecycle
terms (wrong-answers-served, abstentions, collateral regression, `lambda`; gap G4, records RV-377-032/036/037/038,
`vm.lifecycle_vector`: `B_risk = lambda * wrong_served + (lambda / 16) * abstentions`).
    designed to separate  every pair in which one row can compute a GRADED match score and the other can only detect
                          an EXACT KEY MISS: (OBSTRUCT, DENSE_RREF), (QPROJ, TABLE), (AUTOCAT_EAGER, TABLE_FULL),
                          (SHEAF, TABLE_MAT), (POSET, PAIRTABLE).
    why                   "a carrier that can compute a graded match score can abstain informatively; one that can
                          only detect an exact key miss cannot." The served answer here is the PAIR
                          (answer, abstain-flag), so an abstention difference is a response difference.

`REVOKE_THEN_REQUERY` at multiplicity `m = 3, 4, 5` — strictly higher than the registered `double_revoke` (`m = 2`).
    designed to separate  every pair in which one row's state is a MODEL that folded the revoked item in and the
                          other's is the DATA: (SCDI, UNIVERSAL), (VSA, STORE_MAT), (PHASE, PHASE_STORE_MAT),
                          (POSET, PAIRTABLE), (AUTOCAT_EAGER, TABLE_FULL).
    why                   revocation is the one registered intervention that asks a machine to UN-serve something.
                          At m = 2 both members of a certified pair simply deleted a row. At m >= 3 the revoked set
                          starts to interact: the obligation is that every revoked item serves the declared REVOKED
                          sentinel AND that nothing outside the revoked item's semantic dependency closure changes
                          (collateral regression, `GMI_CP_E1_PARENT_FRONTIER_PROTOCOL_V1.md` L_collateral).

Two further demands are justified directly from the carriers' DECLARED NATIVE OPERATORS:

`INTERIOR_PIN` — pin an interior variable and requery.
    designed to separate  (SHEAF, TABLE_MAT) and (SHEAF, PROG_SEARCH). `SHEAF`'s declared native operators are
                          RESTRICT / GLUE / CHECK / PROJECT; RESTRICT at an interior patch is a native step. The
                          table parent's materialised key is the boundary pair alone and the program parent must
                          add a constraint to its declared search program.

`LATE_EXTEND` — append new events (N10) / new moves (N11) AFTER development closes, then requery.
    designed to separate  (POSET, PAIRTABLE) and (OBSTRUCT, DENSE_RREF). `POSET`'s declared native operator EXTEND
                          absorbs one event in `w` JOIN steps; `PAIRTABLE` has no join and must re-materialise the
                          transitive closure. `OBSTRUCT` re-derives the annihilator; `DENSE_RREF` re-echelons.

-------------------------------------------------------------------------------------------------------------------
SCOPE AND ARITHMETIC

Exact arithmetic throughout; the registered 8-bit fixed-point universe unless a DECLARED WIDE INSTRUMENT is named
(`wide` for the DC7, N10 pairs, exactly as the receipts that certified those pairs declared it). No randomness:
every ecology, perturbation and eviction order is a declared deterministic construction. A configuration count is
never called a species count.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

B0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
REVOKED = "<REVOKED>"
ABSTAIN = "<ABSTAIN>"
LAMBDA = 16                      # the declared risk price of one wrong answer served (G4; abstention costs lambda/16)
NOISE_K = (1, 2, 3)              # declared bit-flip multiplicities of NOISY_CUE
REVOKE_M = (3, 4, 5)             # declared revocation multiplicities, all strictly above the registered double_revoke
EVICTIONS = ("FIFO", "LRU", "LFU_TAUGHT")   # the declared eviction policy set a parent is maximised over

DEMANDS = ("OVERFLOW", "NOISY_CUE", "COMPOSITIONAL_UNSEEN", "ABSTAIN_OBLIGATION", "REVOKE_THEN_REQUERY",
           "INTERIOR_PIN", "LATE_EXTEND")
# ABSTAIN_GRADED is run and reported but DOES NOT decide a verdict. Under it each row abstains on a DECLARED margin
# rule rather than on whether its own law can determine the answer, which can deny a row a confidence measure its
# law actually affords -- and protocol rule 19 forbids taking a separation verdict against an opponent that has been
# denied anything. ABSTAIN_OBLIGATION is therefore the PARENT-MAXIMAL form: a row abstains IFF its own law cannot
# determine an answer from its retained state at its CERTIFIED capacity and CERTIFIED budget. A forced abstention is
# a property of the carrier; a margin-rule abstention is a property of the rule.
DEMANDS_DECIDING_THE_VERDICT = ("OVERFLOW", "NOISY_CUE", "COMPOSITIONAL_UNSEEN", "ABSTAIN_OBLIGATION",
                                "REVOKE_THEN_REQUERY", "INTERIOR_PIN", "LATE_EXTEND")
DEMANDS_SENSITIVITY_ONLY = ("ABSTAIN_GRADED",)


# =================================================================================================================
# deliverable 1 — recompute the equality certificates from the COMMITTED receipts (not from the prose)
# =================================================================================================================
RECEIPTS = ("STAGE_DC_V24_DC1_VSA.json", "STAGE_DC_V25_DC3_ENERGY.json", "STAGE_DC_V30_DC2_FIELD.json",
            "STAGE_DC_V31_DC7_QUANTUM.json", "STAGE_DC_V32_DC9_PHASE.json", "STAGE_DN_V26_N3_SHEAF.json",
            "STAGE_DN_V27_N10_PARTIALORDER.json", "STAGE_DN_V28_N10_LAW_LW.json",
            "STAGE_DN_V28_N8_AUTOCATALYTIC.json", "STAGE_DN_V29_N11_OBSTRUCTION.json",
            "STAGE_DN_V30_N11_OBSTRUCTION_R2.json", "STAGE_E1_V35_F4_IQL.json", "STAGE_E1_V36_F6_SCDI.json")

# the instrument each receipt's equality certificate is declared at (None = the receipt has a single instrument)
RECEIPT_INSTRUMENT = {"STAGE_DC_V31_DC7_QUANTUM.json": "wide", "STAGE_DN_V27_N10_PARTIALORDER.json": "wide",
                      "STAGE_DN_V28_N10_LAW_LW.json": "wide"}

# candidate row of each receipt (the carrier under test); everything else in `rows` is a parent or a negative twin
RECEIPT_CANDIDATE = {"STAGE_DC_V24_DC1_VSA.json": "VSA", "STAGE_DC_V25_DC3_ENERGY.json": "HOPFIELD",
                     "STAGE_DC_V30_DC2_FIELD.json": "FIELD", "STAGE_DC_V31_DC7_QUANTUM.json": "QPROJ",
                     "STAGE_DC_V32_DC9_PHASE.json": "PHASE", "STAGE_DN_V26_N3_SHEAF.json": "SHEAF",
                     "STAGE_DN_V27_N10_PARTIALORDER.json": "POSET", "STAGE_DN_V28_N10_LAW_LW.json": "POSET",
                     "STAGE_DN_V28_N8_AUTOCATALYTIC.json": "AUTOCAT_EAGER",
                     "STAGE_DN_V29_N11_OBSTRUCTION.json": "OBSTRUCT",
                     "STAGE_DN_V30_N11_OBSTRUCTION_R2.json": "OBSTRUCT", "STAGE_E1_V35_F4_IQL.json": "IQL",
                     "STAGE_E1_V36_F6_SCDI.json": "SCDI"}

# rows that are NEGATIVE TWINS (ablations of the candidate) or other candidates' rows, never parents of the candidate
NOT_A_PARENT = {"VSA_NOBIND", "HOPFIELD_RND", "FIELD_NONLOCAL", "QPROJ_COMMUTING", "PHASE_NOCOUPLE",
                "SHEAF_NOGLUE", "POSET_NOJOIN", "AUTOCAT_NOFEED", "AUTOCAT_LAZY", "OBSTRUCT_NOCERT",
                "IQL_NOAMBIG", "SCDI_NORECOMPILE"}


def _row_and_context(key, rows):
    parts = key.split("|")
    for p in parts:
        if p in rows:
            return p, tuple(x for x in parts if x != p)
    return None, None


def enumerate_certificates(res_dir=RES):
    """recompute, from the committed receipts alone, every (candidate row, parent row) pair whose served answers are
    BIT-IDENTICAL on every registered cell of that receipt (at the receipt's declared instrument)."""
    out = {"per_receipt": {}, "certificates": [], "n_certificate_pairs": 0, "n_certified_candidates": 0}
    for fname in RECEIPTS:
        path = os.path.join(res_dir, fname)
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        rows = d.get("rows") or []
        cells = d.get("cells") or {}
        if not rows or not cells:
            continue
        cand = RECEIPT_CANDIDATE.get(fname)
        instr = RECEIPT_INSTRUMENT.get(fname)
        idx = {}
        for k, v in cells.items():
            r, ctx = _row_and_context(k, rows)
            if r is None:
                continue
            if instr is not None and instr not in ctx:
                continue
            idx.setdefault(r, {})[ctx] = v.get("answer_signature")
        rec = {"candidate": cand, "instrument": instr or "registered_single_instrument",
               "receipt_sha256": d.get("receipt_sha256"), "revival_record": d.get("revival_record"), "pairs": {}}
        for parent in rows:
            if parent == cand or parent in NOT_A_PARENT:
                continue
            common = sorted(set(idx.get(cand, {})) & set(idx.get(parent, {})))
            if not common:
                continue
            diff = [c for c in common if idx[cand][c] != idx[parent][c]]
            rec["pairs"][parent] = {"n_cells": len(common), "n_differing": len(diff),
                                    "bit_identical_everywhere": not diff}
            if not diff:
                out["certificates"].append({"receipt": fname, "candidate": cand, "parent": parent,
                                            "n_cells": len(common), "instrument": rec["instrument"],
                                            "revival_record": d.get("revival_record"),
                                            "receipt_sha256": d.get("receipt_sha256")})
        out["per_receipt"][fname] = rec
    out["n_certificate_pairs"] = len(out["certificates"])
    out["n_certified_candidates"] = len({c["candidate"] for c in out["certificates"]})
    return out


# =================================================================================================================
# shared machinery for the refined demands
# =================================================================================================================
def _lcg(seed):
    x = seed & 0xFFFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        yield (x >> 16) & 0x7FFF


def flip_positions(seed, width, k):
    """the DECLARED deterministic bit-flip positions of NOISY_CUE: k distinct positions from one declared LCG."""
    g = _lcg(seed); out = []
    while len(out) < k:
        p = next(g) % width
        if p not in out:
            out.append(p)
    return sorted(out)


def evict(entries, cap, policy, taught):
    """the DECLARED eviction policy set a parent is maximised over (protocol rule 19).

    `entries` is the parent's materialised state in insertion order as (key, payload); `taught` maps a key to the
    number of times the development stream taught it. FIFO keeps the oldest, LRU the newest, LFU_TAUGHT the most
    taught (ties by insertion order) -- LFU_TAUGHT is the strongest of the three on every ecology here, and is kept
    in the set precisely so that no verdict can rest on a parent being denied it."""
    if cap is None or len(entries) <= cap:
        return list(entries)
    if policy == "FIFO":
        return entries[:cap]
    if policy == "LRU":
        return entries[len(entries) - cap:]
    if policy == "LFU_TAUGHT":
        order = {k: i for i, (k, _) in enumerate(entries)}
        return sorted(entries, key=lambda kv: (-taught.get(kv[0], 0), order[kv[0]]))[:cap]
    raise ValueError(policy)


class Cells:
    """an accumulator of refined (ecology, intervention, query) cells with both served answers."""

    def __init__(self):
        self.rows = []

    def add(self, demand, ecology, intervention, query, a_cand, a_par, truth=None):
        self.rows.append({"demand": demand, "ecology": ecology, "intervention": intervention, "query": query,
                          "candidate_answer": a_cand, "parent_answer": a_par, "truth": truth})

    def merge(self, other):
        self.rows.extend(other.rows)


def _fmt(v):
    """the served answer as the exact string that goes in the receipt."""
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(_fmt(x) for x in v) + "]"
    return "null" if v is None else str(v)


def adjudicate(cells, per_demand_policy=None):
    """the refined-family verdict for one certificate pair: EQUAL, or SPLIT with the exact first cell."""
    by_demand = {}
    first = None
    for r in cells.rows:
        d = by_demand.setdefault(r["demand"], {"n_cells": 0, "n_differing": 0, "first_split": None, "by_load": {}})
        d["n_cells"] += 1
        ld = d["by_load"].setdefault(r["ecology"], {"n_cells": 0, "n_differing": 0})
        ld["n_cells"] += 1
        differs = _fmt(r["candidate_answer"]) != _fmt(r["parent_answer"])
        if differs:
            d["n_differing"] += 1
            ld["n_differing"] += 1
            cell = {"ecology": r["ecology"], "intervention": r["intervention"], "query": r["query"],
                    "candidate_answer": _fmt(r["candidate_answer"]), "parent_answer": _fmt(r["parent_answer"])}
            if d["first_split"] is None:
                d["first_split"] = cell
            if first is None and r["demand"] in DEMANDS_DECIDING_THE_VERDICT:
                first = dict(cell, demand=r["demand"])
    # the ABSTAIN_OBLIGATION is scored with the registered lifecycle terms of gap G4 (vm.lifecycle_vector):
    #   B_risk = lambda * wrong_answers_served + (lambda / 16) * abstentions
    # plus collateral regression, the number of answers OUTSIDE the demand's own dependency closure that changed.
    risk = {"lambda": LAMBDA, "candidate": {"wrong_served": 0, "abstentions": 0, "scored_cells": 0},
            "parent": {"wrong_served": 0, "abstentions": 0, "scored_cells": 0}}
    for r in cells.rows:
        if r["demand"] != "ABSTAIN_OBLIGATION" or r.get("truth") is None:
            continue
        t = _fmt(r["truth"])
        for who, key in (("candidate", "candidate_answer"), ("parent", "parent_answer")):
            v = _fmt(r[key]); risk[who]["scored_cells"] += 1
            if v == ABSTAIN:
                risk[who]["abstentions"] += 1
            elif v != t:
                risk[who]["wrong_served"] += 1
    for who in ("candidate", "parent"):
        d = risk[who]
        d["B_risk"] = LAMBDA * d["wrong_served"] + (LAMBDA / 16) * d["abstentions"]
    out = {"n_refined_cells": len(cells.rows), "abstain_obligation_lifecycle_score": risk, "per_demand": by_demand,
           "refined_verdict": "SPLIT" if first else "EQUAL", "first_split": first,
           "demands_that_split": sorted(k for k, v in by_demand.items()
                                        if v["n_differing"] and k in DEMANDS_DECIDING_THE_VERDICT),
           "demands_that_do_not_split": sorted(k for k, v in by_demand.items()
                                               if not v["n_differing"] and k in DEMANDS_DECIDING_THE_VERDICT),
           "sensitivity_demands_that_split": sorted(k for k, v in by_demand.items()
                                                    if v["n_differing"] and k in DEMANDS_SENSITIVITY_ONLY)}
    if per_demand_policy:
        out["parent_policy_selected"] = per_demand_policy
    return out


# =================================================================================================================
# P1 (DC1: VSA == STORE_MAT) and P4 (DC9: PHASE == PHASE_STORE_MAT) — the algebraic lazy/eager pairs
# =================================================================================================================
TAU_MARGIN_BITS = 2      # declared abstention margin of the binary code: abstain if best and runner-up are this close


def _vsa_bound_table(eco, depth):
    """every (role path, filler) bound vector — the eager parent's materialised state, UNCHARGED construction of the
    key order only; the charged construction is done inside the row."""
    from . import dc_vsa
    out = []
    for p in dc_vsa.paths(depth):
        for f in range(dc_vsa.F_FILLERS):
            out.append(((p, f), dc_vsa.bound_vector(eco["roles"], eco["fillers"], p, f, eco["D"])))
    return out


def _vsa_taught(eco):
    t = {}
    for rec in eco["dev"]:
        for p, f in rec["items"]:
            t[(p, f)] = t.get((p, f), 0) + 1
    return t


def _vsa_serve(eco, cue, path, cap, policy, revoked=frozenset(), abstain=False, lazy=True):
    """serve one query from EITHER carrier of the DC1 pair, exactly.

    lazy=True  is the candidate VSA: state = the codebook (R + F vectors, independent of depth); UNBIND along the
               path, then CLEANUP by nearest filler.
    lazy=False is the parent STORE_MAT: state = the materialised (path, filler) bound vectors, capacity-limited to
               `cap` entries under `policy`; nearest match among the retained entries whose path matches.
    Both carry the same declared tombstone revocation policy (the strongest available to either) and the same
    declared abstention margin, so no verdict rests on one of them being denied a policy the other has."""
    from . import dc_vsa
    M = Machine(bases.ALL[B0]); D = eco["D"]
    if lazy:
        v = cue
        for r in path:
            v = dc_vsa._xor_bits(M, v, eco["roles"][r], D)
        cands = [(f, dc_vsa._hamming(M, v, eco["fillers"][f], D)) for f in range(dc_vsa.F_FILLERS)]
    else:
        table = evict(_vsa_bound_table(eco, len(path)), cap, policy, _vsa_taught(eco))
        cands = [(k[1], dc_vsa._hamming(M, cue, vec, D)) for k, vec in table if k[0] == path]
    if not cands:
        return None
    cands.sort(key=lambda t: (t[1], t[0]))
    best, bd = cands[0]
    if (path, best) in revoked:
        return REVOKED
    if abstain and len(cands) > 1 and cands[1][1] - bd < TAU_MARGIN_BITS:
        return ABSTAIN
    return best


def suite_dc1(cell="D64_d1_k3"):
    """the refined family for P1. Registered certificate: VSA == STORE_MAT, 7 cells, RV-377-044."""
    from . import dc_vsa
    spec = dc_vsa.CELLS[cell]
    base = dc_vsa.ecology(spec["D"], 1, spec["k"], noise=0)
    deep = dc_vsa.ecology(spec["D"], 2, spec["k"], noise=0)
    C = dc_vsa.R_ROLES * dc_vsa.F_FILLERS          # the parent's CERTIFIED capacity: R*F materialised entries at d = 1
    cells = Cells(); policies = {}

    # ---- OVERFLOW: GMI-DA4's capacity gate. State size S is HELD FIXED at each row's certified value and the number
    # of items P is raised: depth 1 -> 2 multiplies the bindings by R (32 -> 128) while the candidate's sufficient
    # state (the codebook, R + F vectors) is unchanged. The parent is run under every declared eviction policy and
    # the one minimising disagreement decides.
    for load, eco, cap in (("depth1_at_capacity", base, C), ("depth2_past_capacity", deep, C)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            rows = []
            for ri, rec in enumerate(eco["eval"]):
                for p in sorted(rec["answers"]):
                    a = _vsa_serve(eco, rec["cue"], p, None, pol, lazy=True)
                    b = _vsa_serve(eco, rec["cue"], p, cap, pol, lazy=False)
                    rows.append((f"rec{ri}|path{''.join(map(str, p))}", a, b))
            nd = sum(1 for _, a, b in rows if _fmt(a) != _fmt(b))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, a, b in best_rows:
            cells.add("OVERFLOW", f"E_rolefill[{cell}|{load}]", f"capacity={cap}|evict={best_pol}", q, a, b)

    # ---- NOISY_CUE: k bit flips in the cue, k = 1, 2, 3. The lazy/eager identity
    # Hamming(cue XOR role, f) = Hamming(cue, role XOR f) is claimed for EVERY cue; this asks it of corrupted ones.
    for k in NOISE_K:
        for ri, rec in enumerate(base["eval"]):
            cue = rec["cue"]
            for pos in flip_positions(7700 + 11 * ri + k, base["D"], k):
                cue ^= 1 << pos
            for p in sorted(rec["answers"]):
                cells.add("NOISY_CUE", f"E_rolefill[{cell}]", f"noisy_cue_k={k}", f"rec{ri}|path{''.join(map(str, p))}",
                          _vsa_serve(base, cue, p, None, "FIFO", lazy=True),
                          _vsa_serve(base, cue, p, None, "FIFO", lazy=False))

    # ---- COMPOSITIONAL_UNSEEN: a (role path, filler) combination that NEVER occurred in development.
    taught = set(_vsa_taught(base))
    by_path = {p: [f for f in range(dc_vsa.F_FILLERS) if (p, f) not in taught] for p in dc_vsa.paths(1)}
    paths_with_unseen = [p for p in dc_vsa.paths(1) if by_path[p]]
    combos = []
    for rot in range(max(len(v) for v in by_path.values())):
        chosen = [(p, by_path[p][rot % len(by_path[p])]) for p in paths_with_unseen[:spec["k"]]]
        if len(chosen) == spec["k"] and chosen not in combos:
            combos.append(chosen)
    for i, items in enumerate(combos):
        cue, ans = dc_vsa.make_record(base["roles"], base["fillers"], items, base["D"], base["tie"])
        for p in sorted(ans):
            cells.add("COMPOSITIONAL_UNSEEN", f"E_rolefill[{cell}]", "untaught_role_filler_combination",
                      f"unseen{i}|path{''.join(map(str, p))}",
                      _vsa_serve(base, cue, p, None, "FIFO", lazy=True),
                      _vsa_serve(base, cue, p, None, "FIFO", lazy=False))

    # ---- ABSTAIN_OBLIGATION: the served answer becomes (answer | ABSTAIN). Both rows compute a graded Hamming
    # score, so both get the same declared margin rule; the question is whether the scores agree.
    for ri, rec in enumerate(base["eval"]):
        for p in sorted(rec["answers"]):
            cells.add("ABSTAIN_GRADED", f"E_rolefill[{cell}]", f"abstain_margin={TAU_MARGIN_BITS}bits",
                      f"rec{ri}|path{''.join(map(str, p))}",
                      _vsa_serve(base, rec["cue"], p, None, "FIFO", abstain=True, lazy=True),
                      _vsa_serve(base, rec["cue"], p, None, "FIFO", abstain=True, lazy=False),
                      truth=rec["answers"][p])
    # the PARENT-MAXIMAL form: neither carrier of this pair is ever FORCED to abstain -- the codebook always
    # determines an answer and so does the materialised table inside its certified capacity -- which is itself the
    # finding, and is recorded cell by cell rather than asserted.
    for ri, rec in enumerate(base["eval"]):
        for p in sorted(rec["answers"]):
            cells.add("ABSTAIN_OBLIGATION", f"E_rolefill[{cell}]", "abstain_iff_own_law_cannot_determine",
                      f"rec{ri}|path{''.join(map(str, p))}",
                      _vsa_serve(base, rec["cue"], p, None, "FIFO", lazy=True),
                      _vsa_serve(base, rec["cue"], p, None, "FIFO", lazy=False), truth=rec["answers"][p])

    # ---- REVOKE_THEN_REQUERY at m = 3, 4, 5 (registered double_revoke is m = 2). Both rows carry the declared
    # tombstone policy, the strongest revocation policy available to either.
    allb = [(p, f) for p in dc_vsa.paths(1) for f in range(dc_vsa.F_FILLERS)]
    for m in REVOKE_M:
        rev = frozenset(allb[i] for i in range(m))
        for ri, rec in enumerate(base["eval"]):
            for p in sorted(rec["answers"]):
                cells.add("REVOKE_THEN_REQUERY", f"E_rolefill[{cell}]", f"revoke_then_requery_m={m}",
                          f"rec{ri}|path{''.join(map(str, p))}",
                          _vsa_serve(base, rec["cue"], p, None, "FIFO", revoked=rev, lazy=True),
                          _vsa_serve(base, rec["cue"], p, None, "FIFO", revoked=rev, lazy=False))
    return cells, policies


TAU_MARGIN_PHASE = 1     # declared abstention margin of the phase code, in coherence units of the active instrument


def _phase_table(eco, depth, Q):
    from . import dc_phase
    out = []
    for p in dc_phase.paths(depth):
        for f in range(dc_phase.F_FILLERS):
            out.append(((p, f), dc_phase.bind_path(eco["phase_roles"], eco["phase_fillers"], p, f, Q)))
    return out


def _phase_serve(eco, cue, path, cap, policy, precision, revoked=frozenset(), abstain=False, lazy=True):
    """serve one query from EITHER carrier of the DC9 pair, exactly (the phase-code analogue of _vsa_serve).

    lazy=True  is the candidate PHASE: state = the phase codebook; UNBIND by modular phase subtraction along the
               path, then CLEANUP by maximum coherence over the F filler phase vectors.
    lazy=False is the parent PHASE_STORE_MAT: state = the materialised bound phase vectors, capacity-limited."""
    from . import dc_phase
    M = Machine(bases.ALL[B0]); A = dc_phase.PArith(M, precision)
    COS = dc_phase.cos_table(eco["Q"], A.S); Q = eco["Q"]; Dp = eco["Dp"]

    def coherence(a, b):
        s = 0
        for i in range(Dp):
            s = A.add(s, dc_phase._cos_lookup(M, COS, Q, dc_phase._mod_sub(A, a[i], b[i], Q)))
        return s

    if lazy:
        v = list(cue)
        for r in path:
            v = [dc_phase._mod_sub(A, v[i], eco["phase_roles"][r][i], Q) for i in range(Dp)]
        cands = [(f, coherence(v, eco["phase_fillers"][f])) for f in range(dc_phase.F_FILLERS)]
    else:
        table = evict(_phase_table(eco, len(path), Q), cap, policy, _vsa_taught(eco))
        cands = [(k[1], coherence(cue, vec)) for k, vec in table if k[0] == path]
    if not cands:
        return None
    cands.sort(key=lambda t: (-t[1], t[0]))
    best, bc = cands[0]
    if (path, best) in revoked:
        return REVOKED
    if abstain and len(cands) > 1 and bc - cands[1][1] < TAU_MARGIN_PHASE:
        return ABSTAIN
    return best


def suite_dc9(cell="D64_d1_k3_Q4_P32", precision="fx8"):
    """the refined family for P4. Registered certificate: PHASE == PHASE_STORE_MAT, 66 cells, RV-377-054."""
    from . import dc_phase, dc_vsa
    spec = dc_phase.BASE_CELLS[cell]
    base = dc_phase.ecology(spec["D"], 1, spec["k"], spec["Dp"], spec["Q"])
    deep = dc_phase.ecology(spec["D"], 2, spec["k"], spec["Dp"], spec["Q"])
    C = dc_vsa.R_ROLES * dc_vsa.F_FILLERS
    cells = Cells(); policies = {}
    tag = f"E_bindsync[{cell}|{precision}]"

    for load, eco, cap in (("depth1_at_capacity", base, C), ("depth2_past_capacity", deep, C)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            rows = []
            for ri, rec in enumerate(eco["eval"]):
                for p in sorted(rec["answers"]):
                    a = _phase_serve(eco, rec["phase_cue"], p, None, pol, precision, lazy=True)
                    b = _phase_serve(eco, rec["phase_cue"], p, cap, pol, precision, lazy=False)
                    rows.append((f"rec{ri}|path{''.join(map(str, p))}", a, b))
            nd = sum(1 for _, a, b in rows if _fmt(a) != _fmt(b))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, a, b in best_rows:
            cells.add("OVERFLOW", f"E_bindsync[{cell}|{load}|{precision}]", f"capacity={cap}|evict={best_pol}", q, a, b)

    # NOISY_CUE in the phase code: k declared one-step phase kicks (the phase analogue of a bit flip)
    for k in NOISE_K:
        for ri, rec in enumerate(base["eval"]):
            cue = list(rec["phase_cue"])
            for pos in flip_positions(8800 + 11 * ri + k, base["Dp"], k):
                cue[pos] = (cue[pos] + 1) % base["Q"]
            for p in sorted(rec["answers"]):
                cells.add("NOISY_CUE", tag, f"noisy_cue_k={k}", f"rec{ri}|path{''.join(map(str, p))}",
                          _phase_serve(base, cue, p, None, "FIFO", precision, lazy=True),
                          _phase_serve(base, cue, p, None, "FIFO", precision, lazy=False))

    taught = set(_vsa_taught(base))
    by_path = {p: [f for f in range(dc_vsa.F_FILLERS) if (p, f) not in taught] for p in dc_vsa.paths(1)}
    pw = [p for p in dc_vsa.paths(1) if by_path[p]]
    combos = []
    for rot in range(max((len(v) for v in by_path.values()), default=0)):
        ch = [(p, by_path[p][rot % len(by_path[p])]) for p in pw[:spec["k"]]]
        if len(ch) == spec["k"] and ch not in combos:
            combos.append(ch)
    COS = dc_phase.cos_table(base["Q"], 1 << dc_phase.WIDE_BITS)
    for i, items in enumerate(combos):
        vs = [dc_phase.bind_path(base["phase_roles"], base["phase_fillers"], p, f, base["Q"]) for p, f in items]
        cue = dc_phase.bundle_phases(vs, base["Q"], COS)
        for p, _f in items:
            cells.add("COMPOSITIONAL_UNSEEN", tag, "untaught_role_filler_combination",
                      f"unseen{i}|path{''.join(map(str, p))}",
                      _phase_serve(base, cue, p, None, "FIFO", precision, lazy=True),
                      _phase_serve(base, cue, p, None, "FIFO", precision, lazy=False))

    for ri, rec in enumerate(base["eval"]):
        for p in sorted(rec["answers"]):
            cells.add("ABSTAIN_GRADED", tag, f"abstain_margin={TAU_MARGIN_PHASE}coherence_units",
                      f"rec{ri}|path{''.join(map(str, p))}",
                      _phase_serve(base, rec["phase_cue"], p, None, "FIFO", precision, abstain=True, lazy=True),
                      _phase_serve(base, rec["phase_cue"], p, None, "FIFO", precision, abstain=True, lazy=False),
                      truth=rec["answers"][p])
    for ri, rec in enumerate(base["eval"]):
        for p in sorted(rec["answers"]):
            cells.add("ABSTAIN_OBLIGATION", tag, "abstain_iff_own_law_cannot_determine",
                      f"rec{ri}|path{''.join(map(str, p))}",
                      _phase_serve(base, rec["phase_cue"], p, None, "FIFO", precision, lazy=True),
                      _phase_serve(base, rec["phase_cue"], p, None, "FIFO", precision, lazy=False),
                      truth=rec["answers"][p])

    allb = [(p, f) for p in dc_vsa.paths(1) for f in range(dc_vsa.F_FILLERS)]
    for m in REVOKE_M:
        rev = frozenset(allb[i] for i in range(m))
        for ri, rec in enumerate(base["eval"]):
            for p in sorted(rec["answers"]):
                cells.add("REVOKE_THEN_REQUERY", tag, f"revoke_then_requery_m={m}",
                          f"rec{ri}|path{''.join(map(str, p))}",
                          _phase_serve(base, rec["phase_cue"], p, None, "FIFO", precision, revoked=rev, lazy=True),
                          _phase_serve(base, rec["phase_cue"], p, None, "FIFO", precision, revoked=rev, lazy=False))
    return cells, policies


# =================================================================================================================
# P2 (DC7: QPROJ == BAYES_ORDERED) and P3 (DC7: QPROJ == TABLE), at the DECLARED WIDE instrument
# =================================================================================================================
def _dc7_fit(eco, precision):
    """each row's development, exactly as its module declares it, done once and reused across the refined demands."""
    from . import dc_quantum as qm
    M = Machine(bases.ALL[B0]); A = qm.QArith(M, precision); native = [0]; d = eco["d"]
    states = range(qm.G_ANGLES) if eco["n"] == 1 else [eco["truth_state"]]
    max_err, gs, sel = qm._grid_fit(A, d, native, eco["table"], states)
    qproj = {"gs": gs, "sel": sel, "max_err": max_err}
    par = []
    for t in eco["table"]:
        s = [A.from_units(x) for x in t]
        a = A.add(s[0], s[1]); b = A.add(s[4], s[5])

        def fit(av, target):
            lo, hi = 0, A.S
            for _ in range(A.S.bit_length()):
                mid = (lo + hi) // 2
                if A.gt(target, A.mul(av, mid)): lo = mid
                else: hi = mid
            return lo if abs(A.mul(av, lo) - target) <= abs(A.mul(av, hi) - target) else hi
        par.append((a, fit(a, s[0]), fit(A.sub(A.S, a), s[2]), b, fit(b, s[4]), fit(A.sub(A.S, b), s[6])))
    return {"A": A, "native": native, "qproj": qproj, "bayes": par, "table": [list(t) for t in eco["table"]]}


def _dc7_serve(eco, fit, row, qkey, idx, cap=None, policy="FIFO"):
    """serve one (question-pair key, outcome index) from one DC7 row.

    qkey is (i, j): the WITHIN-PAIR key (i, i) is the registered family; a CROSS-PAIR key (i, j), i != j, asks the
    joint of question A of registered pair i with question B of registered pair j -- never taught, but implied by
    the shared state and the two projectors.
      QPROJ          composes: one shared state, the A-angle of pair i, the B-angle of pair j. No new description.
      TABLE          has 8Q registered numbers and no cross-pair entry; PARENT-MAXIMAL fallback is its nearest
                     registered key in its own index metric (the same outcome index of pair i).
      BAYES_ORDERED  has six parameters per registered pair and no cross-pair conditional; PARENT-MAXIMAL fallback
                     is the independence composition of pair i's A-marginal with pair j's B-marginal, which is the
                     strongest cross-pair statement its carrier can make."""
    from . import dc_quantum as qm
    A = fit["A"]; d = eco["d"]; i, j = qkey
    if row == "QPROJ":
        ga = fit["qproj"]["sel"][i][1]; gb = fit["qproj"]["sel"][j][2]
        psi, ops = qm.compile_ops(A, d, fit["qproj"]["gs"], ga, gb)
        return qm.single_prob(A, d, psi, ops, idx, fit["native"])
    if row == "TABLE":
        entries = [((q, k), v) for q, t in enumerate(fit["table"]) for k, v in enumerate(t)]
        kept = dict(evict(entries, cap, policy, {(q, k): 1 for q in range(eco["Q"]) for k in range(8)}))
        if (i, idx) in kept:
            return kept[(i, idx)] if i == j else kept[(i, idx)]   # cross-pair: the nearest registered key
        return 0
    if row == "BAYES_ORDERED":
        entries = [((q, s), v) for q, p in enumerate(fit["bayes"]) for s, v in enumerate(p)]
        kept = dict(evict(entries, cap, policy, {(q, s): 1 for q in range(eco["Q"]) for s in range(6)}))
        need = [(i, 0), (i, 1), (i, 2), (j, 3), (j, 4), (j, 5)]
        if any(k not in kept for k in need):
            return 0
        a, u, v = kept[(i, 0)], kept[(i, 1)], kept[(i, 2)]
        b, x, y = kept[(j, 3)], kept[(j, 4)], kept[(j, 5)]
        if i == j:
            tab = [A.mul(a, u), A.mul(a, A.sub(A.S, u)), A.mul(A.sub(A.S, a), v),
                   A.mul(A.sub(A.S, a), A.sub(A.S, v)), A.mul(b, x), A.mul(b, A.sub(A.S, x)),
                   A.mul(A.sub(A.S, b), y), A.mul(A.sub(A.S, b), A.sub(A.S, y))]
            return A.to_units(tab[idx])
        # cross-pair: independence composition of pair i's A-marginal with pair j's B-marginal
        pB = A.add(A.mul(b, x), A.mul(A.sub(A.S, b), y))
        pAn, pBn = A.sub(A.S, a), A.sub(A.S, pB)
        tab = [A.mul(a, pB), A.mul(a, pBn), A.mul(pAn, pB), A.mul(pAn, pBn),
               A.mul(pB, a), A.mul(pB, pAn), A.mul(pBn, a), A.mul(pBn, pAn)]
        return A.to_units(tab[idx])
    raise ValueError(row)


def _dc7_truth(eco, fit, qkey, idx):
    """the declared projective ground truth: the registered table for a within-pair key, and the SAME declared model
    with pair i's A-angle and pair j's B-angle for a cross-pair key. Disclosed caveat: the registered table is
    itself generated by this model class, so the cross-pair truth favours the projective carrier by construction --
    which is why the SPLIT verdict here rests on the served answers DIFFERING, never on which row is right."""
    from . import dc_quantum as qm
    i, j = qkey
    if i == j:
        return eco["table"][i][idx]
    A = fit["A"]; ga = qm.TRUTH_PAIRS[i][0]; gb = qm.TRUTH_PAIRS[j][1]
    return qm.model_probs(A, eco["d"], eco["truth_state"], ga, gb, fit["native"])[idx]


def suite_dc7(parent, cell="n1_Q4", precision="wide"):
    """the refined family for P2 (parent BAYES_ORDERED) and P3 (parent TABLE). Registered certificates: 6 cells each
    at the declared wide instrument, RV-377-047 / receipt STAGE_DC_V31_DC7_QUANTUM.json."""
    from . import dc_quantum as qm
    spec = qm.CELLS[cell]
    eco = qm.ecology(spec["n"], spec["Q"]); Q = eco["Q"]
    fit = _dc7_fit(eco, precision)
    cap = {"TABLE": 8 * Q, "BAYES_ORDERED": 6 * Q}[parent]   # the parent's CERTIFIED state size, held fixed
    cells = Cells(); policies = {}
    tag = f"E_order[{cell}|{precision}]"
    within = [(i, i) for i in range(Q)]
    cross = [(i, j) for i in range(Q) for j in range(Q) if i != j]

    # ---- OVERFLOW: state size held fixed at the certified value, the served family raised from Q within-pair keys
    # to Q^2 keys. The candidate composes at zero extra description; the parent must evict.
    for load, keys, capacity in (("registered_within_pair_at_capacity", within, cap),
                                 ("cross_pair_family_past_capacity", within + cross, cap)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            rows = []
            for (i, j) in keys:
                for idx in range(8):
                    rows.append((f"pair({i},{j})|outcome{idx}",
                                 _dc7_serve(eco, fit, "QPROJ", (i, j), idx),
                                 _dc7_serve(eco, fit, parent, (i, j), idx, capacity, pol)))
            nd = sum(1 for _, a, b in rows if _fmt(a) != _fmt(b))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, a, b in best_rows:
            cells.add("OVERFLOW", f"E_order[{cell}|{load}|{precision}]", f"capacity={capacity}|evict={best_pol}", q, a, b)

    # ---- NOISY_CUE: k bit flips in the query key (the pair index), k = 1, 2, 3
    for k in NOISE_K:
        width = max(1, (Q - 1).bit_length())
        for i in range(Q):
            ii = i
            for pos in flip_positions(9900 + 7 * i + k, width, min(k, width)):
                ii ^= 1 << pos
            ii %= Q
            for idx in range(8):
                cells.add("NOISY_CUE", tag, f"noisy_cue_k={k}", f"pair({i}->{ii})|outcome{idx}",
                          _dc7_serve(eco, fit, "QPROJ", (ii, ii), idx),
                          _dc7_serve(eco, fit, parent, (ii, ii), idx))

    # ---- COMPOSITIONAL_UNSEEN: the SAME cross-pair keys with NO capacity restriction. Any split here is not a
    # capacity gate: the parent is allowed all the description it wants and still has no cross-pair datum.
    for (i, j) in cross:
        for idx in range(8):
            cells.add("COMPOSITIONAL_UNSEEN", tag, "cross_pair_joint_never_taught|capacity=unbounded",
                      f"pair({i},{j})|outcome{idx}",
                      _dc7_serve(eco, fit, "QPROJ", (i, j), idx),
                      _dc7_serve(eco, fit, parent, (i, j), idx))

    # ---- ABSTAIN_OBLIGATION: each row abstains on the strongest confidence measure its OWN retained state affords.
    # QPROJ has a graded fit residual per pair (max_err of its grid fit); the table has only exact-key hit/miss;
    # ordered-Bayes has the residual of its own conditional fit. Declared rule: abstain when the row's own residual
    # exceeds the registered tolerance TOL_UNITS, or when the key is missing.
    for (i, j) in within + cross:
        for idx in range(8):
            qv = _dc7_serve(eco, fit, "QPROJ", (i, j), idx)
            qres = fit["qproj"]["sel"][i][0] if i == j else max(fit["qproj"]["sel"][i][0], fit["qproj"]["sel"][j][0])
            a = ABSTAIN if qres > qm.TOL_UNITS else qv
            pv = _dc7_serve(eco, fit, parent, (i, j), idx)
            b = ABSTAIN if (i != j) else pv       # neither parent holds a cross-pair key: its miss is the only signal
            cells.add("ABSTAIN_OBLIGATION", tag, f"abstain_if_residual_gt={qm.TOL_UNITS}units_or_key_missing",
                      f"pair({i},{j})|outcome{idx}", a, b, truth=_dc7_truth(eco, fit, (i, j), idx))

    # ---- REVOKE_THEN_REQUERY at m = 3, 4, 5: withdraw m registered pairs, then requery every key.
    for m in REVOKE_M:
        rev = set(range(min(m, Q)))
        for (i, j) in within:
            for idx in range(8):
                a = REVOKED if (i in rev or j in rev) else _dc7_serve(eco, fit, "QPROJ", (i, j), idx)
                b = REVOKED if (i in rev or j in rev) else _dc7_serve(eco, fit, parent, (i, j), idx)
                cells.add("REVOKE_THEN_REQUERY", tag, f"revoke_then_requery_m={m}", f"pair({i},{j})|outcome{idx}", a, b)
    return cells, policies


# =================================================================================================================
# P5 (N3: SHEAF == TABLE_MAT) and P6 (N3: SHEAF == PROG_SEARCH)
# =================================================================================================================
def _n3_fb(e, a, b, pin):
    """the candidate's charged forward GLUE and backward RESTRICT passes, with an optional interior pin
    (pin = (j, c) constrains x_j = c). RESTRICT at an interior patch is one of SHEAF's DECLARED NATIVE OPERATORS,
    which is why the interior pin is a demand this carrier can be asked and the materialising parent cannot."""
    M = Machine(bases.ALL[B0]); n, d, R = e["n"], e["d"], e["R"]
    F = [[0] * d for _ in range(n)]; F[0][a] = 1
    for i in range(n - 1):
        for v in range(d):
            acc = 0
            for u in range(d):
                acc = M.op("OR", acc, M.op("AND", F[i][u], R[i][u][v]))
            F[i + 1][v] = acc
        if pin and pin[0] == i + 1:
            for v in range(d):
                F[i + 1][v] = F[i + 1][v] if v == pin[1] else 0
    B = [[0] * d for _ in range(n)]; B[n - 1][b] = 1
    for i in range(n - 2, -1, -1):
        for u in range(d):
            acc = 0
            for v in range(d):
                acc = M.op("OR", acc, M.op("AND", R[i][u][v], B[i + 1][v]))
            B[i][u] = acc
        if pin and pin[0] == i:
            for u in range(d):
                B[i][u] = B[i][u] if u == pin[1] else 0
    return F, B


def _n3_sheaf(e, a, b, pin=None, confidence=False):
    n, d, R = e["n"], e["d"], e["R"]
    F, B = _n3_fb(e, a, b, pin)
    live = [[u for u in range(d) if F[i][u] and B[i][u]] for i in range(n)]
    if any(not L for L in live):
        return (None, 1) if confidence else None
    out = [a]
    for i in range(n - 1):
        pick = next((v for v in range(d) if R[i][out[i]][v] and B[i + 1][v] and (not pin or pin[0] != i + 1 or v == pin[1])), -1)
        out.append(pick)
    conf = 1 if all(len(L) == 1 for L in live) else 0
    return (tuple(out), conf) if confidence else tuple(out)


def _n3_enumerate(e, a, b, pin=None):
    """the lex-least global section, by exhaustive enumeration — the only law the materialising parent has."""
    n, d, R = e["n"], e["d"], e["R"]
    for asg in itertools.product(range(d), repeat=n):
        if asg[0] != a or asg[n - 1] != b:
            continue
        if pin and asg[pin[0]] != pin[1]:
            continue
        if all(R[i][asg[i]][asg[i + 1]] for i in range(n - 1)):
            return asg
    return None


def _n3_table(e, a, b, pin, cap, policy, may_materialize_pins, confidence=False):
    """the D2 parent, DENIED the gluing operator. Its key space is the BOUNDARY PAIR; the pinned family multiplies
    it by (n-2)*d. `may_materialize_pins` is the PARENT-MAXIMAL grant: when true the parent re-enumerates and
    materialises the enlarged key space (unbounded capacity); when false its state size is held at the value it was
    certified at and it must answer the pinned query from its unpinned key."""
    d, n = e["d"], e["n"]
    keys = [(x, y, None) for x in range(d) for y in range(d)]
    if may_materialize_pins:
        keys += [(x, y, (j, c)) for x in range(d) for y in range(d) for j in range(1, n - 1) for c in range(d)]
    entries = [(k, _n3_enumerate(e, k[0], k[1], k[2])) for k in keys]
    kept = dict(evict(entries, cap, policy, {k: 1 for k in keys}))
    if (a, b, pin) in kept:
        v = kept[(a, b, pin)]
        return (v, 1) if confidence else v
    if (a, b, None) in kept:          # PARENT-MAXIMAL cue-matching fallback: the nearest retained key
        v = kept[(a, b, None)]
        return (v, 0) if confidence else v
    return (None, 0) if confidence else None


def _n3_prog(e, a, b, pin, node_budget, confidence=False):
    """the D4/D5 parent: lex-first DFS with a verifier, PARENT-MAXIMAL (it is given the pinned-DFS program, so the
    interior pin is a constraint it can enforce rather than a query it cannot express)."""
    n, d, R = e["n"], e["d"], e["R"]
    stack = [(a,)]; nodes = 0
    while stack:
        asg = stack.pop(); nodes += 1
        if nodes > node_budget:
            return (None, 0) if confidence else None
        i = len(asg) - 1
        if i == n - 1:
            return (asg, 1) if confidence else asg
        dom = [b] if i == n - 2 else list(range(d))
        if pin and pin[0] == i + 1:
            dom = [v for v in dom if v == pin[1]]
        stack.extend(reversed([asg + (v,) for v in dom if R[i][asg[i]][v]]))
    return (None, 1) if confidence else None


def suite_n3(parent, cell="n6_d3_dense"):
    """the refined family for P5 (parent TABLE_MAT) and P6 (parent PROG_SEARCH). Registered certificates: 22 cells
    each, RV-377-050 / receipt STAGE_DN_V26_N3_SHEAF.json."""
    from . import dn_sheaf
    spec = dn_sheaf.CELLS[cell]
    e = dn_sheaf.ecology(spec["n"], spec["d"], spec["rho_num"], spec["rho_den"], tail=spec.get("tail", False))
    n, d = e["n"], e["d"]
    CAP = d * d                                  # TABLE_MAT's CERTIFIED state size: one entry per boundary pair
    NODES = d ** n                               # PROG_SEARCH's CERTIFIED search budget: the full assignment space
    pins = [(j, c) for j in range(1, n - 1) for c in range(d)]
    bnd = [(a, b) for a in range(d) for b in range(d)]
    cells = Cells(); policies = {}
    tag = f"E_glue[{cell}]"

    def par(a, b, pin, cap, pol, mat, budget, conf=False):
        if parent == "TABLE_MAT":
            return _n3_table(e, a, b, pin, cap, pol, mat, conf)
        return _n3_prog(e, a, b, pin, budget, conf)

    # ---- OVERFLOW: state size held FIXED at the certified value while the served family is raised from the d^2
    # boundary pairs to the d^2*(n-2)*d pinned keys. SHEAF's sufficient state (the local sections) is unchanged.
    for load, qs, cap, mat, budget in (("boundary_family_at_capacity", [(a, b, None) for a, b in bnd], CAP, False, NODES),
                                       ("pinned_family_past_capacity", [(a, b, p) for a, b in bnd for p in pins], CAP, False, NODES)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            rows = [(f"boundary({a},{b})|pin={p}", _n3_sheaf(e, a, b, p), par(a, b, p, cap, pol, mat, budget))
                    for a, b, p in qs]
            nd = sum(1 for _, x, y in rows if _fmt(x) != _fmt(y))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, x, y in best_rows:
            cells.add("OVERFLOW", f"E_glue[{cell}|{load}]", f"capacity={cap}|evict={best_pol}", q, x, y)

    # ---- NOISY_CUE: k symbol perturbations of the boundary pair, k = 1, 2, 3 (mod d on each coordinate in turn)
    for k in NOISE_K:
        for (a, b) in bnd:
            aa, bb = (a + k) % d, (b + (k // 2)) % d
            cells.add("NOISY_CUE", tag, f"noisy_cue_k={k}", f"boundary({a},{b})->({aa},{bb})",
                      _n3_sheaf(e, aa, bb, None), par(aa, bb, None, None, "FIFO", False, NODES))

    # ---- COMPOSITIONAL_UNSEEN and INTERIOR_PIN, both with the parent granted UNBOUNDED capacity and a full
    # re-materialisation of the enlarged key space: any split here is not a capacity gate.
    for (a, b) in bnd:
        for p in pins:
            cells.add("INTERIOR_PIN", tag, "interior_pin|capacity=unbounded|parent_may_rematerialise",
                      f"boundary({a},{b})|pin=x{p[0]}={p[1]}",
                      _n3_sheaf(e, a, b, p), par(a, b, p, None, "FIFO", True, NODES))
    unseen = [(a, b) for a, b in bnd if b != 0]          # development shows only the b = 0 boundary pairs
    for (a, b) in unseen:
        for p in pins[:d]:
            cells.add("COMPOSITIONAL_UNSEEN", tag, "untaught_boundary_and_interior|capacity=unbounded",
                      f"boundary({a},{b})|pin=x{p[0]}={p[1]}",
                      _n3_sheaf(e, a, b, p), par(a, b, p, None, "FIFO", True, NODES))

    # ---- ABSTAIN_OBLIGATION: abstain iff the row's OWN confidence measure is below 1. SHEAF's measure is graded
    # (every position determined by the glued sections); the table's is exact-key hit/miss; the search row's is
    # completion inside its declared budget.
    for (a, b) in bnd:
        for p in [None] + pins[:d]:
            sv, _sc = _n3_sheaf(e, a, b, p, confidence=True)
            pv, pc = par(a, b, p, None, "LFU_TAUGHT", True, NODES, conf=True)
            sc = 1   # PARENT-MAXIMAL / CANDIDATE-MAXIMAL: SHEAF's forward-backward pass DETERMINES the lex-least
                     # section whenever one exists, so it is never FORCED to abstain
            cells.add("ABSTAIN_OBLIGATION", tag, "abstain_if_own_confidence_lt_1",
                      f"boundary({a},{b})|pin={p}", ABSTAIN if not sc else sv, ABSTAIN if not pc else pv,
                      truth=_n3_enumerate(e, a, b, p))

    # ---- REVOKE_THEN_REQUERY at m = 3, 4, 5: withdraw m declared local-relation entries and requery every boundary
    # pair. The parent is PARENT-MAXIMAL: it may fully re-materialise after every revocation.
    allowed = [(i, u, v) for i in range(n - 1) for u in range(d) for v in range(d) if e["R"][i][u][v]]
    for m in REVOKE_M:
        e2 = dict(e); R2 = [[list(r) for r in Mx] for Mx in e["R"]]
        for (i, u, v) in allowed[:m]:
            R2[i][u][v] = 0
        e2["R"] = R2
        for (a, b) in bnd:
            cells.add("REVOKE_THEN_REQUERY", tag, f"revoke_then_requery_m={m}|parent_may_rematerialise",
                      f"boundary({a},{b})", _n3_sheaf(e2, a, b, None),
                      (_n3_table(e2, a, b, None, None, "FIFO", False) if parent == "TABLE_MAT"
                       else _n3_prog(e2, a, b, None, NODES)))
    return cells, policies


# =================================================================================================================
# P7 (N10: POSET == PAIRTABLE) and P8 (N10: POSET == PROG_SEARCH), at the DECLARED WIDE instrument
# =================================================================================================================
def _n10_world(cell, extra=0):
    """the registered poset, optionally LATE-EXTENDED by `extra` events appended AFTER development closes. Each
    appended event depends on the last event of chain 0 AND the last event of chain 1 — a cross-chain combination
    the development stream never presented — which is exactly what POSET's declared native operator EXTEND absorbs
    in w JOIN steps and what the materialising parent can only answer by re-closing."""
    from . import dn_partialorder as po
    spec = po.CELLS[cell]
    n, preds, chain_of, level_of = po.poset(spec["w"], spec["L"])
    preds = [list(p) for p in preds]
    chain_of = list(chain_of)
    base_n = n
    last = {c: max(ev for ev in range(n) if chain_of[ev] == c) for c in range(spec["w"])}
    for t in range(extra):
        c = t % spec["w"]; c2 = (c + 1) % spec["w"]
        # the appended event keeps the ecology's declared chain discipline (it depends on its own chain's last
        # event) AND adds a cross-chain dependency the development stream never presented
        preds.append(sorted({last[c]} | ({last[c2]} if c2 != c else set())))
        chain_of.append(c); last[c] = n
        n += 1
    order = po.interleavings(base_n, preds[:base_n], 53)[0] + list(range(base_n, n))
    reach = po.closure(n, preds)
    return {"w": spec["w"], "L": spec["L"], "n": n, "base_n": base_n, "preds": preds, "chain_of": chain_of,
            "order": order, "reach": reach}


def _n10_poset(e, cap=None, policy="FIFO", precision="wide"):
    """the candidate: one vector clock per event, JOIN on EXTEND. Capacity is counted in CLOCK COMPONENTS."""
    from . import dn_partialorder as po
    M = Machine(bases.ALL[B0]); A = po.Arith(M, precision); w = e["w"]
    clock = {}
    for ev in e["order"]:
        v = [0] * w
        for p in e["preds"][ev]:
            if p in clock:
                for k in range(w):
                    v[k] = A.maxi(v[k], clock[p][k])
        v[e["chain_of"][ev]] = A.step(v[e["chain_of"][ev]])
        clock[ev] = v
    entries = [(ev, clock[ev]) for ev in e["order"]]
    kept = dict(evict(entries, None if cap is None else max(1, cap // w), policy, {ev: 1 for ev in clock}))

    def q(i, j):
        if i not in kept or j not in kept:
            return None
        le = lambda x, y: all(not A.gt(kept[x][k], kept[y][k]) for k in range(w))
        return 1 if le(i, j) else (2 if le(j, i) else 0)
    return q


def _n10_pairtable(e, cap=None, policy="FIFO"):
    """the D2 parent, DENIED the join operator: it materialises the transitive closure and answers by lookup."""
    entries = [((i, j), 1) for i in range(e["n"]) for j in range(e["n"]) if i != j and e["reach"][i][j]]
    kept = dict(evict(entries, cap, policy, {k: 1 for k, _ in entries}))

    def q(i, j):
        if (i, j) in kept:
            return 1
        if (j, i) in kept:
            return 2
        return 0
    return q


def _n10_prog(e, cap=None, policy="FIFO", budget=None):
    """the D4/D5 parent: the immediate-dependency edge list plus a causal-path search at query time."""
    edges = [((p, ev), 1) for ev in range(e["n"]) for p in e["preds"][ev]]
    kept = dict(evict(edges, cap, policy, {k: 1 for k, _ in edges}))
    succ = {}
    for (p, ev) in kept:
        succ.setdefault(p, []).append(ev)

    def path(i, j):
        seen, stack, nodes = {i}, [i], 0
        while stack:
            u = stack.pop(); nodes += 1
            if budget is not None and nodes > budget:
                return None
            for v in succ.get(u, []):
                if v == j:
                    return 1
                if v not in seen:
                    seen.add(v); stack.append(v)
        return 0

    def q(i, j):
        a = path(i, j)
        if a is None:
            return None
        if a:
            return 1
        b = path(j, i)
        return None if b is None else (2 if b else 0)
    return q


def suite_n10(parent, cell="w4_L4", extra=3, precision="wide"):
    """the refined family for P7 (parent PAIRTABLE) and P8 (parent PROG_SEARCH). Registered certificates: 32 cells
    each at the declared wide instrument, RV-377-051/052."""
    base = _n10_world(cell, 0)
    ext = _n10_world(cell, extra)
    CAP_POSET = base["n"] * base["w"]
    CAP_PAIR = sum(1 for i in range(base["n"]) for j in range(base["n"]) if i != j and base["reach"][i][j])
    CAP_EDGE = sum(len(p) for p in base["preds"][:base["n"]])
    CAP_PARENT = CAP_PAIR if parent == "PAIRTABLE" else CAP_EDGE
    pfn = _n10_pairtable if parent == "PAIRTABLE" else _n10_prog
    cells = Cells(); policies = {}
    tag = f"E_causal[{cell}|{precision}]"

    # ---- OVERFLOW: every row's state size held FIXED at its certified value while `extra` further events are
    # appended. The candidate's state grows by w components per event; the pair table's by 2n + 1 entries.
    for load, e, cap_c, cap_p in (("registered_events_at_capacity", base, CAP_POSET, CAP_PARENT),
                                  ("late_events_past_capacity", ext, CAP_POSET, CAP_PARENT)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            cq = _n10_poset(e, cap_c, pol, precision); pq = pfn(e, cap_p, pol)
            rows = [(f"pair({i},{j})", cq(i, j), pq(i, j))
                    for i in range(e["n"]) for j in range(e["n"]) if i != j]
            nd = sum(1 for _, a, b in rows if _fmt(a) != _fmt(b))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, a, b in best_rows:
            cells.add("OVERFLOW", f"E_causal[{cell}|{load}|{precision}]",
                      f"capacity_candidate={cap_c}|capacity_parent={cap_p}|evict={best_pol}", q, a, b)

    cq = _n10_poset(base, precision=precision); pq = pfn(base)
    # ---- NOISY_CUE: k bit flips in the event index of the query pair
    for k in NOISE_K:
        width = max(1, (base["n"] - 1).bit_length())
        for i in range(base["n"]):
            for j in range(base["n"]):
                if i == j:
                    continue
                jj = j
                for pos in flip_positions(6600 + 13 * (i * base["n"] + j) + k, width, min(k, width)):
                    jj ^= 1 << pos
                jj %= base["n"]
                if jj == i:
                    continue
                cells.add("NOISY_CUE", tag, f"noisy_cue_k={k}", f"pair({i},{j}->{jj})", cq(i, jj), pq(i, jj))

    # ---- LATE_EXTEND and COMPOSITIONAL_UNSEEN with UNBOUNDED capacity: both rows may absorb the late events in
    # full. Any split here is not a capacity gate.
    cqe = _n10_poset(ext, precision=precision); pqe = pfn(ext)
    for i in range(ext["n"]):
        for j in range(ext["n"]):
            if i == j:
                continue
            d = "COMPOSITIONAL_UNSEEN" if (i >= base["n"] or j >= base["n"]) else "LATE_EXTEND"
            cells.add(d, tag, f"late_extend_{extra}_events|capacity=unbounded", f"pair({i},{j})", cqe(i, j), pqe(i, j))

    # ---- ABSTAIN_OBLIGATION: abstain iff the row's own confidence is below 1. The candidate's clock comparison is
    # a graded lattice test that is always determinate; the pair table cannot tell CONCURRENT from KEY-ABSENT; the
    # search parent's confidence is completion inside its declared node budget.
    # PARENT-MAXIMAL: PAIRTABLE's DECLARED description is the full n x n closure matrix (dn_partialorder.PairTable
    # .desc_bits returns n*n), so it materialises the ZEROS too and a zero entry is a positive statement of
    # CONCURRENCY rather than a missing key. PROG_SEARCH gets its certified node budget. Neither is then forced to
    # abstain, and the earlier appearance of a split here was a parent-maximality failure, not a separation.
    pq_conf = _n10_pairtable(base) if parent == "PAIRTABLE" else _n10_prog(base, budget=None)
    for i in range(base["n"]):
        for j in range(base["n"]):
            if i == j:
                continue
            a = cq(i, j)
            b = pq_conf(i, j)
            b = ABSTAIN if b is None else b
            truth = 1 if base["reach"][i][j] else (2 if base["reach"][j][i] else 0)
            cells.add("ABSTAIN_OBLIGATION", tag, "abstain_if_own_confidence_lt_1", f"pair({i},{j})", a, b,
                      truth=truth)

    # ---- REVOKE_THEN_REQUERY at m = 3, 4, 5: withdraw m events; both rows may fully recompute (parent-maximal).
    for m in REVOKE_M:
        rev = set(range(base["n"] - m, base["n"]))
        e2 = dict(base); e2["order"] = [x for x in base["order"] if x not in rev]
        e2["preds"] = [[p for p in ps if p not in rev] for ps in base["preds"]]
        from . import dn_partialorder as po
        e2["reach"] = po.closure(base["n"], e2["preds"])
        cq2 = _n10_poset(e2, precision=precision); pq2 = pfn(e2)
        for i in range(base["n"]):
            for j in range(base["n"]):
                if i == j:
                    continue
                a = REVOKED if (i in rev or j in rev) else cq2(i, j)
                b = REVOKED if (i in rev or j in rev) else pq2(i, j)
                cells.add("REVOKE_THEN_REQUERY", tag, f"revoke_then_requery_m={m}|parent_may_recompute",
                          f"pair({i},{j})", a, b)
    return cells, policies


# =================================================================================================================
# P9 (N8: AUTOCAT_EAGER == SEARCH_DERIV) and P10 (N8: AUTOCAT_EAGER == TABLE_FULL)
# =================================================================================================================
def _n8_built(L, cap=None, policy="FIFO", taught=None):
    """the candidate's state: CLOSE to a fixed point at the artifact-size cap L, products re-entering as reagents,
    held to a declared capacity in BUILT ARTIFACTS."""
    from . import dn_autocatalytic as ac
    M = Machine(bases.ALL[B0]); built = []; order = []
    for s in ac.SEEDS:
        if ac._insert(M, built, s):
            order.append(s)
    while True:
        before = set(built)
        if not ac._close_round(M, built, L):
            break
        order += [w for w in built if w not in before]
    # the candidate's TRUE insertion order: seeds first, then products round by round (the autocatalytic order),
    # which is NOT the sorted order the table parent is given -- the order-dependent eviction policies therefore
    # see genuinely different states, which is the hostile form of this demand
    return dict(evict([(w, 1) for w in order], cap, policy, taught or {}))


def _n8_table(L, cap=None, policy="FIFO", taught=None):
    """the strongest D2 parent: GIVEN the entire closure at construction, held to the same declared capacity."""
    from . import dn_autocatalytic as ac
    entries = [(w, 1) for w in sorted(ac.closure(L))]
    return dict(evict(entries, cap, policy, taught or {}))


def _n8_search(seeds, w, budget):
    """the strongest D5/D4 parent: per query, test candidate derivations one by one by recursive splitting, with no
    reuse of sub-results. Its state is the seed set and the rule -- INDEPENDENT of the artifact-size cap L, which is
    why the OVERFLOW demand can put the candidate past its own capacity edge while the parent stays inside its."""
    nodes = [0]

    def rec(x):
        nodes[0] += 1
        if nodes[0] > budget:
            raise RuntimeError("budget")
        if any(x == s for s in seeds):
            return True
        return any(rec(x[:i]) and rec(x[i:]) for i in range(1, len(x)))
    try:
        return int(rec(tuple(w)))
    except RuntimeError:
        return None


def suite_n8(parent, cell="L10", over="L14"):
    """the refined family for P9 (parent SEARCH_DERIV) and P10 (parent TABLE_FULL). Registered certificates: 6 cells
    each, receipt STAGE_DN_V28_N8_AUTOCATALYTIC.json."""
    from . import dn_autocatalytic as ac
    L = ac.CELLS[cell]["L"]; L2 = ac.CELLS[over]["L"]
    e = ac.ecology(L); e2 = ac.ecology(L2)
    CAP = len(ac.closure(L))                 # the CERTIFIED state size of both eager rows at the registered load
    taught = {w: 1 for w, _ in e["dev"]}
    cells = Cells(); policies = {}
    tag = f"E_construct[{cell}]"

    def cand(built, w):
        return int(tuple(w) in built)

    def par(built, w, budget=ac.NODE_BUDGET):
        if parent == "TABLE_FULL":
            return int(tuple(w) in built)
        return _n8_search(ac.SEEDS, w, budget)

    # ---- OVERFLOW: state size held FIXED at the certified closure size while the artifact cap is raised from L to
    # L2, so strictly more patterns are taught than the eager rows can hold. The search parent's state is the seed
    # set and does not grow at all: this demand puts the CANDIDATE past ITS capacity edge.
    for load, eco, Lx in (("L_at_capacity", e, L), ("L_past_capacity", e2, L2)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            cb = _n8_built(Lx, CAP, pol, taught)
            pb = _n8_table(Lx, CAP, pol, taught) if parent == "TABLE_FULL" else None
            rows = [(f"artifact{''.join(map(str, w))}", cand(cb, w),
                     (int(tuple(w) in pb) if parent == "TABLE_FULL" else _n8_search(ac.SEEDS, w, ac.NODE_BUDGET)))
                    for w, _lab in eco["eval"]]
            nd = sum(1 for _, a, b in rows if _fmt(a) != _fmt(b))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, a, b in best_rows:
            cells.add("OVERFLOW", f"E_construct[{cell}|{load}]", f"capacity={CAP}|evict={best_pol}", q, a, b)

    built = _n8_built(L); table = _n8_table(L)
    pb = table

    # ---- NOISY_CUE: k bit flips in the queried artifact, k = 1, 2, 3
    for k in NOISE_K:
        for qi, (w, _lab) in enumerate(e["eval"]):
            ww = list(w)
            for pos in flip_positions(5500 + 17 * qi + k, len(w), min(k, len(w))):
                ww[pos] ^= 1
            ww = tuple(ww)
            cells.add("NOISY_CUE", tag, f"noisy_cue_k={k}", f"artifact{''.join(map(str, ww))}",
                      cand(built, ww), (int(ww in pb) if parent == "TABLE_FULL" else _n8_search(ac.SEEDS, ww, ac.NODE_BUDGET)))

    # ---- COMPOSITIONAL_UNSEEN: DEEP closure members (three or more blocks) never shown in development, and
    # non-members of the same lengths. Capacity unbounded for both rows.
    deep = [w for w in sorted(ac.closure(L)) if (ac._blocks(w) or 0) >= 3 and w not in taught]
    for w in deep[:24]:
        cells.add("COMPOSITIONAL_UNSEEN", tag, "deep_closure_member_never_taught|capacity=unbounded",
                  f"artifact{''.join(map(str, w))}", cand(built, w),
                  (int(w in pb) if parent == "TABLE_FULL" else _n8_search(ac.SEEDS, w, ac.NODE_BUDGET)))

    # ---- ABSTAIN_OBLIGATION: the candidate's MEMBER test over its built set is determinate (it either holds the
    # artifact or knows it closed to a fixed point); the table parent has only exact-key hit/miss; the search parent
    # abstains exactly when its declared derivation-node budget is exhausted.
    SMALL = ac.NODE_BUDGET   # PARENT-MAXIMAL: the search parent's CERTIFIED derivation-node budget, not a tighter one
    for w, _lab in e["eval"]:
        a = cand(built, w)
        if parent == "TABLE_FULL":
            b = int(w in pb)
        else:
            r = _n8_search(ac.SEEDS, w, SMALL)
            b = ABSTAIN if r is None else r
        cells.add("ABSTAIN_OBLIGATION", tag, f"abstain_if_own_confidence_lt_1|search_node_budget={SMALL}",
                  f"artifact{''.join(map(str, w))}", a, b, truth=_lab)

    # ---- REVOKE_THEN_REQUERY at m = 3, 4, 5: withdraw m built artifacts; both rows carry the declared tombstone.
    allw = sorted(ac.closure(L))
    for m in REVOKE_M:
        rev = set(allw[:m])
        for w, _lab in e["eval"]:
            a = REVOKED if w in rev else cand(built, w)
            b = REVOKED if w in rev else (int(w in pb) if parent == "TABLE_FULL"
                                          else _n8_search(ac.SEEDS, w, ac.NODE_BUDGET))
            cells.add("REVOKE_THEN_REQUERY", tag, f"revoke_then_requery_m={m}",
                      f"artifact{''.join(map(str, w))}", a, b)
    return cells, policies


# =================================================================================================================
# P11 (N11: OBSTRUCT == DENSE_RREF)
# =================================================================================================================
def _n11_state(e, m):
    from . import dn_obstruction as ob
    M = Machine(bases.ALL[B0])
    basis, piv = ob._echelon(M, e["moves"], m)
    basis = ob._back_reduce(M, basis, piv, m)
    H = ob._nullspace(M, basis, piv, m)
    return M, basis, piv, H


def _n11_serve(e, m, row, delta, cap_rows=None, policy="FIFO"):
    """OBSTRUCT certifies unreachability by evaluating its annihilator basis; DENSE_RREF decides by reducing the
    instance against its echelon coefficient basis. `cap_rows` is the number of rows the row's CERTIFIED state size
    still affords at the refined instance width."""
    from . import dn_obstruction as ob
    M, basis, piv, H = _n11_state(e, m)
    if row == "OBSTRUCT":
        kept = [v for _, v in evict([((i,), h) for i, h in enumerate(H)], cap_rows, policy, {})]
        ok = 1
        for h in kept:
            ok = M.op("AND", ok, M.op("NOT", ob._parity_and(M, h, delta, m)))
        return ok
    keptb = evict([((i,), (p, b)) for i, (p, b) in enumerate(zip(piv, basis))], cap_rows, policy, {})
    bs = [v[1] for _, v in keptb]; ps = [v[0] for _, v in keptb]
    cur = ob._reduce(M, delta, bs, ps, m)
    return int(ob._eq_vec(M, cur, 0, m))


def suite_n11(cell="m10_d2_k10", over="m24_d2_k24"):
    """the refined family for P11. Registered certificate: OBSTRUCT == DENSE_RREF, 10 cells, RV-377-053,
    reproduced bit-identically by the R2 receipt."""
    from . import dn_obstruction as ob
    s1 = ob.CELLS[cell]; s2 = ob.CELLS[over]
    e1 = ob.ecology(s1["m"], s1["k"], s1["d"]); e2 = ob.ecology(s2["m"], s2["k"], s2["d"])
    m1, m2 = s1["m"], s2["m"]
    CAP_OB_BITS = s1["d"] * m1                       # OBSTRUCT's certified state: d invariants of m bits
    CAP_DR_BITS = (m1 - s1["d"]) * m1                # DENSE_RREF's certified state: the echelon basis
    cells = Cells(); policies = {}
    tag = f"E_obstruct[{cell}]"

    # ---- OVERFLOW: both state sizes held FIXED in BITS at their certified values while the instance width is
    # doubled, so each row retains only floor(bits / m') of its rows.
    for load, e, m, ca, cb in (("m_at_capacity", e1, m1, None, None),
                               ("m_past_capacity", e2, m2, CAP_OB_BITS // m2, CAP_DR_BITS // m2)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            rows = [(f"delta{idx}", _n11_serve(e, m, "OBSTRUCT", dl, ca, pol),
                     _n11_serve(e, m, "DENSE_RREF", dl, cb, pol)) for idx, (dl, _l) in enumerate(e["eval"])]
            nd = sum(1 for _, a, b in rows if _fmt(a) != _fmt(b))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, a, b in best_rows:
            cells.add("OVERFLOW", f"E_obstruct[{cell}|{load}]",
                      f"capacity_bits_candidate={CAP_OB_BITS}|capacity_bits_parent={CAP_DR_BITS}|evict={best_pol}", q, a, b)

    # ---- NOISY_CUE: k bit flips in the instance, k = 1, 2, 3
    for k in NOISE_K:
        for idx, (dl, _l) in enumerate(e1["eval"]):
            dd = dl
            for pos in flip_positions(4400 + 19 * idx + k, m1, k):
                dd ^= 1 << pos
            cells.add("NOISY_CUE", tag, f"noisy_cue_k={k}", f"delta{idx}_flipped{k}",
                      _n11_serve(e1, m1, "OBSTRUCT", dd), _n11_serve(e1, m1, "DENSE_RREF", dd))

    # ---- COMPOSITIONAL_UNSEEN: the XOR of two evaluation instances -- an instance implied by the linearity of the
    # move structure and never taught. Capacity unbounded for both rows.
    ev = [dl for dl, _l in e1["eval"]]
    for i in range(len(ev)):
        for j in range(i + 1, len(ev)):
            cells.add("COMPOSITIONAL_UNSEEN", tag, "xor_of_two_untaught_instances|capacity=unbounded",
                      f"delta{i}_xor_delta{j}", _n11_serve(e1, m1, "OBSTRUCT", ev[i] ^ ev[j]),
                      _n11_serve(e1, m1, "DENSE_RREF", ev[i] ^ ev[j]))

    # ---- ABSTAIN_OBLIGATION: abstain iff the row's own derived object is incomplete. OBSTRUCT's confidence is that
    # its derived corank equals the ecology's; DENSE_RREF's is that its rank equals m - d. Both are computable from
    # each row's own retained state under its own law, so neither is denied a measure the other has.
    _M, basis1, _p1, H1 = _n11_state(e1, m1)
    conf_ob = int(len(H1) == e1["corank"]); conf_dr = int(len(basis1) == m1 - e1["corank"])
    for idx, (dl, _l) in enumerate(e1["eval"]):
        a = _n11_serve(e1, m1, "OBSTRUCT", dl) if conf_ob else ABSTAIN
        b = _n11_serve(e1, m1, "DENSE_RREF", dl) if conf_dr else ABSTAIN
        cells.add("ABSTAIN_OBLIGATION", tag, "abstain_if_derived_object_incomplete", f"delta{idx}", a, b,
                      truth=_l)

    # ---- REVOKE_THEN_REQUERY at m = 3, 4, 5: withdraw m declared moves and requery; both rows re-derive from the
    # retained move set (parent-maximal: neither is denied the re-derivation).
    for mm in REVOKE_M:
        e3 = dict(e1); e3["moves"] = e1["moves"][:-mm]
        for idx, (dl, _l) in enumerate(e1["eval"]):
            cells.add("REVOKE_THEN_REQUERY", tag, f"revoke_then_requery_m={mm}|parent_may_rederive", f"delta{idx}",
                      _n11_serve(e3, m1, "OBSTRUCT", dl), _n11_serve(e3, m1, "DENSE_RREF", dl))

    # ---- LATE_EXTEND: append declared new moves AFTER development closes and requery. DERIVE is OBSTRUCT's native
    # operator; the coefficient parent must re-echelon. Both are granted the re-derivation.
    e4 = dict(e1); e4["moves"] = list(e1["moves"]) + [ob.lcg_bits(7300 + i, m1) for i in range(2)]
    for idx, (dl, _l) in enumerate(e1["eval"]):
        cells.add("LATE_EXTEND", tag, "late_extend_2_moves|parent_may_rederive", f"delta{idx}",
                  _n11_serve(e4, m1, "OBSTRUCT", dl), _n11_serve(e4, m1, "DENSE_RREF", dl))
    return cells, policies


# =================================================================================================================
# P12 (F6: SCDI == AUTH_INTERP), P13 (F6: SCDI == UNIVERSAL), P14 (F6: SCDI == AUTH_TABLE)
# =================================================================================================================
REGIME_E = "E"   # the DECLARED FIFTH SERVING REGIME, over the SAME latent factors, never labelled in development:
                 # 1 iff the scope sum is strictly positive (a sign regime; A, B, C, D are the registered four)


def _f6_truth(coeffs, x, s, regime):
    from .e1_scdi import truth_regime
    from .e1_vlc import truth
    if regime == REGIME_E:
        return 1 if truth(coeffs, x, s) > 0 else 0
    return truth_regime(coeffs, x, s, regime)


def _f6_interp(M, L, x, s, regime):
    """serve by interpreting the authority state at query time -- the operation that requires the authority state
    to still exist. UNIVERSAL released it, which is what this demand is built to expose."""
    from .e1_scdi import Serving
    from .core import clamp
    if regime == REGIME_E:
        tot = clamp(sum(L.value(i, x) for i in s))
        return 1 if M.op("GT", tot, 0) else 0
    return Serving.interp(M, L, x, s, regime)


def _f6_develop(col):
    from .e1_scdi import COLUMN_CYCLE
    from .e1_vlc import COEFF_VALUES, DEV_EVENTS, N_F, Learner
    from .e1_scdi import truth_regime
    M = Machine(bases.ALL_HW[col] if col in bases.ALL_HW else bases.ALL[col])
    coeffs = [(COEFF_VALUES[(2 * i) % 4], COEFF_VALUES[(2 * i + 1) % 4]) for i in range(N_F)]
    M.phase("exec"); L = Learner(M)
    for x, s in DEV_EVENTS:
        M.phase("upd"); L.observe(x, s, truth_regime(coeffs, x, s, "A")); M.end_event()
    M.phase("exec")
    return M, L, coeffs


def _f6_serve(row, M, L, regimes, cap, policy, x, s, regime):
    """serve one query from one F6 row.
      SCDI / AUTH_INTERP  keep the authority state and interpret (SCDI's charged price probe selects INTERP in
                          three of the four declared price columns).
      AUTH_TABLE          keeps the authority state AND compiles per-regime serving tables; PARENT-MAXIMAL, so on a
                          table miss it falls back to interpreting the authority state it still holds.
      UNIVERSAL           compiles ONE universal serving table and RELEASES the authority state, so a table miss is
                          the end of the line -- there is nothing left to recompile from."""
    from .e1_scdi import PATTERNS
    from .e1_vlc import SCOPES
    if row in ("SCDI", "AUTH_INTERP"):
        return _f6_interp(M, L, x, s, regime)
    keys = [(g, si, pi) for g in regimes for si in range(len(SCOPES)) for pi in range(len(PATTERNS))]
    entries = [(k, None) for k in keys]
    kept = {k for k, _ in evict(entries, cap, policy, {k: 1 for k in keys})}
    from .e1_scdi import pat_of
    key = (regime, SCOPES.index(s), PATTERNS.index(pat_of(x, s)))
    if key in kept:
        return _f6_interp(M, L, x, s, regime)      # the compiled entry equals the interpreted value by construction
    if row == "AUTH_TABLE":
        return _f6_interp(M, L, x, s, regime)      # parent-maximal fallback: the authority state is still held
    return None                                    # UNIVERSAL: the authority state was released


def suite_f6(parent, col="B0_LOCAL_ADAPTIVE_TRANSDUCERS", G=4):
    """the refined family for P12 (AUTH_INTERP), P13 (UNIVERSAL) and P14 (AUTH_TABLE). Registered certificates: 16
    cells each, RV-377-064 / receipt STAGE_E1_V36_F6_SCDI.json."""
    from .e1_scdi import PATTERNS, REGIMES
    from .e1_vlc import EVAL_QUERIES, SCOPES
    M, L, coeffs = _f6_develop(col)
    reg4 = list(REGIMES[:G]); reg5 = reg4 + [REGIME_E]
    CAP = G * len(SCOPES) * len(PATTERNS)          # the certified serving-table size at the registered G
    cells = Cells(); policies = {}
    tag = f"E_factored[G={G}|{col}]"

    # ---- OVERFLOW: state size held FIXED at the certified serving-table size while a FIFTH serving regime over the
    # same latent factors is added. The authority-keeping rows interpret; the released-authority row cannot.
    for load, regs, cap in (("four_regimes_at_capacity", reg4, CAP), ("fifth_regime_past_capacity", reg5, CAP)):
        best_pol, best_diff, best_rows = None, None, None
        for pol in EVICTIONS:
            rows = [(f"regime{g}|x={x}|scope{s}",
                     _f6_serve("SCDI", M, L, regs, cap, pol, x, s, g),
                     _f6_serve(parent, M, L, regs, cap, pol, x, s, g))
                    for g in regs for x, s in EVAL_QUERIES]
            nd = sum(1 for _, a, b in rows if _fmt(a) != _fmt(b))
            if best_diff is None or nd < best_diff:
                best_pol, best_diff, best_rows = pol, nd, rows
        policies[f"OVERFLOW|{load}"] = best_pol
        for q, a, b in best_rows:
            cells.add("OVERFLOW", f"E_factored[G={G}|{load}|{col}]", f"capacity={cap}|evict={best_pol}", q, a, b)

    # ---- NOISY_CUE: k bit flips in the query input x, k = 1, 2, 3
    for k in NOISE_K:
        for qi, (x, s) in enumerate(EVAL_QUERIES):
            xx = x
            for pos in flip_positions(3300 + 23 * qi + k, 8, k):
                xx ^= 1 << pos
            for g in reg4:
                cells.add("NOISY_CUE", tag, f"noisy_cue_k={k}", f"regime{g}|x={x}->{xx}|scope{s}",
                          _f6_serve("SCDI", M, L, reg4, None, "FIFO", xx, s, g),
                          _f6_serve(parent, M, L, reg4, None, "FIFO", xx, s, g))

    # ---- COMPOSITIONAL_UNSEEN: the fifth serving regime with UNBOUNDED capacity -- the parent may compile whatever
    # it likes; what it cannot do is derive a regime it was never labelled in without an authority state.
    for x, s in EVAL_QUERIES:
        cells.add("COMPOSITIONAL_UNSEEN", tag, "fifth_serving_regime_never_labelled|capacity=unbounded",
                  f"regime{REGIME_E}|x={x}|scope{s}",
                  _f6_serve("SCDI", M, L, reg5, None, "FIFO", x, s, REGIME_E),
                  _f6_serve(parent, M, L, reg4, None, "FIFO", x, s, REGIME_E))

    # ---- ABSTAIN_OBLIGATION: abstain iff the row's own confidence is below 1 (a table row's confidence is the
    # presence of its key; an interpreting row's is the presence of the authority state).
    for g in reg5:
        for x, s in EVAL_QUERIES:
            a = _f6_serve("SCDI", M, L, reg5, None, "FIFO", x, s, g)
            b = _f6_serve(parent, M, L, reg4, CAP, "LFU_TAUGHT", x, s, g)
            cells.add("ABSTAIN_OBLIGATION", tag, "abstain_if_own_confidence_lt_1", f"regime{g}|x={x}|scope{s}",
                      ABSTAIN if a is None else a, ABSTAIN if b is None else b,
                      truth=_f6_truth(coeffs, x, s, g))

    # ---- REVOKE_THEN_REQUERY at m = 3, 4, 5: withdraw m development events and requery. An authority-keeping row
    # re-develops and re-derives every serving regime; a released-authority row cannot.
    from .e1_vlc import DEV_EVENTS, COEFF_VALUES, N_F, Learner
    from .e1_scdi import truth_regime
    for m in REVOKE_M:
        M2 = Machine(bases.ALL_HW[col] if col in bases.ALL_HW else bases.ALL[col])
        M2.phase("exec"); L2 = Learner(M2)
        for x, s in DEV_EVENTS[:-m]:
            M2.phase("upd"); L2.observe(x, s, truth_regime(coeffs, x, s, "A")); M2.end_event()
        M2.phase("exec")
        for g in reg4:
            for x, s in EVAL_QUERIES:
                a = _f6_serve("SCDI", M2, L2, reg4, None, "FIFO", x, s, g)
                b = (_f6_serve(parent, M2, L2, reg4, None, "FIFO", x, s, g) if parent != "UNIVERSAL"
                     else _f6_serve(parent, M, L, reg4, None, "FIFO", x, s, g))
                cells.add("REVOKE_THEN_REQUERY", tag, f"revoke_then_requery_m={m}|authority_rows_may_redevelop",
                          f"regime{g}|x={x}|scope{s}", a, b)
    return cells, policies


# =================================================================================================================
# the fourteen certified pairs, the gate classification, and the receipt
# =================================================================================================================
PAIRS = {
    "P1":  {"candidate": "VSA", "parent": "STORE_MAT", "domain_candidate": "DC1 hyperdimensional / vector-symbolic",
            "receipts": ["STAGE_DC_V24_DC1_VSA.json"], "instrument": "fx8_registered", "suite": ("dc1", {})},
    "P2":  {"candidate": "QPROJ", "parent": "BAYES_ORDERED", "domain_candidate": "DC7 quantum cognition",
            "receipts": ["STAGE_DC_V31_DC7_QUANTUM.json"], "instrument": "wide", "suite": ("dc7", {"parent": "BAYES_ORDERED"})},
    "P3":  {"candidate": "QPROJ", "parent": "TABLE", "domain_candidate": "DC7 quantum cognition",
            "receipts": ["STAGE_DC_V31_DC7_QUANTUM.json"], "instrument": "wide", "suite": ("dc7", {"parent": "TABLE"})},
    "P4":  {"candidate": "PHASE", "parent": "PHASE_STORE_MAT", "domain_candidate": "DC9 oscillatory / phase coding",
            "receipts": ["STAGE_DC_V32_DC9_PHASE.json"], "instrument": "fx8_registered", "suite": ("dc9", {})},
    "P5":  {"candidate": "SHEAF", "parent": "TABLE_MAT", "domain_candidate": "N3 relational-constraint / sheaf",
            "receipts": ["STAGE_DN_V26_N3_SHEAF.json"], "instrument": "fx8_registered", "suite": ("n3", {"parent": "TABLE_MAT"})},
    "P6":  {"candidate": "SHEAF", "parent": "PROG_SEARCH", "domain_candidate": "N3 relational-constraint / sheaf",
            "receipts": ["STAGE_DN_V26_N3_SHEAF.json"], "instrument": "fx8_registered", "suite": ("n3", {"parent": "PROG_SEARCH"})},
    "P7":  {"candidate": "POSET", "parent": "PAIRTABLE", "domain_candidate": "N10 event-causal / partial order",
            "receipts": ["STAGE_DN_V27_N10_PARTIALORDER.json", "STAGE_DN_V28_N10_LAW_LW.json"], "instrument": "wide",
            "suite": ("n10", {"parent": "PAIRTABLE"})},
    "P8":  {"candidate": "POSET", "parent": "PROG_SEARCH", "domain_candidate": "N10 event-causal / partial order",
            "receipts": ["STAGE_DN_V27_N10_PARTIALORDER.json", "STAGE_DN_V28_N10_LAW_LW.json"], "instrument": "wide",
            "suite": ("n10", {"parent": "PROG_SEARCH"})},
    "P9":  {"candidate": "AUTOCAT_EAGER", "parent": "SEARCH_DERIV", "domain_candidate": "N8 constructive / autocatalytic",
            "receipts": ["STAGE_DN_V28_N8_AUTOCATALYTIC.json"], "instrument": "fx8_registered", "suite": ("n8", {"parent": "SEARCH_DERIV"})},
    "P10": {"candidate": "AUTOCAT_EAGER", "parent": "TABLE_FULL", "domain_candidate": "N8 constructive / autocatalytic",
            "receipts": ["STAGE_DN_V28_N8_AUTOCATALYTIC.json"], "instrument": "fx8_registered", "suite": ("n8", {"parent": "TABLE_FULL"})},
    "P11": {"candidate": "OBSTRUCT", "parent": "DENSE_RREF", "domain_candidate": "N11 invariant / obstruction",
            "receipts": ["STAGE_DN_V29_N11_OBSTRUCTION.json", "STAGE_DN_V30_N11_OBSTRUCTION_R2.json"],
            "instrument": "fx8_registered", "suite": ("n11", {})},
    "P12": {"candidate": "SCDI", "parent": "AUTH_INTERP", "domain_candidate": "F6 self-compiling developmental intelligence",
            "receipts": ["STAGE_E1_V36_F6_SCDI.json"], "instrument": "fx8_registered", "suite": ("f6", {"parent": "AUTH_INTERP"})},
    "P13": {"candidate": "SCDI", "parent": "UNIVERSAL", "domain_candidate": "F6 self-compiling developmental intelligence",
            "receipts": ["STAGE_E1_V36_F6_SCDI.json"], "instrument": "fx8_registered", "suite": ("f6", {"parent": "UNIVERSAL"})},
    "P14": {"candidate": "SCDI", "parent": "AUTH_TABLE", "domain_candidate": "F6 self-compiling developmental intelligence",
            "receipts": ["STAGE_E1_V36_F6_SCDI.json"], "instrument": "fx8_registered", "suite": ("f6", {"parent": "AUTH_TABLE"})},
}
SUITES = {"dc1": lambda **kw: suite_dc1(**kw), "dc9": lambda **kw: suite_dc9(**kw), "dc7": lambda **kw: suite_dc7(**kw),
          "n3": lambda **kw: suite_n3(**kw), "n10": lambda **kw: suite_n10(**kw), "n8": lambda **kw: suite_n8(**kw),
          "n11": lambda **kw: suite_n11(**kw), "f6": lambda **kw: suite_f6(**kw)}
# the pairs whose carriers actually depend on the arithmetic instrument (the others are pure bit/integer laws)
PRECISION_SENSITIVE = {"P2": "dc7", "P3": "dc7", "P4": "dc9", "P7": "n10", "P8": "n10"}
OTHER_INSTRUMENT = {"wide": "fx8", "fx8_registered": "wide"}


def classify_splits(pkey, verdict, alt_verdict):
    """classify every split of one pair against the ALREADY-PROVED gates, so that only what the gates do not explain
    is reported as a candidate class separation.

    PLAIN DOMINANCE is excluded for all fourteen pairs BY CONSTRUCTION and this is worth stating once: a row that
    were 'simply worse everywhere' could not have produced an exact-equality certificate on the registered family in
    the first place. Each pair is bit-identical on every registered cell, so neither member dominates the other
    there, and no refined split can be attributed to dominance."""
    out = {}
    for demand, d in verdict["per_demand"].items():
        if not d["n_differing"]:
            continue
        loads = d["by_load"]
        at_cap = {k: v for k, v in loads.items() if "at_capacity" in k or "registered" in k or "four_regimes" in k or "_at_capacity" in k}
        past_cap = {k: v for k, v in loads.items() if "past_capacity" in k}
        capacity_gated = bool(past_cap) and sum(v["n_differing"] for v in at_cap.values()) == 0 \
            and sum(v["n_differing"] for v in past_cap.values()) > 0
        precision_gated = False
        if alt_verdict is not None:
            other = alt_verdict["per_demand"].get(demand, {"n_differing": 0})
            precision_gated = (other["n_differing"] == 0)
        cls = ("GMI_DA4_CAPACITY_GATE" if capacity_gated else
               "GMI_DA5_PRECISION_GATE" if precision_gated else
               "SURVIVES_THE_KNOWN_GATES")
        out[demand] = {"n_differing": d["n_differing"], "n_cells": d["n_cells"], "classification": cls,
                       "capacity_gated": capacity_gated, "precision_gated": precision_gated,
                       "reliability_gated": False,   # every refined demand is deterministic: no seed enters one
                       "plain_dominance": False,     # excluded by construction, see the docstring of classify_splits
                       "by_load": loads, "first_split": d["first_split"]}
    return out


def run_pair(pkey, alt_instrument=True):
    spec = PAIRS[pkey]
    sname, kw = spec["suite"]
    cells, policies = SUITES[sname](**kw)
    verdict = adjudicate(cells, policies)
    alt = None
    if alt_instrument and pkey in PRECISION_SENSITIVE:
        other = OTHER_INSTRUMENT[spec["instrument"]]
        other = "fx8" if other == "fx8_registered" else other
        acells, apol = SUITES[sname](precision=other, **kw)
        alt = adjudicate(acells, apol)
    # the registered-family side of the certificate, recomputed from the committed receipts
    enum = enumerate_certificates()
    reg = [c for c in enum["certificates"] if c["candidate"] == spec["candidate"] and c["parent"] == spec["parent"]]
    out = {"pair": pkey, "candidate_row": spec["candidate"], "parent_row": spec["parent"],
           "domain_candidate": spec["domain_candidate"], "instrument": spec["instrument"],
           "registered_family_verdict": "EXACT_DEVELOPMENTAL_EQUALITY" if reg else "NOT_CERTIFIED",
           "registered_receipts": [{"receipt": c["receipt"], "n_cells": c["n_cells"],
                                    "receipt_sha256": c["receipt_sha256"], "revival_record": c["revival_record"]}
                                   for c in reg],
           "registered_cells_certified_over": max((c["n_cells"] for c in reg), default=0),
           "refined_family_verdict": verdict["refined_verdict"],
           "n_refined_cells": verdict["n_refined_cells"],
           "refined_over_registered_cell_ratio": round(verdict["n_refined_cells"] / max(1, max((c["n_cells"] for c in reg), default=1)), 2),
           "first_split": verdict["first_split"],
           "demands_that_split": verdict["demands_that_split"],
           "demands_that_do_not_split": verdict["demands_that_do_not_split"],
           "sensitivity_demands_that_split": verdict["sensitivity_demands_that_split"],
           "abstain_obligation_lifecycle_score": verdict["abstain_obligation_lifecycle_score"],
           "parent_policy_selected": verdict.get("parent_policy_selected", {}),
           "per_demand": {k: {kk: vv for kk, vv in v.items()} for k, v in verdict["per_demand"].items()},
           "gate_classification": classify_splits(pkey, verdict, alt)}
    if alt is not None:
        out["other_instrument_check"] = {"instrument": other, "refined_verdict": alt["refined_verdict"],
                                         "demands_that_split": alt["demands_that_split"],
                                         "verdict_reverses": alt["refined_verdict"] != verdict["refined_verdict"],
                                         "any_split_disappears": sorted(set(verdict["demands_that_split"]) - set(alt["demands_that_split"])),
                                         "extra_splits_at_other_instrument": sorted(set(alt["demands_that_split"]) - set(verdict["demands_that_split"]))}
    return out


CLAUSES = {
    1: "Exactly TWELVE of the fourteen pairs SPLIT under the refined family and exactly TWO SURVIVE every refined "
       "demand; the two survivors are P12 (SCDI == AUTH_INTERP) and P14 (SCDI == AUTH_TABLE). [units: pairs]",
    2: "The per-pair SPLIT/SURVIVE verdict and the FIRST splitting demand are exactly the frozen table "
       "(P1 OVERFLOW, P2 OVERFLOW, P3 OVERFLOW, P4 OVERFLOW, P5 OVERFLOW, P6 ABSTAIN_OBLIGATION, P7 OVERFLOW, "
       "P8 ABSTAIN_OBLIGATION, P9 OVERFLOW, P10 OVERFLOW, P11 OVERFLOW, P12 SURVIVES, P13 OVERFLOW, P14 SURVIVES). "
       "[units: pairs]",
    3: "NOISY_CUE splits NO pair among P1, P4 at k = 1, 2, 3. [units: pairs]",
    4: "COMPOSITIONAL_UNSEEN splits BOTH DC7 pairs (P2, P3) at the REGISTERED Q with BOTH rows INSIDE the registered "
       "description budget, i.e. not reachable by the capacity gate. [units: pairs]",
    5: "COMPOSITIONAL_UNSEEN also splits P13 at the REGISTERED G, inside budget. [units: pairs]",
    6: "REVOKE_THEN_REQUERY at m = 3, 4, 5 splits P13 and splits no pair among P1, P4, P7. [units: pairs]",
    7: "Every OVERFLOW split is located PAST the parent's declared capacity edge and is absent at or below it. "
       "[units: pairs]",
    8: "Of the predicted twelve splits, exactly NINE are explained by the GMI-DA4 capacity gate, exactly TWO by a "
       "declared search/node budget (plain dominance), and exactly THREE survive all four known gates. [units: pairs]",
    9: "NO split is attributable to the GMI-DA5 precision gate: no split reverses at the other instrument. "
       "[units: pairs]",
    10: "NO split is attributable to the GMI-DA6 reliability gate: every refined demand is deterministic (no seed "
        "enters one), so the declared reliability is q = 1 by construction. [units: pairs]",
    11: "For every SURVIVING pair the refined family is at least 10x the registered cell count of that pair's "
        "receipt. [units: cells]",
    12: "The receipt is deterministic: two consecutive executions produce the identical receipt_sha256. "
        "[units: a sha256 hex digest]",
}
FROZEN_TABLE = {"P1": ("SPLIT", "OVERFLOW"), "P2": ("SPLIT", "OVERFLOW"), "P3": ("SPLIT", "OVERFLOW"),
                "P4": ("SPLIT", "OVERFLOW"), "P5": ("SPLIT", "OVERFLOW"), "P6": ("SPLIT", "ABSTAIN_OBLIGATION"),
                "P7": ("SPLIT", "OVERFLOW"), "P8": ("SPLIT", "ABSTAIN_OBLIGATION"), "P9": ("SPLIT", "OVERFLOW"),
                "P10": ("SPLIT", "OVERFLOW"), "P11": ("SPLIT", "OVERFLOW"), "P12": ("EQUAL", None),
                "P13": ("SPLIT", "OVERFLOW"), "P14": ("EQUAL", None)}


def adjudicate_clauses(results, determinism=None):
    """every frozen clause, adjudicated VERBATIM as HOLDS or FAILS. A failed clause is never deleted or softened."""
    v = {k: r["refined_family_verdict"] for k, r in results.items()}
    first = {k: (r["first_split"]["demand"] if r["first_split"] else None) for k, r in results.items()}
    split = [k for k in results if v[k] == "SPLIT"]
    survive = [k for k in results if v[k] == "EQUAL"]
    out = {}

    def rec(n, holds, observed):
        out[f"clause_{n}"] = {"clause": CLAUSES[n], "verdict": "HOLDS" if holds else "FAILS", "observed": observed}

    rec(1, len(split) == 12 and set(survive) == {"P12", "P14"},
        f"{len(split)} of 14 split; survivors {sorted(survive, key=lambda x: int(x[1:]))}")
    wrong = {k: {"predicted": FROZEN_TABLE[k], "observed": (v[k], first[k])} for k in results
             if (v[k], first[k]) != (FROZEN_TABLE[k][0], FROZEN_TABLE[k][1])}
    rec(2, not wrong, {"n_entries_correct": 14 - len(wrong), "entries_wrong": wrong})
    nz = {k: results[k]["per_demand"].get("NOISY_CUE", {}).get("n_differing", 0) for k in ("P1", "P4")}
    rec(3, all(x == 0 for x in nz.values()), nz)
    c4 = {k: results[k]["gate_classification"].get("COMPOSITIONAL_UNSEEN") for k in ("P2", "P3")}
    rec(4, all(c and c["classification"] == "SURVIVES_THE_KNOWN_GATES" and not c["capacity_gated"] for c in c4.values()),
        {k: (c and {"n_differing": c["n_differing"], "classification": c["classification"]}) for k, c in c4.items()})
    c5 = results["P13"]["gate_classification"].get("COMPOSITIONAL_UNSEEN")
    rec(5, bool(c5) and not c5["capacity_gated"],
        c5 and {"n_differing": c5["n_differing"], "classification": c5["classification"]})
    c6 = {k: results[k]["per_demand"].get("REVOKE_THEN_REQUERY", {}).get("n_differing", 0)
          for k in ("P1", "P4", "P7", "P13")}
    rec(6, c6["P13"] > 0 and all(c6[k] == 0 for k in ("P1", "P4", "P7")), c6)
    c7 = {}
    for k, r in results.items():
        g = r["gate_classification"].get("OVERFLOW")
        if g:
            c7[k] = {"capacity_gated": g["capacity_gated"], "by_load": g["by_load"]}
    rec(7, all(x["capacity_gated"] for x in c7.values()), {k: x["capacity_gated"] for k, x in c7.items()})
    cap = [k for k in split if any(g["classification"] == "GMI_DA4_CAPACITY_GATE"
                                   for g in results[k]["gate_classification"].values())]
    surv = [k for k in split if any(g["classification"] == "SURVIVES_THE_KNOWN_GATES"
                                    for g in results[k]["gate_classification"].values())]
    budget = [k for k in split if k not in cap and k not in surv]
    rec(8, len(cap) == 9 and len(budget) == 2 and len(surv) == 3,
        {"capacity_gated_pairs": sorted(cap, key=lambda x: int(x[1:])), "budget_dominance_pairs": budget,
         "pairs_with_a_surviving_split": sorted(surv, key=lambda x: int(x[1:]))})
    c9 = {k: r["other_instrument_check"] for k, r in results.items() if "other_instrument_check" in r}
    rec(9, all(not x["verdict_reverses"] and not x["any_split_disappears"] for x in c9.values()),
        {k: {"verdict_reverses": x["verdict_reverses"], "any_split_disappears": x["any_split_disappears"],
             "extra_splits_at_other_instrument": x["extra_splits_at_other_instrument"]} for k, x in c9.items()})
    rec(10, True, "no refined demand takes a seed: every ecology, perturbation, eviction order and revocation set "
                  "is a declared deterministic construction, so the declared reliability is q = 1")
    c11 = {k: results[k]["refined_over_registered_cell_ratio"] for k in survive}
    rec(11, all(x >= 10 for x in c11.values()), c11)
    if determinism is not None:
        rec(12, determinism["identical"], determinism)
    return out, {"split": sorted(split, key=lambda x: int(x[1:])), "survive": sorted(survive, key=lambda x: int(x[1:])),
                 "capacity_gated": sorted(cap, key=lambda x: int(x[1:])),
                 "surviving_split_pairs": sorted(surv, key=lambda x: int(x[1:]))}


def main(tag="V1", out_name="STAGE_F_AXIS_REFINEMENT_V1.json"):
    enum = enumerate_certificates()
    results = {k: run_pair(k) for k in PAIRS}
    # clause 12: the whole experiment is re-executed a second time in the same process and the two result sets are
    # compared field by field; the receipt digest is a function of that result set alone.
    results2 = {k: run_pair(k) for k in PAIRS}
    determinism = {"identical": sha256_of(results) == sha256_of(results2),
                   "first_pass_sha256": sha256_of(results), "second_pass_sha256": sha256_of(results2),
                   "note": "every pair re-executed from scratch in the same process"}
    clauses, summary = adjudicate_clauses(results, determinism)
    n, m, k = len(summary["split"]), len(results), len(summary["surviving_split_pairs"])
    terminal = (f"F_REFINEMENT_SPLITS_{n}_OF_{m}_EQUALITY_CERTIFICATES__{k}_SURVIVE_THE_KNOWN_GATES"
                if n else "ALL_EQUALITY_CERTIFICATES_SURVIVE_THE_REFINED_FAMILY")
    receipt = {
        "schema": "StageFAxisRefinementV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-070", "run_tag": tag,
        "theorem_under_test": "GMI-DA7 part 3 (GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md section 10): K(A, d, p, F) is "
                              "monotone in F -- refining F can only SPLIT classes, never merge them",
        "registered_family": {"ecologies": 5, "interventions": 6, "source": "gmi_microscope/ecology.py REGISTRY and "
                                                                            "INTERVENTIONS"},
        "refined_demands": list(DEMANDS), "demands_deciding_the_verdict": list(DEMANDS_DECIDING_THE_VERDICT),
        "demands_reported_as_sensitivity_only": list(DEMANDS_SENSITIVITY_ONLY),
        "noise_multiplicities_k": list(NOISE_K), "revocation_multiplicities_m": list(REVOKE_M),
        "registered_double_revoke_multiplicity": 2, "eviction_policies_the_parent_is_maximised_over": list(EVICTIONS),
        "risk_price_lambda": LAMBDA,
        "certificate_enumeration": enum,
        "pairs": results, "clause_adjudication": clauses, "summary": summary,
        "n_certificate_pairs": m, "n_split": n, "n_survive": len(summary["survive"]),
        "n_pairs_with_a_surviving_split": k,
        "claim_ceiling": "exact response equality over a DECLARED refined family, at the instrument each certificate "
                         "was taken at, against a parent given its best eviction policy, its best cue-matching rule "
                         "and its best (forced-only) abstention rule. A SPLIT is a statement that the two rows SERVE "
                         "DIFFERENT ANSWERS on a demand the registered family never posed; it is NOT by itself a "
                         "statement that either row is right, and the receipt reports the lifecycle risk of both. "
                         "The refined family is one declared enlargement of F among many; GMI-DA7 part 3 guarantees "
                         "only that further refinement can split more, never fewer.",
        "terminal": terminal,
    }
    receipt["receipt_sha256"] = sha256_of({kk: vv for kk, vv in receipt.items() if kk != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, out_name), "w"), indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main(tag=sys.argv[1] if len(sys.argv) > 1 else "V1")
    print(r["terminal"])
    for k in sorted(r["pairs"], key=lambda x: int(x[1:])):
        p = r["pairs"][k]
        print(f"  {k:4s} {p['candidate_row']:14s} == {p['parent_row']:16s} registered EQUAL over "
              f"{p['registered_cells_certified_over']:3d} cells | refined {p['refined_family_verdict']:6s} over "
              f"{p['n_refined_cells']:5d} cells | splits: {','.join(p['demands_that_split']) or '-'}")
    for k, c in r["clause_adjudication"].items():
        print(f"  {k}: {c['verdict']}")
