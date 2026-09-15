# Banned paper terms — v1 (issue #833, section AB)

Inside-consistent but academically misleading terms that must not appear in paper-facing prose
(flagship documents, manuscripts, external claims). Each entry: legacy/internal term, why it misleads,
the sanctioned replacement(s), and the migration rule. The CI gate
`GMI_TERMINOLOGY_CI_GATE_V1.py` enforces the machine-checkable subset.

## Banned list

| banned term | why it misleads | sanctioned replacement(s) | migration rule |
|---|---|---|---|
| bare **prior-free** (before a noun) | implies no assumptions at all; provably ill-posed as a literal claim (no-free-lunch, bias-necessity) | architecture-agnostic; architecture-uncommitted; family-agnostic search; `architecture-prior-free` only with an explicit residual-prior ledger | QUALIFY: never bare; always carry the residual-prior scope (ledger L) |
| **obligation** (paper-facing) | carries a deontic/legal connotation absent from the scientific object; v1 defines it as a claim-governance tuple, not a behavior | task; behavioral specification; formal specification; requirement | PAPER-RENAME: pick per exact semantics; formal-methods contexts use "formal specification" |
| bare **morphology** (where architecture/model-class fits) | biologically loaded; masks whether "structure across heterogeneous computational organizations" is actually meant | architecture; computational architecture; model class; representation; algorithm; computational mechanism | QUALIFY: keep only where cross-organization structural claims are intended |
| **machine species** (informal) | biological species analogy smuggles speciation semantics not defined anywhere | model family; architecture family; behavioral phenotype; equivalence class | PAPER-RENAME: define the equivalence relation first |
| **ecology** / **niche** (informal) | borrows ecological theory without a defined population/selection process | task distribution; environment; instance space; operating regime; region of instance space; domain of competence | PAPER-RENAME (context table) |
| bare **selection** | conflates five distinct academic selection problems | algorithm selection; model selection; architecture search; configuration/hyperparameter selection; evolutionary selection | QUALIFY: state which of the five |
| **phase law / phase diagram** without control space | implies measured phase-transition physics; overclaims absent a control-parameter space and a qualitative regime change | regime map; crossover map; phase diagram (only with control space + measured transition) | QUALIFY: show control parameter and transition, else regime map |
| **hypothesis space** / **possibility space** (vague) | unmeasured; masks that what matters is the class of candidate hypotheses | hypothesis class; search space; program space | RENAME |
| **DSL / grammar** (unqualified) | hides that DSL choice itself induces strong bias; grammar implies specific expressiveness | DSL/grammar (always say the primitive set and state DSL-induced bias); syntax-guided synthesis | RENAME + bias statement |
| **neutral search** | no search is neutral; hides the actual procedure | family-blind enumerative search; architecture-agnostic search; grammar-based synthesis; evolutionary search | PAPER-RENAME: name the procedure |
| **remint** | internal-process metaphor; reviewer cannot tell what was redone | independent regeneration; re-randomization; relabeling control; fresh-instance replication; independent replication | PAPER-RENAME: say exactly the variant |
| **negative twin** | evocative but undefined for readers | matched negative control; counterfactual control; ablation; placebo condition; negative control | PAPER-RENAME: say which |
| **parent subtraction** | obscure metaphor | comparison to strongest baselines/parents; subsumption analysis; reduction; ablation; novelty analysis | PAPER-RENAME: say which |
| **carrier** (paper-facing) | unrepresentational, substrate-vague | state representation; state space; memory substrate; computational substrate; representation space | PAPER-RENAME: map to a representational object |
| bare **discover** | implies unencoded/privileged-free generation with no evidence | discovery (with non-privilege evidence + strongest-parent reduction) | QUALIFY: state non-privilege and parent reduction |
| loose **derive** | overclaims logical necessity for heuristic/empirical results | recover; select; fit; construct; reproduce; explain | RENAME: reserve "derive" for valid consequences of stated premises |
| backdated **predict** | claims prediction after seeing the outcome | reconstruction; post-hoc explanation | RENAME: require temporal/epistemic separation |
| **proof** for a finite enumeration | exhaustive finite computation is a reconstruction, not a universal proof | reconstruction; certified finite check | RENAME: state certificate/computer-assisted status |
| **novel intelligence** / **unseen form** (bare labels) | unquantified novelty level; reviewer cannot tell the level | novelty ladder level (implementation → architecture → mechanism → model class → paradigm → capability profile) + held-out/predicted/mechanism/class specifier | QUALIFY: state ladder level and object |
| **open-ended** used for a large search space | conflates bigness with open-endedness; the term is already a technical one in ALife | open-ended evolution (with OEE-literature tie-in); bounded search with large coverage | QUALIFY: tie to OEE literature |
| **evolution** without a population/selection process | biology terms (population, variation, heritability, selection) must each be defined | evolution (define population/variation/heritability/selection explicitly first) | DEFINE |
| **cognition** terms (paper-facing) | claims correspondence to human/animal constructs without operational criteria | working memory; episodic/semantic/procedural memory; attention; metacognition; theory of mind (each with operational criteria) | DEFINE + operational criteria |
| bare **causal** | correlation/reconstruction masquerading as causal claims | causal (with SCM/intervention/counterfactual semantics) | QUALIFY: adopt SCM discipline |
| bare **uncertainty** | mixes aleatoric and epistemic senses | aleatoric uncertainty; epistemic uncertainty; confidence set; credible set; calibrated prediction; identifiability; partial identification | RENAME: name the construct |
| **verify / verified** (bare) | conflates formal verification, empirical validation, evaluation, testing, certification | formal verification; empirical validation; evaluation; testing; certification; verifier feedback | QUALIFY: say which |
| **proof** of computer-assisted steps without certificate | understates the checker semantics | computer-assisted proof with certificate (state checker, e.g. Coq/Lean/Isabelle) | RENAME: state certificate |

## Machine-checkable subset (enforced by the CI gate)

The gate scans for these patterns with optional case-insensitivity and word boundaries:

- `prior-free` (bare, for paper-facing targets, when the __context__ argument is not a res-prior ledger)
- `obligation` (paper-facing prose contexts: md docs, manuscript dirs, PR-facing summaries)
- recommend/maybe also `naturalness`? — no, this is out of scope for AB
- The gate is extensible via a JSON/TOML term list.

## Migration rule table (machine-parseable duplicate of the crosswalk migration block)

| legacy | banned-in | replacement |
|---|---|---|
| obligation | paper-facing prose | task / behavioral specification / formal specification / requirement |
| prior-free (bare) | paper-facing prose | architecture-agnostic / architecture-uncommitted / architecture-prior-free+ledger |
| morphology | where architecture/model class fits | architecture / model class / representation / mechanism |
| machine species | informal | model family / architecture family / equivalence class |
| ecology | informal | task distribution / environment / operating regime |
| niche | informal | region of instance space / operating regime / domain of competence |
| selection | bare | algorithm/model/architecture/configuration/evolutionary selection |
| phase law | without control space | regime map / crossover map |
| neutral search | paper-facing | family-blind enumerative / grammar-based synthesis / evolutionary search |
| remint | paper-facing | independent regeneration / relabeling control / independent replication |
| negative twin | paper-facing | matched negative control / ablation / negative control |
| parent subtraction | paper-facing | subsumption analysis / ablation / novelty analysis |
| carrier | paper-facing | state representation / state space / substrate / representation space |
| discover | bare | discovery with non-privilege + parent-reduction evidence |
| derive | loose | recover / select / fit / construct / reproduce / explain |
| predict | backdated | reconstruction / post-hoc explanation |
| proof-by-enumeration | as "proof" | reconstruction / certified finite check |
| open-ended | as bigness | open-ended evolution (OEE sense) |

Version note: this list is a living authority artifact. Updates to the canonical list require a
crosswalk row + a test fixture + a gate-rule change together (see test_ab_ac.py and the gate script).
