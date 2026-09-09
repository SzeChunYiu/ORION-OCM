# HST Definitions V1 (frozen)

Frozen by `FREEZE_HST_V1.json` before any theorem artifact. A lane may not edit these
definitions; a needed change is a declared amendment (`FREEZE_HST_V1.json.amendments`,
sha-chained) and re-derivation of affected rows.

## 1. Developmental search state

```text
Σ_t = (L_t, Q_t, H_t, E_t, R_t, V_t, C)
```

| symbol | object | mathematical type |
|---|---|---|
| `L_t` | constructive language / legal morphology grammar | a set of well-formed candidate descriptions (decidable membership assumed for P1 use; where not decidable, the row says so) |
| `Q_t` | proposal / variation distribution | probability kernel `Q_t(· | L_t, H_t, E_t, R_t)` over candidate descriptions |
| `H_t` | inherited persistent structure | a finite object (methods, memory, archive, failure records, modules) — part of the *state*, not the environment |
| `E_t` | task/ecology | finite or measurable task space with a sampling rule when a P3 row needs one |
| `R_t` | resource-allocation policy | measurable map state → resource split |
| `V_t` | evaluator/verifier | function `V_t(x, τ; C)` returning admissible evidence `e`; its soundness is an *assumption of C*, never a theorem of HST |
| `C` | external constitution | fixed across `t` within any theorem; may carry metering and adoption gates |

Non-circularity: `C` is a parameter (an oracle-contract), not a term HST defines. "Useful"
never appears in a P1/P2 statement except through a frozen admissible-evidence predicate
`Adm(e)` supplied by `C` or the registered ecology.

## 2. Development step

```text
x ~ Q_t(· | L_t, H_t, E_t, R_t)
e = V_t(x, τ; C)
Σ_{t+1} = U(Σ_t, x, e)
```

`U` is an arbitrary measurable update map. HST's object of study is the induced process on
`Σ`, not on `x`.

## 3. Verified Search Burden (measurement object, not a theorem)

For task `τ` and price vector `p` (frozen prospectively per campaign):

```text
B_t(τ) = E[ p · (resources to first C-admissible verified solution) | Σ_t ]
```

`B` is a vector unless a scalarization was frozen first. Self-change burden `B_self,t` is
the same expectation with "first useful legal verified self-change" as the stopping event.
No theorem of HST asserts `B` is "intelligence"; §6 of the issue lists burden-monotonicity
claims as P4.

## 4. Evolvability (finite, non-circular)

```text
Ev_t(x; U, D) = P_{x'~Q_t(·|x)}[ Adm(x') ∧ Useful(x'; D) ]
```

where `D` is a registered future-task distribution/ecology and `Useful` is the frozen
predicate of that registration. At finite scope (finite candidate set, computable `Q_t`)
`Ev` is exactly enumerable — this is what lane B's T10 microscope computes. Any claim
`Ev_{t+1} > Ev_t` **on real systems** is P4.

## 5. Proof classes

P1 formal theorem · P2 finite exact certificate · P3 probabilistic/generalization bound ·
P4 empirical causal hypothesis · P5 impossibility/limit. One primary class per row; a row
may carry an additional secondary class. No empirical positive is retroactively promoted.

## 6. Terminology discipline (binding on all rows)

- "optional inheritance" = old legal strategies remain legal **and runnable at their old
  cost** (`A_t ⊆ A_{t+1}` with zero mandatory overhead).
- "mandatory overhead" `M` = resource cost charged to *every* strategy of `A_{t+1}` that
  `A_t` strategies did not pay (storage/index/maintenance of `H_{t+1}`).
- "reach" `Reach_B(O)` = set of contracts satisfiable within resource bound `B` by
  compositions of `O` (per #145's transformation closure).
- "open-ended" claims are horizon-scoped or barred (T12/T13); no binary OEE declaration
  from any finite run.

## 7. What these definitions deliberately do not define

"intelligence", "understanding", "major transition as a fact of nature" (only the
conditional economic criterion of T11), "sufficiently expressive representation" (T03
gives the falsifiable counterpart), and any semantic property of arbitrary programs
(T15 bars it).
