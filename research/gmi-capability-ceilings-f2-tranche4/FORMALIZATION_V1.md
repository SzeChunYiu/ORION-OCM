# #602 F2 tranche 4 — information acquisition and social identifiability

This unit supplies the final two bounded F2 ceiling rows. Together with merged #640, #641 and #642, the F2 theorem registry covers all eleven listed capability-ceiling/lower-bound coordinates at **G2**. It still does not establish the **G6** map `Cap(M,E,R,H)`.

## Review split

- **Formal-methods lens:** quantifiers, exact necessity/tightness, counterexamples.
- **Information/resource lens:** count only registered information channels and paid queries.
- **Social-inference lens:** distinguish hidden-model recovery from task-relevant social-response recovery.
- **Adversarial lens:** add free side channels, diagnostic probes or stochasticity one at a time and require the exact theorem either to absorb them explicitly or refuse scope.

## Parent subtraction

### Active information acquisition

The parent is decision-tree / twenty-questions counting. A deterministic depth-`q` decision tree with at most `A` outcomes per query has at most `A^q` leaves. No GMI-specific novelty is claimed for that counting law. GMI's role is to bind it to the registered acquisition-cost coordinate, prohibit free information channels, and state exactly when the bound is merely necessary versus tight.

### Social inference

Inverse-planning and Bayesian theory-of-mind models infer hidden goals, beliefs and related latent states from observed actions by inverting a forward model of agent behavior. The exact impossibility result below is even more basic: it is the previously registered F2 **observation-quotient theorem** specialized to a hidden-agent-model domain. Therefore this row is explicitly a corollary/ownership binding, not an independent theory-of-mind novelty claim.

## F2-I — information-acquisition budget -> uncertainty-resolution ceiling

Let the latent hypothesis set be `H`, `|H|=K`. A deterministic adaptive protocol asks at most `q` active queries. Every query outcome belongs to an alphabet of size at most `A`. All target-dependent information reaches the protocol through the registered query outcomes; there is no unmetered side channel.

### Theorem F2-I [P1]

Every complete `q`-query transcript belongs to a set of size at most `A^q`. Therefore zero-error identification of `K` hypotheses requires

```text
K <= A^q.
```

If `A>1`, equivalently

```text
q >= ceil(log_A K).
```

**Proof.** A depth-zero protocol has one transcript. Each additional query can extend each existing transcript by at most `A` outcomes. By induction, depth `q` has at most `A^q` leaves/transcripts. Zero-error identification requires different hypotheses to terminate in distinguishable transcript leaves, so an injective map from `H` into the leaf set is necessary; hence `K<=A^q`. QED.

Adaptivity does not change the leaf-count upper bound; it changes which question labels appear at internal nodes, not the maximum number of outcome paths.

### Uniform acquisition cost

If every acquired answer costs the same positive integer `c` and total acquisition budget is `B`, then

```text
q <= floor(B/c)
```

and therefore

```text
K <= A^floor(B/c).
```

This is an information ceiling, not a promise that every query family attains it.

### Tightness condition

If the registered query family is rich enough to realize an injective `A`-ary code of length `q` over the `K` hypotheses, then the bound is tight. The executable finite witness enumerates code assignments: four hypotheses fit exactly into two binary answers, while five do not; five fit once a third binary answer is available under the rich-query construction.

**Nearest counterexample when an assumption is removed.** Give the agent one free target-correlated side bit. The total distinguishability can then exceed `A^q`; the theorem has not failed—the information interface was undercounted.

**Non-claim.** For noisy observations or allowed error, Shannon/Fano/Bayesian experimental-design bounds are the appropriate parents; this exact zero-error theorem does not silently extend to them.

## F2-T — social observation -> theory-of-mind identifiability ceiling

Let `Theta` be a finite registered set of hidden agent models. A model may encode goals, beliefs, preferences or another architecture-independent latent agent state. The complete allowed social observation protocol induces a deterministic transcript

```text
tau : Theta -> T.
```

A prospectively frozen held-out social query requires response

```text
g : Theta -> Y.
```

The evaluated machine receives `tau(theta)`, not the hidden label `theta`.

### Theorem F2-T1 — response identifiability [P1]

A zero-error decoder `d:T->Y` satisfying

```text
d(tau(theta)) = g(theta)  for every theta in Theta
```

exists **iff** `g` is constant on every transcript fiber `tau^{-1}(t)`.

**Necessity.** If `theta1` and `theta2` share transcript `t`, then the decoder sees the same input for both and must output one value `d(t)`. Thus zero-error correctness requires `g(theta1)=g(theta2)`.

**Sufficiency.** If `g` is constant on every fiber, define `d(t)` to be that common value for each observed transcript. This is well-defined and correct for every model. QED.

This is exactly the deterministic observation-quotient criterion applied to social observation.

### Corollary F2-T2 — full hidden-model identification [P1]

Full zero-error identification of `theta` is possible iff `tau` is injective. Therefore the number of fully distinguishable hidden-model classes is at most the number of distinct registered transcripts.

### Why response identification is the stronger formulation for capability theory

Full model identity can be unnecessary. Two hidden models may remain observationally merged yet prescribe the same held-out response; the task-relevant social capability is then identifiable even though the latent ontology is not. The executable witness pins this distinction so future work cannot accidentally turn a capability theorem into an unjustified latent-state recovery claim.

### Finite collision witness [P2]

The base world contains three registered hidden models:

```text
goal_left       -> context0:wait
belief_blocked  -> context0:wait
goal_stay       -> context0:go
```

The first two models collide observationally but require different held-out predictions (`left` vs `right`). Exhaustive enumeration finds no transcript-only decoder. A registered diagnostic interaction adds model-separating probe outcomes (`left` vs `right` vs `stay`); the transcript becomes injective and both the held-out response and full model become identifiable.

**Nearest counterexample when an assumption is removed.** Reveal the hidden model label directly, expose private state, or allow a later discriminating probe that was omitted from `tau`. Any of these can restore identifiability, but each changes the registered information interface.

**Non-claim.** Real agents are stochastic and model classes can be misspecified. Approximate Bayesian mental-state inference, posterior calibration and finite-sample identification are empirical/statistical problems beyond this exact deterministic ceiling.

## F2 structural closure at bounded G2

With this tranche, #602 F2 has bounded theorem rows for:

1. state capacity;
2. observation quotient;
3. communication bandwidth;
4. precision under a fixed decoder/architecture;
5. finite update bandwidth;
6. protected-state rank;
7. exhaustive planning resource;
8. unstructured verified-search budget;
9. verification false-adoption budget;
10. active information-acquisition budget;
11. social-observation identifiability.

The common pattern is information/resource **first refusal**: every ceiling names the channel that carries the necessary distinction, meters it, states the strongest parent, gives a negative twin, and refuses hidden channels that would invalidate the bound.

Terminal for the theorem registry only:

```text
F2_ALL_ELEVEN_BOUNDED_CEILINGS_REGISTERED_AT_G2
```

This does **not** imply `MORPHOLOGY_TO_CAPABILITY_MAP_SUPPORTED_AT_REGISTERED_SCOPE`. F4 held-family predictions, perturbation predictions, uncertainty/abstention and real-regime replication remain open.
