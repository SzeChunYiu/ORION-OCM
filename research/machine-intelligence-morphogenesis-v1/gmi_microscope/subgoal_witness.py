"""Item 11: are subgoals exactly the entry states of retained skills?

Item 10 derived skills as retained sub-quotients. The natural conjecture is that a SUBGOAL
is a state at which the cost-to-go drops discontinuously because a retained skill becomes
applicable. That is testable, not merely suggestive:

  * compute cost-to-go over every state, with and without retained skills;
  * a state is a "discontinuity" iff retention strictly lowers its cost-to-go;
  * the conjecture holds iff the discontinuity set EQUALS the set of skill entry states.

Complete enumeration over all prefixes of all targets. No search.
"""
import json

TARGETS = ["abcabd", "abcabe", "abdabc", "abeabc", "abcabc"]
C_PRIM, U_REF = 1, 1
SKILLS = ["abc", "abd", "abe"]          # the retained set the hierarchy witness selected

def ctg(target, i, skills):
    """cheapest completion cost of target from position i, given retained skills"""
    n = len(target)
    best = [0] * (n + 1)
    for p in range(n - 1, -1, -1):
        opts = [C_PRIM + best[p + 1]]
        for s in skills:
            if target.startswith(s, p):
                opts.append(U_REF + best[p + len(s)])
        best[p] = min(opts)
    return best[i]

states, disc, entries = [], set(), set()
for t in TARGETS:
    for i in range(len(t)):
        bare = ctg(t, i, [])
        withs = ctg(t, i, SKILLS)
        state = (t, i)
        states.append({"target": t, "pos": i, "prefix": t[:i], "suffix": t[i:],
                       "ctg_bare": bare, "ctg_with_skills": withs, "drop": bare - withs})
        if withs < bare:
            disc.add(state)
        if any(t.startswith(s, i) for s in SKILLS):
            entries.add(state)

print("states enumerated:", len(states))
print("states where retention strictly lowers cost-to-go (discontinuities):", len(disc))
print("states where some retained skill is applicable (entry states):      ", len(entries))
print("sets identical:", disc == entries)
only_disc = disc - entries
only_entry = entries - disc
print("  discontinuity but not an entry state:", len(only_disc), sorted(only_disc)[:4])
print("  entry state but no discontinuity    :", len(only_entry), sorted(only_entry)[:4])

# where the drops are largest -- the strongest subgoals
top = sorted(states, key=lambda s: -s["drop"])[:6]
print("\nlargest cost-to-go drops (strongest subgoals):")
print("  target   pos  suffix     bare  with  drop")
for s in top:
    print("  %-8s %-4d %-10s %-5d %-5d %d" % (s["target"], s["pos"], s["suffix"],
                                              s["ctg_bare"], s["ctg_with_skills"], s["drop"]))
json.dump({"schema": "SubgoalEntryStateWitnessV1", "targets": TARGETS, "skills": SKILLS,
           "n_states": len(states), "n_discontinuities": len(disc), "n_entry_states": len(entries),
           "sets_identical": disc == entries,
           "discontinuity_not_entry": sorted(map(list, only_disc)),
           "entry_not_discontinuity": sorted(map(list, only_entry)),
           "states": states},
          open("microscopes/results/STAGE_SUBGOAL_WITNESS_V1.json", "w"), indent=1, sort_keys=True)
print("\nwritten")
