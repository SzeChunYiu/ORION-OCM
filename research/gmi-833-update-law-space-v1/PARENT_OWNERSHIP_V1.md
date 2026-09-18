# Parent ownership disclosure — GMI #833 Section I, package `gmi-833-update-law-space-v1`

This is the declared parent-ownership file for the package. It is the ONE place
where the named-algorithm instance may be named, and it is a declared exemption
of the A1 lexical screen for exactly that reason (see `DENYLIST_V1.json`).

Assimilation-first: each parent below is absorbed, its mathematics is stated as
ITS mathematics, and the residual of this tranche is named afterwards. Nothing
in this package claims priority over any of it.

## 1. What is NOT claimed novel here

### 1.1 Reverse accumulation and the cheap-gradient principle

**The cheap-gradient principle is PARENT MATHEMATICS. This tranche does not
claim it, does not improve it, and does not re-derive it as a contribution.**
The principle — that the reverse-mode gradient of a scalar function costs a
small constant multiple of one evaluation of the function, independent of the
number of independent variables — is owned by:

- S. Linnainmaa (1970), *The representation of the cumulative rounding error of
  an algorithm as a Taylor expansion of the local rounding errors*, MSc thesis,
  University of Helsinki; and S. Linnainmaa (1976), *Taylor expansion of the
  accumulated rounding error*, BIT Numerical Mathematics 16(2):146-160,
  DOI `10.1007/BF01931367`.
- B. Speelpenning (1980), *Compiling Fast Partial Derivatives of Functions Given
  by Algorithms*, PhD thesis, University of Illinois at Urbana-Champaign,
  report UILU-ENG 80-1702.
- A. Griewank and A. Walther (2008), *Evaluating Derivatives: Principles and
  Techniques of Algorithmic Differentiation*, 2nd edition, SIAM,
  DOI `10.1137/1.9780898717761`. The cheap-gradient result, the vertex/edge
  elimination view of accumulation, and checkpointing as an explicit
  recomputation-versus-retention trade are all theirs (notably Ch. 4, Ch. 9,
  Ch. 12).
- W. Baur and V. Strassen (1983), *The complexity of partial derivatives*,
  Theoretical Computer Science 22(3):317-330,
  DOI `10.1016/0304-3975(83)90110-X`.
- F. L. Bauer (1974), *Computational graphs and rounding error*, SIAM Journal on
  Numerical Analysis 11(1):87-96, DOI `10.1137/0711010` — the path-sum formula
  for derivatives over a computational graph, which is what the Route B oracle
  computes directly.

`IL-4d` in the theorem note re-derives the cheap-gradient bound inside this
package's declared cost model. That re-derivation exists ONLY as a consistency
check on the cost model: if the model had contradicted the parent bound, the
model would have been wrong. It is explicitly not a residual contribution.

### 1.2 The named algorithm

The connectionist named-algorithm instance is D. E. Rumelhart, G. E. Hinton and
R. J. Williams (1986), *Learning representations by back-propagating errors*,
Nature 323:533-536, DOI `10.1038/323533a0`. The name of that algorithm —
backpropagation, commonly backprop — appears in this package only in this file.
It appears in no identifier, no definition module, no theorem statement, no
search space and no objective function. The theorem note derives the regime
structure of reverse accumulation from graph and resource structure alone; it
does not derive, and does not claim to derive, that named algorithm as
necessary.

### 1.3 Optimal accumulation order

U. Naumann (2008), *Optimal Jacobian accumulation is NP-complete*, Mathematical
Programming 112(2):427-441, DOI `10.1007/s10107-006-0042-z`. The elimination-
order census in `IL-4e` is an exhaustive certificate over registered small
graphs (at most 120 orders per graph). It is NOT a solution to optimal Jacobian
accumulation and asserts no general optimality. The census confirms Naumann's
regime on the registered `skip_waist_n2_p2` graph, where a mixed elimination
order strictly beats both pure orders.

### 1.4 Selection requires stated assumptions

- D. H. Wolpert and W. G. Macready (1997), *No Free Lunch Theorems for
  Optimization*, IEEE Transactions on Evolutionary Computation 1(1):67-82,
  DOI `10.1109/4235.585893`.
- T. M. Mitchell (1980), *The Need for Biases in Learning Generalizations*,
  Rutgers technical report CBM-TR-117.
- J. R. Rice (1976), *The Algorithm Selection Problem*, Advances in Computers
  15:65-118, DOI `10.1016/S0065-2458(08)60520-3`.

### 1.5 Combinatorics

The expected position of the first marked item in a uniformly random
arrangement of `m` marked items among `d` positions, and the hockey-stick
identity `sum_{j=m}^{d} C(j,m) = C(d+1,m+1)` that evaluates it, are standard
combinatorics. `IL-2a` applies them; it does not discover them.

## 2. In-corpus parents

### 2.1 Earned authority (pinned in `MANIFEST_V1.json` by path and blob sha)

- `research/gmi-833-foundation-v1` (#837) — the realization contract
  `(X, x0, Q, U, Chi, rho)`, the behavioral specification `B = (I, Acc)`, the
  development law `Delta`, `Reach_Delta(M0, B)`, PF-1, PF-2, R-1, R-2. Every
  object in `IL-1` is built on these; none is newly invented here.
- `research/gmi-833-update-law-nfl-v1` (#870) — the DIRECT PARENT of this
  section. NFL-I1 (uniform-completion equality) and NFL-I3 (constructive
  ecology preference reversal) are why `IL-2` and `IL-3` must be conditional on
  a stated ecology and price structure rather than naming a winner. This
  tranche supplies what #870 said was required: the explicit assumption classes.
- `research/gmi-833-axiom-core-v1` (#854) — AX-1..AX-6. AX-3 (nonnegative
  rational resource coordinates, coordinatewise additive path cost) is the
  premise from which the quiet-step clause of composition is derived in `IL-1.4`.
- `research/gmi-833-no-smuggling-audit-v1` (#855) — the A1 lexical screen and
  the A2 semantic-macro screen with its 11-field signature. The neutrality
  certificate here is an application of that contract, not a new screen.
- `research/gmi-833-remint-equivariance-v1` — presentation-relabeling
  equivariance. The opaque-token remint certificate is an application.
- `research/gmi-833-theory-baseline-v1` — the frozen baseline, its forbidden
  promotions, and the revival doctrine that forbids closing a negative by
  narrowing it.

### 2.2 Disclosed prior art that is NOT proof authority

Both packages below predate #833, are merged on main, and are disclosed here in
full. Neither is cited as a premise, neither has any artifact imported, and no
result of either is re-claimed.

- `research/gmi-formal-derivation-v1/OPTIMIZATION.md`, clause **O4**
  (first landed in commit `1858f7b9`). **This is the closest in-corpus prior art
  to IL-4.** O4 already sets the output adjoint to one, already processes nodes
  in reverse topological order, already proves the accumulation by substituting
  total differentials and summing path products, already handles shared
  parameters by summation, already states that the named primitive need not be
  opaque, already flags the unit-cost elementary-operation caveat, and already
  names checkpointing as a recomputation-versus-retention exchange. Anyone
  reading IL-4 must read O4 first.
  The #870 manifest records `historical_non_authority: "gmi/learning-law-..."`
  for an unmerged branch; that disposition does not apply to this file, which is
  simply pre-#833 corpus work. It is disclosed, absorbed, and not used as
  authority.
- `research/gmi-learning-law-selection-v1/LEARNING_LAW_SELECTION_THEOREM_V1.md`
  (#590/#594/#601/#605). **This is the closest in-corpus prior art to IL-2 and
  IL-3.** Its LLS-3 already establishes that at a fixed capability set the price
  vector alone selects the law, and its LLS-6 already shows that ties are a
  price-equality artifact rather than an incompleteness. It is named
  `historical_non_authority` by the #870 manifest and is treated here as
  disclosed prior art only.
- `research/gmi-section-c-learning-laws-v1` — same disposition.

## 3. The named residual of this tranche

Everything above is subtracted. What remains, and is claimed only at the
registered finite scope:

1. **IL-1.** An admissible update-law space defined over the #837 realization
   contract with no architecture, optimizer or algorithm name in the definition;
   a decidable finite admissibility predicate with an exact operation bound;
   exact closure algebra (mixture at both grades, composition at the closure
   grade, a two-sided monoid whose identity clause is *derived* from AX-3);
   the exact failure of composition closure at the one-step grade, earned by
   counterexample; the subassociativity of worst-case resource charging under
   re-bracketing, earned by counterexample; and a mechanically verified
   name-freedom certificate combining the A1 lexical screen, the A2 semantic
   screen and opaque-token remint invariance.
   Prior art owns the realization contract and both screens. It does not own
   this space, its closure algebra, or the two counterexamples.
2. **IL-2 / IL-3.** The exact threshold `rho*` separating evaluative-only from
   directional update laws, derived from the information structure of the
   declared channels rather than read off a register of named laws; stated as an
   EQUALITY over the whole verified-selection family under the successor-
   relabeling orbit, so that it is unconditional rather than premised on
   equivariance; the exact three-way partition of the registered price/ecology
   space with no gap and no overlap; and the per-instance boundary delivered by
   an explicit counterexample.
   LLS-3 owns "resources select the law". It does not own an architecture-
   neutral threshold, its derivation from channel information structure, its
   value `(d+1)/(m+1)`, or the partition certificate.
3. **IL-4.** The sweep-count NECESSITY half (prior art establishes sufficiency;
   the constructive indistinguishability argument for insufficiency at `k < n`
   is supplied here); the exact retention-price threshold
   `sigma* = (n-p)E/(N-w)` in graph invariants with `w` computed from a declared
   storage schedule; the unconditional `p > n` converse; and the recovery of the
   accumulation order as the argmin of an exhaustive search over an unnamed
   elimination-order space, where the argmin FLIPS with the output-to-input
   ratio without any name entering the space or the objective.
   O4 owns the adjoint recursion and the checkpointing caveat. Griewank and
   Walther own the cheap-gradient principle and the elimination view. Naumann
   owns the NP-completeness of the general problem.
