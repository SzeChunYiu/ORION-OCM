# Ecology laws: affine structure from obligations

Status: conditional mathematical derivations, with an executable finite constraint interface.
These results characterize entire admissible affine classes; architecture names are absent from the premises and solver input.
They specialize established equivariance theory; the contribution here is the explicit obligation, compilation and resource accounting interface.
See [sources](ECOLOGY_SOURCES.md), [family consequences](KNOWN_FAMILY_DERIVATIONS.md), and [memory laws](MEMORY_SELECTION.md).

## E1. When an affine representation is forced

Let the input and output be finite-dimensional vector spaces over a field F.
For a required response f, put b=f(0) and h(x)=f(x)−b.
Assume the obligation requires h(x+y)=h(x)+h(y) and h(ax)=a h(x) for every admitted x,y,a in the whole vector spaces/field.
Then f(x)=Wx+b, with W's ith column h(e_i).
Proof: expand x=Σ_i x_i e_i and apply the two identities; conversely every such W,b satisfies them.
Over R, additivity plus continuity suffices: integer and rational homogeneity follow by repeated addition/division, then real homogeneity by continuity.
Without real homogeneity or regularity, additive pathological functions need not be real-linear.
Without these obligations, equivariance alone permits nonlinear maps, for example coordinatewise cubing under permutations.
Finite examples do not establish the universally quantified obligation; it must be stipulated, proved from the task, or separately warranted.

## E2. Exact coefficient space from finite symmetries and allowed dependencies

Let a finite group G act by permutations on input positions I and output positions O.
Use (gx)_{gi}=x_i. An allowed incidence set E⊆O×I requires W_{oi}=0 outside E.
The obligation f(gx)=g f(x), for every x and g, is equivalent to

    W_{go,gi}=W_{oi},     b_{go}=b_o.                         (1)

Proof: put x=0 to obtain the bias equality, then x=e_i to obtain each matrix equality; these equalities imply equivariance by substitution.
Generator equalities suffice: composition and inversion propagate equality to the generated finite group.
If E is not invariant, define E°=∩_{g∈G}gE, the union of pair orbits wholly contained in E.
Any orbit meeting E's complement has a forced zero entry and hence all its entries zero by (1).
Every wholly included orbit has one freely chosen coefficient; different orbits impose no further constraint.
Therefore indicator matrices of included pair orbits and indicator bias vectors of output orbits form a basis V, with

    d=dim V=|E°/G|+|O/G|.                                   (2)

The indicators have disjoint nonempty support, proving independence; (1) proves spanning.
With C_in,C_out channels on which G acts trivially, the dimension is

    d=|E°/G| C_in C_out + |O/G| C_out.                       (3)

Here E refers to the spatial incidence; all channel pairs are allowed. Other channel actions require their actual product action.
Omit the bias term if a separate obligation fixes b=0.
More generally, if biases are allowed only on B⊆O, use B°=∩_g gB and replace |O/G| by |B°/G|; a partially forbidden bias orbit is forced entirely to zero by the same proof.
Equivalently append a fixed input coordinate x_*=1, let every input permutation fix *, and treat allowed biases as ordinary allowed pairs (o,*). This is the compiler's representation.
This is the smallest dimension of any surjective **linear** coordinate parametrization of V: a map F^q→V has rank at most q.
It is neither a bit lower bound for an individual target nor a ban on discontinuous arbitrary-real encodings.

## E3. Neutral exact compilation and certified realizations

Flatten W,b and express (1) and forbidden coefficients as a matrix A with entries in {−1,0,1}.
Exact rational elimination computes ker A. The preceding proof identifies ker A with V, independently of the elimination algorithm.
Thus a finite generator/support specification constructs all admissible affine operators without enumerating candidate network families.
Equality constraints over Q have the same rank over R, so the returned rational basis also spans the real solution space.
An independent finite group closure/orbit calculation can check dimension and subspace agreement; it must handle noninvariant E using E°.
The canonical orthogonal projection onto V averages coefficients within each included orbit, zeros excluded entries, and averages biases within output orbits.
Proof: on each disjoint block, Σ_j(z_j−a)^2 is uniquely minimized at its arithmetic mean.

For scalar channels, a direct program stores d scalar coefficients, fixed incidence instructions and input/output workspace.
Initialize output accumulators with their biases; for each (o,i)∈E°, multiply its orbit coefficient by x_i and add into output o.
This uses |E°| multiplications and |E°| additions, plus explicit loads, writes, indexing and control.
The current generic compiler instead initializes zeros and applies a uniform multiply-add also to the constant coordinate; its trace therefore counts |E°|+|B°| multiplications and additions. The bias-initialization version is a separate valid optimization.
The counts are constructive upper bounds. Algebraic factoring, sparsity of a fitted target, or transforms can reduce them.
Scalar slots do not bound bit storage: coefficient precision, input precision, indices, code and workspace must be recorded.
Elimination, group closure, fitting, rejected specifications and certificate construction are development costs.

## E4. Consequences of particular task symmetries

For n cyclic positions, simultaneous translations preserve offset i−o mod n.
If k distinct offsets are allowed, exactly k pair orbits survive, and the output is one orbit:

    y_o=b+Σ_{r∈K} a_r x_{o+r},     d=k+1.                   (4)

The direct program uses nk multiplies and nk additions. This derives a shared local affine stencil if K is local.
A nonlinear activation, layer hierarchy, learned symmetry or convolutional network is an additional construction/premise.
For the full permutation group S_n, n≥2, there are two pair orbits: equal and unequal indices.
Writing the diagonal/off-diagonal coefficients as α+β and β gives

    y_i=α x_i+β Σ_j x_j+c,     d=3.                         (5)

Compute S=Σ_jx_j, T=βS+c, then each y_i=αx_i+T.
This requires n+1 multiplies and 2n additions, with n≥1 input positions; coefficient conversion and all nonarithmetic costs remain explicit.
For n=1 the dimension is 2, since there is no off-diagonal orbit.
For independent transitive input/output actions, all pairs form one orbit; only a common weighted sum and common bias remain.
Graph-specific automorphism actions and tensor-index actions fit the same theorem using their actual finite position sets.
Symmetry of a fixed graph does not establish a theorem about all graphs, graph sizes or unseen tensor orders.

## E5. Quantitative bias, sample and charged-cost crossover

Flatten the unconstrained coefficients as θ∈R^D. Fix a candidate subspace V independently of evaluation noise.
Suppose an admitted experiment produces z=θ+ξ with Eξ=0 and Cov(ξ)=σ² I_D/n.
Let P be V's orthogonal projection, d=dim V, and estimate θ̂=Pz. Then

    E||θ̂−θ||² = ||(I−P)θ||² + σ²d/n.                     (6)

Proof: θ̂−θ=−(I−P)θ+Pξ, whose summands are orthogonal pointwise.
The second squared norm has expectation tr(P Cov(ξ) P)=σ²tr(P)/n=σ²d/n.
Gaussian noise is sufficient but unnecessary; the identity uses only these first two moments.
For predictions Wx+b on a fresh x with Ex=0 and E[xxᵀ]=I, excess squared prediction risk equals squared coefficient error.
For another input covariance, replace this norm and projection/risk calculation by the corresponding weighted geometry.

One concrete experiment averages n independent full coefficient-vector observations with isotropic per-vector noise.
It observes nD scalar entries and must charge them. An orthogonal task design is another route only after proving its noise law and charging its measurements.
Equation (6) does not turn n arbitrary scalar task samples into D directly observed coefficients.

For registered nonnegative charges, define an implementation-specific prospective score

    J_V=||(I−P)θ||²+σ²d/n+λd+μW_V+C_dev,V/H.              (7)

Here H>0 is actual intended reuse, W_V is measured/derived per-use work, λd is the declared coefficient-storage charge, and C_dev,V includes the whole relevant acquisition/development bill.
Nonuniform precision, code, indexing, peak memory and other resources require their own terms; (7) is exact only for its specified score.
Against the unconstrained coefficient space with dimension D, V wins strictly exactly when

    ||(I−P)θ||² < σ²(D−d)/n + λ(D−d)
                   + μ(W_full−W_V) + (C_dev,full−C_dev,V)/H. (8)

This follows by subtracting the two scores. Equality gives a tie; reversing the inequality favors the unrestricted parent.
Thus symmetry mismatch, sample count, storage charges, execution work and reuse produce a quantitative selection boundary.
The work and storage terms describe registered implementations, not universal minima over all programs.
Selecting V after inspecting the same ξ invalidates a naive use of (6) for the selected estimator: selection itself changes the distribution.
Use fixed candidate laws with independent evaluation or the globally valid adaptive comparison certificates from the formal derivation unit.
Forecast C_dev/H is not realized repayment; actual reuse and all failed candidate costs must stay in the ledger.

## Falsifiers and scope

Delete one entry from an otherwise included nontrivial pair orbit: the entire orbit must disappear, not just that entry.
A basis that misses a valid coefficient vector or includes one violating a generator/support constraint falsifies E2/E3 implementation.
Coordinatewise cubing disproves any attempt to infer E1 from permutation symmetry alone.
Noise with a different covariance, a reused evaluation sample, or an input covariance different from the registered one violates E5 premises rather than refuting its algebra.
Under the stated moments, a correct independent exact noise witness must satisfy (6), including symmetry-breaking θ.
These theorems do not select a unique neural architecture, establish an unobserved ecological symmetry, or prove empirical superiority.
