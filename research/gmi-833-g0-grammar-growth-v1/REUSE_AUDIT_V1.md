# Reuse-first machinery audit (E8 / #897)

Standing rule: before self-building search/library machinery, audit installable
parents and map components to tools; self-build only the project-specific
residual. This audit was executed before the implementation was finalized; the
installability probe ran on compute host `billy-old` (Python 3.14.4, pip 25.1.1)
on 2026-09-16.

## Probe transcript (verbatim)

```text
$ python3 -m pip index versions <pkg>
pyribs:      pyribs (0.0.2)
qdax:        qdax (0.5.0)
deap:        deap (1.4.4)
hpbandster: hpbandster (0.7.4)
dreamcoder:  ERROR: No matching distribution found for dreamcoder
stitch:      stitch (1.3.0)
dream-coder: ERROR: No matching distribution found for dream-coder
```

Notes: the `stitch` PyPI distribution's provenance relative to the Stitch
corpus-compression engine (Haskell/Rust research binaries) was not verified,
because it cannot change the residual decision below. `qdax` requires a JAX
toolchain. The repository itself pins `dependencies = []` (stdlib-only research
modules loaded by path), and CI runs on stock `ubuntu-latest` CPython 3.12 with
no third-party packages — an importable-parent dependency would break the
byte-identical receipt contract.

## Component → tool mapping

| component in this contract | candidate parent | verdict |
|---|---|---|
| Exact breadth-by-description-length enumeration over a frozen finite grammar | pyribs (QD archives), QDax | NOT A SUBSTITUTE: both are stochastic quality-diversity samplers; the contract freezes an exact deterministic enumerator whose total order is the metric. Importing a sampler would change the registered semantics, not implement them. |
| Deterministic charged admission (`o(b−1) > b+κ`, strict) | DEAP (GP ADFs / automatically defined functions), DreamCoder abstraction engine, Stitch compression | NOT A SUBSTITUTE: all three use stochastic search or heuristic scoring; none implements the frozen exact integer admission with definition+maintenance charges and strict positivity. DEAP's ADFs evolve program structure, they do not certify compression arithmetic. |
| Corpus compression / abstraction mining (repeated contiguous subprograms) | Stitch, DreamCoder wake/sleep, MDL refactoring | CONCEPTUAL PARENTS: imported as literature anchors (`PARENT_LITERATURE_V1.md`); the residual self-built piece is the exact greedy occurrence accounting and syntax-independent tie-break, which is contract-frozen and ~40 lines. |
| Budget allocation across candidate macros (which to admit first) | Hyperband/BOHB successive halving (`hpbandster`) | NOT APPLICABLE: candidate admission is exact per-candidate arithmetic on a corpus where the full candidate set is enumerable (5 first-generation candidates); bandit allocation would add stochastic machinery with nothing to allocate against. |
| Held-out evaluation with error bars | — | The main claims are deterministic integers (no sampling variance); the stochastic element is the null ensemble, which is an exact finite enumeration over 200 frozen seeds with a specified integer hash, not a Monte Carlo error bar. |

## Residual actually self-built

1. Expansion with fail-closed cycle detection on the token grammar (~30 lines).
2. Greedy non-overlapping occurrence counting + rewrite (~25 lines).
3. The deterministic INV-1 mining loop with the frozen tie-break key (~50 lines).
4. The exact burden computation: bottom-up segmentation DP in the main module,
   top-down memoized search in the oracle, naive enumeration as the reference
   (~60 lines each) — three mutually-checking implementations of one 15-line
   mathematical definition (T3).
5. Hostile battery and receipts.

No evolutionary/QD/bandit engine was reimplemented, wrapped, or reinvented: none
of the audited parents implements the frozen contract, and the residual is pure
exact integer arithmetic whose correctness is triple-checked by independent
implementations rather than by library authority.

## Vectorizable-evaluation fraction (recorded per standing rule)

The decisive computation (burden over 200 null libraries × 24 targets) is
vectorizable in principle (word-segmentation DP over a fixed small alphabet),
but the entire ensemble runs in < 2 s single-threaded on the registered fixture,
so vectorization would add a dependency (numpy/jax) and break the stdlib-only,
byte-identical receipt contract for zero scientific gain. The evaluator-trust
bottleneck is addressed the other way: three independent implementations of the
same arithmetic must agree exactly.
