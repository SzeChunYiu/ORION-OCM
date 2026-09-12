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
