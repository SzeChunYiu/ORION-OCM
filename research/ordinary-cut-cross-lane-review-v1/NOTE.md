# Cross-lane syntax completeness and comparability

At main commit b5dfd93746be56d124af92be6564bb6d905efd51, the replay records
44 alias-positive and 32 negative statuses across all 76 proposals/full 4323 P1.
**The 32 complete-negative claims lack a demonstrated syntax-completeness warrant.**
This review does not establish that any particular recorded negative is false.

Immutable tree: 47a93eee0fc73b2b06864e8cb597bce6e8ccb2ce.
[SOURCE-BINDINGS.json](SOURCE-BINDINGS.json) pins the four successor modules,
exact matcher donor and result/process/prose. No theorem, parser or control ran.

## Why complete negatives are unqualified

p1_syntax.py caches by (kind,index). In-progress recursion returns empty;
depth > 24 also stores empty. Neither records UNKNOWN, truncation or a grammar
restriction. Depth is absent from the key, so a result first reached deeply
can be reused by a shallower caller without regard to remaining search depth.

A by-hand grammar example illustrates the missing assumptions: the admitted linear
rule wff -> wff x plus parameter V0:wff derives V0 x; recursive re-entry at the
same start is suppressed, and no fixed-point pass grows the base parse.
Likewise, 25 nested applications of wff -> ( wff ) need only 51 tokens but hit
the depth refusal before the inner parameter. These are abstract source witnesses,
not tests of retained proposals or claims about the actual selected P1 grammar.

p1_syntax.proof raises the same ValueError for no derivation and its input boundary.
typed_grammar.checker passes it through. The exact typed_alias.match donor catches
ValueError and caches False as an ordinary type mismatch. A substitution's syntax
search refusal can therefore disappear inside matching; the outer alias_screen
exception list cannot recover that lost reason.

alias_screen declares coverage from not unknown, without a syntax-completeness
certificate. All ground queries being admitted and all P1 rows being visited do
not establish completeness for every typed substitution checked inside those rows.
The syntax filter also skips unsupported contract forms without a coverage
disposition; the permitted grammar needs an explicit scope.

Thus RESULT.md's deduction that these queries are not one-step P1 theorems,
and the semantic reading of MIXED_ALIAS_AND_NEGATIVE, need qualification.
Defensible wording: **44 retained proof-ready alias records and 32 reported
negative statuses whose completeness is unqualified**. Existing positive witnesses
can be retained on their structural-replay authority; this review does not replay
them or grant native admission.

## Comparison boundary

Replay-02's self-produced PROCESS/RESULT record PID 57045, Python 3.14.6,
macOS ARM64 and 366.067276666 seconds wall / 347.703923 user seconds.
That differs from the registered Linux/Python 3.11 attempt and exceeds both
its 60-second shared work window and 180-second outer containment.

Replay Work enforces 2,000,000 matcher states only, with no elapsed-time checkpoint.
The 60/180 fields report predecessor values; this code does not enforce them.
Recorded 1,773,758 states and 328,548 parent visits are useful counters, but do not
make this a matched-time comparison. The capsule acknowledges the exceeded walls.
PROCESS is emitted by replay itself, not an independent Popen/wait4 receipt.
No broader process-custody or speedup conclusion is asserted here.

## Smallest assimilation step

Preserve immutable source and outcomes. Before treating negative statuses as
semantic nonalias evidence, use distinct UNKNOWN for unsupported, depth/cycle or
resource refusals and require a complete supported syntax method. The reviewed
contract-derived Earley witness adapter is an established parent to reuse.

A future comparison should retain full population/order/P1 and historical costs
under a separately bound common runtime/work contract. Do not use these 32 statuses
as certified negative training or discovery eligibility. No specific row is
relabeled false, and no experiment or execution gate is authorized by this note.
