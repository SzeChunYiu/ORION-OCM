"""N8 — constructive / autocatalytic carrier: exact microscope and bounded-reduction attack
(novel-domain hypothesis N8 "Constructive / Autocatalytic Intelligence"; method of
GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md sections 0 and 2; domain criterion
GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md section 2, novelty criterion section 14;
record RV-377-052, companion of RV-377-044 / RV-377-045).

HYPOTHESIS SPEC AS EXECUTED HERE (reconstructed from the Track B brief; the upstream
GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md is not present on this branch — see
GMI_DOMAIN_N8_N11_EXECUTED_V1.md section 0):

  carrier              a CONSTRUCTION SET: a small set of seed artifacts plus a small set of
                       composition rules, together with the set of artifacts BUILT SO FAR.
                       Sufficient cognitive state = seeds + rules; the built set is the carrier's
                       developmental body, and products re-enter as reagents (autocatalysis).
  native operators     BUILD (apply a rule to two already-built artifacts), CLOSE (one round of BUILD
                       over the whole built set, products re-entering), MEMBER (is this artifact built?).
  complexity coord.    the artifact-size cap L, which controls the closure size |C(L)| exponentially
                       while the seed/rule description stays constant.
  predicted niche      obligations whose answer set is exponentially larger than the generating rule
                       set, and whose queries ask CONSTRUCTIBILITY of artifacts never shown.
  capability hypothesis  exact decision of constructibility with a description that is the rule set,
                       not the answer set, and a serve cost that does not re-derive per query.
  weak regime          short reuse horizons: the closure must be paid for before the first query.
  parent attacks       (D5/D4) a program-search row that tests derivations ONE BY ONE per query and
                       never reuses products across or within queries; (D2) a memory/table row GIVEN
                       the whole closure at construction (the strongest possible memory parent).
  domain discriminator does a bounded semantics-preserving reduction to D2/D5 exist, and is the
                       lifecycle burden of that reduction qualitatively different?

ECOLOGY E_construct(L): artifacts are bit strings of length <= L. Declared seeds SEEDS; the single
declared rule is CONCAT(u, v) = uv when |uv| <= L. The closure C(L) is the set of concatenations of
seeds of length <= L; it grows exponentially in L while |SEEDS| and the rule set stay fixed.
Development streams the seeds (as construction events) and then n_dev LABELLED SHALLOW instances
(artifacts of at most two blocks) — every row sees exactly the same events. Evaluation asks
constructibility of n_eval artifacts NEVER shown, the majority of them DEEP members of the closure
(three or more blocks), the rest non-constructible strings of the same lengths.

Rows (all charged exactly; identical queries, answers compared bit for bit):
  AUTOCAT_EAGER   the candidate: run CLOSE to a fixed point during development (products re-entering
                  as reagents), serve MEMBER against the built set.
  AUTOCAT_LAZY    the same carrier served lazily: seeds and the rule only; every query rebuilds the
                  closure up to the queried length and then tests membership. Small description,
                  large serve cost - the other end of the same carrier.
  SEARCH_DERIV    the strongest D5/D4 parent: per query, search for a derivation of the target by
                  recursive splitting, testing candidate decompositions ONE BY ONE, with NO reuse of
                  sub-results within or across queries. Exponential in the artifact length; a declared
                  node budget yields -1 ("no decision", counted incorrect) rather than a lucky default.
  TABLE_FULL      the strongest D2 parent: GIVEN the entire closure at construction (charged inserts)
                  and answering by indexed MEMBER. Its answers are identical to AUTOCAT_EAGER's by
                  construction, so this row is the bounded-reduction attack: if it matches at bounded
                  overhead, N8 is REDUCED_TO_PARENT(D2).
  TABLE_SEEN      a fair D2 parent: only the labelled shallow development instances.
  AUTOCAT_NOFEED  negative twin: the candidate with autocatalysis removed - one BUILD round over the
                  seeds only, products never re-entering as reagents.

Accounting: exec/upd/ver/rev are exact charged Machine ops on the B0 column (the REDUCED price
vector, one op per character operation). Membership uses a DECLARED binary index (the same amendment
as bases.py `indexed_emulation`): a real binary search with charged lexicographic comparisons.
`native_ops` counts the DECLARED NATIVE price (one op per CLOSE round, one per MEMBER lookup, one per
tested derivation node). `desc_bits` is the information-theoretic description of the SERVED state.
"""
from __future__ import annotations

import json
import math
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
SEEDS = ((0, 1), (1, 1, 0))       # declared seed artifacts: "01" and "110" (block lengths 2 and 3)
RULE_DESC_BITS = 8                # declared descriptor of the single CONCAT rule
NODE_BUDGET = 400000              # declared derivation-node budget for SEARCH_DERIV


class Budget(Exception):
    pass


class Lcg:
    def __init__(self, seed): self.x = seed & 0xFFFFFFFF

    def nxt(self):
        self.x = (self.x * 1103515245 + 12345) & 0xFFFFFFFF
        return self.x >> 16


# ------------------------------------------------------------------ charged artifact primitives
def _concat(M, u, v):
    """charged BUILD: one CONST op per character written."""
    return tuple(M.op("CONST", c) for c in u + v)


def _cmp(M, a, b):
    """charged lexicographic comparison of two artifacts: -1, 0, +1."""
    for i in range(min(len(a), len(b))):
        if not M.op("EQ", a[i], b[i]):
            return -1 if M.op("GT", b[i], a[i]) else 1
    if M.op("EQ", len(a), len(b)): return 0
    return -1 if M.op("GT", len(b), len(a)) else 1


def _member(M, srt, w):
    """charged MEMBER: a real binary search over the sorted built set (declared binary index)."""
    lo, hi = 0, len(srt) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        c = _cmp(M, w, srt[mid])
        if c == 0: return 1
        if c < 0: hi = mid - 1
        else: lo = mid + 1
    return 0


def _insert(M, srt, w):
    """charged ordered insert: locate by binary search, then charge one CONST per shifted slot."""
    lo, hi = 0, len(srt) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        c = _cmp(M, w, srt[mid])
        if c == 0: return 0
        if c < 0: hi = mid - 1
        else: lo = mid + 1
    for _ in range(len(srt) - lo): M.op("CONST", 0)
    srt.insert(lo, w)
    return 1


def _close_round(M, srt, L):
    """one charged CLOSE round: every ordered pair of ALREADY-BUILT artifacts, products re-entering."""
    cur = list(srt); added = 0
    for u in cur:
        for v in cur:
            if len(u) + len(v) > L: continue
            w = _concat(M, u, v)
            added += _insert(M, srt, w)
    return added


# ------------------------------------------------------------------ ecology
def closure(L):
    """uncharged ground truth: the set of concatenations of SEEDS of length <= L."""
    cur = set(SEEDS)
    while True:
        new = set(cur)
        for u in cur:
            for v in cur:
                if len(u) + len(v) <= L: new.add(u + v)
        if new == cur: return cur
        cur = new


def _blocks(w):
    """minimum number of seed blocks in a decomposition of w, or None if not constructible."""
    n = len(w); best = [None] * (n + 1); best[0] = 0
    for i in range(1, n + 1):
        for s in SEEDS:
            j = i - len(s)
            if j >= 0 and best[j] is not None and tuple(w[j:i]) == s:
                best[i] = best[j] + 1 if best[i] is None else min(best[i], best[j] + 1)
    return best[n]


def ecology(L, n_dev=6, n_eval=8, n_deep_eval=5, seed=23):
    C = closure(L)
    shallow = sorted(w for w in C if (_blocks(w) or 99) <= 2)
    deep = sorted(w for w in C if (_blocks(w) or 0) >= 3)
    g = Lcg(seed)
    dev = [(w, 1) for w in shallow[:n_dev]]
    seen = {w for w, _ in dev}
    ev = []
    while len(ev) < n_deep_eval:                      # DISTINCT deep closure members, never shown
        w = deep[g.nxt() % len(deep)]
        if w in seen: continue
        seen.add(w); ev.append((w, 1))
    # non-constructible distractors of the same lengths, drawn from the declared LCG
    lens = [len(ev[i % len(ev)][0]) for i in range(n_eval - n_deep_eval)]
    for ln in lens:
        while True:
            w = tuple(g.nxt() & 1 for _ in range(ln))
            if w not in C and w not in seen: seen.add(w); ev.append((w, 0)); break
    return {"L": L, "closure": sorted(C), "closure_size": len(C), "n_shallow": len(shallow), "n_deep": len(deep),
            "dev": dev, "eval": ev, "n_constructible_eval": sum(a for _, a in ev)}


# ------------------------------------------------------------------ rows
class Row:
    row = "?"

    def __init__(self, eco): self.e = eco; self.native_ops = 0; self.budget_exhausted = 0; self.rounds = 0

    def init(self, M): pass

    def see_seed(self, M, s): pass

    def see_instance(self, M, w, label): pass

    def compile(self, M): pass

    def query(self, M, w): raise NotImplementedError

    def desc_bits(self): return 0


def _artifact_bits(L):
    return L + max(1, math.ceil(math.log2(L + 1)))


class AutocatEager(Row):
    """the candidate served eagerly: CLOSE to a fixed point during development."""
    row = "AUTOCAT_EAGER"

    def init(self, M): self.built = []

    def see_seed(self, M, s): _insert(M, self.built, s)

    def compile(self, M):
        L = self.e["L"]
        while True:
            added = _close_round(M, self.built, L); self.rounds += 1; self.native_ops += 1
            if not added: break

    def query(self, M, w):
        self.native_ops += 1
        return _member(M, self.built, w)

    def desc_bits(self): return len(self.built) * _artifact_bits(self.e["L"])


class AutocatLazy(Row):
    """the same carrier served lazily: seeds and the rule only; rebuild the closure per query."""
    row = "AUTOCAT_LAZY"

    def init(self, M): self.seeds = []

    def see_seed(self, M, s): self.seeds.append(s)

    def query(self, M, w):
        built = []
        for s in self.seeds: _insert(M, built, s)
        while True:
            added = _close_round(M, built, len(w)); self.rounds += 1; self.native_ops += 1
            if not added: break
        self.native_ops += 1
        return _member(M, built, w)

    def desc_bits(self): return len(self.seeds) * _artifact_bits(self.e["L"]) + RULE_DESC_BITS


class AutocatNoFeed(AutocatEager):
    """negative twin: autocatalysis removed - ONE build round over the seeds, products never re-enter."""
    row = "AUTOCAT_NOFEED"

    def compile(self, M):
        _close_round(M, self.built, self.e["L"]); self.rounds = 1; self.native_ops += 1


class SearchDeriv(Row):
    """the strongest D5/D4 parent: per query, test candidate derivations ONE BY ONE by recursive
    splitting, with no reuse of sub-results (the mechanism autocatalysis adds)."""
    row = "SEARCH_DERIV"

    def init(self, M): self.seeds = []

    def see_seed(self, M, s): self.seeds.append(s)

    def _derive(self, M, w):
        self.nodes += 1; self.native_ops += 1
        if self.nodes > NODE_BUDGET: raise Budget
        for s in self.seeds:
            if _cmp(M, w, s) == 0: return True
        for i in range(1, len(w)):
            if self._derive(M, w[:i]) and self._derive(M, w[i:]): return True
        return False

    def query(self, M, w):
        self.nodes = 0
        try:
            return int(self._derive(M, w))
        except Budget:
            self.budget_exhausted = 1
            return -1

    def desc_bits(self): return len(self.seeds) * _artifact_bits(self.e["L"]) + RULE_DESC_BITS


class TableFull(Row):
    """the strongest D2 parent: GIVEN the entire closure at construction; indexed MEMBER per query."""
    row = "TABLE_FULL"

    def init(self, M): self.built = []

    def compile(self, M):
        for w in self.e["closure"]: _insert(M, self.built, w)

    def query(self, M, w):
        self.native_ops += 1
        return _member(M, self.built, w)

    def desc_bits(self): return len(self.built) * _artifact_bits(self.e["L"])


class TableSeen(Row):
    """a fair D2 parent: only the labelled shallow development instances."""
    row = "TABLE_SEEN"

    def init(self, M): self.built = []; self.labels = {}

    def see_instance(self, M, w, label):
        _insert(M, self.built, w); self.labels[w] = label

    def query(self, M, w):
        self.native_ops += 1
        if _member(M, self.built, w): return self.labels[w]
        return -1  # no stored key: no decision (counts as incorrect; never a lucky default)

    def desc_bits(self): return len(self.built) * (_artifact_bits(self.e["L"]) + 1)


ROWS = {"AUTOCAT_EAGER": AutocatEager, "AUTOCAT_LAZY": AutocatLazy, "SEARCH_DERIV": SearchDeriv,
        "TABLE_FULL": TableFull, "TABLE_SEEN": TableSeen, "AUTOCAT_NOFEED": AutocatNoFeed}


def run(row, basis, eco, seed=0):
    M = Machine(basis, seed=seed); ref = ROWS[row](eco)
    M.phase("exec"); ref.init(M)
    for s in SEEDS:
        M.phase("upd"); ref.see_seed(M, s); M.end_event()
    for w, lab in eco["dev"]:
        M.phase("upd"); ref.see_instance(M, w, lab); M.end_event()
    M.phase("upd"); ref.compile(M); M.end_event()
    after_dev = dict(M.L.c)
    M.phase("exec"); correct = 0; answers = []; deep_exec = 0; n_deep = 0
    for idx, (w, lab) in enumerate(eco["eval"]):
        before = M.L.c["exec"]
        a = ref.query(M, w)
        answers.append((idx, a)); correct += int(a == lab)
        if lab == 1: deep_exec += M.L.c["exec"] - before; n_deep += 1
    n = len(eco["eval"]); cap = round(correct / n, 4)
    R = dict(M.L.c)
    return {"row": row, "basis": basis.name, "capability": cap, "admissible": cap >= THETA, "R": R,
            "compile_ops": after_dev["upd"], "exec_per_query": round((R["exec"] - after_dev["exec"]) / n, 4),
            "exec_per_constructible_query": round(deep_exec / n_deep, 4) if n_deep else 0.0,
            "native_ops": ref.native_ops, "native_per_query": round(ref.native_ops / n, 4),
            "desc_bits": ref.desc_bits(), "close_rounds": ref.rounds, "n_queries": n,
            "budget_exhausted": ref.budget_exhausted, "answer_signature": sha256_of(answers)}


CELLS = {"L8": {"L": 8}, "L10": {"L": 10}, "L12": {"L": 12}, "L14": {"L": 14}, "L16": {"L": 16}, "L18": {"L": 18}}


def lifecycle(r, H, native=False):
    return r["desc_bits"] + H * (r["native_per_query"] if native else r["exec_per_query"]) + (0 if native else r["compile_ops"])


def crossovers(per, native=False):
    """analytic reuse-horizon crossovers H* between every pair of ADMISSIBLE rows (DG-2)."""
    out = {}
    names = [r for r in per if per[r]["admissible"]]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = per[a], per[b]
            sa = ra["native_per_query"] if native else ra["exec_per_query"]
            sb = rb["native_per_query"] if native else rb["exec_per_query"]
            ca = ra["desc_bits"] + (0 if native else ra["compile_ops"])
            cb = rb["desc_bits"] + (0 if native else rb["compile_ops"])
            if sa == sb: out[f"{a}|{b}"] = None; continue
            h = (cb - ca) / (sa - sb)
            out[f"{a}|{b}"] = round(h, 4) if h > 0 else None
    return out


def grid_for(cx_list, base=(1, 16, 128, 1024)):
    """declared grid rule (DG-2): the base grid, every finite positive crossover bracketed, and twice
    the largest crossover - so no 'no cell exists' clause is ever checked on a truncated grid."""
    hs = set(base)
    finite = [h for cx in cx_list for h in cx.values() if h is not None and h > 0]
    for h in finite:
        hs.add(max(1, int(math.floor(h)))); hs.add(int(math.ceil(h)) + 1)
    if finite: hs.add(int(math.ceil(2 * max(finite))))
    return sorted(hs)


def main(tag="V28_N8_AUTOCATALYTIC", seed=0, cells_subset=None):
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; b = bases.ALL[col]
    specs = {c: s for c, s in CELLS.items() if cells_subset is None or c in cells_subset}
    cells = {}; ecos = {}
    for cname, spec in specs.items():
        eco = ecology(spec["L"]); ecos[cname] = eco
        for rname in ROWS:
            cells[(cname, rname)] = run(rname, b, eco, seed)

    equality = {}
    for cname in specs:
        for parent in ("TABLE_FULL", "SEARCH_DERIV", "AUTOCAT_LAZY", "TABLE_SEEN"):
            equality[f"{cname}|AUTOCAT_EAGER=={parent}"] = cells[(cname, "AUTOCAT_EAGER")]["answer_signature"] == cells[(cname, parent)]["answer_signature"]

    growth = {}
    for cname in sorted(specs, key=lambda c: specs[c]["L"]):
        e = ecos[cname]; ae = cells[(cname, "AUTOCAT_EAGER")]; tf = cells[(cname, "TABLE_FULL")]
        al = cells[(cname, "AUTOCAT_LAZY")]; sd = cells[(cname, "SEARCH_DERIV")]
        growth[cname] = {"L": e["L"], "closure_size": e["closure_size"], "close_rounds": ae["close_rounds"],
                         "autocat_eager_desc_bits": ae["desc_bits"], "autocat_lazy_desc_bits": al["desc_bits"],
                         "table_full_desc_bits": tf["desc_bits"],
                         "desc_ratio_table_over_lazy": round(tf["desc_bits"] / al["desc_bits"], 4),
                         "autocat_eager_compile_ops": ae["compile_ops"], "table_full_compile_ops": tf["compile_ops"],
                         "autocat_eager_exec_per_query": ae["exec_per_query"], "table_full_exec_per_query": tf["exec_per_query"],
                         "autocat_lazy_exec_per_query": al["exec_per_query"],
                         "search_deriv_exec_per_constructible_query": sd["exec_per_constructible_query"],
                         "search_over_eager_exec": round(sd["exec_per_query"] / ae["exec_per_query"], 4) if ae["exec_per_query"] else None}

    frontier = {}; cx_all = {}
    for cname in specs:
        per = {r: cells[(cname, r)] for r in ROWS}
        for price in ("reduced", "native"):
            cx = crossovers(per, native=(price == "native")); cx_all[f"{cname}|{price}"] = cx
            for H in grid_for([cx]):
                adm = [r for r in ROWS if per[r]["admissible"]]
                costs = {r: lifecycle(per[r], H, native=(price == "native")) for r in adm}
                frontier[f"{cname}|{price}|H={H}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else []

    receipt = {
        "schema": "StageDN28N8AutocatalyticV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-052", "run_tag": tag,
        "domain_candidate": "N8 constructive / autocatalytic intelligence",
        "hypothesis_source": "reconstructed from the Track B brief; GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md is absent from this branch (see GMI_DOMAIN_N8_N11_EXECUTED_V1.md section 0)",
        "column": col, "theta": THETA, "seeds": [list(s) for s in SEEDS], "rule": "CONCAT(u, v) = uv when |uv| <= L",
        "node_budget": NODE_BUDGET, "cells_spec": specs, "rows": list(ROWS),
        "ecology_facts": {c: {"L": ecos[c]["L"], "closure_size": ecos[c]["closure_size"], "n_shallow": ecos[c]["n_shallow"],
                              "n_deep": ecos[c]["n_deep"], "n_dev": len(ecos[c]["dev"]), "n_eval": len(ecos[c]["eval"]),
                              "n_constructible_eval": ecos[c]["n_constructible_eval"]} for c in specs},
        "description_semantics": {
            "AUTOCAT_EAGER": "|built| * (L + ceil(log2(L+1))) bits: the materialized built set",
            "AUTOCAT_LAZY": "|SEEDS| * (L + ceil(log2(L+1))) + 8 bits: seeds plus the rule descriptor",
            "SEARCH_DERIV": "|SEEDS| * (L + ceil(log2(L+1))) + 8 bits: seeds plus the rule descriptor",
            "TABLE_FULL": "|C(L)| * (L + ceil(log2(L+1))) bits: the whole closure",
            "TABLE_SEEN": "n_dev * (L + ceil(log2(L+1)) + 1) bits: artifact plus label",
            "AUTOCAT_NOFEED": "|one-round built set| * (L + ceil(log2(L+1))) bits"},
        "native_price_vector": "one op per CLOSE round, one per MEMBER lookup, one per tested derivation node; declared, not measured",
        "membership_instrument": "DECLARED binary index (the bases.py indexed_emulation amendment): a real binary search with charged lexicographic comparisons, used identically by every row that stores artifacts",
        "cells": {f"{c}|{r}": {k: v for k, v in d.items() if k not in ("row", "basis")} for (c, r), d in cells.items()},
        "autocat_equals_parent_answers": equality, "growth_law_L_sweep": growth,
        "frontier_crossovers": cx_all, "frontier": frontier,
        "claim_ceiling": "exact charged replay at scope on one declared seed/rule family per cell; the reduction attack is an exact answer-signature test against a memory parent that is GIVEN the closure; native prices are declared, not measured; no new domain is claimed",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DN_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("AUTOCAT_EAGER == TABLE_FULL answers everywhere:", all(v for k, v in equality.items() if "TABLE_FULL" in k))
    for cname in specs:
        print(cname, "|C|", ecos[cname]["closure_size"], {r: cells[(cname, r)]["capability"] for r in ROWS},
              "| desc", {r: cells[(cname, r)]["desc_bits"] for r in ("AUTOCAT_EAGER", "AUTOCAT_LAZY", "TABLE_FULL")},
              "| exec/q", {r: cells[(cname, r)]["exec_per_query"] for r in ("AUTOCAT_EAGER", "AUTOCAT_LAZY", "SEARCH_DERIV")})
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V28_N8_AUTOCATALYTIC")
