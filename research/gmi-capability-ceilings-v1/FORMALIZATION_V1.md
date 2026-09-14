# GMI capability ceilings V1 — F2 tranches 1–2

Issue #602, section F2. This unit now closes six **bounded exact ceiling** boxes: internal-state capacity, observation-quotient distinguishability, deterministic communication bandwidth, fixed-architecture precision, finite persistent-update bandwidth, and linear protected-state rank. It remains deliberately narrower than a morphology-to-capability predictor.

## 1. Parent subtraction

These results have strong classical parents, and the GMI claim is not that the underlying counting, quantization, or linear-algebra arguments are new.

- **State capacity.** Myhill–Nerode identifies the minimum number of finite states with the number of future-distinguishable equivalence classes. The repository already derives this specialization from its obligation quotient in `research/machine-intelligence-morphogenesis-v1/GMI_FINITE_STATE_DERIVATION_V1.md`, including an exhibited distinguishing set and matching exhaustive finite machines.
- **Observation quotient.** Blackwell comparison orders information structures by decision value; deterministic coarsening is a special case of garbling. If two latent states are mapped to one complete pre-decision observation, a policy using only that observation cannot condition on which latent state occurred.
- **Communication bandwidth.** Deterministic communication complexity counts transcripts/protocol leaves. A fixed-length `B`-bit one-way protocol exposes at most `2^B` receiver-visible messages.
- **Precision.** Quantization theory studies what finite-precision parameter and arithmetic sets can represent. Importantly, recent expressivity results for quantized networks show why **precision alone cannot be turned into a universal architecture-independent ceiling**: additional width/depth can compensate for low per-parameter precision. The theorem here therefore freezes a one-threshold architecture, its decoder/codebook, and every boundary-selecting precision slot.
- **Update channel.** Finite-alphabet/quantized control and information-constrained optimization study how discrete control/update alphabets restrict reachability or convergence. The result here is the zero-error finite counting specialization: from one fixed persistent state, `A^T` update transcripts cannot select more than `A^T` target-distinct persistent successors if no other target-dependent write channel exists.
- **Protected-state rank.** Rank–nullity gives the exact dimension left after linear protected constraints. Continual-learning methods such as Orthogonal Gradient Descent and later null-space methods exploit the same parent structure: preserve old outputs by restricting updates to an output-insensitive/null subspace.

The residual contribution of this unit is to bind those parent results to the architecture-independent F1 capability interface, state exact scope guards, pair each theorem with a negative twin, and make the tiny finite boundaries executable.

## 2. Common registered scope

A capability ceiling is a tuple

```text
L = (
  information interface,
  mutable/representational interface,
  resource bound,
  obligation quotient,
  error criterion
).
```

These tranches use **finite zero-error** obligations. They do not infer empirical capability scores from morphology and therefore do not reach G6.

All information and mutation channels must be accounted for before applying a ceiling. An uncharged external memory, a later informative probe, a receiver side channel, a task-specific decoder rewrite, or architecture growth is not a counterexample to a frozen-channel theorem; it changes `L`.

## 3. State capacity -> memory ceiling

Let `H` be a finite set of histories and let `~_O` denote obligation equivalence: `h ~_O h'` exactly when no registered continuation requires the machine to distinguish them. Let the quotient contain `K` pairwise distinguishable classes. Suppose that after those histories the machine has only an internal state in a set `Q` with `|Q|=S`, and future observations do not re-separate histories that the internal state has merged.

### Theorem F2-S — state distinction ceiling [P1]

Zero-error satisfaction of all `K` pairwise distinguishable history classes requires

```text
S >= K.
```

**Proof.** If `S<K`, the pigeonhole principle maps two obligation-distinguishable history classes to the same internal state. By distinguishability, there is a registered continuation on which the required responses differ. Starting from the same internal state and receiving the same continuation, the controller produces the same response distribution; it therefore cannot be correct on both classes with probability one. Contradiction. For the finite delayed-label specialization, `S=K` is sufficient by storing the label class directly. QED.

This is the capability-ceiling reading of the existing finite-state derivation, not a new automata theorem. The exact witness exhausts every encoder `K -> S` and decoder `S -> K` for `K=3,S=2` and finds none, then exhibits/exhausts success at `K=3,S=3`.

**Scope guards.** External memory, hidden side channels, or later observations that re-separate merged histories must be incorporated into the information/state object before this theorem is applied.

## 4. Observation quotient -> task distinguishability ceiling

Let a finite latent state `x in X` produce the complete pre-decision observation

```text
O : X -> Z,
```

and let the task require action

```text
g : X -> A.
```

Define observational equivalence by `x ~_O x'` iff `O(x)=O(x')`.

### Theorem F2-O — deterministic observation-fiber criterion [P1]

With no later informative channel, there exists a deterministic zero-error policy `pi:Z->A` satisfying `pi(O(x))=g(x)` for every `x` **iff** `g` is constant on every observation fiber.

**Proof.** Necessity: if `O(x)=O(x')=z`, the policy has only input `z`, so it outputs the same `pi(z)` for both. Hence zero error requires `g(x)=g(x')`. Sufficiency: if `g` is constant on each fiber, define `pi(z)` to be that common action on the fiber. QED.

So the obligation partition may not split an observation class. The maximum number of independently conditionable latent distinctions is bounded by the observation quotient generated by the complete registered information channel.

The hostile witness merges `x0,x1` into `z0` but requires different actions; exhaustive enumeration of every policy over `Z` confirms impossibility. Its negative twin keeps the same observation map but makes the two required actions equal, restoring exact solvability.

**Parent boundary.** Blackwell's theorem is stronger and more general because it compares stochastic experiments across all decision problems. This unit uses only the finite deterministic zero-error specialization needed for a hard F2 ceiling.

## 5. Communication bandwidth -> coordination ceiling

Consider a sender that observes one of `K` registered coordination classes. The receiver has no side information correlated with that class and must produce a distinct matching action. The only channel is a deterministic, noiseless, fixed-length, one-way message of `B` bits.

### Theorem F2-C — transcript-counting coordination ceiling [P1]

Zero-error coordination requires

```text
K <= 2^B,
```

equivalently

```text
B >= ceil(log2 K).
```

The bound is tight.

**Proof.** A `B`-bit message has at most `2^B` values. If `K>2^B`, two sender classes share a transcript. The receiver sees the same transcript and has no correlated side information, so it must choose the same action for both, contradicting the requirement that the classes have distinct matching actions. If `K<=2^B`, assign each class a distinct bit string and decode injectively. QED.

The executable witness exhausts all encoders and decoders for `K=3,B=1` and finds no zero-error protocol, while `K=4,B=2` succeeds. The registered negative twin is `K=5,B=2`.

**Scope guards.** Correlated receiver side information changes the effective coordination classes. Noisy, randomized, variable-length, or interactive protocols require their own registered channel theorem; this unit does not silently extend the fixed-bit one-way result to them.

## 6. Precision -> representable decision-boundary ceiling

Fix ordered probe points

```text
x_1 < x_2 < ... < x_N.
```

A one-dimensional threshold classifier has `N+1` distinct labelings on this probe set: the boundary may lie before `x_1`, between any adjacent pair, or after `x_N`.

Now freeze a threshold architecture whose **only boundary-selecting degree of freedom** is a `B`-bit code `q`, and freeze a decoder

```text
d : {0,...,2^B-1} -> {0,...,N}
```

that maps each code to one of those boundary placements.

### Theorem F2-P — finite-precision threshold-family ceiling [P1]

The number of distinct zero-error threshold boundary placements represented by this fixed decoder is at most

```text
min(2^B, N+1).
```

Therefore representing **every** threshold placement on the probe set requires

```text
2^B >= N+1,
```

equivalently

```text
B >= ceil(log2(N+1)).
```

The bound is tight.

**Proof.** The represented family is the image of `d`. A function from a domain of size `2^B` has image size at most `2^B`, and there are only `N+1` target placements. Hence `|im(d)| <= min(2^B,N+1)`. If `2^B >= N+1`, choose a surjective decoder onto all placements. QED.

The exact witness enumerates every `2`-bit decoder onto the five placements exposed by `N=4`; none covers all five. With `N=3`, the same `2` bits can cover all four placements.

### Why the architecture freeze is load-bearing

This is intentionally **not** the claim that `B`-bit weights impose a universal `2^B` boundary ceiling on arbitrary machines. Quantized-network expressivity work shows that low per-parameter precision can be offset by architecture size and other degrees of freedom. Adding width, adding another precision-bearing parameter, or rewriting the decoder per target supplies new representational resources and moves the system outside this theorem.

The registered F2 precision claim is therefore: *for a frozen boundary-selection interface, precision bounds how many distinct boundary settings that interface can select exactly.*

## 7. Update channel -> plasticity ceiling

Let a machine begin from one fixed persistent state `s_0`. During adaptation it receives at most `T` persistent-update events from an alphabet `U` with

```text
|U| = A.
```

The persistent transition laws may be arbitrary deterministic functions of the current state and the registered update symbol, but **all target-dependent persistent information must pass through those symbols**. Read-only target-independent dynamics are allowed.

### Theorem F2-U — finite update-transcript reachability ceiling [P1]

At most

```text
A^T
```

target-distinct persistent successor states can be selected from `s_0`. Therefore guaranteeing reachability of `K` pairwise target-distinct successors requires

```text
K <= A^T.
```

For `A>1`, equivalently,

```text
T >= ceil(log_A K).
```

The bound is tight whenever the persistent state space can store an injective transcript code.

**Proof.** There are exactly `A^T` length-`T` update transcripts (and no more than that if fewer than `T` events are permitted after padding with a no-op symbol or fixing exact length). Under fixed deterministic transitions and fixed `s_0`, each transcript produces one final persistent state. Hence the image of the transcript-to-final-state map has cardinality at most `A^T`. An injective decoder realizes equality when enough successor states exist. QED.

The exact witness enumerates every transcript decoder for `A=2,T=2`: four binary transcripts cannot cover `K=5` target states, while they can cover `K=4`.

**Scope guards.** A direct parameter write, target-correlated observation that modifies persistent state without being counted, external-memory mutation, or architecture growth is an additional update channel. Stochastic approximate adaptation requires a different error/rate theorem.

## 8. Protected-state rank -> retention/plasticity frontier

Let the registered mutable state be a vector

```text
theta in F^D
```

over an exact field such as the rationals/reals, and let old protected behavior be the linear map

```text
P theta,
```

where `P` has rank `R`.

An update `Delta` has exact zero forgetting on the protected outputs iff

```text
P(theta + Delta) = P theta,
```

equivalently

```text
P Delta = 0.
```

### Theorem F2-R — protected-rank/null-space frontier [P1]

All exact zero-forgetting updates lie in `ker(P)`, so

```text
dim(allowed update space) = D - R.
```

Consequently, if plasticity requires an `S`-dimensional family of linearly independent admissible update directions, exact retention and that plasticity can coexist only if

```text
R + S <= D.
```

The bound is tight.

**Proof.** Exact retention is exactly the homogeneous constraint `P Delta=0`, hence the admissible update space is `ker(P)`. Rank–nullity gives `dim ker(P)=D-rank(P)=D-R`. Any linearly independent plastic family contained in that kernel has size at most `D-R`. Conversely, any basis of the kernel provides exactly `D-R` independent retained update directions. QED.

The witness uses

```text
P = [[1,0,0],
     [0,1,0]]
```

with `D=3`. Its rank is `2`, so exact retention leaves one plastic direction. Two independent plastic directions are impossible without moving a protected output. A redundant-row twin confirms that **rank**, not the raw number of protected equations, is the load-bearing quantity.

This result is complementary to `GMI_INTERFERENCE_STABILITY_PLASTICITY_V1.md`, which derives a frontier in terms of distinguishable-state capacity. Here the carrier is an exact linear mutable space and the protected burden is rank.

**Parent boundary.** Orthogonal/null-space continual-learning methods use this same geometry operationally. For a nonlinear network, replacing `P` by a Jacobian yields only a local/first-order statement unless global invariance is separately proved; this unit does not silently make that escalation.

## 9. Structural and hostile closure

`capability_ceilings_v1.py` validates that all six theorem rows contain scope, assumptions, strongest parent, bound, negative twin, and falsifier. The control suite now has 31 checks and rejects, among other failures:

- G6 claim escalation or omitted theorem rows;
- state claims hiding external memory or future re-separation;
- observation claims omitting later probes/side information;
- communication claims with receiver side information, noise, or randomization;
- precision claims that allow architecture growth, post-hoc decoder rewrites, or hidden precision channels;
- update-channel claims that allow direct writes, external mutation, side channels, or architecture growth;
- protected-rank claims that silently substitute nonlinear/global invariance or auxiliary mutable state for the registered linear fixed-dimensional object;
- floating-tolerance rank ambiguity, by computing witness rank exactly over rational arithmetic.

A `PASS` therefore certifies the **registered finite theorem interfaces and witnesses**, not a general empirical capability predictor.

## 10. Claim ceiling and remaining F2 gaps

Evidence class:

```text
P1 formal theorem family + P2 exhaustive finite witnesses
```

Strongest allowed terminal from the six-row unit:

```text
F2_TRANCHE2_SIX_EXACT_CEILINGS_REGISTERED_AT_G2
```

Still open in #602 F2:

- planning resource -> reachable horizon bound;
- search budget -> reachable verified-solution class;
- verification budget -> admissible false-adoption floor;
- information-acquisition budget -> uncertainty-resolution ceiling;
- social observation -> theory-of-mind identifiability ceiling.

This unit does **not** establish held-family capability prediction, resource-repricing prediction, or the G6 `MORPHOLOGY_TO_CAPABILITY_MAP_SUPPORTED_AT_REGISTERED_SCOPE` terminal.
