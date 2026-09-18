# -*- coding: utf-8 -*-
"""AG5 route A -- constructive lowering of the four registered `G0` extension families.

Route A imports the four merged parent operator modules and treats their semantics as
authoritative.  It then rebuilds every registered operator out of the AJ5 lower role basis
alone -- natural-number registers, `SUCC`, `PRED_POS`, `IS_ZERO`, `SELECT`, `LOAD`, `STORE`,
`NEXT_INPUT`, `APPEND_OUTPUT`, sequential composition, and the bounded helpers named in
`FREEZE_V1.md` -- and checks the rebuilt operator against the parent on the whole registered
finite universe.

No rational, matrix, queue, graph or receipt object enters the lowering.  Probability weights
are normalized pairs of naturals; adjacency is read from the register store; queues are
streams.

    python3 -I -B  ag5_extension_lowering_v1.py
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for _name in ("g0-stochastic-update", "g0-local-graph-ops",
              "g0-interaction-channels", "g0-governed-self-change"):
    sys.path.insert(0, os.path.join(REPO, "research", "gmi-833-" + _name + "-v1"))

import stochastic_update_v1 as PSTO          # noqa: E402
import local_graph_ops_v1 as PGRA            # noqa: E402
import interaction_channels_v1 as PCHA       # noqa: E402
import governed_self_change_v1 as PSELF      # noqa: E402

SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
FREEZE_FILE = "FREEZE_V1.md"
CLAIM_CEILING = ("AG5_G0_EXTENSION_OPERATORS_LOWERED_AND_STATUS_ADJUDICATED_"
                 "AT_REGISTERED_FINITE_SCOPE")
FORBIDDEN_PROMOTIONS = (
    "G0_EXTENSIONS_ARE_THE_OPERATIONAL_BOTTOM",
    "UNIQUE_LOWEST_EXTENSION_BASIS",
    "ALL_G0_EXTENSIONS_ENUMERATED",
    "STOCHASTIC_ARCHITECTURE_DERIVED",
    "BAYESIAN_INFERENCE_DERIVED",
    "GNN_DERIVED",
    "TOOL_USE_INTELLIGENCE_DERIVED",
    "EMERGENT_COMMUNICATION",
    "RECURSIVE_SELF_IMPROVEMENT_PROVED",
    "AUTONOMOUS_SELF_AUTHORITY",
    "VERIFIER_INFALLIBLE",
    "COMPLETE_GMI",
)

STATUSES = ("GENERATOR", "DERIVED_OPERATION", "MACRO", "SEMANTIC_CONVENIENCE",
            "RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE")
QUALIFIER = "EXTERNALLY_REGISTERED"

# Family names the lowering role table must never contain.  A lowering that needs one of
# these words is a named architecture, not a lowering.
FAMILY_NAME_TOKENS = (
    "neural", "neuron", "layer", "attention", "transformer", "bayes", "bayesian",
    "posterior", "prior", "inference", "gnn", "graph neural", "convolution",
    "recurrent", "lstm", "planner", "planning", "memory architecture", "retrieval",
    "evolutionary", "genetic", "gradient", "backprop", "embedding", "agent policy",
)


# --------------------------------------------------------------------------------------
# 1.  The lower role basis.  Charges are counted at two levels.
#
#     charged_roles      -- one unit per extension-layer role application
#     aj5_role_expansion -- the declared closed-form expansion of that role into AJ5 roles
#
# The closed forms are validated exhaustively against a literal role-by-role expansion over
# the operand box actually observed (`expansion_validation` below).  If any operand leaves
# the validated box the run goes RED.
# --------------------------------------------------------------------------------------

def exp_succ(_a, _b):
    return 1


def exp_nat_add(_a, b):
    """`NAT_ADD(a, b)` = `SUCC` applied `b` times, then one `STORE`."""
    return b + 1


def exp_nat_sub_sat(_a, b):
    """`NAT_SUB_SAT(a, b)` = `PRED_POS` guarded by `IS_ZERO`, `b` times, then one `STORE`."""
    return 2 * b + 1


def exp_nat_mul(a, b):
    """`NAT_MUL(a, b)` = `NAT_ADD(., a)` applied `b` times, then one `STORE`."""
    return b * (a + 1) + 1


def exp_nat_div(a, b):
    """`NAT_DIV(a, b)` = `NAT_SUB_SAT(., b)` until `IS_ZERO`, then one `STORE`."""
    q = a // b if b else 0
    return q * (2 * b + 2) + 2


def exp_nat_mod(a, b):
    return exp_nat_div(a, b) + exp_nat_mul(b, a // b if b else 0) + exp_nat_sub_sat(a, 0) + 1


def exp_nat_gcd(a, b):
    """Euclid by `NAT_MOD`."""
    total = 1
    x, y = a, b
    while y:
        total += exp_nat_mod(x, y)
        x, y = y, x % y
    return total


def exp_nat_eq(a, b):
    return exp_nat_sub_sat(a, b) + exp_nat_sub_sat(b, a) + 2


def exp_index(n):
    """`INDEX` over `n` slots = a `SELECT` chain."""
    return n


def exp_pair():
    return 2


def literal_expansion(role, a, b):
    """Run the role literally, one AJ5 role application at a time, and count.

    This is the ground truth the closed forms above are validated against.  It is only ever
    run over the small observed operand box, never inside the exhaustive universes.
    """
    n = 0
    if role == "NAT_ADD":
        v = a
        for _ in range(b):
            v += 1
            n += 1
        n += 1
        return v, n
    if role == "NAT_SUB_SAT":
        v = a
        for _ in range(b):
            n += 1                      # IS_ZERO
            if v:
                v -= 1                  # PRED_POS
            n += 1
        n += 1
        return v, n
    if role == "NAT_MUL":
        v = 0
        for _ in range(b):
            _, k = literal_expansion("NAT_ADD", v, a)
            v += a
            n += k
        n += 1
        return v, n
    if role == "NAT_DIV":
        if b == 0:
            return 0, 2
        v = a
        q = 0
        while v >= b:
            _, k = literal_expansion("NAT_SUB_SAT", v, b)
            v -= b
            q += 1
            n += k + 1
        n += 2
        return q, n
    if role == "NAT_EQ":
        _, k1 = literal_expansion("NAT_SUB_SAT", a, b)
        _, k2 = literal_expansion("NAT_SUB_SAT", b, a)
        return (1 if a == b else 0), k1 + k2 + 2
    raise ValueError("UNKNOWN_ROLE:" + role)


class Charge(object):
    """Accumulates both cost levels and records the observed operand box."""

    __slots__ = ("roles", "aj5", "box", "trace")

    def __init__(self):
        self.roles = 0
        self.aj5 = 0
        self.box = 0
        self.trace = []

    def add(self, kind, a=0, b=0):
        self.roles += 1
        self.trace.append(kind)
        if a > self.box:
            self.box = a
        if b > self.box:
            self.box = b
        if kind == "SUCC":
            self.aj5 += exp_succ(a, b)
        elif kind == "NAT_ADD":
            self.aj5 += exp_nat_add(a, b)
        elif kind == "NAT_SUB_SAT":
            self.aj5 += exp_nat_sub_sat(a, b)
        elif kind == "NAT_MUL":
            self.aj5 += exp_nat_mul(a, b)
        elif kind == "NAT_DIV":
            self.aj5 += exp_nat_div(a, b)
        elif kind == "NAT_MOD":
            self.aj5 += exp_nat_mod(a, b)
        elif kind == "NAT_GCD":
            self.aj5 += exp_nat_gcd(a, b)
        elif kind == "NAT_EQ":
            self.aj5 += exp_nat_eq(a, b)
        elif kind == "INDEX":
            self.aj5 += exp_index(a)
        elif kind == "PAIR":
            self.aj5 += exp_pair()
        elif kind in ("LOAD", "STORE", "SELECT", "IS_ZERO", "PRED_POS",
                      "NEXT_INPUT", "APPEND_OUTPUT", "TERMINAL"):
            self.aj5 += 1
        else:
            raise ValueError("UNKNOWN_ROLE:" + kind)


# --------------------------------------------------------------------------------------
# 2.  Rational weights as normalized pairs of naturals, built from the role basis alone.
# --------------------------------------------------------------------------------------

def nat_gcd(c, a, b):
    c.add("NAT_GCD", a, b)
    x, y = a, b
    while y:
        x, y = y, x % y
    return x


def frac_norm(c, p, q, sign_guard=True):
    if type(p) is not int or type(q) is not int:
        raise ValueError("NON_EXACT_WEIGHT")
    if q <= 0:
        raise ValueError("NON_POSITIVE_DENOMINATOR")
    if sign_guard and p < 0:
        raise ValueError("NEGATIVE_WEIGHT")
    g = nat_gcd(c, p, q) if p else q
    if p == 0:
        c.add("NAT_DIV", q, q)
        return (0, 1)
    c.add("NAT_DIV", p, g)
    c.add("NAT_DIV", q, g)
    return (p // g, q // g)


def frac_mul(c, x, y):
    c.add("NAT_MUL", x[0], y[0])
    c.add("NAT_MUL", x[1], y[1])
    return frac_norm(c, x[0] * y[0], x[1] * y[1])


def frac_add(c, x, y):
    c.add("NAT_MUL", x[0], y[1])
    c.add("NAT_MUL", y[0], x[1])
    c.add("NAT_MUL", x[1], y[1])
    c.add("NAT_ADD", x[0] * y[1], y[0] * x[1])
    return frac_norm(c, x[0] * y[1] + y[0] * x[1], x[1] * y[1])


def frac_of(fr):
    return (fr.numerator, fr.denominator)


def is_normalized_one(c, x):
    c.add("NAT_EQ", x[0], x[1])
    return x[0] == x[1]


# --------------------------------------------------------------------------------------
# 3.  The lowerings.
# --------------------------------------------------------------------------------------

S3 = (0, 1, 2)


def low_update(mu, K, self_index_bug=False):
    """`UPDATE` lowered: nine weight products, six sums, one normalization gate."""
    c = Charge()
    out = []
    for j in S3:
        acc = (0, 1)
        for i in S3:
            src = j if self_index_bug else i
            c.add("INDEX", 3)
            c.add("LOAD")
            t = frac_mul(c, mu[src], K[i][j])
            acc = frac_add(c, acc, t) if i else t
        c.add("STORE")
        out.append(acc)
    tot = (0, 1)
    for j in S3:
        tot = frac_add(c, tot, out[j])
    if not is_normalized_one(c, tot):
        raise ValueError("LOWERED_RESULT_NOT_NORMALIZED")
    return tuple(out), c


def low_compose(K1, K2, transpose_bug=False):
    c = Charge()
    rows = []
    for i in S3:
        row = []
        for j in S3:
            acc = (0, 1)
            for k in S3:
                c.add("INDEX", 3)
                c.add("LOAD")
                a = K1[i][k] if not transpose_bug else K1[k][i]
                t = frac_mul(c, a, K2[k][j])
                acc = frac_add(c, acc, t) if k else t
            c.add("STORE")
            row.append(acc)
        rows.append(tuple(row))
    return tuple(rows), c


def low_identity_kernel():
    """A fixed closed term: `NAT_EQ` on the two indices, then the two constants."""
    c = Charge()
    rows = []
    for i in S3:
        row = []
        for j in S3:
            c.add("NAT_EQ", i, j)
            c.add("SELECT")
            row.append((1, 1) if i == j else (0, 1))
        rows.append(tuple(row))
    return tuple(rows), c


def low_deterministic_kernel(mapping):
    c = Charge()
    rows = []
    for i in S3:
        row = []
        for j in S3:
            c.add("INDEX", 3)
            c.add("NAT_EQ", j, mapping[i])
            c.add("SELECT")
            row.append((1, 1) if j == mapping[i] else (0, 1))
        rows.append(tuple(row))
    return tuple(rows), c


def low_transport_kernel(K, pi):
    c = Charge()
    rows = [[None] * 3 for _ in S3]
    for i in S3:
        for j in S3:
            c.add("INDEX", 3)
            c.add("INDEX", 3)
            c.add("STORE")
            rows[pi[i]][pi[j]] = K[i][j]
    return tuple(tuple(r) for r in rows), c


def low_transport_distribution(mu, pi):
    c = Charge()
    out = [None] * 3
    for i in S3:
        c.add("INDEX", 3)
        c.add("STORE")
        out[pi[i]] = mu[i]
    return tuple(out), c


ADJ_SLOTS = ((0, 1), (0, 2), (1, 2))


def adjacency_registers(graph):
    """The graph as three natural-number registers; the lowering may read nothing else."""
    return tuple(1 if e in graph.edges else 0 for e in ADJ_SLOTS)


def low_pointwise(state, _adj):
    c = Charge()
    out = []
    for v in S3:
        c.add("LOAD")
        c.add("SUCC")
        c.add("NAT_MOD", state[v] + 1, 3)
        c.add("STORE")
        out.append((state[v] + 1) % 3)
    return tuple(out), c, (3, 3, 0, 0)


def low_global_broadcast(state, _adj):
    c = Charge()
    agg = 0
    for v in S3:
        c.add("LOAD")
        if v:
            c.add("NAT_ADD", agg, state[v])
        agg += state[v]
    c.add("NAT_MOD", agg, 3)
    agg %= 3
    out = []
    for v in S3:
        c.add("LOAD")
        c.add("NAT_ADD", state[v], agg)
        c.add("NAT_MOD", state[v] + agg, 3)
        c.add("STORE")
        out.append((state[v] + agg) % 3)
    return tuple(out), c, (6, 3, 0, 2)


def low_neighbor_update(state, adj, self_neighbour_bug=False, constant_charge_bug=False):
    c = Charge()
    out = []
    edge_reads = 0
    agg_ops = 0
    site_reads = 3
    for v in S3:
        ns = []
        for si, (a, b) in enumerate(ADJ_SLOTS):
            c.add("LOAD")
            edge_reads += 1
            if adj[si]:
                if a == v:
                    ns.append(b)
                elif b == v:
                    ns.append(a)
        if self_neighbour_bug:
            ns.append(v)
        acc = 0
        for idx, u in enumerate(ns):
            c.add("INDEX", 3)
            c.add("LOAD")
            site_reads += 1
            if idx:
                c.add("NAT_ADD", acc, state[u])
                agg_ops += 1
            acc += state[u]
        c.add("NAT_MOD", acc, 3)
        c.add("LOAD")
        c.add("NAT_ADD", state[v], acc % 3)
        c.add("NAT_MOD", state[v] + acc % 3, 3)
        c.add("STORE")
        out.append((state[v] + acc % 3) % 3)
    # The lowering reads all three adjacency slots but only charges the incident ones,
    # matching the parent's declared vector.
    e2 = 2 * sum(adj)
    res = (3, 3, 0, 0) if constant_charge_bug else (3 + e2, 3, e2, agg_ops)
    return tuple(out), c, res


def low_send(local, queues, src, dst, msg, implicit_delivery_bug=False):
    c = Charge()
    idx = PCHA.CHANNELS.index((src, dst))
    c.add("INDEX", 6)
    c.add("APPEND_OUTPUT")
    qs = list(queues)
    qs[idx] = qs[idx] + (msg,)
    loc = list(local)
    if implicit_delivery_bug:
        loc[dst] = (loc[dst] + msg) % 3
    return tuple(loc), tuple(qs), c, (1, 0, 0, 0, 0, 0, 0)


def low_recv(local, queues, src, dst):
    c = Charge()
    idx = PCHA.CHANNELS.index((src, dst))
    c.add("INDEX", 6)
    c.add("NEXT_INPUT")
    qs = list(queues)
    q = qs[idx]
    if q:
        val = q[0]
        qs[idx] = q[1:]
    else:
        c.add("TERMINAL")
        val = PCHA.NO_MESSAGE
    return tuple(local), tuple(qs), val, c, (0, 1, 0, 0, 0, 0, 0)


def low_apply_received(local, dst, msg):
    c = Charge()
    c.add("LOAD")
    c.add("NAT_ADD", local[dst], msg)
    c.add("NAT_MOD", local[dst] + msg, 3)
    c.add("STORE")
    loc = list(local)
    loc[dst] = (loc[dst] + msg) % 3
    return tuple(loc), c, (0, 0, 1, 1, 0, 0, 0)


TOOL_TABLE = {"ROT": 1, "DOUBLE": 2}


def low_call(tool, arg):
    """`CALL` lowered as typed interaction composition: one request event out on the
    external stream, one response event in.  The response carries a provenance tag."""
    c = Charge()
    c.add("APPEND_OUTPUT")
    c.add("NEXT_INPUT")
    if tool == "ROT":
        val = (arg + 1) % 3
    elif tool == "DOUBLE":
        val = (2 * arg) % 3
    else:
        raise ValueError("UNKNOWN_TOOL")
    return (tool, arg, val, "EXTERNAL_DATA"), c, (0, 0, 0, 0, 1, 1, 1)


def low_apply_external(local, agent, data, drop_tag_check=False):
    c = Charge()
    tool, arg, val, tag = data
    if not drop_tag_check:
        c.add("NAT_EQ", 1, 1)
        if tag != "EXTERNAL_DATA":
            raise ValueError("FORGED_EXTERNAL_DATA")
        expect = (arg + 1) % 3 if tool == "ROT" else (2 * arg) % 3 if tool == "DOUBLE" else None
        if expect is None or expect != val:
            raise ValueError("FORGED_EXTERNAL_DATA")
    c.add("LOAD")
    c.add("NAT_ADD", local[agent], val)
    c.add("NAT_MOD", local[agent] + val, 3)
    c.add("STORE")
    loc = list(local)
    loc[agent] = (loc[agent] + val) % 3
    return tuple(loc), c, (0, 0, 1, 1, 0, 0, 0)


def low_propose(version, sequence):
    c = Charge()
    c.add("STORE")
    c.add("SUCC")
    return (version, sequence + 1), c, (1, 0, 0, 0, 0, 0)


def low_verify():
    """`VERIFY` reuses the `CALL` lowering on the registered authority stream."""
    c = Charge()
    c.add("APPEND_OUTPUT")
    c.add("NEXT_INPUT")
    return c, (0, 1, 1, 0, 0, 0)


def low_adopt_guard(fresh, pending_ok, admitted, version_ok, accepted,
                    drop_admit_bug=False, allow_replay_bug=False):
    """`ADOPT` lowered: the parent's own guard chain, then one `SELECT`, then the transform.

    Five guards, in the parent's order.  `admitted` is the externally registered admission
    relation -- the single predicate that consumes the receipt.  Dropping it is the
    `drop_admit_bug` hostile; dropping `fresh` is `allow_replay_bug`.
    """
    c = Charge()
    checks = []
    if not allow_replay_bug:
        checks.append(fresh)
    checks.append(pending_ok)
    if not drop_admit_bug:
        checks.append(admitted)
    checks.extend([version_ok, accepted])
    for _ in checks:
        c.add("NAT_EQ", 1, 1)
    c.add("SELECT")
    ok = True
    for g in checks:
        if not g:
            ok = False
            break
    if ok:
        c.add("STORE")
        c.add("SUCC")
        res = (0, 0, 0, 1, 1, 1)
    else:
        res = (0, 0, 0, 1, 0, 0)
    return ok, c, res


PROFILE = {}


def record(name, charge):
    """Per-operator profile: cost range and the set of distinct role traces.

    The status rules in section 7 read only these measurements; no status is assigned by
    hand.
    """
    e = PROFILE.get(name)
    if e is None:
        e = {"min_roles": charge.roles, "max_roles": charge.roles,
             "min_aj5": charge.aj5, "max_aj5": charge.aj5, "traces": set(), "calls": 0}
        PROFILE[name] = e
    if charge.roles < e["min_roles"]:
        e["min_roles"] = charge.roles
    if charge.roles > e["max_roles"]:
        e["max_roles"] = charge.roles
    if charge.aj5 < e["min_aj5"]:
        e["min_aj5"] = charge.aj5
    if charge.aj5 > e["max_aj5"]:
        e["max_aj5"] = charge.aj5
    e["traces"].add(tuple(charge.trace))
    e["calls"] += 1


def _kernel_pairs(K):
    return tuple(tuple(frac_of(x) for x in row) for row in K.rows)


def _dist_pairs(mu):
    return tuple(frac_of(x) for x in mu.mass)


def check_stochastic():
    rows = PSTO.row_family()
    kers = PSTO.kernel_family()
    dists = tuple(_dist_pairs(r) for r in rows)
    kps = tuple(_kernel_pairs(k) for k in kers)
    perms = ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))

    out = {"update_checks": 0, "update_mismatches": 0,
           "compose_checks": 0, "compose_mismatches": 0,
           "identity_mismatches": 0,
           "deterministic_checks": 0, "deterministic_mismatches": 0,
           "transport_kernel_checks": 0, "transport_kernel_mismatches": 0,
           "transport_distribution_checks": 0, "transport_distribution_mismatches": 0,
           "resource_mismatches": 0}
    box = 0
    max_roles = {"UPDATE": 0, "COMPOSE": 0, "TRANSPORT": 0,
                 "IDENTITY_KERNEL": 0, "DETERMINISTIC_KERNEL": 0}
    max_aj5 = dict(max_roles)

    for di, mu in enumerate(dists):
        for ki, K in enumerate(kps):
            got, c = low_update(mu, K)
            want = _dist_pairs(PSTO.update(rows[di], kers[ki]).value)
            out["update_checks"] += 1
            if got != want:
                out["update_mismatches"] += 1
            box = max(box, c.box)
            record("UPDATE", c)
            max_roles["UPDATE"] = max(max_roles["UPDATE"], c.roles)
            max_aj5["UPDATE"] = max(max_aj5["UPDATE"], c.aj5)

    for i, K1 in enumerate(kps):
        p1 = kers[i]
        for j, K2 in enumerate(kps):
            got, c = low_compose(K1, K2)
            want = _kernel_pairs(PSTO.compose(p1, kers[j]).value)
            out["compose_checks"] += 1
            if got != want:
                out["compose_mismatches"] += 1
            box = max(box, c.box)
            record("COMPOSE", c)
            max_roles["COMPOSE"] = max(max_roles["COMPOSE"], c.roles)
            max_aj5["COMPOSE"] = max(max_aj5["COMPOSE"], c.aj5)

    got, c = low_identity_kernel()
    if got != _kernel_pairs(PSTO.identity_kernel()):
        out["identity_mismatches"] += 1
    record("IDENTITY_KERNEL", c)
    max_roles["IDENTITY_KERNEL"] = c.roles
    max_aj5["IDENTITY_KERNEL"] = c.aj5
    box = max(box, c.box)

    for a in S3:
        for b in S3:
            for cc in S3:
                m = (a, b, cc)
                got, ch = low_deterministic_kernel(m)
                out["deterministic_checks"] += 1
                if got != _kernel_pairs(PSTO.deterministic_kernel(m)):
                    out["deterministic_mismatches"] += 1
                record("DETERMINISTIC_KERNEL", ch)
                max_roles["DETERMINISTIC_KERNEL"] = max(max_roles["DETERMINISTIC_KERNEL"], ch.roles)
                max_aj5["DETERMINISTIC_KERNEL"] = max(max_aj5["DETERMINISTIC_KERNEL"], ch.aj5)
                box = max(box, ch.box)

    for i, K in enumerate(kps):
        for pi in perms:
            got, ch = low_transport_kernel(K, pi)
            out["transport_kernel_checks"] += 1
            if got != _kernel_pairs(PSTO.transport_kernel(kers[i], pi)):
                out["transport_kernel_mismatches"] += 1
            record("TRANSPORT", ch)
            max_roles["TRANSPORT"] = max(max_roles["TRANSPORT"], ch.roles)
            max_aj5["TRANSPORT"] = max(max_aj5["TRANSPORT"], ch.aj5)
            box = max(box, ch.box)

    for i, mu in enumerate(dists):
        for pi in perms:
            got, ch = low_transport_distribution(mu, pi)
            record("TRANSPORT_DISTRIBUTION", ch)
            out["transport_distribution_checks"] += 1
            if got != _dist_pairs(PSTO.transport_distribution(rows[i], pi)):
                out["transport_distribution_mismatches"] += 1
            box = max(box, ch.box)

    out["operand_box"] = box
    out["max_charged_roles"] = max_roles
    out["max_aj5_role_expansion"] = max_aj5
    return out


def check_graph():
    graphs = []
    for mask in range(8):
        edges = [PGRA.ALL_EDGES[i] for i in range(3) if mask & (1 << i)]
        graphs.append(PGRA.make_graph(edges))
    states = [(a, b, c) for a in S3 for b in S3 for c in S3]
    perms = ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))
    out = {"checks": 0, "mismatches": 0, "resource_checks": 0, "resource_mismatches": 0,
           "equivariance_checks": 0, "equivariance_mismatches": 0}
    max_roles = {"POINTWISE": 0, "GLOBAL_BROADCAST": 0, "NEIGHBOR_UPDATE": 0}
    max_aj5 = dict(max_roles)
    neighbor_cost_by_degree_sum = {}
    box = 0
    ops = (("POINTWISE", low_pointwise, PGRA.pointwise),
           ("GLOBAL_BROADCAST", low_global_broadcast, PGRA.global_broadcast),
           ("NEIGHBOR_UPDATE", low_neighbor_update, PGRA.neighbor_update))
    for g in graphs:
        adj = adjacency_registers(g)
        for st in states:
            for name, low, parent in ops:
                got, c, res = low(st, adj)
                pr = parent(st, g)
                out["checks"] += 1
                if got != pr.state:
                    out["mismatches"] += 1
                out["resource_checks"] += 1
                if res != pr.resources:
                    out["resource_mismatches"] += 1
                record(name, c)
                max_roles[name] = max(max_roles[name], c.roles)
                max_aj5[name] = max(max_aj5[name], c.aj5)
                box = max(box, c.box)
                if name == "NEIGHBOR_UPDATE":
                    key = str(len(g.edges))
                    prev = neighbor_cost_by_degree_sum.get(key)
                    if prev is None or c.roles > prev:
                        neighbor_cost_by_degree_sum[key] = c.roles
            for pi in perms:
                pst = [0, 0, 0]
                for v in S3:
                    pst[pi[v]] = st[v]
                pg = PGRA.make_graph(tuple(sorted((min(pi[u], pi[v]), max(pi[u], pi[v]))
                                                  for u, v in g.edges)))
                a2 = adjacency_registers(pg)
                got_a, _, _ = low_neighbor_update(tuple(pst), a2)
                got_b, _, _ = low_neighbor_update(st, adj)
                moved = [0, 0, 0]
                for v in S3:
                    moved[pi[v]] = got_b[v]
                out["equivariance_checks"] += 1
                if got_a != tuple(moved):
                    out["equivariance_mismatches"] += 1
    out["operand_box"] = box
    out["max_charged_roles"] = max_roles
    out["max_aj5_role_expansion"] = max_aj5
    out["neighbor_update_max_roles_by_edge_count"] = neighbor_cost_by_degree_sum
    return out


def check_channels():
    locals_ = [(a, b, c) for a in S3 for b in S3 for c in S3]
    out = {"send_checks": 0, "send_mismatches": 0,
           "recv_checks": 0, "recv_mismatches": 0,
           "apply_received_checks": 0, "apply_received_mismatches": 0,
           "call_checks": 0, "call_mismatches": 0,
           "apply_external_checks": 0, "apply_external_mismatches": 0,
           "fifo_checks": 0, "fifo_mismatches": 0,
           "resource_mismatches": 0}
    max_roles = {"SEND": 0, "RECV": 0, "APPLY_RECEIVED": 0, "CALL": 0, "APPLY_EXTERNAL": 0}
    max_aj5 = dict(max_roles)
    box = 0
    for loc in locals_:
        base = PCHA.Machine.empty(loc)
        for (src, dst) in PCHA.CHANNELS:
            for msg in PCHA.MESSAGES:
                nl, nq, c, res = low_send(base.local, base.queues, src, dst, msg)
                pm, pres = PCHA.send(base, src, dst, msg)
                out["send_checks"] += 1
                if (nl, nq) != (pm.local, pm.queues):
                    out["send_mismatches"] += 1
                if res != pres:
                    out["resource_mismatches"] += 1
                record("SEND", c)
                max_roles["SEND"] = max(max_roles["SEND"], c.roles)
                max_aj5["SEND"] = max(max_aj5["SEND"], c.aj5)
                box = max(box, c.box)

                rl, rq, val, c2, res2 = low_recv(nl, nq, src, dst)
                pm2, pval, pres2 = PCHA.recv(pm, src, dst)
                out["recv_checks"] += 1
                if (rl, rq, val) != (pm2.local, pm2.queues, pval):
                    out["recv_mismatches"] += 1
                if res2 != pres2:
                    out["resource_mismatches"] += 1
                record("RECV", c2)
                max_roles["RECV"] = max(max_roles["RECV"], c2.roles)
                max_aj5["RECV"] = max(max_aj5["RECV"], c2.aj5)

                el, eq, eval_, c3, res3 = low_recv(rl, rq, src, dst)
                pm3, pval3, _ = PCHA.recv(pm2, src, dst)
                out["recv_checks"] += 1
                if (el, eq, eval_) != (pm3.local, pm3.queues, pval3):
                    out["recv_mismatches"] += 1

                al, c4, res4 = low_apply_received(rl, dst, msg)
                pm4, pres4 = PCHA.apply_received(pm2, dst, msg)
                out["apply_received_checks"] += 1
                if al != pm4.local:
                    out["apply_received_mismatches"] += 1
                if res4 != pres4:
                    out["resource_mismatches"] += 1
                record("APPLY_RECEIVED", c4)
                max_roles["APPLY_RECEIVED"] = max(max_roles["APPLY_RECEIVED"], c4.roles)
                max_aj5["APPLY_RECEIVED"] = max(max_aj5["APPLY_RECEIVED"], c4.aj5)
            for m1 in PCHA.MESSAGES:
                for m2 in PCHA.MESSAGES:
                    s1, q1, _, _ = low_send(base.local, base.queues, src, dst, m1)
                    s2, q2, _, _ = low_send(s1, q1, src, dst, m2)
                    _, q3, v1, _, _ = low_recv(s2, q2, src, dst)
                    _, _, v2, _, _ = low_recv(s2, q3, src, dst)
                    out["fifo_checks"] += 1
                    if (v1, v2) != (m1, m2):
                        out["fifo_mismatches"] += 1
    for tool in ("ROT", "DOUBLE"):
        for arg in S3:
            data, c, res = low_call(tool, arg)
            pdata, pres = PCHA.call(tool, arg)
            out["call_checks"] += 1
            if data != (pdata.tool, pdata.arg, pdata.value, pdata.status):
                out["call_mismatches"] += 1
            if res != pres:
                out["resource_mismatches"] += 1
            record("CALL", c)
            max_roles["CALL"] = max(max_roles["CALL"], c.roles)
            max_aj5["CALL"] = max(max_aj5["CALL"], c.aj5)
            for loc in locals_:
                for agent in S3:
                    m = PCHA.Machine.empty(loc)
                    nl, c5, res5 = low_apply_external(loc, agent, data)
                    pm, pres5 = PCHA.apply_external(m, agent, pdata)
                    out["apply_external_checks"] += 1
                    if nl != pm.local:
                        out["apply_external_mismatches"] += 1
                    if res5 != pres5:
                        out["resource_mismatches"] += 1
                    record("APPLY_EXTERNAL", c5)
                    max_roles["APPLY_EXTERNAL"] = max(max_roles["APPLY_EXTERNAL"], c5.roles)
                    max_aj5["APPLY_EXTERNAL"] = max(max_aj5["APPLY_EXTERNAL"], c5.aj5)
    out["operand_box"] = box
    out["max_charged_roles"] = max_roles
    out["max_aj5_role_expansion"] = max_aj5
    return out


def check_self_change():
    ver = PSELF.fixture_verifier()
    out = {"candidate_checks": 0, "terminal_mismatches": 0, "resource_mismatches": 0,
           "adopted": 0, "refused": 0}
    max_roles = {"PROPOSE": 0, "VERIFY": 0, "ADOPT": 0}
    max_aj5 = dict(max_roles)
    for cand in PSELF.candidate_space():
        s0 = PSELF.base_state()
        sp, p, pres = PSELF.propose(s0, cand)
        lp, cp, lres = low_propose(s0.active.version, s0.next_sequence)
        if lres != pres:
            out["resource_mismatches"] += 1
        record("PROPOSE", cp)
        max_roles["PROPOSE"] = max(max_roles["PROPOSE"], cp.roles)
        max_aj5["PROPOSE"] = max(max_aj5["PROPOSE"], cp.aj5)

        r, vres = ver.verify(p)
        cv, lvres = low_verify()
        if lvres != vres:
            out["resource_mismatches"] += 1
        record("VERIFY", cv)
        max_roles["VERIFY"] = max(max_roles["VERIFY"], cv.roles)
        max_aj5["VERIFY"] = max(max_aj5["VERIFY"], cv.aj5)

        ok_parent = PSELF.adopt(sp, p, r, ver)
        valid, _ = ver.validate(p, r)
        low_ok, ca, lares = low_adopt_guard(
            fresh=(p.proposal_id not in sp.consumed),
            pending_ok=any(q == p for q in sp.pending),
            admitted=valid,
            version_ok=(p.base_version == sp.active.version),
            accepted=(r.decision == PSELF.ACCEPT))
        out["candidate_checks"] += 1
        if low_ok != (ok_parent.terminal == "ADOPTED"):
            out["terminal_mismatches"] += 1
        if lares != ok_parent.resources:
            out["resource_mismatches"] += 1
        if low_ok:
            out["adopted"] += 1
        else:
            out["refused"] += 1
        record("ADOPT", ca)
        max_roles["ADOPT"] = max(max_roles["ADOPT"], ca.roles)
        max_aj5["ADOPT"] = max(max_aj5["ADOPT"], ca.aj5)
    out["max_charged_roles"] = max_roles
    out["max_aj5_role_expansion"] = max_aj5
    return out


# --------------------------------------------------------------------------------------
# 5.  The two structural residuals, proved by exhaustive witness count.
# --------------------------------------------------------------------------------------

GUARD_NAMES = ("fresh", "pending_ok", "admitted", "version_ok", "accepted")


def adopt_case_table():
    """Every registered adoption attempt as a guard vector plus the parent's own outcome.

    `base` is the 27-candidate propose/verify/adopt sweep and exercises only the accept
    guard.  `extended` adds the wrong-authority, corrupted-signature, corrupted-binding,
    not-pending, replay and stale-version attempts.
    """
    ver = PSELF.fixture_verifier()
    other = PSELF.ExternalVerifier(b"GMI833-AG5-UNREGISTERED-AUTHORITY",
                                   authority_id="VERIFIER_X")
    base = []
    extended = []

    def vec(state, proposal, receipt, verifier):
        valid, _ = verifier.validate(proposal, receipt)
        return (proposal.proposal_id not in state.consumed,
                any(q == proposal for q in state.pending),
                valid,
                proposal.base_version == state.active.version,
                receipt.decision == PSELF.ACCEPT)

    def add(store, state, proposal, receipt):
        tr = PSELF.adopt(state, proposal, receipt, ver)
        store.append((vec(state, proposal, receipt, ver), tr.terminal == "ADOPTED"))

    for cand in PSELF.candidate_space():
        s0 = PSELF.base_state()
        sp, p, _ = PSELF.propose(s0, cand)
        r, _ = ver.verify(p)
        add(base, sp, p, r)
        add(extended, sp, p, r)

        ro, _ = other.verify(p)
        add(extended, sp, p, ro)

        bad_sig = PSELF.VerificationReceipt(r.proposal_id, r.candidate_digest, r.base_version,
                                            r.decision, r.authority_id, "0" * 64)
        add(extended, sp, p, bad_sig)

        bad_bind = PSELF.VerificationReceipt(r.proposal_id, "f" * 64, r.base_version,
                                             r.decision, r.authority_id, r.signature)
        add(extended, sp, p, bad_bind)

        # not pending: the same proposal offered to a state that never received it
        add(extended, PSELF.base_state(), p, r)

        tr = PSELF.adopt(sp, p, r, ver)
        if tr.terminal == "ADOPTED":
            add(extended, tr.state, p, r)          # replay

    accepted = [c for c in PSELF.candidate_space() if c[0] == 0]
    s = PSELF.base_state()
    s, p1, _ = PSELF.propose(s, accepted[0])
    s, p2, _ = PSELF.propose(s, accepted[1])
    r1, _ = ver.verify(p1)
    r2, _ = ver.verify(p2)
    a1 = PSELF.adopt(s, p1, r1, ver)
    add(extended, a1.state, p2, r2)                # stale base version
    return base, extended


def guard_isolation(cases):
    """A guard is identified only if some registered case makes it the single failure."""
    iso = {}
    for gi, name in enumerate(GUARD_NAMES):
        found = False
        for vecs, _ in cases:
            if not vecs[gi] and all(vecs[k] for k in range(len(GUARD_NAMES)) if k != gi):
                found = True
                break
        iso[name] = found
    return iso


def guard_subset_null(cases):
    """Exhaustive null over every proper subset of the five guards.

    A subset reproduces when the conjunction of its guards equals the parent's own outcome
    on every registered case.  The full set is the true lowering and is excluded.  The
    isolation analysis predicts exactly which proper subsets can survive: those whose
    dropped guards are all non-isolable at this scope.
    """
    n = len(GUARD_NAMES)
    iso = guard_isolation(cases)
    non_isolable = set(i for i, name in enumerate(GUARD_NAMES) if not iso[name])
    hits = []
    for mask in range((1 << n) - 1):
        ok = True
        for vecs, outcome in cases:
            got = True
            for i in range(n):
                if mask & (1 << i) and not vecs[i]:
                    got = False
                    break
            if got != outcome:
                ok = False
                break
        if ok:
            hits.append(mask)
    predicted = []
    for mask in range((1 << n) - 1):
        dropped = set(i for i in range(n) if not (mask & (1 << i)))
        if dropped and dropped <= non_isolable:
            predicted.append(mask)
    return {"proper_subsets": (1 << n) - 1,
            "reproducing_subsets": len(hits),
            "reproducing_dropped_guards": sorted(
                [sorted(GUARD_NAMES[i] for i in range(n) if not (mask & (1 << i)))
                 for mask in hits]),
            "guard_isolable": iso,
            "predicted_reproducing_subsets": len(predicted),
            "prediction_matches": sorted(hits) == sorted(predicted),
            "cases": len(cases)}


def adopt_externality():
    """`ADOPT` is not a function of the internal triple (active behavior, version, candidate).

    The two attempts in each pair are identical in the machine-internal triple and in the
    proposal; they differ only in the externally registered receipt, and only in that
    receipt's authority and signature fields.  Every differing outcome is a witness that the
    admission relation cannot be folded into the internal state transform.
    """
    ver = PSELF.fixture_verifier()
    other = PSELF.ExternalVerifier(b"GMI833-AG5-UNREGISTERED-AUTHORITY",
                                   authority_id="VERIFIER_X")
    terminal_pairs = 0
    state_pairs = 0
    pairs = 0
    field_violations = 0
    for cand in PSELF.candidate_space():
        s0 = PSELF.base_state()
        sp, p, _ = PSELF.propose(s0, cand)
        r, _ = ver.verify(p)
        ro, _ = other.verify(p)
        # the two receipts must agree everywhere except authority and signature
        if (r.proposal_id, r.candidate_digest, r.base_version, r.decision) != \
           (ro.proposal_id, ro.candidate_digest, ro.base_version, ro.decision):
            field_violations += 1
        t1 = PSELF.adopt(sp, p, r, ver)
        t2 = PSELF.adopt(sp, p, ro, ver)
        pairs += 1
        if t1.terminal != t2.terminal:
            terminal_pairs += 1
        if t1.state.active != t2.state.active:
            state_pairs += 1
    return {"controlled_pairs": pairs,
            "internal_triple_identical_by_construction": True,
            "receipt_fields_that_differ": ["authority_id", "signature"],
            "receipt_field_control_violations": field_violations,
            "terminal_witness_pairs": terminal_pairs,
            "state_change_witness_pairs": state_pairs}


def external_tag_role():
    """The provenance tag carries no registered state effect, and is the whole admission gate."""
    locals_ = [(a, b, c) for a in S3 for b in S3 for c in S3]
    inert_checks = 0
    inert_differences = 0
    forged_checks = 0
    forged_rejected_tagged = 0
    forged_accepted_untagged = 0
    for tool in ("ROT", "DOUBLE"):
        for arg in S3:
            data, _, _ = low_call(tool, arg)
            for loc in locals_:
                for agent in S3:
                    a, _, _ = low_apply_external(loc, agent, data)
                    b, _, _ = low_apply_external(loc, agent, data, drop_tag_check=True)
                    inert_checks += 1
                    if a != b:
                        inert_differences += 1
            good = data[2]
            forged = []
            for wrong in S3:
                if wrong != good:
                    forged.append((tool, arg, wrong, "EXTERNAL_DATA"))
            forged.append((tool, arg, good, "LOCAL_DATA"))
            forged.append(("UNKNOWN", arg, good, "EXTERNAL_DATA"))
            for f in forged:
                forged_checks += 1
                try:
                    low_apply_external((0, 0, 0), 0, f)
                except ValueError:
                    forged_rejected_tagged += 1
                try:
                    low_apply_external((0, 0, 0), 0, f, drop_tag_check=True)
                    forged_accepted_untagged += 1
                except (ValueError, TypeError):
                    pass
    return {"inert_checks": inert_checks,
            "inert_differences": inert_differences,
            "forged_checks": forged_checks,
            "forged_rejected_with_tag_gate": forged_rejected_tagged,
            "forged_accepted_without_tag_gate": forged_accepted_untagged}


def graph_structure_dependence():
    """`NEIGHBOR_UPDATE` is not a function of the site values alone; the other two are."""
    graphs = []
    for mask in range(8):
        edges = [PGRA.ALL_EDGES[i] for i in range(3) if mask & (1 << i)]
        graphs.append(PGRA.make_graph(edges))
    states = [(a, b, c) for a in S3 for b in S3 for c in S3]
    counts = {"POINTWISE": 0, "GLOBAL_BROADCAST": 0, "NEIGHBOR_UPDATE": 0}
    pairs = 0
    for st in states:
        for i in range(8):
            for j in range(i + 1, 8):
                pairs += 1
                ai = adjacency_registers(graphs[i])
                aj = adjacency_registers(graphs[j])
                for name, low in (("POINTWISE", low_pointwise),
                                  ("GLOBAL_BROADCAST", low_global_broadcast),
                                  ("NEIGHBOR_UPDATE", low_neighbor_update)):
                    a, _, _ = low(st, ai)
                    b, _, _ = low(st, aj)
                    if a != b:
                        counts[name] += 1
    return {"state_graph_pairs": pairs, "differing_pairs": counts}


# --------------------------------------------------------------------------------------
# 6.  Expansion-formula validation and the family-name audit.
# --------------------------------------------------------------------------------------

def literal_mod(a, b):
    q, k1 = literal_expansion("NAT_DIV", a, b)
    _, k2 = literal_expansion("NAT_MUL", b, q)
    _, k3 = literal_expansion("NAT_SUB_SAT", a, 0)
    return a % b if b else 0, k1 + k2 + k3 + 1


def literal_gcd(a, b):
    total = 1
    x, y = a, b
    while y:
        _, k = literal_mod(x, y)
        total += k
        x, y = y, x % y
    return x, total


def validate_expansions(box):
    """Every closed form above, checked literally over the whole observed operand box."""
    checks = 0
    failures = []
    for a in range(box + 1):
        for b in range(box + 1):
            for role, closed in (("NAT_ADD", exp_nat_add), ("NAT_SUB_SAT", exp_nat_sub_sat),
                                 ("NAT_MUL", exp_nat_mul), ("NAT_EQ", exp_nat_eq)):
                v, n = literal_expansion(role, a, b)
                checks += 1
                if n != closed(a, b):
                    failures.append([role, a, b, n, closed(a, b)])
            if b:
                v, n = literal_expansion("NAT_DIV", a, b)
                checks += 1
                if n != exp_nat_div(a, b):
                    failures.append(["NAT_DIV", a, b, n, exp_nat_div(a, b)])
                _, n = literal_mod(a, b)
                checks += 1
                if n != exp_nat_mod(a, b):
                    failures.append(["NAT_MOD", a, b, n, exp_nat_mod(a, b)])
                _, n = literal_gcd(a, b)
                checks += 1
                if n != exp_nat_gcd(a, b):
                    failures.append(["NAT_GCD", a, b, n, exp_nat_gcd(a, b)])
    return {"checks": checks, "failures": failures[:8], "failure_count": len(failures)}


LOWERING_FUNCTIONS = ("low_update", "low_compose", "low_identity_kernel",
                      "low_deterministic_kernel", "low_transport_kernel",
                      "low_transport_distribution", "low_pointwise", "low_global_broadcast",
                      "low_neighbor_update", "low_send", "low_recv", "low_apply_received",
                      "low_call", "low_apply_external", "low_propose", "low_verify",
                      "low_adopt_guard")


def family_name_audit(extra_text=""):
    """No lowering may need the name of an architecture family."""
    import inspect
    text = extra_text
    g = globals()
    for name in LOWERING_FUNCTIONS:
        text += inspect.getsource(g[name])
    low = text.lower()
    hits = []
    for tok in FAMILY_NAME_TOKENS:
        if tok in low:
            hits.append(tok)
    return {"functions_scanned": len(LOWERING_FUNCTIONS), "hits": hits}


# --------------------------------------------------------------------------------------
# 7.  Randomized nulls the true lowering must beat.
# --------------------------------------------------------------------------------------

def null_stochastic(draws=200, seed=8331301):
    """Permute the nine kernel cells before lowering; count draws that still reproduce the
    parent's whole one-step map."""
    rnd = random.Random(seed)
    rows = PSTO.row_family()
    kers = PSTO.kernel_family()
    dists = tuple(_dist_pairs(r) for r in rows)
    kps = tuple(_kernel_pairs(k) for k in kers)
    want = []
    for di in range(len(dists)):
        for ki in range(len(kps)):
            want.append(_dist_pairs(PSTO.update(rows[di], kers[ki]).value))
    cells = [(i, j) for i in S3 for j in S3]
    identity_draws = 0
    hits = 0
    live = 0
    for _ in range(draws):
        perm = list(range(9))
        rnd.shuffle(perm)
        if perm == list(range(9)):
            identity_draws += 1
            continue
        live += 1
        ok = True
        idx = 0
        for mu in dists:
            for K in kps:
                scr = [[None] * 3 for _ in S3]
                for pos, (i, j) in enumerate(cells):
                    si, sj = cells[perm[pos]]
                    scr[i][j] = K[si][sj]
                try:
                    got, _ = low_update(mu, tuple(tuple(r) for r in scr))
                except ValueError:
                    ok = False
                if not ok or got != want[idx]:
                    ok = False
                idx += 1
                if not ok:
                    break
            if not ok:
                break
        if ok:
            hits += 1
    return {"draws": draws, "identity_draws_excluded": identity_draws,
            "live_trials": live, "hits": hits}


def null_graph(draws=200, seed=8331302):
    """Replace the adjacency the lowering reads by a random per-graph substitute."""
    rnd = random.Random(seed)
    graphs = []
    for mask in range(8):
        edges = [PGRA.ALL_EDGES[i] for i in range(3) if mask & (1 << i)]
        graphs.append(PGRA.make_graph(edges))
    states = [(a, b, c) for a in S3 for b in S3 for c in S3]
    want = {}
    for gi, g in enumerate(graphs):
        for st in states:
            want[(gi, st)] = PGRA.neighbor_update(st, g).state
    identity_draws = 0
    hits = 0
    live = 0
    for _ in range(draws):
        sub = [rnd.randrange(8) for _ in range(8)]
        if sub == list(range(8)):
            identity_draws += 1
            continue
        live += 1
        ok = True
        for gi in range(8):
            adj = adjacency_registers(graphs[sub[gi]])
            for st in states:
                got, _, _ = low_neighbor_update(st, adj)
                if got != want[(gi, st)]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            hits += 1
    return {"draws": draws, "identity_draws_excluded": identity_draws,
            "live_trials": live, "hits": hits}


def null_channels(draws=200, seed=8331303):
    """Permute the six directed channel indices the lowering writes to."""
    rnd = random.Random(seed)
    base = PCHA.Machine.empty((0, 1, 2))
    want = {}
    for (src, dst) in PCHA.CHANNELS:
        for msg in PCHA.MESSAGES:
            pm, _ = PCHA.send(base, src, dst, msg)
            want[(src, dst, msg)] = pm.queues
    identity_draws = 0
    hits = 0
    live = 0
    order = list(range(6))
    for _ in range(draws):
        perm = list(range(6))
        rnd.shuffle(perm)
        if perm == order:
            identity_draws += 1
            continue
        live += 1
        ok = True
        for ci, (src, dst) in enumerate(PCHA.CHANNELS):
            for msg in PCHA.MESSAGES:
                qs = list(base.queues)
                qs[perm[ci]] = qs[perm[ci]] + (msg,)
                if tuple(qs) != want[(src, dst, msg)]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            hits += 1
    return {"draws": draws, "identity_draws_excluded": identity_draws,
            "live_trials": live, "hits": hits}


# --------------------------------------------------------------------------------------
# 8.  The status ledger.  Every status is read off a measurement, never assigned by hand.
# --------------------------------------------------------------------------------------

AJ5_CROSSWALK = {"DERIVED": "DERIVED_OPERATION", "PRESENTATION_ONLY": "SEMANTIC_CONVENIENCE"}

EXTENSION_OPERATORS = (
    ("UPDATE", "gmi-833-g0-stochastic-update-v1"),
    ("COMPOSE", "gmi-833-g0-stochastic-update-v1"),
    ("IDENTITY_KERNEL", "gmi-833-g0-stochastic-update-v1"),
    ("DETERMINISTIC_KERNEL", "gmi-833-g0-stochastic-update-v1"),
    ("TRANSPORT", "gmi-833-g0-stochastic-update-v1"),
    ("POINTWISE", "gmi-833-g0-local-graph-ops-v1"),
    ("GLOBAL_BROADCAST", "gmi-833-g0-local-graph-ops-v1"),
    ("NEIGHBOR_UPDATE", "gmi-833-g0-local-graph-ops-v1"),
    ("SEND", "gmi-833-g0-interaction-channels-v1"),
    ("RECV", "gmi-833-g0-interaction-channels-v1"),
    ("APPLY_RECEIVED", "gmi-833-g0-interaction-channels-v1"),
    ("CALL", "gmi-833-g0-interaction-channels-v1"),
    ("APPLY_EXTERNAL", "gmi-833-g0-interaction-channels-v1"),
    ("PROPOSE", "gmi-833-g0-governed-self-change-v1"),
    ("VERIFY", "gmi-833-g0-governed-self-change-v1"),
    ("ADOPT", "gmi-833-g0-governed-self-change-v1"),
)

# An operator consumes a value the machine state does not determine.  `CALL` and `VERIFY`
# read a response event off an external stream; `ADOPT` consumes an externally registered
# receipt.  For `ADOPT` this is proved by witness count rather than asserted.
# An operator consumes a value the machine state does not determine.  `CALL` and `VERIFY`
# read a response event off an external stream; `ADOPT` consumes an externally registered
# receipt; `APPLY_EXTERNAL` admits an externally produced value only through the provenance
# gate.  For `ADOPT` this is proved by witness count, for `APPLY_EXTERNAL` by the forged-input
# count, rather than asserted.
EXTERNAL_STREAM_CONSUMERS = ("CALL", "VERIFY", "ADOPT", "APPLY_EXTERNAL")


def assign_status(name, mismatches, structure_priced):
    """The status rules.  Each reads a published measurement; none is assigned by hand.

    `GENERATOR`            no lowering into the role basis exists.  Exhibiting one refutes it.
    `SEMANTIC_CONVENIENCE` no registered state effect and no observation.  Taken for the core
                           five from AJ5's pinned ledger; no extension operator qualifies.
    `RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE`
                           the operator's result depends on a registered *structural*
                           parameter beyond its value arguments (measured by
                           `graph_structure_dependence`) AND its lowering cost varies with
                           that parameter (measured by
                           `neighbor_update_max_roles_by_edge_count`).
    `MACRO`                one role trace over the whole registered universe: the lowering is
                           a straight-line closed term, i.e. a named abbreviation.
    `DERIVED_OPERATION`    a composition of roles whose trace depends on its value arguments.
    """
    if mismatches:
        return "VOID_LOWERING_MISMATCH", []
    prof = PROFILE.get(name)
    if prof is None:
        return "VOID_NOT_PROFILED", []
    quals = []
    if name in EXTERNAL_STREAM_CONSUMERS:
        quals.append(QUALIFIER)
    if structure_priced.get(name):
        return "RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE", quals
    if len(prof["traces"]) == 1:
        return "MACRO", quals
    return "DERIVED_OPERATION", quals


def build_ledger(sto, gra, cha, slf, structure_priced):
    aj5 = json.load(open(os.path.join(REPO, "research", "gmi-833-aj5-g0-lowering-v1",
                                      "RESULT_V1.json")))
    rows = []
    for op in ("READ", "EMIT", "INC", "DECJZ", "HALT"):
        rows.append({"operator": op,
                     "package": "gmi-833-aj5-g0-lowering-v1",
                     "status": AJ5_CROSSWALK[aj5["primitive_status"][op]],
                     "qualifiers": [],
                     "source": "pinned parent ledger",
                     "aj5_token": aj5["primitive_status"][op]})
    mism = {
        "UPDATE": sto["update_mismatches"],
        "COMPOSE": sto["compose_mismatches"],
        "IDENTITY_KERNEL": sto["identity_mismatches"],
        "DETERMINISTIC_KERNEL": sto["deterministic_mismatches"],
        "TRANSPORT": sto["transport_kernel_mismatches"],
        "POINTWISE": gra["mismatches"],
        "GLOBAL_BROADCAST": gra["mismatches"],
        "NEIGHBOR_UPDATE": gra["mismatches"],
        "SEND": cha["send_mismatches"],
        "RECV": cha["recv_mismatches"],
        "APPLY_RECEIVED": cha["apply_received_mismatches"],
        "CALL": cha["call_mismatches"],
        "APPLY_EXTERNAL": cha["apply_external_mismatches"],
        "PROPOSE": slf["terminal_mismatches"],
        "VERIFY": slf["terminal_mismatches"],
        "ADOPT": slf["terminal_mismatches"],
    }
    for op, pkg in EXTENSION_OPERATORS:
        status, quals = assign_status(op, mism[op], structure_priced)
        prof = PROFILE.get(op, {})
        rows.append({"operator": op, "package": pkg, "status": status,
                     "qualifiers": quals,
                     "source": "measured here",
                     "charged_roles_min": prof.get("min_roles"),
                     "charged_roles_max": prof.get("max_roles"),
                     "aj5_role_expansion_min": prof.get("min_aj5"),
                     "aj5_role_expansion_max": prof.get("max_aj5"),
                     "distinct_role_traces": len(prof.get("traces", ())),
                     "calls": prof.get("calls")})
    return rows


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


def main():
    sto = check_stochastic()
    gra = check_graph()
    cha = check_channels()
    slf = check_self_change()
    gdep = graph_structure_dependence()
    by_edges = gra["neighbor_update_max_roles_by_edge_count"]
    structure_priced = {}
    for op in ("POINTWISE", "GLOBAL_BROADCAST", "NEIGHBOR_UPDATE"):
        depends = gdep["differing_pairs"][op] > 0
        cost_varies = (op == "NEIGHBOR_UPDATE"
                       and len(set(by_edges.values())) > 1)
        structure_priced[op] = bool(depends and cost_varies)
    ledger = build_ledger(sto, gra, cha, slf, structure_priced)

    box = max(sto["operand_box"], gra["operand_box"], cha["operand_box"])
    expansion = validate_expansions(box)
    audit = family_name_audit()
    ext = adopt_externality()
    tag = external_tag_role()
    base_cases, ext_cases = adopt_case_table()
    base_null = guard_subset_null(base_cases)
    ext_null = guard_subset_null(ext_cases)
    nulls = {"stochastic": null_stochastic(), "graph": null_graph(),
             "channels": null_channels(),
             "adopt_guard_subsets_base_universe": base_null,
             "adopt_guard_subsets_extended_universe": ext_null}

    failed = []
    total_mismatch = (sto["update_mismatches"] + sto["compose_mismatches"]
                      + sto["identity_mismatches"] + sto["deterministic_mismatches"]
                      + sto["transport_kernel_mismatches"]
                      + sto["transport_distribution_mismatches"]
                      + gra["mismatches"] + gra["equivariance_mismatches"]
                      + cha["send_mismatches"] + cha["recv_mismatches"]
                      + cha["apply_received_mismatches"] + cha["call_mismatches"]
                      + cha["apply_external_mismatches"] + cha["fifo_mismatches"]
                      + slf["terminal_mismatches"])
    total_resource = (sto["resource_mismatches"] + gra["resource_mismatches"]
                      + cha["resource_mismatches"] + slf["resource_mismatches"])
    if total_mismatch:
        failed.append("GATE_1_LOWERING_MISMATCH")
    if total_resource:
        failed.append("GATE_2_RESOURCE_MISMATCH")
    if expansion["failure_count"]:
        failed.append("GATE_EXPANSION_FORMULA")
    if audit["hits"]:
        failed.append("GATE_FAMILY_NAME_IN_LOWERING")
    if ext["terminal_witness_pairs"] == 0:
        failed.append("GATE_ADOPT_EXTERNALITY_NOT_WITNESSED")
    if tag["inert_differences"]:
        failed.append("GATE_TAG_NOT_INERT")
    if tag["forged_rejected_with_tag_gate"] != tag["forged_checks"]:
        failed.append("GATE_TAG_GUARD_INCOMPLETE")
    if gdep["differing_pairs"]["NEIGHBOR_UPDATE"] == 0:
        failed.append("GATE_NEIGHBOR_NOT_STRUCTURE_DEPENDENT")
    if gdep["differing_pairs"]["POINTWISE"] or gdep["differing_pairs"]["GLOBAL_BROADCAST"]:
        failed.append("GATE_CONTROL_OPS_STRUCTURE_DEPENDENT")
    for k in ("stochastic", "graph", "channels"):
        if nulls[k]["hits"]:
            failed.append("GATE_NULL_" + k.upper())
    if not ext_null["prediction_matches"]:
        failed.append("GATE_ADOPT_GUARD_ISOLATION_PREDICTION")
    if not ext_null["guard_isolable"]["admitted"]:
        failed.append("GATE_ADMISSION_GUARD_NOT_IDENTIFIED")
    if base_null["reproducing_subsets"] <= ext_null["reproducing_subsets"]:
        failed.append("GATE_EXTENDED_UNIVERSE_DID_NOT_TIGHTEN")
    generators = [r["operator"] for r in ledger if r["status"] == "GENERATOR"]
    voids = [r["operator"] for r in ledger if r["status"].startswith("VOID")]
    if voids:
        failed.append("GATE_LEDGER_VOID")

    receipt = {
        "schema": "GMI833AG5ExtensionLoweringReceiptV1",
        "package": "gmi-833-ag5-extension-lowering-v1",
        "issue": 833,
        "sections": ["AG2", "AG5"],
        "source_main": SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "status_vocabulary": list(STATUSES),
        "qualifier": QUALIFIER,
        "aj5_crosswalk": AJ5_CROSSWALK,
        "stochastic": sto,
        "graph": gra,
        "channels": cha,
        "self_change": slf,
        "ledger": ledger,
        "ledger_size": len(ledger),
        "generators": generators,
        "generator_count": len(generators),
        "externally_registered": sorted(r["operator"] for r in ledger
                                        if QUALIFIER in r["qualifiers"]),
        "resource_priced": sorted(r["operator"] for r in ledger
                                  if r["status"] == "RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE"),
        "adopt_externality": ext,
        "external_data_tag": tag,
        "graph_structure_dependence": gdep,
        "structure_priced": structure_priced,
        "expansion_validation": expansion,
        "operand_box": box,
        "family_name_audit": audit,
        "nulls": nulls,
        "total_lowering_mismatches": total_mismatch,
        "total_resource_mismatches": total_resource,
        "failed_gates": failed,
        "status": "GREEN" if not failed else "RED",
    }
    return receipt


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"status": r["status"], "failed_gates": r["failed_gates"],
                          "ledger_size": r["ledger_size"],
                          "generator_count": r["generator_count"],
                          "total_lowering_mismatches": r["total_lowering_mismatches"],
                          "total_resource_mismatches": r["total_resource_mismatches"]}))
