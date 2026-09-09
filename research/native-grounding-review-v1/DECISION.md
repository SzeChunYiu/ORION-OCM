# Native grounding: source diagnosis and next cost lever

8 September 2026. Source/literature review only. No implementation, compilation,
native proof check, corpus read, new outcome or adoption decision was executed here.
Current OCM serving adoption keeps its frozen compiler and eight-arm comparison.

## What the evidence locates

The finished indexed-deduction comparison attributes 3.785–3.925 seconds per cold
arm to rule construction. Changing scheduling alone leaves this work intact.
These are single fixed observations, not a replicated performance estimate.
See [retained result](../native-indexed-deduction-evidence-v1/HANDOFF.md).

Read source: native-ocm-adoption-v1/source-candidate-02 on billy-laptop:

- vendor/finite_search.py, SHA5b174d610c99fcc5e74fa4df803045357729916d76723826bc2918e1536e6de3.
- vendor/native_match.py, SHAd4ddc554f6cc284733418ddec0f9dac08bcef2f53cc77fc9d60b25415754edfb.
- native_engine.py, SHA3092ae496099533094e6a46a0f72e07c912e57e62d391cd520b8a9863915975a.

compile_parent visits every assertion, checks necessary literal counts, then matches
each surviving conclusion against every bank formula. Bound premises use exact
lookup; an unbound premise loops over the entire formula bank. Accepted instances
are materialized and hashed before search. The current result has 69,219 ordinary
instances from 4,191 assertions and 255 formulas. This is whole-bank grounding.

The engine also checks source/input identity repeatedly and replays the native
prefix during qualification/checking. Optimizing grounding cannot establish
whole-task locality while these other whole-input operations remain.

## Assimilate the mechanism

Soufflé's documented magic-set transformation specializes rules from query bindings
and propagates those bindings through dependencies. Its documented implementation
excludes dependencies containing negation, functors or aggregates. This is a mature
parent for avoiding irrelevant derivation work, not an OCM novelty.
[Official documentation](https://souffle-lang.github.io/magicset), read 8 September.

Stuckey and Sudarshan's *Compiling Query Constraints* describes parameterized
constraints and constraint adornment, including explicit conditions needed for
finite evaluation. Runtime demand restrictions are therefore not automatically
free or terminating. Reviewed abstract, sections 4/6/7 and discussion excerpts;
this is not a full proof audit or an implementation qualification.
[Author-hosted paper](https://www.cse.iitb.ac.in/~sudarsha/Pubs-dir/compiling-query-constraints-pods94.pdf).

The native setting admits a simpler first adaptation: exact demand for ground
formula IDs in a fixed finite bank. Mathematical negation inside a formula is an
object-language token, not Datalog negation-as-failure. A future translation must
preserve that distinction. No Soufflé dependency or foreign code was installed.

## Compare three separate levers

| Lever | What it can save | What must remain charged |
|---|---|---|
| Immutable compiled-bank reuse | Repeated construction under the identical library/bank/compiler contract | First construction, storage/load, version checking, invalidation and revision |
| Exact conclusion/premise indexes | Impossible pattern/formula comparisons | Index construction/maintenance, broad-pattern fallback, exact matching and DV checks |
| Demand-driven grounding | Construction of ground rules outside a sufficient target cone | Demand propagation, all matching producers, missing-premise bindings, certificate/refinement |

Do not combine these in one first timing comparison. Identical compiled-bank reuse
is ordinary caching, not active-subspace execution. An index on an already fully
grounded action list does not eliminate the cold grounding cost.

## Correctness obligation for a demand-driven successor

Design inference, not a proved or implemented OCM theorem: start from the requested
target. For every demanded formula, enumerate every legal producing ground action
in the registered finite bank, then demand every ordered premise of those actions.
At complete backward closure, any finite proof of the target uses only retained
actions, by induction down its proof tree. The existing exact search can then run
on that subgraph. The obligation is completeness of producer enumeration and
closure; a retrieval miss or interrupted closure supplies no such certificate.

Keep parallel producers, repeated premise ports, empty-premise rules, cycles,
composite/repeated substitutions, exact type/DV scope and native proof expansion.
Preserve minimum cost 1 + sum(child costs); preserving mere reachability is weaker.
Canonical tie behavior needs its own comparison if exact proof bytes are required.

Variable-headed rules can match almost every demanded formula; premise-only
variables may force whole-bank matching. A backward cone can be global even when
the final proof is short. The index must include these broad-rule fallbacks.
No universal O(k) claim follows from the proposed closure argument.

## Smallest useful next experiment

Finish serving adoption first. Typed learner qualification and separated-family
reuse remain the next scientific capability gap; do not indefinitely postpone
them for engine polish. Choose a cost intervention only when its saved repeated
work materially enables that experiment.

For a future grounding control, preserve the dense complete compiler as oracle.
Freeze authored selective, broad-rule/global, cyclic, repeated-port and false-task
cases before execution. Include controlled unrelated-library growth and report
cold build, warm query, revision, native verification and complete elapsed cost.
Compare exact terminal/minimum cost and independently checked normal proofs.
Report local closure size and producer probes separately from final proof size.

If demand closure is global, retain that outcome and locate the cause. A later
binding-propagation repair is a new frozen candidate, not permission to remove
the troublesome legitimate rule. Supply any successful compiler mechanism to
both the conventional parent and OCM before claiming an architectural residual.
