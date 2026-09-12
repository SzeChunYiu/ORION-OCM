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
