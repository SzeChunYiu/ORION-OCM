# V20 independent formal review

Reviewer authored the mathematical exposition but did not implement the Lean
sources or typed contract. This is independent code and proof review, not a
second independent author of the paper derivations.

## Actual replay

Read all nine new Lean sources, the immutable V15 interface, the static
proof_contract_v20 and the isolated checker. Independently executed a fresh
replay on billy-laptop with Lean 4.19.0: PASS, ten source modules and 100 exact
typed registrations. No cached project objects supplied the compilation.
The independently returned audit SHA256 is
`5eecc29b032a58934de79edd0383da1858ddfa09963b69bc31dd4d57660f90fc`.
The inspected contract SHA256 is
`45e0a2a53ad5f2cb43dff277dcdba6ce2dedae65ef0a8d869fdd0a6ad4bd9794`.
Registrations include constructors and operation equations; their number is not
a count of independent scientific theorems.

## Frontier construction and generality

FrontierOrderV20.extend_spec proves the scan invariant by list induction:
attained membership, domination of its starting value, and maximality against
every scanned value. Existence is derived rather than assumed. The actual
frontier is the registered maximality filter, with membership, cofinality,
downward closure and empty-input theorems. A DecidableRel supplies comparison;
no decidability of arbitrary mathematical orders is claimed.

AttainedFrontierV20 applies the actual V15 P-and-E restricted valueMap to a
finite history list via filterMap. Its membership equation includes selection,
admission, evaluator domain and actual evaluated value. The derived frontier
therefore instantiates the original finite-image target. List membership is
extensional here: Lean may keep duplicate occurrences of identical values,
where Python deduplicates them. No length equality or representative-cardinality
minimum is inferred from this proof. Those results have separate paper and
finite-calibration evidence.

WellFoundedFrontierV20 uses the attained subtype and the correct reverse strict
ascent relation. Its induction constructs a maximal element above each input;
it assumes well-foundedness, not the desired cofinality or existence conclusion.
It supplies neither finite frontier size nor an effective algorithm for arbitrary
infinite carriers. The four infinite separating examples remain paper proofs.

## Partial maps and actual contexts

GuardedMapsV20 includes definedness as well as output comparison. Necessity of
guardedness is proved from the actual two-element finite test and its upper
singleton pruning. Sufficiency works for arbitrary cofinal subsets. The upward
goal characterization uses all such predicates and principal upper-set tests.
Actual Option bind supplies the composition law.

PartialPostcontextV20 constructs a new evaluator domain using original E and
successful F output, independently of P. Proof irrelevance and actual returned
values identify the subtype evaluator; the typed contract binds post.order,
post_domain, post_eval, post_active, post_valueMap and post_attained.
All mapOutcome cases are separately registered. Illegal remains illegal;
a defined admitted value mapped to None becomes undefined. These equations do
not silently preserve the old evaluator domain or confuse illegal with undefined.
Classical choice for arbitrary proposition-valued domains is exposed in scope.

## Greatest simulation and endpoint pruning

SimulationV20 defines actual deterministic partial runs and the union of all
base-contained simulations. Word induction transports each simulation. In the
reverse direction, the first action determines one right successor shared by
every suffix; this is exactly where determinism matters. The empty word supplies
base containment. Reflexivity and transitivity follow from the word condition,
so the constructed simulationOrder has actual preorder laws.

The registered run equations, simulation clause, greatest-union equation and
simulation-order relation bind those constructions. Extra right-side actions
are permitted; the claim is one-sided and uses identical action words. It is
not a nondeterministic trace-language equivalence theorem.

SimulationPruningV20 derives word guardedness and cofinal endpoint pruning.
The value bridge explicitly assumes guardedness of the actual P-and-E active
endpoint evaluator under the supplied base order. Its proof then uses simulation
containment in that order. Actual WordAttained and its image equation ensure
that value preservation concerns evaluated reached states rather than a merely
named observer. No unsupported assumption is hidden in the endpoint conclusion.

## Typed-audit controls and proof boundary

Read test_kernel_guard_v20. Four isolated source-valid controls replace all
sources with empty imports, or respectively replace the exact frontier,
guarded-map and greatest-word contract leaves by True. Each requires failure at
AUDIT after SOURCE compilation; hash mismatch alone cannot count as rejection.
The integrated driver's outcome is recorded in RESULT_V20, separately from this
review's independent clean replay. The checker rejects unproved constructs and
sorryAx, treats warnings as errors, and distinguishes unavailable inputs from
invalid compiled statements. No additional scientific axiom was introduced.

Finite representative minimality, Python refinement and pair-search termination/
correspondence, and the actual V8 endpoint adapter are paper plus finite results.
The generic kernel endpoint theorem does not establish full EDGE/output/cost
trace equality or certify the Python adapter. FORMAL_SCOPE_V20 states these
boundaries correctly. No defect remains in the inspected proof sources or typed
registrations; only original R3-004 receives the bounded construction evidence.
