# B6 lineage attribution correction V1

Date: 2026-09-13. Status: source-derived scope correction and one genuine
primitive countercontrol. Historical search, raw receipts, freeze, scorer,
outputs and the running recovery process remain unchanged.

## Source and parent mechanism

The authority is original
[b1.search, lines 114–117](https://github.com/SzeChunYiu/ORION-OCM/blob/5378c2b7f91f8fbc567764a2ee0c5ff6e256e814/research/machine-intelligence-morphogenesis-v1/gmi_microscope/b1.py#L114)
and [crossover, lines 211–232](https://github.com/SzeChunYiu/ORION-OCM/blob/5378c2b7f91f8fbc567764a2ee0c5ff6e256e814/research/machine-intelligence-morphogenesis-v1/gmi_microscope/morphgen.py#L211).
The parent method is complete derivation provenance, not a new learning law.
[W3C PROV-DM §5.2](https://www.w3.org/TR/prov-dm/#component2) distinguishes
derivation activities and their inputs. We adapt that bookkeeping distinction
to genotype occurrences and crossover roles; provenance is not causal necessity.

## What origin literally records

The search selects a primary archive parent. On the crossover branch it also
selects another parent and calls crossover(rng, parent, other). Regardless of
that branch, placement receives:

    origin = origin_by_id.get(id(parent))

Mutation and crossover therefore copy the primary parent's existing origin.
By induction, a known ["seed", k] identifies the seed obtained by following
only primary-parent links. It is not a list of all seed ancestors.

The crossover primitive can use the other parent: it clones the primary graph,
copies a selected donor node's kind and parameters, wires that node, and checks
the resulting graph. The other parent's ancestry is absent from origin.
This is information loss in the recorder, not evidence that the donor was unused.

A non-DENSE recorded primary founder therefore does not exclude DENSE founder
ancestry, DENSE intermediate machines, or inherited DENSE structure.
The known primary founder still supplies valid information about that recorded
chain. This correction does not withdraw that information.

## One executed countercontrol

On laptop billy, CPython 3.12 executed the unmodified pinned crossover exactly
once; no search or ecology evaluation was invoked. The primary was pinned
zoo.exemplar_table(), raw carrier TABLE. The donor was zoo.constant_emitter(),
raw carrier DENSE. A choice tape selected donor node "1", then destination
("2", 1), replacing LOOKUP's vector input with the donated DENSE node.
Both selections belong to the primitive's actual two-element choice lists.

The operator reported ("op_graft_recombine", True), passed the pinned type and
servability checks, and preserved both parents. Its child has DENSE on the
OUTPUT dependency path and is classified DENSE by pinned b1.carrier_of.
Applying the source's primary-origin assignment to parent roots seed 0 and
seed 1 yields ["seed", 0], whose carrier is TABLE, despite the DENSE donor.
This is a legal operator outcome, not a newly observed B6 campaign event.

| Object | Canonical fingerprint |
|---|---|
| TABLE primary | 9e996cc24b77400032ade16c2a9ad0aa82f5b681331e4b90d1d1ff965cfaa17e |
| DENSE donor | e2a7924da225d19459ce9e582d810fd785e95f8e20d1de8beb1b86a8571b3744 |
| DENSE child | ceb2491757c28b10a6811d18f173c0036b9f11235b84e9df6a7923bd36f811be |

No admissibility, atrophy, learning, or ecological success is claimed for this
child. The countercontrol isolates the primary-lineage-to-full-ancestry
inference. Its positive control preserves the true primary ancestry; only the
other parent's contribution is lost from the field.

The exact [countercontrol receipt](evidence/b6-lineage-countercontrol-20260913/COUNTERCONTROL.json)
contains the full genotypes and source hashes; its SHA-256 is
366d8a923eb5fd14a1821125af8cdd287e5d19be848d29413fc64d8a2ccfd053.
The [portable packet](evidence/b6-lineage-countercontrol-20260913/README.md)
includes all 13 pinned modules, a standalone replay and bound validation.
It reproduced the exact receipt bytes. A second invocation rejected an expected
receipt falsely replacing the primary root with donor seed1; neither run invoked
search or ecology evaluation. The receipt has no nonportable machine paths.
The essential control can also be reproduced from the pinned modules:

```python
from gmi_microscope import b1, morph, morphgen, zoo
class Tape:
    def __init__(self): self.values = iter(("1", ("2", 1)))
    def choice(self, choices):
        value = next(self.values)
        assert value in choices
        return value
primary, donor = zoo.exemplar_table(), zoo.constant_emitter()
record = []
child, _ = morphgen.crossover(Tape(), primary, donor, tries=1, record=record)
assert record == [("op_graft_recombine", True)] and morph.typecheck(child)
assert [b1.carrier_of(g) for g in (primary, donor, child)] == ["TABLE", "DENSE", "DENSE"]
roots = {id(primary): ["seed", 0], id(donor): ["seed", 1]}
assert roots.get(id(primary)) == ["seed", 0]
```

## Existing evidence and Z5

The preserved first-recovery records label primary founders PROGRAM, KVSTORE
and TABLE. They do not prove that those machines lack DENSE donor ancestry.
SAME/CONTINUED S1's seed 38 is its primary-lineage root, not an ancestry-exclusion
certificate.

Z5's all-recovery quantifier and this ancestry limitation are independent.
First recoveries alone are insufficient for every recovered machine.
A complete recovery census containing only primary roots would still be
insufficient for full-founder-ancestry exclusion. The existing V2
recorded_first_recovery_verdict concerns only the literal recorded primary-root
predicate. HELD for that subpredicate cannot be promoted to full ancestry.
Historical output bytes retain their original meaning as recorded observations.

An independently re-exhibited, verified genotype can establish a static
admissible witness even when its genealogy is unavailable. It cannot alone
establish that non-DENSE ancestry was necessary or that direct DENSE development
could not have produced it.

## Constructive repair for a separate instrument

Assign distinct occurrence IDs to seeds and every produced candidate.
Identical canonical genotypes can have different histories, so fingerprint
deduplication must not merge provenance. Record primary and donor occurrence
IDs, operation kind, donor node and parameters, rewiring, acceptance/fallback,
child genotype/hash and archive disposition. Preserve failed-attempt costs.
Separate selected inputs from mechanically verified committed grafts:
an attempted crossover returning a primary clone need not import donor data.

For a declared operation-ancestry relation, compute founder sets R(v) on its
finite event DAG. A founder has R(v)={v}; mutation/copy takes its parent's set;
a committed graft takes the union of both parents' sets. Verify the outcome and
parent references before the union; a missing parent makes ancestry unknown.

Induction over occurrence order proves exactness for this complete recorded
relation: roots establish the base case, and each operation adds precisely its
declared predecessor edges. If every root in R(v) has a verified non-DENSE
carrier, the resulting finite certificate establishes no DENSE founder in that
relation. Event-log completeness, correct operator replay and known root
identities are premises, not consequences of a hash.

This does not exclude DENSE intermediate ancestors; that stronger predicate
needs carrier checks on every ancestral occurrence. Neither predicate proves
causal benefit or necessity. Those claims require matched interventions and
their own successful replay and complete cost accounting.

Occurrence records, parent edges, serialization, root-set propagation and
native verification consume memory and work. Charge them in a separately
registered instrument with a verified recording-neutrality comparison.
The running recovery remains unchanged; its current telemetry does not
retrospectively provide these missing records.

See [the assessment](B6_CORRECTED_EVIDENCE_ASSESSMENT_V1.md) and
[the adjudication correction](B6_ADJUDICATION_CORRECTION_V1.md).
The packet's archived correction copy remains historical; this note qualifies
its lineage interpretation without rebinding or replacing that packet.
