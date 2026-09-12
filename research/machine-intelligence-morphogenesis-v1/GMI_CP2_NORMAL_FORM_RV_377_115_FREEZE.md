# RV-377-115 — FREEZE: CP2, the representation / normal-form theorem

Frozen BEFORE the run. Outcomes appended only.

## What CP2 actually requires

The critical path asks for a representation/normal-form theorem *"so known-form results
become domain-wide results"*. That lift is valid only if the normal form **characterises**
the semantic class — i.e. only if

> two genotypes share a normal form **if and only if** they are observationally equivalent.

The forward direction (same normal form ⇒ same behaviour) is **soundness**, and it is what
lets a result proved on a representative transfer to the class. The reverse direction (same
behaviour ⇒ same normal form) is **completeness**, and it is what makes the class
*identifiable* from the representative — without it, a known-form result covers its own
normal-form class and says nothing about the rest of the behavioural class.

`morph.canonical` already supplies an isomorphism-invariant serialization, so structural
identity modulo node renaming is solved and is not the open part.

## The construction under test

```
prune(g)        drop every node that cannot reach OUTPUT by backward reachability,
                retaining the structural boundary INPUT / OUTPUT / TARGET
normal_form(g)  = morph.canonical(prune(g))
observable(g)   = response_signature over ALL 6 registered ecologies
                  x ALL 6 registered interventions  (36 developments)
```

`observable` is taken at the finest resolution the corpus supports. Measured cost: **0.16 s
per genotype** for all 36 developments.

Sample: **600 genotypes**, produced by applying `k ∈ 0..12` random grammar operators to
seeded genotypes, so that dead sub-graphs and structural variety actually occur.

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| W1 | **`prune` is SOUND** — `observable(g) == observable(prune(g))` on 100% of the sample. | any genotype whose response changes under pruning |
| W2 | **`prune` is idempotent** — `normal_form(prune(g)) == normal_form(g)` on 100%. | any counterexample |
| W3 | **The normal form is NOT complete** — there exist genotypes with identical observable signatures across all 36 cells but different normal forms. | zero such pairs |
| W4 | **The semantic quotient is much coarser than the structural one** — distinct observable signatures < 50% of distinct normal forms. | ≥ 50% |

**W1 is a genuine risk, not a formality.** `response_signature` excludes ρ_M, so a pruned
node's *cost* cannot show up — but the VM carries shared machine state (`M.cells`,
`M.stores`). A node with no edge path into OUTPUT could still write to a store that OUTPUT
reads, in which case backward edge-reachability is the wrong reduction and W1 fails. If it
fails, `prune` is not a semantics-preserving reduction and CP2 needs a different one.

**W3 is the prediction that decides CP2.** If the normal form is sound but incomplete —
which is what I expect, since distinct programs routinely compute the same function — then

> **known-form results do NOT automatically become domain-wide results by this route.**

That is a negative for the critical path as stated, and it is the outcome being tested for
rather than around. The honest consequence would be that CP2's goal needs either a
semantic normal form (decidable equivalence, which for a Turing-complete IR it is not) or
an explicit restriction to a fragment where equivalence *is* decidable.

If W3 is falsified — if equal behaviour always implies equal normal form on this sample —
that is a real and reportable positive, and it would make the CP2 lift available at
registered scope.

---

# RV-377-115 — ADJUDICATION (appended; nothing frozen above was edited)

600 typechecked genotypes, 36 developments each (6 registered ecologies × 6 registered
interventions), 244.9 s.

## Results

```
W1 prune SOUND      : 594/600  -> FALSIFIED
W2 prune IDEMPOTENT : 600/600  -> CONFIRMED

W3 distinct observable signatures                 : 17
   signatures realized by >1 normal form          : 12
   worst signature realized by                    : 183 distinct normal forms
   normal form NOT complete                       -> CONFIRMED

W4 distinct normal forms 266 | distinct signatures 17 | ratio 0.0639  -> CONFIRMED
```

| id | prediction | outcome |
|----|-----------|---------|
| W1 | `prune` is sound on 100% | **FALSIFIED** — 594/600; **six counterexamples** |
| W2 | `prune` is idempotent on 100% | **CONFIRMED** — 600/600 |
| W3 | the normal form is NOT complete | **CONFIRMED** |
| W4 | signatures < 50% of normal forms | **CONFIRMED** — 6.39% |

## W1 failed exactly where the freeze said it might

The freeze flagged this as "a genuine risk, not a formality": `response_signature` excludes
ρ_M, so a pruned node's *cost* cannot show, but the VM carries shared machine state
(`M.cells`, `M.stores`), so a node with no edge path into OUTPUT can still write to a store
that OUTPUT reads.

**Six of 600 genotypes change their observable response when nodes unreachable from OUTPUT
are removed.** Backward edge-reachability is therefore **not** a semantics-preserving
reduction on this IR. The graph's edges do not capture all of the dataflow; the machine
state is a side channel the edge relation does not model.

> `prune` as defined is **unsound**. It may not be used to justify any transfer of a result
> between genotypes, and `normal_form = canonical(prune(g))` is not a semantic normal form.

## The incompleteness is not an artifact of trivial genotypes — checked

17 distinct behaviours from 600 genotypes is suspiciously few, and the obvious confound is
that most random genotypes do nothing, so "many forms, one behaviour" would collapse to
"many ways to do nothing". Measured on `E_sym5` under `standard`:

```
behaviourally trivial (<=1 distinct non-abstain answer) : 484/600  (80.7%)
non-trivial (>1 distinct answers)                       : 116/600  (19.3%)
capability: min 0.0000  median 0.5833  max 0.8542
```

Restricting to the **116 non-trivial** genotypes only:

```
distinct observable signatures : 12
distinct normal forms          : 41
signatures with >1 normal form : 8
worst signature realized by    : 15 distinct normal forms
INCOMPLETE on non-trivial genotypes: True
```

The incompleteness survives. Eight of twelve genuinely different behaviours are each
realized by several distinct normal forms, one of them by fifteen.

**Incidental finding worth recording:** 80.7% of random genotypes drawn from the R5
operator grammar are behaviourally trivial. Four fifths of the search space this corpus
samples produces at most one distinct answer. That is a property of the grammar, measured
here for the first time, and it bears on every claim about what a neutral search "could
have found".

## CP2's answer, stated plainly

CP2 asks for a normal-form theorem *so known-form results become domain-wide results*. That
lift needs soundness to transfer a result and completeness to identify the class. On this
IR, at registered scope:

| requirement | status |
|---|---|
| a semantics-preserving reduction | **FAILS** — `prune` is unsound, 6/600 |
| normal form determines behaviour (soundness of the quotient) | **not established** — it rests on the reduction |
| behaviour determines normal form (completeness) | **FAILS** — 266 → 17, worst 183:1; survives restriction to non-trivial genotypes |

> **`KNOWN_FORM_RESULTS_LIFT_TO_DOMAIN_WIDE_RESULTS` = FALSE at registered scope.**
>
> CP2 as stated is **not achievable by this construction**. A known-form result covers the
> form it was proved on and does not extend to the behavioural class, because the normal
> form does not characterise that class — and the candidate reduction does not even
> preserve behaviour.

This is a negative for the critical path as stated, and it was the outcome the freeze named
as expected and tested for rather than around.

## What would be needed instead

Two routes remain, and neither is claimed here:

1. **A reduction that models the side channel.** The failure of `prune` is diagnosable: the
   edge relation is not the full dataflow because machine state is shared. A reduction that
   accounts for store reads and writes might be sound. That is a concrete, testable repair
   and is registered as the next CP2 step.
2. **Restriction to a decidable fragment.** Completeness cannot be had in general — deciding
   observational equivalence on a Turing-complete IR is undecidable, so no computable normal
   form can be complete over the whole IR. The only honest route to a *complete* normal form
   is to name a fragment where equivalence is decidable and confine the domain-wide claims
   to it. The corpus has never named such a fragment.

Route 2 is the structural reason CP2 cannot be finished as written: **the goal as stated is
not merely unachieved, it is unachievable over the full IR.** Any domain-wide lift must be
scoped to a decidable fragment, and that fragment must be declared before the lift is used.

## New protocol rule

> **Rule 47.** A result proved on one form may not be quoted as a result about a class
> unless the quotient carrying it has been shown **sound** (the reduction preserves the
> observable) and **complete** (the observable determines the representative) on the domain
> where it is used. Absent both, a known-form result is a point claim about that form.

---

## RV-377-115 — diagnosis of the six soundness counterexamples

The six genotypes whose observable response changes under `prune`, with the kinds dropped:

| genotype | nodes | dropped kinds |
|---|---|---|
| 212 | 6 → 3 | `DENSE`, `MATERIALIZE`, `NONLIN` |
| 218 | 10 → 7 | `INSERT`, `LINEAR`, `VERSIONED` |
| 278 | 10 → 7 | `GATE`, `LINEAR`, `PROGEXEC` |
| 348 | 6 → 5 | `INSERT` |
| 370 | 8 → 5 | `INSERT`, `LINEAR`, `SUM` |
| 591 | 7 → 6 | `DENSE` |

Kinds implicated across the six: `INSERT` ×3, `DENSE` ×2, `LINEAR` ×3, `MATERIALIZE`,
`VERSIONED`, `PROGEXEC`, `GATE`, `NONLIN`, `SUM` ×1 each.

**Five of the six are directly explained by the shared-state hypothesis.** Each of 212,
218, 348, 370 and 591 drops at least one kind that writes to shared machine state —
`INSERT` (writes a table entry), `DENSE` (state cells), `MATERIALIZE` (builds a table),
`VERSIONED` (lineage depth). The pure-transducer kinds appearing alongside them (`LINEAR`,
`SUM`, `NONLIN`, `GATE`) are collateral: they are dropped in the same pass but do not
themselves carry state.

**Genotype 278 is not explained by that classification** and is recorded as such. It drops
`GATE`, `LINEAR` and `PROGEXEC`, none of which is in the stateful set used here. `PROGEXEC`
executes a program and may have effects the classification does not capture, but that is a
conjecture, not a measurement, and it is not claimed. One of six counterexamples remains
undiagnosed.

### What this makes concrete

The repair registered as route 1 is now specific and falsifiable rather than a gesture:

> **A sound reduction must treat store reads and writes as dataflow edges.** Backward
> reachability over the *declared* edge relation is insufficient because `INSERT`,
> `DENSE`, `MATERIALIZE` and `VERSIONED` communicate through machine state that the edge
> relation does not represent. Adding an implicit edge from every writer of a store to
> every reader of that store, then re-running backward reachability, is the candidate
> repair — and it is testable by exactly the experiment above: it must reach 600/600.

That experiment is registered as the next CP2 step. It is **not** run here and **not**
claimed. If it reaches 600/600, `prune` becomes sound and the soundness half of CP2 is
available — the completeness half remains blocked for the undecidability reason already
recorded, which no reduction can repair.
