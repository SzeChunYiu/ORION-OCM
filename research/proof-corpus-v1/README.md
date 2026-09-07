# Canonical lexical proof-corpus inventory

This package reconciles the broad wrapper coverage of PR #129 with the pinned
Git custody and graph checks of PR #132. It inventories existing source objects.
It does not construct a solver view, choose holes, export Lean declarations,
perform learning, call a neural service, or run proof search.

**Qualified result:** [all 29,511 declared wrapper/solution pairs are accounted
for](RESULT.md), with zero refusals and an independently checked lexical import
graph. Semantic closure remains NOT_ESTABLISHED; no Lean/proof/selection ran.
README and RESULT are post-run documentation; the archived executed snapshot
and its failed/successful receipts remain immutable.

- [Limitations and next boundary](LIMITATIONS.md)
- [Pinned predecessor records](provenance/PREDECESSORS.json)
- [Custody and cost interpretation](provenance/README.md)

## Fixed public source

- [Anthropic corpus](https://github.com/anthropics/fermats-last-theorem/tree/aa2d8b34692b16c70f699536de0d8e75b9a3e9ef)
  at commit aa2d8b34692b16c70f699536de0d8e75b9a3e9ef.
- Expected 29,511 wrapper/solution pairs.
- Declared Lean leanprover/lean4:v4.33.1 and Mathlib
  db584cd6d46c92f209a44c0f1c829460d327499d are checked as source metadata.
  This package does not install or execute them.

## Operation

Run on the Linux laptop with the stable Python 3.11.14 interpreter. The repository
must already contain the pinned objects. The program never fetches or checks out
source; the output directory must be fresh and evaluator-only.

After source freeze and authorization for the full global inventory:

`python3.11 audit.py --repo /existing/local/corpus --out /new/evaluator/receipt`

Only those two arguments are exposed. Library-level commit/count parameters
exist to exercise small authored Git fixtures. A report identifies their exact
values; a fixture result is never a public-corpus qualification.

Exit 0 means the declared lexical inventory and pair/import graph checks passed.
Exit 3 is an explicit cannot-check result; argument errors exit 2.
A missing/unwritable output location is an operational exception, never success.

## Recorded artifacts

| File | Meaning |
| --- | --- |
| CODE_SOURCE.json | Own package file hashes, including tests and provenance |
| CORPUS_SOURCE.json | Pinned commit/tree and each listed path/blob/hash/read state |
| WRAPPERS.json | Every examined wrapper, accepted or refused, with raw hashes |
| SOLUTIONS.json | Every examined solution's lexical imports and raw hash |
| GRAPH.json | Pair-checked acyclic theorem-import graph, only when checks pass |
| REPORT.json | Terminal, row accounting, artifact bindings, resource scope |

Wrapper records preserve exact context, declaration, bridge and trailing bytes.
Their concatenation reconstructs the original wrapper. This context can contain
helper proofs and remains evaluator-only. Raw solution proof bodies are streamed
and hashed but are not retained in these output files.

Rows are accounted as listed, examined, accepted, refused and unread. A lexical
failure does not stop examination of later rows. An acquisition failure preserves
partial accounting; failure before tree enumeration leaves row counts unknown.

## Controls

`python3.11 -m unittest discover -s tests -q`

Controls cover the observed format failures, exact bridge-to-pair binding,
nested comments/strings, let/letI/default assignments, graph cycles/dangling
imports, replacement refs, dirty files, framing/hash mismatch, source drift,
partial acquisition and no-selection CLI behavior. They use small authored
local Git objects and do not compile Lean or inspect public proof targets.

## Ownership

This directory owns corpus inventory only. The mechanical proof/runtime lane
owns F0 proposal and proof-runtime integration. A separately commissioned Lean
environment exporter must establish semantic closure before hidden-region work.
Do not merge or activate predecessor selection/staging orchestration through this
package. Familiar lexical parsing and Git/index checks are parent-sufficient
engineering, not evidence of OCM novelty.
