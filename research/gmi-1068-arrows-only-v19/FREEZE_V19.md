# V19 / S preregistration — reconstructing process information

Control plane: #1068; historical evidence: #833.
Planning parent: 49c7b6efacf65eab8ad11ad48a461b6d2e76bf32 (R, PR #1114).
Import merged R main ancestry before publication. This freeze precedes all S
outcome implementations, kernel proofs, tests, receipts and adjudication.
No original atom is eligible for closure in this round. This is a substantive
repair of the minimality argument, not a redefinition of original fulfillment.

## Original gap and registered reading

R1-001 is "minimize typed process structure"; R1-007 is "give loss witness
per survivor". The original freeze asks for removal/loss witnesses for each
retained component. Its TYPE and IDENTITY arguments confuse erasing named
fields with erasing information. A declared translation may reconstruct those
fields. V9 already proves generic attained-image recovery and total-unit
uniqueness; V11 already constructs paths, quotients and fixed-object-map
representations. Neither substitutes for the object-changing construction here.

The target is relative information sufficiency for an explicitly declared
operational interface. No signature-independent minimum, universal ontology,
physical substrate characterization or all-family intelligence recovery follows.
R1-001/006/007 remain UNKNOWN; no new qualified ledger revision is authorized
by this freeze. Preserve the existing two V16 qualified readings unchanged.

## S1 — arbitrary partial algebra, with the missing hypothesis exposed

For an arbitrary small type A, including the empty type, use an actual operation
m : A -> A -> Option A. Define Unit(e) from m itself:
m(e,e)=some(e), and every defined m(e,x) or m(x,e) equals some(x).
Require strong partial associativity, including definedness:
bind(m(x,y), u -> m(u,z)) = bind(m(y,z), v -> m(x,v)).
Require local units: each x admits units e,f with m(e,x)=some(x) and
m(x,f)=some(x). Require coherence: m(x,y)=some(u) and m(y,z)=some(v)
imply m(u,z) is defined. These are assumptions, not reconstruction conclusions.

Derive uniqueness of each left and right unit. Define l(x),r(x) by those
unique units and prove m(x,y) is defined iff r(x)=l(y).
Derive the units' own endpoints and endpoints of every composite.
Construct an actual TypedPathsV11.Category: objects are Unit subtypes,
arrows from e to f are x with l(x)=e and r(x)=f, and composition is the
defined value of m. Prove its category laws from the partial-algebra laws.
Use arbitrary carriers, not only a finite table or an assumed Category field.
Classical choice/decidable equality may support abstract construction; disclose
them. No effective reconstruction of arbitrary infinite inputs is asserted.

## S2 — converse and both roundtrips

For every lawful small TypedPathsV11.Category C on objects V, bundle all
arrows as Sigma a, Sigma b, C.Hom a b. Define partial multiplication exactly
when the middle endpoints match, transporting typed arrows along that equality.
Prove strong associativity, local units and coherence for that actual operation.
Derive the unit characterization: precisely the bundled identities.

Give a genuine object bijection a -> bundled(id a), typed Hom inverse maps
along that object bijection, and preservation of identities/composition.
V11's object-fixing CategoryIso cannot stand in for this changing-object result.
Conversely give inverse maps between A and all bundled arrows of its reconstructed
category, preserving AND reflecting the Option-valued partial multiplication.
Include empty carriers/empty object types; do not impose nonemptiness to simplify
the proof. Mathematical equality of dependent transports needs proof, not a
comparison of printed endpoint labels.

A mere multiplicative map need not preserve identity: a constant map from the
one-element monoid into the nonidentity idempotent a of {e,a}, with a*a=a,
is a control. The roundtrip maps are bijections reflecting the entire partial
table. Do not generalize them to arbitrary composition-preserving maps.

## S3 — exact operational interface and information theorem

Queries are nonempty raw arrow words and empty histories anchored at a
candidate unit. A nonempty word is evaluated by sequential partial composition,
returning none at the first undefined product; a singleton returns its arrow.
An empty history anchored at e returns some(e) iff Unit(e), and none otherwise.
These are total tagged responses on a common raw query space, including illegal
words and nonunit anchors; do not hide illegal cases in the query's type.

Prove preservation of responses under both roundtrips for arbitrary word length,
including anchored empty histories and failed composition.
For models on a fixed A, let table be the partial multiplication and responses
the complete query-response function. For every encoding code, prove
Recoverable(code,responses) iff Recoverable(code,table), using V9's attained-image
notion. The length-two query recovers m(x,y); table equality gives equal derived
unit predicates and all word responses. Register the actual evaluator, not an
uninterpreted semantic function assumed to determine the table.
This yields a least sufficient information equivalence class for this interface.
Coarser observations can admit smaller representations; no absolute minimality
or numerical primitive count is implied. All raw words includes intermediate
prefix queries, so preserving final observations does not conceal failed prefixes.

## Prospective finite calibration and falsifiers

Enumerate every Option-valued partial table on carriers of size0 through3.
The planning counts are1,2,81,262144, respectively; these are combinatorial
design sizes, not results. Independently compare the partial-algebra predicate
to a typed-category reconstruction criterion that derives endpoints separately.
Record counts of each law combination, accepted categories, units, objects,
composable pairs and actual reconstruction/response checks only after freeze.
For every accepted table, test all words through length4, all empty anchors,
both roundtrips and all carrier permutations. Both production and oracle must
compute actual operations independently; neither may call the other's answer.

Mandatory named controls, analytically specified before any run:
- Coherence alone: {e,a}, ee=e, ea=ae=a, aa undefined. Strong partial
  associativity and local units hold; coherence fails at (a,e,a). This is
  Cranch-Doherty-Struth Lemma6.4(1), not a new witness.
- Associativity alone: e is a two-sided unit on {e,a,b}, aa=b, ab=ba=e,
  bb=b. Then (aa)b=b while a(ab)=a. Prove a total unital magma with
  at most two elements must associate; the witness is therefore size-minimal.
- The two-element left/right projection operations isolate failure of the
  opposite unit law while associativity and the retained one-sided law hold.
- Definedness information: the two-object discrete category, only ee=e and
  aa=a defined, becomes the one-object monoid table ee=e, ea=ae=aa=a
  if missing products are filled with the existing arrow a. The untagged
  table cannot recover composability or object count. A genuinely fresh tagged
  bottom is different; do not claim all totalization necessarily loses information.
- Composite values: C4 and V4 have identical full composability and their
  common identity but different products. Recover endpoints is not recover m.
- The nonidentity-idempotent map above blocks overclaiming arbitrary morphisms.
- Empty table, singleton unit, multiple objects, nontrivial endomorphisms,
  unequal but isomorphic relabelings, malformed dimensions and strict type aliases.
- Delete strong definedness agreement while keeping equality where both sides
  exist: exhibit why weak equality alone is insufficient, or explicitly record
  the implication under remaining assumptions if no isolating witness exists.
A failed planned witness requires one-stage diagnosis and a genuine repair,
with every revised premise recorded; never tune an outcome into a positive claim.

## Evidence contract and accounting

Lean4.19 must freshly replay the arbitrary partial-algebra construction, converse,
both inverse maps and their operation laws, actual arbitrary-word response
preservation and the attained-image information equivalence. The small named
falsifiers and minimal unital nonassociative size bound also need exact typed
registrations. No source-level theorem name without its precise type suffices.
Compile source-valid corruptions first, then require the typed audit to reject
them; include reconstruction/matching and response-information statements.
Declare any remaining paper-only statement separately, never imply finite tests
or a generic theorem alone prove the registered operational construction.

Each named result gets premises, dependencies, strongest primary parent,
falsifier and exact paper/kernel locators. Independent review must check both
positive and no-alarm cases on actual data. Exact test inventories/counters,
receipt source hashes, fresh isolated dependency compilation and normal/-O
byte-identical receipts are mandatory. Missing input/tool is exit2; checked
invalidity is exit1. Keep docs and source modules focused, each at most200 lines.

A V19 successor preserves all222 original IDs/titles/status/evidence entries.
Add only scoped R1/R14/R15 repair evidence; do not close any original atom.
Accounting stays20 original fulfilled/202 unresolved, two qualified V16
replacements separately leave200 active unresolved. R0 alone is whole-EARNED.
Dereference inherited V18 and V16 receipt bindings, preserve exact predecessor
bytes against the actual PR base, and reject coupled scope/custody/count edits.
No new amendment authority or retrospective preregistration is created.

## Primary ownership and planning-parent bindings

Cranch, Doherty and Struth (2020), Sections3-4 and Lemma6.4:
https://arxiv.org/html/2001.11895v1
The partial-monoid/category reconstruction and coherence distinction are theirs
and earlier parents'; their unit formulations must be mapped explicitly.
Riccardi (2013), CAT_6, object-free category correspondence and law independence:
https://mizar.uwb.edu.pl/version/current/html/cat_6.html
https://fm.mizar.org/2013-21/pdf21-3/cat_6.pdf
Object-free reconstruction is already formalized. This round repairs the GMI
information claim and connects actual operations to observational recovery.
No new category theorem, empirical prediction or breakthrough is claimed.

| Source | SHA256 |
| --- | --- |
| research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json | 4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574 |
| research/gmi-1068-r1-minimal-process-core-v1/FREEZE_V1.md | 5f755106e6e5e2fcda6257d71e6eda6f2d895adf817834b2f2464685a491558a |
| research/gmi-1068-r1-minimal-process-core-v1/THEORY_V1.md | 6daf3aefb21641d13a2793c408ed84b67dac85d3e229322f000fb6dd5a204041 |
| research/gmi-1068-r1-minimal-process-core-v1/IRREDUCIBILITY_V1.json | f5064de97bee6d8ea82447978a6ba425c604a655419782ae5a06aecebc358698 |
| research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean | 164768fbda9a973001312c04e8ad07626de64b3fa0ec44fbd45391d7a0a704bd |
| research/gmi-1068-typed-foundation-v11/TypedPathsV11.lean | c9d8ebd0a544a5f76eee6e15d08a6bd697500e4b623263f799188c523a30cdc9 |
| research/gmi-1068-typed-foundation-v11/QuotientPathsV11.lean | 0a715908c58f351d49974f1983a6a5b16088be90d50a2edef3c506ccefd0e73b |
| research/gmi-1068-reference-envelope-v18/RESULT_V18.json | 248dbb06ec76dcfa27f21d3681c400c2b01868481cfef950a43fbe5783c2e9fa |
| research/gmi-1068-recursive-audit-v18/SCOPE_SNAPSHOT_V18.json | 866fa51b65bb0ecec02d83f398a6479fafb6ba3331962df74e96560984e27af1 |
| research/gmi-1068-recursive-audit-v18/CURRENT_ACCOUNTING_V18.json | 57ff897177ef16e36e0b1e640ced11f7d1df855b2d3bc7e8ff078b79193b52c6 |
| research/gmi-1068-corrected-targets-v16/TARGET_CONTRACT_V16.json | faa8f83c0af7a2f0a042e84deb7be191b09a281c08f287c5e986397124177902 |
| research/gmi-1068-corrected-targets-v16/RESULT_V16.json | 18bea5c6f85b4fcc91c40c53cbf63df59c38d70e9e839efc4585f6640497ad1a |
| research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json | e1cc2d2dbc10171407577889f75ac531c30cf09eab224fc3823f3931c5048618 |
| research/gmi-1068-amendment-governance-v16/RESULT_V16.json | ed491fab2cd0b69fb4ee845b82e349c79ff0d70f0dbc1d312ee0755645437de4 |
