# Neutral binary-carrier construction and recovery v1

## Grammar

A candidate contains four ordinary choices, with no family or architecture
label: a pointwise Boolean combiner (`XOR`, `AND`, `OR`), a list fold
(`first`, parity, strict majority), an index transform (identity or cyclic
rotation), and a chooser (exact match or minimum Hamming distance).  The
interpreter exposes only 64-bit words, lists, integer indices, Boolean
operations, rotation, population count, and argmin.  There is no
`VSA`, hypervector, bind, bundle, permutation, cleanup, memory, or attention
macro in the candidate representation.

Applied to an item `(slot, role, filler)`, the index transform acts on the role
word, the Boolean combiner joins that word to the filler word, and the list
fold joins item words.  At query time the same transform and combiner remove a
role/slot key when that operation is self-inverse, and the chooser maps the
result to one of eight filler words.  Thus the familiar four operations are a
post-run interpretation of low-level operations, not privileged primitives.

## Executed search

The search enumerates all `3*3*2*2 = 36` candidates and receives only exact
output equality and charged operation count.  On four three-item records with
three slots, exactly one candidate reproduces both the record word and every
role/slot query: `(XOR, strict-majority, cyclic-rotation, nearest-Hamming)`.
Only after scoring is that tuple classified as the binding/bundling/
permutation/cleanup phenotype.

The matched negative ecology uses one item at slot zero.  Twelve candidates
are exact because folding and position transformation are unnecessary; the
least-cost exact candidate is `(XOR, first, identity, exact-match)`.  The full
phenotype is therefore recovered only where superposition, positional
distinction, and noisy decoding are jointly required.  The search does not
reward structural similarity and the winner is not fixed by its tie-break.

## Claim ceiling

This is exhaustive neutral recovery in one frozen, finite 36-candidate Boolean
grammar and a matched degenerate twin.  It is not cross-grammar recovery,
search-algorithm replication, an asymptotic capacity result, or evidence of a
new domain: the separate reduction theorem still maps the carrier to D1/D2/D4.
