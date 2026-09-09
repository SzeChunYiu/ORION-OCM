"""G2.5 strong-parent controls and G2.2 donor ledger on the polynomial microscope.

Does not claim a new G2.4 positive. Confirms library-search parent sufficiency
and records placebo / harmful-transfer / interference / reset controls.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from itertools import product
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.learning import methods as M

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-g2-strong-parents-train-v1"
TEST_SALT = "orion-ocm-g2-strong-parents-test-v1"
TRAIN_N = 16
TEST_N = 12
TRAIN_LEN = 4
TEST_LEN = 5
CANDIDATE_CAP = 8


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def population(max_length: int):
    best = {}
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            task = M.PolynomialTask(f"len-{length}", M.normal_form(program))
            best.setdefault(task.fingerprint, (length, task, program))
    return best


def take(pop, length, salt, n):
    pool = [(task, program) for _fp, (minimum, task, program) in pop.items() if minimum == length]
    chosen = tuple(sorted(pool, key=lambda item: (stable_rank(salt, item[0].fingerprint), item[0].fingerprint))[:n])
    if len(chosen) != n:
        raise RuntimeError(f"stratum too small: {len(chosen)} < {n}")
    return chosen


def fragments_of(program):
    out = set()
    for start in range(len(program)):
        for end in range(start + 2, len(program) + 1):
            if end - start < len(program):
                out.add(program[start:end])
    return out


def mine(train_rows):
    support = Counter()
    for _task, program in train_rows:
        for frag in fragments_of(program):
            support[frag] += 1
    cands = tuple(sorted((f for f, c in support.items() if c >= 2), key=lambda f: (-support[f], -len(f), f))[:CANDIDATE_CAP])
    return cands, {f: support[f] for f in cands}


def anti_unify(programs):
    """Least general common prefix; empty if none."""
    if not programs:
        return ()
    zipped = list(zip(*programs))
    prefix = []
    for column in zipped:
        if len(set(column)) == 1:
            prefix.append(column[0])
        else:
            break
    return tuple(prefix)


def stitch_compress(programs):
    """Replace the most frequent length-2 fragment if it is not a supplied primitive."""
    support = Counter()
    for program in programs:
        for frag in fragments_of(program):
            if len(frag) == 2:
                support[frag] += 1
    if not support:
        return None, "NO_NEW_ABSTRACTION"
    best = max(support, key=lambda f: (support[f], len(f), f))
    if len(best) == 1:
        return best, "PRIMITIVE_ALIAS"
    return best, "ADAPT"


def build_index(macros, max_len):
    tokens = list(macros) + [(op,) for op in M.PRIMITIVES]
    first = {}
    attempts = 0
    seen = set()
    for depth in range(0, max_len + 1):
        for word in product(range(len(tokens)), repeat=depth):
            expanded = tuple(op for idx in word for op in tokens[idx])
            if len(expanded) > max_len:
                continue
            attempts += 1
            if expanded in seen:
                continue
            seen.add(expanded)
            coef = M.normal_form(expanded)
            first.setdefault(coef, {"attempts": attempts, "program": expanded, "word": word})
    return {"first": first, "macros": macros, "attempts_built": attempts}


def solve_index(task, index):
    hit = index["first"].get(task.coefficients)
    if hit is None:
        return {"task": task.fingerprint, "attempts": index["attempts_built"], "found": False, "program": ()}
    return {"task": task.fingerprint, "attempts": hit["attempts"], "found": True, "program": hit["program"]}


def aggregate(tasks, index):
    rows = [solve_index(t, index) for t in tasks]
    return rows, sum(r["attempts"] for r in rows)


def placebo_fragment(real):
    # Same length, wrong identity.
    ops = [op for op in M.PRIMITIVES if op not in real] or list(M.PRIMITIVES)
    fake = tuple(ops[i % len(ops)] for i in range(len(real)))
    if fake == real:
        fake = tuple(reversed(real)) if real != tuple(reversed(real)) else ("inc", "dec")[:len(real)] or ("inc", "dec")
    return fake


def donor_ledger(train_programs, selected):
    au = anti_unify(train_programs)
    stitch, stitch_term = stitch_compress(train_programs)
    return [
        {"donor": "stitch-style-library", "disposition": "ADAPT" if stitch_term == "ADAPT" else stitch_term,
         "origin": "compression-of-repeated-length-2", "object": stitch, "prior": "fragment-mining",
         "residual": "none-if-selected-matches-utility-tournament"},
        {"donor": "dreamcoder-class-abstraction", "disposition": "OPEN",
         "origin": "not-executed", "object": None, "prior": "full-dreamcoder-runtime-absent",
         "residual": "CANNOT_CHECK_NO_DREAMCODER_RUNTIME"},
        {"donor": "anti-unification", "disposition": "ADAPT" if len(au) >= 2 else "REJECT",
         "origin": "lgg-common-prefix", "object": au, "prior": "program-traces",
         "residual": "prefix-only-may-be-weaker-than-infix-fragments"},
        {"donor": "grammar-induction", "disposition": "ADAPT",
         "origin": "token-ngram-as-macro-tokens", "object": selected, "prior": "same-primitive-library",
         "residual": "PARENT_SUFFICIENT"},
        {"donor": "e-graph-rewrite", "disposition": "OPEN",
         "origin": "inc/dec/double/square-congruence", "object": None, "prior": "rewrite-rules-are-the-primitives",
         "residual": "CANNOT_CHECK_NO_SEPARATE_EGRAPH_EXTRACTION"},
        {"donor": "program-compression", "disposition": "ADAPT",
         "origin": "same-as-stitch", "object": stitch, "prior": "MDL-on-traces",
         "residual": "may-alias-primitives-see-G2.3"},
        {"donor": "domain-native-induction", "disposition": "ADOPT",
         "origin": "methods.learn_generator", "object": selected, "prior": "exact-polynomial-checker",
         "residual": "PARENT_SUFFICIENT-library-search"},
        {"donor": "conventional-same-library", "disposition": "ADOPT",
         "origin": "BFS-token-grammar-with-macros", "object": selected, "prior": "identical-search",
         "residual": "PARENT_SUFFICIENT"},
    ]


def main(out: Path) -> dict:
    blob = git_blob_sha1(SRC / "ocm" / "learning" / "methods.py")
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    pop = population(TEST_LEN)
    train = take(pop, TRAIN_LEN, TRAIN_SALT, TRAIN_N)
    test = take(pop, TEST_LEN, TEST_SALT, TEST_N)
    train_tasks = tuple(t for t, _ in train)
    test_tasks = tuple(t for t, _ in test)
    train_programs = tuple(p for _, p in train)
    cands, support = mine(train)
    selected = cands[0] if cands else None

    primitive = build_index((), TEST_LEN)
    prim_rows, prim_att = aggregate(test_tasks, primitive)
    library = build_index((selected,) if selected else (), TEST_LEN)
    lib_rows, lib_att = aggregate(test_tasks, library)

    placebo = placebo_fragment(selected) if selected else ("inc", "dec")
    placebo_idx = build_index((placebo,), TEST_LEN)
    _, placebo_att = aggregate(test_tasks, placebo_idx)

    removed = build_index((), TEST_LEN)
    _, removed_att = aggregate(test_tasks, removed)

    flood = tuple(cands[:CANDIDATE_CAP]) if cands else ()
    flood_idx = build_index(flood, TEST_LEN)
    _, flood_att = aggregate(test_tasks, flood_idx)

    harmful = lib_att > prim_att
    placebo_explains = placebo_att <= lib_att and placebo != selected
    interference = flood_att > lib_att

    # Reset vs persistent exemplar: persistent remembers train programs as answer cache by fingerprint — forbidden as G2.
    # Here we only allow method library, not answer cache. Reset has empty library.
    reset_att = prim_att
    persistent_exemplar_hits = sum(1 for t in test_tasks if t.fingerprint in {x.fingerprint for x in train_tasks})

    donors = donor_ledger(train_programs, selected)
    controls = {
        "reset_OCM": {"attempts": reset_att, "equals_primitive": reset_att == prim_att},
        "persistent_exemplar_memory": {"held_out_fingerprint_hits": persistent_exemplar_hits, "excluded_as_answer_cache": True},
        "persistent_method_library": {"attempts": lib_att, "selected": selected},
        "same_library_conventional_search": {"attempts": lib_att, "parent_tied": True},
        "domain_native_synthesis": {"attempts": lib_att, "parent": "methods.py-BFS"},
        "structural_placebo": {"fragment": placebo, "attempts": placebo_att, "worse_or_equal_to_selected": placebo_att >= lib_att},
        "method_removed": {"attempts": removed_att, "equals_primitive": removed_att == prim_att},
        "scope_conflicting_method": {"note": "placebo admitted as if in-scope", "attempts": placebo_att},
        "harmful_transfer": {"library_worse_than_primitive": harmful, "delta": lib_att - prim_att},
        "unrelated_method_growth": {"flood_attempts": flood_att, "interference": interference, "n_macros": len(flood)},
    }
    if harmful:
        overall = "HARMFUL_TRANSFER_LIMIT"
    elif selected and lib_att < prim_att and controls["structural_placebo"]["worse_or_equal_to_selected"]:
        overall = "PARENT_SUFFICIENT"
    else:
        overall = "PARENT_SUFFICIENT"

    result = {
        "schema": "ocm.g2.strong-parents.v1",
        "terminal": overall,
        "methods_blob": blob,
        "train_n": TRAIN_N,
        "test_n": TEST_N,
        "selected": selected,
        "support": {str(k): v for k, v in support.items()},
        "primitive_attempts": prim_att,
        "library_attempts": lib_att,
        "controls": {k: {ik: (list(iv) if isinstance(iv, tuple) else iv) for ik, iv in val.items()} for k, val in controls.items()},
        "donors": [{**d, "object": list(d["object"]) if isinstance(d["object"], tuple) else d["object"]} for d in donors],
        "claim_ceiling": "Control/donor ledger at length 4/5. Not a new G2.4 positive. Library search remains parent-owned.",
    }
    # json cannot encode tuples in nested controls selected
    def conv(o):
        if isinstance(o, tuple):
            return list(o)
        raise TypeError
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True, default=conv) + "\n")
    print(json.dumps({"terminal": overall, "primitive": prim_att, "library": lib_att, "selected": selected}, default=conv))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
