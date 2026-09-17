# THEORY — known-family derivation tranche: symbolic logic, state-space, retrieval (GMI #833)

## Scientific question

For three #833 census families the prior lanes did not treat — symbolic logic
systems (benchmark K05), state-space models (census row; no benchmark entry),
retrieval-augmented systems (benchmark K08) — can the family's morphology be
DERIVED: recovered as the search's own output on a coverage-complete neutral
battery under a tier-declared basis carrying no family information, with the
recovery boundary mapped honestly (which tasks admit the family solution,
which do not — boundaries are results, not failures)?

## Substrate (registered, family-neutral)

Value domain D = [-3,3] (primary; ablations [-2,2], [-4,4]); basis = atoms +
constants {-1,0,1} + binary {ADD} + unary tier U_ORD = {NEG} U {GE_c : c in D}
(the complete one-sided order-test tier; v2 rules verbatim). Machines:

- **M_STREAM(k)**: cells s in D^k, all-zero initial; per stream position,
  s_i := e_i(s, x), y := e_y(s, x); the SAME transition at every position
  (imposed by battery homogeneity). Cost = rho*k + operator nodes.
- **M_ITER(k, T)**: cells loaded from the task encoding; a time-invariant
  transition for T steps; output = designated cell. Cost = rho*(work cells)
  + operator nodes. D-domain finite-scope analog of the pinned G0 register
  core (labelled register/control lineage).

Semantic equivalence class of a machine = its exact output trace/tuple over
the complete battery (the battery enumerates the whole input class, so
trace-equality IS semantic equality at scope). Both machine models expose the
same search surface: expression tuples over the frozen basis; no rewrite,
match, table, select, or store primitive exists anywhere in the basis.

## TR-2 — state-space models (M-FAM)

Formalism. The family morphology at scope: machines whose step map
(s, x) -> (s', y) is integer-affine (zero GE sites anywhere) with persistent
recurrent state. Machine space: the gate-free subspace of M_STREAM. Semantic
equivalence class: equal output traces. Morphology descriptor (posthoc):
gate-site count zero + superposition linearity of the input-output map +
state-cell history decomposition s_t = sum_l a_l x_{t-l} (superposed memory
vs pure delay copy).

**Theorem 1 (affine boundary, all costs).** For any k, a gate-free M_STREAM(k)
machine's cells satisfy s_t = c + sum_{l>=1} A_l x_{t-l} (finite matrix
recurrence unravelling; guard-legal on the battery stream), hence y_t is an
integer-affine form in the input history window of width k+1. Conversely any
guard-legal affine window map is realized by a gate-free machine (constructive
realization with node-level legality). On the B_W2 battery (window width 2,
two de Bruijn periods) every correct machine's output depends only on
(x_{t-1}, x_t); a k-cell gate-free machine with a nonzero coefficient on
x_{t-2} would differ across the two periods' position pairs that share the
2-window but differ in 3-window — the de Bruijn order-3 stream contains all
3-grams, so all effective coefficients beyond lag 1 must vanish: the
gate-free-realizable truth tables are EXACTLY the D-valued affine tables
(231 of 2401), modulo guard legality of the realization.
*Certificate*: exhaustive integer-matrix enumeration at k=1 (coefficients in
[-3,3], 117,649 tuples) and k=2 ([-2,2]^8 x [-1,1]^4), plus the induction
proof for all k <= cell cap.

**Theorem 2 (order-swap impossibility for B_EP, all k, all costs).** Any
GE-free M_STREAM machine (any k) has final output = an affine form of the
stream tokens (induction on steps: affine updates preserve affine state).
B_EP contains two episodes differing only by the presentation order of the
two (key, value) pairs with values swapped appropriately; the required
outputs permute, but a fixed affine form cannot (the coefficient of the
value token at stream position 2 must be both 1 and 0). Hence every correct
B_EP machine contains at least one order-test site — content comparison is
forced by presentation-order completeness, not by authorship.
*Certificate*: exhaustive coefficient-tuple check ([-3,3]^6) — zero matches.

**Resource crossover (cells vs gates; derived, not chosen).** With register
price rho and uniform operator cost, the 2-lag-superposition subclass admits
(a) a 2-cell gate-free machine at cost 2*rho (pure delay-line cells) and
(b) a 1-cell gated machine coding two bits into one domain value (the v2 T2
lag-2 signed-encoding construction) at cost rho + c_gated. The morphology
switches at rho-dagger = c_gated; measured by the exhaustive searches at
rho in {1,2,4,8,16}.

## TR-3 — retrieval-augmented systems (K08)

Formalism. Family morphology at scope: a machine whose cells PERSISTENTLY
hold >= 2 distinct bound items across the query step, whose read path
selects between stored items as a function of the QUERY content (a match
test composed from GE sites — no table primitive exists), and whose output
is causally determined by the selected item (intervention-checkable).
Machine space: all of M_STREAM(k<=8); retrieval is a MORPHOLOGY (eq+mux
composition), never a primitive.

Boundary theorem (order completeness): on the order-complete battery the
positional machine (output = the value at a fixed stream position) errs on
exactly the 8 episodes where the queried key sits at the other position —
the 8-error wall the first search execution hit empirically — and no
GE-free machine is correct at all (Theorem 2). On the ORDER-FIXED ablation
battery the positional machine is exactly correct and cheaper: the
retrieval boundary is presentation-order completeness, earned by
counterexample (the order-fixed champion is the counterexample machine and
its clause battery fails C2: its output does not depend on query content).

## TR-1 — symbolic logic systems (K05)

Formalism. Family morphology at scope: a machine whose work cells carry
subterm-controlled discrete structure (divergence under single-subterm
input change), whose trajectory realizes an iterated local transformation
(staged convergence: the work-state after each phase is a function of the
intermediate term — phase-shifted trajectory match between (t0, rs, g) and
(t1, rs, g) where t0 -> t1 -> g is a contraction chain), with selection
among alternative legal successors (trajectory divergence under rule-set
swap at same-lhs/different-rhs multi-successor structures). Machine space:
all of M_ITER(24 cells, 16 steps); rule-like behavior is a composed
morphology over guarded local edits (GE guards + ADD/NEG combination),
never a supplied macro.

Boundary (completeness forces composition): no sparse-affine (<=4 nonzero
+-1 coefficients, bias in D) or single-gate readout machine solves the
battery (exhaustive certificate over 56,136 support/sign candidates x 7
biases x 7 cuts) — the answer is not a low-order statistic of the encoding.
Nested sub-batteries ordered by the frozen hash: readout-only genomes
(direct map morphology) suffice at small sizes and their cost grows with
sub-battery size, while unrestricted genomes' champion cost stays flat —
the crossover IS the derivation of compositional (rule-application)
morphology from battery completeness. The readout-only champion on the
size-1 sub-battery is the counterexample machine earning the boundary.

## Nulls

200-seed equal-size random admission (frozen hash recipe, grammar-growth
NULL-1): TR-2 analytic resampling over the per-task closure results; TR-3
and TR-1 null batteries (outputs redrawn uniform {0,1}) searched at the
declared budgets. Reported: full null distributions, count of nulls
strictly better, empirical rank of the true battery.

## What this proves / does not prove (claim ceilings)

PROVES (at the declared finite scopes): the three family morphologies are
recovered or bounded-recovered under a protocol whose every channel is
frozen and screened; the recovery boundaries (affine table class;
presentation-order completeness; battery-size crossover) are measured with
exhaustive certificates or counterexample machines; the family-information
content of task-authorship is quantified by the nulls.

DOES NOT PROVE: recovery at scales beyond the caps (k > 2 gate-free
machine-verified, DP costs > 8, M_ITER beyond 24 cells/16 steps); learning
or training extensions; that these bases are the uniquely neutral ones
(bounded by the U_V1 contrast tier); real-scale utility.
