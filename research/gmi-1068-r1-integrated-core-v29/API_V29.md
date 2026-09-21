# V29 registered Python interfaces and independent calibration

Package: research/gmi-1068-r1-integrated-core-v29; no execution before freeze.
Read the final FREEZE_V29, both scope/formal reviews and actual parent loaders.
SOURCE_PINS_V29 records the exact inherited inputs on merged V28 main.
Root supplies production; oracle imports no production to construct expectations.

## 1. Exact parent loading and common guards

Cache each actual module once, rejecting a same-name/different-path module.
Load the18 Python files in the SOURCE_PINS order; V25/V26 loaders import actual V19
classes, so rebuilding lookalike dataclasses or loading a second class is invalid.
Use actual V11 paths, actual V19 Typed/Table, V25 named/raw/typed interpreters,
V26 Functor/restriction/resource operations and V9 attained decoder.
Three historical ledger validators read the five source-ledger files also pinned.
No runtime V27 core import is needed: parent translations are ledger/proof scope,
not another fabricated common seven-parent executable interface.
All new public containers exact tuples; int excludes bool; no float aliases.
Validate every element/descendant before returning semantic None.
ValueError means malformed input/premise failure; valid raw failure is None.

## 2. Proposed core/presentation API

core_v29 exports cached paths, partial, categories, syntax, trees,
presentations, information, named, functors, restrictions, resources, semantic,
survivor_audit, optional_audit, parent_audit. Reuse actual classes unchanged.
GeneratorMap(graph, target, generator_arrows) frozen:
graph=(n,tuple(src,dst)), target actual lawful Typed on exactly n objects,
generator_arrows one strict target-arrow index per generator, matching endpoints.
It assumes neither generation nor invertibility. Parallel/cyclic edges permitted.
evaluate_path(mapping,path)->bundled target response, actual V11 path validation
then V19 identities/composition; full structural/typing checks. The V11 Python
interpret helper is finite-function-specific, not a generic Category interpreter.
A valid typed free path always has a successful target response.

dag_presentation(mapping)->DAGPresentation is explicitly DAG-only.
Use actual enumerate_dag then quotient_dag with equal ACTUAL target evaluations.
Class IDs follow first appearance in the parent path enumeration, not target IDs.
Expose paths, class_of (aligned tuple), representatives (first path per class),
category(actual Typed), lower(actual Functor), generates(bool), quote(Functor|None).
Lower object map=id and arrow map=actual evaluated representative arrow.
Generates iff its image contains every target arrow; quote only when it does.
No claimed inverse chooses a unique raw generating word.
evaluate_path remains valid on cyclic graphs; dag_presentation rejects cycles
because it cannot enumerate their complete path categories.
The generic Lean theorem covers arbitrary G; finite DAG enumeration is calibration.
Tests use actual functors.map_tree/map_response and actual trees.typed_eval/word
for lower/quote equations. No wrapper needs to assume those desired equations.

## 3. Proper injection/named API

NamedAdapter(category,ambient_size,arrow_labels,object_decoder) frozen:
arrow_labels injective local-arrow→ambient-index, not required sorted;
object_decoder is a permutation external-object-name→category-object.
Construct actual Presented using ascending image labels and a real subtype
reindexing of multiplication, then NamedPresented with the composed identities.
Expose .category,.named,.arrow_labels,.object_decoder,.ambient_to_local
(None outside image), plus explicit local/presented reindexing codecs.
named_response(adapter,tree)->None|ambient_arrow calls actual named_eval;
named_word_response likewise calls actual named_word.
typed_query(adapter,tree)->None|actual local tree validates the ENTIRE structure,
then substitutes present Arrow labels and external Empty names. None means
an absent Arrow leaf; it is not a successful default local arrow.
encode_bundle(adapter,response)->None|(external_src,external_dst,ambient_arrow)
checks the source bundle before converting BOTH endpoints and its arrow.
No new permutation-only adapter may accept the proper6→7 injection.
Restriction uses actual wide_restriction(category,A) and composes arrow_labels
with its actual inclusion arrow map; all external names remain unchanged.
The unrestricted ambient raw interface is not the domain of that inclusion.

## 4. Fully specified primary query sequence

Graph edge IDs a=0:(0,1),b=1:(1,2),c=2:(0,2), in that order.
Six target arrows lex endpoints: id0,a,c,id1,b,id2; composition chains endpoints.
ell=(0,1,3,4,5,6); q=(2,0,1); inverse object-name map=(1,2,0).
A=(0,1,3,5), restricted ambient labels=(0,1,4,6), local identities=(0,2,3).
Named identity encoder stays(6,0,4). Use this ordered82-query list for BOTH models.
Write A_i=Arrow(i), E_i=Empty(i), and S(x,y)=Seq(x,y).
Block1: A_0,...,A_6 (7).
Block2: E_0,E_1,E_2 (3).
Block3: S(A_i,A_j), i outer0..6,j inner0..6 (49).
Block4: S(E_i,E_j), i outer0..2,j inner0..2 (9).
Block5, in this exact order (12):
S(E1,A0),S(A0,E1),S(E1,A1),S(A1,E2),
S(E1,A3),S(A3,E0),S(E2,A4),S(A4,E2),
S(E2,A5),S(A5,E0),S(E0,A6),S(A6,E0).
Block6: S(S(A1,A5),E0),S(A1,S(A5,E0)) (2).
Indices in block5/6 are ambient Arrow/external Empty labels.

Independent expected responses use literal endpoint chaining, label availability
and tree recursion, never production quotient/table/interpreter helpers.
For each of164 queries compare named_eval AND named_word:328 parent evaluations.
Present-leaf schedule counts: full6+3+36+9+12+2=68;
restricted4+3+16+9+8=40; total108 typed comparisons,216 typed parent evaluations.
There are56 absent-leaf guard cases. Compare inclusion ONLY on the40 restricted
present-leaf queries, including failed joins; no Some-versus-None cheating.
The shared absent label2 and removed b/c have separate named controls.
Successful/failed response classifications are measured, not assumed by counts.

Also independently check all7 path evaluations and49 ordered path pairs against
actual path typing/composition; all36 quotient-arrow pairs against endpoint rules.
Record both lower/quote arrow inverses:6 each,12 comparisons.
The3-generator DAG quotient is not ownKernel(C.Hom), which has identity loops.

## 5. Fixed-interface response families

Family(model_count,query_count,output_count,responses) has a rectangular
tuple-of-tuples of None|strict output indices; all dimensions explicit, including0.
transport_report(source,target,query_map,output_map,codes) checks common model
domain, every unused target entry, i:Q→R total and j:A→B total; i may repeat.
It returns commutes,output_injective,source_recoverable,
restricted_target_recoverable,full_target_recoverable and exposed V9
observation codebooks/labels/attained decoders. Do not require j injectivity
just to construct the report: missing-premise negatives must remain expressible.
The theorem conclusion is claimed only if commutes AND output_injective.
Code labels are strict Nat, one per model; no arbitrary off-image decoder.
Output map preserves None; restricted target is q↦target(m,i(q)).

Small registered family calibration:
F1 all81 two-model/two-query arrays over(None,0,1), row-major lex order;
i=(0,1),j=(1,0); target obtained by literal Option mapping.
For each family codes=(0,0) then(0,1):162 report cases.
F2 enumerate9 seed arrays with two models and ONE query over(None,0,1).
Construct source with TWO equal queries per model by duplicating its seed entry;
construct target with ONE query by applying j=(1,0) to that seed entry.
Thus i=(0,0):Q={0,1}→R={0}. Same two code arrays:18 cases.
Total90 families/180 reports/360 source-versus-restricted recovery decisions.
Independent oracle enumerates functions on attained observation signatures.
Track full-target decisions separately if evaluated (180), not folded into360.
No arbitrary predicate search, random sampling or enlarged profile population.

Named information cases, separate from those counts:
varying j_m(b)=xor(b,m) gives two valid single-model squares but no fixed j;
source m versus constant target0 is a recovery collision under constant codes.
Retaining the actual two-entry j_m codebook revives recovery.
Noninjective j=(0,0) preserves squares but destroys response distinctions.
Omitted target query: source0,target(m)=(0,m),i=(0),fixed identity j;
restricted target is recoverable, full target is not.
Empty model domain, empty query domain, zero-output all-None family each pass.

## 6. Additional named premises and hostile inventory

Presentation: omit generator b (lower faithful but not onto); add reversed target
arrow labels as a separate named control to catch lower=identity assumptions.
Cyclic one-loop graph allows evaluate_path but forbids full DAG enumeration;
empty graph/category gives empty finite presentation and legitimate empty image.
Wrong generator endpoint, bool arrow, unused out-of-range generator and graph
dimension mismatch reject before interpretation; wrong quotient c/ab split,
cross-Hom merge, representative/evaluation substitution reject semantic checks.

Named: swapped identities fail fixed Empty0; inverse query permutation repairs.
Remove an identity or admit a,b without c; wrong restricted local identities.
Nonunit raw Empty rejects; ambient Arrow2 fails; excluded b/c may be full successes.
Malformed leaf/opcode/arity/container, noninjective label injection, bool aliases,
wrong inverse codec, wrong decoder dimension and malformed later descendant reject.
Corrupt P/table/order-of-labels/identity/endpoint/None tag independently;
accept each original output before coherently mutating its certificate.

Functor/resource: reuse lawful object-collapse-with-faithfulness and nonfaithful
one-object C2 collapse; tagged objects repair failure reflection, not lost arrows.
Actual ResourceLift on the chain costs(0,1,2,0,1,0),max_balance2:
a at balance2 followed by b at balance2 fails the resource join; forgetting joins.
Same path a;b lifted from2 succeeds with residual0 and its exact base path.
These are named controls, not a new resource population.

## 7. Ledger, custody, test inventory and costs

Freshly validate unchanged six survivor/six optional/seven parent ledgers.
ORIGINAL_CROSSWALK_V29.json is one of the five preregistration files;
SOURCE_PINS_V29.freeze_companions binds its exact bytes.
It fixes eight literal original result texts and all ten atom records; preserve
prior R1 scope verbatim in its historical reconciliation.
Mutate missing/duplicate/reordered rows, source/observer/codec/premise swaps,
empty/non-string fields, omission of imported controls and coupled source hashes.
Schema guards cannot certify prose truth or collapse distinct parent meanings.

Register13 unittest methods/9 modules: presentation2,named2,information2,
controls1,hostiles1,rollup-ledger1,custody2,coverage1,root kernel-guard1.
Root kernel guard has4 source-valid mutants (all-empty plus three reviewed leaves).
Counters above are fixed schedule arithmetic; named/malformed/semantic/custody
rejection totals are measured from the explicit frozen test-case inventory.
Record imported source count/bytes, exact replay and oracle/adapter times,
all naming/codebook costs; deterministic receipts exclude variable wall times.
No minimum storage/runtime claim follows from observer information equivalence.
Only R1 round scope/status may change under its reviewed explicit contract;
atom accounting remains35/187/2/185; other statuses and V16 authority stay fixed.
