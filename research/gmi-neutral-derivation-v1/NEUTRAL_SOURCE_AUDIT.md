# Frozen neutral-rediscovery source audit

This audit records precise scope corrections without altering historical files. The coordinating root identified parent commit `df777cd79ba5ec6925fd82552e9341f8d73f3577`. The five inspected files were copied into `inspection-architecture-v1/research/machine-intelligence-morphogenesis-v1/`; their exact content hashes are below. All repository paths in the table have prefix `research/machine-intelligence-morphogenesis-v1/`.

| File | SHA256 |
|---|---|
| `GMI_NEUTRAL_MULTI_ENCODING_REDISCOVERY_V3.md` | `8427176e275ea7d4f3d1e200ba1b42dc33aadf92a3da59021051ee62153118f3` |
| `run_gmi_neutral_multi_encoding_rediscovery_v3.py` | `1978ea398c54bdc217b0fe815e3169e9018a47b6da92aa4cbd57984b86da9aff` |
| `GMI_NEUTRAL_SEARCH_ADEQUACY_THEOREM_V1.md` | `6c9eb8544393873578f37c69a0e2ecc3765a04df2680af9126d00e8516c6f1bd` |
| `GMI_ZERO_PRIOR_EXACT_REDISCOVERY_V2.md` | `55227e98a6dd0af23a158be1d325c0d4eb2f1ee4cfdf01c4fc6babf820ea9c50` |
| `run_gmi_zero_prior_exact_rediscovery_v2.py` | `f81298c252ea45935448b431728ce4cb3828eeca4c2bc66fa5e41b7263996dcf` |

## A. V2 is a supplied-cost comparison

`run_gmi_zero_prior_exact_rediscovery_v2.py::main` constructs fourteen dictionaries of two or three named candidates and supplied scalar costs. `choose` returns their minimum, with floating-point tolerance `1e-12`. Candidate names include `exact_index`, `similarity_cleanup`, `belief_state`, `per_query_search` and `model_plan`.

The runner has no program generator, executable grammar, task learner, noisy-cue simulator or belief-state computation. Some costs are literal numbers; others evaluate supplied analytic formulas. Its only imports are standard-library JSON and path handling. The accompanying statement that historical architecture names are absent from the runner is false at these source hashes. “Exact” should mean the intended finite arithmetic comparison, not exact rational execution of the described mechanisms.

Its variance expression assumes the stipulated covariance model and equal-weight aggregation. Its retry expression assumes the stipulated success/checking model. Neither assumption is established by constructing and running the compared systems. The useful surviving claim is a set of hand-registered analytic cost comparisons with matched twins.

## B. V3 varies expression traversal, not scientific grammar

`run_gmi_neutral_multi_encoding_rediscovery_v3.py` defines constants, named scalar variables, addition and multiplication. It supplies exactly two cost expressions for each of twelve pairs. It does not enumerate a grammar of programs or infer those expressions from tasks.

`postfix` and `graph` mechanically translate the same arithmetic AST. `ast`, `post` and `ge` all call the same `apply` function for arithmetic; thus arithmetic semantics are shared even though traversal code differs. Supplied scalar fields such as `enserr`, `uncert`, `miss`, `global` and `local` already summarize the hypothesized mechanisms and their consequences.

The terminal check compares the winners across traversals, and checks that each positive/twin pair changes winner. It does not assert equality of numeric evaluator outputs. It also does not require the intended positive orientation: consistently reversing both winners would still satisfy the pair-flip condition. Therefore the prose claim of identical numeric costs is not established by that runner's acceptance check.

The explicit caveat that these are equivalent primitive arithmetic encodings, not independently authored scientific grammars, is correct and should remain the claim ceiling. This audit does not assert that any recorded winner is numerically wrong; it identifies what the checks actually establish.

## C. Search adequacy needs a property-fiber correction

NS-1 correctly states that exact exhaustive enumeration returns an optimum within a finite frozen grammar and resource bound. Its first consequence needs stronger quantifiers: a non-F program beating one F witness does not establish that F is absent from the optimum.

Counterexample: an F witness costs two, another F program costs one, and a non-F program costs one. Exhaustive search may return the non-F program by tie-breaking, strictly improving on the witness, although F remains frontier-optimal.

The corrected conditions are:

    min_(not F) J < min_F J  ⇒ every global minimizer lacks F;
    min_F J < min_(not F) J  ⇒ every global minimizer has F;
    min_F J = min_(not F) J  ⇒ both properties occur in the optimal fiber,

provided both minima are attained over the complete registered admissible space. An absent class has minimum +∞ and needs its own expressivity interpretation. No one-witness comparison substitutes for these full-space minima.

NS-2's independent-draw bound `(1−p_min)^n≤exp(−np_min)` is valid under its stated positive discovery-probability premise. Neither inspected runner performs that sampling or certifies such a probability. The theoretical statement itself does not supply search adequacy for an unrelated implementation.

## D. Registration and holdout scope

Expected winners are present alongside supplied cost cells in the V2 source. V3 has fixed positive/twin inputs and a flip check. These five files do not establish that predictions were protected before evaluation, nor do they contain a protected external generator. This is a scoped audit, not a claim that no separate registry or generator exists elsewhere in the repository.

The replacement [executable synthesis unit](NEUTRAL_SYNTHESIS.md) separates a hashed pre-execution prediction registration from exhaustive program generation and exact trace pricing. It adds complete optimal fibers, actual finite semantics, acquisition counters and hostile certificate controls. Its holdouts are explicitly parameters and a function. It does not retrospectively upgrade historical V2/V3 to independent-grammar, neural, or unseen-family rediscovery.
