# Belief, prediction, regime and deception (I7, remainder)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/social_strategic_witness.py`.
Receipt: `STAGE_SOCIAL_STRATEGIC_V1.json`.
Method: exhaustive enumeration over `fractions.Fraction`. No sampling, no
floating point in any reported number. Each part carries a non-vacuity gate
that aborts the run if the machinery under test pays everywhere or nowhere.

This closes the four boxes left open by `GMI_SOCIAL_AGENT_MODELS_V1.md`.

## D1. A hidden belief is not a relabelled hidden goal

A goal is a latent that fixes what the partner wants. A belief is a latent
fixed by what the partner has *observed*. The distinction is usually asserted.
Here it is an exclusion by exhaustion.

A partner acts on where it believes an object is. The object starts at `L1`
and moves to `L2`; the partner may or may not have seen the move.

| goal | saw the move | acts |
|---|---|---|
| fetch | yes | `L2` |
| fetch | no | `L1` |
| avoid | yes | `L1` |
| avoid | no | `L2` |

The witness enumerates **every** function from goals to actions — all four —
and tests each against this table. None fits. A goal-only model is not merely
inelegant here; it is refuted by exhaustion.

Restrict the partner's channel so that it always observes what we observe, and
the same enumeration finds a fit: `{fetch: L2, avoid: L1}`.

> **Belief inference is forced exactly when the partner's information can
> differ from ours, and not otherwise.**

That condition is precisely what a false-belief task engineers. The task is not
imported from developmental psychology as a benchmark — it is the minimal
discriminating experiment between the two model classes, and the accounting
picks it out on its own.

Pricing it, with a stake of `1` for a correct prediction and a belief model
costing `1/5`:

| P(partner saw the move) | goal-only | belief model | belief pays? |
|---:|---:|---:|---|
| 0 | 1 | 4/5 | no |
| 1/4 | 3/4 | 4/5 | **yes** |
| 1/2 | 1/2 | 4/5 | **yes** |
| 3/4 | 3/4 | 4/5 | **yes** |
| 1 | 1 | 4/5 | no |

Belief tracking pays on three of five settings. It is worthless at both
extremes — when the partner's information state is *certain*, there is nothing
to track, and a goal-only model is already right every time.

This is the third independent appearance of one pattern in this corpus:
**cognitive machinery earns its cost only at intermediate uncertainty.** The
agent model in `GMI_SOCIAL_AGENT_MODELS_V1.md` pays only at middling priors;
calibration in `GMI_METACOGNITION_CALIBRATION_V1.md` matters only near the
decision threshold; belief tracking pays only when what the partner knows is
genuinely in doubt. Three different mechanisms, one shape.

## D2. Prediction pays only when commitment precedes revelation

A predictor of the partner's next action is retained state and must pay for
itself. Its value depends on the *protocol*, not on its accuracy alone.

**Sequential protocol** — we act after seeing the partner act. Observation is
free and perfect, so the predictor is redundant: value `2` without it, `9/5`
with it. It loses **exactly its price**, `1/5`, with no residual. A predictor
of a variable we are about to observe anyway is worth nothing.

**Simultaneous protocol** — we must commit first. Now the predictor has
something to do:

| accuracy `q` | no predictor | with predictor | pays? |
|---:|---:|---:|---|
| 1/2 | 1 | 4/5 | no |
| 11/20 | 1 | 9/10 | no |
| 3/5 | 1 | 1 | no (exact tie) |
| **13/20** | 1 | **11/10** | **yes** |
| 7/10 | 1 | 6/5 | yes |
| 3/4 | 1 | 13/10 | yes |
| 4/5 | 1 | 7/5 | yes |

The threshold is `q = 13/20`, and `q = 3/5` is an exact tie — the accuracy at
which the predictor's gain exactly equals its price.

> **Intention prediction is the value of information about a variable we must
> act before seeing.** Remove the commitment, and prediction has no value at
> any accuracy.

This predicts where prediction machinery should appear: in agents facing
simultaneous or anticipatory decisions, and not in agents that can always wait.

## D3. Regime determines whether a signal can carry anything

The partner knows its own type and *chooses* a signal. We have a reading rule.
The witness enumerates all four deterministic reading rules, computes the
sender's best signal against each, and keeps the rules that are a best response
to the signalling they themselves induce — i.e. the fixed points.

**Aligned (common interest).** Three equilibria, two of them informative:

| reading rule | informative | value |
|---|---|---:|
| `says_coop→share, says_comp→guard` | yes | 2 |
| `says_coop→guard, says_comp→share` | yes | 2 |
| `says_coop→guard, says_comp→guard` | no | 1 |

Both informative equilibria score the same. **Which word means which is
arbitrary** — the two are mirror images — but *that* the words mean something
is stable. Conventional meaning falls out of the fixed-point structure; it is
not installed.

**Opposed (zero sum).** One equilibrium, and it is uninformative:
`says_coop→guard, says_comp→guard`, value `1`. There is no informative
equilibrium at all.

**The reason is not that the partner lies.** Against a trusting reader the
opposed sender separates — `coop` sends `says_comp`, `comp` sends `says_coop`.
That is fully informative: *a lie told every time is invertible.* Against an
inverting reader it separates the other way. Each reading re-aims the sender at
the other reading, and the best-response cycle never closes.

> **Deterministic deception destroys no information. What destroys information
> is that no deterministic reading survives its own effect on the sender.**

So the worthlessness of an opposed signal is a fixed-point property, not a
channel property. This is a strict improvement on the stipulated
"uninformative partner" twin in `GMI_SOCIAL_AGENT_MODELS_V1.md`: there the
signal was *declared* uninformative; here uninformativeness is *produced* by
the incentive structure.

## D4. Deception, detection, and a substitution

A sender lies iff its gain exceeds its expected punishment, `gain > ρ·penalty`.
With `gain = 3`:

| penalty | P(detect) | lies? |
|---:|---:|---|
| 0 | 1/4, 1/2 | yes, yes |
| 2 | 1/4, 1/2 | yes, yes |
| 6 | 1/4 | yes |
| 6 | 1/2 | **no** |
| 12 | 1/4, 1/2 | no, no |

We verify iff the expected damage prevented exceeds the verification cost —
the same value-of-information rule as everywhere else in this corpus. With
cost `1/2` and damage `3`, verification starts paying at `P(deception) = 1/4`.

The structural consequence:

> **Commitment and detection are substitutes.** A penalty above `6` at
> `ρ = 1/2` deters entirely; `P(deception)` is then `0`, and verification is
> worth nothing at any cost.

An agent that can credibly commit to punishment needs no lie detector. An agent
that cannot must pay for one. This predicts that detection machinery and
commitment machinery are alternatives rather than companions, and that the
observed mix in any species should track which of the two it can afford.

## Scope and what is not claimed

Every number is exact for the payoff structures registered in the witness.
None of these are claims about magnitudes in any natural system; the reported
thresholds (`q = 13/20`, `P(deception) = 1/4`, penalty `6`) are properties of
the specific matrices enumerated, and moving the matrices moves them. What is
structural, and survives any reparameterisation, is the **shape** of each
result: exclusion-by-exhaustion in D1, protocol-dependence in D2,
fixed-point-not-channel in D3, substitution in D4.

D3 covers deterministic reading rules only. The mixed-strategy equilibrium of
the opposed game is not computed here, and the claim is confined to the
non-existence of an informative *deterministic* fixed point.

D4 treats detection probability `ρ` as exogenous. Making `ρ` a function of
verification effort turns this into a joint optimisation and is not done here.

With these four, I7's nine boxes are complete.
