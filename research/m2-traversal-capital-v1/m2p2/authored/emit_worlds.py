#!/usr/bin/env python3
"""emit_worlds.py -- hidden-chunk arithmetic puzzle worlds.

Writes `worlds.jsonl` into the CURRENT WORKING DIRECTORY (the directory the
script is run from).  Deterministic; standard library only; pure computation
(no file reads, no environment, no network, no threads, no wall clock).

    python3 emit_worlds.py

Besides the hand-authored world table, the file carries a small self-contained
*projector* of the frozen public substrate (four ops, builders of length <= 8,
canonical order, chunk tiling).  It is used for exactly two things: to size the
two "drawn-lot" worlds (fixed-seed draws are accepted or rejected on projected
membership) and to record the author's projected member counts inside each
world's `intent` block.  Projections are recorded as expectations, nothing more.
"""
import json

OPS = ("add1", "sub1", "dbl", "sqr")
MAX_LEN = 8
MASK64 = (1 << 64) - 1
OUT_NAME = "worlds.jsonl"


# ------------------------------------------------------------------ substrate
def apply_op(op, p):
    """p: tuple of integer coefficients, lowest degree first; leading coeff != 0."""
    if op == "add1":
        return (p[0] + 1,) + p[1:]
    if op == "sub1":
        return (p[0] - 1,) + p[1:]
    if op == "dbl":
        return tuple(2 * c for c in p)
    n = len(p)
    out = [0] * (2 * n - 1)
    for i in range(n):
        a = p[i]
        if not a:
            continue
        out[2 * i] += a * a
        for j in range(i + 1, n):
            b = p[j]
            if b:
                out[i + j] += 2 * a * b
    return tuple(out)


def canonical_builders():
    """Every canonical builder of length <= MAX_LEN, listed in the public order."""
    by_len = [[] for _ in range(MAX_LEN + 1)]

    def walk(builder, poly):
        by_len[len(builder)].append((builder, poly))
        if len(builder) == MAX_LEN:
            return
        for op in OPS:  # child order == lex order, so each level is lex-sorted
            walk(builder + (op,), apply_op(op, poly))

    walk((), (0, 1))
    seen = set()
    canon = []
    for level in by_len:  # shorter first
        for builder, poly in level:
            if poly not in seen:
                seen.add(poly)
                canon.append(builder)
    return canon


def tilings(builder, chunks):
    """All exact decompositions of `builder` into `chunks` (as index tuples)."""
    n = len(builder)
    found = []

    def rec(i, acc):
        if i == n:
            found.append(tuple(acc))
            return
        for ci, ch in enumerate(chunks):
            k = len(ch)
            if builder[i:i + k] == ch:
                acc.append(ci)
                rec(i + k, acc)
                acc.pop()

    rec(0, [])
    return found


def project(chunks, min_len, canon):
    chunks = [tuple(c) for c in chunks]
    total, by_len, usage, ambiguous = 0, {}, [0] * len(chunks), 0
    for b in canon:
        if len(b) < min_len:
            continue
        ts = tilings(b, chunks)
        if not ts:
            continue
        total += 1
        by_len[len(b)] = by_len.get(len(b), 0) + 1
        used = set()
        for t in ts:
            used.update(t)
        for ci in used:
            usage[ci] += 1
        if len(ts) > 1:
            ambiguous += 1
    return {"total": total, "by_len": by_len, "usage": usage, "ambiguous": ambiguous}


# -------------------------------------------------------------- drawn worlds
def lcg(seed):
    """64-bit MMIX linear congruential generator; version-independent."""
    s = seed & MASK64
    while True:
        s = (s * 6364136223846793005 + 1442695040888963407) & MASK64
        yield s >> 33


def draw_chunks(pool, k, seed):
    rng = lcg(seed)
    remaining = list(pool)
    picked = []
    for _ in range(k):
        picked.append(remaining.pop(next(rng) % len(remaining)))
    return picked


def accept_draw(pr):
    return pr["total"] >= 40 and len(pr["by_len"]) >= 2 and min(pr["usage"]) >= 1


# ------------------------------------------------------------- world table
PROJECTION_METHOD = (
    "self-contained enumeration of every builder of length <= 8 under the frozen "
    "public semantics, run inside emit_worlds.py; recorded as the author's "
    "expectation, not as ground truth"
)

HAND_WORLDS = [
    {
        "world_id": "hc01-binary-ladder",
        "chunks": [["add1", "dbl"], ["sub1", "dbl"], ["dbl", "add1"],
                   ["dbl", "sub1"], ["dbl", "dbl"], ["add1", "add1", "dbl"]],
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.5, "tuning": 0.25, "future": 0.25},
        "surface": {
            "name": "Binary ladder",
            "story": "No squaring anywhere: every member is a straight line "
                     "2^k x + c. The chunks are rungs of a binary ladder: a "
                     "doubling glued to a single +1 or -1 on either side, a bare "
                     "double-double, and one three-step rung (+2 then double).",
            "why_it_bites": "All members look alike (lines with power-of-two "
                            "slope). The only signal is which constants occur "
                            "for each slope and how the canonical builder places "
                            "its single +1/-1 steps between doublings; the bare "
                            "[dbl,dbl] rung and the [add1,add1,dbl] rung are hard "
                            "to separate from compositions of the two-step rungs.",
            "chunk_lengths": "five 2-chunks, one 3-chunk",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "single-degree world: all members linear; sub1 only "
                           "ever appears glued to a doubling",
            "expected_recurring_chunks": [["dbl", "add1"], ["add1", "dbl"], ["dbl", "dbl"]],
            "expected_difficulty": "medium",
        },
    },
    {
        "world_id": "hc02-square-shift",
        "chunks": [["sqr", "add1"], ["add1", "sqr"], ["sqr", "sub1"],
                   ["sub1", "sqr"], ["dbl", "sqr"], ["sqr", "dbl"]],
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.4375, "tuning": 0.1875, "future": 0.375},
        "surface": {
            "name": "Square and shift",
            "story": "Every chunk is one squaring glued to one neighbour: a +1 "
                     "or -1 before or after the square, or a doubling before or "
                     "after it. Members are towers of squares with small shifts "
                     "between floors, like ((x+1)^2-1)^2+1.",
            "why_it_bites": "Only even builder lengths occur, and a member of "
                            "length 2m always carries exactly m squarings. The "
                            "observer must decide whether a shift belongs to the "
                            "square before it or the square after it.",
            "chunk_lengths": "six 2-chunks",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "every chunk contains sqr, so squaring count equals "
                           "half the builder length for every member",
            "expected_recurring_chunks": [["sqr", "add1"], ["add1", "sqr"], ["sqr", "sub1"]],
            "expected_difficulty": "medium",
        },
    },
    {
        "world_id": "hc03-shift-runs",
        "chunks": [["add1", "add1"], ["add1", "add1", "add1"], ["sub1", "sub1"],
                   ["sub1", "sub1", "sub1"], ["add1", "sqr"], ["sqr", "add1"],
                   ["sub1", "sqr"], ["sqr", "sub1"]],
        "min_builder_length": 5,
        "part_fractions": {"initial": 0.375, "tuning": 0.25, "future": 0.375},
        "surface": {
            "name": "Shift runs",
            "story": "Runs of +1 or -1 of length two and three, plus the four "
                     "ways of gluing a single shift to a square. The runs "
                     "overlap: six +1 steps tile as 2+2+2 or 3+3, five as 2+3 "
                     "or 3+2.",
            "why_it_bites": "Deliberate ambiguity. Many members admit several "
                            "tilings, so no single member pins down which run "
                            "lengths are in the set, and the pure-shift members "
                            "x+k, x-k (k = 5..8) look as if one chunk kind would do.",
            "chunk_lengths": "four 2-chunks, four 3-chunks",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "overlapping chunks (a run of +1s is both 2-chunk and "
                           "3-chunk material) to maximise multi-tiling members",
            "expected_recurring_chunks": [["add1", "add1"], ["sqr", "add1"], ["add1", "sqr"]],
            "expected_difficulty": "hard (ambiguity), but small in degree",
        },
    },
    {
        "world_id": "hc04-seven-triads",
        "chunks": [["add1", "add1", "dbl"], ["dbl", "add1", "dbl"],
                   ["sqr", "add1", "add1"], ["add1", "sqr", "dbl"],
                   ["dbl", "sub1", "sqr"], ["sqr", "dbl", "add1"],
                   ["sub1", "sqr", "add1"]],
        "min_builder_length": 6,
        "part_fractions": {"initial": 0.5, "tuning": 0.25, "future": 0.25},
        "surface": {
            "name": "Seven triads",
            "story": "Seven three-step chunks and nothing shorter; under the "
                     "eight-step ceiling every member is exactly two chunks "
                     "(six steps) long. The triads were chosen by hand so that "
                     "most ordered pairs stay canonical.",
            "why_it_bites": "One length class and a small membership: the world "
                            "is a 7x7 pairing table with holes wherever a pair "
                            "collapses to a shorter builder (for example "
                            "[add1,add1,dbl] twice is 4x+12, which has a "
                            "five-step builder).",
            "chunk_lengths": "seven 3-chunks",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "triads only, so membership is a pairing table; hand "
                           "count of canonical pairs gave about 32 of 49",
            "expected_recurring_chunks": [["sqr", "add1", "add1"], ["dbl", "sub1", "sqr"],
                                          ["add1", "add1", "dbl"]],
            "expected_difficulty": "easy to enumerate, hard to be sure of the set",
        },
    },
    {
        "world_id": "hc05-long-form",
        "chunks": [["add1", "dbl"], ["dbl", "add1"], ["sqr", "add1"], ["add1", "sqr"],
                   ["dbl", "sqr", "add1"], ["sqr", "sub1", "dbl"], ["sub1", "dbl", "sub1"]],
        "min_builder_length": 8,
        "part_fractions": {"initial": 0.5625, "tuning": 0.125, "future": 0.3125},
        "surface": {
            "name": "Long form",
            "story": "Minimum builder length pinned at the ceiling, so only the "
                     "longest canonical builders qualify; four two-step and "
                     "three three-step chunks tile length eight as 2+2+2+2, "
                     "2+3+3, 3+2+3 or 3+3+2.",
            "why_it_bites": "A single length class at the top of the range, "
                            "mixing lines, quadratics and quartics; the -1 steps "
                            "live only inside the three-step chunks, so a member "
                            "containing sub1 reveals a long chunk but not which.",
            "chunk_lengths": "four 2-chunks, three 3-chunks",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "min length = ceiling; members are all maximal-length "
                           "canonical builders",
            "expected_recurring_chunks": [["dbl", "add1"], ["sqr", "add1"], ["add1", "sqr"]],
            "expected_difficulty": "medium-hard",
        },
    },
    {
        "world_id": "hc06-decoy-pair",
        "chunks": [["dbl", "sqr"], ["sqr", "dbl"], ["add1", "sqr"], ["sqr", "sub1"],
                   ["dbl", "add1"], ["add1", "sub1"], ["sqr", "dbl", "dbl"]],
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.375, "tuning": 0.1875, "future": 0.4375},
        "surface": {
            "name": "Decoy pair",
            "story": "Five live two-step chunks plus two decoys that can never "
                     "occur inside a canonical builder: [add1,sub1] cancels to "
                     "nothing, and [sqr,dbl,dbl] is always beaten by the shorter "
                     "[dbl,sqr]. The decoys belong to the hidden set but "
                     "contribute no members.",
            "why_it_bites": "Every member has even length and uses only the five "
                            "live chunks, so the visible world cannot be told "
                            "apart from a five-chunk world; the chunk count and "
                            "the existence of a three-step chunk are invisible "
                            "by construction.",
            "chunk_lengths": "six 2-chunks, one 3-chunk",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "hidden chunks that leave no trace: two never-canonical "
                           "fragments among five live ones",
            "expected_recurring_chunks": [["dbl", "sqr"], ["add1", "sqr"], ["sqr", "sub1"]],
            "expected_dead_chunks": [["add1", "sub1"], ["sqr", "dbl", "dbl"]],
            "expected_difficulty": "structurally unresolvable for the decoys",
        },
    },
    {
        "world_id": "hc09-negative-ladder",
        "chunks": [["sub1", "dbl"], ["dbl", "sub1"], ["sub1", "sqr"], ["sqr", "sub1"],
                   ["sub1", "sub1", "dbl"], ["dbl", "dbl", "sub1"]],
        "min_builder_length": 5,
        "part_fractions": {"initial": 0.5, "tuning": 0.25, "future": 0.25},
        "surface": {
            "name": "Negative ladder",
            "story": "The mirror image of the binary ladder, built around -1 "
                     "instead of +1, with two squaring glues so that a few "
                     "parabolas creep in among the lines: 2x-3, 4x-9, "
                     "(2x-4)^2-1 and their kin.",
            "why_it_bites": "Because add1 sorts before sub1, a sub1-built builder "
                            "is canonical only when no add1-based builder of the "
                            "same length exists, so the membership is skewed "
                            "toward constants sitting just below a power-of-two "
                            "multiple; the two three-step rungs are rare.",
            "chunk_lengths": "four 2-chunks, two 3-chunks",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "sub1-only shifts; tests whether the add1-before-sub1 "
                           "tie-break thins the world",
            "expected_recurring_chunks": [["dbl", "sub1"], ["sub1", "dbl"], ["sqr", "sub1"]],
            "expected_difficulty": "medium",
        },
    },
    {
        "world_id": "hc10-quartic-climb",
        "chunks": [["sqr", "sqr"], ["sqr", "add1"], ["add1", "sqr"],
                   ["sqr", "sqr", "add1"], ["dbl", "sqr"], ["sub1", "sqr", "sqr"]],
        "min_builder_length": 6,
        "part_fractions": {"initial": 0.375, "tuning": 0.25, "future": 0.375},
        "surface": {
            "name": "Quartic climb",
            "story": "Squares of squares: a double square, a double square "
                     "with +1, a -1 before a double square, a doubling before a "
                     "square, and the two small +1 glues. Members are towers of "
                     "degree 4, 8, 16 and beyond with tiny shifts between floors.",
            "why_it_bites": "Degrees explode and coefficients grow huge, so "
                            "members look wildly different as polynomials while "
                            "their builders are near-identical; [sqr,sqr,add1] "
                            "overlaps [sqr,sqr] followed by [add1,sqr], so long "
                            "square towers tile in more than one way.",
            "chunk_lengths": "four 2-chunks, two 3-chunks",
        },
        "intent": {
            "intent_role": "audit_only",
            "design_idea": "high-degree world with overlapping 2/3-chunks built "
                           "from repeated squaring",
            "expected_recurring_chunks": [["sqr", "sqr"], ["sqr", "add1"], ["add1", "sqr"]],
            "expected_difficulty": "medium-hard",
        },
    },
]

DRAWN_WORLDS = [
    {
        "world_id": "hc07-drawn-lot-a",
        "k": 5,
        "base_seed": 7001,
        "min_builder_length": 5,
        "part_fractions": {"initial": 0.5, "tuning": 0.1875, "future": 0.3125},
        "name": "Drawn lot A",
    },
    {
        "world_id": "hc08-drawn-lot-b",
        "k": 8,
        "base_seed": 8001,
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.4375, "tuning": 0.25, "future": 0.3125},
        "name": "Drawn lot B",
    },
]


# ------------------------------------------------------------------ assembly
def validate(w):
    ch = [tuple(c) for c in w["chunks"]]
    assert 4 <= len(ch) <= 8, w["world_id"]
    assert all(len(c) in (2, 3) and all(o in OPS for o in c) for c in ch), w["world_id"]
    assert len(set(ch)) == len(ch), w["world_id"]
    assert 4 <= w["min_builder_length"] <= 8, w["world_id"]
    f = w["part_fractions"]
    assert 0.35 <= f["initial"] <= 0.60, w["world_id"]
    assert 0.10 <= f["tuning"] <= 0.30, w["world_id"]
    assert f["future"] >= 0.25, w["world_id"]
    assert f["initial"] + f["tuning"] + f["future"] == 1.0, w["world_id"]
    assert set(w) == {"world_id", "chunks", "min_builder_length",
                      "part_fractions", "surface", "intent"}, w["world_id"]
    assert w["intent"]["intent_role"] == "audit_only", w["world_id"]


def projection_block(chunks, pr):
    return {
        "method": PROJECTION_METHOD,
        "member_count": pr["total"],
        "members_by_length": {str(k): pr["by_len"][k] for k in sorted(pr["by_len"])},
        "chunk_member_usage": [[list(c), u] for c, u in zip(chunks, pr["usage"])],
        "members_with_multiple_tilings": pr["ambiguous"],
        "dead_chunks": [list(c) for c, u in zip(chunks, pr["usage"]) if u == 0],
    }


def assemble(world_id, chunks, min_len, fractions, surface, intent, canon):
    pr = project(chunks, min_len, canon)
    intent = dict(intent)
    intent["projection"] = projection_block(chunks, pr)
    w = {
        "world_id": world_id,
        "chunks": [list(c) for c in chunks],
        "min_builder_length": min_len,
        "part_fractions": dict(fractions),
        "surface": dict(surface),
        "intent": intent,
    }
    validate(w)
    return w


def build_drawn(spec, canon, pool):
    k, min_len = spec["k"], spec["min_builder_length"]
    for seed in range(spec["base_seed"], spec["base_seed"] + 500):
        chunks = draw_chunks(pool, k, seed)
        pr = project(chunks, min_len, canon)
        if accept_draw(pr):
            break
    else:
        raise RuntimeError("no acceptable draw for " + spec["world_id"])
    order = sorted(range(k), key=lambda i: (-pr["usage"][i], i))
    surface = {
        "name": spec["name"],
        "story": "Chunks drawn by a fixed-seed generator from the pool of every "
                 "two- and three-step builder that is canonical for its own "
                 "polynomial. The first draw was kept whose projected membership "
                 "had at least 40 members over at least two length classes with "
                 "every chunk used by at least one member.",
        "why_it_bites": "No design hand behind the set: whatever regularity an "
                        "observer finds is an accident of the draw, which makes "
                        "it a control against the hand-built worlds.",
        "chunk_lengths": "%d 2-chunks, %d 3-chunks" % (
            sum(1 for c in chunks if len(c) == 2), sum(1 for c in chunks if len(c) == 3)),
    }
    intent = {
        "intent_role": "audit_only",
        "design_idea": "control world: chunk set drawn, not designed",
        "expected_recurring_chunks": [list(chunks[i]) for i in order[:3]],
        "expected_difficulty": "unknown by construction",
        "sampler": {"kind": "lcg64-mmix (a=6364136223846793005, c=1442695040888963407, "
                            "output = state >> 33), draw without replacement",
                    "pool": "canonical builders of length 2 and 3, in public order",
                    "pool_size": len(pool), "base_seed": spec["base_seed"],
                    "accepted_seed": seed, "draws_rejected": seed - spec["base_seed"]},
    }
    return assemble(spec["world_id"], chunks, min_len, spec["part_fractions"],
                    surface, intent, canon)


def main():
    canon = canonical_builders()
    pool = [b for b in canon if len(b) in (2, 3)]
    worlds = [assemble(s["world_id"], s["chunks"], s["min_builder_length"],
                       s["part_fractions"], s["surface"], s["intent"], canon)
              for s in HAND_WORLDS]
    worlds += [build_drawn(s, canon, pool) for s in DRAWN_WORLDS]
    worlds.sort(key=lambda w: w["world_id"])
    assert len({w["world_id"] for w in worlds}) == len(worlds)
    with open(OUT_NAME, "w", encoding="utf-8", newline="\n") as fh:
        for w in worlds:
            fh.write(json.dumps(w, ensure_ascii=True) + "\n")
    # stdout diagnostics only; not part of the artifact
    print("canonical builders:", len(canon), " pool:", len(pool))
    for w in worlds:
        pr = w["intent"]["projection"]
        print(w["world_id"], "members=%d" % pr["member_count"],
              "by_len=%s" % pr["members_by_length"],
              "multi=%d" % pr["members_with_multiple_tilings"],
              "dead=%s" % pr["dead_chunks"])
        print("   chunks:", [(" ".join(c), u) for c, u in pr["chunk_member_usage"]])
        if "sampler" in w["intent"]:
            print("   seed:", w["intent"]["sampler"]["accepted_seed"])


if __name__ == "__main__":
    main()
