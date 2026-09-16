# AJ9a known-family benchmark freeze

The family registry was committed **before** any AJ9 holdout generator/search/evaluator implementation or outcome exists.

- frozen registry path: `research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json`
- frozen Git blob: `6b9ac3095c90d74e2717671a70ad7cc18955310c`
- freeze commit: `aec01b0e4208a6e03423e5c6c020b1cddc43a5e4`
- family count: 11
- role: `POSTHOC_ADJUDICATOR_ONLY`
- generator/search/evaluator access: forbidden

No AJ9 family recovery result exists at this freeze. Later recovery evidence is valid only if its configuration passes the prospective no-smuggling contract and the frozen registry object remains byte/Git-blob identical.

This freeze does not establish that the family list is ontologically complete. It is the **registered known-family benchmark** used for leave-family-out/blind-recovery tests. New historical parent families found later must be versioned as a new benchmark rather than silently inserted into this frozen one.
