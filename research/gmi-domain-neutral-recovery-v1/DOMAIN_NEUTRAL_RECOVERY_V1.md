# Three candidate-domain neutral recoveries v1

Every search below enumerates its entire finite candidate space.  Candidates
are tuples of low-level operations; the evaluator receives only exact output
agreement and charged cost.  Domain/family labels are applied after scoring
and are absent from serialized candidate spaces.  These searches complement,
rather than replace, the separate parent-reduction results.

## Relational compatibility and assembly

The four candidates cross an overlap test (`equal` or unconditional) with an
output operation (map merge or take-left).  The obligation contains compatible
overlapping maps, incompatible overlapping maps, and disjoint maps, and asks
for their union exactly when shared keys agree.  Only `(equal, merge)` is exact;
after scoring it is classified as local compatibility plus gluing.  In the
matched all-disjoint ecology both overlap tests are exact and the cheaper
unconditional test wins.  Thus the compatibility mechanism appears only when
an obstruction can occur.

## Shared local update

Eight candidates cross an observation key (three adjacent bits or the whole
five-bit state), a table address (one shared address or a site address), and a
clock (snapshot or in-place).  Tables are fitted from the complete finite
one-step relation, then rolled out for two steps on all 32 states.  For uniform
elementary rule 90, `(triple, shared, snapshot)` is the least-description exact
candidate: eight one-bit table entries.  A position-addressed version is also
exact but costs 40 entries, and the global version costs 160.

The matched ecology alternates rule 90 and rule 150 by site.  The shared table
becomes inconsistent and `(triple, site, snapshot)` wins.  Only after scoring
is the first phenotype classified as a shared radius-one cellular/local-field
update.  The twin shows that sharing is earned by homogeneous site law, not
granted to the target family.

## Iterative product feedback

Ten candidates cross a feedback bit with iteration counts zero through four.
Starting from strings `{01,110}`, one round may concatenate any two current
strings subject to length at most eight.  Membership is scored against all 510
binary strings of length one through eight.  The exact fixed point has 14
members.  Feedback with two iterations is the least-cost exact candidate;
zero/one rounds and every no-feedback candidate miss deep products.  It is
classified after scoring as constructive/autocatalytic closure.

The matched ecology retains the same seeds and rule but asks only seed-level
membership questions plus absent controls.  Zero iterations with no feedback
wins.  Iterative reuse is therefore selected by deep constructibility, not by
a name or tie-break.

## Claim ceiling

The result establishes three bounded recoveries in three small exact grammars.
It does not establish cross-grammar or cross-search robustness, real transfer,
novel domains, or burden separation from the already proved parents.
