# Z4 parent-ownership disclosure

## 1. Literature parents

| parent | citation | what it owns | not claimed here |
|---|---|---|---|
| Moore machines | Moore, *Gedanken-experiments on sequential machines*, Automata Studies, Princeton UP, 1956 | the Moore form and its defining property | the family and its property are Moore's; this package measures its frontier |
| Mealy machines | Mealy, *A method for synthesizing sequential circuits*, Bell Syst. Tech. J. 34(5):1045-1079, 1955, doi:10.1002/j.1538-7305.1955.tb03788.x | the Mealy form | as above |
| Behavioural quotient | Nerode, *Linear automaton transformations*, Proc. AMS 9:541-544, 1958, doi:10.1090/S0002-9939-1958-0135681-9; Myhill 1957 | quotienting a machine by behavioural equivalence | the `65552 -> 21904` collapse is an instance of Nerode's construction |
| Universality classes | Kadanoff, *Scaling laws for Ising models near Tc*, Physics 2(6):263-272, 1966, doi:10.1103/PhysicsPhysiqueFizika.2.263; Hohenberg & Halperin, *Theory of dynamic critical phenomena*, Rev. Mod. Phys. 49:435, 1977, doi:10.1103/RevModPhys.49.435 | the idea that systems agreeing on scaling behaviour form a class independent of microscopic detail | no critical exponent is claimed here, and none is identified on a 2- or 3-rung ladder |
| Pareto frontiers | Pareto, *Manuale di economia politica*, 1906 | dominance and the efficient frontier | standard construction, used as such |
| Structural invariance | Birkhoff, *On the structure of abstract algebras*, Proc. Camb. Phil. Soc. 31(4):433-454, 1935, doi:10.1017/S0305004100013463 | quotient algebras and invariance under structure-preserving maps | the two-clause criterion is a narrow instance, not a new algebra |

## 2. In-repository parents (pinned in `MANIFEST_V1.json`)

| package | what it owns |
|---|---|
| `research/gmi-833-heldout-20-transitions-v1` | the registered universe and its candidate contract |
| `research/gmi-833-z-z7-impossibility-v1` (branch `research/833-sec-z2`, PR #1034) | the six registered named families and their predicates, and the `IM-5` Moore/Mealy structural separation which `UC-2` reproduces by an independent route and definition |
| `research/gmi-833-z-z2-minimal-prior-v1` (this branch) | the `48`-bit behaviour key, the `21904`-class semantic quotient and the three re-encoding generators `g_rename`, `g_state`, `g_out`, which clause 2 of the `UC-3` criterion uses. Re-implemented here; the definitions are Z2's |

## 3. Residual contribution

1. A **name-free class definition** by resource response over a declared budget
   ladder, with its own non-degeneracy guard validated on two planted degenerate
   definitions — `568` classes, `0` singletons, largest `14360`.
2. **Exact frontiers at every rung** and the exact closed forms
   `(L-1)*2^(L-1)` and `0`, derived analytically in one route and enumerated in
   the other.
3. A **stated refusal** on exponents with the rung counts printed and a guard
   that is shown to accept when the rungs suffice.
4. A **two-clause irreducibility criterion** and its verdict on `16`
   distinctions, with the null that actually tests the second clause, and two
   frozen hypotheses refuted: neither the state-bit split nor the Moore/Mealy
   membership split survives the semantic quotient.

Everything else is parent property.
