"""FNA-4 learners: the classical parents of FNA4_SOURCE_LEDGER.json, stdlib only.

- CHUNK    Soar-style chunking: exact-difference conditions, no abstraction. Every solved
           composition is stored verbatim; reuse requires the exact same parameters.
- AU_PAIR  Reynolds anti-unification, incremental, whole-trace: the least general
           generalization of two solved compositions, holes at disagreement positions.
- STITCH   top-down library learning (Bowers et al. POPL 2023, neural guide absent by
           construction): repeatedly admit the single abstraction with maximum usefulness
           (uses x (body-1) - definition), rewrite the corpus, repeat to budget.
- EGGRAPH  equality saturation (egg) over the trace corpus: canonicalize AC merge inputs,
           union identical segments into e-classes, extract shared classes (>= 2 traces)
           by anti-unifying the class members.
- ORACLE   teleport upper bound: the true family patterns at zero acquisition cost.
           Labelled ORACLE everywhere; never a result.
- CEGIS    counterexample-guided specialization of a macro's hole domains from a misfiring
           assignment (Solar-Lezama parent); each refinement is charged.

Every learner step is charged one unit into the shared Work. Learners see ONLY the solved
compositions (solution chains) -- the same information surface for every arm.
"""
from __future__ import annotations

from fna4 import family_of, name_params, make_macro, Macro
from fna4_solver import solve_task

MAX_LIBRARY = 6
MAX_PATTERN_LEN = 5


def step_sig(name):
    return (family_of(name), name_params(name)[1:])


def traces_of(receipts):
    """The experience surface: every chain the incumbent actually succeeded with (the
    acquisition receipts carry all_solution_chains; single-solve receipts collapse to
    their one chain). Identical for every arm -- parent parity."""
    out = []
    for r in receipts:
        if not r.get("solved"):
            continue
        chains = r.get("all_solution_chains") or [r["solution_chain"]]
        for c in chains:
            t = tuple(c)
            if t not in out:
                out.append(t)
    return out


def anti_unify(t1, t2):
    """Least general generalization of two equal-length traces. None if shapes differ."""
    if len(t1) != len(t2):
        return None
    return _au_stepwise([step_sig(n) for n in t1], [step_sig(n) for n in t2])


def _au_stepwise(sigs1, sigs2):
    if len(sigs1) != len(sigs2):
        return None
    skeleton = []
    for (fa, pa), (fb, pb) in zip(sigs1, sigs2):
        if fa != fb or len(pa) != len(pb):
            return None
        skeleton.append((fa, tuple(x if x == y else None for x, y in zip(pa, pb))))
    return tuple(skeleton)


def windows(seq, length):
    return [tuple(seq[i:i + length]) for i in range(len(seq) - length + 1)]


def match_skeleton(skeleton, window):
    """Window matches if families align and const slots are equal. Returns instance sigs."""
    if len(window) != len(skeleton) or not skeleton:
        return None
    inst = []
    for (fam, slots), name in zip(skeleton, window):
        if not isinstance(name, str):
            return None
        f, p = step_sig(name)
        if f != fam or len(p) != len(slots):
            return None
        for s, v in zip(slots, p):
            if s is not None and s != v:
                return None
        inst.append((fam, p))
    return inst


def find_instances(skeleton, corpus):
    """Every window of every corpus trace (strings only; rewritten '@' nodes opaque)
    that matches the skeleton, as per-step signatures."""
    out = []
    for trace in corpus:
        for w in _all_str_windows(trace, len(skeleton)):
            inst = match_skeleton(skeleton, w)
            if inst is not None:
                out.append(inst)
    return out


def _all_str_windows(trace, length):
    """Windows over maximal contiguous runs of plain primitive names."""
    out, run = [], []
    for x in list(trace) + [None]:
        if isinstance(x, str):
            run.append(x)
        else:
            out.extend(windows(run, length))
            run = []
    return out


def _contig_runs(trace):
    runs, cur = [], []
    for x in trace:
        if isinstance(x, str):
            cur.append(x)
        else:
            if cur:
                runs.append(cur)
                cur = []
    if cur:
        runs.append(cur)
    return runs


def compression(skeleton, uses):
    """uses x (body-1) - definition: the MDL-flavoured usefulness of Stitch, in nodes."""
    return uses * (len(skeleton) - 1) - len(skeleton)


def _dedupe_macros(macros):
    seen, out = set(), []
    for m in sorted(macros, key=lambda m: (-m.size(), m.macro_id)):
        if m.skeleton not in seen:
            seen.add(m.skeleton)
            out.append(m)
    return out[:MAX_LIBRARY]


def learn_chunk(receipts, work):
    """Soar chunking: store every solved composition verbatim (exact-difference key).
    Under the shared MAX_LIBRARY budget, largest compositions first -- the cache analogue
    of the other parents' admission filtering."""
    macros = []
    for t in traces_of(receipts):
        work.learn()
        skeleton = tuple(step_sig(n) for n in t)
        macros.append(make_macro(skeleton, [skeleton], label="CHUNK"))
    return _dedupe_macros(macros)


def learn_au(receipts, work):
    """Reynolds anti-unification over whole solved traces, pairwise and incremental."""
    traces = traces_of(receipts)
    candidates = []
    for i in range(len(traces)):
        for j in range(i + 1, len(traces)):
            work.learn()
            sk = anti_unify(traces[i], traces[j])
            if sk is not None:
                candidates.append(sk)
    macros = []
    for sk in sorted(set(candidates), key=lambda s: (-len(s), s)):
        inst = find_instances(sk, traces)
        if len(inst) >= 2:
            work.learn()
            macros.append(make_macro(sk, inst, label="AU"))
    return _dedupe_macros(macros)


def learn_stitch(receipts, work, budget=8):
    """Top-down: best-compression abstraction first, corpus rewritten, repeat to budget."""
    corpus = [list(t) for t in traces_of(receipts)]
    macros = []
    for _round in range(budget):
        segs = []
        for trace in corpus:
            for run in _contig_runs(trace):
                for ln in range(2, min(MAX_PATTERN_LEN, len(run)) + 1):
                    segs.extend(windows(run, ln))
        best, best_comp = None, 0
        seen_sk = set()
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                work.learn()
                sk = anti_unify(segs[i], segs[j])
                if sk is None or sk in seen_sk:
                    continue
                seen_sk.add(sk)
                work.learn()
                uses = len(find_instances(sk, [tuple(t) for t in corpus]))
                comp = compression(sk, uses)
                if comp > best_comp:
                    best, best_comp = sk, comp
        if best is None:
            break
        inst = find_instances(best, [tuple(t) for t in corpus])
        m = make_macro(best, inst, label="STITCH")
        macros.append(m)
        node = ("@", m.macro_id)
        for t_i, trace in enumerate(corpus):
            replaced = _rewrite(best, trace, node)
            corpus[t_i] = replaced
    return _dedupe_macros(macros)


def _rewrite(skeleton, trace, node):
    """Replace the first matching window (longest-first scan) by the macro node."""
    for ln in range(len(skeleton), 0, -1):
        for wi in range(len(trace) - ln + 1):
            if match_skeleton(skeleton, tuple(trace[wi:wi + ln])) is not None:
                return list(trace[:wi]) + [node] + list(trace[wi + ln:])
    return list(trace)


def canonicalize(trace, work):
    """E-graph rewrite for the AC merge: the two parse inputs of a merge are unordered."""
    t = list(trace)
    for i in range(2, len(t)):
        if family_of(t[i]) == "merge" and family_of(t[i - 1]) == "parse" \
                and family_of(t[i - 2]) == "parse":
            work.learn()
            a, b = t[i - 2], t[i - 1]
            t[i - 2], t[i - 1] = min(a, b), max(a, b)
    return tuple(t)


def learn_egraph(receipts, work):
    """Equality saturation, minimal sound fragment (egg parent, E1/L1 scope): saturate
    the corpus under the two sound rewrite families of this algebra -- idempotent dedup
    of identical segments, and AC reordering of merge inputs -- then union segments into
    family-shaped e-classes and extract each shared class by anti-unifying its members
    (the most specific generalization). The AC canonicalization is the load-bearing part:
    it merges the merge-order variants that whole-trace anti-unification must hold holes
    for, so the extracted pattern has fewer holes, smaller domains and cheaper selection.
    Full e-graph scheduling / rule DSL is out of scope here."""
    traces = traces_of(receipts)
    canon = [canonicalize(t, work) for t in traces]
    classes = {}
    for t in canon:
        for ln in range(2, min(MAX_PATTERN_LEN, len(t)) + 1):
            for seg in windows(t, ln):
                work.learn()
                key = tuple(step_sig(n)[0] for n in seg)  # family shape = e-class key
                classes.setdefault(key, []).append([step_sig(n) for n in seg])
    macros = []
    for key, insts in sorted(classes.items(), key=lambda kv: (-len(kv[0]), kv[0])):
        uses = len(insts)
        if uses < 2:
            continue
        work.learn()
        uniq = []
        for inst in insts:  # saturation: identical segments collapse (dedup rewrite)
            if inst not in uniq:
                uniq.append(inst)
        if len(uniq) >= 2:
            sk = tuple(uniq[0])
            for other in uniq[1:]:
                sk = _au_stepwise(list(sk), other)
                if sk is None:
                    break
            if sk is None:
                continue
        else:
            sk = tuple(uniq[0])  # saturated class: repeated uses, one canonical term
        if compression(sk, uses) <= 0:
            continue  # MDL: uses x (body-1) - definition must be positive to admit
        macros.append(make_macro(sk, uniq, label="EG"))
    return _dedupe_macros(macros)


def learn_oracle(tasks, work):
    """ORACLE teleport: the true composition of each task, zero acquisition, upper bound."""
    macros = []
    for t in tasks:
        skeleton = tuple(step_sig(n) for n in t.true_chain)
        macros.append(make_macro(skeleton, [skeleton], label="ORACLE"))
    return macros


def specialize(macro, failing_assignment, work):
    """CEGIS: shrink hole domains away from a misfiring assignment. Refuses to empty a
    domain (a hole with no values is a refusal, not a claim of impossibility)."""
    holes = sum(1 for _f, slots in macro.skeleton for s in slots if s is None)
    if holes != len(failing_assignment):
        return macro, False
    doms, h = [], 0
    for _fam, slots in macro.skeleton:
        for s in slots:
            if s is None:
                work.learn()
                keep = tuple(x for x in macro.domains[h] if x != failing_assignment[h])
                if not keep:
                    return macro, False  # REFUSED_EMPTY_DOMAIN
                doms.append(keep)
                h += 1
    return Macro(macro.macro_id + "-cegis", macro.skeleton, tuple(doms),
                 macro.warrant, macro.label + "+CEGIS"), True


def acquire(tasks, learner, work, **kw):
    """Solve the acquisition stream first-exposure (no library), then learn from the
    solved compositions. Returns (macros, receipts)."""
    receipts = [solve_task(t, work=work, **kw) for t in tasks]
    macros = learner(receipts, work)
    return macros, receipts
