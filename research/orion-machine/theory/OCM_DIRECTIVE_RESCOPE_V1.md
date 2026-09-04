# OCM programme re-scoped under the operator directive — substrate and constraints

Date: 2026-09-04 · Umbrella: ORION-V2 #194 · Execution master: #197 · P0: #221 · Reviews (unreturned): #199, #245
Directive of record: #194, comment `5539487737` (quoted verbatim there; not restated in full here).

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** This document re-derives the theory programme under
the directive and records where each lane terminates. It closes no checkbox (OPS-012), issues no
review terminal, and grants no architecture, language, quantum, publication or priority authority.

## 1. What the directive fixes

> OCM should be a minimal self-extending machine that learns how to accomplish tasks, not merely
> approximates outputs from large-scale exposure. […] MNI/MNSI should therefore not be predefined
> target architectures. OCM should provide the minimal substrate and constraints, then discover the
> forms of intelligence best suited to its tasks and environments.

Three consequences, each operative below:

1. **The object of study is substrate + constraints.** A theorem "the OCM architecture achieves X"
   is mis-scoped. The well-posed questions are: under what minimal substrate can a machine
   **(a)** acquire a procedure *with warrant* from each of the five channels — instruction,
   demonstration, interaction, experimentation, feedback; **(b)** compose acquired procedures into
   skills with warrant preserved; **(c)** revise its own representation, learning strategy and
   architecture without losing exact authority over what it already knows.
2. **RCL is the authority-preservation constraint on (c)**, not the programme. It stays the live
   residual candidate only in the sense that (c) is where a non-parent-owned theorem could still
   live; §4 says why none does yet.
3. **"Not merely approximates outputs from large-scale exposure" is a falsifiable separation
   claim** and is `NOT_ESTABLISHED` until a registered, budget- and information-matched test exists
   and is passed. Its design audit is `OCM_SEPARATION_TEST_DESIGN_V1.md`; the audit failed
   reachability and comparator matching, so no test is frozen.

The substrate itself is `reference/ocm_reference_semantics.py` with its record
`OCM_OPERATIONAL_SEMANTICS_V1.md` (lane #203).

## 2. The theory lanes in substrate-and-constraint form

| lane | chartered question | substrate-form question | terminal reached | strongest parent (owner) | record |
|---|---|---|---|---|---|
| #200 | verified traces + warrant give a strict learnability frontier | **(a) channel sufficiency:** which observation each channel must expose so a procedure is acquired *with warrant* | `INTERFACE_HIERARCHY_ONLY`; residual `NOT_EARNED__OBSTRUCTION_NAMED` | version space / KWIK (fibre criterion); computational-trace identification (Peng–Saberi–Velegkas 2026); PCC; closed-world assumption (Reiter 1978); Warrant Lift = conditional Hartley entropy | `OCM_LANE_200_TERMINAL_V1.md` |
| #201 | authority-indexed lattice gives a strict state advantage with sound reopening | **(c), representation half:** the coarsest representation preserving exact authority, and the accounting of any saving | `PARENT_SUFFICIENT` (conservation L4 refutes the matched-resource advantage) | minimal sufficient statistic / Blackwell 1953; partition lattice; CEGAR (Clarke et al. 2000); cell-probe trade-offs (Yao 1981) | `OCM_LANE_201_TERMINAL_V1.md` |
| #202 | whole-system "fewer neurons" frontier | **cost of the substrate:** `C_core*(F; t)` and the interpreter constant the substrate itself adds | `TRADEOFF_FRONTIER_ONLY`; comparator equivalence `CANNOT_CHECK` | time-bounded Kolmogorov complexity; invariance theorem (Kolmogorov 1965) | `OCM_LANE_202_TERMINAL_V1.md` |
| #203 | formal OCM semantics and resource contract | **the substrate:** the smallest transition system in which (a)(b)(c) are statable, with its constraints checked | `PARENT_OBJECT_ADOPTED`; freeze and proof-assistant `CANNOT_CHECK` | ATMS (de Kleer 1986) — the RCL profile is an ATMS label; PCC (Necula 1997); TMS (Doyle 1979) | `OCM_OPERATIONAL_SEMANTICS_V1.md` |
| #204 | bounded language/task bridge | **dissolves** into an emergent-form question: language is one *encoding* of the instruction channel; the substrate fixes only what warrant an instruction can carry | `FORMAL_ONLY` (precondition unmet: no surviving theorem candidate) | — (no bridge experiment for a parent to be sufficient for) | `OCM_LANES_204_205_PRECONDITION_RECORD_V1.md` |
| #205 | conditional quantum operator | **dissolves**: no classical operator with a stated access model exists to lift | `NO_ELIGIBLE_OPERATOR` | — | same |

The chartered residual names — `STRICT_WARRANTED_LIFECYCLE_RESIDUAL`, `CERTIFIED_REPRESENTATION_RESIDUAL`,
`STRICT_CORE_RESOURCE_RESIDUAL` — are each `NOT_EARNED`. Under the directive that is the expected
outcome, not a failure: the lanes were asking architecture questions, and the directive says the
architecture is what the substrate must *discover*.

## 3. Parent subtraction for the directive's own capabilities

Absorb, never avoid. For each capability the directive names, the strongest published parent, what
it owns, what it lacks relative to the substrate's constraints, and the disposition. `PARENT_OWNED`
is a successful outcome.

| capability | strongest parent | what it owns | what it lacks vs the substrate | disposition |
|---|---|---|---|---|
| (a) instruction → procedure | program synthesis from specification; library learning — DreamCoder (Ellis et al., PLDI 2021), LILO (Grand et al. 2023) | acquiring procedures from task specs; compressing them into a reusable library (which is also (b)) | no warrant record: a library primitive carries no provenance of the evidence that justified it, so nothing can be revoked; abstraction is chosen by description length, not by authority | `PARENT_OWNED` for acquisition and composition-as-compression; the warrant field the substrate adds is itself ATMS-owned (row (c)) |
| (a) demonstration → procedure | programming by demonstration via version-space algebra (Lau, Wolfman, Domingos, Weld 2003); learning from demonstration / IRL (Abbeel & Ng 2004; Argall et al. 2009) | the trace channel; the version space **is** the fibre criterion of lane #200 | warrant persistence and revocation | `PARENT_OWNED` |
| (a) interaction → procedure | query learning (Angluin 1987 L\*, 1988); KWIK (Li, Littman, Walsh 2008) for principled abstention | membership/equivalence queries; "I don't know" when the version space disagrees | revocation of what was learned | `PARENT_OWNED`; the substrate's three-valued liveness is KWIK's abstention |
| (a) experimentation → procedure | active causal discovery / experimental design (Eberhardt 2007; Tong & Koller 2001) | closure by intervention: an experiment can certify *absence* (the `I3` rung; the substrate's only `complete` channel) | warrant persistence | `PARENT_OWNED` |
| (a) feedback → procedure | RL from feedback (Christiano et al. 2017); bandits | the endpoint channel | **cannot warrant at all**: feedback fixes behaviour only (`I0`); every liveness query abstains (semantics §1) — a theorem of the substrate, and the closed-world parent's | `PARENT_OWNED`; the substrate's contribution is to *refuse* warrant here |
| (b) composition with preserved warrant | options (Sutton, Precup, Singh 1999); skill libraries (Voyager, Wang et al. 2023); DreamCoder library | composing procedures into skills | warrant of the composite | S2: composite profile = minimal unions, liveness conjunctive, scope intersection — ATMS label combination. `PARENT_OWNED` |
| (c) representation revision | Blackwell sufficiency; lane #201 L1/L4/L5; Theorem S4 | coarsest authority-preserving representation = partition generated by the admitted revocations; saving is relocation; reopening = CEGAR | — | `PARENT_OWNED` |
| (c) strategy revision | meta-learning (Schmidhuber 1987; Hochreiter et al. 2001; MAML, Finn et al. 2017) | changing the learner | no obligation on already-acquired knowledge | S5 (policy swap preserves liveness signatures) is a TMS in-list monotonicity fact. `PARENT_OWNED` |
| (c) architecture revision | NAS (Zoph & Le 2017; Elsken et al. 2019); **Gödel machine** (Schmidhuber 2003, 2007) | self-rewrite gated by a checker-verified proof — exactly the substrate's "revise only with a certificate" | the Gödel machine's proof obligation is *expected-utility improvement under fixed axioms*; the RCL obligation is *preservation of the revocation signature of existing knowledge*. Different obligation, but expressible as one more proof obligation in the same system, and verifying it for explicit antichain stores is RCL-0 (trivial); for implicit/compiled stores it is the RCL-7/8 barrier | **`PARENT_PRODUCT_SUFFICIENT` for the constraint as stated** (Gödel machine × ATMS). What is *not* owned by any parent is a theorem that a self-revising learner must pay more than that product at equal information — and none exists, for the reason in §4 |

## 4. What is open, and why it is open

- **The joint residual (RCL-B/RCL-C).** Every registered natural class is rectangular (lane #200
  Thm D): behaviour × warrant decomposes into two parent problems with additive cost, and
  "blindness" is exactly that decomposition. A residual requires a *non-rectangular* natural class
  with an equal-information, non-cardinality separation — a new object, not a consequence of the
  present ones. Recorded as an obstruction, not as a negative: nothing shows such a class cannot
  exist. Under the directive this is the one place a theorem specific to constraint (c) could live.
- **The separation claim.** `NOT_ESTABLISHED`; test not freezable at present
  (`OCM_SEPARATION_TEST_DESIGN_V1.md`, audit `FAILED_REACHABILITY_AND_COMPARATOR_MATCHING`).
- **Independent review.** #199 and #245 unreturned; `NOT_OBTAINED__DISCLOSED_LIMITATION`. The
  authoring-side audit of the RCL pack against #245's gate is
  `revocation_complete_learning/RCL_KILL_GATE_AUDIT_V1.md`; it is not the reviewer's terminal.
- **Mechanization.** `CANNOT_CHECK` in every lane: no proof-assistant toolchain provisioned.

## 5. Terminal block (replaces the pre-directive block in `README.md`)

```text
OBJECT_OF_STUDY                     = SUBSTRATE_AND_CONSTRAINTS (directive 2026-09-04); MNI/MNSI emergent, not specified
SUBSTRATE_SEMANTICS (#203)          = PARENT_OBJECT_ADOPTED (ATMS label + PCC gate + resource vector); FREEZE = CANNOT_CHECK (audit unreturned)
CHANNEL_SUFFICIENCY (a) (#200)      = INTERFACE_HIERARCHY_ONLY; every rung PARENT_OWNED; residual NOT_EARNED__OBSTRUCTION_NAMED
COMPOSITION_WITH_WARRANT (b)        = PARENT_OWNED (ATMS label combination; S2)
SELF_REVISION_AUTHORITY (c) (#201)  = PARENT_SUFFICIENT (Blackwell/CEGAR/L4; Theorem S4); Godel machine x ATMS owns the constraint
REVOCATION_COMPLETE_LEARNING        = CONSTRAINT_ON_(c); elementary pack = CALIBRATION; RCL-C = OPEN_NOT_PROVED__NO_REGISTERED_CLASS_QUALIFIES
SUBSTRATE_COST (#202)               = TRADEOFF_FRONTIER_ONLY; comparator equivalence CANNOT_CHECK
LANGUAGE_BRIDGE (#204)              = FORMAL_ONLY (dissolved into channel encoding)
QUANTUM_OPERATOR (#205)             = NO_ELIGIBLE_OPERATOR (dissolved)
SEPARATION_CLAIM (procedure-learner vs large-exposure approximator) = NOT_ESTABLISHED; test NOT_FROZEN (audit failed)
EXTERNAL_NOVELTY                    = NOT_ESTABLISHED
INDEPENDENT_REVIEW (#199, #245)     = NOT_OBTAINED__DISCLOSED_LIMITATION
MECHANIZATION                       = CANNOT_CHECK (no toolchain)
```

## 6. Non-consequences and reopen conditions

No statement here concerns English, frontier LLMs, parameter efficiency, post-Transformer
architecture, quantum advantage or publication. `RCL_FAILURE_AND_PARENT_COLLAPSE_LEDGER_V0.md`
keeps `DRIFT_RECORDED_NOT_BLESSED`; #199's `base_sha` is not moved. The pre-directive lane records
are retained unedited except for a `§0` restatement each.

Reopens if: a non-rectangular natural class is constructed and survives lane #200 Thm D(iii); a
matched comparator manifest is registered for #202; an independent review returns a terminal on
#199 or #245; or the separation-test audit is passed by a redesigned test.
