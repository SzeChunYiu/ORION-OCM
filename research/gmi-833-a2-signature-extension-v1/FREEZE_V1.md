# A2 signature programme extension freeze V1

Date frozen: 2026-09-17.
Authority: revival ticket `REV-L50-A2-SIGNATURE-PROGRAMME` (#833 baseline register); parent standard #855 (`gmi-833-no-smuggling-audit-v1`, frozen `af467254206fa76ec3eab31078a420f1ad4d7cea`); usage precedent #974 (`gmi-833-blind-recovery-v2-v1/screen_v2.py`); census `research/gmi-833-corpus-passes-v2-v1/P3_SCREENS_V1.json` + refined-census rule in `VERDICT_REGISTER_V1.json` (`L50_macros_privileged_operators.refined_census_revival`).

This document is the **pre-outcome authority** for the extension. It is committed before any extension screen execution. It modifies nothing in the #855 package or #974 screen; both stay frozen. Reuse: the #855 `audit_core_v1.py` matching engine is imported and used unchanged (the `load_audit_core()` importlib pattern from `screen_v2.py`), and the validation discipline (planted recall, no-alarm controls, anchor reproduction) follows the L42/#949 corpus-passes precedent.

## 1. The gap being closed

The #974 wiring registers **three** semantic fingerprint families: `content_route_weighted_aggregate` (attention class), `translation_shared_local_kernel` (convolution class), `recurrent_state_macro` (recurrence class). Every other class in the frozen D2 denylist has **no semantic fingerprint**: a neutral-named primitive whose mechanism is Bayesian updating, population/selection search, verifier-guided program synthesis, self-rewriting, external retrieval, or dense feed-forward aggregation passes A2 today. Lexical cleanliness cannot discharge A2 (#855 `FREEZE_V1.md`).

## 2. New fingerprint families (six)

Required features use the 11-field signature schema of #855 (`audit_core_v1.py` SIG). Matching semantics are #855's unchanged: a primitive is flagged when it satisfies every required feature (list value → membership; scalar → equality).

### F1 `dense_feedforward_aggregate` — covers D2: neural, neuron, perceptron, mlp, feed_forward, feedforward, backprop

```json
{"locality": "global", "recurrence": false, "types": ["weighted_aggregate"]}
```

Mechanism: a full-layer (global) affine aggregation with dense parameters — the perceptron/MLP forward map — together with its training step (gradient/backprop), which is the same family's parameter-acquisition mechanism. Distinguished from attention (no content-dependent routing required), from convolution (global, not neighborhood), from plain variadic addition (requires the weighted-aggregate type tag, which parameter-free arithmetic never derives).

### F2 `stochastic_belief_update` — covers D2: bayes_update, bayesian_network

```json
{"state_access": "read_write", "types": ["belief_update"]}
```

Mechanism: reweighting a persistent belief/probability state by evidence. Exact Bayesian updating is deterministic, so stochasticity is NOT a required feature (a sampled variant still carries the same belief_update type). Distinguished from a generic STATE_CELL by the belief_update type tag (distribution reweighting vocabulary: posterior/prior/likelihood/normalize-probabilities).

### F3 `population_selection_crossover` — covers D2: genetic_algorithm, genetic_crossover

```json
{"stochasticity": true, "types": ["population_selection"]}
```

Mechanism: stochastic selection/recombination over a candidate population (tournament, fitness-proportional selection, crossover). Deterministic population filters are not this family; a macro that mutates a single candidate is not this family.

### F4 `program_synthesis_search_macro` — covers D2: planner_macro, sygus, synthesizer_macro

```json
{"verifier_access": true, "recurrence": true}
```

Mechanism: an iterated propose-then-verify loop over program space packaged as a primitive. The distinguishing in-schema feature is **verifier access inside the primitive** combined with recurrence (search cannot be one-shot). This is the semantic content of planner/sygus/CEGIS-style macros: the searched grammar's own primitive calls the verifier.

### F5 `self_modification_macro` — covers D2: self_modify_macro, godel_machine, rewrite_engine

```json
{"addressability": true, "state_access": "read_write", "types": ["self_rewrite"]}
```

Mechanism: reading and rewriting the currently executing program's own text (splice/patch own genome/Gödel-style self-reference). Addressability of own code + a write to it + the self_rewrite type tag.

### F6 `external_content_retrieval` — covers D2: rag_retriever, content_retriever

```json
{"content_dependent_routing": true, "types": ["retrieval"]}
```

Mechanism: routing computation through content fetched from an external store keyed by similarity (retrieval-augmented step). Distinguished from in-context attention aggregation by the retrieval type tag (external-store vocabulary) rather than by routing alone.

### Alignment with existing families (no new registration needed)

`transformer, self_attention, attention, query_key_value, softmax` → `content_route_weighted_aggregate` (v2); `conv2d, convolution, shared_kernel` → `translation_shared_local_kernel` (v2); `lstm_gate, gru, recurrent_layer, shift_register` → `recurrent_state_macro` (v2). With F1–F6 every D2 class has a semantic fingerprint; the full mapping table is asserted in the screen.

## 3. Signature derivation grammar (frozen; deterministic, from primitive block source)

The corpus packages have no author-declared signatures — that is why they are UNAUDITED_OPERATOR_SURFACE. The extension DERIVES the 11 fields from each extracted primitive block. All rules below are deterministic functions of the block text (and AST where parseable); none inspect the primitive's name (name-blindness is the point of A2 and is tested by plant P2).

### 3.1 Block extraction

A file is primitive-defining under the REGISTERED refined-census rule: vocabulary match (`primitive|operator|instruction set|opcode|grammar|DSL`, case-insensitive, on text or filename stem) AND definition-like structure (an assignment to `OPS|PRIMITIVES|OPERATORS|OPCODES|INSTRUCTIONS|OP_TABLE|BASIS|GRAMMAR`-named symbol, a "primitive basis/set" phrase, an opcode list in markdown, or def/class definitions with operator-ish names) in the same file. Blocks:

- **B-PY-DICT**: parseable Python, module-level dict/list/tuple assignment with a name matching `^(OPS|PRIMITIVES|OPERATORS|OPCODES|INSTRUCTIONS|OP_TABLE|BASIS|GRAMMAR)` — each element (key + value source segment) is one block.
- **B-PY-DEF**: parseable Python, `def`/`class` whose source segment contains a primitive-defining cue (dispatch on a kind/opcode tag, or a name matching `^(op|prim|opcode|instr)_` or the file itself defines the op table) — the def segment is one block.
- **B-MD-ROW**: markdown table row or list item whose first cell is a backticked short identifier, inside a primitive-defining file — the row text is one block.
- **B-RE-ENTRY**: unparseable files — `"name": <expr>` / `("name", ...)` entries inside a block delimited by an OPS-like header — each entry is one block.

### 3.2 Field rules

- `arity`: B-PY: positional parameter count of the def/lambda (`*args` → `"variadic"`; class → method arities, max). B-MD/B-RE: operand count in a signature-like `(a, b)` pattern if present, else `"undeclared"`.
- `types`: tags from the FROZEN TAG LEXICON (3.3) matched against the block body (word-boundary, case-insensitive).
- `state_access`: `"read_write"` if the block assigns/appends into a container that is not a local parameter (subscript assignment on a non-parameter name, `self.<attr>` assignment, `.append/.extend/.update` on a non-parameter name, `global`/`nonlocal` write); `"read"` if such containers are only read; else `"none"`.
- `locality`: `"neighborhood"` if window|neighbor|kernel|stencil|adjacen|offset|conv tokens; `"global"` if the block aggregates over a collection (`for ... in` over an input collection, `sum(|max(|min(|matmul|dot(`, `all_inputs|examples|inputs` iteration) or full-layer/dense/attention tokens; `"local"` otherwise.
- `addressability`: `true` iff the block subscripts or rebinds a program-text-like object: `program[|code[|genome[|instruction[|self.ops[|expr[` on the read side or a write target, or `rewrite|splice|patch` applied to such an object.
- `content_dependent_routing`: `true` iff a branch condition or an index expression consumes a data value: `if <name>` where `<name>` is also read from data (approximated by: `if ` followed by a token that appears subscripted as data, or `bits[|x[|value[|cond|score|fitness` inside a subscript or branch test), or `route|gate|dispatch.*by` tokens; `false` otherwise (position-indexed `for i in range(...)` is NOT content routing).
- `parameter_sharing`: `"none"` if no parameter-ish token (`weight|kernel|theta|params|table|W[|w[` as a name); `true` if a parameter-ish name occurs inside a positional loop or at ≥2 distinct subscript sites in the block; `false` if it occurs at exactly one site.
- `recurrence`: `true` if the block calls itself, or contains `while` with a state write, or a `for ... range/steps/epochs` loop whose body writes the state container read before the loop; `false` otherwise.
- `stochasticity`: `true` if `random|sample|noise|stochastic|probabilistic|temperature|bernoulli|gaussian|shuffle` tokens; else `false`.
- `verifier_access`: `true` if `verifier|oracle|exact_verify|fitness|evaluate|score|judge|check` tokens appear as called names (`<token>(`) or attribute calls; else `false`.
- `resource_class`: `"O(n^2)"` if two nested collection loops or `pairwise|attention|matmul`; `"O(n*k)"` if retrieval tag present with a single loop; `"O(n)"` if one collection pass; `"O(1)"` if no collection access; else `"unclassified"`.

### 3.3 Frozen tag lexicon (mechanism vocabulary; word-boundary matches on the block body)

```text
weighted_aggregate : matmul, dot, weighted, dense, linear_layer, affine, perceptron,
                     mlp, feedforward, feed_forward, backprop, gradient_step,
                     softmax, neural, neuron
belief_update      : bayes, posterior, prior, likelihood, belief, normalize_prob,
                     probability_vector
population_selection: crossover, tournament, fitness, genetic, generation_,
                      select_best, mutate_population, elite
synthesis_search   : sygus, synthes, planner, cegis, propose, program_search
self_rewrite       : rewrite, self_modify, splice, patch_program, edit_genome,
                     godel, self_reference
retrieval          : retriev, embedding_lookup, similarity_search, knn, corpus_fetch,
                     rag, content_retriev
state_io           : cell, register, shift, load, store, read_, write_
arithmetic         : add, sub, mul, xor, and_, or_, neg, not_, sum
comparison         : compare, ge_, le_, eq_, gt_, lt_, threshold
control            : branch, if_, select, mux
```

Lexicon membership is justified per family in section 2; the arithmetic/comparison/control/state_io tags exist so clean decomposed bases derive non-empty type lists that never intersect a family requirement.

## 4. Census re-derivation and anchors (gate P5)

The screen re-derives the refined census with the registered rule over the census population (231 packages of `P3_SCREENS_V1.json`) and MUST reproduce exactly: `primitive_defining_packages == 109`, `unaudited_operator_surface == 108`, `a2_covered == 1`, with anchors `gmi-833-aj9b-k01-blind-recovery-v1` IN, `gmi-833-af-barrier-*` OUT (prose negation), `gmi-833-robustness-controls-v1` A2-covered. Any mismatch → exit code 2, no candidates emitted (the L42 anchor-refusal pattern).

## 5. Validation plan (checker-validation bar; all must pass before corpus candidates are emitted)

- **P1 known-same recall (synthetic)**: one canonical mechanism-typical block per new family (six blocks, written from the family's mechanism description) → all six flagged, each by its own family. 6/6 required.
- **P2 neutral-rename semantic-collision plants**: the same six bodies under neutral names (`step`, `combine`, `update2`, `apply`, `mix`, `fetch`) → still flagged 6/6 (name-blindness; this is the smuggle the screen exists to catch).
- **P3 no-alarm on known-clean bases**: the #974 real v2 basis signatures (ADD, NEG, GE_c, INPUT_ATOM, STATE_CELL as registered in `screen_v2.py`), the #855 fixture admissible primitives, and the corpus's own clean grammar blocks (gmi-neutral-derivation-v1 `neutral_machine.py` c/r/b/i opcodes) → 0 flags.
- **P4 sampled no-alarm**: `random.Random(833215)` sample of 200 extracted corpus blocks whose derived types contain no family tag → 0 flags.
- **P5 census anchor gate** (section 4).
- **P6 existing-family regression**: the three #974 positive controls (`mix`, `local_apply`, `cell_step`) still flag under their families with the extension's deriver off (signatures taken verbatim from `screen_v2.py`), proving the extension does not disturb the merged standard.

## 6. Corpus screen and adjudication rule

Over the 108 UNAUDITED_OPERATOR_SURFACE packages: extract blocks from primitive-defining files, derive signatures, match against the nine families (3 existing + 6 new). Output `A2_EXTENDED_SCREEN_V1.json`: per package `{n_files_scanned, n_blocks, flags: [{file, block_name, family, derived_signature, block_excerpt}]}` and totals.

A flag is **CONFIRMED** only if BOTH: (i) the derived signature matches a family fingerprint, and (ii) the flagged block is part of the package's searched grammar or evaluated operator set — not parent-literature prose, not a ledger/citation echo, not the corpus's own anti-smuggling machinery (denylist definitions themselves: known L50 false-positive classes). Each CONFIRMED flag is adjudicated individually in the result register with a one-line reason and the block excerpt. Flags failing (ii) are adjudicated `CONTEXT_NOT_GRAMMAR` with reason. Packages with zero flags get disposition `CLEAN_AT_EXTENDED_A2_SCOPE` — refining L48/L50 from "cannot exclude" to a signature-level disposition.

## 7. Receipts and counts

Receipt JSON pins sha256 of: `FREEZE_V1.md` (this file), the screen source, `test_a2_extension_v1.py`, `P3_SCREENS_V1.json`, `audit_core_v1.py`, `screen_v2.py`, and the census population inputs; records git HEAD; script-asserts `n_packages == 108`, validation plants P1–P6 all true, and per-family flag counts; re-reads the written output and asserts equality before exiting 0.

## 8. Claim ceiling

```text
A2_SIGNATURE_PROGRAMME_EXTENSION_V1
SIX_NEW_FAMILIES_F1_F6_ALL_D2_CLASSES_MAPPED
DERIVED_SIGNATURES_NAME_BLIND_VALIDATED_ON_PLANTS
CORPUS_SCREEN_108_PACKAGES_WITH_INDIVIDUAL_ADJUDICATION
NO_CHANGE_TO_855_STANDARD_OR_974_SCREEN
```
