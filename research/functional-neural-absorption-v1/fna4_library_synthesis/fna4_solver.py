"""FNA-4 solver: the incumbent composition search and the charged macro application.

The incumbent is breadth-first composition over atom sets, exactly the discipline of
``runtime/solve.py`` composed stage-by-stage: select operators through the PRODUCTION
inverted index (charged posting reads), simulate every structurally applicable candidate
(charged), goal-check every scalar produced (charged). Deadend expansions are the incumbent's
honest cost; a learned macro is one more catalogue entry whose expansion enumerates its hole
domains and simulates its body step-by-step, all charged.

Misfire registry = the failed-experience lane of #62's E_t: hard misfires are keyed by
(operator, input surface tag) -- value-independent and sound by construction; a misfire key
never says anything about other operators, tasks, or solvability, so failure knowledge never
becomes impossibility. Probe granularity is the FNA-1b-style lever: charging one probe per
candidate can never pay (probe cost == saved simulation cost); charging one probe per
selection batch can.
"""
from __future__ import annotations

import itertools
from collections import deque

from fna4 import PRIMITIVES, Work, atom_id, simulate, Misfire, PRIM_WARRANT

MAX_STATE_ATOMS = 14
#: Incumbent expansion bound. Sized once, before any scored run, from the frozen
#: families themselves (hardest F2 draw needs ~3.8e5 expansions), then given ~2.6x
#: margin. Identical for every arm -- parent parity.
INCUMBENT_CAP = 1000000


class MisfireRegistry(object):
    """(operator, surface-tag) hard-misfire memory. Sound: surface tags are value-free.

    Granularity is the FNA-1b-style lever: ``per_op`` charges one probe per candidate
    (can never pay at 1:1 unit commensurability -- a probe costs exactly one saved
    simulation); ``per_batch`` charges one probe per selection batch and the key lookups
    inside that batch are then uncharged."""

    def __init__(self, granularity="per_op"):
        assert granularity in ("per_op", "per_batch")
        self.granularity = granularity
        self.misfires = set()

    def register(self, op_name, surface):
        self.misfires.add((op_name, surface))

    def known(self, op_name, surface):
        return (op_name, surface) in self.misfires


def _apply_macro(macro, state, store, task, work, revoked=frozenset()):
    """State-aware macro application: the macro is one more catalogue entry.

    Entry inputs are enumerated exactly like a primitive's -- every ordered combo of the
    state's atoms of the macro's entry input types -- and the body then runs chain
    semantics over the remaining tape (each step consumes the most recent atom of each
    of its input types), one charged simulation per body step. Hole assignments enumerate
    within DOMAIN_CAP, all charged. The physics never becomes free; what the macro saves
    is search.

    Returns (hit, value, assignments_tried, misfires, first_failed_assignment).
    first_failed_assignment is the CEGIS counterexample (None if the macro never
    misfired, e.g. pure structural non-match)."""
    if not macro.warrant.is_live(revoked):
        return False, None, 0, 0, None
    by_type = {}
    for aid in sorted(state):
        by_type.setdefault(aid.split(":", 1)[0], []).append(aid)
    combos = list(itertools.product(*(by_type.get(t, []) for t in macro.in_types())))
    tried = mis = 0
    first_bad = None
    for combo in combos:
        if not combo:
            continue
        consumed = set(combo)
        seed = [(aid.split(":", 1)[0], store[aid])
                for aid in sorted(state) if aid not in consumed]
        entry_args = [store[aid] for aid in combo]
        for assignment in macro.assignments():
            tried += 1
            body = macro.body_names(assignment)
            tape = list(seed)
            args = list(entry_args)
            ok = True
            for name in body:
                if args is None:
                    args = []
                    for t in PRIMITIVES[name][0]:
                        idx = [i for i, (tt, _d) in enumerate(tape) if tt == t]
                        if not idx:
                            ok = False
                            break
                        args.append(tape.pop(idx[-1])[1])
                    if not ok:
                        break
                work.sim()
                try:
                    tape.append((PRIMITIVES[name][1], simulate(name, args)))
                except Misfire:
                    mis += 1
                    if first_bad is None:
                        first_bad = tuple(assignment)
                    ok = False
                    break
                args = None  # subsequent steps consume the tape
            if ok and macro.out_type() == "scalar":
                work.check()
                if tape[-1][1] == task.goal:
                    return True, tape[-1][1], tried, mis, None
    return False, None, tried, mis, first_bad


def _solution_chain(goal_aid, produced_by):
    """Backward slice from the goal atom: the dependency-ordered primitive composition."""
    seen, order = set(), []

    def walk(aid):
        if aid in seen:
            return
        seen.add(aid)
        name, ins = produced_by[aid]
        for i in ins:
            walk(i)
        if name is not None:
            order.append(name)

    walk(goal_aid)
    return tuple(order)


def solve_task(task, macros=(), registry=None, work=None, cap=INCUMBENT_CAP, index=None,
               revoked=frozenset(), macros_enabled=True, collect_all=False):
    """Breadth-first composition search. Returns the task receipt dict; all work charged.

    collect_all=True (acquisition discipline): do NOT early-exit on the first
    goal-reaching composition -- run the paid search to its bound and record EVERY
    checker-passing chain found. Experience E_t is everything the incumbent actually ran,
    not only its luckiest shallowest success; recording a found chain costs one charged
    bookkeeping step (the search itself was already paid). Test-time solves keep the
    early exit: fresh-task cost is time-to-first-solution."""
    from fna4 import INDEX
    index = index or INDEX
    work = work if work is not None else Work()
    macros = tuple(m for m in macros if macros_enabled)
    store = {}          # atom_id -> data
    surface = {}        # atom_id -> surface tag
    produced_by = {}    # atom_id -> (op_name, input atom ids)
    for (t, s, d) in task.initial:
        aid = atom_id(t, d)
        store[aid] = d
        surface[aid] = s
        produced_by[aid] = (None, ())
    start = frozenset(store)
    queue = deque([(start, None)])
    visited = {start}
    expansions = misfires = macro_hits = 0
    macro_attempts = []
    capped = False
    all_chains = []
    solved_chain = None

    def goal_found(name, combo, out_aid):
        nonlocal solved_chain
        produced_by[out_aid] = (name, combo)
        chain = _solution_chain(out_aid, produced_by)
        if collect_all:
            work.learn()  # one charged bookkeeping step per recorded experience chain
            if chain not in all_chains:
                all_chains.append(chain)
            if solved_chain is None:
                solved_chain = chain
            return False
        solved_chain = chain
        return True

    while queue and not capped:
        state, _ = queue.popleft()
        types_here = {aid.split(":", 1)[0] for aid in state}
        sel = index.select(types_here)
        work.post(sel.work["postings_examined"])
        if registry is not None and registry.granularity == "per_batch":
            work.learn()  # one charged probe for the whole selection batch
        for op in sel.operators:
            name = op.operator_id
            if not PRIM_WARRANT[name].is_live(revoked):
                continue
            ins = PRIMITIVES[name][0]
            by_type = {}
            for aid in sorted(state):
                by_type.setdefault(aid.split(":", 1)[0], []).append(aid)
            for combo in itertools.product(*(by_type.get(t, []) for t in ins)):
                expansions += 1
                surfaces = tuple(surface[a] for a in combo)
                if registry is not None:
                    if registry.granularity == "per_op":
                        work.learn()  # one charged probe per candidate
                    if any(registry.known(name, s) for s in surfaces):
                        continue
                work.sim()
                try:
                    out = simulate(name, [store[a] for a in combo])
                except Misfire:
                    misfires += 1
                    if registry is not None:
                        for s in surfaces:
                            registry.register(name, s)
                    continue
                typ = PRIMITIVES[name][1]
                aid = atom_id(typ, out)
                if typ == "scalar":
                    work.check()
                    if out == task.goal:
                        if goal_found(name, combo, aid):
                            return _receipt(task, True, work, expansions, misfires,
                                            macro_hits, solved_chain, capped,
                                            macro_attempts, all_chains)
                        continue
                if aid in state:
                    continue
                produced_by[aid] = (name, combo)
                store.setdefault(aid, out)
                surface.setdefault(aid, "derived")
                new_state = state | {aid}
                if len(new_state) <= MAX_STATE_ATOMS and new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, aid))
            if expansions > cap:
                capped = True
                break
        for macro in sorted(macros, key=lambda m: m.macro_id):
            if not all(t in types_here for t in macro.in_types()):
                continue
            expansions += 1
            hit, _value, tried, mis, first_bad = _apply_macro(macro, state, store, task,
                                                              work, revoked)
            misfires += mis
            macro_attempts.append({"macro_id": macro.macro_id, "hit": hit,
                                   "assignments_tried": tried, "misfires": mis,
                                   "first_failed_assignment": list(first_bad)
                                   if first_bad is not None else None})
            if hit:
                macro_hits += 1
                if collect_all:
                    continue  # acquisition discipline: record, keep searching
                return _receipt(task, True, work, expansions, misfires, macro_hits,
                                ("<macro:%s>" % macro.macro_id,), capped,
                                macro_attempts, all_chains)
        if expansions > cap:
            capped = True
    return _receipt(task, solved_chain is not None, work, expansions, misfires,
                    macro_hits, solved_chain or (), capped, macro_attempts, all_chains)


def _receipt(task, solved, work, expansions, misfires, macro_hits, chain, capped,
             macro_attempts=(), all_chains=()):
    return {"task_id": task.task_id, "family": task.family, "solved": solved,
            "capped": capped, "expansions": expansions, "misfires": misfires,
            "macro_hits": macro_hits, "solution_chain": list(chain),
            "macro_attempts": list(macro_attempts), "work": work.as_dict(),
            "all_solution_chains": [list(c) for c in all_chains]}


def validate_selection_mirror(index, trials=40, rng=None):
    """Harness validation (FNA4_PROTOCOL.md): production index counts must equal a brute
    force enumeration over the same catalogue and type subsets, or nothing is interpretable."""
    import random as _r
    rng = rng or _r.Random(77003)
    names = sorted(PRIMITIVES)
    for _ in range(trials):
        types = {t for t in ("raw", "tokens", "scalar") if rng.random() < 0.5}
        sel = index.select(types)
        brute = [n for n in names if set(PRIMITIVES[n][0]) <= types]
        if sorted(o.operator_id for o in sel.operators) != brute:
            return False
        postings = sum(len([n for n in names if a in PRIMITIVES[n][0]]) for a in types)
        # production anchors each op under its RAREST input; postings examined per probed
        # atom is the number of ops whose anchor set contains that atom. Anchor rule:
        freq = {a: sum(1 for n in names for x in PRIMITIVES[n][0] if x == a)
                for a in ("raw", "tokens", "scalar")}
        anchors = {}
        for n in names:
            ins = PRIMITIVES[n][0]
            a = min(ins, key=lambda x: (freq[x], x))
            anchors.setdefault(a, []).append(n)
        expected = sum(len(anchors.get(a, [])) for a in types)
        if sel.work["postings_examined"] != expected or \
                sel.work["structural_candidates"] != len(brute):
            return False
    return True
