# Known-family mechanisms: premises, derivations and remaining identification

Status: conditional consequences of explicit task/interface assumptions, not unique derivations of branded architectures.
The architectural families below organize the consequences after derivation; their names are not premises of the affine compiler or memory law.
Primary references and adopted-versus-synthesized attribution are in [sources](ECOLOGY_SOURCES.md).
The full statements are [ecology E1–E5](ECOLOGY_LAWS.md) and [memory M1–M6](MEMORY_SELECTION.md).

## Feedforward networks / MLP

If every operation is affine and their wiring is fixed, any finite composition remains affine: (Ax+b) followed by (Cx+d) equals CAx+Cb+d.
Consequently an exactly nonaffine obligation cannot be met by that restricted operation class; a nonlinear primitive, branch or other richer representation is necessary.
For Boolean input, a constructive threshold-network representative exists: for pattern a∈{0,1}^d, its exact indicator is

    q_a(x)=1{Σ_{i:a_i=1}x_i + Σ_{i:a_i=0}(1−x_i) ≥ d}.

Exactly one q_a is 1, so any Boolean truth table f is f(x)=Σ_a f(a)q_a(x).
This uses at most 2^d detectors and O(d2^d) elementary work/storage; it is a realization, not an efficient universal learning algorithm.
Thresholds, affine primitives and finite truth-table access are supplied; acquisition of the table is charged.
Decision trees and symbolic disjunctions implement the same function. The obligation does not force a neural representation, depth, width, smooth activation, gradient training, or generalization outside the table.
Cybenko's continuous approximation result is an established alternative with its own supplied activation/compact-domain assumptions.

## Convolution / CNN

Affine obligations, cyclic translation equivariance and k allowed offsets force exactly y_o=b+Σ_{r∈K}a_r x_{o+r} by E1–E4.
There are k+1 independent coefficients and a direct nk-multiply realization on n positions.
If sharing is imperfect, E5 gives its exact squared-bias penalty and a sample/resource crossover against unrestricted coefficients.
Padding, noncyclic boundary conditions, channels, pooling, nonlinear activations and layer composition must each be specified and proved separately.
This derives shared local affine computation; a stencil program and a convolutional layer are equivalent representatives for that obligation.

## Recurrence / RNN

For a sequential task with N finite future-distinguishable residual behaviors, M6 requires at least N retained states, or ceil(log₂N) bits.
Define the residual after history h as the function mapping each admitted continuation to its required future outputs.
Equal residuals have equal immediate outputs and equal residuals after each next input; therefore transition by appending an input is well-defined on the quotient.
This constructs a recurrent finite controller if the quotient and transitions are effectively obtainable.
A finite-state table, symbolic rules or a recurrent neural encoding can realize it; a fixed finite horizon also admits an unrolled realization with its own code/state charges.
The state lower bound does not force real-valued hidden vectors, a neural transition map or backpropagation through time.

## Gated persistent memory / LSTM

Suppose a payload c and proposed new value z must satisfy HOLD and WRITE commands g∈{0,1}:

    U(c,0,z)=c,     U(c,1,z)=z.

On this command domain, necessarily U(c,g,z)=(1−g)c+gz. A conditional branch, multiplexer or arithmetic gate realizes the same update.
RESET can be added by specifying a third command returning zero; the selector implementation must then preserve these three cases.
This derives command-controlled retention and replacement, rather than sigmoid/tanh gates, learned controllers or the full LSTM cell.
For a leaky alternative c_{t+1}=f c_t with fixed 0≤f≤1 and no write, c_L=f^L c_0.
Retaining at least fraction 1−ε of the amplitude after L≥1 steps requires f≥(1−ε)^(1/L); exact retention for nonzero payload requires f=1.
For prescribed HOLD independent of c, the payload Jacobian is exactly 1 and its product over time is 1.
If a gate depends on c, its derivative contributes additional terms: no unconditional claim about the full LSTM Jacobian follows.
Finite precision, disturbance and memory refresh require additional models; identity algebra alone does not guarantee physical stability.

## Content selection / attention / Transformer

An exact task returning the value at a query-selected record requires dependence on that record wherever its value can vary independently.
A dictionary lookup, equality branch or content-weighted aggregate can supply it; the task does not identify attention uniquely.
Consider specifically one softmax-weighted average of n≥2 arbitrary values in [0,1], with correct logit Δ above every equal distractor logit.
The correct weight is w*=1/[1+(n−1)e^(−Δ)]. The worst absolute error relative to the selected value is exactly 1−w*.
Proof: the error is Σ_{j≠*}w_j(v_j−v*); its absolute value is at most Σ_{j≠*}w_j, attained by v*=0 and every distractor 1.
For 0<ε<1 this error is at most ε exactly when

    Δ ≥ log((n−1)(1−ε)/ε).

If each distractor is at least Δ below the correct logit, the same expression is a sufficient worst-case bound, attained when all gaps equal Δ.
At finite logits the single convex average cannot exactly retrieve arbitrary continuous values for n≥2.
This counterexample does not cover hard selection, binary thresholded decoding, several heads or a downstream correcting program.
Positional codes, residual connections, normalization, feedforward blocks, head count and learned query/key maps are independent identifying premises of a Transformer.

## Conditional computation / mixture of experts

Let X_1,…,X_n be independent fair bits, and let J be independent of those bits with positive probability for every index; the task is to return X_J exactly, with no other X-dependent side information.
An oblivious fixed read set independent of J and X must contain all n inputs: otherwise an omitted requested bit can be flipped without changing the view.
With an admitted random-access interface, the index-dependent program reads just X_J once.
Thus the interface/task can force conditional data access when the allowed external-read count is below n.
Without constant-time addressing, computing and following the address has an additional cost; a bounded-fanin circuit has its own different depth/work model.
This derives routing or a multiplexer. Neural experts, soft mixtures, top-k approximation and load-balancing penalties are not determined by the obligation.
M1–M4 extend the comparison to coded retained information and acquired reuse, rather than treating expert inputs as free.

## Graph computation / GNN

Permutation-equivariant affine maps on n scalar node values have the shared local-plus-global-sum form in E4 when every permutation is admitted.
A fixed graph's automorphism group generally yields a different orbit basis; graph-valued inputs require the actual action on edge/tensor indices.
Separately, in a synchronous graph with only neighbor communication, information at node v after t rounds depends only on initial data in B_t(v).
Proof: at t=0 the view is local; one round combines views of adjacent nodes, enlarging the dependency set by at most one edge.
Let independent fair bits reside at the n nodes, J be uniform and independent, and v be required to output X_J with J available.
With no X-dependent side information or long-range access, any t-round algorithm has error at least

    [1−|B_t(v)|/n]/2.

On the event J∉B_t(v), the target is an independent fair bit conditional on the view, so even a randomized response has conditional error 1/2.
This forces additional communication radius, another memory/access interface, or relaxed error. It does not uniquely specify a message-passing neural network.
Relabeling symmetry alone does not establish expressivity beyond the known limitations of a chosen aggregation scheme.

## Bayesian systems

For a finite hypothesis set, supplied prior π(h), likelihood P(e|h) and positive evidence probability, conditioning forces π(h|e)=π(h)P(e|h)/Σ_uπ(u)P(e|u).
For predicting H after evidence e under expected log loss, this posterior is the unique minimizing distribution: cross-entropy equals posterior entropy plus KL divergence.
If the admitted evidence law factors P(e_1,…,e_T|h)=∏_tP(e_t|h), posterior log odds are prior log odds plus Σ_t log likelihood ratios.
Thus the factorization yields additive sufficient evidence updates; duplicating perfectly correlated evidence violates that factorization and cannot be justified as a second independent update.
The prior, hypothesis semantics, likelihood correctness and computable normalization remain premises. A Bayesian network's graph requires warranted conditional independences.

## Nearest-neighbor / kNN

Assume a supplied metric d and an L-Lipschitz regression function f. At query x, the noiseless nearest observed label satisfies |f(x_near)−f(x)|≤L d(x_near,x).
For k selected neighbors within radius r_k and labels Y_i=f(x_i)+η_i, suppose selection uses positions only and conditional noises are independent, mean zero, variance at most σ².
The equal-weight prediction has conditional squared bias at most L²r_k² and variance at most σ²/k; hence MSE≤L²r_k²+σ²/k.
Proof: average the k Lipschitz deviations for the bias; independence removes cross terms from the noise average.
This exhibits a locality-versus-noise tradeoff. It does not derive the metric, sample coverage, optimum k, a search index, or a unique neighbor learner.
Correlated label noise removes the σ²/k guarantee; poor coverage keeps the bias term large. Search/acquisition/storage are charged separately.

## Symbolic structures

Finite truth-table synthesis above and finite residual quotients construct explicit executable rules from complete observations under their stated assumptions.
A decision tree represents a Boolean truth table by testing coordinates successively; equivalence follows by following the branch matching each assignment.
Worst-case depth is d and a complete tree has 2^(d+1)−1 nodes. Compact rules require additional regularity or a discovered reusable decomposition.
These are symbolic realizations with exact operational semantics; they do not establish informal meaning, the truth of imported axioms, or unrestricted theorem discovery.

## Retrieval-augmented generation / RAG

For the independent-bit knowledge workload, M2 forces r_query≥1−Σ_{i≤M}p_(i), and M4 identifies the exact best acquisition/retention/probe tradeoff.
When the required exact answers cannot fit in retained state, an admitted external-access mechanism is necessary for some queries.
This derives retrieval pressure and a workload-dependent cache frontier; a lookup table already attains the specified information/probe law.
A language generator, retrieval relevance, semantic grounding and factual correctness of a corpus require separate assumptions and tests.
Lewis et al.'s neural retrieval/generation architecture is a parent comparator; this information law does not derive its encoder or generator.

## Planning

For finite states/actions, supplied transition kernel P, bounded stage rewards r_t and finite horizon H, set V_H(s)=terminal_reward(s).
Then backward conditioning gives

    V_t(s)=max_a [r_t(s,a)+Σ_{s'}P(s'|s,a)V_{t+1}(s')].

Induction proves optimality: every policy's first action yields at most the displayed continuation value, and choosing a maximizing action plus the inductively optimal continuations attains it.
Finite sums and maxima are executable with exact rational data; other real data need certified comparisons/tolerances.
This constructs an optimal planning program with a supplied sufficient state/model/objective. It does not derive the objective or causal validity of the model.
Uncertain dynamics, exploration, model acquisition and lifecycle cost require the additional learning/causal/agency premises; no unique tree-search or neural planner follows.

## What neutral rediscovery must still establish

All claims are restricted to their quantified domains and interfaces. A common low-level grammar supplies representation assumptions even when architecture labels/templates are withheld.
Recovery must be checked on independently registered unseen task specifications, with labels unavailable to search and structural equivalence assessed after execution.
A new form requires a demonstrated behavior/resource advantage or a proved separation against the admitted parent class under matched costs; different syntax is insufficient.
These conditional derivations do not establish empirical task distributions, successful heldout recovery, scientific novelty, or all-domain optimality by assertion.
