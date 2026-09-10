# M2-P1 hidden-family developmental study — RESULT

Read [CORE.md](CORE.md) first. Design registered in
[../HIDDEN_FAMILY_DESIGN.md](../HIDDEN_FAMILY_DESIGN.md) **before** any scored result
was read; the E1/E2 variants and the interleave-toll attribution were committed ahead
of the first run.

## What was and was not changed

`src/ocm/learning/methods.py` is imported and driven **AS-IS**: `learn_generator`,
`validate_generator`, `solve`, `verify_solution`. No new cognitive core, no learned
router (#71), no relaxation of the no-slowdown rule, no threshold tuning (#323 §11).
**The ecology changed; the machine did not.**

The M2 negatives established why that was the right move: on the M1 ecology the agent
is handed the complete generative grammar, so the optimal structural prior is
derivable a priori and history is redundant *by construction*
([../RESULT.md](../RESULT.md#m2-n2)). M1's learner mining 16 useless fragments and
refusing to deploy them was **correct behaviour on an ecology with nothing to learn.**

## Ecology

Targets are normal forms whose canonical (first-in-enumeration) program is a
concatenation of motifs from a **hidden** set the agent is never told. The motif set is
not derivable from the declared grammar, so a grammar-only agent must enumerate
primitives while an agent with history can mine the motifs from its own checked
solutions.

Blocking entry gates, all asserted before scoring: **G1** length-distribution parity
across streams (max deviation 0.0093 — this is the direct guard against M2-N4, where
M1's protected slice was unrepresentative of its own ecology), **G2** disjoint normal
forms between history and targets, **G3** canonical-program motif decomposability.

<a id="m2-p1a"></a>
## M2-P1a `DEVELOPMENTAL_SEARCH_PRIOR_DEMONSTRATED`

The registered learner mines a generator from solved developmental tasks; the
registered `validate_generator` scores it on held-out tasks whose normal forms are
disjoint from history (G2) and which are externally verified.

| world | host | held-out | strictly better | mean `B` baseline → candidate | reduction |
|---|---|---|---|---|---|
| seed 20260910 (E1) | billy-old | 53 | **46** | 33 866 → 12 766 | **62.3 %** |
| seed 1002 (E1) | LUNARC | 55 | 43 | 37 413 → 26 340 | 29.6 % |
| seed 1004 (E1) | LUNARC | 55 | 46 | 34 098 → 14 948 | 56.2 % |
| seed 1006 (E1) | LUNARC | 52 | 35 | 36 971 → 18 921 | 48.8 % |
| seed 1007 (E2) | LUNARC | 50 | 38 | 40 228 → 26 323 | 34.6 % |
| seed 1008 (E1) | LUNARC | 49 | 28 | 29 460 → 23 497 | 20.2 % |

Six independently seeded worlds — **different hidden motif sets** — on **two hosts**.
Every world shows a majority of held-out tasks strictly cheaper and a substantial
mean work reduction. The reduction is measured *net of* the interleave toll the guided
arm pays, so it is conservative against the history arm.

**This is acquisition, not retrieval.** The decisive control is `LIBRARY_ONLY`, which
carries every solved object from history and is byte-identical to `RESET` on the
protected targets (189/395 successes, mean `B` 17 882.9 both). Stored answers are worth
exactly **zero** on new targets, because G2 guarantees their normal forms are disjoint.
What transfers is the *search prior*, not the solutions.

## Scored arms on 79 new targets — structure, not volume

Two worlds have completed all six arms. Every protected target is externally verified
by an independent checker process, and every arm ran after a real OS-process restart
(`pid_changed` asserted).

| arm | world 1002 ladder / mean `B` | world 1008 ladder / mean `B` |
|---|---|---|
| `ORACLE_FAMILY` (true motifs, calibration) | 329 / 2 776 | 282 / 3 432 |
| `ORDINARY_ADAPTIVE_PARENT` (mined library, no gate) | **260 / 8 170** | **257 / 6 643** |
| best **history-free** surface ordering | 190 | 188 |
| `RESET` = `LIBRARY_ONLY` = `CONTINUED` | 186 / 24 342 | 188 / 20 360 |
| `SHUFFLED_HISTORY` (random library, matched profile) | **149 / 43 042** | **157 / 32 395** |

Three things follow.

**The benefit is structure, not volume.** `SHUFFLED_HISTORY` carries a library of the
same fragment count and length profile, with random content — and it is *worse than no
library at all* (43 042 vs 24 342). A library only helps if it is the library history
actually mined. That pairing — shuffled below `RESET`, mined far above it — is the
causal claim.

**It is not the M2-N1 artifact.** The G4 gate compares against the best history-free
surface ordering (`ASC` / `DESC` / `CONST8-first`), which is exactly the constant-offset
trick that manufactured M1's illusory headroom. The mined library beats it decisively
(260 vs 190; 257 vs 188): `PASS_COUNTERFACTUAL`.

**`CONTINUED` is identical to `RESET` to the slot.** Under refusal it serves no
generator, so all three no-library arms coincide exactly — the same signature as M1's
four byte-identical arms, and here we know precisely why.

### A defect in this study's own checker, found and repaired

G4 was originally wired to `CONTINUED`. Under refusal that arm serves nothing, so the
gate compared a *null* arm against the surface baseline and emitted
`FAIL_SURFACE_ORDERING_EXPLAINS_ADVANTAGE` — reporting that surface ordering explained
an advantage that did not exist in that arm at all. That is the #323 §HC-4 failure
class in this lane's own instrument: a locally correct-looking check disconnected from
the proposition it protects.

Repaired: G4 now emits `CANNOT_CHECK_NO_DEPLOYED_HISTORY_ARM` whenever
`admission=false`, and a separately labelled counterfactual gate evaluates the no-gate
parent. `CANNOT_CHECK` is kept distinct from both PASS and FAIL. The two completed
worlds were re-scored under the repaired checker; the terminal did not change.

## Cost completeness (#323 HDI-14) — the prior works and does not yet pay

Acquisition is charged in full, in the same currency as the benefit:

| | world 1002 | world 1008 |
|---|---|---|
| acquisition (developmental solving + validation), slots | 5 026 590 | 3 452 344 |
| saved per protected target, slots | 16 172 | 13 717 |
| total saved over 79 targets | 1 326 137 | 1 001 305 |
| **net** | **−3 700 453** | **−2 451 040** |
| break-even horizon, targets | **311** | **252** |

The transfer is real and large per target, but the developmental investment needs
roughly **250–310** future targets to repay itself and only 79 are available at this
scope. So at this horizon the mechanism is **not** economically positive. This is
recorded as a limitation of the scope, not explained away — and it converges
independently on the `AMORTISATION_DOMINATED` terminal reached by the DEV-CAL-2 lane.

<a id="m2-p1c"></a>
## M2-P1c development depth is a dose-response — and it is **not** monotone

`validate_generator` scored at frozen developmental depths on the same held-out set:

| depth | fragments | strictly better | worse | work reduction |
|---|---|---|---|---|
| 8 | 10 | 36/53 | 17 | 21.9 % |
| 16 | 16 | 39/53 | 14 | 37.7 % |
| 32 | 16 | **50/53** | **3** | **72.2 %** |
| 64 | 16 | 48/53 | 5 | 66.9 % |
| 128 | 16 | 46/53 | 7 | 62.3 % |

The rise from 21.9 % to 72.2 % across a 4x increase in developmental depth is a **history-depth gradient that no stored-answer
account explains**: the held-out set is fixed, only the amount of developmental
experience varies. This is the single strongest piece of evidence for *development*
rather than *possession*.

The decline after the peak is equally informative. `learn_generator` keeps the top-16
fragments by support count; as developmental depth grows, that fixed capacity fills
with **generic high-support fragments** that dilute the true motifs and inflate the
guided branching factor. This is #323 **HC-7** — knowledge value as an economic routing
problem — appearing as a measured curve: unbounded accumulation *degrades* the search
prior. `monotone_nondecreasing` is reported as `false`, which is the finding, not a
defect.

<a id="m2-p1b"></a>
## M2-P1b `ADMISSION_VETO_IS_STRUCTURAL`

**Admission was refused in every world — 6 of 6 (7 of 7 including the depth sweep.)**
That is not bad luck.

`validate_generator` admits only if the candidate is no worse on **every** held-out
task. Under the registered interleaved integration, any task whose answer the guided
stream does not reach first costs exactly **2×**. The attribution is exact rather than
asserted: **every vetoing task returns ratio ≤ 2.00**, the deterministic signature of
"the guided stream contributed nothing here and paid only the toll".

The obvious next question — and the one that decides whether the veto is a fixable
detail — is whether veto-prone targets can be anticipated. They cannot:

| world | held-out | vetoes | rate | best single-threshold lift over the trivial majority null |
|---|---|---|---|---|
| billy-old | 53 | 7 | 0.132 | +0.019 |
| seed 1002 | 55 | 12 | 0.218 | +0.018 |
| seed 1004 | 55 | 9 | 0.164 | +0.036 |
| seed 1005 | 42 | 8 | 0.191 | +0.024 |
| seed 1006 | 52 | 17 | 0.327 | +0.115 |
| seed 1007 | 50 | 12 | 0.240 | +0.020 |
| seed 1008 | 49 | 21 | 0.429 | +0.082 |

Neither search cost nor canonical program length separates vetoing from clean targets
beyond the trivial majority-class baseline, and the per-length veto rates are
**inconsistent across worlds** — one world vetoes 3/3 of its shortest targets, another
0/3. So the veto-prone class is real, is present at a rate of 0.13–0.43 that does not
shrink with `n`, and **cannot be identified in advance**.

The consequence needs no distributional assumption:

> Admission requires universal non-inferiority over a held-out set that reliably
> contains veto-prone targets whose identity cannot be anticipated. Enlarging the
> held-out set — giving the gate *more* evidence — can only add more opportunities to
> veto. The rule is therefore self-defeating in the direction of more validation.

For illustration only, **assuming independence** (which the exactly-2.00 signature
makes questionable and which nothing here relies on), a pooled rate of ≈0.24 gives
`P(admit) = (1−p)^n`, falling below 0.05 by `n ≈ 9`. That bound is labelled as
illustrative throughout; the empirical claim is the 7/7 refusal record with the
measured, unpredictable veto rates above.

**The rule was not relaxed.** It is bounded, and the bound is the finding.

## Terminal

```text
DEVELOPMENTAL_CAPABILITY_DEMONSTRATED__DEPLOYMENT_GATE_VETOED
```

OCM demonstrably **acquires** a transferable search prior that makes new externally
verified cognition 20–72 % cheaper, with a history-depth dose-response; and it
demonstrably **fails to deploy** it, for a reason localized to one stage and bounded
without an independence assumption. The registered precedence in the summarize script
maps `admission=false` to `PARENT_SUFFICIENT__LEARNER_REFUSED_DEPLOYMENT`, and that
precedence stands rather than being reasoned around.

## Claim ceiling

> history-induced search-prior transfer, on an authored ecology whose family structure
> is measured not to be surface-derivable.

**Not** general developmental intelligence. **Not** open-endedness. Fresh-host and
fresh-world replication are met; replication on an ecology **authored by someone else**
is **unmet**, so #323's success certificate is not claimed closed. `CANNOT_CHECK` is
preserved: the deployment-stage counterfactual is reported from the no-gate parent arm
and is labelled as a counterfactual, never as OCM deploying a prior.
