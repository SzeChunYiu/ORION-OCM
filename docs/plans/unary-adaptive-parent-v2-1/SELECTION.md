# Training, utility selection and runtime policy

## Mechanical acquisition and real development evidence

Training rows are solved by the shared exact RegionSolver and independently checked
by verify_result. All 32 original rows must return accepted complete semantic results.
Within each A, training retains one engine per exact predicate registry, preparing every
row anew while retaining expression masks. Development has its separate cold-trial policy below.
UNKNOWN is a valid result with both models; INCONSISTENT is a valid result, not a failure.
Malformed, refused, missing or unverifiable training rows stop acquisition for that
episode. Preserve all attempted rows and mark dependent stages CANNOT_CHECK.
Never silently pass a successful subset to the miner or invent result receipt fields.

Call actual acquire once on the ordered strict {task,result} list. It validates all
training answers, enumerates proper two/three-premise universal subcovers and checks
every premise's necessity. The retained 2–3-premise training workload only permits
two-premise proper fragments. Require at least two distinct semantic training supports
per rule, as implemented. Retain all candidates, attempts and rejected reasons.
No grammar, checker, solver, schema or interpreter is acquired from these episodes.

The actual inner schema is `ocm.unary-rule.v1`, recipe `universal-cover.v1`, fields
schema,parameters,premises,conclusion,recipe,rule_id. Application binding/cover and
discovery/utility/current-correctness evidence belong to separate records.
An outer persistence envelope is not a second interchangeable rule format.

## Frozen development selection

Use the 16 development ASTs in accepted-slot order, formal presentation only.
For each row measure a fresh exact engine: prepare once, snapshot counters, complete,
snapshot counters, then independently verify its complete answer. The development
query score is the delta of constraints_checked across complete, excluding preparation.
Retain preparation, binding, checker, wall and other work; they are not erased by this score.

Evaluate every candidate independently, rule_id ascending; row order ascending.
Each candidate/row uses a fresh exact engine, one preparation, then actual apply_rule.
On PROPOSED verify the complete result. On no match/inconsistent base complete the
same preparation and independently verify. There is no precomputed query answer
inside candidate preparation. A refusal or invalid result invalidates the episode's
development selection; preserve observations, no candidate deletion to hide the defect.

For rule r, benefit is SUM over 16 rows of exact query constraints minus candidate
query constraints. Candidate query constraints are its engine's total delta after
preparation, including any fallback; proposed certificate assembly contributes its
actual observed delta. This is a narrow logical-work heuristic, not economic benefit.
Match cost M is SUM of matching_nodes + mapping_attempts + premise_index_reads +
index_probes from each actual apply_rule observation, with missing unvisited counters
zero only when a complete successful observation establishes they were unvisited.
Incomplete work is unavailable, never zero. All other observed counters remain retained.

Rank positive-benefit rules by (-benefit, M, canonical inner-rule byte length, rule_id).
Select the first min(8,number_positive). Zero/nonpositive rules remain archived but
ineligible for selected execution. Empty pool means NO_METHOD_ACQUIRED; a nonempty
pool with no positive rule means NO_DEVELOPMENT_BENEFIT. Neither triggers replacement.
The selected-library digest is SHA256 of canonical JSON of selected inner rules
in rule_id order; development report separately binds ranking, counts and observations.

This is independent ranking, not greedy marginal optimization. Its limitations are
reported. Admission uses the actual mined pool and this real utility receipt, checks
their source/task/result/library bindings, and cannot accept an authored-selected alias.
Both adaptive arm process-A runs perform this same algorithm physically and compare
pool, ranking and selected-library digests before final use. Keep both actual costs.

## Shared runtime and cache schedule

Both adaptive arms use the same proposal kernel, matcher, independent result/binding
checker, selected rules, first-match rule_id order and conclusion-kind index policy.
Prepare consistency once; index only the query's universal conclusion kind (negate
existential query first), try live selected rules in ascending rule_id, accept the
first fully checked structural match, otherwise complete the same prepared state.
No method ID in output alone earns causal-use credit; record the actual recipe branch.

Within each service/intervention arm process (B, C and role solves), maintain one
RegionSolver per exact predicate registry. Training and development follow their distinct
policies above; this service rule never overrides fresh development trials.
Reuse its expression-mask cache across calls; prepare every task anew because a
Prepared value is bound to the full task/query and only its issuing engine's last
preparation is valid. Never reuse a stale Prepared object or a cached final answer.
All arms have this same policy. New OS process starts with empty engine/cache state.
Final rows use fresh label registries; their two presentations share a registry/cache.
The exact parent can skip rule machinery; that saved overhead is its valid advantage.

Do not add premise-only query caching or an alternative matcher after study outcomes.
Any later stronger parent is a separately frozen successor comparison, with its actual
costs and previous observations preserved. The shared current solver already reuses
compiled premise constraints and consistency state across both query branches.

Correctness depends on schema proof and semantic/checker assumptions. Selection
eligibility additionally depends on live utility evidence. Discovery withdrawal changes
attribution, not mathematical validity; utility withdrawal disables selected invocation
without making the proved rule false. Reinstatement changes eligibility only and must
be followed by fresh matching and complete independent answer checking.

PARENT-POLICY.md fixes the conventional adapter's custody, replay and index-cache
boundaries; its smaller storage/control overhead is measured as a valid parent advantage.
