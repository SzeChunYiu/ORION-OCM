# FLT-KSO v1: proof-route prerequisites, not N4 acceptance

Ownership: #62 / #38, with #115 execution accounting. Roadmap #42 and the
**LOCKED #46** gate are unchanged. Main #128 (787a5d2c) adds the governing
`research/programme/NO_NEURAL_CONTRACT.md` and F0–F4 protocol. This exposed
R1-named development task is an F0 prerequisite, not completion of F0. This is an additive successor, not a rewrite
of the Lean-4.19.0 `research/proof-replay-v1/` record.

## Implemented scope

`native.py` implements a small deterministic, bounded propositional proof search:
implication introduction/application, local exact use and conjunction construction.
It returns a proof AST, not proof warrant. The inspected native search module has no model, API client, embeddings,
external proof donor or task-specific FLT branch. The source-emission language
accepts only those AST constructors, imports `Init`, and requests an axiom audit.

`ocm_adapter.py` uses the real `OCMRuntime`, `KnowledgeSpace`, warrant algebra,
`SolveOperatorIndex`, `ResourceVector`, durable event log and canonical solve loop.
An open obligation is an UNKNOWN `goal` composed through the existing proposal
path. Its exact statement/environment descriptor is a `query_seed` in the same
field. A registered grammar is a `procedure`; attempts are `observation` objects;
only a fresh checker-issued result may support a `proof` and `claim`. Status is
computed from live checked support, not a planner score or an FLT-specific Boolean.
Ordinary instruction admission does not grant truth to an open theorem.

`kernel.py` checks the independently pinned Lean 4.33.1 Linux archive and every
extracted runtime file. It uses fresh work directories, a cleared environment,
process-group deadlines, exit/output capture and false-proof/axiom/sorry controls.
The R1 kernel profile is **Lean.Init only**. Mathlib is not silently assumed
installed. Full runtime hashing is costly global work and is explicitly counted.
The Python host and installed OS are trusted; this is not hostile arbitrary-code
confinement or independently authenticated execution attestation.

`campaign.py` first creates an exclusive source-inventory-bound launch record,
then reruns the original R0 checker and attempts the prospectively registered R1
DEVELOPMENT target. A missing R0 kernel permits only a native proposal diagnostic,
never an R1 positive. Both OCM and the parent execute the identical grammar/search
with the same empty theorem cache and budget. Kernel acceptance, persistence,
restart, withdrawal and restoration of checker support are separate checks.
A tied result is `PARENT_SUFFICIENT_FOR_KERNEL_CONSTRUCTION_ONLY`, not an OCM residual. This parent
is strong for this restricted fragment, not yet a full Prove2Me-style FLT parent.

Prospective registration: issue #62 comment 5562227033. Target:

```lean
∀ P Q R S : Prop,
  (P → Q) → (Q → R) → (P → S) → P → (R ∧ S)
```

This target is public to the implementer, not an independently protected held-out
family. Search is capped at 256 expansions and depth 24. Exact candidate proof text
is not supplied to the native mechanism. This does not test learned methods.

## Anthropic evaluator preparation

`import_source.py` reads **Git objects**, not mutable working-tree content, at
`aa2d8b34692b16c70f699536de0d8e75b9a3e9ef`. It verifies the Lean/Mathlib pins and
Git blob identities, audits every supplied wrapper and requires all 29,511 pairs.
The full evaluator read/materialization is charged as global preparation.
Unsupported syntax produces an explicit coverage refusal, never a guessed type.
`substrate.py` has a position-preserving nested-comment scanner and a strict
wrapper grammar. It extracts multiline signatures and the syntactic import DAG
from solution imports. This is **not** kernel elaboration or an exact logical
proof-dependency graph. A full-source audit must pass before coverage is claimed.

Theorem wrappers import their own solutions, so they are never copied to the
public package. Public JSON contains statements and unresolved boundary
certificate requirements. It contains neither proof bodies nor dependency edges.
Private JSON contains source/proof identities and evaluator topology. Staging
paths must be new and disjoint. The public and private content hashes are bound.
A deterministic, registered hash-ranked root/ancestor rule selects the tiny staged
hole; no result-based reselection is permitted.

**Staging is not sealing.** Public packages remain `STAGED_NOT_EXECUTABLE`.
`guard.py` rejects hidden imports, undeclared public files and path overlap, and
refuses even clean R2/R3 staging with `CANNOT_CHECK_ISOLATION_AND_BOUNDARY`.
No bypass flag launches an unconfined solver. Kernel statement elaboration,
allowed-definition closure, verified boundary modules and a tested OS isolation
backend remain missing. Token filters are defense in depth, not a sandbox.
No `html/`, original wrapper, solution module or unproved Lean axiom is emitted.

## Running

From the repository root, with its declared development environment:

```sh
PYTHONPATH=src python -m unittest discover -s research/flt-kso-v1 -p 'test_*.py'
PYTHONPATH=src python -O -m unittest discover -s research/flt-kso-v1 -p 'test_*.py'
PYTHONPATH=src python research/flt-kso-v1/campaign.py prepare --out /tmp/LAUNCH.json
PYTHONPATH=src python research/flt-kso-v1/campaign.py run \
  --launch /tmp/LAUNCH.json --out /tmp/flt-r1-new-run \
  --archive /path/to/lean-4.33.1-linux.tar.zst \
  --r0-archive /path/to/lean-4.19.0-linux.tar.zst
python research/flt-kso-v1/import_source.py \
  --checkout /private/frozen-anthropic-git --out /private/new-audit
```

Archive URLs, sizes and hashes are in `MANIFEST.json`; R0 retains its original
manifest. Acquisition itself is external to the no-network native search.
Each launch is exclusive and binds the current source files. Results from a
changed inventory cannot qualify a successor. A new registration/launch is
required after source changes. Full engineering and M1–M12 checks are additional
gates; research code is covered by its own source inventory and focused tests.

## Claim boundary and next missing capabilities

Even a positive kernel-construction result terminates scientifically at
`CANNOT_CHECK_MECHANISM_BOUNDARY` until #128's isolated closed executor,
transitive import/dispatch controls and restored-state hostiles are qualified.
The symbolic module's zero model calls do not establish a whole-runtime neural
absence guarantee. The current code deliberately has no promotion bypass.

No R2/R3 reconstruction, subgoal invention, learned-method acquisition, causal
later consumption, failure-memory benefit, sparse scaling, major component,
known-route FLT or full native FLT is claimed by this implementation. The current
canonical solve performs global navigation; conservative touched state is N.
Warm indexing is not substituted for complete costs. Unmeasured bytes read,
peak process-tree RSS, energy and development costs remain unknown.

A failed search remains failure of this grammar/state/budget, not mathematical
refutation. Kernel acceptance of the generated formal statement is separate from
an independent informal-statement correspondence warrant. No `REFUTED` theorem
terminal is implemented in this tranche. The first future learning gate still
requires a genuinely acquired, non-primitive-alias method persisted in this same
field, retrieved and executed after restart on a prospectively fixed fresh task,
with a matched ablation. R4–R8 remain unrun and #46 remains locked.
