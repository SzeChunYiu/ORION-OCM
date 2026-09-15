# Hyperdimensional/vector-symbolic reduction and capacity theorem v1

## Parent reductions

For binary dimension \(D\), a VSA carrier is a vector in \(\{0,1\}^D\) plus
an item-memory codebook. BIND is componentwise XOR, PERMUTE is a coordinate
permutation, BUNDLE is componentwise majority, SIMILARITY is Hamming distance,
and CLEANUP is nearest-code lookup.

- **D1:** the vector/codebook are finite coefficient arrays. XOR, permutation,
  majority, and Hamming compile componentwise with \(O(D)\) Boolean/arithmetic
  work; cleanup costs \(O(FD)\) for \(F\) codewords.
- **D2:** a materialized exemplar store enumerates each finite bound composition
  and serves exact lookup. The committed receipt verifies identical VSA/store
  answer signatures in all 7 registered cells. At fixed structure depth the
  materialization is finite; its growth with depth is explicitly charged.
- **D4:** each VSA expression is a straight-line typed program over XOR,
  permutation, majority, addition/comparison, and lookup. Structural induction
  compiles every expression and preserves its vector result exactly.

These are semantics-preserving reductions; their burden depends on \(D\),
codebook size, and structure depth. Consequently VSA is a useful representation
and price phase, not a new domain at the registered finite/fixed-depth scope.

## Exact noise/capacity law

Let an odd majority bundle contain \(k\) independent random bipolar items and
track one member. At one coordinate, the other \(k-1\) signs sum to \(S\).
The tracked sign survives iff \(S\ge0\), so

\[
p_k=\frac12+
\frac12\frac{\binom{k-1}{(k-1)/2}}{2^{k-1}}.
\]

Thus \(p_k-1/2=\Theta(k^{-1/2})\): superposition margin shrinks with bundle
size. Independent bit-flip probability \(\eta\) changes it to

\[
p_{k,\eta}=\frac12+(p_k-\tfrac12)(1-2\eta).
\]

For \(D\) independent coordinates and \(F\) independent distractor
codewords, splitting the similarity margin and applying Hoeffding plus a union
bound gives the explicit cleanup-failure bound

\[
P_{fail}\le(F+1)\exp[-D(p_{k,\eta}-1/2)^2/2].
\]

Therefore sufficient dimension for failure at most \(\delta\) is
\[
D\ge
\frac{2\log((F+1)/\delta)}{(p_{k,\eta}-1/2)^2}.
\]
This quantifies bundle capacity, external noise, codebook size, and dimension
without claiming independence for non-random learned codebooks.

## Executed frontier

The hash-verified DC1 receipt contains 28 execution cells and 56 frontier cells.
VSA and materialized D2 answers agree 7/7. VSA alone occupies 19 frontier cells;
the materialized store alone occupies 5. The result is the predicted
lazy-composition versus eager-materialization phase: VSA wins selected
short-reuse/native-price cells, while the parent wins after amortizing compile
cost.

## Claim ceiling

Five reduction/scaling/frontier tasks close. “Implement primitives neutrally”
and “Neutral recovery” remain open because the DC1 microscope directly names
and instantiates the candidate.
