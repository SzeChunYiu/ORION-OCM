# Independent review V11

**Verdict: clear at the frozen scope.** No unresolved mathematical or
operational defect was found in the reviewed path/quotient implementation.
This verdict supports review of the three named atoms; it grants no
whole-round or full-theory authority.

## Reviewed artifacts

Read paths_v11.py, independent_paths_v11.py, test_paths_v11.py,
test_path_hostiles_v11.py, both Lean modules, check_lean_v11.py,
THEORY_V11.md, FORMAL_SCOPE_V11.md and ADJUDICATION_V11.md.
The review compares definitions and theorem scope rather than treating
matching digests or reported counts as proof of mathematical validity.

The primary 729-graph and 117649-admission corpus was not rerun during this
review. Its independent passes belong to the main generated receipt.
This review instead ran the targeted checks below on laptop billy with
Python 3.12, normally and with `-O`. Unexpected exceptions fail the checks.

## Representation and operations

An executable path is its start object and a word of positional edge IDs.
The start preserves which empty path is meant; edge IDs preserve distinct
parallel generators and repeated occurrences. This is a finite encoding of
the indexed Lean paths. Composition validates each operand, requires matching
boundaries, and concatenates in execution order.

Complete enumeration uses a topological traversal, not numeric vertex order.
It supports arbitrary acyclic relabelings. Cyclic enumeration is rejected;
individual cyclic paths and composition remain supported, without a false
claim that a truncated cyclic path set is a category.

Interpretation validates the entire object/generator assignment and applies
maps in path order. Noncommuting controls distinguish order; different domain
sizes and empty domains exercise typing. Nonfaithful interpretation is
legitimate and is accepted.

The executable quotient uses globally named integer classes. Each class must
remain inside one Hom. Coverage must contain every path of the finite DAG.
For every composable representative pair it checks that their class pair
determines a unique result class. This is exactly the well-definedness
requirement for composition, not merely equivalence of labels.
The inherited identities and composition therefore match the congruence
quotient construction in Lean.

Every supplied quotient path key is itself validated after set coverage is
checked. This rejects Boolean/float aliases that Python otherwise compares
equal to integer path keys. Exact integer checks also apply to graph
endpoints, edge IDs, domain sizes, function images and class labels.

## Additional independent quotient challenge

Used the graph with two named edges 0→1 and two named edges 1→2.
Its nontrivial parallel-path Hom sets have sizes 2,2,4.
Enumerated all typed equivalences through restricted-growth class labels:
Bell(2)·Bell(2)·Bell(4)=2·2·15=60.

The independent validity criterion compares each equivalent pair under
every possible left and right path context. It does not construct the
production class-pair composition table.
Production acceptance agreed on every case:

- 20 genuine congruences accepted;
- 40 equivalences lacking composition congruence rejected;
- 977 quotient unit and associativity equations checked on accepted cases.

All counts and verdicts agreed in normal and optimized Python.
These are additional review diagnostics, not substituted mandatory coverage
or an exhaustive check over arbitrary graphs.

## Additional representation challenges

For a four-object DAG with five named edges, including parallel edges,
tested all 24 object permutations while reversing edge IDs. Transported
complete path sets and endpoints agreed with the independent word oracle.

For two arrows 0→1 and 0→2 with all three interpreted sets empty, both
function values are the empty tuple. Their different typed endpoints still
prevent merging them into one globally named quotient arrow.
The valid empty-function interpretations passed; the cross-Hom quotient
mutation was rejected.

## Targeted existing controls replayed

Only test_path_hostiles_v11 was replayed, with four tests passing normally
and under `-O`. Measured coverage matched exactly:

- five structural path mutations;
- three long cyclic path cases;
- four cyclic-enumeration rejections;
- eighteen interpretation boundary cases;
- ten quotient rejections, including noncongruence and numeric aliases;
- forty-five malformed-input rejections;
- one admission-cutoff/resource-state-lift comparison.

These include clean positive controls, valid nonfaithful maps, typed empty
paths, a valid quotient after completing its congruence closure, and empty
graphs. No rejected input was counted solely because a checksum changed.

## Proof and claim alignment

The Lean source constructs path associativity and units by induction.
Only target category laws are assumed by interpretation.
The quotient development requires a genuine typed congruence and proves
both inverse Hom maps plus identity/composition preservation for
Path(U C)/ker(eval)≅C. Thus the bridge covers all declared lawful small
categories, including nonfree ones.

The auxiliary general descent/uniqueness statement for every respected
congruence is paper-only. THEORY and FORMAL_SCOPE explicitly distinguish it
from the implemented evaluation-kernel specialization.

check_lean_v11 uses a fresh binary directory, pins Lean 4.19, and compiles both
new sources plus the inherited V9 context proof on each replay.
Compilation remains distinct from the semantic review and source custody.
No proof here certifies Python refinement or infers physical categoryhood.

ADJUDICATION maps only R1-002, R1-003 and R2-002 to the proved results.
The fixed process/common history domain and opposite actual context rankings
satisfy the original forward nonrecoverability target. Reverse independence,
universal primitive minimality and a compulsory probability measure are
explicitly excluded. No change to those exclusions is warranted.

## Proof registration repair

Compilation alone accepted valid empty proof modules. The integrated replay now
checks fourteen explicit theorem and data types in a generated Lean audit and
inspects their axioms. Three actual source-valid corruptions (empty modules,
weakened presentation isomorphism, weakened ranking reversal) compile as source
and must fail at the audit stage. Missing tooling remains distinct from invalid
proofs. These controls passed in ordinary and optimized Python.
