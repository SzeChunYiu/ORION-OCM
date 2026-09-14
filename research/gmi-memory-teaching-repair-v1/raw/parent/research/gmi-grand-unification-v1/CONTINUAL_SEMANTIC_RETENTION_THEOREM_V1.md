# Grand GMI Continual Semantic Retention Theorem V1

Status: **THEOREM + EXACT FINITE WITNESSES**  
Date: 2026-09-12

## 0. Continual learning is a past-to-future semantic cut

Consider a sequence of obligations/tasks

\[
\Omega_1,\Omega_2,\ldots,\Omega_T
\]

learned from sequential experience. At a later evaluation time the machine may be required to answer any of the retained obligations.

The information from old experience must cross the causal cut separating past training from future evaluation through some combination of persistent internal state, weights, external memory, replay data, environment access or other side channels.

Grand GMI therefore treats catastrophic forgetting as a semantic-cut phenomenon before it is a neural-network phenomenon.

---

## 1. Joint semantic state of retained tasks

Let `H` be the set of possible relevant past histories/world states. For each retained obligation define its exact response label

\[
Q_i:H\to Y_i.
\]

Define the joint retained response

\[
\Sigma_t(h)=\big(Q_1(h),\ldots,Q_t(h)\big).
\]

Two histories are retention-equivalent after task `t` iff all retained task responses agree:

\[
h\equiv_t h'
\iff
\Sigma_t(h)=\Sigma_t(h').
\]

Let

\[
N_t=|H/\!\equiv_t|
\]

be the number of exact joint semantic classes.

---

## 2. Exact persistent-memory theorem

Suppose that after training no old-task evidence is available except a persistent memory symbol

\[
Z:H\to\{1,\ldots,M\}.
\]

At evaluation, every retained task answer must be recovered exactly from `Z` and the task/query identity.

**CSR-1 — Continual Retention Width Theorem.** Exact retention of all tasks `1..t` is possible iff the memory encoding separates every pair of histories with different joint signatures. Consequently the minimum number of persistent memory states is exactly

\[
\boxed{M^*_t=N_t.}
\]

The minimum binary memory width is

\[
\boxed{s^*_t=\lceil\log_2N_t\rceil.}
\]

**Proof.** If two joint-distinct histories share a memory state, then some retained task gives different required responses but the decoder sees the same memory symbol and task identity, contradiction. Conversely, assign one memory state to each joint semantic class and decode the appropriate coordinate of `Sigma_t`. QED.

This is an exact specialization of the master semantic-cut theorem to the training→future-evaluation cut.

---

## 3. Semantic capacity growth law

Adding a task appends one coordinate to the joint response. Therefore

\[
h\equiv_{t+1}h'\implies h\equiv_t h',
\]

so the retained partition can only refine:

\[
\boxed{N_{t+1}\ge N_t.}
\]

Define the incremental semantic retention requirement

\[
\boxed{\Delta I_{t+1}=\log_2N_{t+1}-\log_2N_t\ge0.}
\]

**CSR-2 — Stability–Plasticity Capacity Law.**

- If `N_{t+1}=N_t`, the new task is already a function of the retained semantic state and requires zero additional exact semantic capacity.
- If `N_{t+1}>N_t`, the new obligation introduces genuinely new distinctions. Any exact fixed-capacity memory with fewer than `N_{t+1}` states must fail at least one retained/new obligation unless another side channel carries the missing distinction.

Thus “plasticity” costs semantic capacity only when the new task refines what future behavior must distinguish.

### Independent-bit corollary

If task `i` reveals/asks for an independent retained bit, then

\[
N_t=2^t,
\qquad
s_t^*=t.
\]

One exact retained bit of semantic capacity is required per independent binary task.

---

## 4. Architecture-free transfer/redundancy measure

Let

\[
N_i=|Q_i(H)|
\]

be the number of exact response classes required by task `i` alone. Since the joint signature takes values in the Cartesian product,

\[
N_t\le\prod_{i=1}^tN_i.
\]

Define semantic task redundancy/transfer

\[
\boxed{
\mathcal T_t
=
\sum_{i=1}^t\log_2N_i-\log_2N_t
\ge0.
}
\]

**CSR-3 — Semantic Transfer Compression Theorem.** Shared task structure appears as compression of the joint semantic partition relative to independent storage of each task's response state.

- independent task distinctions give `T_t=0`;
- identical or functionally redundant task partitions give positive `T_t`;
- the quantity is architecture-free: it is defined before choosing a neural, symbolic or replay mechanism.

This is not claimed as a complete measure of positive transfer in optimization speed or sample complexity. It is the exact retained-state redundancy component.

---

## 5. Replay/external-memory tradeoff

Suppose future evaluation has access to two jointly designed channels across the past→future cut:

- internal persistent state alphabet `Z`, size `M`;
- replay/external side-information alphabet `R`, size `K`.

The pair `(Z,R)` has at most `MK` distinct values. Exact retention therefore requires

\[
\boxed{MK\ge N_t.}
\]

or in log width,

\[
\boxed{
\log_2M+\log_2K\ge\log_2N_t.
}
\]

**CSR-4 — Replay–Memory Cut Tradeoff.** Internal weights/state and external replay are substitutable only to the extent that their joint channel preserves the required semantic classes.

The cardinality bound is necessary for any fixed channels. It is sufficient when the two channels are jointly designable: injectively encode the `N_t` semantic classes into `Z x R` whenever `MK>=N_t`.

Thus replay does not “magically prevent forgetting”; it supplies side information across the same semantic cut.

---

## 6. Irreversible forgetting theorem

Let a deterministic learning update transform the old persistent state:

\[
Z_{t+1}=U(Z_t,X_{t+1}),
\]

where `X_{t+1}` is the new-task evidence. Consider two old histories `h,h'` that are joint-distinct for retained obligations. If, after conditioning on all future side information available to the system,

\[
Z_{t+1}(h)=Z_{t+1}(h')
\]

and no later observation distinguishes them, then every later deterministic computation receives identical information on the two cases.

**CSR-5 — Irreversible Semantic Merge Theorem.** Once a required retained distinction has been merged across every surviving future channel, exact old-task retention cannot be recovered by subsequent processing alone.

This is a data-processing/no-information-creation result. Replay can repair the loss only if it reintroduces a side signal correlated with the merged distinction.

### Injective preservation corollary

If the update induced on current joint semantic classes is injective and the representation has sufficient states, then all prior task responses remain decodable after the update. Forgetting is therefore not necessary merely because learning is sequential.

---

## 7. Catastrophic forgetting is conditional, not architectural destiny

The theorem gives three qualitatively different regimes.

### Capacity-impossible forgetting

If all available past→future channels jointly have fewer than `N_t` distinguishable states, exact retention is impossible for **every architecture**.

### Update-induced forgetting

Capacity is sufficient, but the actual development/update rule merges obligation-distinct semantic states. Forgetting is a failure of the development law, not an information-theoretic necessity.

### Transfer/no-growth regime

A new task does not refine the joint semantic partition (`N_{t+1}=N_t`). Exact retention and new-task competence require no increase in semantic-state cardinality; a suitable update may reuse existing state.

This separates catastrophic forgetting from the special implementation mechanisms used to address it.

---

## 8. Relation to common continual-learning mechanisms

Within the Grand-GMI typing:

- **replay / generative replay** supplies an external side channel `R`;
- **parameter isolation / expansion** increases the persistent alphabet `M` or changes its resource geometry;
- **regularization / EWC-like methods** constrain the update map in an attempt to preserve old-task distinctions;
- **distillation** transmits old response constraints through current training data/objectives;
- **orthogonalization / pattern separation** changes the representation so new updates are less likely to merge old semantic classes;
- **complementary fast/slow memory** allocates the cut across multiple timescale/substrate channels.

The theorem does not assert any one method is universally optimal. It gives the architecture-neutral obligations each method is trying to satisfy.

---

## 9. Exact finite microscope

`grand_gmi_continual_retention_checks_v1.py` exhausts binary task-response systems on four histories.

Task label universe: all `2^4=16` binary functions.

Sequences:

- length 1: **16**;
- length 2: **256**;
- length 3: **4,096**.

Across every prefix of every sequence (**12,816** prefix states), the joint semantic class count never decreases.

Across task-addition steps:

- **2,900** additions require zero new semantic classes (`N_{t+1}=N_t`);
- **5,548** additions strictly refine the retained partition.

Joint-class distributions:

- two tasks: `N=1:4`, `N=2:84`, `N=3:144`, `N=4:24`;
- three tasks: `N=1:8`, `N=2:392`, `N=3:2,016`, `N=4:1,680`.

Independent brute encoder assault for every length-2 task pair and memory sizes `M=1..4`:

- **1,024** task-pair/memory-size cases;
- exact decoder feasibility agrees with `M>=N_joint` in **1,024/1,024** cases;
- **580** of those cases are feasible.

Irreversible-update witness:

- for four joint semantic classes and four memory states, there are `4^4=256` deterministic update maps;
- exactly `4!=24` are injective and preserve all four classes;
- the remaining **232** merge at least one required distinction and cannot support exact four-class retention without added side information.

Replay product-channel checks verify the necessary/sufficient jointly-designed capacity condition `M*K>=N` for `N=1..8`, `M,K=1..4`.

Aggregate terminal:

`GRAND_GMI_CONTINUAL_RETENTION_TRANCHE_ALL_GREEN`.

---

## 10. Parent subtraction

Continual/lifelong learning, catastrophic forgetting, stability–plasticity, replay, complementary learning systems, regularization and parameter isolation are established research programmes. Modern work provides both empirical methods and mechanism-specific theory, including feature/NTK analyses and information-theoretic replay bounds.

Grand GMI does not claim those methods or observations as inventions.

The residual contribution is the exact architecture-free reduction:

\[
\boxed{
\text{retained obligations}
\to
\text{joint semantic partition }N_t
\to
\text{past→future cut capacity}
\to
\text{required persistent/replay resources}
\to
\text{update injectivity or forgetting}.
}
\]

This gives a common lower-bound language for neural, symbolic, memory-augmented and biological continual learners.

---

## 11. Scope and falsifiers

The exact width theorem is finite and zero-error. Approximate retention should use the existing response metric/covers and declared error criterion rather than naively quotienting by epsilon.

The theorem does not provide universal optimization/sample-complexity rates or say that `log N_t` bits are physically attainable on every substrate; resource realization belongs to `rho` and the physical construction/necessity sandwich.

Direct falsifiers:

1. an exact retention code with fewer than `N_t` joint cut states and no side information;
2. a task addition for which the exact joint semantic class count decreases;
3. jointly designed internal/replay channels with `MK<N_t` that retain all classes exactly;
4. a deterministic update that irreversibly merges two obligation-distinct classes yet later recovers them with no distinguishing side information;
5. a mismatch in the frozen exhaustive receipt.