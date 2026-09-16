"""Neutral search engine v2 — GMI #833 blind-recovery protocol v2.

Generic cost-layered search over expression trees in a FROZEN basis
(BASIS_GRID_V1.json). Reads ONLY the frozen battery JSON (task rows) and the
basis definition. It never reads the family benchmark, fingerprints, or any
family vocabulary. Two procedures with disjoint mechanics:

  PROC1 SEMANTIC_COST_LAYERED_DP — exhaustive layer-wise enumeration over the
       semantic quotient (dedup by exact row-tuple semantics, min-cost
       representative kept). First layer containing the target semantics is a
       complete no-solution-below-cost certificate.

  PROC2 UNIFORM_COST_BEST_FIRST — independent heap-based best-first expansion
       over the same basis with a closed set on pop and a postfix encoding;
       verifies PROC1's cost with different mechanics.

Both are blind: their inputs are (atoms, basis, guard, targets, cap) only.
"""
from __future__ import annotations

import heapq
import json
from pathlib import Path

LAYER_CAP_DEFAULT = 16  # safety cap; derivation in BASIS_GRID_V1.json
WIDTH_CAP_DEFAULT = 2_000_000  # machine-capacity bound: semantics retained
# per layer kept under a bounded working set (~200 MB/layer incl. dict
# overhead); hitting it is REPORTED as width_bound (never silently).


# ---------------------------------------------------------------------------
# basis
# ---------------------------------------------------------------------------

class Basis:
    """Frozen primitive basis. unary_tier in {U_ORD, U_ALL3, U_V1}."""

    def __init__(self, unary_tier: str, guard: int, constants=(-1, 0, 1)):
        self.tier = unary_tier
        self.guard = guard
        self.constants = tuple(constants)
        self.domain = tuple(range(-guard, guard + 1))
        self.unaries: dict = {}
        if unary_tier == "U_ORD":
            self.unaries["NEG"] = {v: -v for v in self.domain}
            for c in self.domain:
                self.unaries[f"GE{c:+d}"] = {v: (1 if v >= c else 0)
                                             for v in self.domain}
        elif unary_tier == "U_V1":
            self.unaries["NEG"] = {v: -v for v in self.domain}
            self.unaries["POS"] = {v: (1 if v > 0 else 0) for v in self.domain}
        elif unary_tier == "U_ALL3":
            # all total unary maps on D (feasible |D|=3 only)
            import itertools
            if len(self.domain) != 3:
                raise ValueError("U_ALL3 requires |D|=3 (guard 1)")
            for i, outs in enumerate(itertools.product(self.domain, repeat=3)):
                self.unaries[f"U{i:02d}"] = dict(zip(self.domain, outs))
        else:
            raise ValueError(unary_tier)
        self.binaries = ("ADD",)

    def unary_names(self):
        return sorted(self.unaries)

    def describe(self):
        return {"tier": self.tier, "guard": self.guard,
                "constants": list(self.constants),
                "unary_count": len(self.unaries),
                "unary_names": self.unary_names()[:24],
                "binaries": list(self.binaries)}


# expressions: ("atom", name) | ("const", v) | ("un", name, e) | ("add", a, b)

def expr_key(e):
    return repr(e)


def expr_canon(e):
    if e[0] == "add":
        a, b = expr_canon(e[1]), expr_canon(e[2])
        return ("add", a, b) if expr_key(a) <= expr_key(b) else ("add", b, a)
    if e[0] == "un":
        return ("un", e[1], expr_canon(e[2]))
    return e


def expr_eval(e, row_env, basis):
    op = e[0]
    if op == "atom":
        return row_env[e[1]]
    if op == "const":
        return e[1]
    if op == "un":
        return basis.unaries[e[1]][expr_eval(e[2], row_env, basis)]
    if op == "add":
        return expr_eval(e[1], row_env, basis) + expr_eval(e[2], row_env, basis)
    raise ValueError(op)


def expr_depth(e):
    if e[0] in ("atom", "const"):
        return 0
    if e[0] == "un":
        return 1 + expr_depth(e[2])
    return 1 + max(expr_depth(e[1]), expr_depth(e[2]))


def expr_ops(e):
    if e[0] in ("atom", "const"):
        return 0
    if e[0] == "un":
        return 1 + expr_ops(e[2])
    return 1 + expr_ops(e[1]) + expr_ops(e[2])


def expr_to_postfix(e):
    if e[0] == "atom":
        return ("A:" + e[1],)
    if e[0] == "const":
        return (f"C:{e[1]}",)
    if e[0] == "un":
        return expr_to_postfix(e[2]) + ("U:" + e[1],)
    return expr_to_postfix(e[1]) + expr_to_postfix(e[2]) + ("B:ADD",)



# ---------------------------------------------------------------------------
# fast encoded representation (carry-free base-256 big-int semantics)
# ---------------------------------------------------------------------------

ENC_OFFSET = 8  # encode(v) = v + 8 in one byte; sums of two encoded bytes
#               stay below 256, so big-int addition is elementwise and
#               carry-free; guard check decodes each byte.


def enc_tuple(tup):
    return int.from_bytes(bytes(v + ENC_OFFSET for v in tup), "big")


def dec_check(encoded, n_rows, guard):
    """Decode; return decoded tuple if every value is within guard else None."""
    raw = encoded.to_bytes(n_rows, "big")
    out = []
    for b in raw:
        v = b - ENC_OFFSET
        if v < -guard or v > guard:
            return None
        out.append(v)
    return tuple(out)


# rebase translate: raw ADD byte sums s = e1+e2 map to standard encoding
# s-OFF when s >= OFF (in-range arithmetic) and to the invalid marker 0xFF
# otherwise; the guard check then rejects any byte outside [OFF-g, OFF+g].
REBASE_T = bytes((s - ENC_OFFSET) if s >= ENC_OFFSET else 0xFF
                 for s in range(256))


def _guard_ok(raw_rebased, guard):
    """All bytes within [OFF-guard, OFF+guard]? (0xFF markers fail)."""
    lo, hi = ENC_OFFSET - guard, ENC_OFFSET + guard
    return all(lo <= b <= hi for b in raw_rebased)


class FastBasis(Basis):
    """Basis with byte-translate tables over the encoded representation."""

    def __init__(self, unary_tier, guard, constants=(-1, 0, 1)):
        super().__init__(unary_tier, guard, constants)
        if 2 * (ENC_OFFSET + guard) >= 256:
            raise ValueError("guard too large for carry-free encoding")
        self.translate = {}
        for name, mapping in self.unaries.items():
            table = bytearray(range(256))
            for v in self.domain:
                table[v + ENC_OFFSET] = mapping[v] + ENC_OFFSET
            self.translate[name] = bytes(table)

    def apply_unary(self, name, encoded, n_rows):
        raw = encoded.to_bytes(n_rows, "big")
        return int.from_bytes(raw.translate(self.translate[name]), "big")

    def add_encoded(self, a, b, n_rows):
        """Elementwise ADD in the encoded domain; returns (encoded, ok)."""
        raw = (a + b).to_bytes(n_rows, "big")   # carry-free (byte sums < 256)
        reb = raw.translate(REBASE_T)
        if not _guard_ok(reb, self.guard):
            return None, False
        return int.from_bytes(reb, "big"), True


# ---------------------------------------------------------------------------
# PROC1: semantic cost-layered DP
# ---------------------------------------------------------------------------

def _apply_un(name, mapping, sem):
    try:
        return tuple(mapping[v] for v in sem)
    except KeyError:
        return None


def _add_sem(a, b, guard):
    s = tuple(x + y for x, y in zip(a, b))
    if any(v < -guard or v > guard for v in s):
        return None
    return s


def semantic_cost_layered_dp(atom_semantics, basis, targets,
                             layer_cap=LAYER_CAP_DEFAULT, return_known=False):
    """atom_semantics: dict atom-name -> row tuple. targets: list of row tuples.

    Returns dict: {"targets": [per-target result], "layers": counts,
    "saturated": bool, "cap_bound": bool}. Semantics are deduplicated
    globally; min-cost representative kept per semantics. With return_known,
    also returns {"semantics": list(t), "cost": c, "expr": e} for every
    discovered semantics (used by the M_STATE pairing search).
    """
    guard = basis.guard
    layer0 = {}
    for name, sem in sorted(atom_semantics.items()):
        if sem not in layer0:
            layer0[sem] = ("atom", name)
    for v in basis.constants:
        sem = (v,) * len(next(iter(atom_semantics.values())))
        if sem not in layer0:
            layer0[sem] = ("const", v)
    layers = [len(layer0)]
    prev = dict(layer0)
    all_known = {sem: (0, e) for sem, e in layer0.items()}
    found = {t: None for t in targets}
    for cost in range(1, layer_cap + 1):
        cand = {}
        # unary closures over all previously known semantics (guarded)
        for sem, (c0, _) in all_known.items():
            if c0 != cost - 1:
                continue  # only NEW semantics of the previous cost layer
            for name in basis.unary_names():
                ns = _apply_un(name, basis.unaries[name], sem)
                if ns is None or any(v < -guard or v > guard for v in ns):
                    continue
                e = expr_canon(("un", name, all_known[sem][1]))
                if ns not in cand or expr_key(e) < expr_key(cand[ns]):
                    cand[ns] = e
        # binary combinations (i, cost-1-i)
        items_prev = list(prev.items())
        for lc in range(0, cost):
            rc = cost - 1 - lc
            lefts = items_prev if lc == cost - 1 else list(
                (s, v) for s, v in all_known.items() if v[0] == lc)
            rights = items_prev if rc == cost - 1 else list(
                (s, v) for s, v in all_known.items() if v[0] == rc)
            for ls, _ in lefts:
                for rs, _ in rights:
                    if expr_key(all_known[ls][1]) > expr_key(all_known[rs][1]):
                        continue
                    ns = _add_sem(ls, rs, guard)
                    if ns is None:
                        continue
                    e = expr_canon(("add", all_known[ls][1], all_known[rs][1]))
                    if ns not in cand or expr_key(e) < expr_key(cand[ns]):
                        cand[ns] = e
        new = {s: e for s, e in cand.items() if s not in all_known}
        for s, e in new.items():
            all_known[s] = (cost, e)
        layers.append(len(new))
        for t in targets:
            if found[t] is None and t in all_known:
                c, e = all_known[t]
                found[t] = {"cost": c, "expr": e, "semantics": list(t)}
        prev = new
        if targets and all(found[t] is not None for t in targets):
            out = {"targets": [found[t] for t in targets], "layers": layers,
                   "saturated": False, "cap_bound": False}
            break
        if not new:
            out = {"targets": [found[t] for t in targets], "layers": layers,
                   "saturated": True, "cap_bound": False}
            break
    else:
        out = {"targets": [found[t] for t in targets], "layers": layers,
               "saturated": False, "cap_bound": True}
    if return_known:
        out["known"] = [{"semantics": list(s), "cost": c, "expr": e}
                        for s, (c, e) in sorted(all_known.items(),
                                                key=lambda kv: (kv[1][0], repr(kv[1][1])))]
    return out


# ---------------------------------------------------------------------------
# PROC2: uniform-cost best-first search (heap, closed-on-pop, postfix)
# ---------------------------------------------------------------------------

def _sem_of_postfix(tokens, atom_semantics, basis):
    stack = []
    guard = basis.guard
    for t in tokens:
        if t.startswith("A:"):
            stack.append(atom_semantics[t[2:]])
        elif t.startswith("C:"):
            stack.append((int(t[2:]),) * len(next(iter(atom_semantics.values()))))
        elif t.startswith("U:"):
            sem = stack.pop()
            try:
                stack.append(tuple(basis.unaries[t[2:]][v] for v in sem))
            except KeyError:
                return None
        elif t == "B:ADD":
            b, a = stack.pop(), stack.pop()
            s = tuple(x + y for x, y in zip(a, b))
            if any(v < -guard or v > guard for v in s):
                return None
            stack.append(s)
        else:
            raise ValueError(t)
    return stack[0] if len(stack) == 1 else None


def postfix_to_expr(tokens):
    stack = []
    for t in tokens:
        if t.startswith("A:"):
            stack.append(("atom", t[2:]))
        elif t.startswith("C:"):
            stack.append(("const", int(t[2:])))
        elif t.startswith("U:"):
            stack.append(("un", t[2:], stack.pop()))
        elif t == "B:ADD":
            b, a = stack.pop(), stack.pop()
            stack.append(("add", a, b))
        else:
            raise ValueError(t)
    return stack[0]


def uniform_cost_best_first(atom_semantics, basis, target, node_cap=4_000_000):
    """Best-first uniform-cost expansion; returns min-cost postfix for target
    (or None under node_cap). Independent mechanics from PROC1."""
    guard = basis.guard
    n_rows = len(next(iter(atom_semantics.values())))
    start = {}
    for name, sem in sorted(atom_semantics.items()):
        start.setdefault(sem, ("A:" + name,))
    for v in basis.constants:
        start.setdefault((v,) * n_rows, (f"C:{v}",))
    target_t = tuple(target)
    if target_t in start:
        return {"cost": 0, "postfix": list(start[target_t])}
    # cost = number of operator tokens
    def op_cost(tok):
        return sum(1 for x in tok if x.startswith("U:") or x == "B:ADD")
    heap = []
    counter = 0
    closed = {}
    for sem, tok in start.items():
        heapq.heappush(heap, (op_cost(tok), counter, sem, tok))
        counter += 1
    expanded = 0
    while heap:
        cost, _, sem, tok = heapq.heappop(heap)
        if sem in closed:
            continue
        closed[sem] = tok
        expanded += 1
        if expanded > node_cap:
            return {"cost": None, "postfix": None, "expanded": expanded,
                    "node_capped": True}
        if sem == target_t:
            return {"cost": cost, "postfix": list(tok), "expanded": expanded,
                    "node_capped": False}
        for name in basis.unary_names():
            ns = _apply_un(name, basis.unaries[name], sem)
            if ns is None or any(v < -guard or v > guard for v in ns) or ns in closed:
                continue
            nt = tok + ("U:" + name,)
            heapq.heappush(heap, (cost + 1, counter, ns, nt))
            counter += 1
        for osem, otok in closed.items():
            ns = _add_sem(sem, osem, guard)
            if ns is None or ns in closed:
                continue
            nt = tok + otok + ("B:ADD",)
            heapq.heappush(heap, (cost + op_cost(otok) + 1, counter, ns, nt))
            counter += 1
    return {"cost": None, "postfix": None, "expanded": expanded,
            "node_capped": False}


# ---------------------------------------------------------------------------
# battery loading helpers
# ---------------------------------------------------------------------------

def load_battery(here: Path):
    return json.loads((here / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())


def rows_to_atom_semantics(rows, atom_names):
    return {name: tuple(r[i] for r in rows)
            for i, name in enumerate(atom_names)}


def jsonable(x):
    if isinstance(x, tuple):
        return [jsonable(y) for y in x]
    if isinstance(x, list):
        return [jsonable(y) for y in x]
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    return x


def semantic_cost_layered_dp_fast(atom_semantics, basis, targets,
                                  layer_cap=LAYER_CAP_DEFAULT,
                                  return_known=False,
                                  width_cap=WIDTH_CAP_DEFAULT):
    """Encoded-domain twin of semantic_cost_layered_dp: identical search
    space, order, and representative rule; byte-translate unaries and
    carry-free big-int elementwise addition. Verified equivalent on the
    small batteries by check_v2."""
    guard = basis.guard
    n_rows = len(next(iter(atom_semantics.values())))
    # per-byte rebase constant: subtracting it from an ADD result (bytes
    # v1+v2+16 >= 16) is borrow-free and renormalizes to v+8 encoding
    rebase = int.from_bytes(bytes([ENC_OFFSET]) * n_rows, "big")
    layer0 = {}
    for name, sem in sorted(atom_semantics.items()):
        enc = enc_tuple(sem)
        if enc not in layer0:
            layer0[enc] = ("atom", name)
    for v in basis.constants:
        enc = enc_tuple((v,) * n_rows)
        if enc not in layer0:
            layer0[enc] = ("const", v)
    layers = [len(layer0)]
    all_known = {enc: (0, e) for enc, e in layer0.items()}
    prev = dict(layer0)
    target_enc = [enc_tuple(tuple(t)) for t in targets]
    found = {te: None for te in target_enc}
    for cost in range(1, layer_cap + 1):
        cand = {}
        get = cand.get
        for enc, (c0, e0) in all_known.items():
            if c0 != cost - 1:
                continue
            for name in basis.unary_names():
                ns = basis.apply_unary(name, enc, n_rows)
                e = ("un", name, e0)
                old = get(ns)
                if old is None or repr(e) < repr(old):
                    cand[ns] = e
        items_prev = list(prev.items())
        for lc in range(0, cost):
            rc = cost - 1 - lc
            if lc == cost - 1:
                lefts = items_prev
            else:
                lefts = [(s, v) for s, v in all_known.items() if v[0] == lc]
            if rc == cost - 1:
                rights = items_prev
            else:
                rights = [(s, v) for s, v in all_known.items() if v[0] == rc]
            for ls, _ in lefts:
                es = all_known[ls][1]
                ks = repr(es)
                lenc = ls
                for rs, _ in rights:
                    if ks > repr(all_known[rs][1]):
                        continue
                    ns, ok = basis.add_encoded(lenc, rs, n_rows)
                    if not ok:
                        continue
                    e = ("add", es, all_known[rs][1])
                    old = get(ns)
                    if old is None or repr(e) < repr(old):
                        cand[ns] = e
        # ADD results were guard-filtered inside add_encoded; unary results
        # are in-guard by table construction; keep a defensive decode pass
        newg = {}
        lo, hi = ENC_OFFSET - guard, ENC_OFFSET + guard
        for ns, e in cand.items():
            if ns in all_known:
                continue
            if ns < 0:
                continue
            if all(lo <= b <= hi for b in ns.to_bytes(n_rows, "big")):
                newg[ns] = e
        for ns, e in newg.items():
            all_known[ns] = (cost, e)
        layers.append(len(newg))
        for te in target_enc:
            if found[te] is None and te in all_known:
                c, e = all_known[te]
                found[te] = {"cost": c, "expr": e,
                             "semantics": list(dec_check(te, n_rows, guard))}
        prev = newg
        if target_enc and all(found[te] is not None for te in target_enc):
            out = {"targets": [found[te] for te in target_enc],
                   "layers": layers, "saturated": False, "cap_bound": False,
                   "width_bound": False}
            break
        if not newg:
            out = {"targets": [found[te] for te in target_enc],
                   "layers": layers, "saturated": True, "cap_bound": False,
                   "width_bound": False}
            break
        if len(all_known) > width_cap:
            out = {"targets": [found[te] for te in target_enc],
                   "layers": layers, "saturated": False, "cap_bound": False,
                   "width_bound": True}
            break
    else:
        out = {"targets": [found[te] for te in target_enc],
               "layers": layers, "saturated": False, "cap_bound": True,
               "width_bound": False}
    if return_known:
        out["known"] = [{"semantics": list(dec_check(s, n_rows, guard)),
                         "cost": c, "expr": e}
                        for s, (c, e) in sorted(all_known.items(),
                                                key=lambda kv: (kv[1][0], repr(kv[1][1])))]
    return out
