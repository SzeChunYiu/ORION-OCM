# GMI POMDP belief-state exact microscope v1

Status: **EXACT FINITE CONTROL-STATE CALIBRATION / T7 NARROWING**

Date: 2026-09-12.

Purpose: execute the belief-state sufficiency theorem in a finite partially observed world and explicitly falsify point-estimate state for a decision family that depends on confidence.

## 1. World

Hidden binary state `H in {0,1}` is fixed during an episode with prior `P(H=1)=1/2`.

Each observation is conditionally iid with noise `eta=1/4`:

\[
P(O_t=H\mid H)=3/4.
\]

The action set is:

```text
guess0   reward 1 if H=0, else 0
guess1   reward 1 if H=1, else 0
safe     reward 4/5 regardless of H
```

The hidden state is not directly observed.

## 2. Exact belief

For history `h`, let

\[
p(h)=P(H=1\mid h).
\]

The next-observation law is

\[
P(O_{t+1}=1\mid h)=\frac14+\frac12p(h).
\]

Expected action values are

\[
V(guess1)=p,
\qquad
V(guess0)=1-p,
\qquad
V(safe)=4/5.
\]

Therefore next predictive law and all registered decision values are functions only of the scalar belief `p`.

## 3. Finite exhaustive result

`run_gmi_pomdp_belief_exact_v1.py` enumerates every observation history of length 0 through 6:

```text
127 histories
13 distinct exact posterior beliefs
1,040 pairs of distinct histories in the same belief class
```

For every same-belief pair the runner verifies exact equality of:

```text
next-observation distribution
all three action values
optimal action set
```

Zero violations occur.

## 4. MAP-point collision

A point estimate `argmax_H P(H|h)` is not sufficient for the registered decision family.

Examples:

```text
p = 3/4    -> MAP state 1, but safe action value 4/5 exceeds guess1
p = 9/10   -> MAP state 1, and guess1 is optimal
```

The exhaustive history set contains 980 history pairs with the same MAP/tie category but different optimal action sets.

Thus confidence-bearing belief state is not decorative: the registered utility structure can force distinctions that MAP state erases.

## 5. Negative twin

If the only available actions are `guess0` and `guess1` with symmetric 0/1 reward, then MAP is sufficient for the immediate action choice even though it is not sufficient for the full predictive law. State sufficiency is obligation-relative.

## 6. Claim ceiling

This is an exact binary known-model POMDP microscope. It does not close belief learning, large/continuous hidden state, exploration, approximation or model-based/model-free lifecycle selection.
