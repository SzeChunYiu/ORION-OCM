# Mechanism and evidence boundary

The previous screen's handwritten wff grammar refused every retained proposal occurrence before matching. This source prototype derives productions from supplied ordinary syntax contracts, allowing legitimate composite or repeated substitutions without special-casing the observed expressions.

The compiler supports the documented Metamath `$j` syntax-tool convention: linear syntax variables, typed floating hypotheses and no essential/DV context on syntax rules. These are adapter assumptions, not restrictions imposed by the native verifier. Unsupported rows remain visible; productive-type closure is relative to the declared parameter context.

Unchanged Lark 1.3.1 provides Earley parsing and ambiguity handling under [MIT](donor/LARK-LICENSE). Encoded tokens preserve Metamath token boundaries. The adapter emits one witness in mandatory-floating order and checks its typed stack replay, including nullary constructors. This establishes neither unique parsing nor minimum proof cost, native acceptance or complete ordinary applicability.

The corrected API has two fields:

- `grammar_coverage_complete` records supported grammar coverage.
- `coverage_complete` is true only when grammar coverage is complete and the query ends in `SYNTAX_PROVED` or `NOT_DERIVABLE_REGISTERED_GRAMMAR`.

Every returned `UNKNOWN` has false query coverage. A replayed positive witness remains usable under incomplete grammar while both coverage flags remain false. Only completed supported nonmembership becomes `ValueError`; `SyntaxUnknown` is distinct and must remain a refusal at the future matcher boundary.

[PATCH.diff](PATCH.diff) changes coverage metadata only. The previous checker already chose exceptions by status; no observed false negative or original audit outcome is being corrected. The three dependency files and Lark runtime are unchanged. [Source origins](records/current/SOURCE-ORIGINS.json)

The original design, donor source references and the complete version/license evidence remain in [RAW.zip](RAW.zip). [Selection](donor/SELECTION.json) and [runtime manifest](donor/LARK-FILES.json) identify the donor. This is conventional parser reuse, not a new parsing algorithm.
