# PR90 digest compatibility repair

**The stale digest regression is repaired under the existing metadata API.**
Base: PR90 head 52d3be2938a3576fb2777bfcb5d415b397db0286.
Only KnowledgeSpace.digest and its implementation-specific cache test changed.
Lookup views, evidence-universe caching, local validation, workflows and all prior receipts
remain as authored on that branch.

The frozen dataclass does not recursively freeze Atom.meta or Hyperedge.meta.
Nested dictionaries/lists can change through input aliases or public as_dict() aliases.
The removed per-instance digest cache retained the old hash after those accepted changes.
The repair recomputes the same canonical serialization/hash on each digest() call.
It introduces no metadata freezing, copy semantics, new API or global cache.

The replacement test adopts the independently reviewed eight-case contract:
unchanged repeat; atom/edge nested input aliases; atom/edge exported nested aliases;
fresh constructor after mutation; fresh with_atoms and with_edges generations.
Each case compares against an independently encoded current canonical JSON SHA256,
and verifies that the intended serialization change actually occurred.

- Before repair: 4 failures and 8 passes in the 12-case file; exactly the four alias cases failed.
- After repair: all 12 pass (0.03 s).
- All M1 tests: 69 pass (38.62 s), including the 12-case file.
- No skips/errors in either green run.

original-review/ preserves the prior exact-source baseline 8/8 versus PR90 4/8 diagnostic,
including raw observations/source bindings. It is historical failure evidence.
red.xml/log, green.xml/log and m1.xml/log preserve this repair's actual executions.
verification.json binds executed source/tests, commands and JUnit counts.

Classification: INFRASTRUCTURE; owner existing #72/#70 and PR90.
This restores content identity; it claims no speed improvement or scientific promotion.
No main merge, current engineering recorder or full-suite qualification occurred in this repair.
Current receipt selection requires qualification after the parent integrates the final source.
