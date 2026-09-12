# Studio D — author's notes on eight hidden-chunk worlds

Eight worlds, seven distinct shapes. Everything here is hand-authored; the
emitter is a lookup table with a self-check bolted on.

**Seeds: none.** There is no randomness anywhere in `emit_worlds.py` — no `random`,
no hashing, no clock, no environment. Every chunk set is a literal in the source.
The part fractions are all dyadic rationals (thirty-seconds), so each one has an
exact binary float representation and each triple sums to exactly `1.0` rather
than to `0.9999999999999999`. `json.dumps` runs with fixed separators over
insertion-ordered dicts. Two runs give byte-identical `worlds.jsonl`; I checked
that by running it twice and comparing digests.

Shorthand below: `a` = add1, `s` = sub1, `d` = dbl, `q` = sqr.

---

## 1. The problem I was actually solving

A world is a chunk set, but a chunk set is not what the world *is*. The members
are polynomials whose **canonical** builder decomposes into my chunks — and
canonical means shortest-then-lex-least. So I can write down a beautiful chunk
set whose concatenations all spell builders that some shorter builder already
beat, and the world comes out empty. Choosing chunks is really choosing *seams*.

Two disciplines carry the collection.

### The sealing rule

Every chunk ends in `d` or `q`, and no chunk begins with a repeated `a`, `s`, or
`d`. A sealed chunk can never hand a shift to its neighbour, which kills
cancellation (`a,s` / `s,a`) outright, and the no-repeat start kills
`d,a,a → a,d` and `d,s,s → s,d` at every seam.

### Square density

Every chunk carries at least one `q`; most carry two. Squaring doubles the
degree, so the degree sequence pins where each `q` sits, and the minimal builder
becomes nearly forced. Linear-only builders are the collision-rich zone — there
are many ways to reach `4x+3` and only one of them wins — so I mostly stayed out
of it. The deep worlds are deep on purpose: it is a canonicality strategy, not
decoration.

### Where the sealing rule stops — two residual leaks

I claimed to myself that sealing was complete, and it is not. It only guards
rewrites that take **one** op from the left chunk. A three-op rewrite can also
straddle a seam two-from-the-left, and two of those walk straight through:

| | pattern | rewrite | fires when |
|---|---|---|---|
| **LEAK-1** | `q,d` \| `d` | `sqr,dbl,dbl` → `dbl,sqr` | chunk ends `sqr,dbl`, next starts `dbl` |
| **LEAK-2** | `a,d` \| `s` | `add1,dbl,sub1` → `dbl,add1` | chunk ends shift-`dbl`, next starts with the opposite shift |

LEAK-2 I knew about and priced early. LEAK-1 I missed entirely until I scanned
the literals against my own rule — my rule banned chunks *starting* with `d,d`
and I never thought about a chunk *ending* `q,d` donating the first `d`.

Ordered chunk pairs that shortcut at the seam, after the fix described below:

| world | pairs | leaking | which |
|---|---|---|---|
| brass_lantern | 144 | 6 | LEAK-1 |
| tin_orchard | 144 | 6 | LEAK-1 |
| narrow_gauge | 256 | 22 | 16 LEAK-1, 6 LEAK-2 |
| deep_well | 100 | **0** | — |
| long_and_short | 196 | 12 | 9 LEAK-1, 3 LEAK-2 |
| shallow_shelf | 121 | 12 | LEAK-1 |
| leaky_seam | 169 | 32 | 26 cancellations, 6 `d,a,a` — **by design** |
| twin_roots | 144 | **0** | — |

I kept the leaks rather than tightening the rule, because a few percent of the
candidate pairs is a price worth paying to keep the vocabulary I wanted. One
exception: `deep_well` is sold on being airtight, so I made it airtight
(below). The complete discipline turns out to be stricter than sealing — end
every chunk in `q`, not in `d`-or-`q`. Then neither rewrite can form, because
neither has a `q` in its second-from-last position. `twin_roots` satisfied that
by accident of its own invariant; `deep_well` I moved onto it deliberately.

---

## 2. The worlds

### `brass_lantern` — 12 chunks (6×3, 6×4), min 4, .5 / .21875 / .28125

Three-chunks `a d q`, `a q d`, `a q q`, `d a q`, `q a d`, `q a q`; four-chunks
`a d q d`, `a q d q`, `a q a q`, `d a q q`, `d q a q`, `q a d q`.

The reference world. One shift op only — `add1` — so every constant that appears
in any member is positive and LEAK-2 is structurally impossible. All four length
classes are populated. If a solver can only crack one world here, it should be
this one.

### `tin_orchard` — 12 chunks (6×3, 6×4), min 4, .5 / .21875 / .28125

The same twelve chunks with every `add1` replaced by `sub1`: three-chunks
`s d q`, `s q d`, `s q q`, `d s q`, `q s d`, `q s q`; four-chunks `s d q d`,
`s q d q`, `s q s q`, `d s q q`, `d q s q`, `q s d q`.

**Same shape as `brass_lantern`, on purpose.** The brief says worlds that differ
only in which chunks they use still count as distinct, and I wanted one matched
pair so that shape is held fixed and only the vocabulary moves. My recorded
expectation is that the orchard comes out slightly *smaller* than the lantern:
`sub1` is lexicographically later than `add1`, so wherever a member here ties on
length against some `add1`-flavoured builder, this world loses the tie-break and
the polynomial belongs to nobody. Squaring erases the sign, so the two worlds'
members should look far more alike than their chunk sets do.

### `narrow_gauge` — 16 chunks, all length 3, min 6, .4375 / .1875 / .375

Sixteen three-chunks spanning all four ops: `a d q`, `a q d`, `a q q`, `d a q`,
`d q d`, `d q q`, `d s q`, `q a d`, `q a q`, `q s d`, `q s q`, `q d q`, `q q d`,
`s d q`, `s q d`, `s q q`.

Maximum chunk count at minimum chunk length. With no 4-chunks and a minimum of
6, the only attainable member length is 6 — length 3 is below the floor and 9
overflows the cap — so the world has exactly **one** builder-length class. That
makes the per-class part split trivially clean and removes length as a signal
entirely. It is also the leakiest sealed world (22/256), because the widest
vocabulary is the one most likely to contain both halves of a leak.

### `deep_well` — 10 chunks, all length 4, min 8, .375 / .25 / .375

`a d q q`, `a q d q`, `a q s q`, `d a q q`, `d q a q`, `d q s q`, `q a d q`,
`q q a q`, `q q s q`, `s d q q`.

The mirror of `narrow_gauge`: minimum chunk count at maximum chunk length, with
a minimum of 8 so the only member length is 8 — exactly two chunks, exactly 100
candidate pairs. Every chunk carries two `q`, so every member has four
squarings and degree ≥ 16. This is the deepest world and the one I expect
closest to full yield.

It did not start that way. Three of its chunks originally ended `q,d`, which
gave it 9 leaking pairs out of 100 — in the one world whose entire story is
airtightness. I swapped those three for `q`-ending chunks (`a q s q`, `q q a q`,
`q q s q`). It is now 0/100. Changing the design to match the claim seemed
better than softening the claim.

### `long_and_short` — 14 chunks (4×3, 10×4), min 7, .5625 / .125 / .3125

Short: `a q q`, `d a q`, `q a q`, `s q d`. Long: `a d q d`, `a q a q`,
`a q d q`, `d a q d`, `d q a d`, `q a d d`, `q a q q`, `q s d q`, `s d q q`,
`s q d q`.

This is the "pair long with short" idea stated bluntly. A minimum of 7 cuts away
the 6-class (3+3), so the surviving classes are 7 (mixed arity, always one short
chunk against one long one) and 8 (two long chunks). The four short chunks
appear in 80 of the candidate builders against 180 for the ten long ones — about
a five-fold over-representation per chunk. The whole 7-class puzzle is telling
3+4 from 4+3.

### `shallow_shelf` — 11 chunks (6×3, 5×4), min 4, .40625 / .28125 / .3125

Three-chunks `a d q`, `a q d`, `d a q`, `d q d`, `s d q`, `s q d`; four-chunks
`a q d q`, `d a q q`, `d s q q`, `q a d q`, `s q d q`.

The only world with all four length classes populated *and* the lowest square
density in the collection — `d q d` and `a q d` carry a single `q`, so length-6
members here can sit at degree 4 instead of degree 16. I expect this to be the
world where canonicality actually bites, since low-degree members have far more
competitors at equal length. It is also the leak-2-free mixed-shift world: it
uses both `add1` and `sub1`, but no chunk ends shift-then-`dbl`, so LEAK-2
cannot form even though LEAK-1 can.

**Known thin class:** with five 4-chunks the length-4 class caps at five
members, so a .40625/.28125/.3125 split there rounds to roughly 2/1/2. I made
that class thin knowingly. (An earlier draft had three 4-chunks and a 1/1/1
class, which felt like it was making the `future ≥ 0.25` band do something
silly; five is the smallest count I was comfortable with.)

### `leaky_seam` — 13 chunks (7×3, 6×4), min 4, .59375 / .125 / .28125

`d q a`, `q d a`, `q q a`, `q a a`, `s q a`, `a q s`, `d q s`; `d q a a`,
`q d q a`, `q q d a`, `s q a a`, `a q d s`, `d q s s`.

**The deliberate counter-example.** Every chunk ends in a shift, in flat
violation of the rule governing the other seven worlds. Each chunk is internally
clean, so the single-chunk 4-class should survive intact — it is the joins that
bleed. 32 of its 169 ordered pairs shortcut: 26 outright cancellations and 6
`d,a,a` reductions, an order of magnitude worse than any sealed world.

This world exists to be falsifiable. If the sealing rule is doing real work,
`leaky_seam` should come out visibly thinner per candidate pair than
`shallow_shelf`, which has a comparable shape and a clean seam discipline. If it
does not, my design thesis is wrong, and I would rather that show up in the
collection than not. Its fractions sit at the band extremes (.59375 initial,
.125 tuning) for the same reason.

### `twin_roots` — 12 chunks (5×3, 7×4), min 6, .375 / .28125 / .34375

`a q q`, `q a q`, `q d q`, `q s q`, `s q q`; `a q a q`, `a q d q`, `d q a q`,
`d q s q`, `q a d q`, `q d a q`, `s q d q`.

One invariant, held exactly: **every chunk contains exactly two `sqr` and ends
in `sqr`.** That forces a degree floor of 16 on the 8-class and pins the
position of every squaring in the degree sequence. It also — I only noticed
afterwards — makes it the one world that came out with zero leaking seams
without my intervening, since ending in `q` is the complete discipline that
ending in `d`-or-`q` only approximates. Degree nearly gives away the chunk
count; the difficulty is entirely in the shift pattern buried between the
squarings.

---

## 3. What I varied, and why

| world | chunks | lengths | min | initial / tuning / future |
|---|---|---|---|---|
| brass_lantern | 12 | 6×3, 6×4 | 4 | .5 / .21875 / .28125 |
| tin_orchard | 12 | 6×3, 6×4 | 4 | .5 / .21875 / .28125 |
| narrow_gauge | 16 | 16×3 | 6 | .4375 / .1875 / .375 |
| deep_well | 10 | 10×4 | 8 | .375 / .25 / .375 |
| long_and_short | 14 | 4×3, 10×4 | 7 | .5625 / .125 / .3125 |
| shallow_shelf | 11 | 6×3, 5×4 | 4 | .40625 / .28125 / .3125 |
| leaky_seam | 13 | 7×3, 6×4 | 4 | .59375 / .125 / .28125 |
| twin_roots | 12 | 5×3, 7×4 | 6 | .375 / .28125 / .34375 |

Seven distinct shapes; `brass_lantern` and `tin_orchard` are the one matched
pair, and that is the point of them.

The axes I moved, each for a stated reason rather than for variety's sake:

- **Chunk-length composition** — all-3 (`narrow_gauge`), all-4 (`deep_well`),
  and every mix between. This is the axis that controls which builder-length
  classes exist at all, since 8 = 4+4, 7 = 3+4, 6 = 3+3.
- **Minimum builder length as a scalpel** — 8 collapses a world to one class,
  7 removes the 3+3 class, 6 removes single chunks, 4 keeps everything. I used
  the minimum to *sculpt the class structure*, not as a difficulty dial.
- **Square density** — from one `q` per short chunk (`shallow_shelf`) to exactly
  two per chunk (`twin_roots`, `deep_well`). This is my main lever on whether
  members are canonical at all.
- **Shift vocabulary** — `add1`-only, `sub1`-only, and mixed. Single-shift worlds
  are immune to LEAK-2 for free.
- **Seam discipline itself** — six sealed, two airtight, one deliberately broken.

---

## 4. What I found hard

**The tie-break, not the length.** I started out reasoning only about minimality:
avoid `a,s`, avoid `d,a,a`, and a builder should be canonical. Then I worked
through `d,a,d,a` = `4x+3`. It is genuinely minimal — no three-op builder reaches
`4x+3`, since three ops with coefficient 4 give you only `4x±1`, `4x±2`, `4x±4`.
So it survives every length argument I had. But `a,d,d,s` computes `4x+3` too, at
the same length, and `a` beats `d` in the public order, so `d,a,d,a` is not
canonical and loses to a builder that looks nothing like it.

That one case rearranged the whole design. It is why square density is a rule
here and not a flourish: in the linear-only region there are many equal-length
routes to the same polynomial and the lex tie-break decides among them in a way
I cannot track by hand, whereas once `sqr` fixes the degree sequence the routes
collapse to essentially one. I cannot rule out lex-tie losses in the deep worlds
either — I just believe they are rare there, and I have no way to know how rare
without enumerating, which is not what this task asks of me.

**Believing my own rule.** The LEAK-1 miss is the honest embarrassment of this
package. I had a clean argument — "a seam is (`d`|`q`) followed by a first op, so
control the first ops" — and the argument was fine as far as it went; it simply
did not occur to me that a three-op window at a seam can sit two-in on the left.
Stating a rule crisply made it *feel* complete. What caught it was scanning the
chunk literals against the rule instead of against my memory of the rule, which
is the only reason `deep_well` is not shipping with nine dead pairs and a boast.

**Fraction bands against small classes.** The bands assume classes with enough
members to split three ways. A length-4 class holds at most one member per
4-chunk, so in `shallow_shelf` that is five members split .40625/.28125/.3125.
The fractions are honest as intent and necessarily coarse as arithmetic. I
resolved it by making the thin class a deliberate feature of exactly one world
and saying so in that world's `intent`, rather than quietly inflating every
chunk count to make the rounding tidy.

**What I did not do.** I did not enumerate members. Every member count in every
`intent` block is a guess with a band and a stated confidence, reasoned from
candidate-pair counts and how much of the seam I believe survives. They are
recorded to be scored, not to be right. My confidence ordering, for whatever it
is worth: `deep_well` and `twin_roots` highest, `narrow_gauge` next,
`leaky_seam` lowest by a wide margin — its band is 30 to 110 because I genuinely
do not know how badly a broken seam bleeds.
