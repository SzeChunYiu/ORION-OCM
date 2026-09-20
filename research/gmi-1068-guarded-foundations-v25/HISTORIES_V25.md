# Anchored histories and bracket preservation

## 1. Actual typed observer

Fix a lawful category C with object type O. Let A be its bundled arrows, including
source and target. The actual V19 operation m(x,y) checks target(x)=source(y), then
returns the bundled C-composite; otherwise it returns None.
For Tree O A define Arrow(x), Empty(o), and Seq(t,u). The typed observer T obeys:
T(Arrow x)=some x; T(Empty o)=some(id_o);
T(Seq(t,u))=T(t).bind(x↦T(u).bind(y↦m(x,y))).
Thus arbitrary malformed joins are legitimate queries with failed responses.

Flatten Arrow(x) to [x], Empty(o) to [id_o], and Seq to concatenation.
Every flattened tree is nonempty, by structural induction; this requires no
inhabitant of A. If O and A are empty, there are no tree leaves and hence no trees.

## 2. Nonempty fold-concatenation lemma

Let m be any strongly associative partial operation; unit/coherence premises are
not required for this lemma. Extend m to Option A by p⋆q=p.bind(x↦q.bind(y↦m(x,y))).
If any of p,q,r is None, both associativity sides are None; if all are some,
strong associativity of m gives (p⋆q)⋆r=p⋆(q⋆r).

For nonempty word w=[x]++xs, F(w) is the actual V19 run m x xs.
For nonempty u,v, F(u++v)=F(u)⋆F(v). Proof: left folding the appended suffix
first gives an extended fold starting at F(u). The identity
fold(p,[y]++ys)=p⋆F([y]++ys) follows by induction on ys, with the inductive
step using associativity of ⋆; it holds also for p=None. This establishes the
concatenation formula, including failure, without selecting a successful output.

Induction on t now proves T(t)=F(flatten(t)). Leaves are the singleton equation;
Seq follows by the induction hypotheses and concatenation lemma. Hence arbitrary
parenthesizations of the same guarded leaf word agree. For category m, strong
associativity follows from category composition and the actual endpoint checks,
as already proved by V19. This is the Y1 observer bridge.

## 3. Actual V11 paths

For a path p:a→b, map nil(a) to Empty(a). Recursively map a first edge followed
by a remaining path to Seq(Arrow(edge), tree(remaining path)); the nullary suffix
therefore retains its endpoint identity. The tree observer is some of the bundled
V11 eval(p). Proof by path induction: nil is C.id; cons has matching endpoints,
and the inductive output composes by the V11 eval equation. The final identity
is harmless by the category unit law. Equivalently an edge-only nonempty encoding
may omit that final identity only after proving the unit equation.

This does not identify nil(a) and nil(b). Their observations are different bundled
identities when a≠b; moreover Seq(Empty(a),Empty(b)) fails in a discrete category.

## 4. Raw presented histories

For a Presented on L, let S be its carrier, p its padded table, and U its true
padded units (constructed in INFORMATION). Define R(Arrow x)=some x if S(x),
R(Empty e)=some e if U(e), and Seq by the same Option bind using p.
Flatten raw leaves to their ambient labels, retaining empty anchors. Define Guard(t)
to require membership for every arrow and true-unit legality for every empty.

If Guard(t) is false, a failed leaf propagates through its ancestors, so R(t)=None.
If Guard(t) holds, all leaves have their singleton labels and strong associativity
of p gives R(t)=F_p(flatten(t)). This can equally be computed in the actual subtype
algebra and mapped back: every guarded leaf lifts to the subtype, and each padded
step is the mapped subtype step. A successful intermediate output remains in S.

In particular a raw singleton outside S returns None although an unguarded V19
run on a singleton syntactically returns its input. The latter assumes an actual
arrow carrier; extending its input interface without the membership guard is false.
Empty support in a nonempty ambient L still has valid raw queries, all failing.

## 5. Executable boundary

The finite syntax API checks the entire structural tree before evaluating it:
strict tuples/opcodes/arities/in-range integer labels, including descendants after
an earlier semantic failure. Semantic membership and unit guards may then short
circuit. A malformed node is rejected as invalid input, not silently reclassified
as a legitimate failed process. The proof syntax itself has no malformed constructor.
