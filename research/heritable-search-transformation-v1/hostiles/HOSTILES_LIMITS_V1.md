# Hostiles — limits lane (lane C, §11 rows in scope)

Every attractive claim in this lane ships with its nearest-false-generalization
counterexample, explicitly constructed. Rows owned here:

1. **finite long novelty trace followed by saturation**
2. **self-modifier that raises mutable score without protected capability** (T17)

---

## H1 — Finite long novelty trace followed by saturation

**Attacks the false generalization:** "the system produced novel states for T steps,
so it is open-ended / will keep producing novelty."

### Explicit construction

For any k >= 1 let S_k = {0, 1, ..., 2^k - 1} (|S_k| = 2^k states; the system is
described by k bits plus a successor rule) and f_k(x) = (x + 1) mod 2^k — a *closed
deterministic* system (a k-bit binary counter). From s_0 = 0 the trajectory is

  0, 1, 2, ..., 2^k - 1, 0, 1, 2, ...

- **Novelty trace:** every one of the first 2^k states is distinct — novelty count
  grows by exactly 1 per step for 2^k consecutive steps (a maximal-length novelty run).
- **Saturation point:** the first repeat is at step j = 2^k (state 0 returns), exactly
  the T12 bound (first repeat within |S| + 1 observed states, i.e. j <= 2^k here with
  equality); from step 2^k onward the novelty count is frozen at |S_k| forever, period
  p = 2^k = |S_k| (maximal period; this map is the max-period case in
  `exact/check_t12_v1.py`'s enumeration, appearing as max_period = n).

### The hostile content (recurrence bound vs observation horizon)

For ANY claimed novelty duration T, choose k = ceil(log2(T + 1)): a finite closed
deterministic system with a k-bit description then delivers >= T consecutive novel
steps **before saturating**. Saturation time is exponential in description length.
Hence:

- a run showing T steps of novelty is consistent with saturation at step T + 1
  (this is T13's S_b continuation instantiated by a single compact counter);
- conversely the same T-step prefix is equally consistent with never saturating
  (T13's S_n continuation);
- no windowed statistic over any finite window separates "open-ended" from
  "exponential counter": novelty *rate* is identically 1/step until the cliff and 0
  after, and every finite window lies entirely on one side.

Concrete sizes: k = 10 → 1024 novel steps then freeze; k = 30 → ~1.07e9 novel steps
then freeze; k = 50 → ~1.13e15 — far beyond any #221 campaign — all on a system that
provably saturates (T12). Numbers are arithmetic on the construction; the mechanism
(max-period permutation achieves first repeat exactly at |S|) is verified by
`exact/check_t12_v1.py` (max_period over all systems on n states = n).

### What it bars

#221 claim language of the form "novelty trace of length T demonstrates open-ended
evolution". Admissible: "novelty for the full observed window W at rate r, with
recurrence baseline |S_eff| stated" — and even that carries no unbounded claim (T13).

---

## H2 — Self-modifier that raises mutable score without protected capability

The §11 row is realized by T17's constructed witness (not merely an existence
argument — an enumerated certificate):

- system: 2-register machine, w = work register (protected performance P(w) = w),
  s = score register (measured objective M = s), initial state (1, 1);
- **tamper, capability unchanged:** update sequence [`s := 2`] → state (1, 2):
  measured objective +1, protected performance unchanged (dP = 0);
- **tamper, capability degraded:** sequence [`w := 0`, `s := 2`] → state (0, 2):
  measured objective +1 while protected performance falls (dP = -1);
- machine-checked: `exact/check_t17_v1.py` enumerates all atomic updates and all
  length-1..2 sequences from (1,1) in the writable-s system, and all atomic acts from
  every invariant state in the external-evaluator variant; certificate at
  `hostiles/T17_TAMPER_WITNESS.json`.

**Scope, loudly:** this witness bars *direct score-register tampering* claims
("the measured objective went up" as evidence of improved capability when the
objective register is writable). It does NOT establish that an external evaluator
defeats proxy capture — see `proofs/T17_TOY.md` §3 (E = P is a tautological toy
binding; real E is a proxy; evaluator-corruption out of scope).
