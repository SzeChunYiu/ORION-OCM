# GMI #833 transform geometry v1 — freeze

Freeze scope: finite exact deterministic transformation kernel for architecture-name-free morphology classes.

Parent issue: #833.
Programme anchor: issue comment 5687604615.
Base main: `4bf5b2164b152556db19007630e784becb3937a8`.

## Frozen theorem targets

### TRANS-1A — category laws at registered finite scope

A registered morphology transform is a directed edge carrying source, target, exact semantic-error increment, nonnegative lifecycle-resource vector, assumption set, and evidence token. Valid transforms include zero-cost/error identities. Composition is defined only when endpoints match, assumptions are compatible, and evidence is present; it adds semantic error and resource vectors and unions assumptions/evidence.

Prove by exact construction/checking that:

1. left and right identities preserve every transform field up to canonical evidence/assumption representation;
2. valid composition is associative;
3. malformed, endpoint-incompatible, negative-cost, evidence-missing, or assumption-conflicting transforms fail closed rather than yielding a transform;
4. resource/error composition is componentwise additive and therefore subadditive for any path that is later compressed by an independently supplied direct transform.

### DIST-1A — directed shortest-transform law under frozen scalarization

For a finite registered transformation graph with nonnegative semantic-error penalty and nonnegative resource coordinates, freeze strictly positive scalar weights. Define edge burden as weighted resources plus nonnegative error weight times semantic error. Define `d(M,N)` as the minimum total burden over valid directed paths, and `+inf` if no valid path exists.

Prove/check:

1. `d(M,M)=0` via identity/empty path;
2. directed triangle inequality `d(A,C) <= d(A,B)+d(B,C)` whenever the right side is finite;
3. symmetry is not required and an exact hostile must witness `d(A,B) != d(B,A)`;
4. unreachable pairs remain `+inf`;
5. changing positive scalar weights may reverse incomparable direct resource alternatives, so the raw Pareto/resource vectors remain primary and scalar distance is explicitly price-conditional.

## Frozen boundaries

This tranche does **not** claim:

- developmental naturality or learning-trajectory equivalence;
- topology of the full infinite machine-intelligence space;
- grammar/remint invariance;
- P3/P4 known-family recovery;
- unknown-form discovery;
- universal category-theoretic novelty.

Parent mathematics receives first refusal: ordinary categories/path composition, shortest-path/Lawvere-style directed metrics, nonnegative weighted sums, Pareto order, and generalized metric spaces.

Expected claim ceiling if all exact/hostile checks are green:

`GMI_TRANSFORM_CATEGORY_AND_DIRECTED_SCALAR_GEOMETRY_AT_REGISTERED_FINITE_SCOPE`
