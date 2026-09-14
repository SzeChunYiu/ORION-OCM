# Strict local skill advantage

## CSG-1: availability versus optimal use

Fix a finite target string t of length n. States are positions i=0,...,n.
The primitive at i emits t_i and moves to i+1 at finite nonnegative cost c_i.
Every registered skill is a nonempty literal string with finite nonnegative
call cost u_s. It is available exactly when it matches at i, emits that same
substring, and moves to j=i+len(s). All underlying emitted-symbol delivery work
is included in both routes. The library is fixed and installed; acquisition,
model construction and planner costs are separately charged below.

Let W_n=V_n=0, W_i=c_i+W_(i+1), and

    P_i = c_i + V_(i+1)
    M_i = min_{matching s} (u_s + V_(i+len(s)))
    V_i = min(P_i,M_i),       min(empty)=+infinity.

Backward induction proves V is the minimum over every complete legal parse:
partition any parse by its first primitive or skill call, then use its optimal
suffix. The finite register guarantees attainment, including zero-cost calls,
because every transition strictly advances position. There is no greedy parse
restriction. An attaining call choice constructs an executable parse.

Write Delta_i=W_i-V_i. Direct subtraction gives the exact local identity

    Delta_i - Delta_(i+1) = P_i - V_i = max(0, P_i-M_i).

Consequently a strict local drop occurs iff some available skill has strictly
smaller total continuation cost than the primitive followed by optimal reuse.
Every strict local drop is a skill entry, but an entry need not improve cost.
The two sets are equal iff M_i<P_i at every entry i. This is a checkable
strict-advantage condition, stronger than fixed availability or cheap calls.
A tie is deliberately not a strict improvement.

## CSG-2: decisive negative and positive controls

For t=abc, skills ab and bc, all primitive and call costs1:

    W=(3,2,1,0), V=(2,1,1,0), Delta=(1,1,0,0).

Both positions0 and1 are entries, but only1 is a strict local drop. At0, using
ab and waiting for bc tie. Each skill saves a primitive instruction in isolation;
overlap defeats the claimed equality. For abcd with ab,bcd at the same costs,
taking ab is strictly worse than waiting for bcd, so a tie convention is not
the whole problem. With abc alone on target abcabc, entries0,3 are exactly
the strict local drops: the stronger premise is attainable.

Adding a common cost d per delivered symbol to every implementation adds
(n-i)d to both V_i and W_i. Delta and the advantage identity are unchanged.
The executor records every emitted symbol even when a skill makes one call.
Compiled invocation never erases descendant output work.

## CSG-3: general finite acyclic planning

For a supplied finite DAG with successful terminals and at least one primitive
path to a terminal from each admitted state, let P(s) be the best primitive
edge cost plus V at its destination; let M(s) be the best available option's
complete cost plus V at its destination. Then V=min(P,M), and P-V>0 iff M<P.
This is ordinary Bellman choice over primitive and extended actions. For
multiple primitive successors there is no canonical successor-drop subtraction;
the prefix identity uses the explicitly unique primitive successor above.

None of these equations proves that every useful psychological or learned
subgoal is a skill entry. They identify strict option advantage under a given
interface, objective, library and target. The source's 30-state result remains
correct for its supplied instance, and the independent checker reconstructs
both its original and local comparisons.
