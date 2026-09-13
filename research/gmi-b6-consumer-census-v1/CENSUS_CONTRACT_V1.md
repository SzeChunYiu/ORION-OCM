# Exact scope and finite algorithms

## What is counted

The ten raw arm records are exact committed bytes, individually verified
against their manifest and their native JSON self-hash convention. The archive
also retains the five previously bound source receipts, the new S1 witness,
the prior S1 witness, native sources and both reviewed claim versions.

| Cohort | Selection rule | Rows / distinct serialized graphs |
|---|---|---|
| All exported arm rows | 50 final best-per-carrier graphs + 10 first-admissible raw + 10 first-admissible pruned | 70 / 63 |
| Original scanner rows | 10 archive-best-DENSE + 5 first-admissible pruned graphs containing any DENSE + two saved witness forms | 17 / 15 |
| Source archives | Every saved cell in five source receipts | 350 rows; eight contain GRAD |

The first two cohorts overlap. Within the second cohort the archive, first-hit
and witness fields are distinct provenance categories. A DENSE node present
anywhere need not be on the syntactic OUTPUT ancestry or define the carrier.
Duplicates mean identical genotype **strings**; this does not solve graph
isomorphism or establish independent experimental replication. The known
CROSS/TWIN and DISJ/TWIN copies remain visible in both raw and deduplicated views.

The arm records report 800 total final archive cells, including the duplicate
arm, but export only 50 best-per-carrier genotypes. Their 20 first-hit graphs
do not fill that gap. Compact search traces omit genotypes. Hence none of
these cohorts enumerates every final archive cell or every searched machine.

## Native consumer roles

`native_roles_v1.py` parses the frozen KINDS declaration and evaluator AST.
It confirms LINEAR/AFFINE parameter-name input port 0 and data port 1;
GRAD reads parameter names, prediction and target at ports 0, 1 and 2.
DOT does not exist in this alphabet. EDGE is identity routing at port 0.
These roles are interpretations of the pinned evaluator, not generic
consequences of vector types. Arbitrary new evaluators need a new authority.

`graph_census_v1.py` rejects unknown kinds, invalid/duplicate ports, type
mismatches and cycles. Missing optional inputs are not treated as completed
semantic evidence. It reports DENSE→EDGE*→consumer adjacencies separately by
native role. All six numeric parameter adjacencies in the 17-row cohort enter
port 0. Three rows have that numeric node on syntactic OUTPUT ancestry.
These are counts of **declared connections**, not proved numeric contributions.

For the finite DAG, forward EDGE exploration terminates and lists exactly
such paths by induction on path length. Backward closure from OUTPUT lists
exactly its syntactic ancestors. An independent oracle instead walks backwards
from each consumer port and computes transitive ancestor sets. It compares
all 437 row instances, including all 350 source cells.

Neither algorithm evaluates runtime type guards, coefficient values, unused
blocks, side effects or cancellation. Output ancestry is not complete for
feedback/storage effects: an off-path update can affect later observations.
The literal packet-family predicate is also only that native structural
predicate; its value is not a proof of a learning mechanism.

## Source and witness custody

Every source receipt passes its own byte and internal-hash checks. Seven
selected-source populations reproduce the recorded top-k ordering, carrier
sequence, fingerprint fields and capabilities. This verifies those selected
source fields, not all two-parent matching inputs or execution authenticity.
E_twin1/S1 is absent from the pinned packet, so the tenth selected-source
population stays `UNVERIFIABLE_FROM_PINNED_PACKET`.

Eight source cells contain GRAD. Ten recorded arm-seed fingerprint occurrences
match these known source graphs; one can match a graph also seen in another
source. The receipt states separately whether the declared source ID matches.
Fingerprint-field equality alone does not authenticate an invocation or a
complete ancestry. GRAD occurrence does not prove effective gradient updates,
task adequacy or a causal source of survival or rejection.

The raw/pruned S1 strings and six reported capabilities equal the prior saved
witness. This is the same representation, not a second machine. The prior
consumer proof covers all finite registered event sequences under its stated
VM assumptions. Common query/store behavior is preserved while representations
and resource charges differ.

## Operational boundary

The source archive is read in memory; no archived module is imported or executed.
The sole historical-function test compiles only the original pure graph probe
to demonstrate its actual AFFINE false negative. No genotype is executed.
Full-payload replay checks every emitted field and rechecks complete unit
membership after the worker finishes. Hashes bind bytes; they do not establish
historical timing, first-attempt chronology or authorship independently.
