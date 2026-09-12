# The GMI derivation of the machine-intelligence domains (V1, executed)

**What this document is.** The programme was asked for a theory that *explains and derives* every domain of machine
intelligence rather than listing them. This is that derivation, at the scope the microscopes actually execute. Every row
carries its claim level and the receipt that earned it. Where the derivation contradicts an earlier statement of this
programme, the earlier statement is marked falsified and replaced rather than quietly edited.

Claim levels: `PROVED_AT_SCOPE`, `PARENT_THEOREM_UNDER_ASSUMPTIONS`, `EMPIRICALLY_SUPPORTED_AT_TIER_X`,
`REGISTERED_FOR_EXPERIMENT`, `REDUCED_TO_PARENT`, `FALSIFIED_AND_REPLACED`, `OPEN_BLOCKING`, `OPEN_NONBLOCKING`,
`OUT_OF_SCOPE`.

---

## 1. What a domain is, stated so that it can be decided

A realization is `M = (Z, K, U, Γ, κ, ρ)` — developmental state, execution law, update law, morphogenesis, interface,
resource semantics. `M₁ ≼_B M₂` iff a compiler built from `M₂`'s carrier and law reproduces `M₁`'s **entire developmental
response** with lifecycle overhead bounded by a declared function of state size. A **domain** is a class of the symmetric
part of `≼_B`.

That relation is not one relation. `GMI-DA7` proves it is indexed by four declared parameters, and every executed
microscope fixes all four:

| parameter | meaning | fixed at |
|---|---|---|
| `A` | the primitive alphabet — typed kinds with signatures and charged costs (`morph.KINDS`) | 34 kinds |
| `d` | the structure-depth bound of the registered family | `d = 1` except where stated |
| `p` | the arithmetic instrument | 8-bit fixed point, `FRAC_BITS = 4` |
| `F` | the ecology family and intervention set the response is quantified over | 5 ecologies × 6 interventions |

Write `K(A, d, p, F)` for the resulting class set. **GMI-DA7** (`PROVED_AT_SCOPE`): it partitions the expressible
realizations; a candidate lies outside it only if it is not a bounded `A`-composition at `(d, p)` with responses separated
within `F`; and it is monotone in all four — enlarging `A`, `d` or `p` can only **add** classes, refining `F` can only
**split** them.

**This is the whole explanatory content.** "How many kingdoms of machine intelligence are there?" is not a question about
the history of the field. It is the question "how many carrier/law pairs does the alphabet admit, at this depth, this
precision and these demands?"

---

## 2. The derivation: domains are the state-type partition of the alphabet

Nodes of the IR carry class letters `S R T U V G H C D P`. The **state** kinds and the **update** kinds that can write
them generate the classes. Reading the type signatures off `morph.KINDS`:

| state type | update kinds that can write it | class | taxonomy name | occupancy at `(p = 8, q = 0.5)` | receipt |
|---|---|---|---|---|---|
| none | — | stateless transducer | — | occupied | `STAGE_B1_*` |
| `VEC` (`DENSE`) | `GRAD` only — **and `GRAD` requires a `TARGET`** | coefficient / function field | **D1** | occupied | `RV-377-021`, `RV-377-071` |
| `TAB` (`KVSTORE`, `TABLE`) | `INSERT`, `CLOSEDFORM` — **neither requires a target** | exemplar / indexed memory | **D2** | occupied | `RV-377-021`, `RV-377-044` |
| `VEC` read as a distribution | Bayes update | probabilistic | **D3** | **empty** — precision gate | `RV-377-029`, `031`, `045` |
| `PROG` | `SEARCH`, `PMUTATE` | symbolic program / deliberative search | **D4/D5** | occupied | `RV-377-025`, `058` |
| `VEC` under an iterated map | *none in `A`* | dynamical / controller | **D6** | **not a class** — see §3 | `RV-377-072`, `073` |
| population of `PROG` | `PMUTATE` | collective / population | **D7** | **empty** — reliability gate | `RV-377-040`, `041b` |
| `G`-class kinds | morphogenesis | morphogenetic | **D8** | occupied | `RV-377-038` |
| more than one dominant state kind | any | hybrid | **D9** | occupied | `RV-377-057`, `071` |

Three facts in that table are not decorations, and each was earned by an experiment that could have gone the other way.

* **Two of the nine domains are empty at the registered instrument settings.** D3 is shut out by 8-bit saturation and D7
  by a reliability index of `q = 0.5`. "Nine domains exist" is therefore false as an unqualified statement; seven are
  occupied and two are gated. Raise `p` and D3 should become non-empty; raise `q` and D7 should. Both are running.
* **D6 is not a class at all.** See §3.
* **The coefficient carrier cannot express an input-driven transition.** `GRAD` is the only update kind producing a `VEC`
  and it requires a target. So in this alphabet "recurrent" is a property of the **memory** carrier, not of the continuous
  one — the opposite of how the neural literature assigns it.

---

## 3. D6 derived away: the register theorem

`GMI-DA1` asserted that the nine taxonomy domains are exactly the classes the alphabet admits. The A axis was executed
against that assertion and it is **false in its enumeration half**.

**GMI-DA8 (register theorem, `PROVED_AT_SCOPE`).** Any carrier whose state is a single finite-precision value updated by
an input-driven transition `z ← g(z, x)` reading no target is exactly emulated by a **one-entry store under
read-modify-write**, `INSERT(tab, key, g(LOOKUP(tab, key), f(INPUT)))`. Every port is a registered kind, the graph is
acyclic, no target is read, and the overhead is constant.

Executed (`RV-377-072`, `RV-377-073`; 630 exact charged replays, 8 190 frontier cells):

| quantity | executed |
|---|---|
| bit-identical answers, iterated map vs register parent | **54 of 54** valid cells, 90 of 90 overall |
| declared description overhead | **exactly 4 bits**, constant in stream length |
| execution overhead ratio | exactly `c + k/T` per column (`6 + 0.5/T` in the worst) |
| frontier cells taken by the register parent | **0** |
| C2 column invariance | 108 groups, 0 violations |

So the alphabet admits **eight** carrier classes, not nine. D6 is the read-modify-write phase of D2. It entered the
taxonomy because the taxonomy was read off the literature rather than off the type system. Gap `DG-1` closes — not by
adding the primitive, but by showing the primitive adds no class. `GMI-DA1`'s enumeration half is
`FALSIFIED_AND_REPLACED`.

---

## 4. Why eleven candidate kingdoms reduced, as a theorem rather than eleven facts

| candidate | carrier | reduced to | how | receipt |
|---|---|---|---|---|
| DC1 hyperdimensional / VSA | superposed hypervector | D2 | lazy phase (`GMI-DA2`), exact equality | `RV-377-044` |
| DC3 energy landscape | coupling field | D2 | lossy eager phase, dominated (`GMI-DA4`) | `RV-377-045` |
| DC9 phase / oscillatory | phase vector | D2 | DC1 is its `Q = 2` case | worker lane |
| DC2 self-organizing field | field state | D1/D2 | dominated | worker lane |
| DC7 quantum cognition | amplitude vector | D3/D2 | exact equality | worker lane |
| N3 relational / sheaf | section over a cover | D2 | exact equality | worker lane |
| N10 event-causal partial order | partial order | D2 | exact equality | worker lane |
| N8 constructive / autocatalytic | reaction set | D4/D5 | exact equality | worker lane |
| N11 impossibility certificate | obstruction witness | D4/D5 | collapses against a **parent-maximal** opponent | worker lane |
| F4 interventional quotient learner | intervention policy | D4/D5 | ties the standard utility where the distinction is vacuous | `RV-377-063` |
| F6 self-compiling developmental intelligence | compiled authority | D2 | exact equality; bit-identical to every parent | `RV-377-064` |

Each was implemented as a type-checking genotype over `A` at fixed `d` and `p = 8` and adjudicated on `F`. By `GMI-DA7`
part 2 its reduction was **forced before it was run**. The receipts therefore do not measure whether these are kingdoms;
they measure *which* parent each compiles into and at what cost, which is the useful content and is what they report.

Two things the run of eleven taught that the theorem did not predict:

* **Bounded reduction is only meaningful against a parent-maximal opponent** (N11). Against a weak parent almost anything
  looks new. This is now protocol rule 19, and it is what produced the register parent of §3.
* **Eight of the eleven were certified by exact developmental equality.** Under `GMI-DA7` part 3 that is not evidence the
  carriers are the same machine; it is evidence that `F` never asked them to differ. `RV-377-070` is testing exactly that.

---

## 5. The reachability half: are the derived domains findable from primitives?

A derivation that no search can reach is a taxonomy, not a biology. Executed:

| question | result | receipt |
|---|---|---|
| does neutral search over the typed IR recover known mechanism classes? | yes — retrieval memory, indexed memory and symbolic search to admissibility in 6 000 evaluations; the coefficient carrier as well on one seed (0.9583) | `RV-377-058` |
| does neutral search over the expression-tree grammar cross admissibility? | yes — 0.8809 and 0.8796 at 10⁶ evaluations against a sound baseline of 0.7346 and a standing plateau of 0.7418–0.7798 | `RV-377-057` |
| what crossed the plateau? | the **archive** (0.7346 → 0.8437 without the duplication operator); the duplication operator supplies the last 0.037, which is the part that crosses θ | `RV-377-057` clause 6 |
| do the recovered machines *contain* a known form? | yes — **24 of 24** atrophy to a two-rule error-driven coefficient learner, `c0 ← ADD(out, MUL(kh, e))` plus a target-tracking rule, with **every** store write deleted; median 65 nodes against the planted learner's 47 | `RV-377-071` |

The standing negative of `RV-377-023`/`028` is `FALSIFIED_AND_REPLACED`: it was a search-and-archive failure, not a budget
failure. Gap `G6` closes at the admissibility level and `G6b` at the form level.

**The lesson that cost the most to learn:** admissibility recovery is not form recovery, but it contains it. A carrier
descriptor computed on a raw genotype is not a measurement of the carrier — the winners were 55–68 % introns and the
descriptor was reading the introns. Recovery receipts now require a charged atrophy stage (protocol rule 20).

---

## 6. What the derivation does **not** yet decide

| open item | status | closure experiment |
|---|---|---|
| `d` axis — is there a depth at which the binding carrier resists a parent-maximal opponent at every reuse horizon? | **EXECUTED, no** to depth 6; and `GMI-DA3` is falsified for the XOR code, surviving only for a permutation-protected one | `RV-377-065` |
| `p` axis — does D3 occupy cells above a precision threshold that no 8-bit carrier occupies? | **EXECUTED, then REFUTED**: an 8-bit log-domain posterior is admissible where ten linear rows are not | `RV-377-066`, `RV-377-075` |
| `F` axis — do the exact-equality certificates survive demands `F` never posed? | **EXECUTED**: 10 of 14 split, 3 survive the known gates, no reduction overturned but every one now qualified by a declared capacity bound | `RV-377-070` |
| stage B4 — does neutral search produce an unknown form? | **EXECUTED, no**: 0 of 7 novel by response, 5 of 7 novel structurally, one recovered machine identical to a parent node for node | `RV-377-077` |
| L8-ADMISSIBILITY — predicting which carriers are admissible in an unseen ecology | closed for retrieval carriers (exact closed forms on 17/17 and 16/16), open for optimization carriers, which are trajectory properties and initialization-asymmetric by 0.07–0.15 | `RV-377-062`; residual `OPEN_NONBLOCKING` |
| lower bounds rather than occupancy | exhaustive census exact only to size 4 | gap `G8`, running |
| real-system validation of any law | none | Codex E3/E4; `OUT_OF_SCOPE` for this lane |

---

## 7. How to falsify this derivation

1. Exhibit a carrier that type-checks in the IR, is not a bounded composition over `A` at the declared `(d, p)`, and
   requires no new primitive kind. That refutes `GMI-DA7` part 2.
2. Exhibit two carriers in the same class of `K(A, d, p, F)` whose frontier occupancy differs on some ecology in `F`.
   That refutes part 1.
3. Exhibit an ecology in `F` on which the one-entry register and the iterated map differ in a single served answer. That
   refutes `GMI-DA8` and reopens D6.
4. Exhibit a refinement of `F` that **merges** two classes. That refutes part 3, and with it the whole monotonicity
   argument.
5. Recover, by neutral search over the IR, an admissible machine whose atrophied form matches none of the eight carrier
   classes. That is the positive discovery the programme is looking for, and it is what stages B4 and later exist to try.
