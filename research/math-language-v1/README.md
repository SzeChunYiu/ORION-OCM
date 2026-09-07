# Unary mathematics and controlled language

This package is a supplied semantic contract and conventional exact symbolic parent.
It does not learn methods, persist an OCM library, prove transfer, or use FLT imports.
No existing OCM runtime or historical proof package is modified.

## Use

From this directory with Python 3.11:

```python
from unary_language import parse, realize
from unary_solver import solve, RegionSolver
from unary_verify import verify_result

task = parse("every violinist is musician. no musician is asleep. query some violinist is asleep?")
result = solve(task)
assert verify_result(task, result)
print(result["status"])
print(realize(task))
```

The example is CONTRADICTED under the supplied premises. It does not imply that
a violinist exists. Text is formal controlled notation with exact predicate labels;
“is” is a fixed grammar token, not an inflection/morphology rule.

## Supplied grammar

```text
document  := (statement ".")* "query" statement "?"
statement := ("every" | "no" | "some" | "not" "every") expression "is" expression
expression := IDENT | "(" "not" expression ")"
            | "(" expression ("and" | "or") expression ")"
```

A name is 1–32 ASCII letters/digits/underscores, begins with a letter, and is not
a reserved grammar word. Names are case-sensitive. Quantifier/operator keywords
are lowercase. Whitespace is insignificant; all other input must be consumed.
The internal JSON tag `not_every` is not a surface quantifier spelling.
No pronouns, implicit facts, equality, cardinality, unstated plurals or paraphrases.

Limits are one to four exactly-used predicates, 32 premises, 512 expression nodes
across the task, nesting depth 16 and 16 KiB of ASCII input. Individual predicates
may be empty. The domain is nonempty. Boolean grouping is explicit.

## Data contract

`validate_task(data)` in [unary_contract.py](unary_contract.py) returns detached
plain JSON data or raises `InputRefused`. Only the following exact task fields occur:

```json
{"schema":"ocm.unary-task.v1","predicates":["A","B"],
 "premises":[{"kind":"every","left":["pred","A"],"right":["pred","B"]}],
 "query":{"kind":"some","left":["pred","A"],"right":["pred","B"]}}
```

AST tags: `["pred", name]`, `["not", expression]`, or
`["and"|"or", left, right]`. Statement kinds: every, no, some, not_every.
The registry is sorted and equals the names actually used by premises and query.
`task_digest` binds the exact validated structure, including premise order and names.
It is not an alpha-equivalence fingerprint for train/test deduplication.

`parse(text)` and `realize(task)` raise `InputRefused` on unsupported input.
Realization is canonical and returns a complete document, not an answer explanation.
Independent supplied text-to-AST pairs supplement inverse roundtrip tests.

## Conventional exact parent

[unary_solver.py](unary_solver.py) caches expression masks in a fixed-vocabulary
`RegionSolver(predicates)`. Its `solve(task)` reprocesses current premises and
can reuse masks across queries or premise withdrawal/reinstatement. The module-level
`solve(task)` creates a cold engine. Invalid tasks return INPUT_REFUSED.
The successor also exposes `prepare(task)` and `complete(prepared)`: premises are
compiled once, without computing query branches, and exact completion reuses them.
See the [prepared API contract](../math-language-learning-v1/CONTRACT.md). Completion
reports its call's work; the engine accumulates work within a preparation scope.
Prepared-state inspection still hashes, decodes and validates the full bound state.

For n predicate symbols, each of the 2^n regions is one possible membership signature.
Universals forbid signatures. Each existential needs an allowed signature independently;
different requirements may have different witnesses. A nonempty domain is checked
even if there are no existential statements. At most one object per occupied signature
is enough for this fragment; this is not a bounded-population assumption.

Results bind the exact task digest and carry:
- `premises`: a model or unsatisfiability certificate;
- `query_true` / `query_false`: certificates after requiring each query polarity;
- `status`: ENTAILED, CONTRADICTED, UNKNOWN, or INCONSISTENT;
- `counters`: explicit mask/cache/constraint/witness operation counts.

UNKNOWN contains two actual models. INCONSISTENT has an unsatisfiable premise
certificate and null query branches; it is not an answer by explosion.
A model is a nonempty sorted unique list of region integers. Bit i records membership
in registry predicate i. An unsatisfiability certificate identifies an existential
(or the nonempty-domain obligation) and universal constraints covering all its
possible witnesses. Covers need not be minimal.

## Independent verification and evidence boundary

[unary_verify.py](unary_verify.py) never imports or invokes the solver.
It directly evaluates expressions and statements on finite models, and enumerates
membership assignments to verify unsatisfiable witness coverage. It checks task
binding, both polarity branches, nonempty domain, exact certificate shapes and status.
`verify_result(task, result)` returns a boolean; INPUT_REFUSED is not a proof.

The verifier checks counter shape, not historical authenticity. Counters describe
logical operations only: `expression_nodes` counts calls requesting a mask;
`predicate_region_tests` counts membership tests constructing primitive masks.
`cache_key_nodes` counts every actual AST-node visit constructing cache probe keys,
including warm hits. A nested hit still traverses its complete expression.
Validation, serialization, Python key hashing/equality and allocation, interpreter,
wall/CPU/RSS and source-custody costs are outside these logical counters.
Complete wall/CPU accounting is still required; cache hits do not imply sparse execution.
The cache and host objects are trusted Python state; this is not an arbitrary-code sandbox.

The four production modules import only Python stdlib and the local contract.
This source observation does not establish whole-host no-neural qualification,
linguistic intent, empirical truth of premises, or a useful learned method.

## Authored qualification

Tests cover polarity, vacuity, empty predicates/domain, inconsistent inputs,
independent existential witnesses, cache reuse, strict grammar and schema,
certificate/result tampering, and independence from optimized solve.

The separate test oracle uses Python sets of objects rather than masks or the
production evaluator. For one, two and three predicates it enumerates every nonempty
region-world for its declared family: atomic queries, zero/one atomic premise,
a two-premise endpoint family and a Boolean De Morgan query. This is not exhaustive
over all bounded ASTs, all 32-premise theories, or four-predicate worlds.

Current authored qualification selects this package and math-language-learning-v1
together, with both import roots and a new explicit external temporary root.
See [the successor qualification](../math-language-learning-v1/QUALIFICATION.md).

Development and final source-bound raw records are retained outside this worktree
under `/home/billy/orion-director-work/20260907/unary-language-qualification-v1`.
Failed attempts remain separate. These authored checks are engineering evidence;
there is no untouched scientific evaluation, learner/persistence/runtime integration,
speedup, broad language competence, or novelty result.

The cache-key counter is a source successor to the original 83-control generation.
Its targeted RED/GREEN and one full-suite result are retained separately under
`/home/billy/orion-director-work/20260907/unary-cache-key-qualification-v1`.
Earlier source snapshots and results are unchanged.

Schema, task-hash and status metadata require exact plain strings before comparison.
The metadata-boundary successor retains its separate authored RED/GREEN and full-suite
records under `/home/billy/orion-director-work/20260907/unary-metadata-qualification-v1`.
These checks validate a data-only API; they do not contain already executing Python.

Retained PR139 records: [historical qualification](QUALIFICATION.md). Its 110-test
source freeze describes the earlier solver, not the prepared-state successor.
