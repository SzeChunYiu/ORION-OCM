# OCM implementation-facing foundation and G2 evidence audit

Status: **bounded formal refinement and retained-receipt reconciliation**, not programme completion.

Repository: `SzeChunYiu/ORION-OCM`. Governing roadmap: #165. Reviewed implementation: `6ebbc4e0efed7cc9d089c206c24a3040e1aa279f`, the final head of #191. This package is an additive follow-up on the same existing research branch. It does not alter the frozen learner, acquisition populations, utility rule, production runtime, or historical receipts.

## 1. What has actually been established

The standalone checker reconstructs the frozen mathematical populations, distinct-task fragment support, all candidate validation costs, selection/rejection, exact first winning programs and their stream origins, four complete test arms, and the search-slot investment ledger. It does not import OCM or trust the receipt's aggregates. It uses integer symmetric convolution and quotient-state breadth-first construction rather than production's rational ordered-pair convolution and exhaustive word population.

The retained #191 artifact is bound by:

```text
workflow run      34279565415
artifact          10077172191
artifact SHA-256  250a9635efdae95ebc6737842e3423763c6800ab2db7b7771de971a83153f639
result SHA-256    ca549bab3e0de0b2aacb1313020805709e09eee2d416175907c665a9b31dad31
methods.py blob   50323a33418b8ef8bb6500ddeba4b9d1f795e9e3
```

Local reconciliation returned `EXACT_G2_RECEIPT_RECONCILED`. The original scientific outcome remains:

```text
UTILITY_TOURNAMENT_SELECTS_NO_METHOD
NO_LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_LENGTH7_TESTS
```

| Retained measurement | Exact search slots |
|---|---:|
| Training, 48 tasks | 44,699 |
| Primitive validation, 32 tasks | 122,787 |
| Best candidate validation: `double, square` | 184,965 |
| All 16 candidate validation runs | 3,427,047 |
| Primitive test, 64 tasks | 903,871 |
| Each of ordinary, OCM and revoked test arms | 903,871 |
| Training + full tournament + OCM test | 4,498,404 |

All 16 candidates fail the registered aggregate utility criterion. No selected method is deployed. Consequently the equal test arms are a **no-deployment control**, not positive evidence for learned-method consumption or operational revocation. The study does not prove that every library-learning mechanism fails.

The original admission error was repaired upstream by `experiment_runner.py`; that repair is not a contribution of this audit. The upstream wrapper is preserved.

## 2. Review coverage and provenance

Three analytical perspectives are applied here: formal semantics/refinement, learning and evaluation design, and runtime/resource reliability. These are roles within a single-assistant review, not separately staffed experts or independent external replication. Each proposition below has an implementation consequence and a stated boundary. Mathematical reimplementation independence must not be confused with independent authorship, independent benchmark construction, or observation of the original execution.

Primary research reviewed for the donor and evaluation boundaries appears in section 12. Repository claims are bound to #165, #189, #191 and the source paths below. The package introduces no claim of OCM-specific algorithmic novelty.

## 3. The machine contract stays fixed

Use the roadmap's canonical machine:

```text
M_t = (F_t, O_t, Pi_t, C)
proposal_t = o_t(F_t, O_t, Pi_t, environment_t)
(F_{t+1}, O_{t+1}, Pi_{t+1}) = Admit_C(proposal_t)
```

`F` holds persistent epistemic state, `O` holds primitive/imported/learned/composed operators, `Pi` selects permitted work, and `C` is the externally governed check/authority/meter/commit constitution. A learned procedure is data in `F/O`, not permission to modify `C` or inject an unmetered domain-specific rule into `Pi`.

A method's record needs four separately checkable claims:

| Claim | Required evidence | What it does not imply |
|---|---|---|
| Correctness | A checked relation between executable and task/specification | Utility or authorization |
| Acquisition lineage | Source tasks, candidate construction and donor identity | Novelty or held-out performance |
| Utility | A registered comparison on a declared task set and resource coordinate | Universal or lifetime benefit |
| Current authorization | Live support, scope, authority and constitution at invocation | Historical correctness becoming false when authority is withdrawn |

**Conditional preservation theorem.** Suppose the initial state satisfies invariant `I`, and every admitted transition is checked by `C` against a specification that implies `I(s) -> I(s')`. Then every finite admitted execution preserves `I`, by induction on transitions. This is an implementation obligation, not a proof that the current entire OCM runtime has been verified: the hard work is establishing sound admission checks and the refinement of every actual transition, including replay, caches, exceptions and cleanup. A file hash or a green unit suite alone cannot discharge that premise.

Implementation bindings: `src/ocm/kso/admission.py`, `src/ocm/runtime/ocm_runtime.py`, `src/ocm/learning/methods.py`. This package changes none of them.

## 4. Exact identity, semantic quotient and scope

The registered grammar starts from `x` and applies `inc`, `dec`, `double`, or `square`. Every finite word denotes a polynomial with integer coefficients, hence also a rational polynomial. Let `N(p)` be its trimmed coefficient vector.

**Proposition 1: normal-form soundness and completeness at this scope.** For words in this grammar, `N(p) = N(q)` exactly when they denote the same polynomial function on the rationals. Soundness follows by induction on each operation's coefficient transformation. Completeness follows because a nonzero polynomial over a field cannot vanish on infinitely many rational inputs. This statement concerns coefficient vectors; their SHA-256 identifiers additionally depend on the usual collision-resistance assumption and canonical serialization.

The audit uses symmetric convolution:

```text
q[2i] += a[i]^2
q[i+j] += 2*a[i]*a[j]    for i < j
```

Production uses all ordered pairs with `Fraction`. Both represent the same polynomial product. Differential controls compare them on every word of length at most three. Separate controls compare direct rational execution at sufficiently many points for those bounded polynomials. These controls support the refinement argument; they are not a proof assistant certificate for arbitrary Python executions.

**Proposition 2: shortest semantic length survives quotienting.** The next polynomial is a deterministic function of the current coefficient vector and the next primitive. Therefore a shortest path in the quotient graph of coefficient vectors has the same length as the shortest primitive word realizing that vector. Breadth-first expansion, retaining each vector's first discovery, computes exact minimum lengths. Any longer path to the same vector can be replaced by the shorter path before an identical suffix.

This justifies independently reconstructing #191's length-5/6/7 strata without mining solver performance. A control compares the quotient result against complete syntactic enumeration through length seven. The same mathematical task under a different label is not held out. Likewise `inc, dec` is an identity alias, not a novel operation. Compression and genuinely new semantic functionality must remain separate.

## 5. Exact search-slot refinement

Freeze a legal library `L`, maximum primitive length `d`, budget `B`, and the registered `alternate-baseline.v1` schedule. Primitive words are generated in increasing length and fixed primitive order. Guided token words use `L` followed by singleton primitives; flattening occurs before the length check. Odd slots use the guided stream while it exists; even slots use the primitive stream. Duplicate and overlength emissions consume slots.

For a task `q`, define `r_L(q)` as the slot of the first admissible emitted word with `N(p)=q`.

**Proposition 3: first-hit rank equals the production solution slot.** Assume exact arithmetic, unchanged enumeration and budget, no exceptional termination, and sound target-specific counterexample checks. A correct identity agrees at every counterexample point and therefore cannot be discarded by that filter. A wrong identity cannot pass the final coefficient equality. Repeated identical words cannot suppress the first correct word: if it had appeared earlier it would already have solved the task. Thus production stops on exactly the first admissible identity and at exactly `r_L(q)`.

This permits one independently reconstructed stream to check many task ranks. It also checks whether the first successful word came from the guided or primitive stream. It does **not** equate counterexample histories, candidate-check counts, CPU time, memory, or execution trace custody. The auditor's own caching is a checking implementation choice, not a free optimization credited to the original experiment.

**Proposition 4: fair fallback gives a slot bound, not a speedup guarantee.** If a primitive solution first occurs at rank `r`, the alternating solver finds a solution by slot `2r`, provided the budget reaches `2r`. Either the same word occurs earlier in the guided stream, or the primitive stream supplies it by its `r`-th opportunity. Earlier guided exhaustion only increases primitive opportunities. A finite budget below this bound need not preserve success.

The guarantee is restricted to emitted slots. A very expensive guided expansion or arithmetic operation can dominate wall time. It does not establish utility, and it explains why a bad library can harm many tasks while retaining eventual completeness in the bounded grammar. `BUDGET_EXHAUSTED` is scoped failure, not task impossibility outside the searched grammar or budget.

Executable bindings: `coefficients`, `first_hits`, `check_rows`, `test_production_refinement.py`.

## 6. Complete comparison is a proof obligation

The frozen experiment's `exact_rows_equal` uses `all(... for ... in zip(a,b))`. That checks only a common prefix; an empty second arm passes. The retained receipt is complete, so this defect does not change its negative result, but the predicate cannot certify coverage generally.

**Proposition 5: paired equality needs domain equality.** Given a fixed nonempty ordered task universe `Q`, first require both arms to contain exactly `Q`, once each. Only then does pointwise equality establish equality of the full result functions on `Q`. Equal lengths alone are insufficient when rows are duplicated or substituted.

The audit's `paired_equal` and `check_rows` reject empty, truncated, duplicated, reordered and substituted coverage. They also reject Boolean slot counts, malformed programs, forged costs, false stream origins, and correct-but-not-first solutions. Canonical JSON comparison distinguishes `true` from `1`; duplicate JSON keys and nonfinite numeric values are refused. Failed reconciliation exits with `CANNOT_CHECK_G2_RECEIPT`, never a scientific success or a fabricated negative experiment.

This is a sidecar qualification of the frozen experiment. Its historical source is not silently rewritten. Consumers needing qualified results must require the audit terminal as well as the original result file.

## 7. Evidence algebra and revocation

For an exact support family `W`, interpret each member `S` as a conjunction of required evidence, and the family as alternatives:

```text
live(W, R) iff there exists S in W with S intersect R empty
join(W1,W2) = minimal(W1 union W2)
meet(W1,W2) = minimal({S1 union S2 : S1 in W1, S2 in W2})
```

`minimal` removes redundant supersets. With this interpretation, withdrawing one premise disables a conjunction but does not destroy an independent surviving alternative. For example, `{{a},{b}}` remains live after withdrawing `a`, whereas `{{a,b}}` does not. Uncertain lower/upper support bounds must not be collapsed to an exact family; absence of established live support is not necessarily established impossibility.

**Proposition 6: exact revocation is support evaluation, not historical erasure.** For fixed `W`, evaluating the expression above after adding revoked evidence yields precisely the surviving derivations. Historical receipt identity and acquired method bytes can remain unchanged while permission to use the method changes. The proof is direct substitution into the disjunction of conjunctions.

For composed methods, scope must narrow to the intersection of premise/operator scopes, and authority cannot exceed the permissions of the premises and external adoption rule. These are additional conditions; a syntactically correct support edge alone cannot grant authority.

This package describes the contract and validates declared metadata identities only. It does **not** execute all runtime revocation cases or certify the whole warrant implementation. The #191 wrapper's support connectivity fix is retained. Its same-interpreter `OCMRuntime(root)` reconstruction is not evidence of a fresh operating-system process.

## 8. Learning, selection and causal claims

A registered candidate tournament is finite optimization, not a population theorem. With validation costs `c_j(q)` and baseline `c_0(q)`, #191 chooses the fixed-tie-break minimizer of `sum_validation c_j(q)` and deploys only on strict aggregate improvement. All candidates' evaluation costs belong in the selection ledger, including rejected candidates.

The proof that this gate enforces improvement on the measured validation set is immediate from its comparison. It implies nothing about a different task distribution. Candidate construction, validation selection and final testing must remain distinct. Model-selection overfitting is a known evaluation failure mode [R3]. Deterministic hash-ranked, disjoint length strata exclude identity overlap but do not by themselves create independent identically distributed samples or population confidence guarantees.

A positive causal-use argument additionally needs an admitted-before-test method, actual invocation of its bound identity, exact task correctness, a registered effect, and a matched removal/withdrawal intervention. Ordinary-parent transplantation separates useful learned content from architectural benefit. If ordinary and OCM have the same task-by-task slot counts, their residual on **that coordinate at that scope** is zero, even when both improve over the primitive solver. Costs or constitutional behavior may still differ and need their own measurements.

In the actual #191 result, no method is deployed. Therefore neither method consumption nor nontrivial revocation is exercised in the test population. Calling the no-method arm 'revoked' must not turn that label into evidence that withdrawal caused a performance change.

## 9. Runtime restart and independent observation

Re-instantiating `OCMRuntime` in the current interpreter can test deserialization and reconstructed-state behavior. It cannot establish that module globals, inherited objects, caches, or monkeypatches were absent. A cold-process claim requires a separate interpreter, explicit persisted-input manifest, executable/source identity, start/exit evidence, and independently checked output. The live and withdrawn arms must differ only in the registered intervention, not unrelated task order, seeds, hidden state, or budget.

A successor should persist the admitted library, terminate the acquisition process, invoke a fresh consumer process using only declared persisted inputs, and record invocation-time authority checks. Withdrawal should be applied through the same runtime path, followed by another fresh consumer. Those receipts would qualify a process-restart claim. This package does not manufacture them, and does not retrofit such a claim onto #191.

## 10. Lifetime economics and minimum sufficient cognition

For resource coordinate `k` and task sequence `Q`, define:

```text
Delta_k(Q) = parent_total_k(Q) - ocm_total_k(Q)
ocm_total = acquisition + validation/selection + build + maintenance
            + retrieval/execution/checking + persistence/replay
            + invalidation/revision + cleanup
```

The comparator must solve the same registered demand at matched capability. State whether acquisition tasks are paid work common to both arms or an extra investment made only by the learning arm; this changes the counterfactual ledger. Do not silently mix those designs.

For a fixed setup cost `K` and constant per-task saving `s>0`, strict payback occurs exactly when `H*s>K`. With varying savings, replace that expression by the measured sum. With reset/invalidation epochs, account for each epoch's rebuild and maintenance. Reuse after invalidation cannot be counted as free continuation of the previous investment. Resource vectors should remain vectors unless prices and constraints were registered before outcomes.

#191 explicitly measures search slots only. Its ledger charges training, baseline validation, all candidate validation, and the OCM test path. That arithmetic is reconciled here. It is not a complete physical-resource ledger or a matched whole-programme lifetime theorem. Since no method is deployed, there is no observed per-task saving to amortize; a projected positive horizon cannot be inferred from this result.

Minimum sufficient cognition consequently has a concrete implementation reading: do not pay for a learned selector, larger library, extra inference or persistent structure when a registered exact parent already suffices and there is no payable residual. This is a decision rule under stated costs, not a claim that learned routing is never useful. #71 remains unauthorized by this package.

## 11. Programme gap disposition and next executable boundary

| Gate | What this work settles | What still requires evidence |
|---|---|---|
| G1: minimum vessel | Keeps `(F,O,Pi,C)` unchanged; identifies concrete refinement obligations | Minimality under subtraction/compensation, controller growth, integration of invariant checks |
| G2: causal acquisition | Independently reconciles the complete #191 negative; closes prefix-coverage qualification in the audit path | A useful constructed abstraction, actual consumption after cold restart, nontrivial withdrawal and strongest-parent comparison |
| G3: composition/failure/representation | States scoped failure and composition contracts | Fresh A+B tasks with both-ID ablations; failure generalization without blacklists; representation interventions |
| G4: lifetime economics | Exact finite search-slot ledger and explicit payback conditions | Paid physical resources, drift/reset epochs, capability-matched lifecycle comparisons |
| G5: governed development | Preserves external authority and historical identity requirements | Earned self-change, scalable persistent updates, safe consolidation and revision |
| G6: cross-domain development | No cross-domain inference from polynomial identity | Persistent heterogeneous raw traces and earned transfer/self-change |
| G7: integrated strongest-parent comparison | Separates shared learned content from architectural residual | Integrated machine, equal priors/tools/demand, fully charged comparisons |
| G8: replication/proof of function | Adds independently implemented mathematical checking | Independently authored families, external assessment and protected replication |

The next G2 mechanism must be materially different from selecting one of these exposed fixed fragments. A faithful abstraction constructor with arguments, such as a Stitch-style donor, is a concrete parent to implement and test. Its learned abstractions must actually enter a correct consumer; compression without executable consumption is not G2 closure. A new prospective protocol must freeze its mechanism, abstraction language, donor version, costs, population construction, utility rule, comparator parity and negative terminals before evaluating a new final population. Re-running or relabeling #191 is not new evidence.

A representation/consumer change may be the appropriate response rather than a router. This is a research direction supported by the limits of the tested candidate class, not a demonstrated positive successor and not permission to tune to #191's exposed test outcomes.

## 12. Primary literature and concrete adoption decisions

| Primary source | Implementation implication | Decision/boundary here |
|---|---|---|
| [R1] Bowers et al., *Top-Down Synthesis for Library Learning*, PACMPL/POPL 2023, DOI 10.1145/3571234; arXiv:2211.16605v2 | Corpus-guided abstraction construction with a declared utility objective is a stronger donor than recurring fixed substrings | OPEN donor implementation; compression quality is not automatically downstream search utility |
| [R2] Ellis et al., *DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep Bayesian program learning*, arXiv:2006.08381 | Separate learned library structure from search guidance; test transfer to new tasks | Comparator/design reference; its neural guidance is not imported or authorized here |
| [R3] Cawley and Talbot, *On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation*, JMLR 11 (2010), 2079-2107 | Selection data cannot also serve as unbiased final evaluation | ADOPT separate construction/selection/test accounting; no unsupported confidence claim |
| [R4] Howard et al., *Time-uniform, nonparametric, nonasymptotic confidence sequences*, Annals of Statistics 2021; arXiv:1810.08240 | Repeated monitoring needs a guarantee valid under its sampling/stopping assumptions | OPEN for future stochastic protocols; not applicable merely because hashes produce an ordering |
| [R5] Willsey et al., *egg: Fast and Extensible Equality Saturation*, arXiv:2004.03082 | Explicit congruence and rebuilding are conventional parents for equivalence organization | OPEN comparator; no need to relabel equality saturation as OCM novelty |
| [R6] Zhang et al., *Better Together: Unifying Datalog and Equality Saturation*, arXiv:2304.04332 | Incremental relational inference and equality reasoning provide a strong field/index parent | OPEN comparator; provenance, scope and authority still require explicit contracts |

Source locators: R1 `https://arxiv.org/html/2211.16605v2`; R2 `https://arxiv.org/abs/2006.08381`; R3 `https://jmlr.org/papers/v11/cawley10a.html`; R4 `https://arxiv.org/abs/1810.08240`; R5 `https://arxiv.org/abs/2004.03082`; R6 `https://arxiv.org/abs/2304.04332`.

## 13. Reproduction and trust boundary

Standalone authored controls, from this directory:

```sh
python -B -m unittest -v test_audit_g2
python -B -O -m unittest -v test_audit_g2
python -B audit_g2.py /path/to/retained/result.json --out /new/path/audit.json
```

From a real repository checkout, also run the source-pinned production differential controls:

```sh
PYTHONPATH=src:research/ocm-foundation-audit-v1 \
  python -B -m unittest discover -s research/ocm-foundation-audit-v1 -p 'test_*.py' -v
```

The workflow downloads the exact historical artifact, checks both archive and result hashes, runs normal/optimized controls, and reconciles the retained receipt. It does not rerun the protected study. Artifact expiration or changed bytes must fail closed; obtain a byte-identical archived copy rather than silently substituting a new experiment.

Local execution passed 42 authored controls normally and 42 with `-O`, and reconciled the retained receipt. Local production differential tests were not run because no repository checkout was available; their actual hosted outcome must be read from CI, not inferred from their presence. `EVIDENCE.json` is a record of that local scope, not a claim about later hosted runs.

The checker proves no physical custody, general intelligence, universal efficiency, full runtime correctness, or programme closure. Its result deliberately contains `programme_closure: false`. Finishing those obligations requires the concrete gate evidence above, rather than promoting a negative study or an engineering test suite into a completed scientific programme.
