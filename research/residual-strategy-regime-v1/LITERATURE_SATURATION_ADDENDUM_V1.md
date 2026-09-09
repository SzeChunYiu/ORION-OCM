# Literature saturation addendum V1 — early-exit semantics and proof scheduling

**Status:** parent-map closure for R0A/R0C / no novelty claim / no ML authorization.

`LITERATURE_SYNTHESIS_V1.md` covered the common executive core.  Two specialized
questions required an additional search pass before calling the #152 literature
map saturated at the current scope.

## A. R0A exact early exit — observational/stuttering equivalence

The formal-methods literature already supplies the relevant abstraction
hierarchy:

```text
strong/stepwise bisimulation
  preserves exact observable transition structure

branching / stuttering equivalence
  may collapse internal unobservable steps while preserving the chosen
  linear/branching temporal observations (classically without an exact next-step
  observation)

program slicing
  removes statements only relative to an explicitly chosen semantic/variable
  criterion
```

This is the right parent for removing post-answer checks.  The scientific
question is not "did the final answer stay the same?" but "are the removed steps
silent under a prospectively frozen protected observation alphabet, and does the
early state remain equivalent for every future lifecycle transition?"

Key parent references:

- Browne, Clarke, Grumberg, "Characterizing finite Kripke structures in
  propositional temporal logic," 1988: stuttering-equivalence characterization
  for temporal logics without exact next-step sensitivity.
- De Nicola and Vaandrager, early 1990s work connecting branching bisimulation and
  stuttering semantics.
- Clarke, Grumberg, Peled, *Model Checking*: standard stuttering invariance of
  LTL without `X`.
- Groote and Wijs, "An O(m log n) Algorithm for Stuttering Equivalence and
  Branching Bisimulation," 2016: efficient behavioral-equivalence computation.
- Harman and Danicic, "Using program slicing to simplify testing," 1995:
  slicing is criterion-relative.

Adopted result: `R0A_TRACE_EQUIVALENCE_PROTOCOL_V1.md`.

## B. R0C proof scheduler — portfolio, schedule and restart parents

The proof-search scheduling problem is also mature.

### General algorithm portfolios

Gomes and Selman, "Algorithm portfolios," *Artificial Intelligence* 126 (2001),
43--62, show why interleaving/parallel portfolios can exploit variable runtime
profiles of stochastic search algorithms.

### Existing ATP schedulers

E's `--auto-schedule` explicitly tries several fully specified search strategies
under a schedule.  Vampire's CASC/portfolio mode likewise runs many proof-search
strategies.  These are direct engineering parents, not distant analogies.

### Learned ATP scheduling/tuning

Kühlwein and Urban, "MaLeS: A Framework for Automatic Tuning of Automated Theorem
Provers," *Journal of Automated Reasoning* 55 (2015), 91--116, explicitly solves
both strategy finding and strategy scheduling and evaluates on E, LEO-II and
Satallax.

Jakubův and Urban's BliStr/BliStrTune line automatically invents/tunes E search
strategies.  Therefore a learned proof scheduler already has strong conventional
parents and cannot be sold as a new executive principle by itself.

### Restart theory boundary

Luby, Sinclair and Zuckerman, "Optimal Speedup of Las Vegas Algorithms,"
*Information Processing Letters* 47(4) (1993), 173--180, derive universal restart
schedules for a Las Vegas algorithm with randomized runtime and correct output on
termination.

Adopt only when the actual proof experiment satisfies the independence/runtime
distribution assumptions.  Deterministic layered and indexed searches on the
same theorem are not automatically a Luby-restart instance.

Adopted result: `R0C_PROOF_SCHEDULER_PARENT_MAP_V1.md`.

## Saturation conclusion for current #152 scope

After adding these two lanes, continued searches repeatedly map the current
questions back into the same mature families:

```text
safe-enough information acquisition     -> DRD/ECD
worth another computation?              -> rational metareasoning / VoC
observation-channel sufficiency          -> Blackwell / deficiency
persistent lifecycle state              -> bisimulation / information state
unknown reuse horizon                    -> capital investment / multislope
safe check removal                       -> trace/stuttering equivalence / slicing
proof strategy choice                    -> portfolios / ATP schedules / restart
out-of-class truth                       -> misspecification / abstention/checker
residual per-instance prediction         -> classical algorithm selection
```

This is a productive saturation result: the next scientific work is mostly
**reduction validation and complete accounting**, not invention of new named
mechanisms.