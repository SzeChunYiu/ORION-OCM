"""finite_world_v1.py -- shared tiny fully-enumerable world for HST-D3 lane B (issue #233).

World FW1 (frozen in this file; every certificate JSON cites this spec):
  state space   S = Z_16 = {0..15}
  operator basis O = {a2: x->x+2 mod 16, m2: x->2x mod 16}
  candidate primitive p = {a1: x->x+1 mod 16}   (the promotion candidate)
  candidate solutions = finite words over an operator alphabet (ops applied left to right)
  cost model      cost(w) = number of operator applications (composition length); frozen
  Adm(w, tau)     = [ f_w(s_tau) == g_tau ]  (exact, decidable)
  tasks T (10)    = (start, goal) pairs below; 5 solvable from O, 5 requiring p
Reachability facts used by design (verified by enumeration, not assumed):
  every word over O induces x -> 2^j*x + 2m (mod 16): j>=1 => even image; j=0 => parity of x.
  => an odd goal is unreachable from an even start under O at ANY budget;
     a1 (odd shift) is not in the full transformation closure <O>.
Python 3.8 compatible (no match / PEP604 / builtin generics).
Everything deterministic; exact arithmetic via fractions.Fraction.
"""

from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

N = 16  # Z_N

# operators: name -> (image tuple over Z_N), i.e. the full transformation as a tuple
def _fn(coeff, const):
    # x -> coeff*x + const  (mod N), as an N-tuple of images
    return tuple((coeff * x + const) % N for x in range(N))

OPS = {
    "a2": _fn(1, 2),   # add 2
    "m2": _fn(2, 0),   # multiply by 2
}
P_OP = {"a1": _fn(1, 1)}  # candidate primitive: add 1

# task set T (frozen): 5 O-solvable with abundant O-solutions (tau04 chosen from the
# exhaustive 184-pair scan: a starved outlier was replaced so the C6 hostile measures
# TYPICAL burden, not one rare-event task; 115/184 O-solvable pairs worsen after p),
# 5 p-required (odd goal from even start => unreachable under O at any cost)
TASKS = [
    ("tau01", 1, 6), ("tau02", 0, 8), ("tau03", 3, 12), ("tau04", 13, 0), ("tau05", 4, 10),
    ("tau06", 2, 11), ("tau07", 0, 7), ("tau08", 6, 13), ("tau09", 8, 15), ("tau10", 12, 5),
]

WORLD_SPEC = {
    "world_id": "FW1",
    "state_space": "Z_16",
    "operator_basis": {"a2": "x->x+2 mod 16", "m2": "x->2x mod 16"},
    "candidate_primitive": {"a1": "x->x+1 mod 16"},
    "cost_model": "cost(word) = number of operator applications (composition length)",
    "admissibility": "Adm(w,tau) iff composed function maps s_tau to g_tau (exact)",
    "tasks": [{"task_id": t, "start": s, "goal": g} for (t, s, g) in TASKS],
}


def apply_word(word: Sequence[str], x: int, table: Dict[str, Tuple[int, ...]]) -> int:
    for op in word:
        x = table[op][x]
    return x


def word_fn(word: Sequence[str], table: Dict[str, Tuple[int, ...]]) -> Tuple[int, ...]:
    return tuple(apply_word(word, x, table) for x in range(N))


def adm(word: Sequence[str], task: Tuple[str, int, int], table: Dict[str, Tuple[int, ...]]) -> bool:
    _, s, g = task
    return apply_word(word, s, table) == g


def all_words(alphabet: List[str], max_len: int) -> List[Tuple[str, ...]]:
    """Complete enumeration of every word of length 0..max_len (full tree, no pruning)."""
    out = [()]
    frontier = [()]
    for _ in range(max_len):
        nxt = []
        for w in frontier:
            for op in alphabet:
                nxt.append(w + (op,))
        out.extend(nxt)
        frontier = nxt
    return out


def full_closure(ops: Dict[str, Tuple[int, ...]]) -> Dict[str, object]:
    """BFS the full transformation closure <ops> until fixpoint.

    Label-correcting enumeration from the generators: start with the generator functions,
    repeatedly post-compose every member with every generator, add new image tuples until
    a full sweep adds nothing. Terminates because all functions Z_N -> Z_N form a finite
    set. The returned dict image-tuple -> shortest-ish witness word, plus the self-check
    that the set is closed under post-composition with every generator: that assertion IS
    the exhaustive proof that the enumeration is the complete closure.
    """
    words = {g: (op,) for op, g in ops.items()}
    changed = True
    while changed:
        changed = False
        for f, wf in list(words.items()):
            for op2, g2 in ops.items():
                h = tuple(g2[v] for v in f)
                if h not in words:
                    words[h] = wf + (op2,)
                    changed = True
    closed_ok = all(tuple(g2[v] for v in f) in words
                    for f in words for g2 in ops.values())
    assert closed_ok, "closure not closed under generators -- enumeration incomplete"
    return {"size": len(words), "functions": words, "closed_under_generators": True}


def closure_membership(ops: Dict[str, Tuple[int, ...]], f: Tuple[int, ...],
                       closure: Optional[Dict[Tuple[int, ...], Tuple[str, ...]]] = None
                       ) -> Optional[Tuple[str, ...]]:
    """Exhaustive membership: search the FULL closure for f; return witness word or None.

    Uses the precomputed closure dict when given, else computes it. The None answer is
    exhaustive because the closure enumeration is a verified fixpoint (see full_closure).
    """
    clo = closure if closure is not None else full_closure(ops)["functions"]
    return clo.get(f)


def exact_burden(alphabet: List[str], table: Dict[str, Tuple[int, ...]], task: Tuple[str, int, int],
                 prop_max_len: int) -> Dict[str, object]:
    """Exact expected first-admissible-solution cost under the frozen proposal distribution.

    Proposal distribution (frozen): one proposal round draws a word w UNIFORMLY from the
    set of ALL words of length <= prop_max_len over the alphabet (each word equiprobable).
    Rounds repeat i.i.d. until the first admissible word. Charged cost = total operator
    slots proposed (sum of proposed word lengths, successful round included).
    E[total] = E[len] / p_succ   (Wald; N geometric -> E[N]=1/p, lengths i.i.d.).
    Exact rationals; p_succ = 0 => infinite burden (unsolvable at this proposal scope).
    """
    words = all_words(alphabet, prop_max_len)
    n_words = len(words)
    total_len = sum(len(w) for w in words)
    mean_len = Fraction(total_len, n_words)
    solving = [w for w in words if adm(w, task, table)]
    p_succ = Fraction(len(solving), n_words)
    if p_succ == 0:
        burden = None  # infinity
    else:
        burden = mean_len / p_succ
    return {
        "proposal_words_enumerated": n_words,
        "mean_proposed_length": [str(mean_len), float(mean_len)],
        "p_succ": [str(p_succ), float(p_succ)],
        "solving_words": len(solving),
        "expected_first_solution_cost": (["INF", None] if burden is None
                                         else [str(burden), float(burden)]),
    }


def state_bfs(table: Dict[str, Tuple[int, ...]], alphabet: List[str], start: int):
    """Complete reachability BFS on the finite state space Z_N under the given operators.

    Returns (visited_states, dist). Since the state space is finite and fully explored to
    BFS fixpoint, membership in `visited` is an ALL-LENGTHS solvability decision.
    """
    from collections import deque
    dist = {start: 0}
    q = deque([start])
    while q:
        x = q.popleft()
        for op in alphabet:
            y = table[op][x]
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)
    return set(dist), dist


def frac(f: Fraction) -> List[Optional[str]]:
    return [str(f), float(f)]
