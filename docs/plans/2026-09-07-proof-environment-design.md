# Proof environment: implementation decision

The previous goal turn was progress: PR134 merged, and its native/runtime/corpus
records were verified against live main. Current main remains9b00cfe on2026-09-07.
The full scientific/papers objective remains active; environment engineering alone
does not establish method learning, FLT reconstruction or novelty.

## Choice

Adopt the native lean4export data path and Lean's checked Environment.replay,
with comparator parser/closure mechanisms where useful. Preserve exact upstream
source/license attribution and qualify any adaptation under Lean4.33.1.
Add OCM-specific task registration, permitted-declaration selection, comprehensive
dependency accounting, independent target binding and isolated process custody.

Alternatives considered:

- Filtering source files/imports alone leaves aliases, compiled proofs and hidden
  dependencies accessible. It cannot supply the required semantic boundary.
- A new small proof AST would repeat F0 and discard mature support for universes,
  opaque values and inductive families. It would postpone actual Mathlib use.
- The mature kernel format retains those structures. Its parser/replay still need
  explicit unsafe/partial rejection, complete closure and exact membership checks.

## Required behavior

An evaluator exports the source environment and registers the target independently.
The allowed packet contains selected safe declarations and their checked closure,
with withheld roots and structural dependants removed. A fresh checker reconstructs
that packet from an empty kernel environment; it does not import the source library.
Every selected item, inductive family and implicit kernel dependency is accounted for.
Unsupported or missing coverage produces CANNOT_CHECK with the exact obstruction.

The candidate contributes only a parsed proof expression. Its own declarations,
axioms, imports or target assertion cannot extend the checking environment.
Final acceptance inserts a checker-owned theorem via Kernel.Environment.addDeclCore
using independently registered universes/type. Only actual kernel success and the
registered transitive axiom policy permit acceptance. Parser success is not proof.

Target data are bound independently of candidate data; original meaning and current
allowed declarations must agree. Preserve exact packet bytes separately from
parent-normalized expression identity and kernel conversion used to check a proof.
Development corrected the original strict Expr.equal requirement: independent
parent exports can intern alpha-equivalent expressions with different binder names
and annotations. Use the parent's kernel-term alpha equality for expression fields,
retaining full declaration metadata and ordered universes. This is not equivalence
of source-level binder interfaces. The strict failures remain in development records.

Explicit typed expressions avoid running arbitrary notation, macros, tactics or
instance search in the checker. Instance declarations still receive ordinary type/
value closure checks. Any exposed instance index has a separately stated policy;
do not claim arbitrary elaborator-extension reconstruction from kernel data alone.

## Process boundaries

Reuse the commissioned isolation helper and copied Lean4.33.1 runtime. Do not widen
the old F0 registry or mutate any historical runtime/receipt. Export/build processes
may see registered fixture sources; fresh checking and later proposing receive
only their approved packets, generic program and runtime. Private source, compiled
modules and exporter logs are outside those mounts. Hash each mounted artifact set.

All process return values require exact command/source/input identities, complete
stdout/stderr, intended result shape and cleanup. External time/output bounds remain
in force even where the parent replay uses unlimited internal kernel settings.
Account for export, compilation, preparation, replay, checking and retained storage.
Do not count logical denial caused by a missing executable or stale hash as a valid
semantic rejection. Keep historical failures and diagnosed successors separate.

## Qualification and scientific use

Commission on authored fixtures that exercise composition, polymorphism, definitions,
opaque bodies, custom inductive/recursor reconstruction and independent cold replay.
Test withheld roots, aliases/helpers, type/value dependencies, instances, opaque/
inductive dependencies, custom axioms, target/universe substitutions, incomplete
families, unsupported forms and physical source/cache exposure. The actual offending
dependency path and intended refusal layer must be retained.

This gate enables the next real-corpus semantic coverage and registered F1 masking
study. It does not replace that study with authored fixtures. Then proceed to actual
mechanical reconstruction, explicit acquired methods and causal held-out transfer
against equally informed, equally adaptive symbolic parents. No neural cognition.
