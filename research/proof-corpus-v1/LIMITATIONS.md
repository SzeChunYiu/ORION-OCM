# Exact scope and the next boundary

## What a passing inventory establishes

The declared local commit is read through Git objects. Commit and every traversed tree
payload hash are checked, and every selected blob is checked against its Git
object identity plus SHA256. Dirty files, replacement refs and untracked paths
do not supply source. No remote fetch is attempted.

The selected roots are Theorems, P2M, Definitions, FinalCheck.lean and the pinned
toolchain/package metadata. All selected regular files have inventory records.
Each expected wrapper/solution module pair is present, and each accepted wrapper
contains one recognized bridge to its own expected solution constant.

The lexical scanner preserves nested comments/string positions, all recognized
line import commands, ambient source context and raw byte hashes. It tolerates
additional definition imports and preambles, helper declarations, let/letI and
assignment expressions in types. Supported Unicode/prime identifier boundaries
and escaped identifiers do not become command tokens. This remains a lexical
subset; unknown layouts refuse explicitly. A trailing #p2m_type_eq_warn directive
is retained as unevaluated metadata and grants no type-equivalence authority.

The graph records deduplicated Theorems.Thm_* imports in solution modules.
Kahn's algorithm checks that this graph is acyclic and has no dangling pair
references. Direct solution-to-solution proof imports and unknown theorem-module
layouts refuse. Context imports remain recorded separately.

## What it does not establish

This is not a Lean parser, elaborator or proof checker. A recognized lexical
bridge is not checked for definitional equality, correct argument inference or
the intended mathematical meaning. A .solution reference is not evidence that
the solution declaration type is right. Names and source slices are not LeanExpr.

The graph is a theorem-module import graph, not an elaborated proof-support
graph. Dependencies through Definitions, instances, helper declarations, notation,
macros, inductives, recursors or auxiliary declarations are not resolved here.
No negative semantic conclusion may follow from absence in this graph.

Wrapper context may itself contain proof text. These records must never be
passed as a sanitized hidden-region solver input. No hole has been chosen and
no source has been staged for a solver. Inventory coverage is not a hidden
support reconstruction result, theorem-only strategy result or transfer result.

Git is the trusted local object reader. This package checks content identity;
it is not a hostile-process sandbox or an independent Git object database.
Resource measurements cover global inventory work, not kernel checking or
future acquisition/build costs. No warm-query scaling inference follows.

## Minimum separately qualified successor

Before a hidden-region experiment, an exporter must preserve:

1. Canonical elaborated target type, universe parameters and exact declaration
   identity, bound to the source statement and patched toolchain/environment.
2. Definition, instance, helper, inductive/recursor and auxiliary dependency
   closure, with the allowed boundary library explicitly declared and checked.
3. A solver-visible environment that cannot obtain hidden proofs through imports,
   context, caches, generated files or substituted axioms.
4. Independent type/definition correspondence checks and kernel replay of any
   candidate; a missing closure must produce CANNOT_CHECK, not a guessed target.
5. Separately tested filesystem/network/cache containment and complete cost
   accounting for export, construction, search, verification and reuse.

Preserve the historical Lean 4.19 replay records. Selecting and qualifying a
patched successor does not retroactively invalidate those fixtures or silently
replace their toolchain. Corpus import engineering precedes any new theorem claim.
