# V22 blockers, minimality and finite existence

Read [CONTEXTS_V22.md](CONTEXTS_V22.md) for the earned incidence semantics.

## V3.1 — blocking equals hitting current supports

For enabled S let W_S={h in W:R(h) contained in S}. Restrict deletions to B subset
S and define Blocks(B,S) iff not Cap(S minus B). Then
Blocks(B,S) iff every h in W_S has R(h) intersect B nonempty.
Proof: an enabled witness after deletion has R(h) contained in S and disjoint
from B. Conversely any such available disjoint witness remains enabled. Negating
this existential gives the displayed equivalence, using classical logic for
arbitrary predicate-valued sets. Supports unavailable at S must be excluded.
These are classical hitting sets of the actual retained support family.

## V3.2 — private-witness minimality certificate

MinimalBlocker(B,S) means B subset S, Blocks(B,S), and no proper subset of B blocks.
Within deletions B subset S, this holds iff Blocks(B,S) AND for every b in B,
there is h in W_S with R(h) intersect B={b}.
Forward: B minus {b} fails to block, so some h is available after that deletion.
Its intersection with B is contained in {b}. Because B blocks, that intersection
is nonempty; it is therefore {b}. Reverse: suppose B' proper subset B. Pick b
in B minus B'. Its private witness intersects B only at b, hence is disjoint
from B' and remains enabled. Thus B' does not block. This argument does not
require B finite. The blocker premise is essential; private witnesses alone can
hold even when some other target path survives the full deletion.

The certificate provides both a universal hitting condition and an explicit
surviving history after restoring each individual b. It does not identify an
actual physical cause or a preferred explanation. Restoring any one b in a
minimal blocker restores some target witness, which may differ across b.

## V3.3 — finite existence and complete enumeration

Let finite L cover available permissions U. Its recursive powerset enumerates
empty at the base and, after adding q, both each old subset and that subset with
q adjoined. Induction shows every enumerated set is contained in U and every
subset of U is represented. Duplicated list representations have the same set
meaning. For any property F and F-set B subset U, the finite collection of
F-subsets of B is nonempty (contains B). Choose one of minimum cardinality;
any proper F-subset would have smaller cardinality, contradiction. This proves
inclusion-minimal existence beneath every enabling addition or blocker.
Equivalently apply finite frontier existence under reverse inclusion to the
filtered powerset. Neither route assumes the desired minimality conclusion.

Filtering all subsets by enabling/blocking and deleting every set with a proper
successful subset therefore returns exactly all inclusion-minimal answers.
The mathematical existence statement permits F to quantify over infinite
histories; that does not make its membership test computable. Effective finite
enumeration here requires a supplied complete finite witness roster or an exact
decidable incidence predicate. A tested finite word horizon is not such a
certificate for arbitrary all-word history-sensitive evaluation.

## V3.4 — support compression and boundaries

Within a finite support family, every support contains some inclusion-minimal
support from that family by finite descent. Therefore capability at any S holds
iff a minimal support is contained in S. Hitting all supports is likewise
equivalent to hitting every minimal support: the forward direction is immediate;
for the reverse, hit a minimal support contained in each original support.
Availability filtering remains sound, since a subset of an available support
is also available. Thus antichain reduction preserves Boolean capability and
blockers. It need not preserve the catalogue of actual successful histories.

Equal supports may be grouped while retaining all original history backpointers.
Strict-superset deletion intentionally forgets some witness identities; it cannot
be advertised as full-profile or provenance equivalence. Minimal deficits for
additions are formed relative to their baseline, not inferred from an unlabelled
attainable-value image. Inclusion minimality does not choose a minimum-cardinality
or cheapest member; those use separately declared objectives.

If W is empty, no permissions enable the target and the unique minimal blocker
is empty. If an empty-support target witness exists, all S enable it and no
blocker exists. These facts include U empty and must not be conflated.

Infinite incidence equivalences do not guarantee minimal sets. For Q=Nat take
supports R_n={k:k>=n}. Each support enables, but contains the smaller R_(n+1),
so there is no minimal enabling set. A set hits every R_n iff it is unbounded;
removing one element preserves unboundedness, so no blocker is inclusion-minimal.
Each such support is infinite: finite word length alone does not rule that out
when a declared edge may require infinitely many permissions. If each witness
support is finite, a successful witness gives a finite enabling candidate and
finite descent within it gives a minimal addition. No corresponding finite
blocker enumeration follows merely from finite supports.
