# F1 matched mechanical search parent

Read-only decision, 2026-09-07. **Adopt the pinned Aesop search engine with an explicit permitted rule set and fresh Lean environment.** Keep a small native Lean application search as an ablation. Preserve the Python F0 engine as historical fragment evidence; extending its private type system is not the next implementation.

This is a proposed, unbuilt adapter. First commission it on exposed fixtures; actual masked-region registration follows semantic coverage. No targets, withheld proofs or successful routes were inspected. No builds, native operations or studies ran.

## Exact inputs and attribution

| Component | Source binding and role |
|---|---|
| Aesop | [`3448c0bcc5ce01b2d1546e483ec3620e32df3d0e`](https://github.com/leanprover-community/aesop/tree/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e), corpus lockfile revision; Apache-2.0 source headers |
| Lean | [`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`](https://github.com/leanprover/lean4/tree/819816b2e0a3bf405af45ae5c7af2491d8f5bee6), qualified 4.33.1 distribution already on billy |
| Batteries | Corpus lock resolves `4488d40d070b9700d4d5a6aa342f0d40c31b2a2d`; retain this exact dependency resolution |
| Existing F0 | OCM [`9b00cfe36880855a3786f942b990755553b74956`](https://github.com/SzeChunYiu/ORION-OCM/tree/9b00cfe36880855a3786f942b990755553b74956/research/mechanical-proof-v1); inspected working bytes match its Git blobs |

Aesop's own [toolchain](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/lean-toolchain) says **4.33.0**; its [Lake file](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/lakefile.toml) requests Batteries v4.33.0. Rebuilding the locked source under 4.33.1 is a separately qualified adaptation. No compatible compiled Aesop artifact was established here.

The [existing parent matrix](../programme/PARENTS.md) remains applicable: donor search, indexing and library reuse are parent mechanisms. This adapter supplies a matched baseline, not OCM novelty or learned cognition.

## Mechanism to absorb

Aesop performs symbolic AND–OR search with normalization, committed safe rules, backtracking unsafe rules and explicit priorities. Its default queue is best-first; neither the queue nor rule probabilities require a neural model. Automatic induction is outside its documented basic design. [Pinned README](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/README.md).

The useful entry is **`Aesop.search`**, not a generated `by aesop` script. It accepts `MVarId`, optional `LocalRuleSet`, options and simp configuration, returning remaining goals plus statistics in `MetaM`. Passing `some rules` bypasses its default global-rule lookup. Proof completion assigns the root metavariable; extract the instantiated expression and still send it to the independent checker. [Search/Main.lean:250–271](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/Search/Main.lean#L250).

`LocalRuleSet.empty` supplies empty rule, simp and simproc collections. Add explicitly built members with `LocalRuleSet.add`. The constant-application builder indexes the conclusion, and its rule tactic creates fresh universe metavariables before applying the named constant. This absorbs real Lean unification and dependent application rather than reimplementing them in Python. [RuleSet.lean:234–242](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/RuleSet.lean#L234), [Builder/Apply.lean:28–46](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/Builder/Apply.lean#L28), [RuleTac/Apply.lean:64–76](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/RuleTac/Apply.lean#L64).

## Three boundaries that prevent a misleading comparison

1. **Removing rule names is not removing imported knowledge.** The ordinary frontend loads global rules; `mkLocalRuleSet` can load default simp lemmas and simprocs. Moreover, `SearchM.run` obtains `getSimpCongrTheorems` even with an explicit rule set. `useDefaultSimpSet=false` explicitly does not exclude congruence lemmas. Start in a newly reconstructed environment, not an imported Mathlib environment with names erased. [Frontend/Tactic.lean:175–179](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/Frontend/Tactic.lean#L175), [SearchM.lean:75–85](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/Search/SearchM.lean#L75), [Options/Public.lean:130–135](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/Options/Public.lean#L130).

2. **Compiled code and logical declarations are separate.** Aesop's named builtin rule callbacks use `evalConst`; tactic syntax uses elaboration. Simply linking Aesop does not prove these paths function against a fresh permitted environment. Prefer data descriptors for admitted constants. If builtin callback lookup needs an imported code environment, resolve a fixed audited callback table before task loading and adapt dispatch to invoke those compiled callbacks under the permitted environment. Never temporarily import/restore the code environment inside search or copy its extensions. This is an implementation proposal requiring validation, not a verified workaround. [RuleTac/Tactic.lean:15–51](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/RuleTac/Tactic.lean#L15).

3. **Non-neural is an enforced configuration, not a library-name claim.** Aesop exposes `TacGen` callbacks and arbitrary tactic descriptors. The initial adapter must reject those inputs and accept only registered symbolic primitive descriptors and an audited builtin callback allowlist. Do not load a tactic generator, embedding service, pretrained policy or task-provided executable. [RuleTac/Descr.lean](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/RuleTac/Descr.lean), [RuleTac/Basic.lean:136–146](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/RuleTac/Basic.lean#L136).

## Smallest useful successor

1. Build a separate generic search executable from the pinned Lean/Aesop/Batteries code. Its link/import audit excludes corpus and fixture modules. Qualify its own measured runtime mounts; do not reuse the smaller checker's binary receipt.
2. Reuse the checked permitted declaration packet, independent target packet and primitive/axiom policy. Replay exactly the same permitted kernel environment as the checker, then start fresh `Core.State`/`Meta.State`. Do not expose evaluator source exports, wrapper text, withheld-proof metadata, support paths, masks' derivation history or route notes to search. Admitted declaration names remain exactly registered.
3. Construct all eligible application rules deterministically from the admitted declarations, with frozen priorities and order; use the same rule list for both experimental arms. Add audited intros, local-hypothesis application/assumption and constructor application. Keep theorem applications backtrackable unless a registered generic safety argument justifies commitment. No task-specific “safe” classification inferred from the withheld proof.
4. Commission the core with explicit empty simp/simproc collections, `enableSimp=false`, `enableUnfold=false`, `useDefaultSimpSet=false`, no script generation and terminal proof completion required. These switches reduce the initial adapter boundary; they do not certify absent extension state. Keep native definitional equality and universe handling.
5. Before the first scored run, test whether registered development obligations require simplification, cases or instances. Add those existing parent mechanisms using explicit permitted lemma/congruence/instance metadata and audited callbacks. Charge compilation/indexing. Do not score only obligations where the stripped core happens to succeed or call it the strongest full Aesop configuration.
6. Return a closed instantiated `Expr` via the existing transport. Missing environment support, unsolved metavariables, exhausted resources and incomplete search remain distinct outcomes. Only a fresh independent exact-target/kernel/axiom check can accept the candidate.

The native entry can be as small as this **uncompiled API sketch**:

```text
checked replay → Core.State.env := permittedEnv; fresh Meta.State
independent target Expr → fresh root metavariable
explicit LocalRuleSet + registered options → Aesop.search root (some rules)
require no remaining goals → instantiate assigned root Expr
candidate-only packet → separate already-qualified checker
```

Lean already exposes `MetaM.toIO` with explicit core/meta state. `mkEmptyEnvironment` creates empty constants but initializes registered extensions, so extension initialization must be audited rather than assumed empty. `MVarId.apply` performs dependent matching and can invoke instance synthesis; absent instance metadata is a capability gap, while inherited instance indexes are an exposure gap. [Meta/Basic.lean:612–620](https://github.com/leanprover/lean4/blob/819816b2e0a3bf405af45ae5c7af2491d8f5bee6/src/Lean/Meta/Basic.lean#L612), [Environment.lean:1530–1543](https://github.com/leanprover/lean4/blob/819816b2e0a3bf405af45ae5c7af2491d8f5bee6/src/Lean/Environment.lean#L1530), [Apply.lean:169–227](https://github.com/leanprover/lean4/blob/819816b2e0a3bf405af45ae5c7af2491d8f5bee6/src/Lean/Meta/Tactic/Apply.lean#L169).

Do not silently add helper lemmas needed by automation. Either admit their independently checked declarations/closure as an explicit common base for both arms and checker, or preserve a capability refusal. Compiled tactics may propose constants; the permitted environment and final proof dependency check remain authoritative.

## What is actually compared

| Arm | Intended role | Faithfulness boundary |
|---|---|---|
| Historical Python F0 | Regression/control for finite application closure after leading-Pi introductions | Six AST forms; universes 0–2; beta conversion; opaque constants; no internally synthesized lambdas or induction. Not a full-Lean parent. [Search](https://github.com/SzeChunYiu/ORION-OCM/blob/9b00cfe36880855a3786f942b990755553b74956/research/mechanical-proof-v1/f0_search.py), [terms](https://github.com/SzeChunYiu/ORION-OCM/blob/9b00cfe36880855a3786f942b990755553b74956/research/mechanical-proof-v1/f0_terms.py) |
| Native Lean bounded intro/apply search | Small ablation separating native unification from indexed AND–OR search | New adaptation using the same admitted rules and fresh environment; not a reproduction of historical Python F0 |
| Pinned Aesop fixed-rule adapter | Primary matched non-neural search baseline; same engine available to OCM | Upstream queue/index/search and selected rule mechanics retained; changed dispatch/environment/rule policy disclosed. Initial reduced configuration is not default Aesop or best possible Lean automation |

Full imported-Mathlib `aesop` may be an external reference later, but it is not a matched masked-region baseline when it can read excluded declarations. An eventual OCM search/library improvement must beat the equally equipped allowed-environment Aesop arm, not only Python enumeration.

## Qualification and complete cost boundary

Before any protected region: clean reconstruction/search/check positive; a goal needing an introduced lambda; dependent/universe application; and paired authored controls where only a removed alias, instance, simp/congruence lemma or callback can close the goal. The restricted arm must not recover excluded data through imported extensions or code lookup. Check the permitted declaration inventory before and after search; reject unintended persistent additions. Reset all search caches between independently cold trials.

Account for evaluator semantic export/closure, packet construction, checked replay, search executable/codebase and background logical information, rule/index construction, instance/simp metadata, failed attempts, reductions/unification, explored goals/rule applications, candidate serialization, fresh checking, restart, wall/CPU/RSS and retained bytes. Aesop returns statistics and supports goal/application/depth controls; its internal counts do not cover the entire pipeline. [Stats/Basic.lean](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/Stats/Basic.lean), [Options/Public.lean](https://github.com/leanprover-community/aesop/blob/3448c0bcc5ce01b2d1546e483ec3620e32df3d0e/Aesop/Options/Public.lean).

Register resource settings and rule policies on development inputs, retain failures, then freeze the denominator before masked-region results. No neural selection, acquired library, lifetime amortization or transfer is supplied by this first parent. The immediate implementation owner should build **one permitted-environment Aesop adapter and its boundary controls**, reusing the commissioned exporter/checker. Corpus semantic coverage remains the prerequisite for the first actual reconstruction study.
