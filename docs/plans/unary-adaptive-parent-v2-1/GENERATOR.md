# Exact prospective generator and split identity

All indices start at zero. Canonical JSON is UTF-8, ASCII escapes, sorted dictionary
keys, separators comma/colon, no whitespace/newline, finite plain JSON values only.
Array order is significant. Every recorded draw retains its input fields and task bytes.

## Stream and ordered choices

Master is `ocm-unary-causal-v1`; episode is integer 0,1,2,3.
Split strings/order are `train`, `development`, `final`; target sizes are 32,16,32.
Each split has its own attempted draw index d=0..65535 and accepted slot s=0..target-1.
For a choice with field tag f and ordered array A, choose:
`A[int.from_bytes(SHA256(JSON([master,episode,split,d,f])), "big") % len(A)]`.
No random module, system clock, process ID or task outcome participates in a choice.

Slot predicates are P0,P1,P2. Atomic expressions in order are pred(P0),pred(P1),pred(P2).
Training expression choices are these three atoms.
Development/final expression choices are these atoms, then not(P0),not(P1),not(P2),
then and(pred(Pi),pred(Pj)) for i outer/j inner 0..2, then or in that same pair order.
Repeated operands and premise duplicates are permitted; no algebraic simplification.
Kinds in order: `every`, `no`, `some`, `not_every`.

Field `premise_count` chooses [2,3] for train and [4,5,6] otherwise.
For each premise index i, fields `premise/i/kind`, `premise/i/left`,
`premise/i/right` independently choose from kinds and the split's expression array.
Query kind is kinds[s % 4], for every split. Fields `query/left` and `query/right`
choose expressions. Query rotation follows accepted slot, so a rejected draw does
not consume the slot's query kind. The next attempted draw always advances d by one.

Before identity tests, reject a draw unless all three predicates occur somewhere
in premises or query. For development/final also require at least one non-atomic
expression in premises or query. These are syntactic gates, never answer gates.
Retain every reason in this precedence: missing predicate, missing Boolean group,
syntax duplicate, semantic duplicate, accepted. Later gates need not run after rejection.
No filtering for consistency, entailment, learned-rule applicability, cost or a desired route.

## Exact keys and duplicate scopes

Validate with actual `ocm.unary-task.v1`. Syntax identity enumerates all six bijections
from its sorted names to P0,P1,P2. Under each rename, recursively preserve AST order,
sort the list of premise statements by canonical bytes (preserving multiplicity),
and encode the full task with sorted predicates and its query. The minimum byte
string is hashed with SHA256. Commutativity is not an additional syntax normalization.

Semantic identity uses the released `unary_rule_identity.semantic_key` mechanism:
enumerate predicate-name permutations in lexicographic order; region r=0..7 gives
predicate i truth value bool(r & (1<<i)). World w=1..255 contains exactly regions
whose bits in w are one. Universal statements use all occupied regions; existential
statements use any occupied region. Bit w-1 of B is premise conjunction satisfaction;
bit w-1 of Q is premise conjunction AND query satisfaction. Minimize numeric pair
(B,Q) over six permutations, then hash canonical JSON
`{"predicates":3,"models":B,"query_models":Q}`. The actual source is bound by the seal.
This treats inconsistent premise sets alike; that is a declared identity consequence.

Use two accepted-key sets per episode, initially empty. Accept only when neither
key occurs in ANY earlier accepted slot of that episode, including earlier splits.
After acceptance insert both keys. Candidate rejections never insert a new key.
Episodes reset these sets; cross-episode repetitions are allowed, reported, and
not represented as IID evidence. Allocation order is episode-major, then split order.
Each partition draws until full, 65,536 attempts, or the whole-run deadline.
Any unfilled original slots remain GENERATION_CANNOT_CHECK; no replacement seed.

## Data exposure and presentations

Evaluator owns complete draw/rejection/identity records. Training worker receives only
accepted training ASTs and their original row IDs; it computes its own charged training
semantic identities. It receives no development/final semantic keys or reference answers.
Development adapter gets accepted development ASTs only, after mining. Final AST/text
inputs are exposed only after the selected library and process-A output are sealed.

Learning uses P0,P1,P2. For each final task, deterministically rename Pi to
`e{episode}f{slot}p{i}` in BOTH its formal AST and text. These valid fresh lexical labels
do not change the split identity. Realize with the supplied canonical grammar.
The text arm parses those bytes independently; parsed task digest must equal the
paired renamed formal digest before answer comparison. Label cost is charged once
to evaluation setup; text realization and parse costs are recorded separately.

All failed/accepted draws, duplicate keys, original indices and final rename maps
remain available for audit. Study code must not inspect these records to choose
new sources, seeds, methods, rows, repairs or interpretations within that same run.
Diagnosis may inform a separately registered successor with the original evidence retained.
