"""G2.2 donor / library-learning parent boxes on the #192 polynomial ecology.

Issue #165 still needs Stitch, DreamCoder-class, anti-unification, grammar
induction, e-graph, program compression, domain-native induction, and a strong
conventional parent on the same primitive library {inc, dec, double, square},
each with ADOPT/ADAPT/GENERALIZE/REJECT/OPEN, origin, prior-information charge,
integration cost, and residual after subtraction.

`research/g2-acquisition-economics-v1/` already ran that comparison as a
selector study: compression / Stitch-style FAILED the argmax against the
utility tournament (every compressor chose `dec square`, rank 13 / 16,
validation saving −93,883); SEARCH_AWARE succeeded (chose `square dec square`,
rank 1, validation saving +92,599) at zero enumeration attempts against the
tournament's 9,010,526. This capsule does not retune those selectors. It
instantiates TINY research parents that carry the IDEA of those systems,
scores each proposal against the FROZEN receipt, and records the donor
disposition.

Importing the frozen receipt is stronger than rerunning the tournament.
This file never calls `build_search_index` or `evaluate_index`.

Research-only. Stdlib only. No DreamCoder/Stitch pip install. No src edit.
No OCM-specific claim that the programme invented library learning.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.learning import methods as M  # noqa: E402

SCHEMA = "ocm.g2.abstraction-parents.v1"
METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
FROZEN_PATH = REPO / "research" / "g2-acquisition-economics-v1" / "G2_ACQUISITION_ECONOMICS_V1.json"
FROZEN_TERMINAL = "CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE"
SEARCH_AWARE_KEY = "square dec square"
COMPRESSION_KEY = "dec square"
PRIMITIVES = M.PRIMITIVES
if PRIMITIVES != ("inc", "dec", "double", "square"):
    raise RuntimeError("primitive library drifted from the G2.2 ecology")
DISPOSITIONS = ("ADOPT", "ADAPT", "GENERALIZE", "REJECT", "OPEN")
G22_BOXES = (
    "Stitch-style library learning",
    "DreamCoder-class abstraction",
    "anti-unification",
    "grammar induction",
    "e-graph / rewrite-derived abstraction",
    "program compression",
    "domain-native method induction",
    "strong conventional parent with same primitive library",
)
DEPTH = 7
BUDGET = 7
N_PRIMITIVES = 4


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def pin_methods() -> str:
    blob = git_blob_sha1(SRC / "ocm" / "learning" / "methods.py")
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    return blob


def load_frozen() -> dict:
    if not FROZEN_PATH.is_file():
        raise RuntimeError(f"missing frozen receipt {FROZEN_PATH}")
    doc = json.loads(FROZEN_PATH.read_text(encoding="utf-8"))
    if doc["verdict"]["terminal"] != FROZEN_TERMINAL:
        raise RuntimeError(
            "frozen acquisition-economics terminal is %r, expected %r"
            % (doc["verdict"]["terminal"], FROZEN_TERMINAL)
        )
    if "SEARCH_AWARE" not in doc["verdict"]["selectors_agreeing_with_the_tournament"]:
        raise RuntimeError("frozen receipt no longer records SEARCH_AWARE agreement")
    mdl = next(row for row in doc["cheap_selectors"] if row["selector"] == "MDL_COMPRESSION")
    if " ".join(mdl["chosen"]) != COMPRESSION_KEY:
        raise RuntimeError("refusing to retune: frozen compression must remain %s" % COMPRESSION_KEY)
    aware = next(row for row in doc["cheap_selectors"] if row["selector"] == "SEARCH_AWARE")
    if " ".join(aware["chosen"]) != SEARCH_AWARE_KEY:
        raise RuntimeError("frozen SEARCH_AWARE must remain %s" % SEARCH_AWARE_KEY)
    if " ".join(doc["tournament"]["choice"]) != SEARCH_AWARE_KEY:
        raise RuntimeError("frozen tournament choice must remain %s" % SEARCH_AWARE_KEY)
    return doc


def _load_by_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s from %s" % (name, path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_parents():
    """Load #192 and the economics selectors by path so this file can be `experiment`."""
    g2 = _load_by_path(
        "g2_macro_operator_v1_experiment",
        REPO / "research" / "g2-macro-operator-v1" / "experiment.py",
    )
    saved = sys.modules.get("experiment")
    sys.modules["experiment"] = g2
    try:
        acq = _load_by_path(
            "g2_acquisition_economics_v1_experiment",
            REPO / "research" / "g2-acquisition-economics-v1" / "experiment.py",
        )
    finally:
        if saved is not None:
            sys.modules["experiment"] = saved
        else:
            sys.modules.pop("experiment", None)
    return g2, acq


G2 = None
ACQ = None


def _ensure_harness():
    global G2, ACQ
    if G2 is None or ACQ is None:
        G2, ACQ = load_parents()
    return G2, ACQ


def key_of(fragment) -> str:
    return " ".join(fragment)


def as_tuple(fragment) -> tuple:
    if fragment is None:
        return ()
    if isinstance(fragment, str):
        return tuple(fragment.split())
    return tuple(fragment)


def argmax_scores(scores: dict, candidates: tuple) -> tuple:
    order = {c: i for i, c in enumerate(candidates)}
    return min(candidates, key=lambda c: (-scores[c], order[c]))


def grammar_word_count(macro_len: int | None, depth: int = DEPTH,
                       primitives: int = N_PRIMITIVES, budget: int = BUDGET) -> int:
    _, acq = _ensure_harness()
    return acq._cumulative(depth, primitives, macro_len, budget)


def integration_cost(fragment) -> dict:
    prim = grammar_word_count(None)
    length = len(as_tuple(fragment)) if fragment else 0
    with_macro = grammar_word_count(length if length else None)
    delta = with_macro - prim
    return {
        "depth": DEPTH,
        "budget": BUDGET,
        "primitives": N_PRIMITIVES,
        "primitive_word_count": prim,
        "with_macro_word_count": with_macro,
        "grammar_width_delta": delta,
        "relative_widening": (delta / prim) if prim else None,
        "macro_length": length,
    }


def frozen_selector(frozen: dict, name: str) -> dict:
    return next(row for row in frozen["cheap_selectors"] if row["selector"] == name)


def lookup_utility(fragment, frozen: dict) -> dict:
    key = key_of(as_tuple(fragment)) if fragment else None
    savings = frozen["tournament"]["savings"]
    ranked = sorted(savings, key=lambda c: (-savings[c], frozen["candidates"].index(c)))
    if key not in savings:
        return {
            "chosen_key": key,
            "in_frozen_pool": False,
            "validation_saving": None,
            "utility_rank_of_pool": None,
            "matches_search_aware": False,
            "matches_tournament": False,
        }
    return {
        "chosen_key": key,
        "in_frozen_pool": True,
        "validation_saving": savings[key],
        "utility_rank_of_pool": ranked.index(key) + 1,
        "matches_search_aware": key == SEARCH_AWARE_KEY,
        "matches_tournament": key == key_of(frozen["tournament"]["choice"]),
        "frozen_test_saving": (
            frozen.get("test_by_macro", {}).get(key, {}) or {}
        ).get("saving"),
    }


def empty_work() -> dict:
    return {"token_operations": 0, "enumeration_attempts": 0, "unique_checks": 0}


# --- tiny parents -----------------------------------------------------------


def longest_common_substrings(left, right, min_len: int = 2, max_len: int = 4):
    """Grounded consecutive AU residue: longest common substrings, longest only."""
    a, b = tuple(left), tuple(right)
    cap = min(max_len, len(a), len(b))
    for length in range(cap, min_len - 1, -1):
        found = set()
        needles = {a[i:i + length] for i in range(len(a) - length + 1)}
        for j in range(len(b) - length + 1):
            frag = b[j:j + length]
            if frag in needles:
                found.add(frag)
        if found:
            return found
    return set()


def antiunify_inner(left, right) -> tuple:
    """Term AU from the variable: shared program prefix (inner ops)."""
    n = min(len(left), len(right))
    i = 0
    while i < n and left[i] == right[i]:
        i += 1
    return tuple(left[:i])


def antiunify_outer(left, right) -> tuple:
    """Term AU from the outside: shared program suffix (outer ops)."""
    n = min(len(left), len(right))
    i = 0
    while i < n and left[-1 - i] == right[-1 - i]:
        i += 1
    if i == 0:
        return ()
    return tuple(left[-i:])


def antiunify_positional(left, right) -> tuple:
    """Positional LGG: keep equal tokens, cut at the first hole for a fragment."""
    grounded = []
    best = ()
    for a, b in zip(left, right):
        if a == b:
            grounded.append(a)
        else:
            if len(grounded) > len(best):
                best = tuple(grounded)
            grounded = []
    if len(grounded) > len(best):
        best = tuple(grounded)
    return best


def parent_antiunification(programs, candidates) -> dict:
    """Anti-unification of two training programs, with a corpus vote for stability."""
    if len(programs) < 2:
        raise RuntimeError("anti-unification needs two training programs")
    p0, p1 = tuple(programs[0]), tuple(programs[1])
    pair_parts = {
        "inner_prefix": list(antiunify_inner(p0, p1)),
        "outer_suffix": list(antiunify_outer(p0, p1)),
        "positional_lgg": list(antiunify_positional(p0, p1)),
        "longest_common_substrings": sorted(
            " ".join(f) for f in longest_common_substrings(p0, p1)
        ),
    }
    pair_frags = [
        antiunify_inner(p0, p1),
        antiunify_outer(p0, p1),
        antiunify_positional(p0, p1),
        *longest_common_substrings(p0, p1),
    ]
    pool = set(candidates)
    pair_in_pool = [f for f in pair_frags if f in pool]
    votes = Counter()
    for i, a in enumerate(programs):
        for b in programs[i + 1:]:
            for frag in longest_common_substrings(a, b):
                if frag in pool:
                    votes[frag] += 1
            inner = antiunify_inner(a, b)
            outer = antiunify_outer(a, b)
            pos = antiunify_positional(a, b)
            for frag in (inner, outer, pos):
                if frag in pool:
                    votes[frag] += 1
    order = {c: i for i, c in enumerate(candidates)}
    if votes:
        chosen = max(votes, key=lambda f: (votes[f], len(f), -order[f]))
    elif pair_in_pool:
        chosen = max(pair_in_pool, key=lambda f: (len(f), -order[f]))
    else:
        nonempty = [f for f in pair_frags if len(f) >= 2]
        chosen = max(nonempty, key=len) if nonempty else ()
    return {
        "chosen": list(chosen) if chosen else [],
        "pair_programs": [list(p0), list(p1)],
        "pair_extracts": pair_parts,
        "corpus_votes": {" ".join(f): n for f, n in sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))},
        "prior_programs": 2,
        "corpus_pairs": len(programs) * (len(programs) - 1) // 2,
    }


class TinyEGraph:
    """Hashcons + union-find, saturated on a handful of polynomial rewrite rules.

    Rules (applied inside-out, matching `methods.execute` order):
      inc(dec(x)) ≡ x
      dec(inc(x)) ≡ x
    Congruence: interned ops whose children already share an e-class merge.
    This is the IDEA of e-graph extraction, not egg/eqsat production software.
    """

    CANCEL = {("inc", "dec"), ("dec", "inc")}

    def __init__(self):
        self.nodes: list[tuple] = []
        self.hashcons: dict[tuple, int] = {}
        self.parent: list[int] = []
        self.rank: list[int] = []

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True

    def intern(self, key: tuple) -> int:
        if key[0] == "op":
            key = ("op", key[1], self.find(key[2]))
        existing = self.hashcons.get(key)
        if existing is not None:
            return self.find(existing)
        i = len(self.nodes)
        self.nodes.append(key)
        self.hashcons[key] = i
        self.parent.append(i)
        self.rank.append(0)
        return i

    def input_id(self) -> int:
        return self.intern(("input",))

    def apply(self, op: str, child: int) -> int:
        return self.intern(("op", op, self.find(child)))

    def add_program(self, program) -> list[int]:
        nid = self.input_id()
        trace = [nid]
        for op in program:
            nid = self.apply(op, nid)
            trace.append(nid)
        return trace

    def saturate(self, max_rounds: int = 64) -> int:
        rounds = 0
        for rounds in range(1, max_rounds + 1):
            changed = False
            for idx, node in enumerate(list(self.nodes)):
                if node[0] != "op":
                    continue
                op = node[1]
                child = self.find(node[2])
                inner = self.nodes[child]
                if inner[0] == "op" and (op, inner[1]) in self.CANCEL:
                    if self.union(idx, self.find(inner[2])):
                        changed = True
            buckets: dict[tuple, int] = {}
            for idx, node in enumerate(self.nodes):
                if node[0] != "op":
                    continue
                key = ("op", node[1], self.find(node[2]))
                seen = buckets.get(key)
                if seen is None:
                    buckets[key] = idx
                elif self.union(idx, seen):
                    changed = True
            self.hashcons = {}
            for idx, node in enumerate(self.nodes):
                key = ("op", node[1], self.find(node[2])) if node[0] == "op" else node
                self.hashcons.setdefault(key, self.find(idx))
            if not changed:
                return rounds
        raise RuntimeError("tiny e-graph failed to saturate")

    def irreducible_ngrams(self, program, trace, n: int):
        out = []
        for i in range(len(program) - n + 1):
            if self.find(trace[i]) != self.find(trace[i + n]):
                out.append(tuple(program[i:i + n]))
        return out


def parent_egraph(programs, candidates) -> dict:
    egg = TinyEGraph()
    traces = [egg.add_program(p) for p in programs]
    rounds = egg.saturate()
    pool = set(candidates)
    votes = Counter()
    identity_cancelled = 0
    for program, trace in zip(programs, traces):
        for n in (2, 3, 4):
            grams = egg.irreducible_ngrams(program, trace, n)
            cancelled = max(0, len(program) - n + 1 - len(grams))
            identity_cancelled += cancelled
            for frag in grams:
                if frag in pool:
                    votes[frag] += 1
    order = {c: i for i, c in enumerate(candidates)}
    chosen = max(votes, key=lambda f: (votes[f], len(f), -order[f])) if votes else ()
    return {
        "chosen": list(chosen) if chosen else [],
        "saturate_rounds": rounds,
        "nodes": len(egg.nodes),
        "eclasses": len({egg.find(i) for i in range(len(egg.nodes))}),
        "identity_cancelled_windows": identity_cancelled,
        "corpus_votes": {" ".join(f): n for f, n in sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))},
        "rules": ["inc(dec(x)) = x", "dec(inc(x)) = x", "congruence hashcons"],
    }


def parent_grammar_induction(programs, candidates) -> dict:
    """Trivial right-linear grammar: count productions, emit the hottest bigram."""
    productions = Counter()
    for program in programs:
        program = tuple(program)
        if not program:
            productions[("S", "ε")] += 1
            continue
        productions[("S", program[0])] += 1
        for a, b in zip(program, program[1:]):
            productions[(a, b)] += 1
        productions[(program[-1], "ε")] += 1
    binary = {k: v for k, v in productions.items() if k[0] in PRIMITIVES and k[1] in PRIMITIVES}
    order = {c: i for i, c in enumerate(candidates)}
    if not binary:
        chosen = ()
    else:
        # Prefer a production that is already a frozen candidate, else the raw bigram.
        pool_hits = {frag: binary[frag] for frag in candidates if len(frag) == 2 and frag in binary}
        if pool_hits:
            chosen = max(pool_hits, key=lambda f: (pool_hits[f], -order[f]))
        else:
            chosen = max(binary, key=lambda k: (binary[k], k))
    return {
        "chosen": list(chosen) if chosen else [],
        "n_productions": len(productions),
        "n_binary_productions": len(binary),
        "top_binary": [
            {"production": list(k), "count": binary[k]}
            for k in sorted(binary, key=lambda k: (-binary[k], k))[:5]
        ],
    }


def _require_agreement(live_key: str, frozen_key: str, name: str) -> None:
    if live_key != frozen_key:
        raise RuntimeError(
            "%s live choice %r diverged from frozen %r; refusing to retune"
            % (name, live_key, frozen_key)
        )


def score_row(parent_id: str, box: str, chosen, frozen: dict, extra: dict,
              origin: str, prior: dict, disposition: str, residual: str) -> dict:
    fragment = as_tuple(chosen) if chosen else ()
    utility = lookup_utility(fragment, frozen) if fragment else {
        "chosen_key": None,
        "in_frozen_pool": False,
        "validation_saving": None,
        "utility_rank_of_pool": None,
        "matches_search_aware": False,
        "matches_tournament": False,
    }
    cost = integration_cost(fragment if fragment else None)
    row = {
        "parent": parent_id,
        "box": box,
        "chosen": list(fragment) if fragment else [],
        "origin_identity": origin,
        "prior_information": prior,
        "integration_cost": cost,
        "disposition": disposition,
        "residual_after_subtraction": residual,
        **utility,
        **extra,
    }
    if row["disposition"] not in DISPOSITIONS:
        raise RuntimeError("illegal disposition %s" % row["disposition"])
    return row


def dispositions_for(utility: dict, kind: str) -> tuple[str, str]:
    """What OCM should do with this parent versus SEARCH_AWARE / the tournament."""
    match = bool(utility.get("matches_search_aware"))
    if kind == "search_aware":
        return (
            "ADOPT",
            "None at this ecology for SELECTION. SEARCH_AWARE already is the "
            "conventional parent that prices grammar width in closed form. No "
            "OCM-specific residual.",
        )
    if kind == "tournament":
        return (
            "ADAPT",
            "The tournament found the same object and is the utility ground "
            "truth, but its 9,010,526 enumeration attempts are integration "
            "cost. Keep the objective; replace the search with the SEARCH_AWARE scan.",
        )
    if kind == "compression":
        return (
            "REJECT",
            "Compression / Stitch-style FAILED the argmax: frozen MDL and "
            "per-token both chose dec square (rank 13, validation −93,883, "
            "test −609,213) against square dec square (rank 1, +92,599 / "
            "+275,329). Residual after subtraction is the grammar-width term "
            "SEARCH_AWARE adds. Not retuned.",
        )
    if kind == "generalize_scan":
        return (
            "GENERALIZE",
            "Keep the scan (zero enumeration, training programs only) and "
            "generalize the objective from corpus MDL to search description "
            "length. That generalization already has a name: SEARCH_AWARE. "
            "Residual after subtracting raw compression is grammar widening.",
        )
    if kind == "adapt_mining":
        return (
            "GENERALIZE",
            "Keep domain-native fragment mining on primitive solutions as the "
            "candidate generator. Do not use frequency / production-count as "
            "the admission objective; generalize admission to SEARCH_AWARE.",
        )
    if match:
        return (
            "ADAPT",
            "This parent proposed the tournament object by another route. "
            "Residual after subtraction is SEARCH_AWARE's justification "
            "(closed-form width), which this parent does not compute.",
        )
    if not utility.get("in_frozen_pool"):
        return (
            "OPEN",
            "Proposed fragment is outside the frozen 16-candidate pool, so "
            "validation utility is not looked up (tournament not rerun). "
            "Not the SEARCH_AWARE object.",
        )
    return (
        "REJECT",
        "Proposed a different fragment than SEARCH_AWARE/tournament. Frozen "
        "validation utility is strictly worse than square dec square. Residual "
        "after subtraction is the width-aware selector, not a new abstraction.",
    )


def run() -> dict:
    blob = pin_methods()
    frozen = load_frozen()
    g2, acq = _ensure_harness()
    if git_blob_sha1(SRC / "ocm" / "learning" / "methods.py") != frozen["reused_from_192"]["method_blob"]:
        raise RuntimeError("methods blob drifted from the frozen economics receipt")

    _population, training, _validation, _test = g2.frozen_partition()
    training_rows, training_slots = g2.solve_training(training)
    candidates, support = g2.candidate_pool(training_rows)
    live_keys = [key_of(c) for c in candidates]
    if live_keys != frozen["candidates"]:
        raise RuntimeError("live candidate pool drifted from frozen economics; refusing to retune")
    programs = [tuple(result.program) for _task, result in training_rows]

    work = empty_work()
    mdl_scores = acq.score_compression(candidates, support, training_rows, work)
    mdl_choice = argmax_scores(mdl_scores, candidates)
    _require_agreement(key_of(mdl_choice), COMPRESSION_KEY, "MDL_COMPRESSION")

    work_pt = empty_work()
    pt_scores = acq.score_compression_per_token(candidates, support, training_rows, work_pt)
    pt_choice = argmax_scores(pt_scores, candidates)
    _require_agreement(key_of(pt_choice), COMPRESSION_KEY, "COMPRESSION_PER_TOKEN")

    work_sa = empty_work()
    sa_scores = acq.score_search_aware(candidates, support, training_rows, work_sa)
    sa_choice = argmax_scores(sa_scores, candidates)
    _require_agreement(key_of(sa_choice), SEARCH_AWARE_KEY, "SEARCH_AWARE")

    freq_choice = candidates[0]
    _require_agreement(key_of(freq_choice), COMPRESSION_KEY, "FREQUENCY/domain-native")

    au = parent_antiunification(programs, candidates)
    gi = parent_grammar_induction(programs, candidates)
    egg = parent_egraph(programs, candidates)

    frozen_hash = hashlib.sha256(FROZEN_PATH.read_bytes()).hexdigest()
    prior_scan = {
        "training_programs": len(programs),
        "training_search_slots": training_slots,
        "primitive_library": list(PRIMITIVES),
        "kind": "verified primitive solutions from #192, not the 9e6 tournament",
    }

    def util(chosen):
        return lookup_utility(as_tuple(chosen), frozen)

    parents = []

    stitch_disp, stitch_res = dispositions_for(util(pt_choice), "compression")
    parents.append(score_row(
        "stitch-style-library", G22_BOXES[0], pt_choice, frozen,
        extra={
            "selector_instantiated": "COMPRESSION_PER_TOKEN",
            "acquisition_work": work_pt,
            "agrees_with_frozen_selector": True,
            "live_score": pt_scores[pt_choice],
            "frozen_score": frozen_selector(frozen, "COMPRESSION_PER_TOKEN")["scores"][key_of(pt_choice)],
            "full_system_runtime": {
                "disposition": "OPEN",
                "reason": "CANNOT_CHECK: Stitch is not pip-installed; tiny per-token compressor only",
            },
        },
        origin="stitch-style-library",
        prior=dict(prior_scan, idea="Bowers/Ellis Stitch: compress the training corpus by a syntactic fragment"),
        disposition=stitch_disp,
        residual=stitch_res,
    ))

    dc_disp, dc_res = dispositions_for(util(mdl_choice), "compression")
    parents.append(score_row(
        "dreamcoder-class-abstraction", G22_BOXES[1], mdl_choice, frozen,
        extra={
            "selector_instantiated": "MDL_COMPRESSION",
            "sleep_cycles": 1,
            "wake_recognition_model": "not-executed",
            "dreamcoder_runtime": "absent-tiny-sleep-only",
            "acquisition_work": work,
            "agrees_with_frozen_selector": True,
            "full_system_runtime": {
                "disposition": "OPEN",
                "reason": "CANNOT_CHECK: DreamCoder runtime is not pip-installed; tiny one-sleep MDL only",
            },
        },
        origin="dreamcoder-class-abstraction",
        prior=dict(prior_scan, idea="DreamCoder sleep: invent a library entry that compresses solved programs; wake/neural recognition not run"),
        disposition=dc_disp,
        residual=dc_res,
    ))

    au_disp, au_res = dispositions_for(util(au["chosen"]), "antiunification")
    parents.append(score_row(
        "anti-unification", G22_BOXES[2], au["chosen"], frozen,
        extra={
            "pair_programs": au["pair_programs"],
            "pair_extracts": au["pair_extracts"],
            "corpus_votes": au["corpus_votes"],
            "corpus_pairs": au["corpus_pairs"],
            "acquisition_work": empty_work(),
        },
        origin="anti-unification",
        prior={
            "training_programs_for_the_primitive": au["prior_programs"],
            "corpus_pairs_for_the_vote": au["corpus_pairs"],
            "primitive_library": list(PRIMITIVES),
            "kind": "two training programs for LGG; all pairs for the vote",
        },
        disposition=au_disp,
        residual=au_res,
    ))

    gi_disp, gi_res = dispositions_for(util(gi["chosen"]), "antiunification")
    parents.append(score_row(
        "grammar-induction", G22_BOXES[3], gi["chosen"], frozen,
        extra={
            "n_productions": gi["n_productions"],
            "n_binary_productions": gi["n_binary_productions"],
            "top_binary": gi["top_binary"],
            "acquisition_work": empty_work(),
        },
        origin="grammar-induction",
        prior=dict(prior_scan, idea="count right-linear productions; hottest primitive bigram becomes the library token"),
        disposition=gi_disp,
        residual=gi_res,
    ))

    egg_disp, egg_res = dispositions_for(util(egg["chosen"]), "antiunification")
    parents.append(score_row(
        "egraph-rewrite", G22_BOXES[4], egg["chosen"], frozen,
        extra={
            "saturate_rounds": egg["saturate_rounds"],
            "nodes": egg["nodes"],
            "eclasses": egg["eclasses"],
            "identity_cancelled_windows": egg["identity_cancelled_windows"],
            "corpus_votes": egg["corpus_votes"],
            "rules": egg["rules"],
            "acquisition_work": empty_work(),
            "full_system_runtime": {
                "disposition": "OPEN",
                "reason": "CANNOT_CHECK: egg/eqsat is not pip-installed; tiny hashcons + two cancel rules only",
            },
        },
        origin="egraph-rewrite",
        prior=dict(prior_scan, idea="tiny hashcons e-graph; cancel inc/dec pairs; extract irreducible n-grams"),
        disposition=egg_disp,
        residual=egg_res,
    ))

    comp_disp, comp_res = dispositions_for(util(mdl_choice), "generalize_scan")
    parents.append(score_row(
        "program-compression", G22_BOXES[5], mdl_choice, frozen,
        extra={
            "selector_instantiated": "MDL_COMPRESSION",
            "acquisition_work": work,
            "agrees_with_frozen_selector": True,
            "citation": (
                "g2-acquisition-economics-v1: MDL_COMPRESSION rho=+0.518 yet argmax "
                "rank 13. SEARCH_AWARE rho=+0.531 argmax rank 1. Not retuned."
            ),
        },
        origin="program-compression",
        prior=dict(prior_scan, idea="MDL description length of the rewritten training corpus plus |fragment|"),
        disposition=comp_disp,
        residual=comp_res,
    ))

    native_disp, native_res = dispositions_for(util(freq_choice), "adapt_mining")
    parents.append(score_row(
        "domain-native-induction", G22_BOXES[6], freq_choice, frozen,
        extra={
            "selector_instantiated": "FREQUENCY",
            "support": {key_of(c): support[c] for c in candidates},
            "acquisition_work": {"token_operations": len(candidates), "enumeration_attempts": 0, "unique_checks": 0},
            "agrees_with_frozen_selector": True,
        },
        origin="domain-native-induction",
        prior=dict(prior_scan, idea="methods.py primitive BFS solutions, then proper-fragment support (the #192 miner)"),
        disposition=native_disp,
        residual=native_res,
    ))

    conv_disp, conv_res = dispositions_for(util(sa_choice), "search_aware")
    parents.append(score_row(
        "conventional-same-library", G22_BOXES[7], sa_choice, frozen,
        extra={
            "selector_instantiated": "SEARCH_AWARE",
            "acquisition_work": work_sa,
            "agrees_with_frozen_selector": True,
            "tournament_twin": {
                "disposition": "ADAPT",
                "chosen": list(frozen["tournament"]["choice"]),
                "acquisition_enumeration_attempts": frozen["tournament"]["acquisition_enumeration_attempts"],
                "note": "same primitive library, same object; do not pay 9,010,526 attempts again",
            },
            "live_score": sa_scores[sa_choice],
            "frozen_score": frozen_selector(frozen, "SEARCH_AWARE")["scores"][key_of(sa_choice)],
        },
        origin="conventional-same-library",
        prior=dict(prior_scan, idea="same {inc,dec,double,square} token grammar; SEARCH_AWARE prices width without a tournament"),
        disposition=conv_disp,
        residual=conv_res,
    ))

    by_parent = {row["parent"]: row for row in parents}
    compression_class = [
        by_parent["stitch-style-library"],
        by_parent["dreamcoder-class-abstraction"],
        by_parent["program-compression"],
        by_parent["grammar-induction"],
        by_parent["domain-native-induction"],
    ]
    compression_class_wrong = all(
        not row["matches_search_aware"] for row in compression_class
    )
    adopted = [row["parent"] for row in parents if row["disposition"] == "ADOPT"]
    rejected = [row["parent"] for row in parents if row["disposition"] == "REJECT"]
    dispositions_used = set()
    for row in parents:
        dispositions_used.add(row["disposition"])
        twin = row.get("tournament_twin")
        if twin:
            dispositions_used.add(twin["disposition"])
        runtime = row.get("full_system_runtime")
        if runtime:
            dispositions_used.add(runtime["disposition"])
    any_parent_reran_search = any(
        (row.get("acquisition_work") or {}).get("enumeration_attempts", 0)
        for row in parents
    )
    if any_parent_reran_search:
        raise RuntimeError("a parent charged enumeration_attempts; tournament must not rerun")

    if (
        compression_class_wrong
        and by_parent["conventional-same-library"]["matches_search_aware"]
        and by_parent["conventional-same-library"]["disposition"] == "ADOPT"
        and by_parent["stitch-style-library"]["disposition"] == "REJECT"
        and by_parent["program-compression"]["disposition"] == "GENERALIZE"
    ):
        terminal = "CONVENTIONAL_LIBRARY_PARENTS_SUBORDINATE_TO_SEARCH_AWARE"
        terminal_reason = (
            "On the frozen #192 polynomial ecology, every compression-class "
            "library-learning parent (Stitch-style per-token, DreamCoder-class "
            "one-sleep MDL, raw program compression, production-count grammar "
            "induction, domain-native frequency mining) proposes `dec square`. "
            "The frozen utility tournament and SEARCH_AWARE both propose "
            "`square dec square`. Compression already FAILED that argmax in "
            "g2-acquisition-economics-v1 (rho +0.518, rank 13 / 16, validation "
            "saving −93,883, test saving −609,213) and is not retuned here. "
            "SEARCH_AWARE collects the tournament object at 4,608 token operations "
            "and zero enumeration attempts against 9,010,526. "
            "ADOPT SEARCH_AWARE. REJECT compression / Stitch / DreamCoder-class "
            "as a selection objective. GENERALIZE the scan. That earns the G2.2 "
            "compare boxes without claiming OCM invented library learning."
        )
    else:
        terminal = "LIBRARY_PARENT_DISPOSITIONS_RECORDED"
        terminal_reason = (
            "Donor dispositions recorded on the frozen ecology; compression-class "
            "subordination did not fire under the registered rule."
        )

    box_mapping = {row["box"]: {
        "parent": row["parent"],
        "disposition": row["disposition"],
        "chosen": row["chosen"],
        "origin_identity": row["origin_identity"],
        "validation_saving": row["validation_saving"],
        "utility_rank_of_pool": row["utility_rank_of_pool"],
        "grammar_width_delta": row["integration_cost"]["grammar_width_delta"],
    } for row in parents}

    missing = [box for box in G22_BOXES if box not in box_mapping]
    if missing:
        raise RuntimeError("unmapped G2.2 boxes: %s" % missing)

    return {
        "schema": SCHEMA,
        "authority": (
            "Research-only. Tiny parents instantiate the IDEA of Stitch, "
            "DreamCoder sleep, anti-unification, grammar induction and e-graph "
            "extraction on {inc,dec,double,square}. Utility numbers are imported "
            "from the frozen g2-acquisition-economics-v1 receipt. The 9,010,526-"
            "attempt tournament is not rerun. No production change, no ML, no "
            "src edit, no pip-installed DreamCoder/Stitch. No OCM-specific claim."
        ),
        "methods_blob": blob,
        "imported_receipt": {
            "path": str(FROZEN_PATH.relative_to(REPO)),
            "sha256": frozen_hash,
            "schema": frozen["schema"],
            "terminal": frozen["verdict"]["terminal"],
            "tournament_choice": list(frozen["tournament"]["choice"]),
            "tournament_acquisition_enumeration_attempts": frozen["tournament"]["acquisition_enumeration_attempts"],
            "compression_failed_argmax": True,
            "compression_choice": COMPRESSION_KEY,
            "search_aware_choice": SEARCH_AWARE_KEY,
            "citation": (
                "compression/Stitch-style FAILED argmax vs tournament; "
                "SEARCH_AWARE succeeded. Not retuned."
            ),
        },
        "primitive_library": list(PRIMITIVES),
        "training_n": len(programs),
        "training_search_slots": training_slots,
        "candidates": live_keys,
        "parents": parents,
        "box_mapping": box_mapping,
        "adopt": adopted,
        "reject": rejected,
        "g22_boxes": list(G22_BOXES),
        "dispositions_used": sorted(dispositions_used),
        "compression_class_subordinate": compression_class_wrong,
        "tournament_rerun": False,
        "terminal": terminal,
        "terminal_reason": terminal_reason,
        "claim_ceiling": (
            "G2.2 donor dispositions at the frozen polynomial ecology. Not a new "
            "G2.4 causal-reuse positive. Not a claim that OCM invented library "
            "learning. SEARCH_AWARE is a conventional parent."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    doc = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal": doc["terminal"],
        "adopt": doc["adopt"],
        "reject": doc["reject"],
        "dispositions_used": doc["dispositions_used"],
        "tournament_rerun": doc["tournament_rerun"],
        "imported_terminal": doc["imported_receipt"]["terminal"],
        "chosen": {row["parent"]: " ".join(row["chosen"]) for row in doc["parents"]},
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
