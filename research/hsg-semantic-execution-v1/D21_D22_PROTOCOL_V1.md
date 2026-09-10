# D21 + D22 execution protocol V1 (frozen before result-generating code)

Scope: issue #233 HSG v4 lanes **D21** (reduction + equality saturation) and **D22**
(heterogeneous-logic transport). The `EXPERIMENT_REGISTRY_V1.json` rows `D21`/`D22`
and the `HOSTILE_REGISTRY_V1.json` rows `H-T74a` / `H-T85a` / `H-T86a` / `H-T86b`
are already frozen and are **not modified**. This document pins only the operational
detail those rows leave open: arms, evaluation domains, cost model, exact hostile
witnesses, no-alarm controls, endpoints and falsifiers.

Frozen worlds are reused verbatim from `exact/worlds.py` (`SEED = 20260910`):
`ow6_worlds()` (10 expression worlds, depth 2-4), `ow7_worlds()` (6 finite-logic
worlds), `expr_eval`, `REWRITE_NAMES`, `rewrite_apply`. Generators are **not edited**.

## 0. Reuse audit (billy-old, python 3.14.4)

| candidate | installs | decision |
|---|---|---|
| `egglog` 13.2.0 (Rust egraphs-good bindings) | yes | **REUSE** as the mature equality-saturation arm and independent cross-check |
| `sympy` 1.14.0 | yes | **REUSE** as the second, independent semantics oracle (polynomial normal form) |
| `snake-egg` | no (no cp314 wheel, build fails) | rejected |
| `egg-python` | no such distribution | rejected |
| `pyegg` 1.0 | yes, but unrelated to e-graphs | rejected |
| `z3-solver` 5.1.0.0 | yes | **deliberately NOT used**: N4_formal_proof is LOCKED, D22 is finite-exhaustive-first |
| `python-sat`, `pysmt` | yes | **deliberately NOT used**: same N4 lock |
| `lark` | yes | not needed, frozen ASTs are already structured |

`egglog.EGraph` exposes `run`/`saturate`/`check_eq`/`extract`/`extract_multiple`.
It does **not** expose exhaustive e-class membership enumeration. T86 is stated as an
**e-class invariant** ("every expression in an e-class remains semantically equivalent
to the seed"), and `WORLDS_V1["OW6"].justify` requires that "e-class members can each be
ground-truth evaluated". Extraction alone tests only the corollary. Therefore the
**project-specific residual** is a minimal hash-consed e-graph with union-find plus
congruence closure whose e-classes can be walked exhaustively on tiny worlds; `egglog`
runs as an independent second implementation and every equivalence decision is
cross-checked against it. Build-vs-reuse is recorded per component, not per lane.

## 1. D21 — reduction + equality-saturation worlds

### 1.1 Registered semantics and the two independent oracles

A term is a frozen-alphabet AST over `{2,3,5,x}` with `+`,`*`, extended on the *output*
side with non-negative integer literals (needed by constant folding). Registered
semantics is the integer polynomial function `x |-> value`.

* **O1 point oracle** — exhaustive evaluation over `X = 0..20` (21 points). Frozen
  worlds have depth <= 4, so degree <= 2^4 = 16; 21 > 16 points separate any two
  distinct polynomials of that degree, so O1 is exact on this family, not a sample.
* **O2 symbolic oracle** — `sympy.expand` normal form over `Z[x]` (independent library).

`sem_equal(a,b) := O1(a,b) and O2(a,b)`. If O1 and O2 disagree the result is
`CANNOT_CHECK` with its own exit status; it is never reported as "checked and fine".

**Conformance control (must pass):** on every frozen world and every point of `X`, the
D21 evaluator must equal the frozen `worlds.expr_eval`. A failure here invalidates the
lane rather than the arm.

### 1.2 Rewrite sets

* `SOUND_FROZEN = REWRITE_NAMES = {comm+, comm*, assoc+}` — frozen, cost-preserving.
* `SOUND_EXT = {fold, factor}` — registered here, before any run, because the frozen
  set is purely permutative and would make the optimisation task vacuous (every
  reachable term has identical node count). `fold` evaluates a constant-only binary
  node; `factor` rewrites `(a*b)+(a*c) -> a*(b+c)`. Both are semantics-preserving and
  strictly node-count-non-increasing, so saturation still terminates.
* `UNSOUND = {unsound_swap}` — the frozen planted rewrite `(+ l r) -> (* l r)`
  (`rewrite_apply`, tagged H-T86a). **Exactly one** unsound rule, hostile arms only.

### 1.3 Arms

`direct_solve`, `one_shot_rewrite`, `ordered_rewriting`, `knuth_bendix`,
`equality_saturation` (self-built, exhaustive e-class walk), `egglog_saturation`
(mature engine cross-check), `learned_library`.

`knuth_bendix` is expected to report `FAILS_TO_ORIENT` on the permutative axioms
`comm+`/`comm*`: no reduction order orients commutativity. That is the honest reading
of "Knuth-Bendix where applicable"; `ordered_rewriting` under a total ground order is
the applicable substitute and is run as such.

### 1.4 Tasks

* **TASK-EQ** — 10 worlds x (4 sound-rewrite random walks of length 1/2/4/8 giving
  TRUE pairs + 4 single-leaf constant perturbations giving expected-FALSE pairs) = 80
  pairs. Ground truth is `sem_equal`, so a perturbation that happens to be equivalent
  is reclassified by ground truth, never discarded.
* **TASK-OPT** — minimum node-count member of the rewrite-reachable class, tie-broken
  by canonical string. Reference optimum is the exhaustive closure under
  `SOUND_FROZEN + SOUND_EXT` (BFS, capped at 200k terms; a cap hit is reported as
  `CANNOT_CHECK`, not as an optimum).

### 1.5 Frozen hostile witness (H-T86a)

`unsound_swap` must be able to change a value inside the frozen family. Witness fixed
before running: any frozen world containing a `+` node whose two operands `l`,`r`
satisfy `l+r != l*r` at some point of `X`; the run records the first such
`(world_id, subterm, x, value_sound, value_unsound)` triple and **fails the lane** if no
frozen world admits one.

### 1.6 Frozen no-alarm control

Clean arms run `SOUND_FROZEN + SOUND_EXT` only, on all 10 worlds. The contamination
detector must fire **zero** times. A detector that only ever fires is as broken as one
that never fires.

### 1.7 Cost model (T27/T87 split, defined here)

`T27` is not restated in #233, so the split is **defined by this protocol** rather than
inherited: **present cost** = work spent to answer the current query (rewrite
applications, e-nodes created, terms enumerated, process CPU seconds), charged in full
including rejected candidates and library acquisition. **Future reuse** = measured
saving on held-out worlds only, never netted against present cost in the same figure.
Library acquisition (worlds 0-4) and library application (held-out worlds 5-9) are
reported as two separate columns; the library is only credited on held-out worlds.

### 1.8 Endpoints and falsifiers

| id | endpoint | falsifier |
|---|---|---|
| E1 | contamination detection rate on hostile arms = 1.0 | any contaminated e-class with no alarm |
| E2 | false-alarm rate on clean arms = 0.0 | any alarm on a clean arm |
| E3 | per-arm present cost and gap to `direct_solve` optimum | an arm returning a non-equivalent term |
| E4 | library future reuse on held-out worlds, acquisition charged separately | acquisition never repaid -> `PARENT_SUFFICIENT`, a success terminal |
| E5 | T74 reduction composition sound; H-T74a broken leg caught | broken leg not caught |
| E6 | self-built e-graph vs `egglog` agreement on all TASK-EQ = 1.0 | any disagreement |

## 2. D22 — heterogeneous-logic transport

### 2.1 Fragments (all finite, all exhaustively enumerated)

* **L1 propositional** — frozen `ow7_worlds()`, atoms `{p,q}`, 4 valuations.
* **L2 Horn** — atoms `{p,q,r}`, 8 valuations, sentences restricted to Horn clauses.
* **L3 equational** — one binary operation on carrier `{0,1}`: all 16 algebras;
  sentences are equations in <= 2 variables.
* **L4 first-order finite-model fragment** — one binary relation on a 2-element
  universe: all 16 structures; sentences are quantifier-prefixed quantifier-free
  formulas in <= 2 variables.

### 2.2 Mechanical tests

* **T-SAT** satisfaction condition `M' |=_J alpha(phi) <=> beta(M') |=_I phi`, for every
  target model and every frozen sentence.
* **T-PRES** consequence preservation `Gamma |=_I phi => alpha(Gamma) |=_J alpha(phi)`.
* **T-REFL** reflection `alpha(Gamma) |=_J alpha(phi) => Gamma |=_I phi`.
* **T-EXP** model-expansiveness: surjectivity of `beta` onto `Mod(I)`.

### 2.3 Arms

* **CLEAN** — `beta = beta_alpha`, the induced reduct `beta(M')(a) := M' |=_J alpha(a)`,
  full target model set. Expected: T-SAT, T-PRES, T-EXP, T-REFL all hold; **no alarm**.
* **HOSTILE-SAT** — the frozen literal drop-extra reduct against the frozen translation
  `alpha(p)=p'`, `alpha(q)=p' & q'`. The satisfaction condition is expected to **fail**
  with witness `M'=(p'=0,q'=1,e)`, `phi=q`. The checker must fire and name the witness.
* **HOSTILE-IMAGE (H-T85a)** — `beta = beta_alpha` but the target model set is
  restricted to models with `p'=1`, so `beta`'s image misses every source model with
  `p` false. Expected: T-PRES still holds, T-EXP and T-REFL **fail**, witness
  `Gamma = {}`, `phi = p`, source counter-model `(p=0,q=0)`. The checker must fire on
  reflection and expansiveness and stay **quiet** on preservation.

Note recorded before running: the frozen `ow7_worlds` per-world removal of the single
target model `(0,0,1)` does **not** by itself break surjectivity of the drop-extra
reduct, because `(0,0,0)` still maps onto `(0,0)`. Model-image incompleteness is
therefore constructed as a derived hostile variant, following the established
`ow1_unsound_variant` pattern, rather than being read off the frozen generator.

### 2.4 Endpoints and falsifiers

| id | endpoint | falsifier |
|---|---|---|
| F1 | T-SAT decided exhaustively on every (model, sentence) pair per fragment | any pair left unchecked and reported as passing |
| F2 | T-PRES holds wherever T-SAT holds (T85 preservation half) | a preservation failure under a satisfying comorphism |
| F3 | T-REFL holds exactly where T-EXP holds | reflection holding without expansiveness, or failing with it |
| F4 | HOSTILE-SAT and HOSTILE-IMAGE both fire, each with a named witness | a hostile that does not fire |
| F5 | CLEAN arm raises zero alarms | any alarm on CLEAN |

### 2.5 Locks

`N4_formal_proof` stays **LOCKED**. No Lean adapter, no SMT adapter, no solver call.
`z3-solver`, `python-sat` and `pysmt` all install cleanly on the host and are
deliberately unused for exactly this reason. All D22 verdicts are P2 finite
certificates over enumerated models and are never relabelled as universal proofs.

## 3. Supersession rule

Changing anything above after this file is committed requires an explicit recorded
supersession in `FREEZE_V1.json` amendments with cause, plus a full re-run. Results
produced before this file existed are inadmissible.
