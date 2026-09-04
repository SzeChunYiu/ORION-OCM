# KSO M0 replay receipt V1

Branch: `research/ocm-kso-math-v1-20260904`  
Stack base: PR #289 head `3a96e2ad8d30eadbcf6e55338fabe9231b583950`  
Scope: KnowledgeSpace.v1 M0 only; no M1–M6 result authority.

## Replay

The committed reference checker and its repo-relative unit-test contract were reproduced in an isolated filesystem with the same expected path structure.

```text
python -m pytest -q test_kso_math_v1.py
.........                                                                [100%]
9 passed in 0.43s
```

A first scratch invocation intentionally lacked the repository-relative `research/orion-machine/reference/` path expected by the test loader and therefore produced nine `FileNotFoundError` setup errors. Creating the same repository-relative layout and replaying the unchanged module/test produced the green result above. This was a harness-layout error, not a scientific or implementation defect; it is disclosed so the first failure is not silently discarded.

## Exact finite denominators

- warrant antichains, n=3: 20;
- semiring ordered pairs: 400;
- semiring ordered triples: 8,000;
- independent navigation matrices: 2/2 equal;
- bad post-revocation renormalizer: 1/1 detected;
- exact restart fixed point: 1/1;
- contraction probes: 200/200;
- conjunctive firing/revocation: 2/2;
- lumpability pushforward commutation: 80/80;
- planted non-lumpable control: 1/1 rejected;
- connectivity cases: 5;
- impact cone: 1/1.

Finite checks validate the executable finite model. They do not replace the all-size proofs in `theory/KSO_SUBSTRATE_CONTRACT_V1.md`.

## Terminals

```text
M0_FINITE_MATH_CORE = GREEN
GENERAL_NOVELTY = NOT_ESTABLISHED
M1_KSO_INSTANCE = NOT_RUN
M2_SOLVE_LOOP = NOT_RUN
M3_GAP_LEARNING = NOT_RUN
M4_JUMP_LOOP = NOT_RUN
M5_CHAT = NOT_RUN
M6_FRONTIER_MATH = NOT_RUN
```
