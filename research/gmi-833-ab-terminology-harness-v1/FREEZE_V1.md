# FREEZE — `gmi-833-ab-terminology-harness-v1` (issue #833, section AB)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, test,
receipt or workflow file of this package exists. `git log --reverse` over
`research/gmi-833-ab-terminology-harness-v1/` must show this file first.

## 1. Source pin

- `source_main` = `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`
- issue comment under reconciliation: `5684607872`, anchor
  `### AB. Academic terminology and ontology normalization`
- live comment bytes at freeze: 13248 (LF only).

## 2. Claim ceiling

`REGISTERED_TERMINOLOGY_AUDIT_VERIFIED_V1`

This package is an **exact instrument** over terminology artifacts already
frozen on `main`. It verifies, per AB row, that the registered audit exists and
covers every comparison term the row names, and it measures corpus-state
compliance exactly. It establishes nothing about the truth of any GMI theorem
and does not itself perform any corpus migration.

## 3. Audit-clause vs corpus-state clause (declared before implementation)

Most AB rows carry two clauses: an **audit clause** (compare the legacy term
against a named set of canonical parents and emit a verdict + migration rule)
and a **corpus-state clause** (how the corpus actually uses the term). This
package earns the audit clause by exact verification and **reports the
corpus-state number as a disclosed residual**, never as discharged. A row whose
governing verb is itself corpus-mutating (AB02 `Replace`) is NOT earned here.

## 4. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Build a living `GMI_TERMINOLOGY_CROSSWALK` with: legacy GMI term, proposed paper term, academic field, canonical term(s), exact match/partial match/non-match, citations, definition, migration rule.
    - [ ] Audit `morphology`; compare against **architecture**, **computational architecture**, **model class**, **representation**, **algorithm**, and **computational mechanism**. Keep `morphology` only where structure across heterogeneous computational organizations is genuinely intended.
    - [ ] Audit `machine species`; compare against **algorithm/configuration class**, **model family**, **architecture family**, **behavioral phenotype**, and **equivalence class**. Treat biological language as analogy unless formally defined.
    - [ ] Audit `ecology`; compare against **task distribution**, **environment**, **problem distribution**, **instance space**, and **operating regime**.
    - [ ] Audit `niche`; compare against **region of instance space**, **operating regime**, **performance region**, and **domain of competence**.
    - [ ] Audit `selection`; distinguish **algorithm selection**, **model selection**, **architecture search**, **hyperparameter/configuration selection**, and evolutionary selection.
    - [ ] Audit `phase law/phase diagram`; use only when there is a well-defined control-parameter space and qualitative regime transition; otherwise use regime map/crossover map.
    - [ ] Audit `prior-free`; replace with **architecture-agnostic**, **architecture-uncommitted**, **family-agnostic search**, or explicit `architecture-prior-free` only after defining what priors remain.
    - [ ] Use **inductive bias** for representational/search preferences when that is the established ML concept.
    - [ ] Use **hypothesis class/search space/program space** rather than vague `possibility space` where appropriate.
    - [ ] For synthesis, use **DSL / grammar / primitive set / search space / search strategy** where those are the actual objects; explicitly acknowledge that the DSL itself induces strong bias.
    - [ ] Audit `neutral search`; replace with a precise description such as family-blind enumerative search, architecture-agnostic search, grammar-based synthesis, evolutionary search, etc.
    - [ ] Audit `remint`; paper-facing alternatives should normally be **independent regeneration**, **re-randomization**, **relabeling control**, **fresh-instance replication**, or **independent replication**, depending on what was done.
    - [ ] Audit `negative twin`; compare with **matched negative control**, **counterfactual control**, **ablation**, **placebo condition**, or **negative control**.
    - [ ] Audit `parent subtraction`; paper-facing terminology should normally be **comparison to strongest baselines/parent theories**, **subsumption analysis**, **reduction**, **ablation**, or **novelty analysis**.
    - [ ] Audit `carrier`; map where possible to **state representation**, **state space**, **memory substrate**, **computational substrate**, or **representation space**.
    - [ ] Audit `quotient`; retain mathematical quotient where exact; otherwise use **equivalence classes**, **state abstraction**, **minimal sufficient representation/state**.
    - [ ] Audit `capability ceiling`; compare with **upper bound**, **impossibility result**, **capacity bound**, **information-theoretic limit**, **sample/communication/complexity bound**.
    - [ ] Audit `development`; distinguish **online learning**, **continual learning**, **meta-learning**, **self-modification**, **architecture adaptation**, **developmental learning**, and **evolution**.
    - [ ] Audit `evolvability`; use the established evolutionary-computation/ALife meaning and avoid using it as a synonym for ordinary adaptability.
    - [ ] Audit `open-ended`; connect explicitly to **open-ended evolution/open-endedness** literature; do not use it merely to mean a large search space.
    - [ ] Audit `novel intelligence`; distinguish **novel implementation**, **novel architecture**, **novel algorithmic mechanism**, **novel model class**, **novel computational paradigm/domain**, and **novel capability profile**.
    - [ ] Audit `unseen form`; paper-facing term should specify whether this means held-out architecture, predicted morphology, novel mechanism, or new computational class.
    - [ ] Audit `cognition` terms against cognitive science rather than ML metaphors: working/episodic/semantic/procedural memory, attention, metacognition, theory of mind, etc.
    - [ ] Require cognitive terms to satisfy operational criteria before claiming correspondence to human/animal constructs.
    - [ ] Audit `causal` terminology against SCM/intervention/counterfactual conventions.
    - [ ] Audit uncertainty terminology against aleatoric/epistemic, confidence set, credible set, calibration, identifiability, and partial identification conventions.
    - [ ] Audit `verification`; distinguish formal verification, empirical validation, evaluation, testing, certification, and verifier feedback.
    - [ ] Audit `proof`; never call exhaustive finite computation a mathematical proof without stating the certificate/computer-assisted status precisely.
    - [ ] Audit `derive`; reserve it for a conclusion logically/mathematically obtained from stated premises; otherwise use recover, select, fit, construct, reproduce, or explain.
    - [ ] Audit `predict`; require temporal/epistemic separation from the outcome; otherwise use post-hoc explanation or reconstruction.
    - [ ] Audit `discover`; require that the target was not encoded/named/privileged and that novelty survives parent reduction.
    - [ ] Create a banned/avoid list of internally convenient but academically misleading terms for manuscripts.
    - [ ] Require terminology review as a CI/checklist gate for flagship documents.
**No neighboring row is earned here.** Explicitly NOT earned:

    - [ ] Replace paper-facing `obligation` with `task`, `specification`, or `formal/behavioral specification` according to exact semantics; formal methods uses **formal specification** for a mathematical description of intended system behavior.
    - [ ] Explicitly parent-subtract Rice-style **algorithm selection**: problem space, feature space, algorithm space, performance space, selection mapping.
    - [ ] Define a novelty ladder using those academically interpretable levels.
and no row of AA, AC or AD.

## 5. Forbidden promotions

- `CORPUS_TERMINOLOGY_CLEAN` / `MIGRATION_COMPLETE` — false at `source_main`;
  the measured repo-wide gate baseline is disclosed in `RESULT_V1.json`.
- `ALL_PARENTS_EXHAUSTED`, `CITATIONS_VERIFIED` — the parent crosswalk
  self-flags most references `CITE-TF` (not re-verified); AC05 and AC09 are
  NOT earned and are not in scope here.
- any promotion of a registered audit verdict into a proof that the legacy term
  is or is not novel.

## 6. Parent ownership (declared before implementation)

- `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md`
  blob `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054` — **owns** the 48-row
  crosswalk and every AB term audit. Not claimed novel here.
- `research/gmi-833-tranche-ab-ac-lit/BANNED_PAPER_TERMS_V1.md`
  blob `dac215a93c1d5066c927e822edc12766e765fe17` — owns the banned list (AB36).
- `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py`
  blob `93041ba0ecd24abd5228a21feddec5d5d45db5de` — owns the scanner.
- `research/gmi-833-terminology-migration-v1/MIGRATION_LOG_V2.md`
  blob `0f6ed3d18ce1155d5d8a5ec0bf3977c21e55199e` — owns the executed migration
  over the non-aj `research/gmi-833-*` corpus.
- `research/gmi-833-g0-grammar-bias-v1/` — owns the grammar-induced-bias result
  (AB13's "DSL itself induces strong bias").
- `research/gmi-833-cognitive-reaudit-v1/COGNITIVE_REAUDIT_THEOREMS_V1.md` —
  owns the operational probe-distinguishability criterion (AB28).

External parents cited by the crosswalk and re-stated, not claimed novel:
Rice, "The algorithm selection problem", *Advances in Computers* 15 (1976),
doi:10.1016/S0065-2458(08)60520-3; Mitchell, "The need for biases in learning
generalizations" (1980); Wolpert & Macready, "No free lunch theorems for
optimization", IEEE TEC 1(1) 1997, doi:10.1109/4235.585893; Alur et al.,
"Syntax-guided synthesis", FMCAD 2013, doi:10.1109/FMCAD.2013.6679385;
Wagner & Altenberg, "Complex adaptations and the evolution of evolvability",
Evolution 50(3) 1996, doi:10.2307/2410639; Hales, "Formal proof", Notices AMS
55(11) 2008; Pearl, *Causality* (2000); Der Kiureghian & Ditlevsen, "Aleatory
or epistemic? Does it matter?", Structural Safety 31(2) 2009,
doi:10.1016/j.strusafe.2008.06.020.

**Residual contribution claimed here:**
(a) a per-row machine-checkable requirement table binding each AB row to the
    exact comparison terms its own text names, and an exact two-route verifier
    that the registered audit covers them;
(b) the first repo-wide measurement of terminology corpus state at
    `source_main` (the parent gate had only ever been run over one package);
(c) a **ratcheting**, blocking, repo-wide CI gate over `research/**` that
    acknowledges the measured baseline and fails on any new banned-term site —
    the residual AB37 asks for, which the parent's path-scoped `|| true`
    workflow does not supply.

## 7. Evidence standard binding this package

Two materially independent routes for every computational claim; hostiles that
are detected AND whose perturbed quantity is asserted to have moved; a null the
true result beats; exact arithmetic only; stdlib only; runnable under
`python3 -I -B` and `python3 -I -O -B`.
