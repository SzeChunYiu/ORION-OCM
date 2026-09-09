# R0D executable calibration V1 — paid Decision Region Determination

**Status:** exact synthetic calibration / mature-parent adoption / no ML / no operational R0D terminal.

This tranche makes `R0D_PAID_DECISION_REGION_PROTOCOL_V1.md` executable.  It does
not claim a new active-learning theorem.  The information-acquisition parent is
Decision Region Determination (DRD), and the paid-cognition layer is ordinary
rational metareasoning/value-of-computation.  The OCM-specific contribution at
this stage is narrower: source-custody the repository's DEV-5/6/X1 observations,
put the relevant parents into one exact cost model, and expose the price regimes
under which an earlier safe stop is or is not economically worthwhile.

## 1. Parent provenance

Javdani et al., *Near Optimal Bayesian Active Learning for Decision Making*,
AISTATS/PMLR 33 (2014), formulate DRD over overlapping decision regions: testing
may stop when every hypothesis consistent with observations lies in a common
region.  Their paper also identifies Equivalence Class Determination (ECD) as the
partition special case.  This is the correct parent for the safety/information
question; full hidden-state identification is not the objective when multiple
hypotheses license the same decision.

Russell and Wefald, *Principles of Metareasoning*, Artificial Intelligence 49
(1991), provide the second parent: computational actions should be selected by
their effect on external decision utility, with the computation itself charged.
R0D therefore keeps these two layers separate:

```text
DRD/ECD:  has enough information been acquired to license a protected action?
P-PAID:   even if an action is licensed, is more cognition worth its full cost?
```

The second question is not attributed to the DRD paper.

## 2. Executable object

`r0d_paid_decision_region.py` uses exact `fractions.Fraction` arithmetic and a
finite deterministic model:

```text
H                 hypotheses/world states
G_h               protected actions safe in h
R_a               worlds covered by action a
T                 legal probes
obs(h,t)          deterministic registered outcome
c_probe(t)        probe price
c_action(a)       protected-action price
c_policy          controller lookup price per visited information state
c_region          explicit decision-region predicate price per visited state
```

It runs four parents on the same model:

```text
P-ID     identify one hypothesis before acting
P-ECD    stop in one registered disjoint equivalence class
P-DRD    stop once the surviving version space has a common safe action
P-PAID   exact Bellman choice between acting now and buying another probe
```

`P-PAID` is deliberately allowed to continue after `Gamma(V) != empty`: safety
sufficiency is not economic sufficiency when the currently common safe action is
expensive and more information can reveal a cheaper protected action.

Controller and region-predicate work are never free.  This is the accounting
correction demanded by DEV-6 and X1.

## 3. Exact synthetic witnesses

The registered controller lookup price is `1/4` per visited information state.
All numbers below are exact rationals.

### 3.1 Decision region can stop strictly before identity

A four-hypothesis partition has two action regions `{h0,h1}` and `{h2,h3}`.  One
probe identifies the region; a second identifies the member.

```text
parent    total cost    worst probes
P-ID      11/4          2
P-ECD      3/2          1
P-DRD      3/2          1
P-PAID     3/2          1
```

This is the ordinary DRD/ECD advantage: exact cause identity is unnecessary for
the protected decision.

### 3.2 Fewer probes can be more expensive

Charge the naive DRD region predicate `r` on every visited information state.
For this instance:

```text
C_ID       = 11/4
C_DRD(r)   = 3/2 + 2r
```

Therefore the exact break-even is

```text
r* = 5/8.
```

The tests verify all three sides:

```text
r = 1/2    C_DRD = 5/2   < 11/4
r = 5/8    C_DRD = 11/4  = 11/4
r = 3/4    C_DRD = 3     > 11/4
```

At the receipt's hostile price `r=1`, DRD uses only one probe but costs `7/2`,
which is worse than P-ID's `11/4` with two probes.  Probe count alone is not an
economic objective.

### 3.3 Safe now can still mean probe

A two-world problem gives both worlds a common safe action costing `10`, while
world-specific actions cost `1`.  One legal probe reveals the world.  With
controller lookup `l=1/4` and probe price `p`:

```text
C_stop      = l + 10            = 41/4
C_probe     = l + p + l + 1     = p + 3/2
```

The exact break-even is

```text
p* = 35/4 = 8.75.
```

Below it, exact P-PAID continues cognition despite an already-safe common action;
above it, P-PAID stops.  The tests certify the boundary with `p=8`, `35/4`, and
`9`, plus receipt cases at `p=2` and `p=10`.

This is the formal correction to the tempting but false implication

```text
Gamma(V) != empty  =>  stop cognition.
```

The valid implication is only that further identification is unnecessary for
**safety**.  Economics still depends on the cost of the currently available
action and the value/cost of further computation.

### 3.4 Observation collision remains an authority failure

A hostile pair is given the same complete legal probe transcript but disjoint
protected action sets.  `observation_action_collisions()` detects the pair, and
P-DRD is unsolvable from that legal channel.  High posterior confidence inside a
misspecified declared class would not repair this; the observation/hypothesis
boundary itself is insufficient.

## 4. Repository-source calibration

The executable microbenchmarks above are synthetic witnesses, not re-runs of the
following donor experiments.  Their role is source custody and cross-check only.

```text
DEV-5  a0c4931629263ee92fe676e479445b188af5df6e
       same full language; singleton vs per-query unanimity decision rule;
       the weaker common-action rule preserves soundness when truth remains in V.

DEV-6  f676a34e022fff710a05cede0ea6027a8c390e28
       consultation re-priced proportional to work scanned;
       unanimity-vs-singleton direction survives, corrected ratio range
       0.2923502856247197 .. 0.9704311019045002;
       incremental vote maintenance is refuted when fully charged.

X1     2ba88a80593a8e3ddcbedaf6520da5bc7fddbed3
       cross-domain one-line `determined(candidate)` ablation;
       198 vs 529 interventions at matched capability, but 8039 vs 4936 total
       work: fewer external queries can still lose after cognition is charged.
```

These three sources motivate the exact R0D cost decomposition; they do not make
the synthetic thresholds operational measurements.

## 5. What has converged

R0D no longer needs a learned routing hypothesis at this layer.  The immediate
parent ladder is exact and conventional:

```text
full identification
  -> equivalence/decision-region stopping
  -> fully charged decision-region predicate
  -> exact paid metareasoning
  -> observation/hypothesis-class hostile
```

A learned selector is admissible only after a real frozen donor population shows
residual economic regret that survives these parents and the complete cost of
features, inference, training, update, storage, replay and revision.

Current executable terminal:

```text
R0D_EXECUTABLE_PARENT_ESTABLISHED_SYNTHETIC_ONLY
```

It deliberately does **not** claim `DECISION_REGION_STOPPING_USEFUL_R0D` or
`PAID_META_POLICY_SUFFICIENT_R0D` operationally.  The next empirical step is a
prospectively frozen real donor population/trace with legal observation and cost
channels, not an MLP.
