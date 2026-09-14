"""Exact finite witnesses for the five-type developmental taxonomy (A3).

n=3 product fixture (parent factorization) plus four declared registers
(r, K, L, M) and generation flag g. All values exact ints/frozensets.
CPython 3.8 safe. No network, no sampling.
"""

N = 3

# --- local unit law (parent fixture) ---
def query_output(local_state):
    if local_state not in (0, 1, 2):
        raise ValueError("local_state must be 0/1/2")
    return 0 if local_state in (0, 1) else 1


def teach1_local(local_state):
    if local_state not in (0, 1, 2):
        raise ValueError("local_state must be 0/1/2")
    if local_state == 0:
        return 2
    if local_state == 1:
        return 1
    return 2


def teach1_global(s, idx):
    """Apply teach1_idx to global s tuple."""
    if not isinstance(s, tuple) or len(s) != N:
        raise ValueError("s must be tuple length %d" % N)
    if idx not in (0, 1, 2):
        raise ValueError("idx must be 0/1/2")
    lst = list(s)
    lst[idx] = teach1_local(lst[idx])
    return tuple(lst)


def query_outputs(s):
    """Tuple of query_i outputs for i=0..N-1."""
    if not isinstance(s, tuple) or len(s) != N:
        raise ValueError("s must be tuple length %d" % N)
    return tuple(query_output(s[i]) for i in range(N))


def all_global_states():
    """All 3^N product states."""
    out = []

    def rec(prefix):
        if len(prefix) == N:
            out.append(tuple(prefix))
            return
        for v in (0, 1, 2):
            rec(prefix + [v])
    rec([])
    return out


# --- configuration ---
# C = (s, r, K, L, M, g)  where K is frozenset, others are ints

def make_config(s, r, K, L, M, g):
    if not isinstance(s, tuple) or len(s) != N or any(v not in (0, 1, 2) for v in s):
        raise ValueError("bad s")
    if r not in (0, 1):
        raise ValueError("r must be 0/1")
    if not isinstance(K, frozenset):
        raise ValueError("K must be frozenset")
    if L not in (0, 1):
        raise ValueError("L must be 0/1")
    if M not in (0, 1):
        raise ValueError("M must be 0/1")
    if g not in (0, 1):
        raise ValueError("g must be 0/1")
    return (s, r, K, L, M, g)


C0 = make_config((0, 0, 0), 0, frozenset(), 0, 0, 0)

SKILLS = ("skill_0", "skill_1", "skill_2")

# --- predicates (observable decision criteria) ---
def _unpack(C):
    s, r, K, L, M, g = C
    return s, r, K, L, M, g


def is_hereditary(before, after):
    """Flag: generation boundary crossed (g 0->1). Orthogonal to five types."""
    _, _, _, _, _, g0 = _unpack(before)
    _, _, _, _, _, g1 = _unpack(after)
    return g0 == 0 and g1 == 1


def p_info(before, after):
    s0, r0, K0, L0, M0, g0 = _unpack(before)
    s1, r1, K1, L1, M1, g1 = _unpack(after)
    return s0 != s1 and r0 == r1 and K0 == K1 and L0 == L1 and M0 == M1 and g0 == g1


def p_recode(before, after):
    s0, r0, K0, L0, M0, g0 = _unpack(before)
    s1, r1, K1, L1, M1, g1 = _unpack(after)
    return r0 != r1 and s0 == s1 and K0 == K1 and L0 == L1 and M0 == M1 and g0 == g1


def p_skill(before, after):
    s0, r0, K0, L0, M0, g0 = _unpack(before)
    s1, r1, K1, L1, M1, g1 = _unpack(after)
    return K1 > K0 and s0 == s1 and r0 == r1 and L0 == L1 and M0 == M1 and g0 == g1


def p_law(before, after):
    s0, r0, K0, L0, M0, g0 = _unpack(before)
    s1, r1, K1, L1, M1, g1 = _unpack(after)
    return L0 != L1 and s0 == s1 and r0 == r1 and K0 == K1 and M0 == M1 and g0 == g1


def p_morph(before, after):
    s0, r0, K0, L0, M0, g0 = _unpack(before)
    s1, r1, K1, L1, M1, g1 = _unpack(after)
    return M0 != M1 and s0 == s1 and r0 == r1 and K0 == K1 and L0 == L1 and g0 == g1


def p_meta(before, after):
    """Object-level law change. In witness every P_LAW is object-level."""
    return p_law(before, after)


def classify(before, after):
    """Return name of the unique firing predicate among the five, or None."""
    hits = []
    if p_info(before, after):
        hits.append("INFO")
    if p_recode(before, after):
        hits.append("RECODE")
    if p_skill(before, after):
        hits.append("SKILL")
    if p_law(before, after):
        hits.append("LAW")
    if p_morph(before, after):
        hits.append("MORPH")
    if len(hits) == 1:
        return hits[0]
    if len(hits) == 0:
        return None
    return "CONFLICT:" + ",".join(hits)


# --- witness log: 15 transitions round-robin INFO/RECODE/SKILL/LAW/MORPH x3 ---
def build_witness_log():
    log = []
    cur = C0
    # skill progression
    skill_steps = [frozenset((SKILLS[0],)),
                   frozenset((SKILLS[0], SKILLS[1])),
                   frozenset((SKILLS[0], SKILLS[1], SKILLS[2]))]
    skill_idx = 0
    info_idx = 0  # which unit teach1 hits
    for round_idx in range(3):
        # INFO: teach1 on unit info_idx, r/K/L/M/g unchanged
        s, r, K, L, M, g = _unpack(cur)
        ns = teach1_global(s, info_idx % N)
        nxt = make_config(ns, r, K, L, M, g)
        log.append((cur, nxt, "INFO"))
        cur = nxt
        info_idx += 1

        # RECODE: flip r
        s, r, K, L, M, g = _unpack(cur)
        nxt = make_config(s, 1 - r, K, L, M, g)
        log.append((cur, nxt, "RECODE"))
        cur = nxt

        # SKILL: grow K
        s, r, K, L, M, g = _unpack(cur)
        nxt = make_config(s, r, skill_steps[skill_idx], L, M, g)
        skill_idx += 1
        log.append((cur, nxt, "SKILL"))
        cur = nxt

        # LAW: flip L
        s, r, K, L, M, g = _unpack(cur)
        nxt = make_config(s, r, K, 1 - L, M, g)
        log.append((cur, nxt, "LAW"))
        cur = nxt

        # MORPH: flip M
        s, r, K, L, M, g = _unpack(cur)
        nxt = make_config(s, r, K, L, 1 - M, g)
        log.append((cur, nxt, "MORPH"))
        cur = nxt
    return log


WITNESS_LOG = build_witness_log()

# Hereditary example: copy s into next generation
HEREDITARY_BEFORE = make_config((2, 0, 0), 1, frozenset((SKILLS[0],)), 0, 0, 0)
HEREDITARY_AFTER = make_config((2, 0, 0), 1, frozenset((SKILLS[0],)), 0, 0, 1)

# --- behavioural equivalence / irreducibility ---
def successors_and_outputs(config):
    """All continuations of length 1: query outputs + teach successors."""
    s, _, _, _, _, _ = _unpack(config)
    return {
        "query": query_outputs(s),
        "teach": [teach1_global(s, i) for i in range(N)],
    }


def histories_equivalent(h1_landing, h2_landing):
    """Two histories equivalent iff landing configs identical."""
    return h1_landing == h2_landing


# Irreducibility witness: s_a=(0,0,0) vs s_b=(1,0,0)
S_A = (0, 0, 0)
S_B = (1, 0, 0)
C_A = make_config(S_A, 0, frozenset(), 0, 0, 0)
C_B = make_config(S_B, 0, frozenset(), 0, 0, 0)


def irreducibility_witness():
    """Return dict describing the history-irreducibility pair."""
    q_a = query_outputs(S_A)
    q_b = query_outputs(S_B)
    succ_a = teach1_global(S_A, 0)
    succ_b = teach1_global(S_B, 0)
    q_succ_a = query_outputs(succ_a)
    q_succ_b = query_outputs(succ_b)
    return {
        "s_a": S_A,
        "s_b": S_B,
        "query_a": q_a,
        "query_b": q_b,
        "query_match": q_a == q_b,
        "succ_a": succ_a,
        "succ_b": succ_b,
        "succ_query_a": q_succ_a,
        "succ_query_b": q_succ_b,
        "successors_differ": q_succ_a != q_succ_b,
    }


# --- parent scaling (preserved) ---
def global_state_count():
    return 3 ** N


def flat_transition_entries():
    return 2 * N * (3 ** N)


def min_state_bits():
    # ceil(log2(3^N))
    import math
    return int(math.ceil(N * math.log2(3)))
