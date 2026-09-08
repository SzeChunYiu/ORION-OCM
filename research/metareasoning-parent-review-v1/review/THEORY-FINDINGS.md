# Actionable source findings

Frozen commit: `9087971dd3a9847149fa8cf844cb13e84a57cacd`.
Source inspection and by-hand mathematics only; priorities concern this scope.

## T1 · P2 · State a termination condition for cognitive transitions

**Evidence:** [formal note, lines 39–57](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/ACTION_SUFFICIENT_STATE_V1.md#L39)
allows nonnegative prices and introduces a supposedly finite stopping recurrence.
[Lines 101–118](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/ACTION_SUFFICIENT_STATE_V1.md#L101) preserve demand horizon
`h` on a cognitive transition. Neither passage supplies a cognitive-depth
index, a decreasing rank, or a definition restricting policies to proper
termination. A finite number of demands alone does not bound cognitive steps.

**By-hand witness:** one state has a certified action costing 1 and a cognitive
action costing 0 that returns to the same state, leaving `h=1`.
The displayed recurrence becomes `J = min(1, J)`. Every `J in [0,1]` solves
it. If eventual action is required, the actual value is 1; if infinite
zero-cost cognition counts as a feasible policy, the machine can avoid serving
the demand. Nonnegative scalar prices permit this case even when a cognitive
operation consumes an unpriced resource.

**Impact:** the recurrence alone does not define the intended finite stopping
value or guarantee that its selected policy ever acts. This is a formal
assumption defect, not evidence of a runtime hang or of an erroneous R0B row.

**Repair:** define the policy class and terminal values. The simplest finite
form adds a cognitive allowance `k` (or a well-founded state rank), decreases
it on every cognitive transition, freezes `J(sigma,0,k)=0`, and disables
cognition when `k=0`. Define `min(empty)=+infinity` for unavailable actions.
Alternatively specify a stochastic-shortest-path formulation with conditions
that make proper termination and Bellman-value selection valid; merely adding
“finite horizon” while leaving `h` unchanged is insufficient.

**Scope control:** the actual R0B DP uses the previous horizon on both arms
([regime_sweep.py 183–205](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/regime_sweep.py#L183);
[prospective_selector.py 119–150](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/prospective_selector.py#L119)).
Those recurrences are well-founded in `h` and do not instantiate this defect.

## T2 · P2 · The purported exact action/collision audit uses approximate ties

**Evidence:** the protocol defines the genuine `argmin` action set and exact
bucket intersections ([protocol 148–169](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/PROSPECTIVE_SELECTOR_PROTOCOL_V1.md#L148)).
The implementation instead returns `"tie"` through `math.isclose` with
`rel_tol=1e-12` and scaled absolute tolerance
([prospective_selector.py 100–104](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/prospective_selector.py#L100)).
These labels decide collision counts at
[171–180](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/prospective_selector.py#L171), while the module and audit
docstrings call the result exact ([1–10](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/prospective_selector.py#L1),
[158–159](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/prospective_selector.py#L158)).

**By-hand witness, not a frozen-population result:** put two states in the same
feature bucket with action pairs
`(1, 1 + 2^-42)` and `(1 + 2^-42, 1)`.
The numbers are representable in binary floating point. Their exact optimum
sets are opposite singletons, yet both differences fall below the specified
tolerance, so the classifier calls both “tie” and records no collision.
This also illustrates why tolerance ties and literal minimum-based regret
need not give matching zero/nonzero classifications.

**Numerical extension:** both DPs initialize values as `0.0` and repeatedly
divide by `n`; the static expectation uses floating powers
([regime_sweep.py 123–134](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/regime_sweep.py#L123)).
The audit clamps a negative computed regret to zero
([prospective_selector.py 182–188](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/prospective_selector.py#L182));
the phase-1 residual likewise clamps at zero
([regime_sweep.py 207–210](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/regime_sweep.py#L207)).
There is no explicit exact-arithmetic or interval certificate for action
margins, collision counts, regret, or the 8% comparison in these sources.

**Impact and limit:** the code establishes an approximate numerical audit.
The source supports an exactness-claim defect. It does **not** establish that
any particular frozen 142-target label, collision count, phase boundary, or
8% statement is numerically wrong. No such computation was performed here.

**Repair:** certify all action-gap signs and bucket regret by exact scaled
integers/rationals, or publish outward error intervals and label any unresolved
action “numerically unresolved.” An epsilon-optimal set is another legitimate
choice only if the protocol, lemma application, output names, and claims all
use that relaxed meaning. Retain raw signed residuals before any display clamp.
See the [integer certificate specification](THEORY-BOUNDARIES.md#exact-numerical-repair).

## T3 · P2 · README still contains the economically invalid stopping rule

**Evidence:** [README 191–201](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/README.md#L191) says that if surviving
models license a common safe action, “stop identifying”; it considers another
probe only “If not.” The newer note explicitly explains why this is insufficient
for economic stopping ([formal note 18–35](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/ACTION_SUFFICIENT_STATE_V1.md#L18))
and corrects that implication ([64–77](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/ACTION_SUFFICIENT_STATE_V1.md#L64)).

**By-hand witness:** two surviving models both permit a safe action costing 10.
A cost-1 probe distinguishes the models and enables a model-specific protected
action costing 1. Acting immediately costs 10; probing and then acting costs 2.
The common safe action justifies safety without identification, not economic
stopping.

**Repair:** update the README gate to say that common-action existence makes
full identification unnecessary for safety, and stop only when the registered
paid-cognition comparison favors the stop arm. Consider that comparison
regardless of whether a common safe action already exists.
