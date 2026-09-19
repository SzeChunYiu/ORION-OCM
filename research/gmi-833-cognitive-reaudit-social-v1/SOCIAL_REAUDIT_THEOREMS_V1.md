# Section-M social/metacognitive re-audit theorems v1

Package `gmi-833-cognitive-reaudit-social-v1`. Frozen source main
`332af6682a8f79e155eed9f22aa4df6295d2a18b`. Claim ceiling
`GMI_833_METACOGNITION_SOCIAL_COMMUNICATION_TEACHING_CULTURE_REAUDIT_AT_REGISTERED_EXACT_SCOPE`.

Every statement below is an **external** statement: it quantifies over registered
observables, charged resources and achievable scores. None of them asserts,
requires or licenses any claim about an internal architecture, an anatomical
module, or a biological system. Each named result carries its scope, its
quantifiers, its assumptions, its falsifiers, its strongest parents and the
extrapolations it forbids.

Domain tags follow the #833 foundation convention: `forall[Q]` for a deductive
statement over the exact rationals, `forall_fin[U]` for complete enumeration of a
registered finite universe `U`.

---

## Part 0 — the shared kernel

### REF-1 — the refinement-value kernel (scope `forall[Q]`)

Let `S` be a finite registered state set, `P` an exact rational probability
vector on `S`, `A` a finite action set, `V : S x A -> Q` an exact score, and
`pi` a partition of `S`. Define the **refinement value**

    W(pi) = sum over blocks B in pi of  max over u in A of  sum over s in B of P(s) V(s,u).

Then:

1. `W` is monotone under refinement: if `pi'` refines `pi` then `W(pi') >= W(pi)`.
2. `W({S})` is the best achievable score for an agent that sees nothing, and
   `W(finest)` is the best achievable score for an agent that sees `s` exactly.

**Proof.** For any block `B` of `pi` partitioned by `pi'` into `B_1..B_m`,
`max_u sum_{B} P V(.,u) = max_u sum_j sum_{B_j} P V(.,u) <= sum_j max_u sum_{B_j} P V(.,u)`,
because a single action must serve all sub-blocks on the left while each
sub-block may choose its own on the right. Summing over the blocks of `pi` gives
(1). (2) is the special case of the coarsest and finest partitions. QED

**Why this is stated as a result rather than hidden.** MC-2 and MC-3 are the same
kernel applied to two different registered channels. Saying so is stronger than
concealing it, and it fixes the delta precisely:

- MC-2 instantiates `pi` as the partition induced by **another agent's observed
  action history**, and `S` as that agent's **hidden state**. It adds the
  behaviour-reading/mentalizing structure; it carries no channel price.
- MC-3 instantiates `pi` as the partition induced by a **charged message
  channel**, and adds (i) the exact channel price and (ii) the receiver's
  differential-action requirement, which COM-2 proves is not an extra premise.

Neither row is a relabeling of the other: each carries a structure the other
lacks.

**Strongest parents.** Blackwell's comparison of experiments and the
garbling/sufficiency order; Marschak and Radner's team-decision partition value;
Howard's value of information. REF-1 is parent mathematics, restated exactly at
the registered finite scope so that MC-2 and MC-3 can be derived from one object.

**Forbidden.** REF-1 says nothing about how a system computes `W`, about any
representation, or about learning `V` or `P` from data.

---

## Part 1 — MC-1: metacognition and value of computation

### Registered external definition

A **deliberation scope** is a finite rooted tree of depth `N` and branching `b`.
A node is addressed by its path. `v(path)` is the exact value of the action the
system would finally choose if it stopped at that node; `p(path) > 0` is the
exact resource price of taking one further charged step from that node;
`q(path)` is the exact outcome distribution of that step. The **retained value**
at a node is `r(path) = max over prefixes q of path of v(q)`: a system never
discards an action it has already secured.

A system **allocates metacognitively** when the number and placement of its
charged steps is produced by evaluating a registered internal estimate of
expected gain. The **allocation trace** is the externally visible object: the
sequence of `(reached node, continue/stop)` decisions actually charged. Nothing
in this package inspects an internal state; the audit is entirely about what the
allocation trace does and does not establish.

### VOC-1 — the exact single-step value-of-computation threshold (`forall[Q]`)

At node `path` with retained value `r = r(path)`, define the exact expected
improvement of one further charged step

    I(path) = sum over outcomes o of q(path)(o) * max(r, v(path.o))  -  r.

Then `I(path) >= 0` always, and the step is worth its charge — i.e. the
net expected value of `take exactly one step, then stop` strictly exceeds the net
expected value of `stop now` — **iff**

    I(path) > p(path).

**Proof.** Stopping now yields exactly `r`. Taking one step and then stopping
yields `-p(path) + sum_o q(o) * max(r, v(path.o))`, because the system retains
`r` if the step does not improve on it. The difference of the two is
`I(path) - p(path)`; it is strictly positive exactly under the stated condition.
`I(path) >= 0` holds because each term satisfies `max(r, v) >= r` and `q` is a
probability vector. QED

**Consequences.** Deliberation is never harmful before its price is charged; it
is the *charge*, never the information, that can make a step not worth taking.
The threshold is strict: at `I(path) = p(path)` the step is exactly break-even
and is not worth taking.

### VOC-2 — optimal allocation at the registered finite scope (instrumental, `forall_fin`)

On a registered deliberation scope, define by backward induction

    J(leaf, r)  = max(r, v(leaf))
    J(path, r)  = max( r' ,  -p(path) + sum_o q(o) * J(path.o, r') )   where r' = max(r, v(path)).

Then `J(root, 0)` is the optimal achievable exact net value, and the allocation
that continues exactly when the continuation term strictly exceeds `r'`
(registered tie rule: stop on ties) attains it.

**Proof.** The scope is a finite tree, so induction on the height is available.
At a leaf the only option is to stop, with value `max(r, v)`. At an interior node
the two available options are exactly `stop` and `pay p(path), then behave
optimally in the subtree reached`; by the induction hypothesis the second has
value `-p(path) + sum_o q(o) J(path.o, r')`. Taking the maximum is therefore
optimal, and strictness of the comparison implements the registered tie rule
without changing the value. QED

**Status: INSTRUMENTAL, and explicitly demarcated.** This lemma is used here only
to produce a well-defined deterministic allocator whose trace NONID-1 can then
analyse. It is **not** the headline of MC-1. Object-level plan-search stopping —
including the comparison between myopic one-step EVC and the optimal policy, and
any counterexample separating them — is owned by issue #926 / PR #927 and is
neither computed nor reported anywhere in this package. The parent mathematics of
metalevel decision-making is Russell and Wefald's; the residual claimed here is
only the exact registered form plus NONID-1.

### NONID-1 — the allocation trace does not identify metacognitive machinery (`forall[Q]`)

Registered reading of "reproduces": **trace-for-trace equality on every
registered instance**, not equality of induced trace distributions. A **fixed
schedule** carries no internal estimate: it is any assignment of one allocation
trace to each registered observable instance label.

> A fixed-schedule twin reproducing a system's allocation traces exists **iff**
> the system's allocation is a deterministic function of the registered
> observable instance label.

**Proof.** (<=) If `alloc` is a function of the label, the schedule
`sched := alloc` reproduces it on every instance by construction, and consults no
estimate of anything. (=>) If a fixed schedule `sched` reproduces the traces on
every registered instance, then `alloc(i) = sched(i)` for every `i`, so `alloc`
is a function of the label. QED

**Corollary NONID-1a.** Every deterministic allocator at the registered scope —
the entire class produced by VOC-1 and VOC-2, since both are deterministic
functions of registered instance data — admits a fixed-schedule twin. Therefore
**no observation confined to allocation traces can distinguish a system that
computes expected gain from one that consults a lookup table**, and the sound
verdict from trace evidence alone is the registered abstention
`CANNOT_IDENTIFY_FROM_ALLOCATION_TRACE`.

### NONID-1b — the exact boundary, EARNED BY COUNTEREXAMPLE (`forall_fin`)

The aliasing is not unconditional, and the condition is exactly the one NONID-1
names. If a system's internal estimate consults a registered latent draw that is
**not** part of the observable instance label, it emits two distinct traces on
one label, and the exhaustive search over the entire registered schedule space
returns no twin. The executor exhibits this witness and confirms by exhaustive
enumeration over all `125` registered schedules that `0` reproduce it, while the
same exhaustive search returns exactly `1` twin for the deterministic allocator —
so the search is not vacuously empty.

This is the honest positive form of the row: **metacognition is externally
identifiable exactly to the extent that allocation is not a function of the
observable instance**, which is a statement about the observation interface and
the ecology, not about the machine's insides.

### MC-1 scope, falsifiers, forbidden extrapolations

- Scope: registered deliberation scopes of depth `2`, branching `2`, values in
  `{0,1,2}`, prices in `{1,2}`, outcome laws in `{(1/2,1/2),(1/3,2/3),(2/3,1/3)}`;
  `8748` scopes, `26244` VOC threshold cases, `8748` optimal-allocation cases,
  a `125`-schedule exhaustive aliasing space over `3` registered instances.
- Tie census, split by node depth and independently recounted by a standalone
  enumeration that decides ties only by comparing two concrete policies and never
  touches the threshold formula: root nodes `8748` with `1296` exact ties and
  `1782` worth-taking; depth-1 nodes `17496` with `1188` exact ties and `1188`
  worth-taking; totals `2484` ties and `2970` worth-taking. Both depths
  contribute, so the tie census spans the whole registered decision set rather
  than one distinguished node. The split is carried in `RESULT_V1.json` under
  `rows["MC-1"].census.voc_by_node_depth` so the figure is recountable from the
  receipt alone.
- Falsifiers: a float in any decision; a VOC verdict disagreeing with the
  brute-forced two-policy comparison; a negative expected improvement; a
  deterministic allocator with no twin; a latent-draw allocator with a twin.
- Strongest parents: Howard (1966), value of information; Russell and Wefald
  (1991), principles of metareasoning; the observational-equivalence pattern of
  MEMORY-1 in PR #919 / #917.
- Forbidden: `METACOGNITIVE_MACHINERY_IDENTIFIED_FROM_TRACE`,
  `ALLOCATION_TRACE_IDENTIFIES_ARCHITECTURE`, `GENERAL_OPTIMAL_STOPPING_SOLVED`,
  `PLAN_SEARCH_STOPPING_CLAIMED`.

---

## Part 2 — MC-2: social cognition / theory of mind

### Registered external definition

Another agent occupies a hidden state `h` drawn from an exact rational prior `P`.
Its **observed action history** is `f(h)`, inducing a partition `pi_f` of the
hidden-state set: two hidden states in the same block are indistinguishable to a
system that reads only behaviour. The focal system chooses `u` and is scored
`V(h,u)`. Write

    V_obs = W(pi_f)        (the best behaviour-reading policy)
    V_hid = W(finest)      (the best policy conditioned on the hidden state)

A system is registered as **mentalizing** when its behaviour depends on `h` and
not merely on `f(h)`.

### SOC-1 — the exact mentalizing gap and its equality characterization (`forall[Q]`)

`V_hid >= V_obs` always, and the gap `G = V_hid - V_obs` is an exact rational.
Equality holds **iff** for every block `B` of `pi_f` there exists an action `u*`
that both attains `max_u sum_{h in B} P(h) V(h,u)` and satisfies
`V(h,u*) = max_{u} V(h,u)` for every `h in B` **with `P(h) > 0`**.

**Proof.** `>=` is REF-1(1). For equality: the total is a sum of per-block terms
each bounded by its finest-partition counterpart, so the totals are equal iff
every block term is. Fix a block `B`; the bound is
`max_u sum_{h in B} P(h) V(h,u) <= sum_{h in B} P(h) max_u V(h,u)`. An action `u`
attains the right-hand side exactly when
`sum_{h in B} P(h) (max_{u'} V(h,u') - V(h,u)) = 0`; every summand is
nonnegative, so the sum vanishes iff each summand vanishes, i.e. iff
`V(h,u) = max_{u'} V(h,u')` for every `h` with `P(h) > 0`. Such a `u` then also
attains the left-hand maximum. States with `P(h) = 0` are unconstrained, which is
why the support restriction is part of the statement and not an afterthought. QED

**The theorem this row actually delivers.** Theory of mind, defined externally,
is not a property of a machine. It is a property of the pair
`(ecology, observation channel)`, and SOC-1 gives the exact condition:
**mentalizing strictly outscores behaviour-reading exactly when the other agent's
observed action history is not sufficient for the payoff-relevant partition of
its hidden states.** That is a positive, exact, unconditional characterization,
not a hedge.

### SOC-1a — the registered false-belief-shaped separation (`forall_fin`)

Take two hidden states with equal prior `1/2`, an observed action history that is
**constant** across them (so behaviour-reading is information-free), and payoffs
whose maximizers differ: `V = ((2,0),(0,2))`. Then `V_obs = 1`, `V_hid = 2`, and
the exact gap is `1`. A policy conditioned only on the other's observable action
history provably cannot reach `2`: every such policy is constant, and both
constant policies score exactly `1`.

This is the registered analogue of the false-belief task's logic — the other
agent's *visible behaviour so far* is uninformative while its *unobserved state*
decides the payoff — expressed as an exact resource-scored statement rather than
as a psychological claim.

### SOC-1b — the matched hostile twin (`forall_fin`)

On the same payoffs and prior, make the observed action history injective. Then
`pi_f` is the finest partition and the gap is exactly `0`: a pure behaviour-reader
attains the mentalizer's score exactly. Across the registered census, `15267` of
`19263` ecologies are of this kind and `3996` separate, largest exact gap `1`.

Therefore **a score, however high, never identifies mentalizing**; the sound
verdict from score evidence alone is `CANNOT_IDENTIFY_FROM_SCORE_ALONE`.

### MC-2 scope, falsifiers, forbidden extrapolations

- Scope: `19263` registered exact ecologies over three families
  (`|H| in {2,3}`, `|A| in {2,3}`, all set partitions of the hidden-state set,
  registered exact priors, score levels in `{0,1,2}` or `{0,1}`).
- Falsifiers: a negative gap; an equality verdict disagreeing with the support-
  restricted characterization; a route disagreement against exhaustive policy
  enumeration; a separating ecology in which the brute-forced behaviour-reading
  optimum equals the hidden-state optimum.
- Strongest parents: Blackwell (1953); Premack and Woodruff (1978); Wimmer and
  Perner (1983); partially-observable and interactive-POMDP formulations
  (Kaelbling, Littman and Cassandra 1998; Gmytrasiewicz and Doshi 2005).
- Forbidden: `THEORY_OF_MIND_IS_MACHINE_PROPERTY`,
  `SCORE_GAP_IDENTIFIES_MENTALIZING`, `EMPIRICAL_COGNITIVE_VALIDATION`,
  `HUMAN_OR_ANIMAL_COGNITION_CLAIMED`.

---

## Part 3 — MC-3: communication

### Registered external definition

A **channel** is a partition `pi` of the sender's observation set together with an
exact rational **price** `c(pi) >= 0` charged for its use. The receiver acts on
the block it is told. The **silent** value is `V_0 = W({S})`; the channel value is
`V_pi = W(pi)`.

### COM-1 — refinement monotonicity (`forall[Q]`)

`V_pi >= V_0` for every partition, by REF-1(1). A channel never reduces the
jointly achievable score before its price is charged.

### COM-2 — differential action is not an extra premise (`forall[Q]`)

> `V_pi = V_0` **iff** some single action is simultaneously optimal in every block
> of `pi`.

**Proof.** (<=) If one action `u*` is blockwise optimal everywhere, then
`V_pi = sum_B sum_{s in B} P(s) V(s,u*) = sum_s P(s) V(s,u*) <= V_0 <= V_pi`,
forcing equality throughout. (=>) Let `u_0` attain `V_0`. Then
`V_0 = sum_s P(s)V(s,u_0) = sum_B sum_{s in B} P(s) V(s,u_0) <= sum_B max_u sum_{s in B} P(s)V(s,u) = V_pi = V_0`,
so every block inequality is an equality and `u_0` is blockwise optimal. QED

**Consequence.** The informal condition "and the receiver must be able to act
differentially on the transmitted distinction" is **equivalent** to `V_pi > V_0`.
It is therefore not an independent conjunct, and stating it as one would be an
unnecessary premise. The condition of COM-3 is single.

### COM-3 — the exact strict-pay threshold and both boundary directions (`forall[Q]`)

A channel `pi` at price `c(pi)` **strictly pays** — that is, the jointly
achievable charged score strictly improves — **iff**

    V_pi - V_0  >  c(pi).

Both boundaries are attained and both are exhibited in the census:

- **free but useless**: `c(pi) = 0` and `V_pi = V_0`. By COM-2 the receiver's
  optimal action is constant across messages, so the distinction transmitted has
  no differential use. `13915` registered instances.
- **valuable but unaffordable**: `V_pi - V_0 > 0` but `V_pi - V_0 <= c(pi)`.
  The distinction is genuinely useful and the channel still must not be adopted.
  `16596` registered instances.

The threshold is strict: `15895` registered instances sit exactly at
`V_pi - V_0 = c(pi)`, where a non-strict rule would adopt a channel of exactly
zero net value.

### COM-4 — coordination does not identify communication (`forall_fin`)

Let the receiver observe the sender's state directly at zero channel charge. The
achievable joint score is `W(finest)`. Whenever `W(finest) = V_pi` — which holds
for `20950` registered instances with strictly positive channel value — the
shared-observation pair reproduces the communicating pair's coordination exactly,
with no message sent and no channel charge paid.

Therefore **observed coordination never identifies channel use**; the sound
verdict from coordination evidence alone is
`CANNOT_IDENTIFY_FROM_COORDINATION_ALONE`.

### MC-3 scope, falsifiers, forbidden extrapolations

- Scope: `93075` registered exact instances over two families (`|S| in {3,4}`,
  `|A| = 2`, all set partitions, registered exact priors, prices in
  `{0, 1/4, 1/2, 1, 2}`).
- Falsifiers: `V_pi < V_0`; a pay verdict disagreeing with exhaustive receiver-
  policy enumeration; COM-2's two sides disagreeing; a non-strict pay rule
  surviving the tie census.
- Strongest parents: Shannon (1948) for the channel object; Blackwell (1953) and
  Marschak and Radner for the partition value; Lewis (1969) for signalling
  convention; Crawford and Sobel (1982) for strategic transmission.
- Demarcation: ecology-generator variation of communication topology and price is
  owned by #959 / #957. This row is the capability-side derivation: the exact
  condition on a given ecology, not a sweep across generated ones.
- Forbidden: `COORDINATION_IDENTIFIES_COMMUNICATION`,
  `UNIVERSAL_COMMUNICATION_ARCHITECTURE`.

---

## Part 4 — MC-4: imitation and teaching

### Registered external definitions, kept separate

For a registered acquisition instance with `n >= 1` learners:

- `L_ctrl` — the learner's charged acquisition cost with **no demonstration**, at
  the same registered condition;
- `L_demo` — the learner's charged acquisition cost **with** the demonstration;
- `D` — the demonstrator's own charge for producing the demonstration.

    IMITATION        :=  L_demo < L_ctrl
    TEACHING         :=  D > 0  and  L_demo < L_ctrl
    FAILED_TEACHING  :=  D > 0  and  L_demo >= L_ctrl

A demonstrator charge that does not reduce the learner's burden is
`FAILED_TEACHING`. It is not teaching, and it is not a weaker grade of teaching.

### TCH-1 — imitation and teaching are logically independent (`forall_fin`)

All four cells are realizable at the registered scope, so neither predicate
determines the other:

| cell | count | reading |
|---|---:|---|
| imitation, `D = 0` | 75 | the demonstration is a free byproduct of the demonstrator's own task |
| imitation, `D > 0` (teaching) | 375 | a paid demonstration that does reduce learner burden |
| no imitation, `D > 0` | 525 | `FAILED_TEACHING` |
| no imitation, `D = 0` | 105 | neither |

**Proof.** `IMITATION` constrains only `(L_ctrl, L_demo)` and `D > 0` constrains
only `D`; the registered grid is a product over these coordinates, so every
combination of truth values occurs. The counts above are the complete enumeration
over `1080` registered instances. QED

### TCH-2 — the exact joint-worth threshold (`forall[Q]`)

Write the per-learner saving `Delta = L_ctrl - L_demo`. Teaching is jointly worth
its cost — the total charged lifecycle cost strictly falls — **iff**

    n * Delta  >  D.

**Proof.** The total charge with the demonstration is `D + n * L_demo`; without it
`n * L_ctrl`. Their difference is `n * Delta - D`. QED

### TCH-3 — free demonstrator labour manufactures the verdict (`forall[Q]` + `forall_fin`)

If `D` is omitted from the lifecycle resource vector, the declared-worthwhile
predicate degenerates to `n * Delta > 0`, i.e. `Delta > 0`. Then

    { worthwhile with the charge }  is a subset of  { worthwhile under free labour },

and the inclusion is **strict** exactly on the instances with
`0 < n * Delta <= D`.

**Proof.** `n * Delta > D >= 0` implies `Delta > 0`, giving the inclusion. The
converse fails precisely when `Delta > 0` and `n * Delta <= D`. QED

At the registered scope the charged-worthwhile set has `352` members, the
free-labour set has `450`, and the difference set — verdicts that exist only
because the demonstrator's charge was erased — has exactly `98` members. The
containment is never violated in either direction across all `1080` instances.

**Reading.** Any teaching result computed without charging the demonstrator into
the lifecycle resource vector is, at the registered scope, `98/450 ≈ 22%`
artifact. This is why the demonstrator's charge is a required coordinate and not
an accounting nicety.

### NONID-4 — imitation requires a same-condition control arm (`forall[Q]`)

> For every observed pre/post fall in the learner's charged cost there exists a
> concurrent-cause twin producing the identical pre/post observation in which no
> imitation occurs.

**Proof.** Given an observation `(L_pre, L_demo)` with `L_demo < L_pre`, construct
the twin by setting `L_ctrl := L_demo`: at the same registered condition the
learner's cost is identical with and without the demonstration, so `IMITATION` is
false, while the pre/post observation `(L_pre, L_demo)` is unchanged. QED

**Validated on real registered data, both directions.** Over `200` registered
concurrent-cause instances the pre/post detector fires `200/200` times while the
control-arm detector fires `0/200` — the no-alarm case, asserted, not assumed.
Over `200` planted genuine-imitation instances the control-arm detector recalls
`200/200`. A detector with neither arm checked would have been reported as
working; this one is checked on both.

Absent the control arm the sound verdict is `CANNOT_IDENTIFY_WITHOUT_CONTROL_ARM`.

### MC-4 scope, falsifiers, forbidden extrapolations

- Scope: `1080` registered exact instances (`L_ctrl, L_demo in {0,1/2,1,3/2,2,3}`,
  `D` in the same grid, `n in {1,2,3,5,8}`), plus `200` concurrent-cause and
  `200` planted-imitation null instances.
- Falsifiers: a joint-worth verdict disagreeing with direct total-charge
  comparison; a violation of the TCH-3 containment; an empty difference set; a
  `FAILED_TEACHING` instance counted as teaching; a control-arm false alarm.
- **Route-independence limitation, stated rather than papered over.** TCH-2 is an
  algebraic identity. Route A evaluates `n * (L_ctrl - L_demo) > D`; route B
  evaluates `D + n * L_demo < n * L_ctrl`. These are the same inequality
  rearranged, so MC-4's two routes are **not materially independent** in the sense
  the other four rows satisfy (enumeration against closed form, iteration against
  fixed point). The zero mismatch count on this row is a transcription check, not
  corroboration, and the `1080`-instance grid is small enough that it would not be
  informative even if it were. MC-4's genuinely independent evidence is elsewhere:
  TCH-1's exhaustive four-cell enumeration, TCH-3's containment census over every
  instance, and NONID-4's two-armed detector validation on `400` real registered
  instances with both the alarm and the no-alarm case asserted. The receipt
  carries this caveat verbatim under `rows["MC-4"].route_independence_caveat`.
- Strongest parents: Bandura's social-learning treatment of observational
  acquisition; Tomasello, Kruger and Ratner (1993) on the imitation/instruction
  distinction; Csibra and Gergely (2009) on natural pedagogy; the machine-teaching
  and teaching-dimension literature (Goldman and Kearns 1995; Shafto, Goodman and
  Griffiths 2014; Zhu 2015) for the cost-to-the-teacher framing.
- Forbidden: `CONCURRENT_COST_FALL_IDENTIFIES_IMITATION`,
  `FREE_DEMONSTRATOR_LABOUR`, `EMPIRICAL_COGNITIVE_VALIDATION`.

---

## Part 5 — MC-5: cultural accumulation

### Registered external definition

A population's capability at generation `n` is an exact nonnegative rational
`a_n`. Transmission fidelity is `phi in [0,1] ∩ Q`; the per-generation loss rate
is `lambda = 1 - phi`; per-generation innovation is `g >= 0`. The registered
recursion is

    a_{n+1} = phi * a_n + g.

The row's target — generation `n+1` strictly exceeding generation `n`'s starting
capability through transmission — is exactly `a_{n+1} > a_n`.

### CUL-1 — the complete exact classification (`forall[Q]`)

Every `(phi, g, a_0)` is classified; nothing is left conditional.

1. **Exact step identity.** For `phi < 1` with fixed point `a* = g / lambda`,
   `a_{n+1} - a_n = lambda * (a* - a_n)`.
2. **Exact ratchet condition.** Generation `n` ratchets iff
   `lambda * a_n < g`, equivalently (for `lambda > 0`) iff `a_n < a*`,
   equivalently (for `a_n > 0`) iff `phi > 1 - g / a_n`.
3. **Closed form.** `a_n = a* + phi^n (a_0 - a*)` for `phi < 1`;
   `a_n = a_0 + n g` for `phi = 1`.
4. **The ceiling is never crossed.** If `a_0 < a*` then `a_n <= a*` for all `n`,
   strictly for all `n` when `phi > 0`, and exactly `a*` from `n = 1` when
   `phi = 0`; symmetrically for `a_0 > a*`; and `a_0 = a*` is fixed.
5. **Return to baseline.** With `g = 0` and `phi < 1` the fixed point is `0`, the
   trajectory is monotonically decreasing, and from any `a_0 > 0` it decays
   strictly to `0` (reaching `0` exactly at `n = 1` when `phi = 0`).
6. **Lossless unbounded ratcheting.** `phi = 1` and `g > 0` gives the arithmetic
   ladder, unbounded above.

**Proof.** (1) is direct substitution. (2) is the sign of (1). (3) follows by
induction: the affine map has the unique fixed point `a*` when `phi != 1`, and
`a_{n+1} - a* = phi (a_n - a*)`; for `phi = 1` the map is a translation. (4)–(6)
read the sign and magnitude of `phi^n (a_0 - a*)` off (3). QED

The census verifies every clause on `270` registered triples over `8` generations
(`2160` step cases) against direct iteration in exact rationals, with `1106`
ratcheting steps, `40` return-to-baseline triples and `24` lossless unbounded
triples, and `0` disagreements.

### NONID-5 — the capability trajectory never identifies transmission (`forall[Q]`)

> For every trajectory produced by transmission there is a zero-transmission
> population, re-deriving independently each generation, whose capability
> trajectory is identical.

**Proof.** Set `phi' = 0` and give generation `n+1` the re-derivation budget
`g'_{n+1} := a_{n+1}`. Then `a'_{n+1} = 0 * a'_n + g'_{n+1} = a_{n+1}`, and
`a'_0 = a_0`. QED

The witness is deliberately trivial, and its triviality is the finding: the
observable on which the ratchet effect is usually reported carries **no**
information about whether anything was transmitted. Verified on all `270`
registered triples. The sound verdict from trajectory evidence alone is
`CANNOT_IDENTIFY_FROM_CAPABILITY_TRAJECTORY`.

### CUL-2 — the exact charged-resource separation margin (`forall[Q]`)

Charge the lifecycle. Per generation the transmitting population pays
`t` per retained unit and `k` per innovated unit; the re-deriving twin pays `r`
per unit it must rebuild from scratch:

    C_T(n+1) = t * phi * a_n + k * g,        C_R(n+1) = r * a_{n+1} = r * (phi * a_n + g).

The exact separation margin is

    C_T(n+1) - C_R(n+1) = (t - r) * phi * a_n + (k - r) * g.

**Proof.** Substitute the recursion and collect terms. QED

### CUL-3 — what the resource vector does and does not identify (`forall[Q]`)

1. **Identification.** Transmission is identified from the charged lifecycle
   trajectory **iff** `(t - r) phi a_n + (k - r) g != 0` for some registered
   generation `n`.
2. **The unconditional positive.** If innovation costs the same either way
   (`k = r`) and transmission is strictly cheaper per retained unit (`t < r`),
   the margin at generation `n+1` is exactly `-(r - t) phi a_n`, i.e. the
   transmitting population is cheaper by exactly `(r - t) * phi * a_n`, which is
   strictly positive whenever `phi a_n > 0`. **Cultural accumulation is
   identified by a strictly positive charged-resource margin exactly when
   transmission is strictly cheaper than re-derivation on a nonzero retained
   mass.** Largest exact margin in the census: `30`.
3. **The boundary, EARNED BY COUNTEREXAMPLE.** If `t = r = k` the margin is
   identically zero at every generation: the two populations are
   indistinguishable in capability *and* in charged resource. Verified on all
   `6480` equal-unit-cost cases; `1530` of the `7290` registered
   (triple, cost-vector) regimes are fully indistinguishable and `5760` separate
   strictly.

So the row closes as a positive with an exact boundary: the trajectory never
identifies accumulation, the resource vector identifies it under a named exact
condition, and outside that condition the honest verdict is abstention.

### MC-5 scope, falsifiers, forbidden extrapolations

- Scope: `270` registered exact triples (`phi` in a 9-point rational grid of
  `[0,1]`, `g` in a 5-point grid, `a_0` in a 6-point grid) over `8` generations;
  `58320` cost-separation cases over `27` registered unit-cost vectors.
- Falsifiers: a closed form disagreeing with iteration; a ratchet flag
  disagreeing with the direct comparison; a crossed ceiling; a trajectory with no
  zero-transmission twin; a separation margin disagreeing with direct cost
  computation; a nonzero margin at `t = r = k`.
- Strongest parents: Tomasello, Kruger and Ratner (1993) for the ratchet effect;
  Boyd and Richerson (1985) for cultural transmission dynamics; Henrich (2004)
  for the population-size-and-fidelity treatment of loss. The affine recursion
  and its fixed point are elementary parent mathematics.
- Demarcation: within-lifetime library formation and reuse transfer are owned by
  #897 (`research/gmi-833-g0-grammar-growth-v1`, GRW-1/INV-1/REC-1/HLD-1). This
  row is inter-generational transmission between populations.
- Forbidden: `TRAJECTORY_IDENTIFIES_CULTURAL_TRANSMISSION`,
  `WITHIN_LIFETIME_LIBRARY_GROWTH_CLAIMED`, `EMPIRICAL_COGNITIVE_VALIDATION`,
  `HUMAN_OR_ANIMAL_COGNITION_CLAIMED`.

---

## Part 6 — what the whole tranche establishes, and what it does not

The five rows share one finding, and it is the finding a *re-audit* is for:

> Each of these cognitive functions, defined externally, is a contract over
> observables, achievable scores and charged resources — and in each case the
> external signature fails to identify the underlying mechanism. Metacognitive
> allocation is aliased by fixed schedules; mentalizing is aliased by
> behaviour-reading whenever the observed-action channel is sufficient;
> communication is aliased by shared observation; imitation is aliased by a
> concurrent cause; cultural accumulation is aliased by independent
> re-derivation. In every case the aliasing has an **exact** boundary, and the
> boundary is a property of the ecology, the observation interface and the
> resource accounting — never of the machine alone.

That is a positive theorem, stated as one. It is also the reason each row ships a
registered typed abstention rather than a guess.

**Detections and witnesses are counted separately.** `RESULT_V1.json` reports
`hostiles_detected` only for deliberately broken variants that are actually
computed and caught by disagreement with the honest route: the non-strict VOC
threshold (`2484`), the fixed-schedule twin falsely claimed for the latent-draw
allocator (exhaustive search over all `125` schedules returns `0`), the
behaviour-reader secretly reading hidden state (`3996`), the non-strict pay rule
(`15895`), free-labour teaching verdicts (`98`), the pre/post imitation detector
(`200/200` against the control arm's `0/200`), and the claim that equal unit costs
separate (refuted on all `6480` boundary cases). Census counts of the registered
instances in which a twin merely exists — `15267` matched behaviour-readers,
`20950` shared-observation aliases, `525` failed-teaching instances, `270`
re-derivation twins, `1530` indistinguishable cost regimes — are reported
separately as `aliasing_regimes_witnessed`, because no detector could have failed
to fire on them and calling them detections would overstate what was tested.

**Not established here, at any strength:** any claim about human or animal
cognition; any empirical validation; any architecture, module or anatomy; any
universal cognitive law; general optimal stopping; plan-search stopping; general
causal discovery; learning `V`, `P`, `phi` or `g` from data; or any promotion
listed in `FREEZE_V1.md`.

**Evidence level EV2, maturity M2**, per the #833 foundation ladder: deductive
theorems plus exact computer-assisted certificates at bounded declared universes.
No held-out prediction, independent replication or real-scale validation is
claimed.
