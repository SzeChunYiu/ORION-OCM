# IG-5 Independent Primitive-Alphabet Specification, V1 (spec-only brief for a blind author)

Record: RV-377-160. Gate: IG-5 ENCODING AUTHORSHIP (selection of the neutral primitive alphabet).
This brief is the ONLY thing the independent author receives. It names no existing alphabet, no
existing kind, and no file in the repository. Everything the author selects is the author's own.

## 1. Task in one paragraph

Select a **neutral morphology alphabet**: a finite set of typed primitive kinds from which
learning machines are built as typed dataflow terms, such that the alphabet contains **no
architecture macro** (§2.3) and is the **minimal typed set closed under the composition rules of
§2.2** that can express the nine reference parents of §4. Then show, for each parent, an explicit
compilation into your alphabet, or state that the parent is not expressible and why. Deliver one
JSON file (§5). Someone else will later typecheck your compilations against your own signatures,
count their size, and compare the size with an independent reference you never see. Do not try to
guess that reference; select the alphabet you believe is right and say why.

## 2. Requirements on the alphabet

### 2.1 Kinds and types

* A **kind** is an elementary operation with: a class (§2.1.1), a list of typed input ports, one
  typed output, and a list of named small-integer parameters (possibly empty).
* You choose the **value types**. A typical machine needs at least a vector-like type for the
  query, a scalar-like type for the served answer and the feedback signal, and whatever carrier
  types your state kinds need (table-like, program-like, set-like, flag-like ...). Name them freely.
* Every kind is elementary: one state family, or one routing act, or one local transform, or one
  update law, or one check. A kind that bundles several of these is a macro and is forbidden.

#### 2.1.1 Required classes (each must be non-empty)

| class | what it holds |
|---|---|
| **state** | the carriers a machine may retain across queries (each state kind is one carrier family) |
| **routing** | how a query reaches state or a sub-computation: fixed wiring, lookup by key, retrieval by metric, score-and-select, conditional selection ... |
| **transform** | local computation on values (linear map, elementwise nonlinearity, product, sum, execution of a stored program ...) |
| **update** | laws by which a state kind changes on a feedback event (gradient-like, closed-form solve, insertion, program mutation/search, no-update ...) |
| **verification** | checks on a candidate answer or state before it is served or committed (predicate check, abstain, rollback ...) |
| **interface** | query input, feedback input, served output (and, if you need them, evidence buffers, compile/materialize, shadow copies) |

You may add classes (history, morphogenesis, physical placement) if your selection needs them;
justify each.

### 2.2 Composition rules (abstract)

A **machine** is a finite typed directed acyclic graph: nodes are kind occurrences, edges connect a
node's output to one typed input port of another node, every input port of every node is bound
exactly once, output type must equal the port's type, the graph has exactly one served-output node,
and the graph is acyclic (feedback through time is expressed by update kinds reading and writing
state, not by cycles in the graph).

The alphabet must be **closed** under the following edit operators, in the sense that any
well-typed machine remains a well-typed machine whenever the edit itself respects the types:

1. add a node of any kind, wiring its inputs from existing outputs of matching type;
2. remove a node and rewire its consumers to another producer of the same type;
3. rewire one edge to another producer of the same type;
4. change a parameter value;
5. change the state family of a carrier (swap one state kind for another) and re-type its consumers;
6. change the update law acting on a carrier;
7. gate an answer with a verification kind (insert a check between a value and the output);
8. compile / materialize: replace a computed carrier by a stored one with the same output type;
9. clone a sub-graph and re-specialize it (duplicate nodes and edges, then apply edits 1–7);
10. crossover: replace a typed sub-graph of one machine by a typed sub-graph of another with the
    same interface types.

Concretely this requires **type closure**: every output type of every kind must be consumable by
at least one input port of some kind or be the served-answer type, and every input-port type must
be producible by at least one kind or be an interface type. Dead types are a defect.

### 2.3 Neutrality: no architecture macro

No kind may name or bundle a known architecture or a known learning system. Forbidden as kinds
(names or semantics): transformer, attention head, retrieval-augmented generator, mixture of
experts, convolutional network, recurrent unit (LSTM/GRU), neuron, backpropagation-as-a-network,
Bayesian filter, particle filter, k-nearest-neighbour classifier, gradient network, and any name
of a published model family. Elementary update laws (a gradient step on a coefficient block, a
multiplicative reweighting, an insertion) are allowed; a kind that is a whole trained network is not.

### 2.4 Selection criterion (state it, then apply it)

The alphabet must be **minimal**: no kind may be a fixed composition of the other kinds with at
most a two-fold increase in occurrence count. Give the argument for each kind you keep: which
parent needs it, and why the remaining kinds cannot express it within 2×. Report kinds you
considered and rejected as derivable.

## 3. Registered carrier classes

Every parent in §4 belongs to one of five registered carrier classes. Coverage is scored per class.

| class | carrier |
|---|---|
| **memory** | stored exemplars or indexed entries, read by lookup or retrieval |
| **coefficient** | a dense block of numeric parameters read by a linear/affine map |
| **program_search** | a program/term drawn from a grammar, executed on the query, improved by search |
| **belief** | a distribution over hypotheses, updated by evidence, read by expected-value decision |
| **dynamical** | a hidden state updated at every step of a sequence by a fixed recurrence |

## 4. The nine reference parents (abstract descriptions)

Each parent takes a query of fixed width (a short vector of small integers) and serves one
scalar answer; on feedback it receives the true scalar target for that query.

| id | class | description |
|---|---|---|
| `m1_exact_table` | memory | a finite table keyed by the bits of the query; serves the entry; on feedback writes the observed target into the entry by an exact (closed-form) solve |
| `m2_nearest_exemplar` | memory | a store of (query, target) exemplars; serves the target of the k nearest stored queries under Hamming distance; on feedback inserts the pair |
| `m3_soft_retrieval` | memory | a store of exemplars; serves a similarity-weighted (score-and-select) combination of stored targets; on feedback inserts the pair |
| `c1_threshold_net` | coefficient | query → affine map of width h (coefficient block 1) → threshold nonlinearity → linear readout with bias (coefficient block 2) → answer; on feedback a reverse-mode gradient step on both blocks; keeps an evidence buffer of (query, target) pairs for replay |
| `p1_program_search` | program_search | a program from a declared grammar executed on the query; keeps an evidence buffer; on feedback runs a bounded black-box search over programs against the evidence |
| `p2_population_search` | program_search | as `p1` but the program is improved by a population / mutation update |
| `p3_compile_then_serve` | program_search | a program searched against the evidence buffer is compiled (materialized) into a lookup table, which then serves by key lookup |
| `b1_finite_belief` | belief | a posterior over H hypotheses, each hypothesis a fixed predictor of the answer; serves the posterior-expected prediction; on feedback reweights the posterior multiplicatively by each hypothesis's likelihood of the observed target |
| `d1_linear_recurrence` | dynamical | a hidden state vector updated at every step of the query sequence by a fixed linear map of (state, input); serves a linear readout of the final state; on feedback a gradient step on the recurrence and readout coefficients |

## 5. Deliverable: `ig5_independent_primitives_v1.json`

```json
{
 "schema": "GMIIG5IndependentAlphabetV1",
 "served_model": "<the model id you are running as>",
 "label": "HUMAN_GATE_BYPASSED__MODEL_PROXY",
 "date": "YYYY-MM-DD",
 "types": {"<type name>": "<one-line meaning>"},
 "answer_type": "<type name of the served answer>",
 "kinds": {
   "<KIND_NAME>": {"class": "state|routing|transform|update|verification|interface|<extra>",
                   "inputs": ["<type>", "..."], "output": "<type>", "params": ["<name>", "..."],
                   "meaning": "<one line>", "needed_by": ["<parent id>", "..."],
                   "why_not_derivable": "<one or two sentences>"}
 },
 "rejected_as_derivable": {"<candidate kind>": "<how it is a composition of kept kinds>"},
 "composition_rules": "<your restatement of §2.2 as you implemented it>",
 "selection_justification": "<why this set, why minimal, why closed>",
 "parent_compilations": {
   "<parent id>": {"class": "<carrier class>", "status": "EXPRESSED | NOT_EXPRESSIBLE",
                   "nodes": {"<node id>": ["<KIND_NAME>", {"<param>": 0}]},
                   "edges": [["<src node id>", "<dst node id>", 0]],
                   "note": "<what each node does; or why not expressible>"}
 }
}
```

Compilation conventions: `edges` entries are `[source, destination, input-port-index]` with port
index 0-based into the destination kind's `inputs` list; every input port of every node must be
bound exactly once; exactly one node must be the served-output node (the interface kind whose
output is the answer or whose role is "serve"; state which kind that is in `composition_rules`);
the graph must be acyclic; parameters must be integers and must match the kind's `params` list
exactly. Interface nodes (query input, feedback target, served output) count as occurrences.

Rules on conduct: read only this brief; do not read anything else in the repository, do not read
version-control history, do not execute anything. Select from the requirements, then compile the
parents. If a parent cannot be expressed without a macro, say `NOT_EXPRESSIBLE` and explain; that
is a legitimate outcome and is recorded as such.
