# Causal cognition closure — CAU-5 separator, discovery boundary, counterfactual rung (checklist item 13)

Status: **THEOREM + EXACT FINITE WITNESSES. Admissibility claim** (holds for every
learner under the declared interface; it does not claim neutral search *reaches*
the right structure — DU-1 standing rule applies).
Date: 2026-09-14. Scope: finite binary SCMs with declared acyclic graph,
deterministic equations, product root-noise law (the CAU-1–4 interface, unchanged).

Item-13 gap map: "no `P(Y|X)` vs `P(Y|do(X))` separation" → CAU-5a; "no causal-discovery
procedure" → CAU-5b (boundary + discharge list); "no counterfactual rung" → CAU-5c.
Item 13 is **POSITIVE at finite-SCM scope** on all three.

## CAU-5a — the separator has no universal sign

`P(Y|X=x)` and `P(Y|do(X=x))` are distinct functionals of one model. Two exact worlds:

- **W4a (confounded exaggeration).** `U` fair; `B` independent `Bern(1/4)`; `X=U xor B`;
  `Y=U`. Then `P(Y=1|X=1)=3/4` while `P(Y=1|do(X=1))=1/2`. Gap `+1/4`.
  (Observed law: `(0,0):3/8,(0,1):1/8,(1,0):1/8,(1,1):3/8` — machine-checked.)
- **W4b (confounded prevention).** `X=U` fair; `Y=¬U`. Then `P(Y=1|X=1)=0` while
  `P(Y=1|do(X=1))=1/2`. Gap `−1/2`.

Hence neither `P(Y|X) ≥ P(Y|do)` nor `≤` holds universally; the sign is
model-dependent. Any cognition that substitutes one for the other is wrong on at
least one admitted world. (W4a reuses the CAU W2 numbers through a fresh
construction path; W4b is new.)

## CAU-5b — discovery-procedure boundary

Let `D` be any measurable map from the observational law alone to an answer about
a `do`-target. On the CAU-1 W1 pair (world 0: `X=U,Y=U`; world 1: `X=U,Y=X`; same
observed law `{(0,0):1/2,(1,1):1/2}`, true `do(X=1)` targets `1/2` vs `1`), `D`
returns identically on both worlds while the truth differs — so its worst-world
error is unavoidable without further premises. A toy skeleton procedure
(`skeleton_w1`: keep `X–Y` iff dependent) is machine-checked to return the same
edge set on both worlds.

A discovery procedure therefore must discharge, in writing, at least: (i) the
declared compatible model class (fiber); (ii) the orientation premise
(faithfulness, declared DAG, or experimental access); (iii) observational support
for every stratum it adjusts (CAU-3). This is a boundary on what "discovery from
passive data" can mean, not a discovery algorithm.

## CAU-5c — the counterfactual rung is strictly above intervention

Rung 1 = observational law; rung 2 = all `do`-laws; rung 3 = counterfactuals.
**W5A/W5B:** root `U ∈ {0,…,5}` uniform; `X=1[U≥2]`; response tables

- A: `r = {0:(0,0),1:(0,0),2:(1,1),3:(0,1),4:(0,0),5:(0,0)}`
- B: `r = {0:(0,0),1:(0,0),2:(0,1),3:(0,1),4:(1,0),5:(0,0)}`

Machine-checked: identical rung-1 law (`(0,0):1/3,(1,1):1/3,(1,0):1/3`),
identical rung-2 laws (`do(1)→1/3`, `do(0)→1/6`), but probability of necessity
`PN=P(Y_0=0|X=1,Y=1)` is `1/2` in A vs `1` in B. Any rung-2-blind estimator
returns identically on both (checked for the midpoint rule, `1/4` both ways), so
its worst-world error is at least `|1−1/2|/2=1/4`. Rung 1+2 do not determine
rung 3 — this is why the right shape for partial rung-3 knowledge is *bounds*,
not points (cf. Balke–Pearl, cited as parent, not re-derived).

## Parents and what is new

Pearl (2009) supplies SCMs, `do`-calculus framing, and the identification/estimation
split; Balke–Pearl supply the bounds shape for rung 3. GG29/GG30 supply
obligation-relative relevance; CAU-1–4 supply the interface and supported routes.
New here: the no-universal-sign separator pair, the obs-law-only procedure
impossibility stated as a worst-world bound, and the minimal 6-unit rung-3 witness
with all three rungs machine-checked. No new identification calculus is claimed.

## Falsifier

Every equality above is an assertion in `test_causal_rungs_v1.py`. A refutation is
a miscount in the six-row tables — refuted or confirmed by re-running the file.
A finite SCM inside the declared class whose rung-1+2 laws pin `PN` would not
refute this (the claim is existential); a second independent implementation of
the three evaluators disagreeing would.

## Claim ceiling

No finite-sample rates, no general discovery algorithm, no learned premises, no
physical-randomizer warrant, no claim beyond finite binary SCMs. Exact scope only.

Files: [model](causal_rungs_v1.py) → [11 controls](test_causal_rungs_v1.py) →
[receipt](CAU5_RECEIPT_V1.json: 11/11 on billy-old py3.14 + laptop-billy py3.8,
normal + optimized). Existing CAU-1–4 sources untouched; their repair receipt is unaffected.
