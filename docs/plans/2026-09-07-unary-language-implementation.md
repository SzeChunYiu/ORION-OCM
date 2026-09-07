# Unary Language Semantic Slice Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Supply a strict unary-Boolean task language, exact cached solver and independent certificates.

**Architecture:** Four stdlib modules share only the validated data contract. Optimized bitsets
and independent direct-model semantics are separate. No existing OCM source or historical records change.

**Tech Stack:** Python 3.11, stdlib, existing pytest on billy-laptop; no added dependencies.

---

## Task 1: Contract and controlled language

Create `research/math-language-v1/unary_contract.py`, `unary_language.py`.
Create `test_unary_contract_language.py` plus `unary_test_support.py`.
Write failing schema/bounds/polarity/full-input/roundtrip tests first. Observe RED
because these modules are absent, then implement exact fields and explicit grammar.
No lowercasing, inflection or partial-match recovery.

## Task 2: Exact solver and independent certificate verification

Create `unary_solver.py`, `unary_verify.py`, `test_unary_solver.py`.
Write failing vacuity/consistency/independent-witness/model/cover/tamper/cache tests.
Implement cached expression masks and complete region satisfiability.
Verifier shares schema validation only and directly evaluates each world/region.
Check semantic statuses separately from INPUT_REFUSED and fail closed on false certificates.

## Task 3: Independent exhaustive oracle and source qualification

Create `test_unary_oracle.py` and `README.md`.
Enumerate all nonempty worlds for the declared <=3-predicate task family.
Compare statuses and actual certificate verification. Include De Morgan/Boolean controls.
Run only this package; retain each raw attempt and final snapshots externally.

Exact laptop command (RUN is a new numbered external directory):
```sh
cd /home/billy/orion-director-work/20260907/ocm-unary-language/research/math-language-v1
/home/billy/orion-director-work/20260907/proof-runtime-engineering-env/bin/python -m pytest -q . --basetemp=$RUN/cases --junitxml=$RUN/tests.xml
```
A stdlib external recorder supplies create-only RUN, exact argv/source/interpreter hashes,
raw stdout/stderr, return code, wall/CPU scope and before/after source comparison.
RED should be missing-feature assertions; final GREEN has no skips.
Register no learner/transfer/performance result. Review diff/line counts, then commit
only these new files and this design/plan. Root owns independent review and publication.
