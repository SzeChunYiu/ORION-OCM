# Joint relational composition — JRC-1–4

Date: 2026-09-13. Finite corollary/application, no technical novelty claimed.
Read [parents and costs](PARENTS_AND_COSTS_V1.md). Existing GG27 assumes product
feasible machines and GG28 concerns exact functions; both statements are retained.

## 1. Registered classical interface

Let X and A be finite nonempty labelled sets and let nonempty Γ(x)⊆A be
explicitly supplied for every x∈X. An encoder sees all x and sends one complete
classical message c(x)∈Z. A decoder sees only that message and emits d(c(x))∈A.
It has no input side information. Every input must satisfy d(c(x))∈Γ(x).
There is no abort, feedback, quantum carrier, changed input promise or relaxed
error criterion. All finite deterministic encoders and decoders are admitted.
Only the number of used message symbols is optimized. An adequate output need
not preserve every action response or identify x.

Write H_a={x:a∈Γ(x)}. Empty preimages are harmless. Let τ(H) be the minimum
number of these sets whose union is X; nonempty Γ guarantees a finite cover.

## 2. JRC-1 — complete constructive coverage

The minimum message alphabet is exactly m(Γ)=τ(H). Equivalently,

    m(Γ)=min_{f(x)∈Γ(x) for every x} |image(f)|.

**Proof.** Every message fiber c⁻¹(z) lies inside H_{d(z)}. Thus the decoded
actions of all used symbols cover X and at least τ(H) messages are necessary.
Conversely choose a minimum cover and send the index of the first covering
set containing x; decode to its action. Every input succeeds, so the bound
is attained. Any adequate selector f factors through its output image, and
any encoder/decoder composes to such an f, proving the second equality. QED.

This covers arbitrary finite code implementations at this message interface,
not just lookup tables. Enumerating all action subsets or all adequate selectors
is a terminating exact algorithm on the supplied finite relation. The checker
uses a memoized uncovered-set recurrence: choose an uncovered point x, branch
over H_a containing x, and minimize 1+V(U\H_a). Every branch removes x;
any cover must contain one such set. This proves exactness by induction on |U|.
It does not prove an efficient solver or small physical encoder/decoder.

SC-1's no-side-information hypergraph coloring is the same optimum: a fiber
is valid exactly when all its acceptable-action sets have a common member.
Pairwise compatibility alone need not determine that intersection.

## 3. JRC-2 — product obligations with a shared message

Supply Γ_i on X_i,A_i, i=1,2. Every pair in X_1×X_2 is admitted, and the
acceptable output pairs are exactly Γ_1(x_1)×Γ_2(x_2). No probabilistic law is
needed. The joint encoder sees both inputs; its one message can depend on both.
The decoder emits the pair. Then

    m_12 = τ({H^1_a × H^2_b : a∈A_1,b∈A_2}),
    max(m_1,m_2) <= m_12 <= m_1 m_2.

**Proof.** Apply JRC-1 to the product relation: an output pair has precisely
the displayed rectangle as its adequate preimage. Products of two local
minimum covers give the upper bound. For any fixed x_1, the second-coordinate
sets of rectangles containing that row cover X_2, requiring at least m_2
rectangles. Fixing x_2 gives the other lower bound. QED.

For a stronger incidence certificate put n_i=|X_i| and
s_i=max_a |H^i_a| (positive). Counting row/message incidences gives

    m_12 >= max(ceil(n_1 m_2/s_1), ceil(n_2 m_1/s_2)).

Each of n_1 rows requires at least m_2 messages, while one message intersects
at most s_1 rows. The second inequality exchanges the roles. Counting cells
also gives ceil(n_1 n_2/(s_1 s_2)); that weaker bound need not be sharp.

If the admissible encoder/decoder must be a product of local protocols,
c=(c_1,c_2), d=(d_1,d_2), its used alphabet is exactly the product of local
used alphabets on the full Cartesian domain. Its optimum is m_1m_2.
For exact functions Γ_i(x)={f_i(x)}, even the arbitrary shared encoder needs
|image(f_1)|·|image(f_2)| messages, because every distinct output pair must be
decoded. These positive results preserve GG27/GG28 and specify their scope.

The message width is b=ceil(log2 m), with b=0 for m=1. Log-alphabet additivity
does not imply additivity of separately rounded bit fields. Compare the shared
code against an optimally packed product alphabet, not an artificially padded
parent. All constructions below use that matched baseline.

## 4. JRC-3 — independent ambiguous tasks need three, not four, messages

Let X=A={0,1,2} and Γ(x)=A\{x}. Locally any action covers two inputs, so
m=2. Jointly send one of the three diagonal outputs (0,0),(1,1),(2,2): for
any (x,y), at least one a differs from both inputs. Each rectangle has four
cells; two rectangles cannot cover the nine inputs. Thus m_12=3<2·2=4.
Both three and four messages require two fixed bits: this example establishes
alphabet savings, not a fixed-bit saving. Its local pairwise conflict graph
has no edges, yet a constant action is impossible because the triple
intersection is empty. The hypergraph/cover condition is load-bearing.

## 5. JRC-4 — a strict packed-bit saving with five inputs

Let X=A={0,1,2,3,4}, defining adequate-action preimages by

    H_0={0,2}, H_1={1,3}, H_2={2,4}, H_3={0,3}, H_4={1,4}.

Equivalently Γ(x)={a:x∈H_a}. These are the maximal independent pairs of a
five-cycle, used only as an explicit set system. Locally m=3: two sets cover
at most four points, and H_0,H_1,H_2 cover all five. For the joint obligation,
this decoder list covers every one of the 25 inputs:

    (0,0),(0,1),(1,0),(1,1),(2,2),(2,3),(3,2),(4,4).

Choose the first listed rectangle containing the input as its encoded symbol.
Every fixed first-input row needs three second-input sets. The five rows
therefore need at least 15 row/message incidences; any message spans at most
two rows. Hence 2m_12>=15 and m_12>=8. The eight-message construction attains
this bound, while separately optimal protocols use 3·3=9 messages. Packing
both alphabets optimally gives three versus four fixed bits. The elementary
cell-area bound gives only ceil(25/4)=7 and is not the exact lower certificate.

The finite evidence checks all 25 encoded outputs against both original local
relations. It does not claim exhaustive enumeration of 4^25 joint selectors;
the general coverage proof, incidence lower certificate and explicit encoder
establish the optimum. The eight-subset search is reproducible construction
work; it is not evidence for a new graph capacity or asymptotic rate.

## 6. Scientific ceiling

Independent obligations permit this saving because the feasible shared-message
class is larger than the product-protocol class. This is no counterexample to
a theorem that already restricts machines to products. It also does not turn
message compression into controller-memory, code-length, acquisition, energy
or lifetime dominance. Those are distinct jointly realized resource coordinates.
The finite relation and lawful input/output interface remain supplied premises.
