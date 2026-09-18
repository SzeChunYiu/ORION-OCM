# Section-M social/metacognitive re-audit — core

Package: `research/gmi-833-cognitive-reaudit-social-v1`. Issue #833, Section M.
Claim ceiling:
`GMI_833_METACOGNITION_SOCIAL_COMMUNICATION_TEACHING_CULTURE_REAUDIT_AT_REGISTERED_EXACT_SCOPE`.
Evidence level EV2, maturity M2. Verdict GREEN on `242,892` registered exact cases.

## The one finding

Each of these five cognitive functions, defined externally, is a contract over
observables, achievable scores and charged resources — and in each case the
external signature **fails to identify the underlying mechanism**, with an exact
boundary saying precisely when it fails. That relativity is the theorem, not a
hedge.

| result | external definition | exact characterization | hostile twin that aliases it |
|---|---|---|---|
| `VOC-1`/`NONID-1` | allocation of charged computation driven by a registered internal estimate, evidenced only by the allocation trace | a further step is worth its charge iff `I(path) > p(path)`; a fixed-schedule twin exists **iff** allocation is a deterministic function of the observable instance label | a fixed schedule with no internal estimate, found by exhaustive search over all `125` registered schedules |
| `SOC-1` | behaviour depends on another agent's *unobserved* state, not only on its observed actions | `V_hid >= V_obs`; equality **iff** the observed-action channel is sufficient for the payoff-relevant partition, on the positive-probability support | a pure behaviour-reader scoring exactly the same — `15,267` of `19,263` ecologies |
| `COM-1..4` | a charged channel whose use changes the joint achievable score | strictly pays **iff** `V_pi - V_0 > c(pi)`; "the receiver can act differentially" is *proved equivalent* to `V_pi > V_0`, not assumed | coordination from a shared observation at zero channel charge — `20,950` instances |
| `TCH-1..3`/`NONID-4` | imitation = learner's charge falls because of the demonstration; teaching = the demonstrator pays to cause that fall | jointly worth it **iff** `n * Delta > D`; omitting `D` strictly enlarges the worthwhile set (`450` vs `352`, `98` artifacts) | a concurrent cause: `200/200` pre/post false alarms against `0/200` with a control arm |
| `CUL-1..3`/`NONID-5` | generation `n+1` exceeds generation `n`'s starting capability *through transmission* | ratchets **iff** `lambda * a_n < g`, exact ceiling `a* = g / lambda`; transmission is identified by a charged margin `(r - t) * phi * a_n`, and **never** by the trajectory | independent re-derivation reproducing every trajectory exactly — all `270` triples |

`RESULT_V1.json` keeps two counts apart on purpose. **`hostiles_detected`** are
deliberately broken variants that are actually computed and caught by
disagreement with the honest route — a non-strict threshold, a behaviour-reader
secretly reading hidden state, a free-labour verdict, a pre/post detector with no
control arm, a claimed separation at `t = r = k`. **`aliasing_regimes_witnessed`**
are censuses of the registered instances in which the twin exists; no detector
could have failed to fire on them, and they are not reported as detections.

Where a probe cannot separate two hypotheses the executor emits the registered
typed abstention (`CANNOT_IDENTIFY_FROM_ALLOCATION_TRACE`,
`CANNOT_IDENTIFY_FROM_SCORE_ALONE`, `CANNOT_IDENTIFY_FROM_COORDINATION_ALONE`,
`CANNOT_IDENTIFY_WITHOUT_CONTROL_ARM`,
`CANNOT_IDENTIFY_FROM_CAPABILITY_TRAJECTORY`) rather than guessing.

## Two materially independent routes

Route A (`cognitive_reaudit_social_v1.py`) decides by closed form, backward
induction, the refinement-value decomposition and the exact classification of the
transmission recursion. Route B (`route_b_oracle_v1.py`) decides by exhaustive
enumeration over policies and schedules and by direct iteration of the recursion;
it imports no route-A logic and knows none of the results. `0` mismatches across
every census. `registered_scopes_v1.py` is pure data construction shared by both
and holds no decision rule.

## Nulls beaten (no-alarm case asserted, not only recall)

```
mc1 random policy beats the backward-induction optimum   0/200
mc2 false alarms on a sufficient channel                 0/162  (of 200 drawn, 162 had a sufficient channel)
mc2 recall on planted separating ecologies             200/200
mc3 two-route disagreements on strict pay                0/200
mc3 useless channel declared paying                      0/200
mc4 control-arm false alarms on concurrent cause         0/200
mc4 control-arm recall on planted imitation            200/200
mc5 closed form versus direct iteration                  0/200
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-cognitive-reaudit-social-v1/cognitive_reaudit_social_v1.py
python3 -I -O -B research/gmi-833-cognitive-reaudit-social-v1/cognitive_reaudit_social_v1.py
python3 -I -B  research/gmi-833-cognitive-reaudit-social-v1/test_cognitive_reaudit_social_v1.py
python3 -I -O -B research/gmi-833-cognitive-reaudit-social-v1/test_cognitive_reaudit_social_v1.py
```

Both executor modes must write a byte-identical `RESULT_V1.json`
(`md5 398e9eb802d0fd67f02ee7936a878ca1`). Stdlib only; exact `Fraction`
arithmetic throughout; no float literal exists in any file and a test enforces it.
Parent blobs are pinned in `MANIFEST_V1.json` and re-checked at run time — parent
drift is a red result.

## Demarcations

- `#926` / PR `#927` owns hierarchical skills, **plan-search stopping** and causal
  cognition. `VOC-2` here is an instrumental backward-induction lemma; the
  myopic-versus-optimal EVC comparison is theirs and is never computed here.
- `#959` / `#957` owns ecology-generator variation of communication topology and
  price. MC-3 is the capability-side derivation.
- `#897` (`gmi-833-g0-grammar-growth-v1`) owns within-lifetime library formation.
  MC-5 is inter-generational transmission.
- PR `#919` / `#917` owns `MEMORY-1`/`ATTENTION-1`/`CONCEPT-1`, whose re-audit
  pattern this package follows.

## Files

`FREEZE_V1.md` (committed before any implementation) · `SOCIAL_REAUDIT_THEOREMS_V1.md`
· `PARENT_OWNERSHIP_V1.md` · `RESULT_V1.json` · `MANIFEST_V1.json` ·
`ISSUE_833_RECONCILIATION_SOCIAL_V1.json` · `registered_scopes_v1.py` ·
`route_b_oracle_v1.py` · `cognitive_reaudit_social_v1.py` ·
`test_cognitive_reaudit_social_v1.py` ·
`.github/workflows/gmi-833-cognitive-reaudit-social.yml`.

## Not claimed

Nothing about human or animal cognition; no empirical validation; no architecture,
module or anatomy; no universal cognitive law; no general or plan-search optimal
stopping; no causal discovery; no learning of any registered quantity from data.
