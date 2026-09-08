# Syntax-witness adapter preconditions

This is a bounded interface/design review, not successor source acceptance or an
execution gate. Only the three frozen consumer interfaces below were read.
No reviewed imports, tests, native/audit/alias execution or corpus read occurred.
Map the obligations below to existing authored controls; add only uncovered cases.

## Frozen source boundary

All paths are under ordinary-cut-opportunity-v1/consumer-v3.

| Source | Bytes | SHA256 |
|---|---:|---|
| donor/typed_alias.py | 3979 | bee31a4cd2f29e3be91c4fecf3fff13db9775f5010462d0137018ae6a0858190 |
| donor/typed_grammar.py | 1221 | 4790b648077d20af79835a5c1bca5d4281e8a7c96a0a58aeb55e69e3b3651a67 |
| alias_screen.py | 3992 | ed16b2cd299aeebf0594e22d184ff4ccd6bee9eae5416bf96119bf3766849055 |

`typed_alias.match:26-27` catches every ValueError from syntax and caches False.
This is an actual control-flow fact, not evidence that the new adapter fails.
`alias_screen:38` constructs its checker outside its ground-guard exception block;
its per-assertion catch at 59 also does not include a new RuntimeError subclass.

## Required failure contract

| Syntax decision | Required meaning at the unchanged matcher seam |
|---|---|
| Witness ready | Exact requested type/token vector has a structurally replayed proof using allowed contracts and local leaves. Return success. |
| Certified nonmembership | Complete supported grammar and exhaustive successful recognition establish this vector is not in the requested type. Only this may raise ValueError and be cached as False. |
| UNKNOWN | Unsupported contract/input, incomplete grammar, parser construction, conversion/replay failure, unresolved ambiguity or resource failure. Raise a distinct exception that does not inherit ValueError. |

`SyntaxUnknown(RuntimeError)` is a sufficient small interface. The future screen
must catch it at grammar construction, ground validation, matching and proof
emission. Preserve the reason and set completed query/screen coverage false.
Do not rewrap it as ValueError inside the callback or cache it as a type failure.
A parser/work counter that itself raises ValueError also needs this translation.

Grammar support and completed query coverage are different facts. A fully
supported grammar can still have an UNKNOWN query after resource or witness
failure. Separate fields or explicit names must make that distinction clear;
UNKNOWN cannot carry an unqualified complete-query/complete-screen flag.

A known positive proof may survive unrelated UNKNOWN comparisons with incomplete
coverage. An empty alias list is a complete negative only after every required
comparison completed in the declared domain. Grammar construction failure cannot
be interpreted as an empty grammar or a completed negative.

## Contract-to-grammar and proof obligations

1. Bind the complete allowed syntax-contract inventory and local parameter context.
   Do not silently discard relevant unsupported productions when certifying
   nonmembership. A constructive valid witness can remain usable despite them.
2. A Metamath syntax assertion is not automatically a plain CFG production.
   Repeated variables require equal substitutions; omitted mandatory variables
   leave proof obligations. Either support those conditions exactly or report
   the rule form unsupported. Linear rules containing every mandatory variable
   exactly once are a sufficient initial subset, not a completeness theorem.
3. Preserve original token boundaries and literal identities. Lexer longest-match,
   whitespace joining or punctuation filtering must not merge, split or erase
   Metamath tokens. Any internal encoding needs an exact reversible token map.
4. Emit child syntax proofs in the contract floating-hypothesis order, even when
   textual variable occurrence order differs. Bind original labels, types and
   local leaf identity; retain nullary rules and unit conversions when supported.
5. Replay every returned witness to precisely `[wanted_type] + original_tokens`.
   Validate stack arity, ordered floating types, shared substitutions, allowed
   contract kind, essential/DV restrictions and the final singleton stack.
   Recognition alone does not grant native acceptance or a usable proof witness.
6. One finite replayed witness suffices despite ambiguity. Default tree choice is
   not an exhaustive search over alternative witnesses: if its conversion fails,
   find a valid allowed alternative or return UNKNOWN. Do not call it nonmembership.
   Cycles and truncated forests require a terminating witness policy or UNKNOWN.

## Minimal falsifying obligations

| Control obligation | Falsifies |
|---|---|
| Known composite alias plus clean closed-domain nonalias; repeat one variable across conclusion/premises | Adapter that avoids false negatives by making everything UNKNOWN, or changes the conventional matcher. |
| Force SyntaxUnknown inside a would-match type callback and genuine nonmembership separately | ValueError swallowing uncertainty or treating an invalid slice as global uncertainty. |
| Unsupported relevant syntax rule: keep an independent valid witness, but refuse an unsupported complete negative | Silent grammar narrowing and loss of constructive positives. |
| Reordered floating declarations, a nullary constructor and a type-conversion witness; reject unsupported repeated/omitted-variable rules | Text-order emission, invented leaves, or unsound CFG translation. |
| Token-prefix collision and an ambiguous/cyclic grammar with a finite valid witness; conversion failure remains UNKNOWN | Lossy tokenization or mistaking one failed derivation for no derivation. |
| Construction, replay and numeric resource refusal at their actual exception seams | UNKNOWN swallowed as invalid type; a coverage flag claiming completed recognition after refusal. |

These are authored helper controls, not a request to reopen or re-screen retained
rows. Existing controls can satisfy multiple obligations. Future isolated screen
entry and parser import custody require their own bounded qualification.

## Resource and integration boundary

Keep the full P1 and existing one-step assertion/premise semantics unchanged.
The registered matcher state count and 60-second soft bound do not automatically
measure Earley grammar construction, recognition, forest conversion or replay.
Record those costs separately with explicit finite refusal conditions; do not
report absent counters as zero or sum nested time windows as lifetime cost.
A 512-token adapter boundary is a prototype support/refusal boundary: affected
queries remain UNKNOWN. It does not replace or silently revise the registered
two-million matcher-state / 60-second protocol or authorize another execution.
Pin the actual parser package/runtime and source dependency set before execution.

## Primary parser read scope

Lark documents Earley dynamic lexing as longest-match per terminal;
`dynamic_complete` also explores token-length alternatives. A lossless encoded
token stream can avoid those lexical ambiguities without requiring that option.
Its default derivation selection is distinct from explicit/forest ambiguity
handling. See [Parsers](https://lark-parser.readthedocs.io/en/stable/parsers.html).

The [API reference](https://lark-parser.readthedocs.io/en/stable/classes.html)
distinguishes parse errors (`UnexpectedInput`) from parser configuration and
conversion concerns, and documents ambiguity/tree-filtering options. Mapping
parse failure to nonmembership still depends on our grammar-coverage preconditions.

The [SPPF guide](https://lark-parser.readthedocs.io/en/stable/forest.html)
documents cyclic forests and visitor cycle notifications. It does not certify our
proof conversion or automatically bound its work. These stable docs were read on
2026-09-08; they do not replace a pinned-version implementation/control receipt.
