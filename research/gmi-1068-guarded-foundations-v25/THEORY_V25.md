# V25 theory — information needed by the registered process observer

## 1. Scope and notation

Composition is written in execution order: m(x,y) executes x, then y.
Failure is None, distinct from every successful some(x). No default output erases
that tag. An arrow carrier may be empty. Equality of observations includes failure
and the actual labelled output, not just successful cardinalities.

A V19 Algebra on A consists of m:A×A→Option A with strong partial associativity,
local true units and coherence. A true unit e satisfies m(e,e)=some(e), and every
defined m(e,x) or m(x,e) returns x. Every x has such left and right units. Coherence
requires m(x,y) and m(y,z) both defined to imply m(m(x,y),z) defined.
Strong associativity is equality of Option binds, including definedness.

V19 derives unique local units l(x),r(x), and
m(x,y) is defined iff r(x)=l(y). Its category has true units as objects and arrows
with these endpoints. Conversely actual bundled category arrows have this partial
operation. These constructions commute through explicit object and arrow maps.
V25 reuses those theorems; it supplies the previously missing complete observer
bridge and common-interface recoverability statement.

## 2. Y1 — anchored tree interpretation

[HISTORIES §1–4](HISTORIES_V25.md) proves arbitrary bracketed tree observation
agrees with actual V19 folding after every Empty(o) becomes the identity arrow at
o. This includes failed joins and actual V11 nullary paths. Dropping empties is
not an admissible encoding. The proof uses strong Option associativity, not merely
agreement when both bracketings happen to be defined.

## 3. Y2 — common-interface information equivalence

[INFORMATION §1–5](INFORMATION_V25.md) fixes ambient labels L, admits a possibly
empty subset S, and uses an actual V19 Algebra on S. The padded table records
None outside S. Local units derive S from its nonempty rows. The raw observer
checks membership of arrow leaves and genuine unit legality of empty anchors.
For arbitrary encoders on arbitrary families of these presentations, raw observer
recovery is equivalent to padded-table recovery, with decoders only on attained
codes. This is a factorization theorem about retained information; it gives neither
a shortest code nor independent necessity of stored table cells or named fields.

## 4. Y3 — six survivor requirements

[CONTROLS](CONTROLS_V25.md) gives actual loss witnesses for all six original rows:
typed definedness, process availability, composition, internal neutral behavior,
strong associativity, and neutral insertion laws. The [row ledger](SURVIVOR_LEDGER_V25.json)
records precisely what was removed and which other premises survive.
TYPE and IDENTITY fields may be reconstructed. Removing a law is different from
erasing a field. Coherence is an additional explicit admission requirement.
These corrected witnesses do not purport to establish six independent coordinates.

## 5. Y4 — external names and commuting encodings

[ENCODINGS §1–4](ENCODINGS_V25.md) proves tree observations commute with the
actual V19 maps in both directions. With fixed external object names O, an identity
map O→L is additional observable information. A NamedPresented supplies such a map
landing in true units; bijection onto all units is needed for a complete category
presentation. Named-observer recovery is equivalent to recovery of the pair
(padded table, identity map). A same-table swapped-map collision supplies the
negative control and retaining the pair supplies its constructive repair.

## 6. Proof and scientific boundaries

The general statements above have paper proofs in the linked details. Exact Lean
coverage is governed by the final FORMAL_SCOPE and typed contract; finite Python
calibration never proves the arbitrary-family theorem. The executable named API
may enforce complete bijective presentations even where a theorem only needs
unit landing. Equality is relative to the retained ambient query/output interface.

The category/path mechanisms are classical. V9 supplies the attained-image fiber
criterion; V19 supplies reconstruction and its law countermodels. This is a repair
of their integration into original registered requirements, not a new category theorem.
Physical adequacy, optional higher cells, process admission selection, universal
objectives and all-machine derivation remain outside this result.
