"""Emit the hidden-chunk arithmetic puzzle worlds of the "studio D" collection.

Running this module writes ``worlds.jsonl`` into the CURRENT WORKING DIRECTORY,
one JSON object per line, one line per world.

Determinism
-----------
There are no seeds and no randomness anywhere in this file.  Every chunk set was
chosen by hand and is stored below as a literal; the emitter is a pure function
of those literals.  Dict literals preserve insertion order, ``json.dumps`` is
called with fixed separators, and all part fractions are dyadic rationals
(k/32), so their decimal repr is exact and their sum is exactly 1.0 in binary
floating point.  Two runs therefore produce byte-identical output.

The vocabulary I build chunks from
----------------------------------
Shorthand used in the comments below: a = add1, s = sub1, d = dbl, q = sqr.

A concatenation of my chunks is only a member of a world if the builder it
spells is the *canonical* builder of the polynomial it computes -- the first one
in the public order.  So the whole craft here is choosing chunks whose
concatenations stay canonical.  Two disciplines do that work:

*The sealing rule.*  Every chunk ends in ``dbl`` or ``sqr``, and no chunk begins
with a repeated ``add1``/``sub1``/``dbl``.  Because a sealed chunk never hands a
shift to its neighbour, this closes shift cancellation (``a,s`` / ``s,a``)
outright, and it closes ``d,a,a`` -> ``a,d`` and ``d,s,s`` -> ``s,d`` at every
seam.  It is NOT complete, and I want to be exact about where it stops: it only
guards the rewrites that take ONE op from the left chunk.  A three-op rewrite
can also straddle a seam two-from-the-left, and two of those survive the rule.
They are listed under "Known residual leaks" below.

*Square density.*  Every chunk carries at least one ``sqr``, most carry two.
Squaring doubles the degree, so a length-8 member of a square-dense world has
degree 16 or more, and the position of each ``sqr`` is pinned by the degree
sequence.  That makes the minimal builder essentially forced, which is what
canonicality needs.  Linear-only builders are the collision-rich zone and I
mostly stay out of it.

Known residual leaks
--------------------
Two three-op rewrites straddle a seam two-from-the-left and so slip past the
sealing rule:

  LEAK-1  ``q,d`` | ``d``   =  ``sqr,dbl,dbl`` -> ``dbl,sqr``
          a chunk ending in sqr-then-dbl, followed by a chunk starting with dbl.
  LEAK-2  ``a,d`` | ``s``   =  ``add1,dbl,sub1`` -> ``dbl,add1``  (mirror ``s,d``|``a``)
          a chunk ending in shift-then-dbl, followed by the opposite shift.

An ordered chunk pair that hits either one spells a builder some shorter builder
already computes, so that concatenation is nobody's canonical builder and the
polynomial is not a member.  I priced these instead of tightening the rule,
because the cost is a few percent of the candidate pairs and I did not want to
give up the vocabulary.  Per-world counts of leaking ordered pairs are in
AUTHOR_NOTES.md.

The one discipline in this collection that IS complete is stricter: end every
chunk in ``sqr`` rather than in dbl-or-sqr.  Then neither leak can form, because
neither rewrite has a ``sqr`` in its second-from-last position.  Two worlds meet
it -- twin_roots by its two-squarings invariant, and deep_well, which I tightened
to it on purpose once I found LEAK-1.
"""

import json

# --- op names ---------------------------------------------------------------

A = "add1"
S = "sub1"
D = "dbl"
Q = "sqr"


WORLDS = [
    {
        "world_id": "brass_lantern",
        # Single-shift vocabulary: add1 only, never sub1.  Six 3-chunks and six
        # 4-chunks, all sealed, all square-bearing.
        "chunks": [
            [A, D, Q],
            [A, Q, D],
            [A, Q, Q],
            [D, A, Q],
            [Q, A, D],
            [Q, A, Q],
            [A, D, Q, D],
            [A, Q, D, Q],
            [A, Q, A, Q],
            [D, A, Q, Q],
            [D, Q, A, Q],
            [Q, A, D, Q],
        ],
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.5, "tuning": 0.21875, "future": 0.28125},
        "surface": {
            "display_name": "The Brass Lantern",
            "one_liner": "Everything climbs. Nothing ever comes back down.",
            "vocabulary": "add1 / dbl / sqr only -- sub1 never appears",
            "chunk_shape": "6 chunks of length 3, 6 of length 4",
            "length_classes_present": [4, 6, 7, 8],
            "seam_discipline": (
                "sealed; immune to LEAK-2 because the world has no sub1 at all, "
                "but 6 of its 144 ordered chunk pairs hit LEAK-1 (sqr,dbl|dbl)"
            ),
            "what_i_think_makes_it_easy": (
                "Every constant in every member is positive, so a solver who "
                "notices the missing sub1 can prune half the op alphabet on sight."
            ),
            "what_i_think_makes_it_hard": (
                "add1 and dbl commute up to a shift, so the same polynomial is "
                "approached from several directions and the solver has to trust "
                "the canonical-order tie-break rather than intuition."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "chunks_i_expect_to_recur_most": [[A, Q, Q], [D, A, Q], [A, Q, D, Q]],
            "chunks_i_expect_to_recur_least": [[A, Q, A, Q]],
            "member_count_guess": 210,
            "member_count_guess_band": [150, 260],
            "confidence": "medium",
            "design_note": (
                "This is the reference world of the collection: the cleanest "
                "possible seam discipline, and the twin of tin_orchard."
            ),
        },
    },
    {
        "world_id": "tin_orchard",
        # Exact sign-mirror of brass_lantern: every add1 replaced by sub1.
        # Same shape, disjoint chunk set.
        "chunks": [
            [S, D, Q],
            [S, Q, D],
            [S, Q, Q],
            [D, S, Q],
            [Q, S, D],
            [Q, S, Q],
            [S, D, Q, D],
            [S, Q, D, Q],
            [S, Q, S, Q],
            [D, S, Q, Q],
            [D, Q, S, Q],
            [Q, S, D, Q],
        ],
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.5, "tuning": 0.21875, "future": 0.28125},
        "surface": {
            "display_name": "The Tin Orchard",
            "one_liner": "The lantern's reflection, with every step taken backwards.",
            "vocabulary": "sub1 / dbl / sqr only -- add1 never appears",
            "chunk_shape": "6 chunks of length 3, 6 of length 4",
            "length_classes_present": [4, 6, 7, 8],
            "seam_discipline": (
                "sealed; immune to LEAK-2 because the world has no add1 at all, "
                "but 6 of its 144 ordered chunk pairs hit LEAK-1 (sqr,dbl|dbl)"
            ),
            "relationship_to_other_worlds": (
                "Identical in shape to brass_lantern, chunk-for-chunk mirrored "
                "under add1 <-> sub1. Deliberately the same shape: it is the "
                "control for 'does the sign of the shift change the world?'"
            ),
            "what_i_think_makes_it_hard": (
                "Squaring destroys the sign, so (x-1)^2 and (x+1)^2 differ only "
                "in the middle coefficient. Members here look far more like "
                "brass_lantern members than the chunk sets do."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "chunks_i_expect_to_recur_most": [[S, Q, Q], [D, S, Q], [S, Q, D, Q]],
            "member_count_guess": 205,
            "member_count_guess_band": [145, 255],
            "confidence": "medium",
            "expectation_vs_twin": (
                "I expect a slightly SMALLER member count than brass_lantern. "
                "sub1 is lexicographically later than add1, so where a member "
                "here ties on length with some add1-flavoured builder, this "
                "world loses the tie-break and the polynomial belongs to no one."
            ),
        },
    },
    {
        "world_id": "narrow_gauge",
        # Sixteen 3-chunks, no 4-chunks at all.  With min 6 the only attainable
        # member length is 6 (3 alone is below the minimum, 9 is over the cap),
        # so the world has exactly one builder-length class.
        "chunks": [
            [A, D, Q],
            [A, Q, D],
            [A, Q, Q],
            [D, A, Q],
            [D, Q, D],
            [D, Q, Q],
            [D, S, Q],
            [Q, A, D],
            [Q, A, Q],
            [Q, S, D],
            [Q, S, Q],
            [Q, D, Q],
            [Q, Q, D],
            [S, D, Q],
            [S, Q, D],
            [S, Q, Q],
        ],
        "min_builder_length": 6,
        "part_fractions": {"initial": 0.4375, "tuning": 0.1875, "future": 0.375},
        "surface": {
            "display_name": "Narrow Gauge",
            "one_liner": "One track, one gauge, one length. Sixteen ways onto it.",
            "vocabulary": "all four ops",
            "chunk_shape": "16 chunks, every one of length 3",
            "length_classes_present": [6],
            "seam_discipline": (
                "sealed, and the leakiest of the sealed worlds: 22 of its 256 "
                "ordered chunk pairs shortcut at the seam -- LEAK-2 via "
                "[sqr,add1,dbl] before a sub1-starting chunk and [sqr,sub1,dbl] "
                "before an add1-starting chunk, plus LEAK-1 via the chunks that "
                "end in sqr,dbl"
            ),
            "what_i_think_makes_it_hard": (
                "Every member has the same builder length, so length carries no "
                "information at all. The only signal is which 3-chunk vocabulary "
                "the two halves come from."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "candidate_concatenations": 256,
            "dead_from_known_leak_guess": 6,
            "chunks_i_expect_to_recur_most": [[A, Q, Q], [D, Q, Q], [Q, D, Q]],
            "chunks_i_expect_to_recur_least": [[Q, A, D], [Q, S, D]],
            "member_count_guess": 225,
            "member_count_guess_band": [180, 250],
            "confidence": "medium-high",
            "design_note": (
                "Deliberately maximal chunk count at minimal chunk length: the "
                "widest vocabulary in the collection over the narrowest shape."
            ),
        },
    },
    {
        "world_id": "deep_well",
        # Ten 4-chunks, no 3-chunks.  With min 8 the only attainable member
        # length is 8, i.e. exactly two chunks, exactly 100 candidates.
        "chunks": [
            [A, D, Q, Q],
            [A, Q, D, Q],
            [A, Q, S, Q],
            [D, A, Q, Q],
            [D, Q, A, Q],
            [D, Q, S, Q],
            [Q, A, D, Q],
            [Q, Q, A, Q],
            [Q, Q, S, Q],
            [S, D, Q, Q],
        ],
        "min_builder_length": 8,
        "part_fractions": {"initial": 0.375, "tuning": 0.25, "future": 0.375},
        "surface": {
            "display_name": "The Deep Well",
            "one_liner": "Two chunks. Never one, never three.",
            "vocabulary": "all four ops",
            "chunk_shape": "10 chunks, every one of length 4",
            "length_classes_present": [8],
            "seam_discipline": (
                "airtight: every chunk ends in sqr, which is the only discipline "
                "here that closes BOTH residual leaks. 0 of 100 ordered chunk "
                "pairs shortcut at the seam"
            ),
            "degree_floor": (
                "every chunk carries at least two sqr, so every member has degree "
                "at least 16 -- the deepest world in the collection"
            ),
            "what_i_think_makes_it_easy": (
                "Only one decomposition arity is possible. Any member splits 4+4 "
                "and nowhere else."
            ),
            "what_i_think_makes_it_hard": (
                "Degree-16-and-up polynomials have enormous coefficients; the "
                "members are hard to even write down, let alone compare."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "candidate_concatenations": 100,
            "chunks_i_expect_to_recur_most": [[A, D, Q, Q], [D, A, Q, Q], [S, D, Q, Q]],
            "member_count_guess": 92,
            "member_count_guess_band": [80, 100],
            "confidence": "high",
            "design_note": (
                "The square density here is the highest I use anywhere. This "
                "world originally held three chunks ending in sqr,dbl, which gave "
                "it 9 leaking pairs out of 100; I replaced them with sqr-ending "
                "chunks so that the world would actually be what its story claims "
                "it is. If any world in the collection is at full yield it is "
                "this one."
            ),
        },
    },
    {
        "world_id": "long_and_short",
        # Deliberately lopsided: only four 3-chunks against ten 4-chunks, with
        # min 7 so the 6-class (3+3) is cut away.  Classes 7 (3+4 or 4+3) and
        # 8 (4+4) survive; the four short chunks are scarce and load-bearing.
        "chunks": [
            [A, Q, Q],
            [D, A, Q],
            [Q, A, Q],
            [S, Q, D],
            [A, D, Q, D],
            [A, Q, A, Q],
            [A, Q, D, Q],
            [D, A, Q, D],
            [D, Q, A, D],
            [Q, A, D, D],
            [Q, A, Q, Q],
            [Q, S, D, Q],
            [S, D, Q, Q],
            [S, Q, D, Q],
        ],
        "min_builder_length": 7,
        "part_fractions": {"initial": 0.5625, "tuning": 0.125, "future": 0.3125},
        "surface": {
            "display_name": "Long and Short",
            "one_liner": "Four short planks holding up ten long ones.",
            "vocabulary": "all four ops",
            "chunk_shape": "4 chunks of length 3, 10 of length 4",
            "length_classes_present": [7, 8],
            "seam_discipline": (
                "sealed; 12 of its 196 ordered chunk pairs shortcut at the seam, "
                "LEAK-2 at [dbl,sqr,add1,dbl] before either sub1-starting chunk "
                "and LEAK-1 at the chunks ending in sqr,dbl"
            ),
            "what_i_think_makes_it_hard": (
                "The 7-class is entirely mixed-arity: every one of its members "
                "is a short chunk against a long one, in one order or the other. "
                "Telling 3+4 from 4+3 is the whole puzzle."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "candidate_concatenations": {"length_7": 80, "length_8": 100},
            "dead_from_known_leak_guess": 2,
            "chunks_i_expect_to_recur_most": [[A, Q, Q], [D, A, Q], [S, D, Q, Q]],
            "member_count_guess": 160,
            "member_count_guess_band": [130, 180],
            "confidence": "medium",
            "design_note": (
                "This is the 'pair long with short' idea stated as bluntly as I "
                "could: the four 3-chunks appear in 80 of the candidate builders "
                "and the ten 4-chunks in 180, so the short vocabulary is "
                "over-represented per chunk by a factor of about five."
            ),
        },
    },
    {
        "world_id": "shallow_shelf",
        # Six 3-chunks, five 4-chunks, min 4: the only world where every
        # attainable length class (4, 6, 7, 8) is populated.  Square density is
        # deliberately the lowest in the collection -- one sqr per short chunk.
        "chunks": [
            [A, D, Q],
            [A, Q, D],
            [D, A, Q],
            [D, Q, D],
            [S, D, Q],
            [S, Q, D],
            [A, Q, D, Q],
            [D, A, Q, Q],
            [D, S, Q, Q],
            [Q, A, D, Q],
            [S, Q, D, Q],
        ],
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.40625, "tuning": 0.28125, "future": 0.3125},
        "surface": {
            "display_name": "The Shallow Shelf",
            "one_liner": "Four depths at once, and none of them very deep.",
            "vocabulary": "all four ops",
            "chunk_shape": "6 chunks of length 3, 5 of length 4",
            "length_classes_present": [4, 6, 7, 8],
            "seam_discipline": (
                "sealed, and free of LEAK-2 by construction -- the world mixes "
                "add1 with sub1, but no chunk ends in shift-then-dbl. LEAK-1 is "
                "live: 12 of its 121 ordered chunk pairs end sqr,dbl into a "
                "dbl-starting chunk"
            ),
            "what_i_think_makes_it_hard": (
                "The 4-class holds at most five members -- one per 4-chunk -- so "
                "the smallest part of that class is a single polynomial. The "
                "world is lopsided by length in a way the fractions can only "
                "approximate."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "candidate_concatenations": {
                "length_4": 5,
                "length_6": 36,
                "length_7": 60,
                "length_8": 25,
            },
            "chunks_i_expect_to_recur_most": [[A, D, Q], [D, A, Q], [S, D, Q]],
            "member_count_guess": 105,
            "member_count_guess_band": [80, 125],
            "confidence": "medium",
            "known_thin_class": (
                "The length-4 class caps at five members, so a 0.40625 / 0.28125 "
                "/ 0.3125 split there rounds to something like 2 / 1 / 2. I made "
                "that class thin on purpose and I am recording that I knew."
            ),
            "design_note": (
                "Lowest square density of the collection: [dbl,sqr,dbl] and "
                "[add1,sqr,dbl] carry a single sqr, so length-6 members here can "
                "sit at degree 4 rather than degree 16. I expect this to be the "
                "world where canonicality actually bites -- low-degree members "
                "have more competitors of equal length."
            ),
        },
    },
    {
        "world_id": "leaky_seam",
        # The deliberate counter-example.  Every chunk here ENDS in a shift, in
        # direct violation of the sealing rule that governs the other seven
        # worlds.  Seams can therefore cancel (a|s, s|a) or trigger d,a,a.
        "chunks": [
            [D, Q, A],
            [Q, D, A],
            [Q, Q, A],
            [Q, A, A],
            [S, Q, A],
            [A, Q, S],
            [D, Q, S],
            [D, Q, A, A],
            [Q, D, Q, A],
            [Q, Q, D, A],
            [S, Q, A, A],
            [A, Q, D, S],
            [D, Q, S, S],
        ],
        "min_builder_length": 4,
        "part_fractions": {"initial": 0.59375, "tuning": 0.125, "future": 0.28125},
        "surface": {
            "display_name": "The Leaky Seam",
            "one_liner": "Thirteen chunks that all end mid-step, and pay for it.",
            "vocabulary": "all four ops",
            "chunk_shape": "7 chunks of length 3, 6 of length 4",
            "length_classes_present": [4, 6, 7, 8],
            "seam_discipline": (
                "DELIBERATELY UNSEALED. Every chunk ends in add1 or sub1, so a "
                "seam can cancel outright ([...,add1] before [sub1,...]) or hand "
                "a doubled shift to a preceding dbl. Each chunk is internally "
                "clean, so the single-chunk 4-class should survive intact; it is "
                "the joins that bleed."
            ),
            "what_i_think_makes_it_hard": (
                "Not hard so much as sparse. I expect this world to be the "
                "smallest in the collection by a wide margin, and I expect its "
                "surviving members to be strongly biased toward seams where an "
                "add1-ending chunk meets another add1-starting chunk."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "candidate_concatenations": {
                "length_4": 6,
                "length_6": 49,
                "length_7": 84,
                "length_8": 36,
            },
            "chunks_i_expect_to_recur_most": [[Q, Q, A], [Q, D, Q, A]],
            "chunks_i_expect_to_recur_least": [[A, Q, S], [D, Q, S, S]],
            "member_count_guess": 70,
            "member_count_guess_band": [30, 110],
            "confidence": "low",
            "design_note": (
                "This world exists to be the contrast case for the sealing rule "
                "the rest of the collection is built on. If the sealing rule is "
                "doing real work, leaky_seam should come out visibly thinner per "
                "candidate concatenation than shallow_shelf, which has a similar "
                "shape and an airtight seam discipline. If it does not, my whole "
                "design thesis is wrong and I would rather find that out."
            ),
        },
    },
    {
        "world_id": "twin_roots",
        # Every chunk carries EXACTLY two sqr and ends in sqr.  Length-8 members
        # therefore have four squarings and degree 16+; min 6 cuts nothing below.
        "chunks": [
            [A, Q, Q],
            [Q, A, Q],
            [Q, D, Q],
            [Q, S, Q],
            [S, Q, Q],
            [A, Q, A, Q],
            [A, Q, D, Q],
            [D, Q, A, Q],
            [D, Q, S, Q],
            [Q, A, D, Q],
            [Q, D, A, Q],
            [S, Q, D, Q],
        ],
        "min_builder_length": 6,
        "part_fractions": {"initial": 0.375, "tuning": 0.28125, "future": 0.34375},
        "surface": {
            "display_name": "Twin Roots",
            "one_liner": "Two squarings per chunk, no more and no less.",
            "vocabulary": "all four ops",
            "chunk_shape": "5 chunks of length 3, 7 of length 4",
            "length_classes_present": [6, 7, 8],
            "seam_discipline": (
                "airtight: every chunk ends in sqr, not merely in dbl-or-sqr, so "
                "both residual leaks are closed. 0 of 144 ordered chunk pairs "
                "shortcut at the seam -- the only world that came out clean "
                "without my having to intervene"
            ),
            "invariant": "exactly two sqr per chunk, chunk always ends in sqr",
            "what_i_think_makes_it_hard": (
                "Degree alone tells you the chunk count (4 squarings means two "
                "chunks, 6 means three -- except three chunks overflow the cap, "
                "so degree is nearly a giveaway). The difficulty is entirely in "
                "the shift pattern buried between the squarings."
            ),
        },
        "intent": {
            "intent_role": "audit_only",
            "candidate_concatenations": {
                "length_6": 25,
                "length_7": 70,
                "length_8": 49,
            },
            "chunks_i_expect_to_recur_most": [[A, Q, Q], [Q, D, Q], [A, Q, D, Q]],
            "member_count_guess": 135,
            "member_count_guess_band": [115, 144],
            "confidence": "high",
            "design_note": (
                "The uniform two-sqr invariant is the strongest structural claim "
                "I make anywhere: it forces a degree floor of 16 on the 8-class "
                "and pins the position of every squaring in the degree sequence. "
                "This is the world where I most expect the canonical builder to "
                "simply be the obvious one."
            ),
        },
    },
]


# --- hard-bound self-check --------------------------------------------------
# This checks the PACKAGE against the stated bounds. It does not enumerate or
# inspect any world's members -- the member sets are left to speak for
# themselves, as the brief asks.

def check(worlds):
    seen_ids = set()
    for w in worlds:
        wid = w["world_id"]
        assert wid not in seen_ids, "duplicate world_id: %s" % wid
        seen_ids.add(wid)

        assert list(w) == [
            "world_id",
            "chunks",
            "min_builder_length",
            "part_fractions",
            "surface",
            "intent",
        ], "wrong top-level key set in %s" % wid

        chunks = w["chunks"]
        assert 10 <= len(chunks) <= 16, "%s: chunk count %d" % (wid, len(chunks))
        for c in chunks:
            assert len(c) in (3, 4), "%s: chunk length %r" % (wid, c)
            for op in c:
                assert op in (A, S, D, Q), "%s: unknown op %r" % (wid, op)
        assert len({tuple(c) for c in chunks}) == len(chunks), "%s: repeated chunk" % wid

        m = w["min_builder_length"]
        assert isinstance(m, int) and 4 <= m <= 8, "%s: min_builder_length %r" % (wid, m)

        pf = w["part_fractions"]
        assert list(pf) == ["initial", "tuning", "future"], "%s: part keys" % wid
        assert 0.35 <= pf["initial"] <= 0.60, "%s: initial %r" % (wid, pf["initial"])
        assert 0.10 <= pf["tuning"] <= 0.30, "%s: tuning %r" % (wid, pf["tuning"])
        assert pf["future"] >= 0.25, "%s: future %r" % (wid, pf["future"])
        assert pf["initial"] + pf["tuning"] + pf["future"] == 1.0, "%s: sum" % wid

        assert w["intent"]["intent_role"] == "audit_only", "%s: intent_role" % wid

    # at least 6 worlds, at least 2 distinct shapes
    assert len(worlds) >= 6
    shapes = {
        (
            len(w["chunks"]),
            tuple(sorted(len(c) for c in w["chunks"])),
            w["min_builder_length"],
            tuple(w["part_fractions"][k] for k in ("initial", "tuning", "future")),
        )
        for w in worlds
    }
    assert len(shapes) >= 2, "need at least two distinct shapes"
    return len(shapes)


def main():
    check(WORLDS)
    # Relative path on purpose: the file lands in the directory this is RUN from.
    with open("worlds.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for w in WORLDS:
            fh.write(json.dumps(w, ensure_ascii=True, sort_keys=False))
            fh.write("\n")


if __name__ == "__main__":
    main()
