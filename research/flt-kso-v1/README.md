# FLT-KSO v1 — staged native mathematics falsification substrate

This directory is an additive successor to `research/proof-replay-v1/`. It does **not** modify,
reinterpret, or upgrade the historical Lean-4.19 replay receipt. The original tranche was
prospectively registered on #62, then `main` advanced through #128. The branch was replayed from
exact governed main `787a5d2c1611cdf9acbb87cb44fa1b878c8a4d1f` and the #128 F0 requirement was
prospectively registered before implementation. #46 remains LOCKED.

## Claim discipline

The native mechanism arm permits no LLM, foundation model, Transformer/neural proof generator, or
opaque learned oracle. Receipts explicitly record `LLM_CALLS=0`, `LLM_TOKENS=0` and zero foundation
model calls. Search score, retrieval rank and planning edges are never theorem warrant.

### F0 — masked authored composition apparatus

Before unseen composition, current governance requires an exposed apparatus check. The public
`research/proof-replay-v1/Composition.lean` fixture is therefore used with its authored body masked.
The generator receives no Lean source, no target theorem constant and no Foundation source. It
receives only JSON typed state plus the registered signatures of:

- `MEFoundation.agreement_sound`
- `MEFoundation.agreement_refinement`

`f0_generator.py` is a separate `python -I` process. Its only generative operations are structural
unification, `LOCAL_HYPOTHESIS` and generic `APPLY_LEMMA`; it emits a proof AST, not Lean. On Linux,
`strace` must show that this process did not open `Composition.lean`, did not open `Foundation.lean`
and made no network `connect()` call. The trusted host validates the AST whitelist and bindings,
then renders Lean. The pinned fixture blobs are:

- Foundation: `4cce6e295bc1f3e8e289be9ebd7a41ee801d859c`
- masked Composition: `bd32922dd220085b5695140f7e684d87cb6f37c7`

The F0 budget is 128 expanded proof states, 256 rule/hypothesis candidates and 16 total checker calls
for native plus matched-parent controls. Exact Lean 4.33.1 must accept the rendered theorem and its
axiom report before KSO admission. The only positive F0 terminal is
`F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED`; it means **apparatus only**. It earns no discovery,
unseen-proof, FLT-progress, learning or OCM-residual claim. Parent parity is valid
`PARENT_SUFFICIENT` evidence.

### R1 — prospective unseen exact composition

`R1_PROP_CHAIN_001` is frozen as:

```text
(P → Q) → (Q → R) → P → R
```

The generic implicational constructor may use only `INTRO`, exact local `ASSUMPTION`, and local
function `APPLY`. The preregistered budget is 64 proof-state expansions and 16 total checker calls
across native and matched-parent arms. Its generated source imports no Mathlib; exact Lean 4.33.1 is
the checker. Success is `UNSEEN_COMPOSITION_SUPPORTED`. If the matched non-KSO parent achieves the
same result under the same grammar/budget/checker, comparison is `PARENT_SUFFICIENT` and no OCM
residual is claimed.

For both F0 and R1 the theorem starts as a canonical KSO `goal` atom with UNKNOWN warrant. A
production `BackendKind.PROOF` operator is retrieved through `IndexedOperatorRegistry`; an unchecked
candidate remains UNKNOWN. Only exact checker evidence makes a proof candidate LIVE and permits a
`proof`/`claim` plus `SUPPORT` route. Failed bounded search is attempt evidence, not theorem
falsehood. Alternative checked proof routes are alternative supports; revoking one evidence receipt
must not kill another surviving route.

## Frozen FLT evaluator source

`MANIFEST.json` pins Anthropic `anthropics/fermats-last-theorem` at
`aa2d8b34692b16c70f699536de0d8e75b9a3e9ef`, Lean 4.33.1, and Mathlib v4.33.0 /
`db584cd6d46c92f209a44c0f1c829460d327499d`, with 29,511 theorem-wrapper modules and 29,511 proof
modules.

`validate_anthropic.py` fails closed unless checkout commit, toolchain, Mathlib manifest revision and
both module counts match. It then validates **every** wrapper/solution pair and active
`Theorems.Thm_*` import from `P2M/Sol/S_*.lean`. Target statements are lexically isolated at the
unique generated `:= by p2m_exact_reverting` bridge; wrappers containing helper lemmas are handled by
taking the nearest declaration before that unique bridge. Repository-wide coverage must pass;
`html/` is never consumed.

This is necessary because `Theorems/Thm_*.lean` wrappers import their corresponding `P2M.Sol.S_*`
solution modules. Copying a wrapper into a challenge would expose an answer path.

## Sealed R2/R3 boundary

`sealer.py` writes sibling public/private packages. Public packages contain target statements,
permitted boundary statements, environment identity and budget metadata; they contain no hidden
solution text/path and R3 contains no original dependency topology. Private evaluator manifests
retain exact proof/wrapper hashes and original topology. Symlinks, embedded private paths,
`P2M/Sol`, hidden imports, `html/`, `sorry`, `admit`, `axiom`, `native_decide`, and `unsafe` are
rejected. `LEAN_PATH`, `PYTHONPATH`, `ELAN_TOOLCHAIN` and provider credentials are removed.

The Linux open-file hostile requires `strace`; absence is
`CANNOT_CHECK_PRIVATE_OPEN_GUARD`, never isolation evidence. A later R2/R3 native solver must execute
from a physically public-only package. The existence of this sealer is **not** R2/R3 success.

## Current claim ladder

This tranche may earn, if actually executed on the exact current source:

- `F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED`
- `UNSEEN_COMPOSITION_SUPPORTED`
- comparison `PARENT_SUFFICIENT`

Still unearned without separate execution:

- `MECHANICAL_HIDDEN_PROOF_RECONSTRUCTION_SUPPORTED` (R2)
- `MECHANICAL_DEPENDENCY_DISCOVERY_SUPPORTED` (R3)
- `MECHANICAL_SUBGOAL_GENERATION_SUPPORTED` (R4)
- `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`
- `FAILURE_MEMORY_USEFUL_AT_SCOPE`
- `ACTIVE_SUBSPACE_SCALING_SUPPORTED`
- `KNOWN_ROUTE_FLT_FORMALIZATION_SUPPORTED`
- `FULL_FLT_NATIVE_SUPPORTED`

Causal method reuse remains a later prospective gate requiring process restart, a fresh fixed task,
an actual learned-method retrieval+execution event in the native search path, and a matched ablation.
Mere storage/final-proof appearance is insufficient; primitive aliases must be reported as
`METHOD_IS_PRIMITIVE_ALIAS`.

## Reproduction

```bash
PYTHONPATH=src python -m pytest -q \
  research/flt-kso-v1/test_flt_kso.py \
  research/flt-kso-v1/test_anthropic_dag_edgecases.py \
  research/flt-kso-v1/test_f0.py

PYTHONPATH=src python research/flt-kso-v1/run_f0.py --out /tmp/f0.json
PYTHONPATH=src python research/flt-kso-v1/run_r1.py --out /tmp/r1.json
python research/flt-kso-v1/validate_anthropic.py /path/to/frozen/fermats-last-theorem
```

A missing exact Lean checker or custody primitive produces an explicit `CANNOT_CHECK_*`; it is not a
positive theorem result. No result JSON or qualification receipt is reusable across source drift. If
`main` moves, replay/rebase the intended change and requalify on the actual source.
