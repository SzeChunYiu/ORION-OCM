# V24 — image transport and conservative definitions

Authority: FREEZE_V24.md, commit dec818e7acbdb270251caae72507e4e49e3fd1f4.
Exact executable outcomes and kernel types are separately recorded in the receipt
and formal scope. The following are mathematical proofs at stated assumptions.

## X1.1 — actual contextual images and projection

Let k be an actual V15 Context on histories H, with defined domain E, evaluator
f:E->W and declared preorder. Admission P is independent of E. Write D=P intersect E.
For a history predicate T, actual V20 Attained is
A_T={f(h):h satisfies P,E,T}. The full image uses T=True.
Its observation is illegal off P, undefined on P outside E, and VALUE f(h) on D.
An ambient defined evaluation off P remains defined but is not admitted.

For any explicit q:W->Z, actual V17 postcomposition preserves E and replaces f
by q composed with f. Unfolding image membership gives its attained image exactly
q(A_T): an original witness supplies a mapped witness, and conversely each mapped
witness supplies the original history and value. Every observation maps VALUE
through q and preserves the illegal/undefined tags.
No monotonicity of q is needed for this direct-image equality. Transporting
frontier comparisons additionally needs appropriate order preservation/reflection.
Neither injectivity nor a history reconstruction follows from image equality.

## X1.2 — exactly when a selected roster preserves a projection

Take a selected B subset D. Put A_B={f(b):b in B}, A_D={f(h):h in D}.
Then q(A_B)=q(A_D) iff for every h in D there is b in B with q(f(b))=q(f(h)).
Forward: q(f(h)) belongs to the full image and hence selected image; unpack its
witness. Backward: these witnesses prove full image is contained in selected;
B subset D proves the reverse inclusion. This is an exact observation-relative
sufficiency criterion, not a claim that the entire profile is always needed.
An arbitrary selector predicate has the same theorem after intersecting with D.

Suppose q(f(h))=g(terminal(h)) for all h in D and B covers each such terminal:
for every h in D there is b in B with terminal(b)=terminal(h).
Then q(f(b))=g(terminal(b))=g(terminal(h))=q(f(h)), proving image equality.
Coverage by undefined or inadmissible representatives does not meet this premise.
The factorization condition is sufficient; equal projected images alone do not
imply that q composed with f factors through terminal state.

If q composed with f is injective on D, equality of images forces B=D: the witness
b for h has equal projected value, so b=h. Thus retaining one terminal representative
cannot preserve an injective full-history profile when another active history exists.
A profile containing complete history identity is injective in that component;
a coarse capability projection generally is not.

## X4.1 — what conservative substitution establishes

A source signature supplies the types, admitted histories, partial domains,
evaluators, orders, resources, targets, context comparisons and horizon semantics.
A legacy symbol L is conservative at that signature when its old denotation equals
an explicit construction using those supplied ingredients. The correspondence may
use a declared decoding/projection between representations; its commuting equality
must state which information it retains or loses.

For an equality-preserving translation, replacing L by its equal expansion in any
well-typed expression preserves denotation by congruence. For propositions this
preserves truth; for formulas with quantifiers it does so pointwise on the SAME
domains and hence under those quantifiers. This is elementary substitution, not
an independent proof of each historical theorem or its omitted premises.
A change of domain, objective, horizon or loss interpretation is an extension or
specialization to label explicitly, not justified by matching notation.

PROFILES transports formal AF images and separately actual BFS-selected records.
PREFERENCES transports full candidate-ID Pareto and positive-price correspondences.
PLANS transports common-universe feasible plans and their joint compatibility.
These constructions expose the extra supplied data; they do not infer a universal
objective or prove a unique minimal ontology. AI0 SEL names their downstream
interface and supplies no new deterministic tie breaker. Unrelated adequate-output
Gamma and the conditional SEL opcode are source-keyed exclusions, left unchanged.
