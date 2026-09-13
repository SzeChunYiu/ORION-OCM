# Grand GMI End-to-End Derivations V1

Status: **EXACT FINITE DERIVATION TRACES; FAMILY VERDICTS CONDITIONAL ON DECLARED RESOURCE/SUBSTRATE MODELS**  
Date: 2026-09-12

This tranche executes the whole Grand-GMI chain rather than stopping at isolated theorems:

\[
(\mathcal E,\Omega,\Theta)
\to S^*
\to (\kappa,\tau)
\to \text{operational structure}
\to \text{realization families}
\to \rho,Reach
\to \text{reachable Pareto set}
\to \text{derived family/property}.
\]

The examples are exact finite proofs of the derivation method. Their resource numbers are declared synthetic substrate models and are **not** measurements of real neural/program hardware.

---

## 1. E2E-1 — selector obligation: neural family selected by a declared substrate

### 1.1 Obligation

A development phase reveals two persistent world bits `(x0,x1)`. Only later does a query bit `q` arrive. The required exact output is

\[
y=x_q.
\]

The query is not known during development.

### 1.2 Exact semantic state before the query

The protected continuation family contains both future queries `q=0` and `q=1`. The pre-query response signature of history `(x0,x1)` is therefore

\[
Q_{x_0x_1}=(x_0,x_1).
\]

All four bit pairs have distinct signatures. Hence

\[
|S^*|=4.
\]

No exact pre-query representation with fewer than four semantic states can preserve both possible future answers.

### 1.3 Temporal cut

Because the two bits disappear from the environment before `q` arrives, the development→query cut must carry four mutually distinguishable messages:

\[
\kappa(C_{dev\to query},0)=4\text{ states}=2\text{ ideal bits}.
\]

This is the Temporal Memory Cut Theorem.

### 1.4 Query-time routing transformation

At query time the answer requires selecting one of two retained coordinates according to `q`. Under a one-source access restriction, every fixed source choice has maximum average accuracy `3/4`; context-conditioned routing reaches exact accuracy `1`. Therefore dynamic routing is an operationally derived property under that access model.

What is derived so far:

- four-state pre-query semantic memory;
- a two-to-one context-conditioned selection operation;
- exact protected output.

No neural syntax has yet been derived.

### 1.5 Candidate realizations

Register three exact reachable implementations of the same operational structure:

| realization | family | energy | memory | latency | exact |
|---|---|---:|---:|---:|---|
| `N_route` | neural | 2 | 4 | 2 | yes |
| `P_mux` | program/circuit | 5 | 4 | 3 | yes |
| `T_lookup` | table | 7 | 8 | 4 | yes |

All three preserve the same four semantic states and exact selector response. The substrate/resource declaration is what distinguishes them.

`N_route=(2,4,2)` strictly dominates both alternatives. Therefore the reachable Pareto set contains only `N_route`.

### 1.6 Verdict

Under this registered substrate/resource model,

\[
\boxed{\text{neural family is Pareto-derived}.}
\]

This is a legitimate Grand-GMI derivation because non-neural alternatives were registered and excluded by resource domination rather than omitted.

If the substrate profile is changed so that `P_mux` is cheaper, the selected family can reverse while `S*`, `kappa`, `tau` and protected behavior remain unchanged. Thus neurality is not fundamental semantics; it is a morphology consequence of semantics **plus physical/developmental constraints**.

---

## 2. E2E-2 — exact recurrent controller: non-neural family selected

### 2.1 Obligation

The world supplies a binary stream `u_t`. The machine must output the running parity

\[
s_t=u_1\oplus\cdots\oplus u_t
\]

after every symbol, exactly.

### 2.2 Semantic state

Two histories are continuation-equivalent exactly when they have the same current parity. Therefore

\[
S^*=\{0,1\}.
\]

Both states are necessary: appending no further input already requires different current outputs.

### 2.3 Temporal cut and local transform

The temporal cut needs two persistent states, exactly one ideal bit. The local update is

\[
s_{t+1}=s_t\oplus u_{t+1}.
\]

Thus the operational morphology requires one-bit persistent state plus exact XOR update. A recurrent state is derived; an RNN is not.

### 2.4 Candidate realizations

Register three exact reachable realizations:

| realization | family | energy | memory | latency | exact |
|---|---|---:|---:|---:|---|
| `P_fsm` | program/FSM | 1 | 1 | 1 | yes |
| `N_recur` | neural | 4 | 2 | 3 | yes |
| `T_transition` | table | 3 | 2 | 2 | yes |

`P_fsm` strictly dominates both alternatives on the declared substrate.

### 2.5 Verdict

\[
\boxed{\text{non-neural exact controller family is Pareto-derived}.}
\]

Again, this is not an assertion that parity is intrinsically symbolic. It states that the declared substrate/resource model selects the exact finite controller after the architecture-neutral semantic requirement has been derived.

---

## 3. E2E-3 — factorized obligation: hybrid family selected

### 3.1 Product problem

Take two independent regions whose obligations and resource accounting satisfy the Grand-GMI product/tensorization hypotheses:

- region `A`: selector/routing obligation from E2E-1;
- region `B`: exact parity-state controller from E2E-2.

The protected joint obligation is the product of the two exact obligations; interface cost is declared zero beyond already counted fixed cuts; resource coordinates add.

### 3.2 Local family fronts

Use the local profiles

- selector region: neural `(1,2)`, program `(5,5)`;
- exact-controller region: neural `(5,5)`, program `(1,2)`.

The four family assignments are

| selector | controller | total profile |
|---|---|---|
| neural | neural | `(6,7)` |
| neural | program | `(2,4)` |
| program | neural | `(10,10)` |
| program | program | `(6,7)` |

The neural+program assignment strictly dominates every other assignment.

### 3.3 Verdict

\[
\boxed{\text{hybrid family is uniquely Pareto-derived}.}
\]

The result follows because the problem factorizes and different local transformation/resource structures select different families. The theory therefore has no requirement that one implementation paradigm dominate an entire intelligent system.

---

## 4. E2E-4 — same semantics, substrate-driven family inversion

Keep one exact protected transformation and two response-equivalent realizations `N` and `P`.

Substrate `A`:

\[
\rho_A(N)=(2,2),\qquad \rho_A(P)=(5,3).
\]

Substrate `B`:

\[
\rho_B(N)=(5,3),\qquad \rho_B(P)=(2,2).
\]

The semantic state, semantic cut requirements and protected response are identical. Family selection flips solely because the physical resource frontier deforms.

This is the concrete end-to-end demonstration of Substrate Lifting + Physical Resource Bridge + Family Selection:

\[
\boxed{\text{same intelligence semantics}\;\not\Rightarrow\;\text{same optimal implementation family}.}
\]

---

## 5. E2E derivation theorem

**GG60 — Finite End-to-End Derivation Theorem.** For a finite registered GMI problem with exact response semantics, finite exact candidate realizations/families, exact resource profiles and finite developmental reachability, every stage of the chain

\[
\mathcal G
\to S^*
\to (\kappa,\tau)
\to \mathcal A
\to \{Y_F\}
\to \operatorname{Pareto}
\to \text{derived common properties/family}
\]

is decidable by finite exact enumeration. A claimed family/property is derived iff it satisfies the Morphology Selection / Family Selection quantifiers on the resulting selected set.

This theorem is an immediate synthesis of finite operational completeness with the morphology/family-selection theorems; its value is that it closes the complete derivation pipeline.

## 6. What these traces establish

They establish all four logically distinct outcomes inside one theory:

1. **neural selection** can be derived conditionally;
2. **non-neural selection** can be derived conditionally;
3. **hybrid selection** can be derived conditionally;
4. **family coexistence/inversion** is the correct answer when physical/developmental facts do not force one family.

The theory therefore does not hide a neural or symbolic prior in its foundation.

## 7. What remains empirical

To turn one of these exact derivation traces into a statement about a real modern system, replace the synthetic resource profiles with independently measured/proved substrate profiles and validate the predicted family/operational properties prospectively.

The logical derivation pipeline is closed; the truth of any concrete real-world resource model remains an empirical question.