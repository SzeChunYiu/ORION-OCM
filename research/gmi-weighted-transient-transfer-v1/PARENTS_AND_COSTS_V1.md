# Matched parents, subtraction and full charges

## Primary mathematical parents

- [Feinberg–Huang, On the Reduction of Total-Cost and Average-Cost MDPs to
  Discounted MDPs](https://arxiv.org/pdf/1507.00664), Proposition 1,
  Sections 3.2/3.4 and Proposition 8. Weighted transience, bounded comparison
  functions and the Hoffman–Veinott transformation are mature mechanisms.
  Under the paper's conditions, V<=mu<=KV and Qmu<=mu-V imply
  Qmu<=(1-1/K)mu. That is the contraction form used here. Its Borel optimizer
  results additionally require the stated measurability, compactness and
  continuity assumptions; WTT does not inherit them without verification.
- [Bertsekas, Proper Policies in Infinite-State Stochastic Shortest Path
  Problems](https://arxiv.org/html/1711.10129v2), Sections II/V:
  finite expected termination and comparison-function domains matter in
  undiscounted problems. Properness is not a pathwise length bound.
- [Cavus–Ruszczynski, Risk-Averse Control of Undiscounted Transient Markov
  Models](https://optimization-online.org/wp-content/uploads/2012/03/3406.pdf),
  Section 2 and the risk-neutral specialization of Section 6: weighted
  substochastic-kernel transience on Borel spaces. We use that risk-neutral
  mechanism, not their nonlinear risk objective or its policy assertions.
- [Wiesemann–Kuhn–Rustem, Robust Markov Decision
  Processes](https://doi.org/10.1287/moor.1120.0566): a covered model confidence
  region can warrant a subsequently selected policy. This is the statistical
  logic being reused, not a new confidence principle or a claim that every
  uncertainty set admits the same tractable robust dynamic program.
- [Wolff–Topcu–Murray, Robust Control of Uncertain MDPs with Temporal Logic
  Specifications](https://www.cds.caltech.edu/~murray/papers/wtm12-cdc.html):
  supplied transition uncertainty and an SSP reduction are prior robust-control
  mechanisms. WTT does not claim novelty for robust SSP or import temporal
  abstraction correctness automatically.

The finite backward replacement proof is a weighted, undiscounted application
of the common-policy simulation argument already used in FMT/CMP. Geometric
drift supplies its summable continuation bound. There is no new general
Bellman theorem, SSP solver, model-identification theorem or learning law.

## Exact internal parent binding

PARENT_BINDINGS_V1.json identifies commit, original path, bytes and SHA256 for
the complete copied ARC, FMT, CMP and SPS theorem parents under raw/parents/.
These are explanatory authorities, not executable dependencies; active parent
documents and frozen historical receipts are unchanged. Their finite/known-law
scope is retained. Main at binding is df777cd79ba5ec6925fd82552e9341f8d73f3577.

## What the finite implementation actually certifies

The checker receives explicit rational finite model vertices, a nominal model
and supplied w,beta,C. It validates all retained rows, including zero-observation
states, and computes weighted error/charge/probability envelopes. Affinity of
drift/cost inequalities and convexity of absolute error make these bounds valid
for the rowwise convex hull of the supplied rows, and any correlated subset.
This is a sufficient rectangular envelope, not an exact robust optimization
algorithm. It never asserts that listed vertices cover an arbitrary statistical
confidence region. No generic continuous-corner sufficiency is assumed.

Independent exact absorbing-chain elimination evaluates stationary witnesses.
Finite tree execution and deterministic analytic examples check the bound
rather than substitute finite enumeration for the measurable theorem.

## Charge register

Record acquisition calls, all state preparation/resets, observation, audit
storage, conditional-law/support identification, confidence calculation,
tail-envelope certification, synthesis of w/beta, robust row supremum solving,
verification, policy search/evaluation, executable controller/program retention,
random-bit/seed setup, deployment actions and stopping/settlement separately.
Their units must match before addition; WTT's c is only the declared
nonnegative expected resource coordinate. The same argument may be applied
coordinatewise with separate constants; scalar minima are not a Pareto proof.

The total realized acquisition/synthesis cost is already payable when D is
selected. If policy-dependent setup is compared, use it in the same augmented
objective on both sides. A comparator given a law or controller for free is a
different experiment. Analytic existence of a certificate or approximate policy
does not price or construct it. No hardware work, elapsed time, state meaning,
physical safe rescue, global architecture winner or learned-method transfer
claim is inferred from these exact arithmetic controls.
