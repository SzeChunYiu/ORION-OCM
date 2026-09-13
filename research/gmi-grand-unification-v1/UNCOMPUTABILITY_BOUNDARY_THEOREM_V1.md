# Grand GMI Uncomputability Boundary Theorem V1

Status: **NO-GO THEOREM**  
Date: 2026-09-12

## 1. Claim

There is no total computable procedure that, for every unrestricted Turing-complete GMI instance with unbounded horizon, returns the exact protected capability/reachability result.

This is not an empirical conjecture. It follows by reduction from the halting problem.

## 2. Reduction

Take an arbitrary program `p` and input `x`. Construct a deterministic machine `M_{p,x}` with no informative external input. On start it simulates `p(x)`. If and only if the simulation halts, `M_{p,x}` emits protected success symbol `1`; otherwise it continues forever without success.

Declare the obligation

\[
\Omega_{halt}: \text{eventually emit }1.
\]

Then

\[
M_{p,x}\models\Omega_{halt}
\iff
p(x)\text{ halts}.
\]

Suppose a total exact GMI solver `A` decided obligation satisfaction, exact unbounded reachability, or the exact capability coordinate for every such instance. Running `A(M_{p,x},Omega_halt)` would decide whether `p(x)` halts, contradiction.

Therefore no such total solver exists.

**GG35 — unrestricted exact-solver no-go.** Exact global algorithmic closure over unrestricted Turing-complete machine spaces and unbounded horizons is impossible.

## 3. Frontier form

The same reduction can be embedded into a frontier query. Let the admissible set contain `M_{p,x}` and a dead machine that never emits success. Give both identical registered resource cost. The attainable set contains a capability-1 point iff `p(x)` halts. A total procedure returning the exact attainable set/frontier would therefore decide halting.

Thus the no-go applies not merely to source-code equivalence but to exact unrestricted GMI capability/frontier computation.

## 4. What remains decidable

The theorem does not weaken the finite operational completeness result. If the horizon, state/action spaces, legal kernel family and development budget are finite/decidable, exhaustive exact closure is valid.

Many structured infinite problems are also computable under additional restrictions. The no-go applies to a total procedure covering all unrestricted Turing-complete instances.

## 5. Theory completion consequence

A fundamental theory should distinguish:

- **global definability** — the semantic quotient, cut spectrum, transformation spectrum, physical frontier and reachability objects are mathematically specified for the declared process problem;
- **instance solvability** — a particular object can be computed/proved/approximated under its regularity and computability assumptions.

Requiring the first is a theory requirement. Requiring the second for every unrestricted process would contradict computability theory.

Therefore uncomputability is a boundary theorem of Grand GMI, not an unresolved architectural gap.