# Lane #200 terminal record — verified-trace / warranted-lifecycle learnability

**Terminal: `INTERFACE_HIERARCHY_ONLY`.**
**Residual `STRICT_WARRANTED_LIFECYCLE_RESIDUAL`: `NOT_EARNED__OBSTRUCTION_NAMED`.**

Date: 2026-09-04
Umbrella: ORION-V2 #194 · Execution master: #197 · Lane: #200 · P0: #221 · Reviews (unreturned): #199, #245
Exact checker: `reference/ocm_lane200_decomposition_exact.py` · Tests: `tests/unit/test_ocm_lane200_decomposition_exact.py`

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** This record drives the lane to a terminal by parent
subtraction. Every object below is either shown to be owned by a named parent (a collapse, which is
a successful outcome) or given a precisely stated obstruction. Nothing here is a review: #199 and
#245 remain unreturned and were not simulated.

## 0. Substrate-form restatement (operator directive, #194 comment 5539487737, 2026-09-04)

The directive makes the object of study *substrate + constraints*, not an architecture. In that
form this lane's question is **(a) channel sufficiency**: which observation interface a minimal
substrate must expose so that a procedure can be acquired *with warrant* from each of the five
channels — instruction, demonstration, interaction, experimentation, feedback. The registered
rungs are those channels' observation maps: feedback = endpoint-only `I0`; demonstration = raw
trace `I1`; instruction = a positive certificate `I2`; experimentation with a closure certificate
= `I3`; interaction = query access to any rung. Theorems A–E below therefore read as a *channel
calibration of the substrate*: each rung's gain is the fibre criterion applied to one more
observation, and each is owned by the parent named on its row. Nothing here is an architecture
claim, and the terminal is unchanged by the restatement — it was already architecture-neutral.
The cross-lane synthesis is in `OCM_DIRECTIVE_RESCOPE_V1.md`.

## 1. What the lane asked

> Locally verifiable proof-carrying traces plus scope/epoch-bound warrant yield a strict
> learnability/query/description-complexity frontier for a natural compositional class after
> counting all resources.

Candidate objects: the strict interface hierarchy `I0 < I1 < I2 < I3`; Warranted Lifecycle Learning
and Warrant Lift; open-world positive-support impossibility (WLL-5); retain/retract NP/coNP
asymmetry (WLL-6); the natural classes WPL V1/V2 and WGPL; the lifecycle-identifiability bound LI-1.

## 2. Theorem A — Warrant Lift is conditional Hartley entropy (collapse)

Let `Omega` be finite, `B: Omega -> Bset` current behaviour, `L: Omega -> Lset` the lifecycle
profile with `L` refining `B`. `OCM_WARRANT_LIFT_THEORY_V1.md` defines
`Lambda_inf(L|B) = ceil(log2 max_b |{L(w): B(w)=b}|)`.

**Theorem A.** `Lambda_inf(L|B)` is the worst-case conditional Hartley (Rényi order-0) entropy
`max_b H_0(L | B=b)`, rounded up; equivalently the deterministic one-way communication complexity of
`L` when the receiver already holds `B`. WL-1 to WL-6 are the standard properties of that quantity.

*Proof.* `H_0(L|B=b) = log2 |{L(w): B(w)=b}|` by definition of Hartley entropy of the conditional
range. One-way communication: the sender (who holds `w`, hence `B(w)`) transmits the index of `L(w)`
inside the fibre of `B(w)`, which needs `ceil(log2 max_b m_b)` bits and no fewer, since the largest
fibre carries `m_b` distinct values that must receive distinct messages. WL-1 (zero criterion) is
"`B` and `L` induce the same partition", i.e. `B` is a sufficient statistic for `L`. WL-2 is the
communication statement just proved. WL-3 (monotone under refinement of `L`), WL-4 (additive under
Cartesian product) and WL-5 (subadditive, strict when a latent coordinate is shared) are the
monotonicity, additivity and subadditivity of `H_0`. WL-6 (blind spot) is the existence, for each
`k`, of a fibre of size `2^k`. ∎

*Parents.* Hartley 1928; Rényi 1961 (order-0 entropy); Blackwell 1953 (sufficiency as partition
equality); Yao 1979 and Kushilevitz–Nisan, *Communication Complexity* (one-way deterministic
complexity = log of the number of distinct rows). Disposition: `PARENT_OWNED`; "Warrant Lift" is
notation for `H_0(L|B)` with a lifecycle reading. This settles the #201 checkbox "compare with
Warrant Lift, do not double-claim": both lanes' bounds are instances of the same quantity (§7 of the
#201 record).

## 3. Theorem B — the fibre criterion owns every rung of the hierarchy (collapse)

**Fibre criterion.** For an observation map `O` and a target coordinate `c: Omega -> {0,1}`, a
zero-error rule may answer `c` at observation `o` iff `c` is constant on `O^{-1}(o)`; otherwise it
must query, hold more certified state, or abstain. (Stated in `OCM_WLL_STRICT_INTERFACE_HIERARCHY_V1.md` §2.)

*Parents.* Version-space agreement region (Mitchell 1982); KWIK learning (Li, Littman, Walsh 2008:
predict only when the version space agrees, else say "I don't know"); Blackwell sufficiency.

Each strict rung of WLL-8 is the fibre criterion applied to one extra observation:

| Rung | What refines the partition | Strongest parent |
|---|---|---|
| `I0 < I1` | the raw trace exposes the module vector `theta` | computational-trace identification, Peng–Saberi–Velegkas ICLR 2026 (`P-TRACE-ICLR-2026`) |
| `I1 < I2` | an observed positive certificate fixes one support bit | proof-carrying code (Necula 1997): a checked certificate is a positive fact |
| `I2 < I3` | closure information decides absent support | closed-world assumption, Reiter 1978; open-world reasoning: absence of a positive is not a negative |
| WLL-5 | two worlds `P` and `P ∪ {T}` share the observation | the CWA/OWA two-world indistinguishability, same parent |
| WLL-6 / RCL-7 | RETAIN ∈ NP, RETRACT ∈ coNP; both cheap ⇒ NP = coNP | standard (Cook 1971; Stockmeyer 1976) |

The hierarchy is **true and strict on the registered 256-world family** (checker green, denominator
pinned since #254). It survives as an interface calibration. No rung is new.

## 4. Theorem C — the closure dichotomy (definitional obstruction)

Let `c` be a retraction coordinate. By the fibre criterion, an exact RETRACT at `o` requires `c ≡
RETRACT` on `O^{-1}(o)`. Whatever part of the transcript makes that constancy hold is, by
definition, a closure certificate for `c` at `o`. Therefore in the zero-error regime exactly two
cases exist:

1. **Closure present.** The warrant object for `c` is *given* in the transcript. Its maintenance
   under revocation is provenance/TMS/self-adjusting computation (RCL-F05); its static shape is a
   complete reason / prime-implicant family (`04_POSTFREEZE_PARENT_DELTA…` §1); its compiled form is
   knowledge compilation (§3 there). Acquiring it by queries is exact learning of a monotone DNF /
   hidden hypergraph from liveness queries (Abasi–Bshouty–Mazzawi 2014, `P-MDNF-2014`); for the
   parity classes it is `N` independent coordinate bits (INDEX).
2. **Closure absent.** The learner must query or abstain; the count is LI-1 / WB-3
   (`min(C,B) + Q + a >= log2 M`), a cardinality bound (`P-UNLEARN-SPACE-2025` owns the generic
   memory-for-future-deletion phenomenon; the counting step is elementary).

There is no third regime in which the warrant is "learned but not given" *and* exact. The
bounded-error regime is Fano/INDEX (WGPL-3, parent-owned); the computational regime is
WLL-6 and knowledge compilation (parent-owned). ∎

## 5. Theorem D — rectangularity ⇔ oracle blindness; direct-product collapse

Let `L(w) = (B(w), Z(w))` with `Z` the hidden warrant profile (this is the registered lifecycle
target in WPL V1, WPL V2 and WGPL). A *current-function oracle* answers any query whose answer is a
function of `B(w)`. Call the class **rectangular** when `{(B(w), Z(w)) : w in Omega} = B(Omega) x
Z(Omega)`. Call it **blind** when for every `b`, `{Z(w) : B(w) = b} = Z(Omega)` (WB-1's hypothesis).

**Theorem D.**
(i) Blind ⇔ rectangular.
(ii) If rectangular: `Lambda_inf(L|B) = log2 |Z(Omega)|`; with a `B`-oracle and a `Z`-oracle the
deterministic exact query complexity satisfies `log2|B(Omega)| + log2|Z(Omega)| <= Q(Omega) <=
Q_B + Q_Z`, and when both factors are full binary cubes with bit oracles, `Q(Omega) = p + N`
exactly, attained by running the two factor learners one after the other.
(iii) If not rectangular, the complete `B`-transcript excludes some warrant value, so the
current-function oracle carries warrant information and blindness fails.

*Proof.* (i) Both sides say every `z` occurs with every `b`. (ii) Under rectangularity the fibre of
each `b` is a copy of `Z(Omega)`, giving the lift; the lower bound is the decision-tree count on
`|Omega| = |B||Z|` leaves; the upper bound composes the two learners, whose queries are answered by
their own oracles independently of the other factor. For full cubes `Q_B = p`, `Q_Z = N` by the
same count. (iii) A missing pair `(b, z)` means that after `b` is revealed the conditional class is
a proper subset of `Z(Omega)`. ∎

**Consequence.** WB-1 blindness — the property the programme used as the signature of its residual —
holds exactly when the lifecycle problem is the Cartesian product of two parent problems with
additive complexity and no interaction term. WPL-2 (`p(h+1) = p + p·h`) and WGPL's `n + binom(n,2)`
*are* this decomposition. The exact checker verifies rectangularity, blindness, `H_0` additivity,
the registered query counts and the product learner on all three committed classes (2,048 worlds),
and requires three planted coupled classes (648 worlds) to fail rectangularity and leak warrant bits
through the current-function oracle; four mutation controls are asserted applied and detected.

## 6. Theorem E — Revocation-Shattering Dimension is a fibre-wise VC dimension (demotion)

For profile class `Phi`, transcript map `tau`, revocations `Gamma`, `RSD(Phi, tau, Gamma)` is the
largest `k` such that some transcript value `t` and `R_1..R_k in Gamma` have every `b in {0,1}^k`
realised by some `J` with `tau(J) = t`. Writing `Live_J : Gamma -> {0,1}`, this says the set
`{R_1..R_k}` is shattered by the class `Lcal_t = {Live_J : tau(J) = t}`. Hence

`RSD(Phi, tau, Gamma) = max_t VCdim(Lcal_t restricted to Gamma)`.

The checker `revocation_complete_learning/rcl_checks_v1.py::verify_rsd_is_fibrewise_vc` computes
the VC dimension of the liveness class on the fixed-certificate fibre at `n = 4` by brute force and
matches the recorded `RSD = 5`. RCL-R33/R34 of #245 are answered from the authoring side by
contraction: RSD is notation, `RCL-F11 -> PARENT_OWNED (fibre-wise VC dimension)`.

## 7. Parent table for every candidate object of this lane

| Object | Strongest parent | Disposition |
|---|---|---|
| Warrant Lift, WL-1..6 | conditional Hartley entropy / one-way communication / sufficiency | `PARENT_OWNED` (Thm A) |
| fibre criterion, WLL-8 rungs | version space, KWIK, trace learning, PCC, CWA | `PARENT_OWNED`; hierarchy kept as calibration (Thm B) |
| WLL-1 strict refinement | future equivalence / Myhill–Nerode-style refinement | `PARENT_OWNED` |
| WLL-3 unlearning ≠ warrant | two-observable incomparability, elementary | calibration |
| WLL-4 scope intersection | trust logics / refinement types (intersection of scopes) | `PARENT_OWNED` |
| WLL-5, WLL-6, RCL-7 | CWA/OWA; NP/coNP | `PARENT_OWNED` (Thm B) |
| LI-1, WB-2, WB-3, WGPL-3 | decision-tree counting; Fano; INDEX | `PARENT_OWNED` |
| WPL V1/V2, WGPL classes | parity learning × INDEX; graph connectivity × INDEX | `DIRECT_PRODUCT_OF_PARENT_PROBLEMS` (Thm D) |
| RSD | fibre-wise VC dimension | `NOTATION` (Thm E) |
| static CWC, storage/query frontier | complete reasons; knowledge compilation | `PARENT_OWNED` (already contracted in RCL V1 delta) |

## 8. The obstruction, stated precisely

A residual of the kind the lane conjectured would need a natural class that is **not rectangular**
(so Theorem D gives no product decomposition) and yet exhibits a strict interface separation not
attributable to either factor alone, with a computational (not cardinality) lower bound at equal
information. Non-rectangularity forfeits blindness (Thm D iii), after which the problem is ordinary
exact learning of a joint concept with two query types (Angluin 1988). No registered class is
non-rectangular; constructing one would be a new object, not a residual of the present ones.
Recorded as `STRICT_WARRANTED_LIFECYCLE_RESIDUAL = NOT_EARNED__OBSTRUCTION_NAMED`.

## 9. Lane checklist disposition

| #200 task | Disposition |
|---|---|
| reconstruct trace / query / program / automata / process-supervision / privileged-information parents | named per rung (§3, §7); primary full-text reconstruction remains a review obligation (#199/#245) |
| reconstruct future-equivalence, PCC, provenance/TMS, knowledge compilation, unlearning parents | named (§3, §4, §7) |
| freeze interfaces, family, verifier, revocation model, information accounting | frozen in the V1 artifacts; unchanged here |
| endpoint-only lower bound | LI-1 / I0 row; cardinality, `PARENT_OWNED` |
| raw-trace upper bound | I1 row; trace-learning parent |
| positive-only boundary + closure-certified upper bound on a non-direct-bit family | WLL-5 / I3 on WPL, WGPL; both `PARENT_OWNED` via Thm C, D |
| count all resources | LI-1 vector; no new resource found that changes a terminal |
| laundering controls | verifier-independence remains PCC's contract; no new theorem |
| partial / corrupt / self-authored / stale traces | not a residual: each is a fibre-criterion instance (Thm C) |
| recurrent-Transformer comparison | architecture-neutral by every V1 artifact; see #202 record |
| mechanize finite core theorem | `CANNOT_CHECK` here: no proof-assistant toolchain provisioned (#203 record) |
| record terminal | `INTERFACE_HIERARCHY_ONLY` |

## 10. Non-consequences and reopen conditions

Supported: Theorems A–E as stated, each elementary and each a contraction toward a named parent;
the hierarchy remains a correct calibration.

Not supported: literature priority, novelty, post-Transformer architecture, natural-language
competence, parameter efficiency, quantum advantage, publication readiness. No checkbox in #197 is
closed by this file (OPS-012); no review terminal for #199/#245 is issued or simulated.

Reopens if: a non-rectangular natural class with a strict equal-information separation and a
non-cardinality lower bound is constructed and survives Thm D(iii); or an independent review finds
a defect in Theorems A–E.
