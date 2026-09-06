# FLT-KSO v1 — staged native mathematics falsification substrate

This directory is an additive successor to `research/proof-replay-v1/`. It does **not** modify,
reinterpret, or upgrade the historical Lean 4.19 proof-replay receipt. The tranche was
prospectively registered on issue #62 before branch implementation; #46 remains LOCKED.

## Claim discipline

The native mechanism arm permits no LLM, foundation model, Transformer/neural proof generator, or
opaque learned oracle. `LLM_CALLS=0` and `LLM_TOKENS=0` are explicit receipt fields. Search score,
retrieval rank and planning edges are never theorem warrant.

The first gate is `R1_PROP_CHAIN_001`:

```text
(P → Q) → (Q → R) → P → R
```

A generic implicational proof constructor may use only `INTRO`, exact local `ASSUMPTION`, and exact
local function `APPLY`. The preregistered budget is 64 proof-state expansions and 16 total checker
calls across native and matched-parent arms. The generated proof text is scanned for disallowed
shortcuts/imports and then checked by exactly Lean 4.33.1. The R1 file intentionally imports no
Mathlib; its receipt therefore says `LEAN_4_33_1_KERNEL_ONLY_R1` and `mathlib_loaded_for_r1=false`.
It does **not** pretend that this is already an FLT-environment or FLT theorem result.

The theorem is represented first as a canonical KSO `goal` atom with an UNKNOWN warrant. The proof
operator is a production `BackendKind.PROOF` operator and is retrieved through the production
`IndexedOperatorRegistry`. An unchecked proof candidate stays UNKNOWN. Only exact Lean checker
evidence can make a proof candidate LIVE and create a `proof`/`claim` plus `SUPPORT` route. A failed
bounded search is stored as an observation about that attempt and never refutes the theorem.
Alternative checked proof routes have alternative evidence warrants; revoking one checker receipt
must not destroy another surviving support route.

A strong matched parent uses the same proof grammar, search budget and Lean checker without the KSO
lifecycle. If it matches the R1 result, the comparison terminal is `PARENT_SUFFICIENT`; R1 can still
earn `UNSEEN_COMPOSITION_SUPPORTED`, but no OCM-specific residual is claimed.

## Frozen FLT evaluator source

`MANIFEST.json` pins:

- Anthropic `anthropics/fermats-last-theorem` at
  `aa2d8b34692b16c70f699536de0d8e75b9a3e9ef` (tree
  `8bb1c43c8f26f1c127591dddeffdead2b5094eb7`);
- Lean `4.33.1` (`leanprover/lean4:v4.33.1`);
- Mathlib `v4.33.0`, commit `db584cd6d46c92f209a44c0f1c829460d327499d`;
- 29,511 theorem-wrapper modules and 29,511 proof modules.

`validate_anthropic.py` fails closed unless the checkout commit, Lean toolchain, Mathlib manifest
revision, wrapper count and solution count all match. It then validates **every** wrapper/solution
pair and extracts every active `Theorems.Thm_*` import from `P2M/Sol/S_*.lean`. A wrapper is accepted
only if it imports its exact corresponding `P2M.Sol.S_*` module. The exact statement prefix is
lexically isolated from the generated `:= by p2m_exact_reverting` bridge; a repository-wide coverage
run must succeed before this is treated as complete. `html/` is never consumed.

This is necessary because a `Theorems/Thm_*.lean` wrapper imports the corresponding solution module;
copying a wrapper into a solver challenge would expose an answer path.

## Sealed R2/R3 challenge boundary

`sealer.py` writes sibling public/private packages. The public package contains the target statement,
permitted boundary statements, environment identity and budget metadata; it contains no `P2M/Sol`
text/path and, for R3, no original dependency topology. The private evaluator manifest retains exact
wrapper/proof hashes and dependency topology. Symlinks, embedded private paths, hidden imports,
`html/`, `sorry`, `admit`, `axiom`, `native_decide`, and `unsafe` are rejected.

A subprocess guard clears `LEAN_PATH`, `PYTHONPATH`, `ELAN_TOOLCHAIN` and model/provider credentials.
On Linux, private-file-open tracing requires `strace`; absence is reported as
`CANNOT_CHECK_PRIVATE_OPEN_GUARD`, never silently treated as isolation evidence. A later R2/R3 CI
solver must run from a public artifact in a job that does not checkout the private Anthropic tree;
this tranche does not claim that R2/R3 is earned merely because the sealer exists.

## What this tranche can and cannot earn

Possible current positive terminal:

- `UNSEEN_COMPOSITION_SUPPORTED` — only after the generated R1 source is accepted by Lean 4.33.1.

Expected comparison terminal at this small scope:

- `PARENT_SUFFICIENT` — valid and scientifically informative.

Still unearned unless separately executed:

- `MECHANICAL_HIDDEN_PROOF_RECONSTRUCTION_SUPPORTED` (R2)
- `MECHANICAL_DEPENDENCY_DISCOVERY_SUPPORTED` (R3)
- `MECHANICAL_SUBGOAL_GENERATION_SUPPORTED` (R4)
- `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`
- `ACTIVE_SUBSPACE_SCALING_SUPPORTED`
- `KNOWN_ROUTE_FLT_FORMALIZATION_SUPPORTED`
- `FULL_FLT_NATIVE_SUPPORTED`

Causal method reuse requires a separate prospective fresh task after process restart, an actual
method retrieval+execution event in the native search path, and a matched ablation. Storage or final
proof appearance is insufficient; primitive aliases must be reported as `METHOD_IS_PRIMITIVE_ALIAS`.

## Reproduction

Focused Python hostiles/integration tests:

```bash
python -m pytest -q research/flt-kso-v1/test_flt_kso.py
```

R1 (records `CANNOT_CHECK_PINNED_FLT_ENVIRONMENT` if exact Lean is absent):

```bash
PYTHONPATH=src python research/flt-kso-v1/run_r1.py --out /tmp/r1.json
```

Frozen Anthropic source validation (private/evaluator side only):

```bash
python research/flt-kso-v1/validate_anthropic.py /path/to/frozen/fermats-last-theorem
```

No committed result JSON is a qualification receipt for a different source SHA. If `main` moves,
replay/rebase and requalify on the actual source rather than reusing a stale receipt.
