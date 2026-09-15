# J2 bounded completeness attacks theorem v1

## Scope

The bounds and candidate languages are fixed in `FREEZE_V1.json`.  A failure
means only that no member of that finite registered realization class meets the
listed obligation.  It is not an unbounded separation between domains.  Each
negative search has a nearby positive control obtained by relaxing one bound
or simplifying the obligation.

## Eight domain-specific attacks

- **D1.** Exhaust 125 integer threshold parameter tuples on two bits.  XOR has
  no exact row; AND is a positive control.  This is also implied by the usual
  four incompatible threshold inequalities.
- **D2.** Exhaust all 186 default-plus-at-most-three-exception truth tables on
  three bits.  Parity needs four exceptions from either default, so none is
  exact; any target with at most three minority outputs is the control.
- **D3.** Exhaust probabilities `{0,1/2,1}`.  The exact `1/3` forecast is absent
  at the frozen precision; `1/2` is present.
- **D4.** Compute the semantic closure of variables/constants under at most two
  NOT/AND/OR instructions.  It contains 40 of 256 signatures and excludes
  three-bit parity; a conjunction is present.
- **D5.** Exhaust all `8! = 40320` leaf-query orders.  Seven equality queries
  always leave the last possible goal unqueried, so no order succeeds for all
  eight placements; eight queries make every order exact.
- **D6.** Exhaust all 16 two-state unary controllers (four transition maps,
  four output maps).  None recognizes length modulo three on lengths 0--5;
  the 216 three-state controllers include an exact control.
- **D7.** Exhaust all 16 Boolean response tables available to a root after one
  round on a three-node path.  Marking only the distance-two node collides with
  the unmarked configuration at the root, while one-hop detection is exact.
- **D8.** Exhaust the three genotypes reachable from `00` by at most one
  single-bit rewrite.  `11` is unreachable and `10` is the positive control.

These are resource-bound witnesses, not claims that a stronger member of any
domain cannot solve the obligation.

## Pairwise composition census

Each D1--D8 bound is also mapped to a finite set of three-bit Boolean response
signatures.  For every one of the 28 distinct pairs, the census includes either
constituent alone and every pointwise AND, OR, or XOR of one signature from
each constituent.  Six pairs span all 256 truth tables under this generous
one-combiner rule.  The other 22 leave at least two signatures absent and hence
supply explicit pairwise failures.  Reporting the six nulls is essential: the
search was not constructed to force failure for every pair.

## Higher-order witness

For the bounded D5/D6/D7 signature sets, the union of all constituent and
pairwise one-combiner responses contains 194 functions.  Allowing a nested
second combiner over one response from each of the three expands the set to all
256.  Exactly 62 functions, including signature `00000111` in lexicographic
input order, are therefore genuinely present at order three and absent from
every constituent pair at this scope.

## Bounded completeness proof

The input universe is the Cartesian product `{0,1}^3`, so the response universe
has exactly `2^8 = 256` truth tables and is explicitly enumerated.  Each domain
generator is a Cartesian product, combination iterator, or breadth closure over
the exact finite choices in the freeze.  The verifier compares generated sets
to independent combinatorial counts for D1 parameter tuples, D2 exception
sets, D3 precision values, D5 permutations, D6 transition/output tables, D7
response tables, and D8 one-edit states.  It then enumerates all 28 pairs and
all registered D5/D6/D7 nested triples.  Set difference against the complete
256-table oracle produces each witness; therefore no candidate in a registered
class or composition was skipped.

## Claim ceiling

`P2 FINITE-EXACT` for the stated bounds only.  D4 and D6 are universal under
looser resources, and several pair classes are already complete on three-bit
functions.  No result licenses global D1--D8 irreducibility, an unknown domain,
or an asymptotic lower bound.
