# V17 / Q preregistration — actual context specializations

Control plane: #1068. Historical programme: #833.
Planning parent: 557d2f9a2fb357ca6ae03fed8d300c30b13fef3a (PR #1112).
Merge the published P/V16 main ancestry before Q publication; do not rewrite P.
This freeze precedes all Q outcome code, proofs, tests, receipts and adjudication.
Only GMI2-R2-005 is eligible for original-atom closure in this study.
Exact original title: "characterize scalar/vector/viability contexts".
Original evidence kind: FORMAL_OR_FINITE; current V15 status: UNKNOWN.

Original R2 freeze target 5, preserved verbatim:
> Show scalar utility, acceptance, viability, vector cost and Pareto evaluation are special context codomains, not separate ontology.

Original THEORY_V1 additionally names confidence objects. Its interpretation
here is declared information order, with no inferred statistical calibration.
The target requires actual contexts and mathematical laws, not example labels.

## Q1 — context constructors and exact domain/order laws

Reuse the immutable V15 Context, PreorderSpec, relative P-intersection and
three Outcome constructors: illegal, undefined, value. P:H→Prop is admission;
E:H→Prop is ambient evaluator definedness. Active histories satisfy P∧E.
An evaluator may be defined on illegal histories; its value stays unobservable.
No constructor replaces P by E, E by P, or an absent value by a default value.

Construct actual codomain maps/postcomposition on any Context H W.
For f:W→Z and a declared preorder on Z, postcomposition retains E exactly and
maps only the value case of observe; illegal/undefined are unchanged.
Prove identity/composition laws and comparison preservation under monotonicity.
Prove comparison reflection under an explicit order-reflection hypothesis;
monotonicity alone must not imply reflection or preservation of incomparability.
Construct the dual preorder/context, prove comparison reversal and unchanged
P/E/nonvalue tags, and prove double dual returns the original order/evaluation.

Construct shared-domain finite products: each component evaluates on the same
E, values are finite tuples and order is coordinatewise. Retain E even in
zero dimensions; the unique empty tuple does not erase undefinedness.
Also construct independently partial products with Eprod=intersection of all
component E predicates. Prove the exact intersection and joint observation law.
For an empty independent family the intersection is True, so every admitted
history has the unique empty-tuple value. State this difference explicitly.
Prove actual projection/comparison laws without assuming an undeclared total order.

## Q2 — actual specializations, not separate primitives

Construct generic utility contexts into any declared preordered scalar space,
with an actual Int example; any Real interpretation must have its proof level
stated separately from an Int-only kernel instance.
Construct Bool acceptance contexts with false≤true and the actual 0/1 Int
embedding; prove its comparison-preserving and comparison-reflecting property.
Construct finite vector contexts and Pareto coordinatewise comparison.
Construct vector resource burdens and explicitly dual cost preference when
smaller burden means better. The orientation is supplied, not inferred.
Do not choose a scalarization or totalize incomparable vectors.

Construct uncertainty/confidence values as nonempty subsets of a declared
possibility type, ordered by reverse inclusion (narrower means more precise).
Prove the actual preorder and contextual evaluation laws. Executable constructors
reject empty confidence values; do not equate inconsistency with maximal confidence.
This is an information order, not a probability, calibrated confidence level,
coverage guarantee, truth guarantee or empirically validated uncertainty model.
Skip interval-specific and bundled preorder-category expansions in this round.
All six specializations must instantiate the actual generic Context interface.

## Q3 — viability with genuine infinite-horizon semantics

Let X be any state type, K:X→Prop a safe predicate and R:X→X→Prop a relation.
R need not be deterministic, total, finite, computable or finitely branching.
R is a declared one-step evolution advancing the discrete index. Category
identities/empty paths are not inserted as time-advancing transitions; a self-loop
counts only if explicitly present in R. This transition interpretation is extra
declared process structure, not a consequence of bare category laws.
Set T(A)(x):=K(x)∧∃y,R(x,y)∧A(y).
Define V(x):=∃I:X→Prop,I(x)∧∀z,I(z)→T(I)(z).
Derive T monotonicity, V⊆K, V=T(V), and greatest-postfixed-set inclusion.
The fixedpoint and maximality conclusions must not be assumed as interface laws.

Prove, with explicit classical choice, that V(x) holds iff there exists
γ:Nat→X with γ(0)=x and, for every n, K(γ(n)) and R(γ(n),γ(n+1)).
The forward proof chooses a successor within V and uses Nat recursion;
the reverse proof uses the range of the actual trajectory as a safe postfixed set.
Do not replace one infinite trajectory by independently chosen finite prefixes.
Construct the actual Bool viability context by applying V to an endpoint/state
map defined on E; retain the caller's P, E and illegal/undefined observations.
No physical-system identification, effective arbitrary-state membership decision,
robust adversarial safety, continuous-time limit or numerical convergence is claimed.

Kernel-check a countably branching countdown countermodel: a root chooses any
finite natural countdown chain; all states are safe, but zero has no successor.
Every finite safe horizon is realizable from the root, yet no infinite safe
trajectory exists. Thus intersecting all finite-horizon survivor sets is not
silently identified with V under the general assumptions above.

## Prospective falsifiers and exact finite calibration

These numbers are planning algebra, not reported outcomes or empirical predictions.
Enumerate all labelled relations R and safe masks K on n=0,1,2,3 states:
4,165 cases, 12,420 state-membership answers and 13,975 candidate safe subsets.
Compare production descending elimination with independent cycle-reachability
and union-of-all-safe-postfixed-subsets oracles. A horizon-only oracle is invalid.
Cover empty K/X, safe deadends, safe cycles, and a branch with one safe infinite
choice plus one deadend, which separates existential from universal safety.

Enumerate every preorder on labelled carriers of sizes 0..3 and every map
between them: 24,907 candidate maps. Measure the accepted monotone/reflecting
map counts; do not invent them. Use two-history status contexts for accepted
maps and actually test value/comparison/tag laws.
A monotone constant map must collapse a distinction; a nonmonotone map must
fail preservation where appropriate. Do not infer reflection from injectivity alone.

Specialization corpus: utility125 (three histories with three values plus two
nonvalue statuses), acceptance64 (three histories), vector utility121 and
reversed-cost121 (two histories, nine 2D values plus statuses), and nonempty
subset confidence81 (two histories, seven nonempty subsets plus statuses).
Total512 actual contexts. Exercise actual evaluator values, comparisons and
three tags, including defined-on-illegal controls independent of these counts.
Independent partial-product corpus: three histories, eight admission masks,
and each evaluator in {None,False,True}^3, yielding5,832 pairs. Explicitly test
intersection definedness, absent-component controls and the two empty-family
conventions. Additional malformed-type, empty-confidence, zero-dimensional,
nonmonotone-map and incomparable-vector controls are mandatory.

## Evidence, custody and successor contract

Use an independent oracle that does not call production logic for its answer.
Persist actual measured counters with mandatory module/key/type/count guards,
clean positive controls and real hostile mutations. Normal/optimized receipts
must agree. Missing tools/inputs are CANNOT_CHECK exit2; checked invalidity is1.
Fresh Lean4.19 replay must register exact theorem types, including constructor
outputs, domain/tag laws, viability fixedpoint and both infinite-run directions.
Build every inherited dependency from its bound source in an isolated directory.
Source-valid corruptions must compile the changed source but fail the typed
AUDIT; include a constructor/domain law and an infinite-trajectory direction.
Finite enumeration does not prove arbitrary functions linear/monotone or certify
an arbitrary callback's declared domain; premises stay explicit in the theory.

The successor snapshot must preserve all222 original IDs/titles, every existing
CLOSED atom and every untouched status/evidence/disposition. Only R2-005 may
move UNKNOWN→CLOSED after independent scientific/formal review and all gates.
Its evidence must point to this round's actual registered proof and receipt.
Original fulfilled18/unresolved204 then becomes fulfilled19/unresolved203.
R2 remains OPEN; R0 remains the only whole-EARNED round; overall closure OPEN.
Original R2-003/007 remain UNKNOWN, and R2-008/009 are untouched.

The V16 scientific/amendment records remain immutable historical18/204 totals.
A new current reconciliation must derive19/203 from the new original snapshot
and separately carry the two still-qualified V16 replacements, yielding201
active unresolved. It must not report the old receipt totals as current or
count either qualified replacement as fulfillment of its original atom.
Bind exact source records, reject coupled scope/hash changes, and preserve
qualified-reading limitations and classical parent ownership. No novel mechanism,
canonical utility/prior, universal scalar or complete intelligence theory is claimed.

## Primary assimilation and exact inherited bindings

Tarski1955 Theorem1 pp286–287, read before mechanism selection, owns the
greatest-fixedpoint/union-of-postfixed-sets argument (powerset specialization):
https://msp.org/pjm/1955/5-2/pjm-v5-n2-p11-p.pdf
Stacks002Z Definition4.21.1 supplies preorder and dual-order conventions:
https://stacks.math.columbia.edu/tag/002Z
Coquelin–Martin–Munos2007 §I equation2 supplies indefinitely-safe trajectory
motivation. Its §II continuous dynamics/HJB/regularity/discretization results
are not assumptions or conclusions of this discrete relational study:
https://chercheurs.lille.inria.fr/munos/papers/files/DP_viabilite.pdf

The following SHA256 bindings refer to actual planning-parent source bytes.

| Source | SHA256 |
| --- | --- |
| research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json | 4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574 |
| research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md | cd3754eb383e2796c3fe06dc7e9fbb7cf17d9d0bca35bea983e43fbc6b6ae320 |
| research/gmi-1068-r2-context-irreducibility-v1/THEORY_V1.md | 09773eab96a80843585154e6211e494b9ca721393542a8cbdd114fe7bae3ab5e |
| research/gmi-1068-partial-context-v15/CORE.md | 5d0dc01e0abf9b2e2ff39afb5cbf80fb994e0c28bc7ee9c7e2e71543b3f7ceb0 |
| research/gmi-1068-partial-context-v15/PartialContextV15.lean | 332dcfb63304d5668800ea21f09795c2d92267989291ffe35d9e38ea2db0edf5 |
| research/gmi-1068-partial-context-v15/RESULT_V15.json | 9db4c35d4184e1e080f8bcf88950a16fc5d0d7e55b6ae4c86736ba75068b4101 |
| research/gmi-1068-recursive-audit-v15/SCOPE_SNAPSHOT_V15.json | 4bb8d4dc9b0a918bb172a1d1c4e38e325a8af85f6e57c00788c6b63133070b61 |
| research/gmi-1068-corrected-targets-v16/TARGET_CONTRACT_V16.json | faa8f83c0af7a2f0a042e84deb7be191b09a281c08f287c5e986397124177902 |
| research/gmi-1068-corrected-targets-v16/RESULT_V16.json | 18bea5c6f85b4fcc91c40c53cbf63df59c38d70e9e839efc4585f6640497ad1a |
| research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json | e1cc2d2dbc10171407577889f75ac531c30cf09eab224fc3823f3931c5048618 |
| research/gmi-1068-amendment-governance-v16/RESULT_V16.json | ed491fab2cd0b69fb4ee845b82e349c79ff0d70f0dbc1d312ee0755645437de4 |
