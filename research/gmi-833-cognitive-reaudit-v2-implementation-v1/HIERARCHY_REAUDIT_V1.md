# Hierarchy re-audit — re-frame and register of the charged-hierarchy repair

Issue #833 Section M row `Re-audit hierarchical skills/chunking.`; freeze
`cb6d6a59`; package `gmi-833-cognitive-reaudit-v2-implementation-v1`.

## What this row re-audits

The legacy package `research/gmi-hierarchical-chunking-repair-v1` (commit
`9d50b7a1`) already contains the exact content: HCR-1 exact fixed-dictionary
parsing, HCR-2 finite acyclic acquisition with actual child calls, HCR-3
matched classes and the refutation of universal shallowness, HCR-4 quotient
identity does not choose a program factorization — plus the two freeze
hostile controls (longest-match greedy failure; hierarchy-loses workload) and
the normal + optimized replay (`VALIDATION_V1.json`, 23 tests). This tranche
re-frames that exact content as the Section-M re-audit: it re-parents the
package to the upgraded #833 foundation and axiom core, states the freeze's
allowed terminal as the claim ceiling, adds the freeze's hierarchy hostile
controls (already present, now explicitly re-asserted under freeze labels),
and produces a `RESULT` plus replay.

## Freeze conclusion under test (verbatim)

> Hierarchy is a charged reuse policy, not an anatomical or universal-depth
> primitive. Exact finite string chunking is shortest path over legal
> dictionary calls. Exact finite acyclic library acquisition is min-plus
> dynamic programming over retained sets. A chunk/higher skill is supported
> only when its complete acquisition, validation, storage, lookup, transport,
> and execution charges beat the flat alternative on the registered demand.
> Greedy parsing and universal shallow/deep claims require hostile failures.

## Registered content

- **HCR-1 exact parsing.** Fix a finite alphabet, a word `x` of length `n`,
  and a finite dictionary. Build vertices `0..n`; `i -> i+1` costs
  `c_(x_i)`; `i -> i+|p|` costs `u_p` when `p` matches at `i`. Every legal
  parse is a path and conversely; the backward recurrence `D(i) =
  min_(i->j)[cost+D(j)]` is exact. Greedy longest-match fails: for
  `x = abcde`, dictionary `{abc, ab, cde}`, greedy costs 3 (`abc,d,e`) while
  the exact parse costs 2 (`ab,cde`). Overlapping raw substring counts are not
  realized reuse demands (`aaa`, `aa` counts 2, at most 1 realized call).
- **HCR-2 finite acyclic acquisition with actual child calls.** Min-plus
  dynamic programming over retained sets: primitives plus topologically
  ordered rules; each rule has a unique finite expanded primitive trace; a
  retained artifact may be invoked for `u_j`, expansion pays dispatch `d_j`,
  first body execution may additionally pay `s_j` to retain. Primitive
  delivery `v_a` is charged in every arm. The exact optimum over ALL legal
  history policies is the min over final retained sets of the min-plus
  composition. The registered lifecycle: `3060` without retention, `3032`
  with the lower artifact allowed, `1233` with both allowed (common delivery
  30 charged in every arm); the extra-level saving `1799` exceeds the first
  saving `28` — yet PVR never implies universal shallow benefit.
- **HCR-3 refutation of universal shallowness** and **HCR-4** (quotient
  identity does not choose a program factorization: the same trace `abcde`
  is emitted by several bodies) are retained verbatim.
- **Freeze hostile controls (re-asserted).**
  - `H_FREEZE_1` longest-match greedy failure: greedy 3 vs exact 2 on
    `x=abcde`.
  - `H_FREEZE_2` a workload where hierarchy loses after complete charges:
    `Register(('a',),(1,), (('a',),),(0,),(9,),(0,))` on workload `(0,0)` —
    retained invocation priced 9, re-derivation 2; the exact solver returns
    cost 2 (retention is never chosen).
  - Complete lifecycle `3060/3032/1233` with first-use and descendant charges
    and the 30-unit common delivery.

## Re-parenting (CUSTODY)

The legacy package originally imported its own upstream parents. Under the
freeze, this re-audit re-parents it to the upgraded #833 foundation
(`c0c574c4...`) and axiom core (`3366a3bc...`): the result blobs are pinned
in `MANIFEST_V1.json` and checked at run time, and the foundation/axiom-core
Python objects are actually imported and exercised (`parents_v1.py`). The
legacy package's own content is pinned by its frozen blobs (CORE
`057ba5b7...`, executable `34266004...`, RECEIPT `a8aa57c6...`) and replayed
byte-exactly from the isolated `-I -B` run. In git order every implementation
artifact of this package postdates the freeze commit `cb6d6a59` (enforced by
the CI freeze-custody step).

## Claim ceiling

`GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE`; the
result is red if it erases first-use or descendant charges, treats a named
chunking algorithm as a primitive, silently breaks optimal ties, uses
floating-point decisions, or accepts parent drift. Forbidden promotions
include `UNIVERSAL_HIERARCHY_DEPTH`, `GOALS_DERIVED_FROM_DYNAMICS`,
`EMPIRICAL_COGNITIVE_VALIDATION`, `COMPLETE_GMI`.
