# Causal re-audit — re-frame and register of the causal-rung repair

Issue #833 Section M row `Re-audit causal cognition/intervention/counterfactuals.`;
freeze `cb6d6a59`; package `gmi-833-cognitive-reaudit-v2-implementation-v1`.

## What this row re-audits

The legacy package `research/gmi-causal-rung-repair-v1` (repair of PR #603)
already contains the exact content: CRR1 sharp Tian–Pearl PN bounds with
constructive attainment, CRR2 terminating finite-class query procedure, the
faithfulness-does-not-orient counterexample, smaller counterfactual
separators, incompatible-evidence refusal, identified constant-on-fiber
control, and the exhaustive 6-unit census (n=1..6, 1716 models at n=6). This
tranche re-frames that exact content as the Section-M re-audit: re-parents to
the upgraded #833 foundation and axiom core, states the freeze's allowed
terminal as the claim ceiling, re-asserts the freeze's causal hostiles under
freeze labels, and produces a `RESULT` plus replay.

## Freeze conclusion under test (verbatim)

> Causal answers are fiber-relative. For admitted models, evidence identifies
> a target exactly iff it is constant on the compatible-model fiber. A finite
> exact model list gives a terminating identified / partially identified /
> incompatible procedure and attaining endpoint witnesses. Observational
> equivalence can preserve different intervention or counterfactual targets,
> requiring abstention or bounds. The audit does not infer a causal
> graph/model class from data or promote population identities to
> finite-sample estimation.

## Registered content

- **CRR1 sharp necessity bounds.** For binary endogenous `X,Y` with a finite
  hidden root specifying response types `(X,Y0,Y1) in {0,1}^3`, exact
  population evidence `(a,b,c,d)`, `q0 = P(Y0=1)`, `q1 = P(Y1=1)`, every
  compatible model satisfies
  `max(0,(b+d-q0)/d) <= PN <= min(1,(1-q0-a)/d)`, every point attained by an
  explicit endpoint model, and the endpoints are equal iff the population
  point-identifies PN in the full response-type class. This is the
  constructive implementation of Tian–Pearl (2000) equation 25; it is an
  exact population calculation, not finite-sample estimation.
- **CRR2 terminating finite-class query procedure.** For a complete finite
  model list, an exact signature `s`, and a total target, the procedure
  returns INCOMPATIBLE (no match), IDENTIFIED (constant on the fiber), or
  PARTIALLY_IDENTIFIED with attaining lower/upper model witnesses.
- **Freeze hostile controls (re-asserted).**
  - `C_FREEZE_1` observation-equivalent models with different intervention /
    counterfactual targets: the registered rung pairs have all nine joint
    intervention laws equal while PN differs (six-original: PN `1/2` vs `1`;
    two-smaller: PN `0` vs `1`; three-treatment-supported: PN `0` vs `1`), so
    equal observation does not identify the counterfactual target.
  - `C_FREEZE_2` incompatible evidence: evidence with an empty compatible
    response-model class is refused (`empty compatible`), and `solve_fiber`
    over a disjoint model class returns INCOMPATIBLE — an absent model is not
    an identified value.
  - `C_FREEZE_3` identified constant-on-fiber control: the model
    `((1,0,1),)` is point-identified (`IDENTIFIED`, PN = 1) and `solve_fiber`
    over the n=1 uniform class returns IDENTIFIED — the no-alarm control.
  - `C_FREEZE_4` faithfulness does not orient: two graphs `X -> Y` and
    `Y -> X` with the same full-support observed law and dependence yet
    `do(Y=1|X=1)` `3/4` vs `1/2` — faithfulness alone does not orient.
  - `C_FREEZE_5` undefined conditioning is a distinct refusal from an empty
    fiber (never coerced to zero).

## Re-parenting (CUSTODY)

The legacy package originally imported its own PR #603 parents. Under the
freeze, this re-audit re-parents it to the upgraded #833 foundation
(`c0c574c4...`) and axiom core (`3366a3bc...`): the result blobs are pinned
in `MANIFEST_V1.json` and checked at run time, and the foundation/axiom-core
Python objects are actually imported and exercised (`parents_v1.py`). The
legacy package's own content is pinned by its frozen blobs (CORE `8fca71ec...`,
executable `f0f80cd3...`, RECEIPT `dbc910b0...`) and replayed byte-exactly
from the isolated `-I -B` run. In git order every implementation artifact of
this package postdates the freeze commit `cb6d6a59` (enforced by the CI
freeze-custody step).

## Claim ceiling

`GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE`; the
result is red if it reports a point outside a singleton causal target fiber,
treats a named causal algorithm as a primitive, uses floating-point decisions,
or accepts parent drift. Forbidden promotions include
`OBSERVATION_IDENTIFIES_CAUSATION`, `GENERAL_CAUSAL_DISCOVERY_SOLVED`,
`EMPIRICAL_COGNITIVE_VALIDATION`, `COMPLETE_GMI`.
