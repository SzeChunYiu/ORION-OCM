# AE12 parent ownership and residual contribution

## What the parents own

**The free-energy functional and its decomposition.** `F(q, o) = KL(q||P0) -
E_q[log2 L(o|s)] = -log2 P(o) + KL(q || posterior)` is the evidence lower bound
of variational inference. Jordan, Ghahramani, Jaakkola and Saul (1999), *An
Introduction to Variational Methods for Graphical Models*, Machine Learning
37:183-233, doi:10.1023/A:1007665907178; Blei, Kucukelbir and McAuliffe (2017),
JASA 112(518):859-877, doi:10.1080/01621459.2017.1285773. The identity, the fact
that its minimiser is the posterior, and the fact that a restricted family pays
a divergence penalty are all theirs.

**Active inference.** The free energy principle and its process theory are
Friston's: Friston (2010), Nature Reviews Neuroscience 11:127-138,
doi:10.1038/nrn2787; Friston, FitzGerald, Rigoli, Schwartenbeck and Pezzulo
(2017), *Active Inference: A Process Theory*, Neural Computation 29(1):1-49,
doi:10.1162/NECO_a_00912; Parr, Pezzulo and Friston (2022), *Active Inference*,
MIT Press, doi:10.7551/mitpress/12441.001.0001. The expected-free-energy
functional and its risk/ambiguity decomposition are theirs.

**The technical criticisms.** Biehl, Pollock and Kanai (2021), Entropy 23(3):293,
doi:10.3390/e23030293; Aguilera, Millidge, Tschantz and Buckley (2022), Physics
of Life Reviews 40:24-50, doi:10.1016/j.plrev.2021.11.001; Bruineberg, Dolega,
Dewhurst and Baltieri (2022), Behavioral and Brain Sciences 45:e183,
doi:10.1017/S0140525X21002351. Every criticism in the receipt's table is theirs;
none is claimed here.

**The comparators.** Rate-distortion theory: Shannon (1959), IRE National
Convention Record 7:142-163; Berger (1971), *Rate Distortion Theory*,
Prentice-Hall; rational inattention: Sims (2003), Journal of Monetary Economics
50(3):665-690, doi:10.1016/S0304-3932(03)00029-1. Control as inference: Todorov
(2009), PNAS 106(28):11478-11483, doi:10.1073/pnas.0710743106; Kappen, Gomez and
Opper (2012), Machine Learning 87:159-182, doi:10.1007/s10994-012-5278-7; Levine
(2018), arXiv:1805.00909.

**Markov blankets.** Pearl (1988), *Probabilistic Reasoning in Intelligent
Systems*, Morgan Kaufmann. The blanket definition and its conditional-independence
characterisation are Pearl's.

## What is explicitly NOT claimed novel

Nothing in the mathematics above. In particular this package does not claim to
have discovered that free-energy minimisation recovers the Bayes posterior, that
mean-field families are biased, that misspecified models give wrong posteriors,
that expected free energy decomposes into risk and ambiguity, or that Markov
blankets need not exist. Every one of those is parent-owned and is cited.

The package registers `GMI_NOVEL_OVER_ACTIVE_INFERENCE` as a **forbidden
promotion** and emits `PARENT_SUFFICIENT` at the perception scope, where the
parent owns the result outright.

## The named residual contribution of this tranche

1. **A finite exactly-rational instantiation.** The registered dyadic
   restriction makes every entropy, divergence and free energy an exact rational
   number of bits, so the parent identities and their failures are *checked* on a
   concrete roster rather than argued. That is an engineering residual, not a
   mathematical one, and it is stated as such.
2. **A necessity certificate for each assumption.** Each of the three assumptions
   the equivalence needs is paired with a registered world where dropping it
   breaks the equality, with the exact price attached: exactly `1` bit for the
   mean-field restriction, a named posterior disagreement for misspecification,
   and a preference-independent `1`-bit gap for the ambiguity term.
3. **The preference-independence argument in AE12-4.** The observation that two
   actions with identical predicted outcome distributions have equal risk terms
   for *every* preference distribution, so that the expected-free-energy order is
   pinned at the ambiguity difference and cannot be re-ordered by any preference
   prior, is elementary but is stated here as an exact finite certificate with a
   `2/27` exhaustive rarity census. The underlying decomposition is the parents'.
4. **Machine-evaluated criticisms.** Each cited criticism is attached to a finite
   predicate a program evaluates on a registered object. The criticisms are the
   authors'; only the attachment is this tranche's.
5. **A pre-registration that actually refuted two of its own predictions**, with
   the refutations reported, attributed to a single stage, and paired with the
   statement that was earned instead.
