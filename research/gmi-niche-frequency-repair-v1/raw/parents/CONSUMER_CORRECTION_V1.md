# PR551 consumer repair: native ports and update-side state

## Source and parent

Reviewed upstream head:
[6a4495bbd4f2df9acf883ef630c3c0a03858675f](https://github.com/SzeChunYiu/ORION-OCM/commit/6a4495bbd4f2df9acf883ef630c3c0a03858675f).
The author delta adds 49 freeze lines and changes the scanner's whitelist;
its preceding first-parent commit imports then-main1277. It adds no raw
execution record for its newly reported source population. This does not
establish that no execution occurred or that the reported scores are invalid.

The mature local parent is the accepted
[B6 typed census](../gmi-b6-consumer-census-v1/CENSUS_CONTRACT_V1.md).
Its contract, native AST role extraction and graph analysis are reused unchanged.
The new analysis adapts their port distinctions to the conditional update schedule.
The primary semantic authority is the bound actual VM and IR, not a neural
architecture label. NAR's
[parameter-adjoint correction](../gmi-native-adjoint-repair-v1/PARAMETER_ADJOINT_CORRECTION_V1.md)
separately repairs the former adjoint marker. This unit makes no new AD theorem.

## CPR-1: parameter routes are port-specific structural observations

DENSE has no input ports and emits a list of allocated parameter-cell names.
LINEAR reads names on port0 and numerical data on port1. AFFINE has the same
roles. GRAD reads names on port0, prediction on port1 and target on port2.
EDGE port0 returns its input unchanged. These roles are extracted from the
bound native declarations and AST; DOT is absent from the declared alphabet.

Therefore a DENSE→LINEAR edge into port1 is not evidence that DENSE supplies
coefficients, although both ports have the declared vector type. The scanner
records every relevant role and follows only identity EDGE chains. All other
route semantics remain UNINSPECTED; absence of an inspected identity route
is not a general impossibility of indirect influence.

Even a valid parameter route does not prove effective numerical contribution:
names, dimensions, runtime value types, masking, saturation, learning rate,
zero gradient, and later use matter. No field promotes adjacency to causal use.
The old incoming-edge "writer" proxy is removed: DENSE has no graph input
ports, and state writes are not represented by incoming dataflow edges.

## CPR-2: GRAD writes state without exporting a result value

The bound VM constructs its evaluation order from every genotype node,
putting forward nodes before update nodes. Query evaluation skips U nodes.
Evaluation with a supplied feedback label reaches GRAD provided initialization
and prior evaluations complete; graph disconnection from OUTPUT does not
prune it. Actual entry/completion is not established by static inspection.

The GRAD branch checks list-of-string names and scalar prediction/target,
backpropagates the error, and conditionally writes named parameter cells.
It returns None. The branch never requires an outgoing GRAD edge. Future
LINEAR/AFFINE evaluations read the updated cells directly through their names.

Thus "only eight graphs route the GRAD update back out" cannot identify a
missing update mechanism. The retained NAR audit already includes a native
zero-outgoing-edge graph with a nonzero cell update. We do not repeat that
execution. Conversely, outgoing edges or DENSE→GRAD wiring do not establish
a nonzero gradient, changed value or successful learning. The static report
keeps all of these effects UNVERIFIED. No full callback, storage or physical
resource equivalence follows.

## CPR-3: population and provenance boundaries

The retraction of campaign-wide GRAD absence is accepted. The established
historical census contains eight GRAD-bearing graphs in 350 retained source
graphs, plus source-bound selected-arm observations. It also established six
numeric parameter-port adjacencies among the 17 old scanner rows.

The new appendix reports 34/677 cells across nine of11 archives,33/34 with a DENSE
input,8/34 with an outgoing edge, and0/34 above the standard threshold.
No complete source list, per-cell table, invocation, runtime identity or
cost record for that enlarged population is added by the two-file author
delta. These remain retained reports; the denominator is not silently
identified with the earlier350 or selected70. If the reported scores were
verified under the same protocol, they would constrain those cells and that
standard test, not an entire architecture family or the corrected runtime.

The old VM blob is unchanged from the previously audited551 source and
precedes NAR. This unit parses the current NAR-corrected VM. Its static role
agreement with historical graphs does not remeasure their capabilities.

## Positive mechanism and validation

The active scanner uses the repaired module, emits source hashes and exact
selected JSON field paths, and distinguishes STRUCTURE_INSPECTED,
NOT_RETAINED, unsupported/invalid input and missing input. No matching files
is explicitly unavailable evidence, not a zero-incidence population claim.
All other source fields and unretained search states stay UNINSPECTED.

The real no-alarm check covers422 selected source/arm/witness rows with an
independent reverse-route oracle, and87 original overlapping arm/scan
descriptions with exact role equality. It preserves the original350-source,
eight-GRAD and17-row/six-parameter baselines; no graph is evaluated.

Hostile controls exchange parameter/data ports, add an AFFINE consumer,
remove every GRAD output edge, add an output edge, remove the target port,
set zero width/rate, insert a nonidentity route, and supply malformed inputs.
The outcome is correct classification or explicit uncertainty/refusal, never
a forced causal verdict. All operations are static parsing, traversal and
hashing; their host work is not a campaign/lifetime cost measurement.
