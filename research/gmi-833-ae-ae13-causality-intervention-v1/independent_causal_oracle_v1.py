#!/usr/bin/env python3
"""GMI #833 AE13 -- route B.  Materially independent oracle.

Imports NOTHING from route A.  Every quantity is rebuilt by a different method:

  * DAGs are enumerated over topological orders and edge subsets, not over all
    directed-edge masks with an acyclicity peel;
  * observational equivalence classes are decided by comparing the full set of
    d-separation statements each DAG implies -- the CI-set characterisation --
    NOT by comparing skeletons and v-structures;
  * interventional distributions are obtained by PARENT ADJUSTMENT,
    p(y | do(v)) = sum_z p(y | v, z) p(z) over z = the parents of v, applied to
    the observational joint, NOT by truncating the factorisation;
  * the joint itself is built by forward accumulation over a topological order
    using exact Fractions, not by an integer-numerator product table.

    python3 -I -B independent_causal_oracle_v1.py
"""

from fractions import Fraction as F
import itertools
import json
import sys

NV = 3
NAMES = ("A", "B", "C")
GRID = (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))
ATOMS = tuple(itertools.product((0, 1), repeat=NV))


# ------------------------------------------------------------------- dags ---

def dags_by_topological_order():
    """For each permutation, every subset of the backward-closed edge set."""
    out = set()
    for order in itertools.permutations(range(NV)):
        pos = dict((v, i) for i, v in enumerate(order))
        allowed = [(u, v) for u in range(NV) for v in range(NV)
                   if u != v and pos[u] < pos[v]]
        for r in range(len(allowed) + 1):
            for sub in itertools.combinations(allowed, r):
                par = [[] for _ in range(NV)]
                for (u, v) in sub:
                    par[v].append(u)
                out.add(tuple(tuple(sorted(p)) for p in par))
    return sorted(out)


DAGS = dags_by_topological_order()


def children(dag):
    ch = [[] for _ in range(NV)]
    for v, ps in enumerate(dag):
        for p in ps:
            ch[p].append(v)
    return ch


def d_separated(dag, x, y, Z):
    """Reachability form of d-separation (Shachter's Bayes-ball, explicit)."""
    ch = children(dag)
    # states: (node, direction) with direction 0 = arrived from a parent
    # (travelling down), 1 = arrived from a child (travelling up)
    seen = set()
    stack = [(x, 1)]
    while stack:
        node, d = stack.pop()
        if (node, d) in seen:
            continue
        seen.add((node, d))
        if node == y:
            return False
        if d == 1:                       # coming from a child
            if node not in Z:
                for p in dag[node]:
                    stack.append((p, 1))
                for c in ch[node]:
                    stack.append((c, 0))
        else:                            # coming from a parent
            if node in Z:
                for p in dag[node]:
                    stack.append((p, 1))
            else:
                for c in ch[node]:
                    stack.append((c, 0))
    return True


def ci_signature(dag):
    """Every (x, y, Z) with x < y and Z a subset of the rest, d-separated."""
    sig = []
    for x in range(NV):
        for y in range(x + 1, NV):
            rest = [v for v in range(NV) if v not in (x, y)]
            for r in range(len(rest) + 1):
                for Z in itertools.combinations(rest, r):
                    if d_separated(dag, x, y, set(Z)):
                        sig.append((x, y, tuple(sorted(Z))))
    return tuple(sorted(sig))


def equivalence_classes():
    cls = {}
    for i, d in enumerate(DAGS):
        cls.setdefault(ci_signature(d), []).append(i)
    return sorted(cls.values())


# ------------------------------------------------------- joints and do() ----

def slots(dag):
    out = []
    for v, ps in enumerate(dag):
        for asg in itertools.product((0, 1), repeat=len(ps)):
            out.append((v, asg))
    return out


def joint(dag, sl, theta):
    """Forward accumulation over a topological order, exact Fractions."""
    table = dict((sl[i], theta[i]) for i in range(len(sl)))
    order = []
    done = set()
    while len(order) < NV:
        for v in range(NV):
            if v not in done and all(p in done for p in dag[v]):
                order.append(v)
                done.add(v)
                break
    out = {}
    for x in ATOMS:
        p = F(1)
        for v in order:
            q = table[(v, tuple(x[u] for u in dag[v]))]
            p *= q if x[v] == 1 else (F(1) - q)
        out[x] = p
    return out


def marg(j, cond):
    return sum(p for x, p in j.items() if all(x[k] == v for k, v in cond))


def do_by_adjustment(dag, j, var, val, target, tval):
    """p(target=tval | do(var=val)) = sum_z p(target|var,z) p(z), z = pa(var).

    Pearl's parent-adjustment formula, evaluated on the OBSERVATIONAL joint.
    Terms whose conditioning event has zero mass are declared, not dropped.
    """
    pa = dag[var]
    total = F(0)
    undefined = False
    for zv in itertools.product((0, 1), repeat=len(pa)):
        cond_z = list(zip(pa, zv))
        pz = marg(j, cond_z)
        if pz == 0:
            continue
        den = marg(j, cond_z + [(var, val)])
        if den == 0:
            undefined = True
            continue
        num = marg(j, cond_z + [(var, val), (target, tval)])
        total += pz * (num / den)
    return total, undefined


def ace(dag, j, cause, effect):
    hi, u1 = do_by_adjustment(dag, j, cause, 1, effect, 1)
    lo, u0 = do_by_adjustment(dag, j, cause, 0, effect, 1)
    return hi - lo, (u1 or u0)


QUERIES = (("ACE_A_on_B", 0, 1), ("ACE_A_on_C", 0, 2), ("ACE_B_on_C", 1, 2),
           ("ACE_C_on_A", 2, 0))


# -------------------------------------------------------------------- run ---

def main():
    classes = equivalence_classes()
    sizes = sorted(len(c) for c in classes)

    # the named two-DAG class: A -> C against C -> A, B isolated
    dag_ac = (tuple(), tuple(), (0,))
    dag_ca = ((2,), tuple(), tuple())
    sl_ac, sl_ca = slots(dag_ac), slots(dag_ca)
    th_ac = []
    for (v, asg) in sl_ac:
        if v in (0, 1):
            th_ac.append(F(1, 2))
        else:
            th_ac.append(F(3, 4) if asg == (1,) else F(1, 4))
    th_ac = tuple(th_ac)
    j_ac = joint(dag_ac, sl_ac, th_ac)
    q_ac = tuple(ace(dag_ac, j_ac, c, e)[0] for _, c, e in QUERIES)

    members = []
    for th in itertools.product(GRID, repeat=len(sl_ca)):
        j = joint(dag_ca, sl_ca, th)
        if all(j[x] == j_ac[x] for x in ATOMS):
            members.append(tuple(ace(dag_ca, j, c, e)[0] for _, c, e in QUERIES))

    q_all = [q_ac] + members
    lo = [min(q[i] for q in q_all) for i in range(len(QUERIES))]
    hi = [max(q[i] for q in q_all) for i in range(len(QUERIES))]

    # CI-5: predictive versus causal/control state on B -> A, B -> C, A -> C
    dag5 = ((1,), tuple(), (0, 1))
    sl5 = slots(dag5)
    counts = {"EQUAL": 0, "PREDICTIVE_STRICTLY_REFINES": 0,
              "CAUSAL_STRICTLY_REFINES": 0, "INCOMPARABLE": 0}
    excluded = 0
    for th in itertools.product(GRID, repeat=len(sl5)):
        j = joint(dag5, sl5, th)
        if any(j[x] == 0 for x in ATOMS):
            excluded += 1
            continue
        cells = [(a, b) for a in (0, 1) for b in (0, 1)]
        pred = {}
        caus = {}
        for (a, b) in cells:
            # p(C=1|A=a,B=b) straight off the joint -- not off a CPT slot
            pred[(a, b)] = (marg(j, [(0, a), (1, b), (2, 1)])
                            / marg(j, [(0, a), (1, b)]))
            caus[(a, b)] = (marg(j, [(0, 0), (1, b), (2, 1)])
                            / marg(j, [(0, 0), (1, b)]),
                            marg(j, [(0, 1), (1, b), (2, 1)])
                            / marg(j, [(0, 1), (1, b)]))
        pp = part(cells, pred)
        cp = part(cells, caus)
        r1, r2 = refines(pp, cp), refines(cp, pp)
        counts["EQUAL" if (r1 and r2) else
               "PREDICTIVE_STRICTLY_REFINES" if r1 else
               "CAUSAL_STRICTLY_REFINES" if r2 else "INCOMPARABLE"] += 1

    # the observational-read-off hostile, recomputed independently
    pa1c1 = marg(j_ac, [(2, 1), (0, 1)]) / marg(j_ac, [(2, 1)])
    pa1c0 = marg(j_ac, [(2, 0), (0, 1)]) / marg(j_ac, [(2, 0)])

    out = {
        "schema": "GMI_833_AE13_INDEPENDENT_ORACLE_V1",
        "route": "B",
        "method": ("topological-order DAG enumeration; equivalence by "
                   "d-separation CI signatures; interventions by parent "
                   "adjustment on the observational joint; joints by forward "
                   "Fraction accumulation"),
        "labelled_dags": len(DAGS),
        "equivalence_classes": len(classes),
        "class_size_multiset": sizes,
        "classes_with_more_than_one_dag": sum(1 for c in classes if len(c) > 1),
        "singleton_classes": sum(1 for c in classes if len(c) == 1),
        "CI_2": {
            "fixed_observational_joint": [str(j_ac[x]) for x in ATOMS],
            "joint_sums_to_one": sum(j_ac.values()) == 1,
            "members_of_the_other_dag_reproducing_it": len(members),
            "answer_from_A_to_C": [str(x) for x in q_ac],
            "answer_from_C_to_A": [[str(x) for x in m] for m in members],
            "identification_interval_low": [str(x) for x in lo],
            "identification_interval_high": [str(x) for x in hi],
            "interventional_answers_differ": any(lo[i] != hi[i]
                                                 for i in range(len(QUERIES))),
        },
        "CI_5": {"relation_counts": counts, "excluded_non_positive": excluded},
        "H1_check": {
            "true_ACE_C_on_A": str(q_ac[3]),
            "observational_contrast": str(pa1c1 - pa1c0),
        },
    }
    sys.stdout.write(json.dumps(out, indent=2) + "\n")
    return 0


def part(cells, valmap):
    g = {}
    for c in cells:
        g.setdefault(valmap[c], []).append(c)
    return tuple(sorted(tuple(sorted(v)) for v in g.values()))


def refines(fine, coarse):
    for blk in fine:
        if not any(set(blk) <= set(cb) for cb in coarse):
            return False
    return True


if __name__ == "__main__":
    sys.exit(main())
