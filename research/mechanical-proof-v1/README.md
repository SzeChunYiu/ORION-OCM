# Mechanical proof construction — exposed F0 apparatus

This separate research package constructs a small proof by deterministic symbolic
search and checks it against an independently fixed Lean theorem. It contains no
neural learner, embedding or model call. The existing
[fixed proof replay](../proof-replay-v1/README.md) remains historical evidence.

Read [the mechanism and trust boundary](PROTOCOL.md),
[the commissioning result](RESULT.md), then the linked raw records.
The [FLT programme](../programme/FLT_RECONSTRUCTION.md) defines the subsequent gates.

## What the apparatus does

1. Supply a closed goal, numeric constant signatures and explicit search bounds.
2. Introduce leading binders and enumerate a type-indexed application closure.
3. Return a closed term as data; `FOUND` is only a proposal.
4. Translate the permitted constructors in a separate trusted process.
5. Rebuild the pinned Foundation, target and candidate under Lean 4.33.1.
6. Accept only the exact target with a fresh artifact and registered axiom audit.

The checker permits only `propext`, `Classical.choice` and `Quot.sound`; the actual
axiom list is recorded. The constructed development proof uses none of them.

The exposed target expresses membership refinement followed by agreement. Its
direct proof is `agreement actual (subset actual member)`. Ordinary symbolic
methods suffice. This commissioning is **PARENT_SUFFICIENT** apparatus evidence;
it establishes no learning, FLT reconstruction or comparative performance result.

## Source map

| Responsibility | Files |
|---|---|
| Typed data, substitution, checking | `f0_terms.py` |
| Indexed finite application search | `f0_search.py` |
| Public task and controlled variants | `f0_fixture.py`, `Target.lean` |
| Closed learner and import/dispatch audit | `worker.py`, `worker_guard.py` |
| Process containment and cleanup | `isolation.py` |
| Copied runtime and dependency inventory | `runtime_bundle.py`, `runtime_recipe.py` |
| Trusted rendering and exact-target checking | `lean_transport.py`, `proof_check.py`, `kernel_check.py` |
| Source-bound episode and control matrix | `episode.py`, `commission.py` |

## Operating the registered apparatus

Use Linux x86_64 and Python 3.11 on **billy-laptop**, never the Mac. The recorded
runtime manifest binds the qualified copied Python, Lean and individual shared
libraries. Bubblewrap is separately pinned by `isolation.py`; an arbitrary newer
installation is not automatically equivalent. Refusals preserve their records.

From the repository root, using the qualified Python interpreter:

```sh
python -B research/mechanical-proof-v1/commission.py \
  --runtime-manifest /absolute/path/to/runtime-manifest.json \
  --runtime-sha256 REGISTERED_MANIFEST_SHA256 \
  --out /absolute/path/to/new-commissioning-directory
```

The output directory must not exist. Prepare a new runtime with
`runtime_recipe.prepare_runtime(archive, python_prefix, destination)` from the
pinned official Lean archive and reviewed Python prefix. Review and register its
manifest digest before commissioning. Changed runtime bytes require qualification;
the historical manifest is not a reusable receipt for another machine.

Top-level controls can run with:

```sh
python -B -m pytest research/mechanical-proof-v1 \
  --ignore=research/mechanical-proof-v1/records -q
```

The native containment/runtime controls require the registered Linux environment.
Hosted CI runs the portable source/protocol controls explicitly; it does not claim
to repeat the native kernel commissioning or qualify a different Bubblewrap build.
Archived source snapshots are evidence, not additional tests to collect.

Each run records all assigned cases, including refused and unexecuted cases,
runtime/source bindings, declared inputs, raw process streams and actual costs.
Prior development failures are retained separately. No result authorizes promotion
to a broader proof grammar, library, no-neural acquisition contract or FLT stage.
