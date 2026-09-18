# Parent ownership and residual disclosure v1

Package `gmi-833-cognitive-reaudit-social-v1` (#833 Section M: metacognition,
social cognition, communication, imitation/teaching, cultural accumulation).

Assimilation first. Every result below rests on mathematics and empirical
traditions that are **not ours**. This document names the strongest parent for
each result, states plainly what is *not* claimed novel, and then names the
narrow residual this tranche adds. Where a parent already owns a function, that
ownership is recorded as ownership, not as a threat to be routed around.

DOIs are recorded as the publisher-registered identifiers for citation
resolution. The ownership attributions below do not depend on any DOI string: if
an identifier fails to resolve it should be corrected in place, and the
attribution stands unchanged. Monographs are cited without a DOI.

---

## 1. Value of computation and metareasoning (MC-1)

**Strongest parents.**

- Howard, R. A. (1966). *Information Value Theory.* IEEE Transactions on Systems
  Science and Cybernetics 2(1), 22–26. DOI `10.1109/TSSC.1966.300074`.
- Russell, S. & Wefald, E. (1991). *Principles of metareasoning.* Artificial
  Intelligence 49(1–3), 361–395. DOI `10.1016/0004-3702(91)90015-C`.
  (Companion monograph: Russell & Wefald, *Do the Right Thing: Studies in Limited
  Rationality*, MIT Press, 1991 — book, no DOI.)

**Not claimed novel.** The expected-value-of-computation framing is **parent
mathematics and we say so without qualification.** The idea that a deliberation
step should be taken when its expected improvement to the finally chosen action
exceeds its cost is Howard's value of information specialized to internal
computation by Russell and Wefald. The backward-induction argument that gives an
optimal metalevel policy on a finite computation tree is theirs, and VOC-2 in
this package is labelled INSTRUMENTAL for exactly that reason. We claim no part
of it.

**Also not ours, and owned inside this repository.** Object-level plan-search
stopping — including any comparison between a myopic one-step EVC rule and the
optimal policy, and any counterexample separating them — is owned by issue #926 /
PR #927 (`research/gmi-833-cognitive-reaudit-v2`). This package neither computes
nor reports that comparison.

**Residual claimed here.** Two things, both narrow:

1. The **architecture-neutral external contract** for metacognition inside the
   #837/#833 foundation objects: metacognition registered as a property of the
   charged *allocation trace*, with the internal estimate never inspected.
2. **NONID-1**, an exact iff: a fixed-schedule twin reproducing the allocation
   trace-for-trace exists exactly when the allocation is a deterministic function
   of the registered observable instance label — with the latent-draw
   counterexample mapping the boundary, verified by exhaustive enumeration over
   the entire registered schedule space.

The non-identification statement, not the threshold, is what this row adds.

---

## 2. Comparison of experiments (MC-2 and MC-3 share this parent)

**Strongest parents.**

- Blackwell, D. (1953). *Equivalent Comparisons of Experiments.* Annals of
  Mathematical Statistics 24(2), 265–272. DOI `10.1214/aoms/1177729032`.
- Marschak, J. & Radner, R. (1972). *Economic Theory of Teams.* Yale University
  Press — book, no DOI. (Team-decision value of an information partition.)

**Not claimed novel.** REF-1 — the blockwise partition value, its monotonicity
under refinement, and the fact that finer information is never worth less — is
Blackwell/Marschak–Radner territory in full. We restate it exactly at the
registered finite scope only so that MC-2 and MC-3 can be derived from one
object, and we state the unification openly rather than letting the two rows look
independent when they are not.

---

## 3. Theory of mind (MC-2)

**Strongest parents.**

- Premack, D. & Woodruff, G. (1978). *Does the chimpanzee have a theory of mind?*
  Behavioral and Brain Sciences 1(4), 515–526. DOI `10.1017/S0140525X00076512`.
- Wimmer, H. & Perner, J. (1983). *Beliefs about beliefs: Representation and
  constraining function of wrong beliefs in young children's understanding of
  deception.* Cognition 13(1), 103–128. DOI `10.1016/0010-0277(83)90004-5`.
- Kaelbling, L. P., Littman, M. L. & Cassandra, A. R. (1998). *Planning and acting
  in partially observable stochastic domains.* Artificial Intelligence 101(1–2),
  99–134. DOI `10.1016/S0004-3702(98)00023-X`.
- Gmytrasiewicz, P. J. & Doshi, P. (2005). *A framework for sequential planning in
  multi-agent settings.* Journal of Artificial Intelligence Research 24, 49–79.
  DOI `10.1613/jair.1579`. (Interactive POMDPs: modelling the other agent's state.)

**Not claimed novel.** The false-belief paradigm's logic — that an agent's
*unobserved* state, and not its visible behaviour so far, predicts its
payoff-relevant future action — is Wimmer and Perner's, and the question is
Premack and Woodruff's. The formal apparatus for acting under partial
observability, and for conditioning on a model of another agent's hidden state,
belongs to the POMDP and I-POMDP literature.

**Residual claimed here.** The **exact ecology-relativity theorem**: `V_hid` and
`V_obs` differ by an exact rational gap, and the gap vanishes **iff** the other
agent's observed-action channel is sufficient for the payoff-relevant partition
of hidden states, with the equality condition stated only on the
positive-probability support. Plus the matched hostile twin as a census: across
`19263` registered ecologies, `15267` are ones in which a pure behaviour-reader
attains the mentalizer's score exactly. The claim that theory of mind is a
property of the `(ecology, channel)` pair rather than of the machine — with the
exact condition attached — is the residual.

---

## 4. Communication (MC-3)

**Strongest parents.**

- Shannon, C. E. (1948). *A Mathematical Theory of Communication.* Bell System
  Technical Journal 27(3), 379–423. DOI `10.1002/j.1538-7305.1948.tb01338.x`.
- Lewis, D. (1969). *Convention: A Philosophical Study.* Harvard University Press
  — book, no DOI. (Signalling games and the sender/receiver object.)
- Crawford, V. P. & Sobel, J. (1982). *Strategic Information Transmission.*
  Econometrica 50(6), 1431–1451. DOI `10.2307/1913390`.

**Not claimed novel.** The channel object, the sender/receiver decomposition, and
the value of a transmitted distinction are parent-owned. So is the observation
that a message is worthless when the receiver's best action does not depend on
it — this is folklore in team theory and in signalling games.

**Also not ours, and owned inside this repository.** Variation of communication
topology and price inside the *ecology generator* is owned by #959 / #957. This
package does not re-run or extend that sweep.

**Residual claimed here.** COM-2 as a **proved equivalence rather than an assumed
premise**: "the receiver can act differentially on the transmitted distinction" is
*equivalent* to strictly positive refinement value, so the strict-pay condition
COM-3 is a single exact inequality and not a conjunction. Plus both boundary
directions exhibited as registered censuses (`13915` free-but-useless, `16596`
valuable-but-unaffordable, `15895` exactly at the threshold), and COM-4, the
shared-observation aliasing hostile (`20950` instances).

---

## 5. Imitation and teaching (MC-4)

**Strongest parents.**

- Bandura, A. (1977). *Social Learning Theory.* Prentice-Hall — book, no DOI.
- Tomasello, M., Kruger, A. C. & Ratner, H. H. (1993). *Cultural learning.*
  Behavioral and Brain Sciences 16(3), 495–511. DOI `10.1017/S0140525X0003123X`.
  (The imitative/instructed/collaborative distinction.)
- Csibra, G. & Gergely, G. (2009). *Natural pedagogy.* Trends in Cognitive
  Sciences 13(4), 148–153. DOI `10.1016/j.tics.2009.01.005`.
- Goldman, S. A. & Kearns, M. J. (1995). *On the complexity of teaching.* Journal
  of Computer and System Sciences 50(1), 20–31. DOI `10.1006/jcss.1995.1003`.
- Shafto, P., Goodman, N. D. & Griffiths, T. L. (2014). *A rational account of
  pedagogical reasoning: Teaching by, and learning from, examples.* Cognitive
  Psychology 71, 55–89. DOI `10.1016/j.cogpsych.2013.12.004`.
- Zhu, X. (2015). *Machine teaching: An inverse problem to machine learning and an
  approach toward optimal education.* AAAI Conference on Artificial Intelligence
  — conference proceedings, no DOI.

**Not claimed novel.** That teaching is distinct from imitation, that a
demonstration can reduce a learner's acquisition burden, and that the teacher's
choice of examples is itself an optimization problem are all parent-owned. The
teaching-dimension literature already measures the size of a helpful
demonstration set.

**Residual claimed here.** The **resource-accounting separation**: imitation and
teaching are defined on *different* coordinates of the lifecycle resource vector
(the learner's charge and the demonstrator's charge), TCH-1 shows all four cells
realizable so neither predicate determines the other, `FAILED_TEACHING` is given
a name and a cell rather than being absorbed into teaching, and TCH-3 proves
**unconditionally** that omitting the demonstrator's charge strictly enlarges the
worthwhile set — `98` of `450` free-labour verdicts at the registered scope are
artifacts. NONID-4 adds the control-arm necessity theorem, validated on real
registered data in both directions (`0/200` false alarms, `200/200` recall).

---

## 6. Cultural accumulation (MC-5)

**Strongest parents.**

- Tomasello, M., Kruger, A. C. & Ratner, H. H. (1993), as above — the ratchet
  effect.
- Boyd, R. & Richerson, P. J. (1985). *Culture and the Evolutionary Process.*
  University of Chicago Press — book, no DOI.
- Henrich, J. (2004). *Demography and cultural evolution: How adaptive cultural
  processes can produce maladaptive losses — the Tasmanian case.* American
  Antiquity 69(2), 197–214. DOI `10.2307/4128416`. (Transmission fidelity,
  population size, and loss.)

**Not claimed novel.** The ratchet effect is Tomasello's. The modelling of
cultural change as a transmission process with fidelity and loss is Boyd and
Richerson's; the specific finding that insufficient fidelity produces loss rather
than accumulation is Henrich's. The affine recursion `a_{n+1} = phi a_n + g` and
its fixed point are elementary mathematics owned by nobody in particular.

**Also not ours, and owned inside this repository.** Within-lifetime library
formation and reuse transfer are owned by #897
(`research/gmi-833-g0-grammar-growth-v1`, GRW-1/INV-1/REC-1/HLD-1). This row is
about inter-generational transmission between populations.

**Residual claimed here.** Three things:

1. **CUL-1**, a complete exact rational classification — the step identity, the
   exact ratchet condition `lambda a_n < g`, the exact ceiling `a* = g / lambda`
   which is never crossed from either side, the return-to-baseline case and the
   lossless unbounded case — with nothing left conditional.
2. **NONID-5**, the unconditional statement that the capability trajectory alone
   never identifies transmission, because an independently re-deriving population
   reproduces any trajectory exactly. The witness is trivial; the point is that
   the observable on which the ratchet effect is normally reported carries no
   information about transmission.
3. **CUL-2/CUL-3**, which is where the depth is: the exact charged-resource
   separation margin `(t - r) phi a_n + (k - r) g`, the identification condition
   it yields, the unconditional positive that transmission is identified by a
   strictly positive margin `(r - t) phi a_n` exactly when transmission is
   cheaper per retained unit on a nonzero retained mass, and the proved boundary
   `t = r = k` at which even the full lifecycle resource vector fails to
   separate.

---

## 7. Repository parents pinned by this package

These are pinned by path and git blob sha in `MANIFEST_V1.json` and re-checked at
run time; parent drift is a red result.

| package | what it owns that this tranche reuses |
|---|---|
| `gmi-833-foundation-v1` | the realization contract `(X,x0,Q,U,Chi,rho)`, behavioral specification `B=(I,Acc)`, development law `Delta`, the lifecycle resource vector, evidence/maturity ladders, the `forall` / `forall_fin` domain-tag discipline |
| `gmi-833-axiom-core-v1` | the compact finite axiom core |
| `gmi-833-cognitive-reaudit-v1` (PR #919 / #917) | the re-audit pattern this package matches: external operational definition, exact threshold or extremal characterization, exhaustive finite census, hostile twin proving functional traces do not identify mechanism |
| `gmi-833-morphcap-v1` (#848) | capability as an external contract, ceilings, the observational-aliasing hostile |
| `gmi-833-global-uncertainty-v1` (#851) | abstention and non-identifiability semantics; the typed vocabulary in which this package abstains |
| `gmi-833-theory-baseline-v1` | frozen assertions, claim ceiling, forbidden promotions |

---

## 8. What is not claimed, in one place

No claim is made here about human or animal cognition, about any empirical
finding, about any architecture, module or anatomy, about any universal cognitive
law, about general optimal stopping or plan-search stopping, about general causal
discovery, or about learning any of the registered quantities from data. The
tranche is EV2 / M2: deductive theorems plus exact computer-assisted certificates
at bounded declared universes.
