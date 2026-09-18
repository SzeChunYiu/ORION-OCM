# CORE — `gmi-833-grammar-morphology-encoding-v1` (#833 Section B)

**Row closed:** `Identify search grammars that encode the target morphology.`

**What this package does.** It supplies the *structural/cost* route that the row's parents
(#976 L48-SCREEN, the merged A2 signature extension) explicitly declared out of their own
reach, runs it exactly over the extractable grammar population, and adjudicates every hit
of both routes individually.

**Operational criterion (name-blind, exact integers).** A grammar `G` with declared target
`t` encodes `t` when some production set `Q` is *target-exclusive* — deleting `Q` changes
the minimum description cost of `t` and of **no other** semantic class — and the target's
minimum then strictly rises (`TARGET_SPECIFIC_SHORTCUT`) or becomes unreachable
(`TARGET_IS_A_PRIMITIVE`). Exclusivity is computed from cost tables, never from names.

**Headline (all exact integers; every number reproducible from `RESULT_V1.json`).**
Over 14 grammar instances from 5 merged packages (12 with a declared target):
**7 encode their declared target, all `ENCODES_DISCLOSED_CHARGED`, 0 `ENCODES_UNDISCLOSED`.**
3 of the 7 also flip the selected class (Tier-2). The only `TARGET_SPECIFIC_SHORTCUT` is
`gmi-833-g0-grammar-growth-v1`: unfolding the invented composite layer `{m1, m2}` raises
`mu(REUSE_POSITIVE)` **2 -> 5** and moves the selection to `UNRELATED_CONTROL`, while
changing no other class's minimum. 4 instances are `SCREENED_NOT_ADJUDICATED`
(3 `NO_PRODUCTION_STRUCTURE`, 1 `NUMERIC_PARAMETER_SPACE`) and 2 are `NO_DECLARED_TARGET` —
screened, **not** cleared.

Lexical route over 158 packages / 1,923 blocks: **37 hits, all 37 adjudicated with written
reasons, 0 CONFIRMED** (PARENT_LITERATURE_ATLAS 19, AUDIT_RECORD_ECHO 10,
SUBSTRING_COLLISION 5, PROSE_NEGATION 3).

**The two routes disagree completely** — D-LEX flags none of the packages D-COST identifies.
Every encoding in this corpus carries a neutral production name (`shared`, `rows`, `leaves`,
`branches`, `not_s`, `m1`, `m2`) and is invisible to lexical and fingerprint screens. That
is the row's real finding.

**Detector power is proven, not assumed.** V1 re-finds #891's registered `GA/GB`
counterexample (ALPHA -> BETA at `w = (1,1)`, equal coverage); V2 catches 11/11 shortcuts
planted into real corpus grammars; V3 raises 0 alarms on the clean control and is invariant
under every isometric relabeling; V4 detects all 6 hostile detector variants; V5 runs 204
randomized isometry controls with 0 spurious changes. The executor **refuses to emit any
finding** unless V1-V5 all pass.

**#891 is the boundary, not a target.** Its terminal
`NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE` is cited
EARNED-BY-COUNTEREXAMPLE and reproduced over the population (3 of 14 instances, 55 remints);
this package's claim is its exact complement — the identified, adjudicated population.

**Read in order:** `FREEZE_V1.md` (protocol + Amendments A1-A4, all frozen before the code)
-> `GRAMMAR_MORPHOLOGY_ENCODING_THEOREMS_V1.md` (GME-1..GME-6) -> `RESULT_V1.json` ->
`ADJUDICATION_V1.json` (per-instance and per-hit reasons) -> `PARENT_LITERATURE_V1.md`.

**Reproduce (stock CPython >= 3.8, stdlib only):**

```bash
cd research/gmi-833-grammar-morphology-encoding-v1
python3 -I -B    grammar_morphology_encoding_v1.py    # writes RESULT/ADJUDICATION/PLEX/DUMP
python3 -I -B    independent_oracle_v1.py             # writes ORACLE_RESULT_V1.json
python3 -I -B    test_grammar_morphology_encoding_v1.py   # 34 tests
python3 -I -O -B test_grammar_morphology_encoding_v1.py   # 34 tests
```

The executor takes about a minute (the corpus-wide lexical sweep dominates); the oracle and
the tests are instantaneous. Runs were executed on laptop-billy (python3 3.8.10), never on
the Mac.

**Claim ceiling:** `GMI_833_SEARCH_GRAMMAR_TARGET_ENCODING_IDENTIFICATION_AT_REGISTERED_SCOPE`.
Forbidden promotions are listed in `MANIFEST_V1.json` and asserted by the test battery. In
particular this is **not** a claim that no grammar encodes its target.
