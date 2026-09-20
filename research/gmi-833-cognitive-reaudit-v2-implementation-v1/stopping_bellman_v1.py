"""Exact Bellman-comparison stopping on finite acyclic computation graphs.

Section-M planning re-audit (issue #833 row ``Re-audit planning and
stopping.``; freeze commit cb6d6a59; package
gmi-833-cognitive-reaudit-v2-implementation-v1).

PS-1 (theorem, forall[finite acyclic computation graphs]): on a finite
acyclic computation graph with every cost charged (first-use, storage,
lookup, transport, execution), stopping is optimal at state ``s`` exactly
when the best registered terminal action value ``best(s)`` is at least
every cost-charged continuation value

    cont(s,t) = -c(t) + sum_{c in Ch(t)} P(c) * V*(c)

computed with future optimal computation ``V*(c)`` included.

PS-2 (hostile, forall_fin[registered instance]): a merely myopic one-step
EVC rule -- which substitutes ``best(c)`` for ``V*(c)`` -- is not
generally sufficient.  The registered hostile (X = f1 XOR f2 with f1,f2
iid fair, tests at cost 1/8) has myopic one-step EVC <= 0 at the root
(myopic stops) while a two-step information plan has strictly positive
net value +1/4 (Bellman comparison continues); the k=1 clean variant does
not alarm.

All arithmetic is exact rational.  A state with no registered terminal
action (missing goal/model) and a cyclic unbounded computation graph are
refused, never silently completed.  Optimal ties are returned as sets and
never silently broken.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path
import sys
from typing import Mapping, Sequence

SCOPE_TAG_THEOREM = "forall"      # PS-1 is a universal claim.
SCOPE_TAG_HOSTILE = "forall_fin"  # PS-2 is a finite registered instance.


def exact(value) -> F:
    """Exact rational guard: int or Fraction only, never float/bool."""
    if isinstance(value, bool) or type(value) not in (int, F):
        raise ValueError("exact rational required (floats and booleans refused)")
    return F(value)


@dataclass(frozen=True)
class State:
    """A node of the computation graph.

    ``terminal_actions`` maps registered terminal action labels to their
    exact rational value.  ``tests`` maps test names to ``(exact nonnegative
    cost, ((exact prob, child name), ...))``; child probabilities sum to 1
    and every child appears strictly earlier in the acyclic backward-induction
    order (children are computed before their parents).
    """

    name: str
    terminal_actions: Mapping[str, F]
    tests: Mapping[str, tuple[F, Sequence[tuple[F, str]]]] = field(default_factory=dict)


def _topological_order(graph: "ComputationalGraph") -> tuple[str, ...]:
    """Deterministic DFS topological order, children before parents.

    Uses separate visiting/visited sets so a diamond DAG (a child shared by
    two parents) is NOT mistaken for a cycle; only a genuine back edge raises.
    """
    order: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> bool:
        if name in visiting:
            return False  # back edge -> cyclic
        if name in visited:
            return True
        visiting.add(name)
        for _p, child in graph._states[name].tests.items():
            for _prob, cname in child[1]:
                if not visit(cname):
                    return False
        visiting.discard(name)
        visited.add(name)
        order.append(name)
        return True

    for name in graph._states:
        if not visit(name):
            raise ValueError("cyclic computation graph refused (unbounded computation cannot be silently completed)")
    return tuple(order)


class ComputationalGraph:
    """Finite acyclic computation graph with exact rational arithmetic."""

    def __init__(self, states: Sequence[State]):
        self._states = {s.name: s for s in states}
        if not self._states:
            raise ValueError("empty computation graph")
        # Refuse cyclic / unbounded graphs rather than silently completing.
        self._topo = _topological_order(self)
        if len(self._topo) != len(self._states):
            raise ValueError("cyclic computation graph refused")
        self._index = {name: i for i, name in enumerate(self._topo)}
        for s in self._states.values():
            if not s.terminal_actions:
                raise ValueError("missing goal/model: state %s has no registered terminal action" % s.name)
            for t, (cost, children) in s.tests.items():
                cost = exact(cost)
                if cost < 0:
                    raise ValueError("negative test cost refused: %s/%s" % (s.name, t))
                prob_sum = F(0)
                for p, cname in children:
                    p = exact(p)
                    if p < 0:
                        raise ValueError("negative transition probability refused")
                    prob_sum += p
                    if cname not in self._states:
                        raise ValueError("unknown child state %s" % cname)
                    if self._index[cname] >= self._index[s.name]:
                        raise ValueError("non-acyclic edge %s -> %s refused" % (s.name, cname))
                if prob_sum != 1:
                    raise ValueError("test %s at %s: probabilities must sum to 1" % (t, s.name))
        self._value_memo: dict[str, F] | None = None

    def names(self) -> tuple[str, ...]:
        return tuple(s.name for s in self._states.values())

    def best(self, s: str) -> F:
        """Best registered terminal action value at s (exact)."""
        return max(exact(v) for v in self._states[s].terminal_actions.values())

    def best_set(self, s: str) -> tuple[str, ...]:
        """All registered terminal actions attaining best(s) -- ties remain sets."""
        values = {a: exact(v) for a, v in self._states[s].terminal_actions.items()}
        top = max(values.values())
        return tuple(sorted(a for a, v in values.items() if v == top))

    def test_cost(self, s: str, t: str) -> F:
        return exact(self._states[s].tests[t][0])

    def myopic_evc(self, s: str, t: str) -> F:
        """One-step expected value of computation: best after one test vs now.

        This is the myopic rule: it evaluates the immediate children by
        ``best(c)`` and stops if the result is <= 0.  PS-2 shows it is not
        generally sufficient.
        """
        cost, children = self._states[s].tests[t]
        return (-exact(cost) + sum(exact(p) * self.best(cname) for p, cname in children)
                - self.best(s))

    def cont(self, s: str, t: str) -> F:
        """Cost-charged continuation value with future optimal computation included."""
        if self._value_memo is None:
            self._compute_all()
        cost, children = self._states[s].tests[t]
        return -exact(cost) + sum(exact(p) * self._value_memo[cname] for p, cname in children)

    def _compute_all(self) -> None:
        """Backward induction over the acyclic order (children first, exact)."""
        memo: dict[str, F] = {}
        # Children appear strictly earlier in self._topo, so forward iteration
        # computes every child's optimal value before its parents.
        for name in self._topo:
            st = self._states[name]
            conts = []
            for t in st.tests:
                cost, children = st.tests[t]
                conts.append(-exact(cost) + sum(exact(p) * memo[cname] for p, cname in children))
            memo[name] = max([self.best(name)] + conts)
        self._value_memo = memo

    def value(self, s: str) -> F:
        """Backward-induction optimal value V*(s) over the DAG (exact)."""
        if self._value_memo is None:
            self._compute_all()
        return self._value_memo[s]

    def stop_is_optimal(self, s: str) -> bool:
        """Bellman comparison: stop iff best(s) >= every continuation value."""
        conts = [self.cont(s, t) for t in self._states[s].tests]
        return self.best(s) >= max(conts, default=self.best(s))

    def optimal_choice_set(self, s: str) -> tuple[str, ...]:
        """All optimal options at s: 'stop' and/or test names. Ties remain sets."""
        best = self.best(s)
        choices = []
        if self.stop_is_optimal(s):
            choices.append("stop")
        for t in sorted(self._states[s].tests):
            if self.cont(s, t) >= best:
                choices.append(t)
        return tuple(choices)


def _xor_terminal(px: Mapping[str, F], name: str) -> dict[str, F]:
    one = F(1)
    p = px[name]
    return {"a0": one - p, "a1": p}


def xor_graph(k) -> ComputationalGraph:
    """X = f1 XOR f2, f1,f2 iid fair bits; tests t1/t2 observe f1/f2 at cost k."""
    k = exact(k)
    half = F(1, 2)
    one = F(1)
    px = {
        "root": half, "f1=0": half, "f1=1": half, "f2=0": half, "f2=1": half,
        "00": F(0), "01": one, "10": one, "11": F(0),
    }
    return ComputationalGraph([
        State("root", _xor_terminal(px, "root"), {
            "t1": (k, ((half, "f1=0"), (half, "f1=1"))),
            "t2": (k, ((half, "f2=0"), (half, "f2=1"))),
        }),
        State("f1=0", _xor_terminal(px, "f1=0"), {"t2": (k, ((half, "00"), (half, "01")))}),
        State("f1=1", _xor_terminal(px, "f1=1"), {"t2": (k, ((half, "10"), (half, "11")))}),
        State("f2=0", _xor_terminal(px, "f2=0"), {"t1": (k, ((half, "00"), (half, "10")))}),
        State("f2=1", _xor_terminal(px, "f2=1"), {"t1": (k, ((half, "01"), (half, "11")))}),
        State("00", _xor_terminal(px, "00")),
        State("01", _xor_terminal(px, "01")),
        State("10", _xor_terminal(px, "10")),
        State("11", _xor_terminal(px, "11")),
    ])


def hostile_report(k) -> dict:
    """Exact numbers for the two-step information hostile (or clean variant).

    k = 1/8: myopic one-step EVC stops (<= 0) while the Bellman comparison
    continues: cont(root,t) = 3/4 > best(root) = 1/2, V*(root) = 3/4, and
    the two-step information plan has strictly positive net value +1/4.
    k = 1: stopping is optimal (no alarm); myopic EVC <= 0 agrees.
    """
    g = xor_graph(k)
    root = "root"
    evc1 = g.myopic_evc(root, "t1")
    evc2 = g.myopic_evc(root, "t2")
    cont1 = g.cont(root, "t1")
    cont2 = g.cont(root, "t2")
    best = g.best(root)
    vstar = g.value(root)
    return {
        "k": str(exact(k)),
        "best_root": str(best),
        "myopic_evc_t1": str(evc1),
        "myopic_evc_t2": str(evc2),
        "myopic_stops": bool(evc1 <= 0 and evc2 <= 0),
        "bellman_continuation_t1": str(cont1),
        "bellman_continuation_t2": str(cont2),
        "bellman_continues": bool(cont1 > best or cont2 > best),
        "optimal_value_vstar_root": str(vstar),
        "two_step_plan_net_value": str(vstar - best),
        "stop_is_optimal": bool(g.stop_is_optimal(root)),
        "policy_search_optimal_value": str(optimal_value_by_policy_search(g, root)),
    }


def optimal_value_by_policy_search(g: ComputationalGraph, root: str) -> F:
    """Independent oracle: enumerate every policy, propagate its exact value.

    A policy chooses, at each reachable state, either to stop or which test
    to run.  Because the graph is a DAG the policy value is well defined by
    backward propagation; the optimum over ALL policies must equal V*(root)
    computed by the Bellman comparison.  This is a genuinely different code
    path from ``value``.
    """
    from itertools import product

    def policy_value(policy) -> F:
        memo: dict[str, F] = {}
        for name in g._topo:  # children first, same acyclic order
            choice = policy[name]
            if choice == "stop":
                memo[name] = g.best(name)
            else:
                cost, children = g._states[name].tests[choice]
                memo[name] = -exact(cost) + sum(exact(p) * memo[c] for p, c in children)
        return memo[root]

    options: dict[str, tuple[str, ...]] = {}
    for name in g._states:
        choices = ["stop"] + sorted(g._states[name].tests)
        options[name] = tuple(choices)
    best_val = None
    for combo in product(*[options[n] for n in g._states]):
        policy = dict(zip(g._states, combo))
        val = policy_value(policy)
        if best_val is None or val > best_val:
            best_val = val
    return best_val


def policy_count(g: ComputationalGraph) -> int:
    """Number of distinct policies: product over states of (stop | tests)."""
    total = 1
    for name in g._states:
        total *= 1 + len(g._states[name].tests)
    return total


def tie_control() -> dict:
    """Tie-preserving control: at k = 1/4 stop and both tests tie at best.

    The optimal choice set at the root is {stop, t1, t2} (size 3) and the
    best terminal-action set is {a0, a1} (size 2) -- ties remain sets and
    are never silently broken.
    """
    g = xor_graph(F(1, 4))
    root = "root"
    return {
        "k": "1/4",
        "best_root": str(g.best(root)),
        "optimal_choice_set": list(g.optimal_choice_set(root)),
        "optimal_choice_set_size": len(g.optimal_choice_set(root)),
        "best_terminal_action_set": list(g.best_set(root)),
        "best_terminal_action_set_size": len(g.best_set(root)),
        "stop_is_optimal": bool(g.stop_is_optimal(root)),
        "value_equals_best": str(g.value(root)) == str(g.best(root)),
    }


def refusal_controls() -> dict:
    """Missing goal/model and cyclic graphs are refused, never completed."""
    refused_missing_goal = False
    try:
        ComputationalGraph([State("s", {})])
    except ValueError:
        refused_missing_goal = True
    refused_cycle = False
    try:
        # self-loop makes the graph cyclic
        ComputationalGraph([
            State("a", {"act": F(1)}, {"t": (F(0), ((F(1), "a"),))}),
        ])
    except ValueError:
        refused_cycle = True
    return {
        "missing_goal_model_refused": refused_missing_goal,
        "cyclic_unbounded_graph_refused": refused_cycle,
    }


def planning_row_report() -> dict:
    """The planning row: Bellman theorem checks + hostile + clean + ties."""
    hostile = hostile_report(F(1, 8))
    clean = hostile_report(F(1))
    ties = tie_control()
    refusals = refusal_controls()
    hostile_fired = (
        hostile["myopic_stops"] is True
        and hostile["bellman_continues"] is True
        and hostile["stop_is_optimal"] is False
        and hostile["two_step_plan_net_value"] == "1/4"
        and hostile["optimal_value_vstar_root"] == "3/4"
        and hostile["policy_search_optimal_value"] == "3/4"
    )
    clean_no_alarm = (
        clean["stop_is_optimal"] is True
        and clean["optimal_value_vstar_root"] == "1/2"
        and clean["best_root"] == "1/2"
    )
    ties_preserved = (
        set(ties["optimal_choice_set"]) == {"stop", "t1", "t2"}
        and set(ties["best_terminal_action_set"]) == {"a0", "a1"}
    )
    return {
        "hostile": hostile,
        "clean_variant": clean,
        "tie_control": ties,
        "refusals": refusals,
        "hostile_policy_count": policy_count(xor_graph(F(1, 8))),
        "policy_enumerations_total": 3 * policy_count(xor_graph(F(1, 8))),
        "hostile_fired": hostile_fired,
        "clean_variant_no_alarm": clean_no_alarm,
        "ties_preserved": ties_preserved,
        "refusals_enforced": bool(refusals["missing_goal_model_refused"]
                                  and refusals["cyclic_unbounded_graph_refused"]),
        "scope_tags": {"theorem": SCOPE_TAG_THEOREM, "hostile": SCOPE_TAG_HOSTILE},
    }


def planning_myopic_legacy_report() -> dict:
    """The retained myopic META-3 EVC rule at its PROVED scope (13/35).

    Imported verbatim from the frozen legacy planning/stopping package
    (freeze pin 7219b55a...).  The freeze requires the myopic rule be retained
    only at its proved scope, never promoted to a general stopping rule
    (MYOPIC_EVC_IS_UNIVERSALLY_OPTIMAL is forbidden).
    """
    legacy_dir = Path(__file__).resolve().parent.parent / "gmi-planning-stopping-v1"
    sys.path.insert(0, str(legacy_dir))
    import planning_stopping_v1 as legacy
    agree = 0
    total = 0
    for s in legacy.all_subsets():
        if legacy.common_actions(s):
            continue
        try:
            mins = set(legacy.tda_minimizers(s))
        except ValueError:
            continue
        total += 1
        leaders, _omegas, _conf = legacy.formed_goal(s)
        a = leaders[0]
        if bool(set(legacy.max_evc_tests(a, s)) & mins):
            agree += 1
    w = frozenset(legacy.WORLD6)
    subgoal = frozenset((3, 4))
    subsets = legacy.all_subsets()
    return {
        "myopic_greedy_optimality_13_of_35": [agree, total],
        "subset_census": len(subsets),
        "myopic_rule_proved_scope": "META-3 EVC composed as the planning stop rule; "
                                    "optimal in exactly 13/35 no-common-action subsets",
        "root_tda_value": str(legacy.tda_value(w)),
        "subgoal_strictly_between": str(legacy.tda_value(subgoal)),
        "disagree_witness": list(legacy.tda_minimizers(frozenset((3, 5)))),
        "forbidden_promotion": "MYOPIC_EVC_IS_UNIVERSALLY_OPTIMAL",
    }


def planning_row_full() -> dict:
    """The planning row: theorem checks, hostile, clean, ties, legacy scope."""
    return {
        "row": "Re-audit planning and stopping.",
        "results": ["PS-1", "PS-2"],
        "report": planning_row_report(),
        "legacy_myopic_scope": planning_myopic_legacy_report(),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(planning_row_full(), sort_keys=True, indent=2))
