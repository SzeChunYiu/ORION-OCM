# Independent-host re-execution of the 2026-09-12 exact theory tranches

Date: 2026-09-12 (22:36–22:55 local). Host: `billy-laptop-old` (12-core Linux, uv CPython 3.11),
a different machine from the one that authored and committed the tranches. Fresh clone of
`origin/main` at `85052467`; every checker executed from the committed sources with no edits.

| tranche (PR) | checker | terminal reproduced | committed receipt changed? |
|---|---|---|---|
| Grand GMI layer 1 (#463) | `gmi-grand-unification-v1/grand_gmi_checks_v1.py` | `GRAND_GMI_SEMANTIC_CUT_TRANCHE_ALL_GREEN` | no |
| Grand GMI layer 2 (#464) | `gmi-grand-unification-v1/grand_gmi_recursive_checks_v1.py` | `GRAND_GMI_RECURSIVE_MORPHOGENESIS_TRANCHE_ALL_GREEN` | no |
| Grand GMI layer 3 (#466) | `gmi-grand-unification-v1/grand_gmi_substrate_symmetry_checks_v1.py` | `GRAND_GMI_SUBSTRATE_SYMMETRY_TRANCHE_ALL_GREEN` | no |
| prior-free formal core (#460) | `gmi-prior-free-derivation/finite_hostile_checks_v1.py` | `all_green: true` (5/5 checks) | no |
| finite operational closure (#462) | `machine-intelligence-morphogenesis-v1/gmi_microscope/run_gmi_operational_closure_v1.py` | `GMI_FINITE_OPERATIONAL_CLOSURE_MICROSCOPES_ALL_GREEN` | no |

"Changed?" was decided by `git status --short` on the clone after all five runs: zero lines, so
every regenerated receipt is byte-identical to the committed one. Raw stdout of each run is
stored under `microscopes/results/theory_replication_v1/`. All five programs are deterministic
(no RNG, exact rationals or exhaustive enumeration), so this is a reproducibility check on a
second host and interpreter, not an independent-authorship check: IG-4/IG-5 remain the
independence gates.

Scope note carried from the tranches themselves: every terminal above is at *finite operational*
/ registered scope; none lifts the protected K4 negative (0/264 at 10^6), the undecidability of
observational equivalence over the full IR, or the external empirical gates in
`GMI_CLOSURE_GAP_LEDGER_V10.md` §6.

## Addendum — second and third replication passes (main@fa5a754f, main@9e592bdd)

Re-executed every `*checks*.py` under `gmi-grand-unification-v1/` and `gmi-prior-free-derivation/` on
billy-old from a fresh checkout at each head. All reproduce their committed terminals with zero receipt
drift **except one**:

`grand_gmi_realization_compiler_checks_v1.py` (Grand GMI realization-compilation layer, receipt committed
at 33d35d5e) fails on every run with `AssertionError` at `assert functions == 274`. The exhaustive family
of Boolean functions on n = 1, 2, 3 inputs has 2² + 2⁴ + 2⁸ = **276** members, which is what the
script counts on billy-old under four different `PYTHONHASHSEED` values (deterministic). The committed
receipt is internally inconsistent: its `by_n` block records 4 + 16 + 256 functions while its aggregate
says 274, so the receipt was not produced by the committed script as written. Every one of the 2,120
point checks passes, so the theorem's exact claim holds and is in fact stronger than the receipt states.
Disposition: instrument/receipt defect, not a theory defect; fixed additively in a separate PR (assert
corrected to 276, receipt regenerated on billy-old), recorded here so that the tranche's
`ALL_GREEN` is read as "green after correction of a mis-pinned constant".

## Addendum — fourth pass (main@cf7c76e5, after the count correction and seven further layers)

26 checkers under `gmi-grand-unification-v1/` and `gmi-prior-free-derivation/` executed from a fresh
checkout on billy-old: 26 of 26 exit 0, 25 distinct `…ALL_GREEN` terminals reproduced (the prior-free
hostile checks report `all_green: true` in JSON rather than a terminal string), `git status` clean after
the runs — no committed receipt changed. The realization-compiler layer now reproduces after PR #480.
Layers covered by this pass and not by the earlier ones: physical resource bridge, quantum process
instantiation, measurable continuous GMI, realization compilation, morphology selection, neural /
non-neural family selection, phenomenology reduction, end-to-end derivation traces, epistemic
acquisition, continuous realization bridge, non-neural constructive derivation, active closed-loop,
compositional language morphology, NN/non-NN derivation certificate, planning semantic resolution.
