"""C: a negative ecology for every learning law, constructed not asserted.

Section C asks, for each law, for a negative ecology where it loses.  The
update object of GMI_UPDATE_OBJECT_V1 makes that computable rather than
rhetorical: paradigms are subsets of one enumerated space, so "loses" means a
task on which the paradigm's BEST member scores below another paradigm's best.

THE ECOLOGY
    Evidence sequences of length 2 over {0,1} -- four of them.  An update runs
    from a fixed initial state and produces a final state per sequence, so every
    update has a BEHAVIOUR: a 4-tuple of final states.

    A TASK is a required behaviour -- one of 4^4 = 256.  A paradigm's score on a
    task is the best match any of its members achieves, 0 to 4.

    A task is a NEGATIVE ECOLOGY for paradigm P when some other paradigm scores
    strictly higher on it.  That is a constructed instance, not an argument:
    the task is exhibited and both scores are computed.
"""

import json
import os
import itertools

S, E, L = 4, 2, 2
SEQS = list(itertools.product(range(E), repeat=L))
START = 0
ALL = list(itertools.product(range(S), repeat=S * E))


def apply(u, s, e):
    return u[s * E + e]


def behaviour(u):
    out = []
    for seq in SEQS:
        s = START
        for e in seq:
            s = apply(u, s, e)
        out.append(s)
    return tuple(out)


def is_additive(u):
    return any(all(apply(u, s, e) == (s + g[e]) % S for s in range(S) for e in range(E))
               for g in itertools.product(range(S), repeat=E))


def is_overwrite(u):
    return all(apply(u, 0, e) == apply(u, s, e) for s in range(S) for e in range(E))


def is_insertion(u):
    return all((s & ~apply(u, s, e)) == 0 for s in range(S) for e in range(E))


def is_idempotent(u):
    return all(apply(u, apply(u, s, e), e) == apply(u, s, e)
               for s in range(S) for e in range(E))


def is_keep_or_replace(u):
    return any(all(apply(u, s, e) in (s, h[e]) for s in range(S) for e in range(E))
               for h in itertools.product(range(S), repeat=E))


def is_state_only(u):
    return all(apply(u, s, 0) == apply(u, s, e) for s in range(S) for e in range(E))


PRED = {
    "additive": is_additive,
    "overwrite": is_overwrite,
    "insertion-monotone": is_insertion,
    "idempotent-on-repeat": is_idempotent,
    "keep-or-replace": is_keep_or_replace,
    "state-only": is_state_only,
}

print("=" * 88)
print("C: A NEGATIVE ECOLOGY FOR EVERY LEARNING LAW")
print("=" * 88)
beh = {name: {behaviour(u) for u in ALL if f(u)} for name, f in PRED.items()}
for n, b in beh.items():
    print("  %-24s %4d distinct behaviours" % (n, len(b)))
    assert b, "%s has no behaviour at all" % n

TASKS = list(itertools.product(range(S), repeat=len(SEQS)))
print("  tasks (required behaviours): %d" % len(TASKS))


def best(name, task):
    return max(sum(1 for a, b in zip(v, task) if a == b) for v in beh[name])


scores = {n: [best(n, t) for t in TASKS] for n in PRED}

print()
print("-" * 88)
print("NEGATIVE ECOLOGIES")
print("-" * 88)
neg, dominant, examples = {}, [], {}
for n in PRED:
    losses = [i for i in range(len(TASKS))
              if any(scores[m][i] > scores[n][i] for m in PRED if m != n)]
    neg[n] = len(losses)
    if losses:
        i = losses[0]
        winner = max((m for m in PRED if m != n), key=lambda m: scores[m][i])
        examples[n] = {"task": list(TASKS[i]), "its_score": scores[n][i],
                       "beaten_by": winner, "winner_score": scores[winner][i]}
    else:
        dominant.append(n)
    print("  %-24s loses on %4d of %d tasks%s"
          % (n, len(losses), len(TASKS), "" if losses else "   <-- never loses"))

print()
for n, ex in list(examples.items())[:6]:
    print("  %-22s e.g. task %s scores %d, beaten by %s at %d"
          % (n, ex["task"], ex["its_score"], ex["beaten_by"], ex["winner_score"]))

assert not dominant, (
    "a paradigm never loses on any task: %s -- it would dominate the space and "
    "section C's negative-ecology requirement would be unsatisfiable for it"
    % dominant)
assert all(0 < v < len(TASKS) for v in neg.values()), (
    "a paradigm loses on every task or none; losing everywhere would mean it is "
    "never worth using, and the box asks for an ecology where it loses, not for "
    "a law that always loses")

uniq = {}
for n in PRED:
    u = sum(1 for i in range(len(TASKS))
            if all(scores[n][i] > scores[m][i] for m in PRED if m != n))
    uniq[n] = u
print()
print("-" * 88)
print("WHERE EACH LAW UNIQUELY WINS")
print("-" * 88)
for n, u in uniq.items():
    print("  %-24s uniquely best on %4d of %d tasks" % (n, u, len(TASKS)))
never = [n for n, u in uniq.items() if u == 0]
print()
print("  laws with no task of their own: %s" % (", ".join(never) or "none"))

# WHY a law is never uniquely best matters more than THAT it is.
# A paradigm strictly contained in another can never be uniquely best: whenever
# it is optimal, its superset contains that same member and ties.  That is a
# theorem, and it should account for some of the never-unique laws.  Any law
# that is never uniquely best WITHOUT being contained needs a different
# explanation, and is reported as unexplained rather than folded in.
contained = {}
for a, b in itertools.permutations(PRED, 2):
    A = {u for u in ALL if PRED[a](u)}
    B = {u for u in ALL if PRED[b](u)}
    if A < B:
        contained.setdefault(a, []).append(b)
explained = [n for n in never if n in contained]
unexplained = [n for n in never if n not in contained]
print()
print("-" * 88)
print("WHY, AND WHERE THE EXPLANATION RUNS OUT")
print("-" * 88)
for n in never:
    if n in contained:
        print("  %-22s never uniquely best -- strictly inside %s"
              % (n, ", ".join(contained[n])))
    else:
        print("  %-22s never uniquely best -- NOT contained in any other law;"
              % n)
        print("  %-22s this is unexplained by containment and is reported as such" % "")
assert explained, (
    "no never-unique law is explained by containment, so the theorem that a "
    "strictly contained paradigm cannot be uniquely best has no instance here")
for n in contained:
    assert uniq[n] == 0, (
        "%s is strictly contained in %s yet is uniquely best on %d tasks, which "
        "contradicts the containment argument -- one of the two computations is "
        "wrong" % (n, contained[n], uniq[n]))

OUT = {"contained_in": contained,
       "never_unique_explained_by_containment": explained,
       "never_unique_unexplained": unexplained,
       "tasks": len(TASKS), "behaviours": {n: len(b) for n, b in beh.items()},
       "loses_on": neg, "uniquely_best_on": uniq,
       "never_uniquely_best": never, "examples": examples,
       "scope": ("length-2 evidence sequences from one fixed initial state; a "
                 "law losing here is a constructed instance, not a claim that "
                 "it loses in general")}
os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_NEGATIVE_ECOLOGY_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 88)
print("all assertions held")
print("=" * 88)
print("  receipt: microscopes/results/STAGE_NEGATIVE_ECOLOGY_V1.json")
