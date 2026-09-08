# R0A non-test checker population census

**Status:** research-only census / no migration / no production change / no ML authorization.

The handoff for this tranche asked for a non-test checker population census from the
repository tree, and warned that GitHub code search returned empty and that a zero
must not be inferred from it. `checker_census.py` answers that question on the parsed
syntax tree of `git ls-files '*.py'`, and `test_checker_census.py` attacks the answer.

## 1. Why a line-oriented search is the wrong instrument

A checker reaches `OperatorSpec` in more shapes than a grep can see: a call split over
several lines, a mapping literal, an attribute assignment, a factory, a bound method.
The census therefore looks for three syntactic shapes on the AST —

```text
KEYWORD_ARGUMENT             f(..., checker=<expr>, ...)
ASSIGNED_NAME_OR_ATTRIBUTE   checker = <expr>   /   self.checker = <expr>
DICT_LITERAL_KEY             {"checker": <expr>}
```

— and it reports what it could not see rather than implying coverage: a positional
checker, a factory imported from another module, and a checker assembled at run time
from data are all named as blind spots in the receipt.

Every tracked file that fails to parse is counted and named. A zero resting on an
unparsed file is not a zero, and a test asserts the unparsed list is empty.

## 2. The population

```text
tracked Python files    2219
parsed                  2219
unparsed                   0
checker sites            114
```

| bucket | sites | classification |
|---|---:|---|
| PRODUCTION (`src/`) | 4 | 2 FIELD_DECLARATION, 2 NOT_A_CHECKER_CALLABLE |
| RESEARCH | 29 | 5 CONSTANT_STATUS, 17 NOT_REPRESENTABLE, 3 NOT_A_CHECKER_CALLABLE, 2 INDIRECT_UNRESOLVED, 2 NO_CHECKER |
| TEST | 40 | 6 CONSTANT_STATUS, 6 NOT_REPRESENTABLE, 7 INDIRECT_UNRESOLVED, 21 NO_CHECKER |
| ARCHIVED_SNAPSHOT | 41 | frozen copies under `raw/`, `records/`, `results/`, `vendor/`, counted apart from live source |

### The production result

**Production constructs no checker.** The four `src/` sites are:

| site | what it is |
|---|---|
| `src/ocm/runtime/solve.py:344` | the `OperatorSpec.checker` field declaration itself |
| `src/ocm/operators/registry.py:63` | the same field on the registry's `OperatorSpec` |
| `src/ocm/learning/methods.py:133` | `"checker": CHECKER` in `SearchResult.as_dict`, where `CHECKER = "rational-polynomial-coefficients.v1"` — a string naming a checker DOMAIN in a record |
| `src/ocm/chat/learning.py:34` | the same constant, reached through an import alias and resolved across modules |

Neither of the last two is a callable. Counting them would have invented a population;
the census resolves module constants and one hop of import aliases precisely so that
they can be excluded by evidence rather than by assertion.

So the checker population reaching the protected CHECK stage is **entirely
host-supplied**. That is not a new claim — it is what
`R0A_SUFFIX_ELISION_AUDIT_V1.md` assumes and what `R0A_CHECKER_PROVENANCE_AUDIT_V1.md`
demonstrated a collision against — but it is now a measured statement about the tree
rather than a background assumption, and `test_production_supplies_no_checker_callable`
is a tripwire that fails loudly the first time production supplies one.

It also settles the migration question for production in the only honest direction:
there is nothing in `src/` to migrate into the restricted DSL, so a restricted-checker
language cannot be justified by the current production population. Its justification
has to come from the admission path for host-supplied checkers, which is exactly what
`R0A_PROSPECTIVE_CHECKER_BINDING_V1.md` prototypes.

## 3. Classification, and why it is conservative

A site earns the first class it can be *shown* to belong to:

```text
FIELD_DECLARATION         the dataclass field, not a construction site
NOT_A_CHECKER_CALLABLE    a string/number naming a checker domain
NO_CHECKER                literal None
CONSTANT_STATUS           returns one registered status unconditionally
DSL_REPRESENTABLE         a boolean combination of HAS/TYPE/EQ over the argument
NEEDS_DSL_EXTENSION       pure and bounded, but uses operations the grammar lacks
INDIRECT_UNRESOLVED       a reference this pass could not resolve
NOT_REPRESENTABLE         everything else, including everything unrecognised
```

`NEEDS_DSL_EXTENSION` is kept separate from `NOT_REPRESENTABLE` deliberately. `d["n"] > 3`
is pure, total and bounded; it is simply absent from a grammar that has only equality.
Collapsing "needs a bigger language" into "cannot be certified" would hide the cheapest
available improvement to the calculus.

## 4. Proposition 1 (translation soundness) and its proof

> **Proposition 1.** Let `s` be a site the census classifies `CONSTANT_STATUS` or
> `DSL_REPRESENTABLE`, with emitted AST `A`. Then (i) `A` is admitted by the certified
> calculus of `PURE_CHECKER_EFFECT_CONTRACT_V1.md`, and (ii) for every detached
> candidate `d` on which the original Python checker returns a registered status
> without raising, `evaluate(A, d)` returns that same status.

**Proof of (i).** Immediate and mechanical rather than argued: the census calls
`issue_certificate` on every emitted AST and records failures. The receipt reports
13 of 13 translated sites admitted, with an empty failure list, and a test asserts
that list stays empty.

**Proof of (ii).** By structural induction on the translation, which is defined by
cases and is undefined (returns `None`, rejecting the site) on every case not listed.

*Base — status.* `_is_status` recognises `Status.PASS`, `SV.Status.PASS` and the string
`"PASS"`, and emits `STATUS(PASS)`. The Python expression evaluates to that status on
every input, and `evaluate` returns it on every input. Equal.

*Base — `HAS`.* `"k" in x[p]` is translated to `HAS(p ++ [k])`. The census admits this
form only when `p` is a chain of constant subscripts rooted at the checker's own single
parameter (`_path_of`), so the DSL path resolves the same sequence of mapping keys and
sequence indices that Python's `in` inspects, and both are true exactly when the key is
present. Equal wherever Python does not raise.

*Base — `EQ`.* `x[p] == literal` is translated to `EQ(p, literal)` only when the literal
passes `_literal_ok`, the same closed detached grammar the interpreter compares under
`_literal_equal`. `_literal_equal` is type-strict, so it agrees with Python `==` on that
grammar wherever the path resolves.

*Base — `TYPE`.* `isinstance(x[p], K)` is translated to `TYPE(p, kind(K))` only for the
seven closed detached kinds. The interpreter's `_kind` is exact-type, so it agrees with
`isinstance` on those kinds except for `bool`/`int`, where exact-type is the stricter
and therefore the safe direction: a site whose Python form would accept a `bool` as an
`int` is translated to a checker that does not, and the differential battery includes
that case.

*Induction — `NOT`, `AND`, `OR`.* Python's `not`, `and`, `or` on operands already shown
equal, translated to the corresponding DSL predicate. The DSL operators are total
Boolean functions of their children, so the induction hypothesis carries. Python's `and`
and `or` short-circuit and the DSL's do not; since the operands are total wherever their
paths resolve, and every operand is a predicate rather than an effectful expression,
short-circuiting is unobservable at the level of the returned status.

*Induction — `IF`.* `A if T else B` translated to `IF(T, A, B)`. `T` is a predicate by
the induction hypothesis and `A`, `B` are checkers; both languages select the same
branch on the same truth value. ∎

**The premise that carries weight.** The proposition is stated only where the original
*does not raise*. This is not a hedge, it is the interesting content: `d["status"] == "PASS"`
raises `KeyError` on a candidate with no `status` key, where the calculus resolves the
path, fails to find it, and returns `FAIL`. The calculus is **strictly more defined**
than the Python it replaces. That is a property of the language and not an accident of
the translation, so the differential check counts those inputs separately under
`original_raised_translation_returned_a_status` rather than scoring them as agreement,
and a dedicated test asserts the fixture that exercises them actually does.

The consequence for R0A is worth stating: *replacing* a host checker with a certified
translation is not verdict-preserving on inputs where the host checker raises, so a
migration would change behaviour on exactly the inputs an operator author is least
likely to have considered. Nothing here authorizes such a replacement.

## 5. The mechanical half

`differential_check` evaluates the original and the translation on the same battery of
detached candidates — an empty mapping, a present key with the right and the wrong type,
a nested path, a non-mapping root — for every site the census translated whose source is
a closed lambda that reads nothing but its argument and the registered statuses.

```text
sites checked                      6
sites skipped, not a closed lambda 7
candidates per site               14
agreements                        84
disagreements                      0
```

The live-tree run exercises only `CONSTANT_STATUS` translations, because the tree happens
to contain no conditional checker in the recognised subset. That would leave the whole
conditional fragment of Proposition 1 untested by the census alone, so
`test_checker_census.py` carries eight synthetic fixtures — one per grammar construct,
plus a nested `IF` and a nested path — and runs the same classify → translate → admit →
differentially-evaluate pipeline over each. Writing them found two real defects in the
translator: `NOT` and `IF` were emitted with the wrong field names (`operand`/`otherwise`
rather than `arg`/`else`) and were rejected by the validator, and a bound method's `self`
was being counted as the candidate parameter.

## 6. Conservativity, and how it is attacked

The classifier returns "not recognised" rather than "representable" for anything outside
its listed cases. Seven hostile fixtures assert this directly: a checker that calls out
to another function, one that reads an attribute of the candidate, one that closes over a
free name, a comprehension, a subscript by a non-constant key, a nested lambda, and one
that opens a file. None may be classified `CONSTANT_STATUS` or `DSL_REPRESENTABLE`, and
none may carry an emitted AST.

The ordering-comparison fixture is asserted to land in `NEEDS_DSL_EXTENSION`, so that a
future change which quietly folds "pure but richer" into "not representable" fails a test
rather than silently shrinking the reported opportunity.

## 7. What this census does not establish

- It is a census and a static classification. It migrates nothing, changes no production
  code, and authorizes no omission. `R0A_SUFFIX_ELISION_AUDIT_V1.md` still rejects
  unrestricted first-PASS early exit under the arbitrary-host-checker contract, and
  nothing here touches that.
- `INDIRECT_UNRESOLVED` is an honest gap, not zero. Two research sites remain unresolved
  and are listed in the receipt.
- The archived-snapshot bucket is frozen evidence, not maintained source. It is counted
  because excluding it silently would be a choice about the population, and choices about
  the population are what make a census wrong.
- A production checker population of zero is a fact about this tree at this commit. It
  says the restricted DSL cannot be justified by the current production population; it
  says nothing about whether it could be justified by the host-supplied population, which
  the repository cannot see and which the census names as its first blind spot.
