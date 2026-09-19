# AE11 parent-ownership disclosure

Assimilation-first: the parent science below is absorbed and credited, and the
residual contribution of this tranche is stated afterwards. **Nothing in the
list is claimed novel.** The parents own the physics and the mathematics; this
package owns one exact finite construction and its machine-checked verification.

## Strongest parents

| parent | what it owns | citation |
|---|---|---|
| Landauer's principle | that erasing one bit of information in contact with a reservoir at temperature `T` costs at least `k_B T ln 2` of dissipated work, and that the cost attaches to logical irreversibility rather than to computation as such | Landauer, "Irreversibility and heat generation in the computing process", IBM Journal of Research and Development 5 (1961) 183-191. doi:10.1147/rd.53.0183 |
| Reversible computation | that any computation can be made logically reversible, so that the erasure cost is not a cost of computing but of discarding; and the resolution of the demon by the cost of resetting its memory | Bennett, "Logical reversibility of computation", IBM Journal of Research and Development 17 (1973) 525-532, doi:10.1147/rd.176.0525; Bennett, "The thermodynamics of computation -- a review", International Journal of Theoretical Physics 21 (1982) 905-940, doi:10.1007/BF02084158 |
| Experimental verification | the measured saturation of the Landauer limit in a single-particle colloidal bit, which is the empirical warrant for the bound this package only audits formally | Berut, Arakelyan, Petrosyan, Ciliberto, Dillenschneider, Lutz, "Experimental verification of Landauer's principle", Nature 483 (2012) 187-189. doi:10.1038/nature10872 |
| The demon and the value of information | that information about a system converts to extractable work, and the engine that makes it exact | Szilard, "Uber die Entropieverminderung in einem thermodynamischen System bei Eingriffen intelligenter Wesen", Zeitschrift fur Physik 53 (1929) 840-856. doi:10.1007/BF01341281 |
| Information thermodynamics with feedback | the generalized second law with mutual information, which is why an erasure bound stated without conditioning on correlations is the wrong bound | Sagawa and Ueda, "Minimal energy cost for thermodynamic information processing", Physical Review Letters 102 (2009) 250602, doi:10.1103/PhysRevLett.102.250602; Parrondo, Horowitz, Sagawa, "Thermodynamics of information", Nature Physics 11 (2015) 131-139, doi:10.1038/nphys3230 |
| Shannon entropy | the entropy of a distribution, its maximum at the uniform distribution, and the code-length reading used here to compute it by an independent route | Shannon, "A Mathematical Theory of Communication", Bell System Technical Journal 27 (1948) 379-423. doi:10.1002/j.1538-7305.1948.tb01338.x |
| Algorithmic complexity | the definition of `K`, the invariance theorem, machine-relativity up to an additive constant, and the counting argument that most strings are incompressible | Kolmogorov, "Three approaches to the quantitative definition of information", Problems of Information Transmission 1 (1965) 1-7; Chaitin, "On the length of programs for computing finite binary sequences", JACM 13 (1966) 547-569, doi:10.1145/321356.321363; Li and Vitanyi, *An Introduction to Kolmogorov Complexity and Its Applications*, 4th ed., Springer (2019), doi:10.1007/978-3-030-11298-1 |
| Statistical-mechanical entropy | the Boltzmann count `S = k_B ln W`, the Gibbs form, and the information-theoretic reading that relates them | Jaynes, "Information theory and statistical mechanics", Physical Review 106 (1957) 620-630. doi:10.1103/PhysRev.106.620 |
| Energy measurement methodology | how one actually measures the energy of a computation on real hardware -- the methodology this package explicitly does **not** perform and whose absence is the reason three AE11 rows stay open | Strubell, Ganesh, McCallum, "Energy and Policy Considerations for Deep Learning in NLP", ACL 2019, arXiv:1906.02243; Henderson, Hu, Romoff, Brunskill, Jurafsky, Pineau, "Towards the Systematic Reporting of the Energy and Carbon Footprints of Machine Learning", JMLR 21 (2020) 248, arXiv:2002.05651 |

## What is NOT claimed novel

- That Shannon entropy, algorithmic complexity, Boltzmann entropy and Clausius
  entropy are different quantities. This is textbook.
- That `H <= log2 W` with equality exactly at the uniform distribution.
- That `K` is machine-relative and defined only up to an additive constant.
- That erasing `m` bits costs at least `m k_B T ln 2` under the stated
  assumptions, and that a quasi-static protocol saturates it.
- That a logically reversible map has no erasure cost.
- That conditioning on correlations changes the bound, and that a correlated
  memory can beat the unconditioned form. Szilard, Sagawa-Ueda and
  Parrondo-Horowitz-Sagawa own this completely.
- That a bound on erasure does not bound the total cost of an implementation.
- Any statement about the energy of any real computing device or organism. None
  is made here.

## Residual contribution of this tranche

1. A **single finite roster** of 8 composite objects on which all four notions
   are evaluated simultaneously in exact arithmetic, together with the complete
   12-cell ordered-pair non-dependence table, each cell carrying its witness
   objects and a classification of whether the witness exhibits slack in a
   registered definitional relation or outright registered independence.
2. A **frozen prefix-free machine** small enough to search exhaustively, with
   the complete 64-entry `K_U` table verified by two independent searches that
   share no code and no enumeration order, the instruction Kraft sum exactly `1`
   and the program Kraft sum exactly `67/128`.
3. A **resource registry** that turns the logical-versus-physical distinction
   into a checked property rather than a paragraph: 24 rows, two classes, and an
   executor assertion that the instantiated physical count is `0` and that no
   float reaches the receipt.
4. An **exact non-inference witness**: two registered device models of the same
   map with identical erased-bit count and registered operation counts differing
   by exactly 5, which makes "the Landauer bound does not determine total cost"
   a computed fact on this roster rather than a remark.
5. **Vacuity discipline applied to Landauer's own bound**: the bijection's
   record is emitted with bound value `0` against a definitional floor of `0`,
   flagged vacuous and unfalsified, and used to close nothing. Emitting the
   parent's most famous bound as vacuous where it genuinely says nothing is the
   kind of honesty the row asks for.
6. A **certified strict gap** between the count-based erased-bit number and the
   distributional drop for `F_AND`, decided by the integer comparisons
   `3**12 >= 2**19` and `3**5 <= 2**8` rather than by evaluating a logarithm,
   with the undecided value reported as `NOT_DECIDED`.

## What the residual does not license

The construction is finite, abstract and registered. It contains no physical
system, no measurement and no energy value. It cannot support any claim about
real hardware, about biological metabolism, or about whether information-theoretic
savings translate into energy savings — the three AE11 rows that stay open, each
with its required instrument named in `MANIFEST_V1.json`.
