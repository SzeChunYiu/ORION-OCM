# Syntax coverage API successor

This source-only correction separates grammar support from the outcome of one syntax query.
It does not wire the ordinary screen or evaluate the retained 76 proposals.

- **grammar_coverage_complete:** every supplied syntax contract has a supported compilation.
- **coverage_complete:** grammar coverage is complete and the query ended in a completed
  supported decision: SYNTAX_PROVED or NOT_DERIVABLE_REGISTERED_GRAMMAR.
- **UNKNOWN:** coverage_complete is always false, including input, resource and replay refusal.
- A replayed positive witness remains usable under incomplete grammar; its two coverage
  flags remain false. Unsupported grammar never establishes negative type membership.
- Only completed supported nonmembership raises ValueError through checker.
  UNKNOWN still raises SyntaxUnknown, which is not a ValueError.

The existing 512-token input boundary is an explicit syntax-prototype domain boundary.
Crossing it yields UNKNOWN. It does not replace the registered 2,000,000 matcher-state
and 60-second soft study bounds. No resource threshold or proof/parser behavior changes.

PATCH.diff is the complete production delta. The three other source files are exact copies
of the original dependencies; the same pinned Lark 1.3.1 runtime is reused from the parent.
Nine focused authored controls cover the affected metadata and exception boundaries.

The original 17-control suite is not rerun or retroactively requalified. Its PROCESS records
51 source/runtime pins but omits the dynamically imported legacy reproduction source
from before/after pins, and does not record actual cwd/module paths. Current legacy bytes
were independently read back as matching their historical pin. New controls record actual
cwd, all file-backed imported module paths, and their complete before/after source coverage.

The original DESIGN.md's syntax restrictions refer to the documented Metamath $j
syntax-tool convention, not restrictions imposed by the core native proof verifier.
This additive clarification preserves the historical document unchanged.

Qualification results and their exact source/custody records will be bound in
SOURCE-REVIEW-REQUEST.json. No native acceptance, alias result or new study is claimed.
