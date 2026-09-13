# PR603 disposition at pinned source 51753a8c

The seven changed files are preserved in raw/pr603, with four unchanged CAU
parent files in raw/parents. The source commit, path, exact byte count and
SHA256 of each are bound separately. Its reported historical host runs remain
archived reports; this successor records its own laptop execution.

| Source statement | Scientific disposition |
|---|---|
| W4a/W4b separate observation and intervention with opposite bias signs | Retained; independent surgical evaluation reproduces +1/4 and -1/2. |
| W1 obstructs observational-law-only identification | Retained, inherited CAU1; CRR2 explicitly includes randomized estimators. |
| Faithfulness is an orientation premise sufficient as a listed alternative | Qualified: it can recover a Markov equivalence class under other premises, not generally a unique orientation or do-target. |
| Discovery gap is positive through a boundary/discharge list | Qualified: the source explicitly supplies no discovery algorithm. CRR2 adds a finite-class query procedure; structure discovery remains separate. |
| W5 has identical observed and do laws but PN=1/2 versus1 | Retained; all nine endogenous joint intervention laws checked independently. |
| Six root units are minimal | False in the declared class; two suffice, and three suffice with both treatments observed. |
| Rung3 knowledge should take the form of bounds | Constructively revived using inherited sharp PN bounds and attaining SCMs. Point identification remains possible in restricted compatible fibers. |

## Faithful orientation counterexample

Let independent U be fair and E~Bernoulli(1/4). In F, X=U and Y=X xor E.
In R, Y=U and X=Y xor E. Each is a fully observed two-node DAG with independent
noise. Both have P00=P11=3/8 and P01=P10=1/8. There is dependence and full
support, so both distributions are faithful to their single-edge graphs.
Nevertheless do(X=1) gives P(Y=1)=3/4 in F and1/2 in R. Faithfulness alone
does not distinguish these orientations. This is a control of inherited
Markov-equivalence theory, not a new orientation theorem. These forward/reverse
models form a separate comparison class. The reverse graph is outside CRR1–2’s
fixed X=f(U), Y=g(X,U) intervention register; its PN fiber is not pooled with theirs.

## Smaller counterfactual separators

For a uniform root, each row lists (factual X,Y0,Y1).

- Two units: A={(1,1,1),(1,0,0)}, B={(1,0,1),(1,1,0)}.
- Three units with both factual treatments: append (0,0,0) to both lists.

Each pair agrees on all nine joint intervention laws but has PN=0 versus1.
They refute six-unit minimality while preserving the source's valid six-unit
example and its PN gap1/2. The census additionally checks that one uniform
unit has no PN ambiguity, and two uniform units have none when both factual
treatments have positive probability. These census statements are scoped to
this binary response register, not minimum complexity claims for arbitrary
causal theories or machines.

Finite **binary endogenous** variables allow finite nonbinary hidden roots,
as the unchanged CAU1–4 parent already states. No product-noise violation is
inferred merely from one shared six-valued root.

## Historical prose binding

The archived receipt reports the theorem as4604bytes with SHA256
63aca5c5f68313b8fc9499e85f02cb4c1c35267fe2e45423bfcc08812ef0a68c.
The pinned Git prose is4614bytes with SHA256
932c13e1748c387a9e59ddcfe7c17f850f50020957d0dfe7a98f6b946bd82318.
Its code and test bindings match. This successor records the prose mismatch
explicitly and binds the delivered original bytes; it does not silently alter
the old receipt or infer that its old prose was the tested prose.
