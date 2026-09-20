# V25 independent formal review

## Verdict and reviewer separation

Read all 13 new Lean modules, their 13 immutable imports at the declared interface,
the final 177-entry static contract, replay checker and final 152-line FORMAL_SCOPE.
No unresolved mathematical or registration defect was found. This reviewer authored
the paper documents but did not author the Lean implementation/contract or root's
source-valid mutation tests. This is independent source/proof review, not an
independent second authorship of the paper statements.

A separate fresh isolated SOURCE/AUDIT replay on billy-laptop passed all 26 sources
and 177 exact registrations with Lean 4.19.0. It rebuilt dependencies from source;
no preexisting .olean was accepted as evidence. Record:
/tmp/gmi-v25-independent-kernel.json.

Final SHA256 bindings:
- proof_contract_v25.py:26994c17270bc9cfaa8cd08841de1c0fd67a5284d63f83d2e52fc4027750caa1
- check_lean_v25.py:bb5b30bbed559db2fa01fe5e64de086d39bdf284d72f745f35427f7ed4528bae
- generated audit:bb1703bea2d9638328c051a271f2a3100cb06740496da0f80e8b878c32165c3c
- FORMAL_SCOPE_V25.md:16b386159f9b540e846ea45c5e2fb4973ab2d92c91971b126e5763a43ae6e16f
The replay record binds the individual source hashes. Canonical package outcomes
and source-valid mutation results belong to RESULT_V25.json.

## Y1 — no assumed flattening theorem

Bracket syntax and recursion equations are concrete. Word is a head/tail pair,
so flatten cannot erase all-empty trees into an unanchored empty list. Empty leaves
become actual category identity arrows. OptionFold derives run append/product and
fold concatenation from strong Option associativity; tree equality follows by
induction. None cases are included, not excluded by successful-execution premises.
The category instance uses actual BundledCategoryV19.mul, aligned/rejected endpoint
equations and C.comp. Actual V11 Path nil/cons and eval are connected by induction.
Category laws are supplied by C; the observer/word consequence is derived.

## Y2 — carrier and information are earned

Presented contains an actual Algebra on the supported subtype. Padded_lookup binds
both lifts and the real subtype multiplication. Carrier_from_row uses a real local
right unit, rather than assuming row completeness. Absent labels do not acquire
local units. Padded associativity handles all present/absent cases, and unit_present
and padded_unit use the actual IsUnit definition and subtype equality.

Raw singleton/pair extraction and structural recursion establish observer equality
iff table equality. The attained-code recovery theorem applies the actual V9 fiber
criterion, with no assumed decoder conclusion or off-image default. The explicit
raw_threeway_recovery connects observer, carrier/table pair and table alone.
There is no Inhabited requirement on the carrier; supported(False) is a real model.
The full construction binds multiplication to the actual underlying Algebra.

## Y3 — actual controls, preserved premises

The contract includes inherited isolated associativity, weak-definedness, coherence
and projection-neutrality laws, alongside new actual tree-response contrasts.
C4/V4 use the true group operations through full Presented records. Default-tag
loss uses the actual discrete/join algebras. Empty/singleton supports share ambient
Bool labels and differ on an actual membership-checked singleton.

Designated insertion controls explicitly use Bracket.eval with a supplied candidate
empty map. They do not pretend the candidate satisfies genuine IsUnit; lawful raw
Empty would reject it. Constant-product identity failure has the same explicit
weakened-interface distinction. Bracket_loss_contract is the weak-definedness
leaf; the ordinary nonassociative output contrast is independently registered.
The six-row historical reconciliation is paper/ledger meaning backed by these
controls, not a kernel assertion that six stored fields are independently minimal.

## Y4 — no hidden external encoder

NamedPresented carries its actual identity map and true-unit landing proof.
Its general recovery theorem derives pair(table,map) from named observation using
Empty and binary queries. Complete separately adds injectivity and coverage of all
units. Actual CategoryTrees.named, named_table, named_identity, named_complete,
named_observer and category_named_carrier bind the category specialization.

Both actual V19 object and arrow roundtrip maps are used. Forward/backward response
equations and query inverse equations are proved; malformed joins and empty anchors
are transported, not omitted. AlgebraTrees unpack_raw connects actual reconstructed
category trees to raw unit-label observations. Same-table swapped-name nonrecovery
and paired revival are genuine decoder statements over two complete named models.
The general theorem does not infer independently chosen object names from a table.

## Registration and limits

Constructor bindings cover Arrow/Empty/Seq evaluation, flattening, guard recursion,
query maps, lookup, padded operation, core signature and named data. The audit
assigns declarations to explicit fixed types and prints dependencies. It does not
accept declaration-name existence or infer expected types from mutated sources.
The checker rejects forbidden proof constructs and sorryAx, compiles with warnings
as errors, and classifies missing inputs/toolchain separately from invalid proofs.

General statements are kernel theorems under their visible structural premises.
Python classification, syntax validation, finite decoder search, formula counts
and implementation correspondence remain separate finite calibration. Lean does
not certify the Python programs or prove a shortest encoding/physical ontology.
The source-level interpretation of classical parent definitions remains as stated
in PARENTS and the paper; no all-machine or complete-GMI conclusion is licensed.
