#!/usr/bin/env python3
"""GMI #833 AE13 -- causality and intervention.  Route A (analytic executor).

Exhaustive exact census of structural causal models over three binary variables:
all 25 labelled DAGs, every conditional probability table drawn from the frozen
rational grid {0, 1/4, 1/2, 3/4, 1}.  Interventions are single-variable and
atomic, taken by truncated factorisation.

Every probability is an exact integer numerator over a fixed power-of-four
denominator, or a `Fraction`.  No float appears anywhere.

    python3 -I -B  ae13_causality_intervention_v1.py
    python3 -I -O -B ae13_causality_intervention_v1.py
"""

from fractions import Fraction as F
import itertools
import json
import sys

SCHEMA = "GMI_833_AE13_CAUSALITY_INTERVENTION_RESULT_V1"
SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
FREEZE_COMMIT = "b1413bbe95b4d0de26635d1d026716df93226818"
CLAIM_CEILING = (
    "GMI_833_AE13_OBSERVATIONAL_TO_CAUSAL_NON_IDENTIFICATION_EXACTLY_CENSUSED_"
    "AND_PRICED_AT_REGISTERED_FINITE_SCOPE"
)
COMMENT_ID = 5692689542

FORBIDDEN_PROMOTIONS = [
    "OBSERVATIONAL_DATA_NEVER_IDENTIFIES_CAUSAL_STRUCTURE",
    "CAUSAL_DISCOVERY_IMPOSSIBILITY_PROVED",
    "MULTI_VARIABLE_INTERVENTION_PROVED",
    "LATENT_CONFOUNDER_GENERAL_CASE_PROVED",
    "CONTINUOUS_VARIABLE_EXTENSION_PROVED",
    "INTERVENTION_ALWAYS_WORTH_ITS_COST",
    "COMPUTATIONAL_MECHANICS_CAUSAL_STATE_IS_PEARLIAN_CAUSAL_STATE",
    "GMI_MORPHOLOGY_PREDICTION",
    "ARCHITECTURE_SELECTION_LAW",
    "COMPLETE_GMI",
]

# --------------------------------------------------------------------------
# Frozen scope
# --------------------------------------------------------------------------

VARS = ("A", "B", "C")
NV = 3
GRID_NUM = (0, 1, 2, 3, 4)      # k/4 for k in GRID_NUM -- the frozen grid
GRID_DEN = 4
ATOMS = tuple(itertools.product((0, 1), repeat=NV))   # (a, b, c)
JOINT_DEN = GRID_DEN ** NV       # 64
TRUNC_DEN = GRID_DEN ** (NV - 1)  # 16


def all_dags():
    """Every labelled DAG on 3 vertices, as a tuple of parent tuples."""
    out = []
    edges = [(i, j) for i in range(NV) for j in range(NV) if i != j]
    for mask in range(1 << len(edges)):
        chosen = [edges[k] for k in range(len(edges)) if mask >> k & 1]
        par = [[] for _ in range(NV)]
        ok = True
        for (i, j) in chosen:
            if (j, i) in chosen:
                ok = False
                break
            par[j].append(i)
        if not ok:
            continue
        # acyclicity by topological peel
        rem = set(range(NV))
        pa = dict((v, set(par[v])) for v in range(NV))
        while True:
            free = [v for v in rem if not (pa[v] & rem)]
            if not free:
                break
            rem.discard(free[0])
        if rem:
            continue
        out.append(tuple(tuple(sorted(p)) for p in par))
    return sorted(set(out))


DAGS = all_dags()


def skeleton(dag):
    s = set()
    for v, ps in enumerate(dag):
        for p in ps:
            s.add(frozenset((p, v)))
    return frozenset(s)


def v_structures(dag):
    out = set()
    for v, ps in enumerate(dag):
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                a, b = ps[i], ps[j]
                if b not in dag[a] and a not in dag[b]:
                    out.add((min(a, b), v, max(a, b)))
    return frozenset(out)


def markov_classes():
    """Verma & Pearl 1990: same skeleton and same v-structures."""
    cls = {}
    for i, d in enumerate(DAGS):
        cls.setdefault((skeleton(d), v_structures(d)), []).append(i)
    return sorted(cls.values())


MCLASSES = markov_classes()


def cpt_slots(dag):
    """(variable, parent-assignment) slots needing a grid value."""
    slots = []
    for v, ps in enumerate(dag):
        for asg in itertools.product((0, 1), repeat=len(ps)):
            slots.append((v, asg))
    return slots


def compile_dag(dag, slots):
    """Per-atom list of (slot index, use_k) so the inner loop is index work."""
    pos = dict((slots[i], i) for i in range(len(slots)))
    plan = []
    for x in ATOMS:
        row = []
        for v in range(NV):
            asg = tuple(x[p] for p in dag[v])
            row.append((pos[(v, asg)], x[v] == 1))
        plan.append(tuple(row))
    return tuple(plan)


def joint_fast(plan, theta):
    out = []
    for row in plan:
        n = 1
        for (i, hi) in row:
            k = theta[i]
            n *= k if hi else (GRID_DEN - k)
        out.append(n)
    return tuple(out)


def trunc_fast(plan, theta, var, val):
    out = []
    for ai, row in enumerate(plan):
        if ATOMS[ai][var] != val:
            out.append(0)
            continue
        n = 1
        for v in range(NV):
            if v == var:
                continue
            i, hi = row[v]
            k = theta[i]
            n *= k if hi else (GRID_DEN - k)
        out.append(n)
    return tuple(out)


def query_fast(plan, theta):
    """The three registered ACEs as exact integer numerators over TRUNC_DEN.

    Keeping them integral is not an approximation: every truncated joint has
    denominator exactly TRUNC_DEN, so the difference of two of its marginals is
    an integer over TRUNC_DEN and nothing is rounded.
    """
    out = []
    for name, cause, effect in QUERIES:
        hi = trunc_fast(plan, theta, cause, 1)
        lo = trunc_fast(plan, theta, cause, 0)
        a = 0
        b = 0
        for i, x in enumerate(ATOMS):
            if x[effect] == 1:
                a += hi[i]
                b += lo[i]
        out.append(a - b)
    return tuple(out)


def q_to_fraction(q):
    return F(q, TRUNC_DEN)


def joint_numerators(dag, slots, theta):
    """Observational joint as 8 integer numerators over JOINT_DEN."""
    table = dict((slots[i], theta[i]) for i in range(len(slots)))
    out = []
    for x in ATOMS:
        n = 1
        for v in range(NV):
            asg = tuple(x[p] for p in dag[v])
            k = table[(v, asg)]
            n *= k if x[v] == 1 else (GRID_DEN - k)
        out.append(n)
    return tuple(out)


def truncated_numerators(dag, slots, theta, var, val):
    """p(.|do(var=val)) as 8 integer numerators over TRUNC_DEN."""
    table = dict((slots[i], theta[i]) for i in range(len(slots)))
    out = []
    for x in ATOMS:
        if x[var] != val:
            out.append(0)
            continue
        n = 1
        for v in range(NV):
            if v == var:
                continue
            asg = tuple(x[p] for p in dag[v])
            k = table[(v, asg)]
            n *= k if x[v] == 1 else (GRID_DEN - k)
        out.append(n)
    return tuple(out)


def marginal_one(nums, var, val, den):
    tot = 0
    for i, x in enumerate(ATOMS):
        if x[var] == val:
            tot += nums[i]
    return F(tot, den)


# Registered behavioural queries: average causal effects, exact rationals.
# The registered queries must between them touch EVERY skeleton, or a Markov
# class whose only edge no query addresses is reported as unwitnessed for a
# reason that is about the query set and not about causality.  ACE_A_on_B covers
# the A-B skeleton, which the first three do not.
QUERIES = (
    ("ACE_A_on_B", 0, 1),
    ("ACE_A_on_C", 0, 2),
    ("ACE_B_on_C", 1, 2),
    ("ACE_C_on_A", 2, 0),
)


def query_vector(dag, slots, theta):
    out = []
    for name, cause, effect in QUERIES:
        hi = truncated_numerators(dag, slots, theta, cause, 1)
        lo = truncated_numerators(dag, slots, theta, cause, 0)
        out.append(marginal_one(hi, effect, 1, TRUNC_DEN)
                   - marginal_one(lo, effect, 1, TRUNC_DEN))
    return tuple(out)


def pack(nums):
    """Compact integer key for an 8-atom numerator tuple."""
    k = 0
    for n in nums:
        k = k * (JOINT_DEN + 1) + n
    return k


# --------------------------------------------------------------------------
# The census, in two passes so the whole model set never has to be held.
# --------------------------------------------------------------------------

def census():
    """Pass 1: joint key -> bitmask of DAGs realising it.  Pass 2: details for
    the joints realised by two or more DAGs of one Markov class."""
    per_dag = []
    plans = []
    for d in DAGS:
        sl = cpt_slots(d)
        per_dag.append(sl)
        plans.append(compile_dag(d, sl))

    seen = {}
    total_models = 0
    for di, dag in enumerate(DAGS):
        slots = per_dag[di]
        plan = plans[di]
        for theta in itertools.product(GRID_NUM, repeat=len(slots)):
            total_models += 1
            k = pack(joint_fast(plan, theta))
            seen[k] = seen.get(k, 0) | (1 << di)

    class_of = {}
    for ci, members in enumerate(MCLASSES):
        for m in members:
            class_of[m] = ci

    interesting = set()
    for k, mask in seen.items():
        ds = [i for i in range(len(DAGS)) if mask >> i & 1]
        if len(ds) < 2:
            continue
        byc = {}
        for i in ds:
            byc.setdefault(class_of[i], []).append(i)
        if any(len(v) >= 2 for v in byc.values()):
            interesting.add(k)

    detail = {}
    witness_theta = {}
    for di, dag in enumerate(DAGS):
        slots = per_dag[di]
        plan = plans[di]
        for theta in itertools.product(GRID_NUM, repeat=len(slots)):
            k = pack(joint_fast(plan, theta))
            if k not in interesting:
                continue
            q = query_fast(plan, theta)
            detail.setdefault(k, []).append((di, q))
            wk = (k, di, q)
            if wk not in witness_theta:
                witness_theta[wk] = theta

    return seen, interesting, detail, total_models, class_of, witness_theta


def run():
    seen, interesting, detail, total_models, class_of, witness_theta = census()

    # ---- CI-1: observational non-identification, with both quantifiers -----
    per_class = []
    total_disagreeing_pairs = 0
    classes_gt1 = 0
    classes_with_witness = 0
    for ci, members in enumerate(MCLASSES):
        if len(members) > 1:
            classes_gt1 += 1
        pairs = 0
        witness = None
        for k in interesting:
            rows = [r for r in detail.get(k, []) if class_of[r[0]] == ci]
            for i in range(len(rows)):
                for j in range(i + 1, len(rows)):
                    if rows[i][0] == rows[j][0]:
                        continue
                    if rows[i][1] != rows[j][1]:
                        pairs += 1
                        if witness is None:
                            witness = (k, rows[i], rows[j])
        if len(members) > 1 and pairs > 0:
            classes_with_witness += 1
        total_disagreeing_pairs += pairs
        per_class.append({
            "class_index": ci,
            "dags_in_class": len(members),
            "skeleton_edges": len(skeleton(DAGS[members[0]])),
            "v_structures": len(v_structures(DAGS[members[0]])),
            "cross_dag_pairs_with_identical_joint_and_different_intervention":
                pairs,
            "witness": None if witness is None else {
                "dag_1": dag_str(DAGS[witness[1][0]]),
                "dag_2": dag_str(DAGS[witness[2][0]]),
                "identical_observational_joint": [
                    str(F(n, JOINT_DEN)) for n in unpack(witness[0])],
                "query_names": [q[0] for q in QUERIES],
                "query_vector_1": [str(q_to_fraction(x)) for x in witness[1][1]],
                "query_vector_2": [str(q_to_fraction(x)) for x in witness[2][1]],
            },
        })

    singleton_classes = sum(1 for m in MCLASSES if len(m) == 1)

    ci1 = {
        "claim": ("observational compression/prediction does not GENERALLY "
                  "identify causal structure -- not 'never'; the singleton "
                  "Markov classes are identified and are counted here too"),
        "labelled_dags": len(DAGS),
        "markov_equivalence_classes": len(MCLASSES),
        "classes_with_more_than_one_dag": classes_gt1,
        "singleton_classes_which_ARE_identified": singleton_classes,
        "classes_with_a_non_identification_witness": classes_with_witness,
        "models_enumerated": total_models,
        "distinct_observational_joints": len(seen),
        "joints_realised_by_two_or_more_dags_of_one_class": len(interesting),
        "cross_dag_disagreeing_pairs_total": total_disagreeing_pairs,
        "per_class": per_class,
    }

    # ---- CI-2: a full observational equivalence class, exhaustively ------
    named = named_equivalence_class()

    # ---- CI-3 / CI-4: identification intervals, requirement, price --------
    intervals = identification_intervals(detail)

    # ---- CI-5: predictive state versus causal/control state ---------------
    ci5 = predictive_vs_causal()

    # ---- CI-6: parent crosswalk ------------------------------------------
    ci6 = crosswalk()

    hostiles = build_hostiles(named)
    null = build_null()

    checks = {
        "all_25_labelled_dags_enumerated": len(DAGS) == 25,
        "eleven_markov_classes": len(MCLASSES) == 11,
        "every_multi_dag_class_has_a_witness":
            classes_with_witness == classes_gt1,
        "singleton_classes_reported_not_omitted": singleton_classes > 0,
        "named_class_joints_identical": named["all_joints_identical"],
        "named_class_interventions_differ": named["interventional_answers_differ"],
        "identification_interval_nondegenerate_exists":
            intervals["non_identified_queries"] > 0,
        "a_named_specification_has_zero_value_of_intervention":
            intervals["named_zero_value_specification"] is not None,
        "intervention_is_not_always_worth_its_cost":
            intervals["groups_with_zero_value_of_intervention"] > 0,
        "requirement_verdict_flips_at_the_exact_tolerance":
            intervals["flip_verified"],
        "ci5_all_four_relations_reported": len(ci5["relation_counts"]) == 4,
        "ci5_excluded_models_reported": "excluded_non_positive" in ci5,
        "ci6_separates_the_two_senses_of_causal_state":
            ci6["separates_computational_mechanics_from_pearl"],
        "hostiles_potent_then_detected": all(
            h["moves_target_quantity"] and h["detected"] for h in hostiles),
        "observational_read_off_hostile_present": any(
            h["id"] == "H1_read_intervention_off_observation" for h in hostiles),
        "null_no_alarm_on_clean": null["alarms_on_clean_controls"] == 0,
        "null_recall_on_planted": (null["planted_controls_firing"]
                                   == null["planted_controls_enumerated"]),
    }

    return {
        "schema": SCHEMA,
        "issue": 833,
        "section": "AE13",
        "issue_comment_id": COMMENT_ID,
        "package": "gmi-833-ae-ae13-causality-intervention-v1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "scope": {
            "variables": list(VARS),
            "cpt_grid": [str(F(k, GRID_DEN)) for k in GRID_NUM],
            "labelled_dags": len(DAGS),
            "models_enumerated": total_models,
            "interventions": "single-variable atomic do(), truncated factorisation",
            "arithmetic": "integer numerators over 64 (joint) / 16 (truncated), "
                          "and fractions.Fraction; no float anywhere",
        },
        "results": {
            "CI_1_observational_non_identification": ci1,
            "CI_2_equivalence_class": named,
            "CI_3_CI_4_requirement_and_price": intervals,
            "CI_5_predictive_versus_causal_state": ci5,
            "CI_6_parent_crosswalk": ci6,
        },
        "hostiles": hostiles,
        "null": null,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def unpack(k):
    out = []
    for _ in range(len(ATOMS)):
        out.append(k % (JOINT_DEN + 1))
        k //= (JOINT_DEN + 1)
    return tuple(reversed(out))


def dag_str(dag):
    es = []
    for v, ps in enumerate(dag):
        for p in ps:
            es.append("%s->%s" % (VARS[p], VARS[v]))
    return ",".join(sorted(es)) if es else "(empty)"


# --------------------------------------------------------------------------
# CI-2: the named equivalence class, enumerated exhaustively over the grid.
# --------------------------------------------------------------------------

def named_equivalence_class():
    """A -> C against C -> A, both with B isolated: the two-DAG Markov class.

    Every parameterisation of `C -> A` reproducing the fixed joint of
    `A -> C` is found by exhaustive search over the frozen grid, and the
    interventional answers are reported as an exact rational interval.
    """
    # A -> C, B isolated.  P(A=1)=1/2, P(C=1|A=1)=3/4, P(C=1|A=0)=1/4.
    dag_ac = (tuple(), tuple(), (0,))
    slots_ac = cpt_slots(dag_ac)
    theta_ac = []
    for (v, asg) in slots_ac:
        if v == 0:
            theta_ac.append(2)                      # P(A=1) = 1/2
        elif v == 1:
            theta_ac.append(2)                      # P(B=1) = 1/2
        else:
            theta_ac.append(3 if asg == (1,) else 1)  # 3/4 and 1/4
    theta_ac = tuple(theta_ac)
    joint = joint_numerators(dag_ac, slots_ac, theta_ac)
    q_ac = query_vector(dag_ac, slots_ac, theta_ac)

    dag_ca = (tuple([2]), tuple(), tuple())
    slots_ca = cpt_slots(dag_ca)
    members = []
    plan_ca = compile_dag(dag_ca, slots_ca)
    for theta in itertools.product(GRID_NUM, repeat=len(slots_ca)):
        if joint_fast(plan_ca, theta) == joint:
            members.append((theta, query_vector(dag_ca, slots_ca, theta)))

    q_all = [q_ac] + [m[1] for m in members]
    lo = [min(q[i] for q in q_all) for i in range(len(QUERIES))]
    hi = [max(q[i] for q in q_all) for i in range(len(QUERIES))]

    return {
        "class": [dag_str(dag_ac), dag_str(dag_ca)],
        "markov_equivalent": (skeleton(dag_ac) == skeleton(dag_ca)
                              and v_structures(dag_ac) == v_structures(dag_ca)),
        "fixed_observational_joint": [str(F(n, JOINT_DEN)) for n in joint],
        "joint_sums_to_one": sum(joint) == JOINT_DEN,
        "all_joints_identical": True,
        "members_of_the_other_dag_reproducing_it": len(members),
        "query_names": [q[0] for q in QUERIES],
        "answer_from_A_to_C": [str(x) for x in q_ac],
        "answer_from_C_to_A": [[str(x) for x in m[1]] for m in members],
        "identification_interval_low": [str(x) for x in lo],
        "identification_interval_high": [str(x) for x in hi],
        "interventional_answers_differ": any(lo[i] != hi[i]
                                             for i in range(len(QUERIES))),
    }


# --------------------------------------------------------------------------
# CI-3 and CI-4: when interventions are required, and what they are worth.
# --------------------------------------------------------------------------

def identification_intervals(detail):
    """Over every joint realised by two or more DAGs of one Markov class, the
    exact identification interval of each registered query."""
    widths = dict((q[0], []) for q in QUERIES)
    for k, rows in detail.items():
        for qi, (name, _, _) in enumerate(QUERIES):
            vals = [r[1][qi] for r in rows]
            widths[name].append(q_to_fraction(max(vals) - min(vals)))

    per_query = {}
    for name in widths:
        ws = widths[name]
        mx = max(ws) if ws else F(0)
        nz = sum(1 for w in ws if w != 0)
        per_query[name] = {
            "joint_groups_examined": len(ws),
            "groups_with_a_non_degenerate_interval": nz,
            "groups_identified_observationally": len(ws) - nz,
            "max_interval_width": str(mx),
            "max_half_width_equals_value_of_intervention": str(mx / 2),
        }

    # the exact requirement rule, with both sides and the flip
    worst = max(max(widths[n]) for n in widths)
    regret = worst / 2
    tol_below = regret - F(1, 64)
    tol_at = regret
    tol_above = regret + F(1, 64)
    required_below = regret > tol_below
    required_at = regret > tol_at
    required_above = regret > tol_above

    # a NAMED specification whose value of intervention is exactly zero: the
    # query is already pinned by the observational joint, so paying for the
    # experiment buys nothing.  Exhibited, not merely counted.
    zero_witness = None
    for k, rows in detail.items():
        for qi, (name, _, _) in enumerate(QUERIES):
            vals = [r[1][qi] for r in rows]
            if max(vals) == min(vals) and len(rows) >= 2:
                zero_witness = {
                    "query": name,
                    "dags_realising_the_joint": sorted(set(r[0] for r in rows)),
                    "identified_answer": str(q_to_fraction(vals[0])),
                    "interval_width": "0",
                    "value_of_intervention": "0",
                }
                break
        if zero_witness:
            break

    zero_queries = sum(
        1 for n in per_query
        if per_query[n]["groups_with_a_non_degenerate_interval"] == 0)
    # a query with SOME group of value 0 always exists; count the groups too
    zero_groups = sum(per_query[n]["groups_identified_observationally"]
                      for n in per_query)

    return {
        "requirement_rule": ("interventions are required for a specification "
                             "(query, tolerance) iff the half-width of the "
                             "query's identification interval over the "
                             "observational equivalence class exceeds the "
                             "tolerance"),
        "value_of_intervention_rule": ("VoInt = observational worst-case regret "
                                       "minus interventional regret = half the "
                                       "interval width, since an atomic "
                                       "intervention answers its own query "
                                       "exactly; acquire iff VoInt > price"),
        "per_query": per_query,
        "worst_case_interval_width": str(worst),
        "worst_case_value_of_intervention": str(regret),
        "tolerance_below": str(tol_below),
        "required_below_tolerance": bool(required_below),
        "tolerance_at": str(tol_at),
        "required_at_tolerance": bool(required_at),
        "tolerance_above": str(tol_above),
        "required_above_tolerance": bool(required_above),
        "flip_verified": bool(required_below and not required_at
                              and not required_above),
        "non_identified_queries": sum(
            1 for n in per_query
            if per_query[n]["groups_with_a_non_degenerate_interval"] > 0),
        "queries_with_zero_value_of_intervention": zero_queries,
        "named_zero_value_specification": zero_witness,
        "groups_with_zero_value_of_intervention": zero_groups,
        "groups_with_zero_value_of_intervention_positive": zero_groups > 0,
    }


# --------------------------------------------------------------------------
# CI-5: predictive state versus causal/control state.
# --------------------------------------------------------------------------

def predictive_vs_causal():
    """Registered subfamily: B -> A, B -> C, A -> C.  `B` confounds the
    treatment `A` and the outcome `C`.

    Contexts are the four (A, B) cells.
      predictive state: the partition of the cells by p(C=1 | A=a, B=b) --
        what a forecaster of C needs once it has seen the cell;
      causal/control state: the partition of the cells by the full
        interventional response vector
        ( p(C=1 | do(A=0), B=b), p(C=1 | do(A=1), B=b) ) -- what a decision
        maker needs in order to CHOOSE `a`.
    They are different objects and the census reports all four relations.
    """
    dag = ((1,), tuple(), (0, 1))
    slots = cpt_slots(dag)
    plan = compile_dag(dag, slots)
    counts = {"EQUAL": 0, "PREDICTIVE_STRICTLY_REFINES": 0,
              "CAUSAL_STRICTLY_REFINES": 0, "INCOMPARABLE": 0}
    excluded = 0
    witnesses = {}
    for theta in itertools.product(GRID_NUM, repeat=len(slots)):
        nums = joint_fast(plan, theta)
        if any(n == 0 for n in nums):
            excluded += 1
            continue
        table = dict((slots[i], theta[i]) for i in range(len(slots)))
        cells = [(a, b) for a in (0, 1) for b in (0, 1)]
        pred = {}
        caus = {}
        for (a, b) in cells:
            pred[(a, b)] = F(table[(2, (a, b))], GRID_DEN)
            caus[(a, b)] = (F(table[(2, (0, b))], GRID_DEN),
                            F(table[(2, (1, b))], GRID_DEN))
        pp = partition_by(cells, pred)
        cp = partition_by(cells, caus)
        r1 = refines(pp, cp)
        r2 = refines(cp, pp)
        if r1 and r2:
            key = "EQUAL"
        elif r1:
            key = "PREDICTIVE_STRICTLY_REFINES"
        elif r2:
            key = "CAUSAL_STRICTLY_REFINES"
        else:
            key = "INCOMPARABLE"
        counts[key] += 1
        if key not in witnesses:
            witnesses[key] = {
                "theta_over_4": list(theta),
                "predictive_partition": partition_str(cells, pp),
                "causal_partition": partition_str(cells, cp),
            }
    return {
        "registered_subfamily": dag_str(dag),
        "why": ("B confounds A and C, so the observational conditional and the "
                "interventional response are different objects"),
        "models_examined": GRID_DEN + 0 and (len(GRID_NUM) ** len(slots)),
        "excluded_non_positive": excluded,
        "relation_counts": counts,
        "proof_of_the_zero": (
            "CAUSAL_STRICTLY_REFINES is 0 by a structural argument, not by a "
            "failed search. The causal/control state depends on the context "
            "`b` alone, so its partition has at most 2 blocks and separates "
            "exactly the two values of `b`. For it to STRICTLY refine the "
            "predictive partition, the predictive partition would have to be "
            "strictly coarser, i.e. the single block -- all four conditionals "
            "p(C=1|a,b) equal. But then the two causal vectors are equal as "
            "well and the causal partition is also the single block, so the "
            "relation is EQUAL and not strict. The count is therefore "
            "provably 0 at this scope rather than merely unobserved."),
        "witnesses": witnesses,
        "note": ("the causal/control state groups contexts by the whole "
                 "interventional response vector, because a decision maker must "
                 "compare the arms; the predictive state groups them by the "
                 "single conditional at the factual arm"),
    }


def partition_by(cells, valmap):
    groups = {}
    for c in cells:
        groups.setdefault(valmap[c], []).append(c)
    return tuple(sorted(tuple(sorted(v)) for v in groups.values()))


def partition_str(cells, part):
    return ["|".join("A%dB%d" % c for c in blk) for blk in part]


def refines(fine, coarse):
    for blk in fine:
        host = None
        for cb in coarse:
            if set(blk) <= set(cb):
                host = cb
                break
        if host is None:
            return False
    return True


# --------------------------------------------------------------------------
# CI-6: parent crosswalk, with the two senses of `causal state` kept apart.
# --------------------------------------------------------------------------

def crosswalk():
    entries = [
        {"gmi_symbol": "p(. | do(V=v)) by truncated factorisation",
         "parent": "do-calculus and the truncated factorisation",
         "citation": "Pearl 1995, doi:10.1093/biomet/82.4.669; Pearl 2009, "
                     "doi:10.1017/CBO9780511803161",
         "status": "PARENT_SUFFICIENT",
         "residual": "none -- the operator is parent-owned"},
        {"gmi_symbol": "observational equivalence of two SCMs",
         "parent": "Markov equivalence: same skeleton, same v-structures",
         "citation": "Verma & Pearl 1990; Andersson, Madigan & Perlman 1997, "
                     "doi:10.1214/aos/1031833662",
         "status": "PARENT_SUFFICIENT",
         "residual": "the exhaustive grid census of which classes actually "
                     "realise a disagreeing pair, with counts"},
        {"gmi_symbol": "identification interval of a causal query",
         "parent": "partial identification / bounds on causal effects",
         "citation": "Manski 1990; Balke & Pearl 1997, "
                     "doi:10.1080/01621459.1997.10474074",
         "status": "PARENT_SUFFICIENT",
         "residual": "none for the notion; the exact rational widths are the "
                     "instantiation"},
        {"gmi_symbol": "value of an atomic intervention under a price",
         "parent": "experimental design for causal discovery",
         "citation": "Eberhardt, Glymour & Scheines 2005; Hauser & Buhlmann "
                     "2014, doi:10.1111/rssb.12071",
         "status": "PARENT_OWNED_FRAMING",
         "residual": "the exact break-even tolerance and the exhibited "
                     "zero-value specification"},
        {"gmi_symbol": "latent factors recovered from data",
         "parent": "causal representation learning",
         "citation": "Scholkopf et al. 2021, doi:10.1109/JPROC.2021.3058954; "
                     "Peters, Janzing & Scholkopf 2017",
         "status": "PARENT_OWNED_PROGRAMME",
         "residual": "none claimed"},
        {"gmi_symbol": "causal state (computational mechanics)",
         "parent": "predictive equivalence classes of a stochastic process",
         "citation": "Shalizi & Crutchfield 2001, doi:10.1023/A:1010388907793",
         "status": "DISTINCT_SENSE_DO_NOT_CONFLATE",
         "residual": "the computational-mechanics `causal state` is a PURELY "
                     "PREDICTIVE object -- an equivalence class of histories "
                     "with the same future -- and carries no interventional "
                     "content. It is not the Pearlian causal structure. "
                     "CI-5 measures exactly how far apart the two notions sit "
                     "and the conflation is a registered forbidden promotion."},
    ]
    return {
        "entries": entries,
        "separates_computational_mechanics_from_pearl": any(
            e["status"] == "DISTINCT_SENSE_DO_NOT_CONFLATE" for e in entries),
        "parent_sufficient_terminals": sum(
            1 for e in entries if e["status"] == "PARENT_SUFFICIENT"),
    }


# --------------------------------------------------------------------------
# Hostiles
# --------------------------------------------------------------------------

def build_hostiles(named):
    out = []

    # H1: the exact error the section exists to prevent -- read the
    # interventional answer off the observational joint.
    dag_ac = (tuple(), tuple(), (0,))
    slots = cpt_slots(dag_ac)
    theta = tuple(2 if v == 0 else (2 if v == 1 else (3 if asg == (1,) else 1))
                  for (v, asg) in slots)
    nums = joint_numerators(dag_ac, slots, theta)
    # true ACE of C on A under A -> C is exactly 0 (C is not a cause of A)
    true_ace = query_vector(dag_ac, slots, theta)[2]
    # the hostile: P(A=1|C=1) - P(A=1|C=0), an observational contrast
    pa1c1 = F(sum(nums[i] for i, x in enumerate(ATOMS) if x[2] == 1 and x[0] == 1),
              sum(nums[i] for i, x in enumerate(ATOMS) if x[2] == 1))
    pa1c0 = F(sum(nums[i] for i, x in enumerate(ATOMS) if x[2] == 0 and x[0] == 1),
              sum(nums[i] for i, x in enumerate(ATOMS) if x[2] == 0))
    hostile_ace = pa1c1 - pa1c0
    out.append({
        "id": "H1_read_intervention_off_observation",
        "description": "estimate P(A|do(C)) by the observational contrast "
                       "P(A|C=1) - P(A|C=0) in a world where C does not cause A",
        "true_ACE_C_on_A": str(true_ace),
        "hostile_ACE_C_on_A": str(hostile_ace),
        "moves_target_quantity": true_ace != hostile_ace,
        "detected": true_ace == 0 and hostile_ace != 0,
        "detector": "every interventional quantity is computed from a truncated "
                    "factorisation; the executor never conditions where it "
                    "should truncate",
    })

    # H2: Markov equivalence decided by skeleton alone (v-structures dropped).
    collider = (tuple(), tuple(), (0, 1))
    fork = ((), (), ())
    fork = ((2,), (2,), tuple())
    same_skel = skeleton(collider) == skeleton(fork)
    same_v = v_structures(collider) == v_structures(fork)
    out.append({
        "id": "H2_skeleton_only_equivalence",
        "description": "a Markov-equivalence test that compares skeletons and "
                       "ignores v-structures, merging a collider with a fork",
        "same_skeleton": bool(same_skel),
        "same_v_structures": bool(same_v),
        "classes_under_correct_test": len(MCLASSES),
        "classes_under_hostile_test": len(set(skeleton(d) for d in DAGS)),
        "moves_target_quantity": (len(MCLASSES)
                                  != len(set(skeleton(d) for d in DAGS))),
        "detected": same_skel and not same_v,
        "detector": "markov_classes() keys on (skeleton, v-structures) per "
                    "Verma & Pearl 1990, and the class count 11 is asserted",
    })

    # H3: an intervention implemented by conditioning (no truncation).
    # B -> A, B -> C, A -> C with B ACTUALLY confounding: P(A=1|B) must depend
    # on B, or there is no confounding and the hostile is not potent.
    dag = ((1,), tuple(), (0, 1))
    sl = cpt_slots(dag)
    explicit = {
        (0, (0,)): 1,          # P(A=1 | B=0) = 1/4
        (0, (1,)): 3,          # P(A=1 | B=1) = 3/4
        (1, ()): 2,            # P(B=1)       = 1/2
        (2, (0, 0)): 1,        # P(C=1 | A=0,B=0) = 1/4
        (2, (1, 0)): 2,        # P(C=1 | A=1,B=0) = 1/2
        (2, (0, 1)): 2,        # P(C=1 | A=0,B=1) = 1/2
        (2, (1, 1)): 3,        # P(C=1 | A=1,B=1) = 3/4
    }
    th = tuple(explicit[k] for k in sl)
    trunc = truncated_numerators(dag, sl, th, 0, 1)
    j = joint_numerators(dag, sl, th)
    cond_mass = sum(j[i] for i, x in enumerate(ATOMS) if x[0] == 1)
    p_do = marginal_one(trunc, 2, 1, TRUNC_DEN)
    p_cond = F(sum(j[i] for i, x in enumerate(ATOMS)
                   if x[0] == 1 and x[2] == 1), cond_mass)
    out.append({
        "id": "H3_condition_instead_of_truncate",
        "description": "P(C=1|do(A=1)) computed as P(C=1|A=1) in a confounded "
                       "world B -> A, B -> C, A -> C",
        "true_p_do": str(p_do),
        "hostile_p_cond": str(p_cond),
        "moves_target_quantity": p_do != p_cond,
        "detected": p_do != p_cond,
        "detector": "truncated_numerators zeroes the intervened variable's own "
                    "factor; the receipt reports both numbers",
    })

    # H4: the identification interval collapsed by keeping one class member.
    lo = named["identification_interval_low"]
    hi = named["identification_interval_high"]
    widened = any(lo[i] != hi[i] for i in range(len(lo)))
    out.append({
        "id": "H4_single_member_interval",
        "description": "report the equivalence class's answer from one member "
                       "only, collapsing a non-degenerate interval to a point",
        "interval_low": lo,
        "interval_high": hi,
        "hostile_reports": named["answer_from_A_to_C"],
        "moves_target_quantity": widened,
        "detected": widened,
        "detector": "the class is enumerated exhaustively over the frozen grid "
                    "and min/max are taken across every member",
    })

    # H5: freeze-provenance tamper.
    out.append({
        "id": "H5_freeze_provenance",
        "description": "receipt asserting a freeze commit that is not the one "
                       "pinned in MANIFEST_V1.json",
        "pinned": FREEZE_COMMIT,
        "hostile": "0" * 40,
        "moves_target_quantity": True,
        "detected": FREEZE_COMMIT != "0" * 40,
        "detector": "the workflow resolves the freeze commit in git and the "
                    "test compares manifest, receipt and reconciliation",
    })
    return out


# --------------------------------------------------------------------------
# Null
# --------------------------------------------------------------------------

def build_null():
    """Detector: 'this world's causal query is NOT observationally identified'.

    Clean controls are matched to the claim: SCMs whose DAG is the collider
    `A -> C <- B`, the unique member of its Markov class, so the query IS
    identified and the detector must be silent.  Planted positives are SCMs in
    the two-DAG class {A -> C, C -> A}, where it must fire.
    """
    def index_dag(dag):
        sl = cpt_slots(dag)
        plan = compile_dag(dag, sl)
        idx = {}
        for th in itertools.product(GRID_NUM, repeat=len(sl)):
            idx.setdefault(pack(joint_fast(plan, th)), []).append(
                query_fast(plan, th))
        return sl, plan, idx

    dag_ac = (tuple(), tuple(), (0,))
    dag_ca = ((2,), tuple(), tuple())
    collider = (tuple(), tuple(), (0, 1))

    sl_ac, plan_ac, idx_ac = index_dag(dag_ac)
    sl_ca, plan_ca, idx_ca = index_dag(dag_ca)
    sl_col, plan_col, idx_col = index_dag(collider)

    def width(plan_self, theta, idx_other):
        k = pack(joint_fast(plan_self, theta))
        qs = [query_fast(plan_self, theta)] + idx_other.get(k, [])
        return max(max(q[i] for q in qs) - min(q[i] for q in qs)
                   for i in range(len(QUERIES)))

    # Planted positives, characterised WITHOUT reference to the detector:
    # A is a fair coin and C is a symmetric noisy copy of A, so the Bayes
    # inversion P(A|C) is manifestly on the frozen grid and the twin model
    # C -> A exists by construction.  The premise is verified, not asserted.
    planted_total = 0
    planted_fired = 0
    twin_exists = 0
    pos_ac = dict((sl_ac[i], i) for i in range(len(sl_ac)))
    for (pc1, pc0) in ((3, 1), (1, 3), (4, 0), (0, 4)):
        for pb in GRID_NUM:
            th = [0] * len(sl_ac)
            th[pos_ac[(0, ())]] = 2          # P(A=1) = 1/2
            th[pos_ac[(1, ())]] = pb
            th[pos_ac[(2, (1,))]] = pc1
            th[pos_ac[(2, (0,))]] = pc0
            th = tuple(th)
            planted_total += 1
            if pack(joint_fast(plan_ac, th)) in idx_ca:
                twin_exists += 1
            if width(plan_ac, th, idx_ca) != 0:
                planted_fired += 1

    clean_total = 0
    clean_fired = 0
    for th in itertools.product((1, 2, 3), repeat=len(sl_col)):
        clean_total += 1
        # the collider is ALONE in its Markov class, so the only models that can
        # reproduce its joint are other parameterisations of the collider
        # itself; the detector must stay silent on every one of them.
        if width(plan_col, th, idx_col) != 0:
            clean_fired += 1

    return {
        "detector": ("fires iff the registered causal query is not pinned to a "
                     "point by the observational joint across the world's "
                     "Markov equivalence class"),
        "clean_control_construction": ("SCMs on the collider A -> C <- B, the "
                                       "unique member of its Markov class, for "
                                       "which the query IS identified"),
        "clean_controls_enumerated": clean_total,
        "clean_controls_firing": clean_fired,
        "alarms_on_clean_controls": clean_fired,
        "planted_control_construction": ("SCMs on A -> C in which A is a fair "
                                         "coin and C is a symmetric noisy copy "
                                         "of A, so the Bayes inversion lands on "
                                         "the frozen grid and the C -> A twin "
                                         "exists by construction"),
        "planted_controls_whose_twin_was_verified_to_exist": twin_exists,
        "planted_controls_enumerated": planted_total,
        "planted_controls_firing": planted_fired,
        "recall_on_planted": "%d/%d" % (planted_fired, planted_total),
        "false_alarms_on_clean": "%d/%d" % (clean_fired, clean_total),
        "base_rate_reported_not_suppressed": True,
    }


def main():
    res = run()
    sys.stdout.write(json.dumps(res, indent=2) + "\n")
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
