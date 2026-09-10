"""D26 domain adapters — the domain-specific half of the operator contract.

Each adapter supplies primitives for the four abstract drivers in
oracle/d26_operators.py.  The drivers are never edited per domain; if a
contract obligation fails here it is a property of the domain, which is the
result the test exists to produce.

Every world generator and every semantic primitive is imported from the FROZEN
labs on main (exact/worlds.py, exact/d20.py, exact/d21_reduction_equality.py).
Nothing about their semantics is re-implemented.

  D_SEM  OW2   states / actions / declared safe sets
  D_ABS  OW5S  finite transition systems + block abstractions
  D_ALG  OW6   expression ASTs over {2,3,5,x,+,*} with sound rewrites
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class NotSupported(Exception):
    """This domain cannot host this operator. Distinct from a contract failure."""


class _Base:
    domain = "?"
    NotSupported = NotSupported

    def wid(self, w: Any) -> str:
        return w.get("id", "?")


# ------------------------------------------------------------------- D_SEM

class SemAdapter(_Base):
    """OW2 — ambiguity and safe-action sets."""
    domain = "D_SEM"

    def worlds(self) -> List[Any]:
        from exact.worlds import ow2_worlds
        return ow2_worlds()

    # --- DISTINGUISH: hidden truth = which state we are in
    def hypotheses(self, w):
        return list(w["states"])

    def truth(self, w):
        return w["states"][0]

    def best_observation(self, w, H):
        if len(H) < 2:
            return None
        best = None
        for a in w["actions"]:
            yes = [s for s in H if a in w["safe"][s]]
            if 0 < len(yes) < len(H):
                bal = min(len(yes), len(H) - len(yes))
                if best is None or bal > best[0]:
                    best = (bal, a)
        return None if best is None else best[1]

    def no_distinguisher_certificate(self, w, H):
        if len(H) < 2:
            return True
        return all(not (0 < len([s for s in H if a in w["safe"][s]]) < len(H))
                   for a in w["actions"])

    def filter(self, w, H, obs):
        ans = obs in w["safe"][self.truth(w)]
        return [s for s in H if (obs in w["safe"][s]) == ans]

    def render(self, obs):
        return "safe?(%s)" % obs

    # --- REFINE: abstraction = partition of states by agreement on a probe set
    def initial_abstraction(self, w):
        return {"probes": [], "blocks": [sorted(w["states"])]}

    def _blocks(self, w, probes):
        buckets: Dict[Tuple[bool, ...], List[str]] = {}
        for s in sorted(w["states"]):
            k = tuple(a in w["safe"][s] for a in probes)
            buckets.setdefault(k, []).append(s)
        return [sorted(v) for _, v in sorted(buckets.items())]

    def spurious_counterexample(self, w, A):
        """Two states merged by A that some unprobed action separates."""
        for b in A["blocks"]:
            for i, s in enumerate(b):
                for t in b[i + 1:]:
                    for a in w["actions"]:
                        if (a in w["safe"][s]) != (a in w["safe"][t]):
                            return (s, t, a)
        return None

    def refine(self, w, A, cex):
        _, _, a = cex
        probes = list(A["probes"]) + [a]
        return {"probes": probes, "blocks": self._blocks(w, probes)}

    def admits(self, w, A, cex):
        s, t, _ = cex
        return any(s in b and t in b for b in A["blocks"])

    def sound_over_approx(self, w, A):
        """States with identical safe-sets are never separated: the partition
        only ever over-approximates true behavioural equality."""
        for b1 in A["blocks"]:
            for b2 in A["blocks"]:
                if b1 is b2:
                    continue
                for s in b1:
                    for t in b2:
                        if w["safe"][s] == w["safe"][t]:
                            return False
        return True

    def abstraction_size(self, A):
        return len(A["blocks"])

    # --- REDUCE: "safe in every possible state" -> membership in the intersection
    def problem(self, w):
        H = self.hypotheses(w)
        return {"H": H, "actions": list(w["actions"])}

    def reduce(self, w, p):
        inter = None
        for s in p["H"]:
            ss = set(w["safe"][s])
            inter = ss if inter is None else (inter & ss)
        return {"intersection": sorted(inter or [])}, (lambda sol: sol)

    def solve(self, w, p2):
        return p2["intersection"] or None

    def solvable(self, w, p):
        return self._universally_safe(w, p) != []

    def _universally_safe(self, w, p):
        return sorted([a for a in p["actions"]
                       if all(a in w["safe"][s] for s in p["H"])])

    def checks(self, w, p, mapped):
        """Every action the reduction returns really is safe everywhere."""
        if not mapped:
            return False
        return all(all(a in w["safe"][s] for s in p["H"]) for a in mapped)

    # --- VERIFY
    def verify_cases(self, w):
        H = self.hypotheses(w)
        return [(a, "safe_everywhere", all(a in w["safe"][s] for s in H))
                for a in w["actions"]]

    def verify(self, w, x, claim):
        bad = [s for s in self.hypotheses(w) if x not in w["safe"][s]]
        return ("REJECT", {"state": bad[0], "action": x}) if bad else ("ACCEPT", None)

    def check_witness(self, w, x, claim, witness):
        s = witness.get("state")
        return s in w["safe"] and x not in w["safe"][s]


# ------------------------------------------------------------------- D_ABS

class AbsAdapter(_Base):
    """OW5S — finite transition systems with block abstractions (D20's lab)."""
    domain = "D_ABS"

    def worlds(self) -> List[Any]:
        from exact.worlds_d19d20 import ow5s_worlds
        return [w for w in ow5s_worlds() if not w.get("degenerate")]

    def _ctr(self):
        from exact import d20
        return d20._new_counters()

    # --- DISTINGUISH: hidden truth = which concrete state we occupy inside a block
    def hypotheses(self, w):
        from exact import d20
        blocks = [list(b) for b in w["start_blocks"]]
        ctr = self._ctr()
        blk_of, _ = d20.build_abstraction(w, blocks, ctr)
        b0 = blk_of[w["init"]]
        return sorted([s for s in w["states"] if blk_of[s] == b0])

    def truth(self, w):
        return w["init"]

    def _succ_blocks(self, w, s):
        from exact import d20
        blocks = [list(b) for b in w["start_blocks"]]
        blk_of, _ = d20.build_abstraction(w, blocks, self._ctr())
        return set(blk_of[t] for t in w["trans"][s])

    def best_observation(self, w, H):
        """A target block whose reachability-in-one-step splits H."""
        if len(H) < 2:
            return None
        succ = {s: self._succ_blocks(w, s) for s in H}
        cands = sorted(set().union(*succ.values())) if succ else []
        for j in cands:
            yes = [s for s in H if j in succ[s]]
            if 0 < len(yes) < len(H):
                return j
        return None

    def no_distinguisher_certificate(self, w, H):
        if len(H) < 2:
            return True
        return self.best_observation(w, H) is None

    def filter(self, w, H, obs):
        ans = obs in self._succ_blocks(w, self.truth(w))
        return [s for s in H if (obs in self._succ_blocks(w, s)) == ans]

    def render(self, obs):
        return "step_to_block?(%s)" % obs

    # --- REFINE: CEGAR predicate split (D20's own primitives)
    def initial_abstraction(self, w):
        from exact import d20
        return d20._canon([list(b) for b in w["start_blocks"]])

    def _abs_path(self, w, A):
        from exact import d20
        ctr = self._ctr()
        blk_of, at = d20.build_abstraction(w, A, ctr)
        verdict, path = d20.abstract_bfs(w, blk_of, at, ctr)
        return verdict, path

    def spurious_counterexample(self, w, A):
        from exact import d20
        verdict, path = self._abs_path(w, A)
        if verdict == "SAFE" or not path:
            return None
        kind, spec = d20.validate(w, A, path, self._ctr())
        if kind == "VALID":
            return None            # a real counterexample, nothing to refine
        return {"path_states": [frozenset(A[i]) for i in path], "spec": spec}

    def refine(self, w, A, cex):
        from exact import d20
        spec = cex.get("spec")
        if spec is None:
            return None
        A1 = d20.apply_split(A, spec)
        return None if A1 == A else A1     # no-progress is DETECTED, not assumed

    def admits(self, w, A, cex):
        """Is the SAME concrete abstract path still derivable? Index-free."""
        verdict, path = self._abs_path(w, A)
        if verdict == "SAFE" or not path:
            return False
        return [frozenset(A[i]) for i in path] == cex["path_states"]

    def sound_over_approx(self, w, A):
        seen: Dict[Any, int] = {}
        for i, b in enumerate(A):
            for s in b:
                if s in seen:
                    return False
                seen[s] = i
        return all(s in seen for s in w["states"])

    def abstraction_size(self, A):
        return len(A)

    # --- REDUCE: concrete reachability -> abstract reachability (sound? tested)
    def problem(self, w):
        return {"w": w["id"]}

    def reduce(self, w, p):
        verdict, path = self._abs_path(w, self.initial_abstraction(w))
        return {"abstract_verdict": verdict}, (lambda sol: sol)

    def solve(self, w, p2):
        return "UNSAFE" if p2["abstract_verdict"] == "UNSAFE" else None

    def solvable(self, w, p):
        return bool(w["concrete_unsafe"])

    def checks(self, w, p, mapped):
        """The reduction claims UNSAFE; is the system concretely unsafe?

        This is the obligation abstraction famously cannot discharge without
        refinement, and a failure here is the D20 phase boundary showing up as
        a contract violation rather than as a runtime cost.
        """
        return mapped == "UNSAFE" and bool(w["concrete_unsafe"])

    # --- VERIFY
    def verify_cases(self, w):
        truth = bool(w["concrete_unsafe"])
        return [(w["id"], "reachable_bad", truth),
                (w["id"], "not_reachable_bad", not truth)]

    def verify(self, w, x, claim):
        hit = sorted(set(w["concrete_reachable"]) & set(w["bad"]))
        unsafe = bool(hit)
        want = (claim == "reachable_bad")
        if want == unsafe:
            return "ACCEPT", None
        return "REJECT", {"reachable_bad": hit, "claim": claim}

    def check_witness(self, w, x, claim, witness):
        return set(witness.get("reachable_bad", [])) == (
            set(w["concrete_reachable"]) & set(w["bad"]))


# ------------------------------------------------------------------- D_ALG

# D21's own sem_equal cross-checks an exact evaluation vector against a sympy
# normal form and returns (equal, status). sympy is NOT installed on the LUNARC
# compute nodes and installing it would need a network call from the cluster,
# which is prohibited. The evaluation-vector oracle alone is EXACT here, not an
# approximation: X_DOMAIN has 21 points and two polynomials of degree <= 20
# agreeing on 21 points are identical. The degree bound is therefore ENFORCED
# as a hard gate rather than assumed, and a term over the bound returns
# CANNOT_CHECK, never a guess.
_DEGREE_BOUND = 20


def sem_equal_exact(a, b):
    """(equal, status) with the same shape D21's sem_equal returns."""
    from exact import d21_reduction_equality as d21
    if d21.degree(a) > _DEGREE_BOUND or d21.degree(b) > _DEGREE_BOUND:
        return None, "CANNOT_CHECK_DEGREE_OVER_BOUND"
    return (d21.o1_vector(a) == d21.o1_vector(b)), "CHECKED"


def sem_equal_bool(a, b):
    eq, status = sem_equal_exact(a, b)
    if status != "CHECKED":
        raise NotSupported("sem_equal %s" % status)
    return bool(eq)


class AlgAdapter(_Base):
    """OW6 — expression rewriting and semantic equality (D21's lab)."""
    domain = "D_ALG"

    def worlds(self) -> List[Any]:
        from exact.worlds import ow6_worlds
        return ow6_worlds()

    def _variants(self, w, n=6):
        """One-step sound rewrites of the world expression, the planted unsound
        rewrite, and one CONSTRUCTED unequal term.

        The constructed term matters: sound rewrites are all semantically equal
        to the original, so a hypothesis set built from them alone would never
        exercise the rejection obligations (V2) or produce a genuine REFINE
        counterexample. A test that cannot fail is not a test, so a term that
        is provably unequal is included and its inequality is ASSERTED, not
        assumed -- if the world is degenerate enough that (expr + 2) evaluates
        equal to expr, this domain reports CANNOT_CHECK rather than a pass.
        """
        from exact import d21_reduction_equality as d21
        t = w["expr"]
        outs = [t]
        for _, _, new in d21.one_step_results(t, d21.SOUND_ALL)[:n]:
            outs.append(new)
        for _, _, new in d21.one_step_results(t, d21.UNSOUND)[:2]:
            outs.append(new)
        shifted = ("+", t, "2")
        eq, status = sem_equal_exact(t, shifted)
        if status != "CHECKED":
            raise NotSupported("degree bound: %s" % status)
        if eq:
            raise NotSupported("degenerate world: expr + 2 == expr")
        outs.append(shifted)
        seen, uniq = set(), []
        for u in outs:
            k = repr(u)
            if k not in seen:
                seen.add(k)
                uniq.append(u)
        return uniq

    # --- DISTINGUISH: hidden truth = which candidate expression equals w.expr
    def hypotheses(self, w):
        return self._variants(w)

    def truth(self, w):
        return w["expr"]

    def best_observation(self, w, H):
        from exact import d21_reduction_equality as d21
        if len(H) < 2:
            return None
        for x in d21.X_DOMAIN:
            vals = {d21.d21_eval(h, x) for h in H}
            if len(vals) > 1:
                return x
        return None

    def no_distinguisher_certificate(self, w, H):
        from exact import d21_reduction_equality as d21
        if len(H) < 2:
            return True
        return all(len({d21.d21_eval(h, x) for h in H}) == 1
                   for x in d21.X_DOMAIN)

    def filter(self, w, H, obs):
        from exact import d21_reduction_equality as d21
        want = d21.d21_eval(self.truth(w), obs)
        return [h for h in H if d21.d21_eval(h, obs) == want]

    def render(self, obs):
        return "eval@x=%s" % obs

    # --- REFINE: an equality abstraction refined by a distinguishing point
    def initial_abstraction(self, w):
        return {"points": [], "H": self._variants(w)}

    def _classes(self, w, points, H):
        from exact import d21_reduction_equality as d21
        buckets: Dict[Tuple[Any, ...], List[Any]] = {}
        for h in H:
            k = tuple(d21.d21_eval(h, x) for x in points)
            buckets.setdefault(k, []).append(h)
        return list(buckets.values())

    def spurious_counterexample(self, w, A):
        """Two expressions merged by A that some unused point separates."""
        from exact import d21_reduction_equality as d21
        H = A["H"]
        for cls in self._classes(w, A["points"], H):
            for i, a in enumerate(cls):
                for b in cls[i + 1:]:
                    for x in d21.X_DOMAIN:
                        if d21.d21_eval(a, x) != d21.d21_eval(b, x):
                            return {"a": a, "b": b, "x": x}
        return None

    def refine(self, w, A, cex):
        return {"points": list(A["points"]) + [cex["x"]], "H": A["H"]}

    def admits(self, w, A, cex):
        return any(any(u is cex["a"] or u == cex["a"] for u in cls)
                   and any(u is cex["b"] or u == cex["b"] for u in cls)
                   for cls in self._classes(w, A["points"], A["H"]))

    def sound_over_approx(self, w, A):
        """Semantically equal expressions are never separated: point-agreement
        is a coarsening of true equality, never a refinement past it."""
        from exact import d21_reduction_equality as d21
        classes = self._classes(w, A["points"], A["H"])
        for i, c1 in enumerate(classes):
            for c2 in classes[i + 1:]:
                for a in c1:
                    for b in c2:
                        if sem_equal_bool(a, b):
                            return False
        return True

    def abstraction_size(self, A):
        """Number of equality classes the current point set induces."""
        return len(self._classes(None, A["points"], A["H"]))

    # --- REDUCE: "are these equal?" -> "are their normal forms equal?"
    def problem(self, w):
        H = self._variants(w)
        pairs = [(H[0], h) for h in H[1:4]] or [(H[0], H[0])]
        return {"pairs": pairs}

    def reduce(self, w, p):
        """Normal form = the exact evaluation vector over X_DOMAIN.

        For degree <= 20 this is a sound AND complete canonical form, so the
        reduction is expected to discharge both Q1 and Q2 -- unlike D_ABS,
        where the abstraction only over-approximates.
        """
        from exact import d21_reduction_equality as d21
        for a, b in p["pairs"]:
            if d21.degree(a) > _DEGREE_BOUND or d21.degree(b) > _DEGREE_BOUND:
                raise NotSupported("term degree over exact bound")
        red = [(d21.o1_vector(a), d21.o1_vector(b)) for a, b in p["pairs"]]
        return {"normal_pairs": red}, (lambda sol: sol)

    def solve(self, w, p2):
        eq = [i for i, (na, nb) in enumerate(p2["normal_pairs"]) if na == nb]
        return eq or None

    def solvable(self, w, p):
        return bool([i for i, (a, b) in enumerate(p["pairs"])
                     if sem_equal_bool(a, b)])

    def checks(self, w, p, mapped):
        """Every pair the reduction called equal really is semantically equal."""
        if not mapped:
            return False
        return all(sem_equal_bool(*p["pairs"][i]) for i in mapped)

    # --- VERIFY
    def verify_cases(self, w):
        from exact import d21_reduction_equality as d21
        H = self._variants(w)[:4]
        cases = []
        for i, a in enumerate(H):
            for b in H[i:]:
                cases.append(((a, b), "sem_equal", sem_equal_bool(a, b)))
        return cases

    def verify(self, w, x, claim):
        from exact import d21_reduction_equality as d21
        a, b = x
        if sem_equal_bool(a, b):
            return "ACCEPT", None
        for v in d21.X_DOMAIN:
            if d21.d21_eval(a, v) != d21.d21_eval(b, v):
                return "REJECT", {"x": v}
        return "REJECT", None

    def check_witness(self, w, x, claim, witness):
        from exact import d21_reduction_equality as d21
        a, b = x
        v = witness.get("x")
        return v is not None and d21.d21_eval(a, v) != d21.d21_eval(b, v)


ADAPTERS = {"D_SEM": SemAdapter, "D_ABS": AbsAdapter, "D_ALG": AlgAdapter}
