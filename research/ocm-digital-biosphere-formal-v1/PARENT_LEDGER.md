<!--
MERGE NOTE FOR EB-F0-A. This file is an APPEND-ONLY appendix contributed by lane EB-F0-P.
If your capsule table lands first, resolve by placing it ABOVE the heading below and keeping
this section verbatim. Nothing here edits, restates or supersedes any row of your table.
-->

## Primary-source verification appendix (EB-F0-P)

Issue #296 section 14 requires that established results be reconstructed faithfully and
subtracted before ORION claims novelty about biospheres, evolution, culture or collective
cognition. This appendix does that for all fifteen BIO-T rows of section 13, and supplies the
primary-source check that this ledger's own header demands before any citation may mint a
sufficiency terminal.

Machine-readable companion: `BIO_PARENT_MATRIX_V1.json` in this directory. It carries, per row,
the owning parent, a fetched quoted line with its provenance, the faithful reconstruction, the
parent's own assumption list, the gap or its absence, the subtraction verdict, and the attached
published negatives. It is the intended source for the `parent_ownership` field of
`THEOREM_REGISTRY_V1.json`. Grading enums are reused unchanged from
`research/top-tier-atomic-closure-v1/PARENT_FIRST_REFUSAL_V1.json`, so the join needs no translation.

### Result

Of fifteen rows, **14 are owned outright by an established result** and one carries a named
partial gap. No row was left without a parent. This is the good outcome, and it is reported as one:
the programme's standing doctrine is assimilation-first, and a row that turns out to be owned
closes as a success rather than as work.

| | count |
|---|---|
| PARENT_PARTIAL_GAP_NAMED | 1 |
| PARENT_RECONSTRUCTED | 14 |
| rows verified by this lane's own fetch | 13 |
| rows cited by prior-lane byte-exact anchor | 2 |
| rows naming a source that could not be reached | 2 |
| published negatives attached to rows | 11 |

### Row ownership

| row | owning parent | what the parent already says | verdict |
|---|---|---|---|
| BIO-T1 | Pearl, *Statistics Surveys* 3:96-146, 2009 (do-operator / SCM) | intervention on a non-ancestor changes nothing | `PARENT_RECONSTRUCTED` |
| BIO-T2 | Pigeonhole (deterministic); Levin-Peres-Wilmer (finite chains) | eventual periodicity; pi(x)=1/E_x(tau_x+) | `PARENT_RECONSTRUCTED` |
| BIO-T3 | Enhanced POET, arXiv:2003.08536v2 (anchor B05) | novelty exhausts when the encoding does | `PARENT_RECONSTRUCTED` |
| BIO-T4 | Rogers, *Am. Anthropol.* 90(4):819-831, 1988 | social learning does not raise mean fitness | `PARENT_RECONSTRUCTED` |
| BIO-T5 | Data processing inequality (Polyanskiy-Wu Thm 7.16) | I(U;Y) <= I(U;X) for U->X->Y | `PARENT_RECONSTRUCTED` |
| BIO-T6 | Minton, AAAI-88 p.566 (anchor A10; RV-8) | Utility = (AvrSavings x ApplicFreq) - AvrMatchCost | **`PARENT_PARTIAL_GAP_NAMED`** |
| BIO-T7 | Blount, Borland & Lenski, *PNAS* 105(23):7899-7906, 2008 | potentiation must precede actualization | `PARENT_RECONSTRUCTED` |
| BIO-T8 | Bahrami et al., *Science* 329(5995):1081-1085, 2010 | two heads worse than the better one | `PARENT_RECONSTRUCTED` |
| BIO-T9 | Price 1970/1972 (originals not reached); Frank, arXiv:1204.1515 | w-bar dz-bar = Cov(w,z) + E(w dz), an identity | `PARENT_RECONSTRUCTED` |
| BIO-T10 | Goguen-Burstall (P12, HSG ledger); Sogaard et al., ACL 2018 P18-1072 | preservation is not reflection | `PARENT_RECONSTRUCTED` |
| BIO-T11 | Kac's formula (Aldous-Fill Lemma 2.24; LPW eq. 21.7) | mean return time = 1 / stationary mass | `PARENT_RECONSTRUCTED` |
| BIO-T12 | Imai, Keele & Yamamoto, *Statist. Sci.* 25(1):51-71, 2010 | mediation needs sequential ignorability | `PARENT_RECONSTRUCTED` |
| BIO-T13 | Mesoudi & Thornton, *Proc. R. Soc. B* 285:20180712, 2018 | four criteria; growth satisfies none of (iii)-(iv) | `PARENT_RECONSTRUCTED` |
| BIO-T14 | Sukumaran & Knowles, *PNAS* 114(7):1607-1612, 2017 | the method delimits structure, not species | `PARENT_RECONSTRUCTED` |
| BIO-T15 | Dwork, Feldman, Hardt, Pitassi, Reingold & Roth, STOC 2015; arXiv:1411.2664 | adaptivity voids the held-out guarantee | `PARENT_RECONSTRUCTED` |

### The one named gap: BIO-T6

Minton's utility problem owns the row. A learned rule earns its place only if average savings
times application frequency exceed the average match cost paid on every attempt. That
inequality is fully owned and must never be claimed here.

What no parent supplies is the **crossover locus**: the pair (critical same-family share,
break-even task horizon) at which the sign of the inequality flips for a given substrate. RV-8 in
`research/top-tier-atomic-closure-v1/REVIVAL_BACKLOG_V1.json` records a primary-source sweep of the
utility-problem literature that found the per-rule inequality and sample-complexity conditions for
deciding its sign, but no analytic crossover in the number of tasks. This is stated conservatively:
the residue is a measured regime boundary, not a theorem, and RV-8 already records that the lifetime
repayment claim behind #165's H1 is projected rather than observed.

BIO-T6 is also the pattern the brief asked to look for: a result this repository rediscovered
independently in a different substrate before recognising its parent. **No second instance of that
pattern was found among the other fourteen rows.**

### Published negatives, and what each one attacks

These are results whose own authors reported the failure. They are the highest-value payload here,
because they are how the programme avoids re-deriving known dead ends. Full extension text per
negative is in the JSON under `published_negatives[].extension_for_EB_F0_X`.

- **Darwin Godel Machine, authors' own reported objective-hacking incident** — attacks BIO-T1. BIO-T1 and BIO-T15 jointly.
- **Enhanced POET authors on the absence of a progress measure in original POET** — attacks BIO-T3. BIO-T3 and #296 section 12.
- **SkillLearnBench, on learned skills measurably hurting performance** — attacks BIO-T4. BIO-T4's bounded-agent half.
- **SkillFlow, on an unbounded skill library degrading performance without retrieval** — attacks BIO-T4. BIO-T4 jointly with BIO-T6.
- **Tambe, Newell and Rosenbloom on expensive chunks in Soar** — attacks BIO-T6. BIO-T6 directly, and it is the direct symbolic ancestor of this repository's own capital negative.
- **Kennedy and De Jong on unused chunks and learning saturation in Soar** — attacks BIO-T6. BIO-T6 and BIO-T13 jointly.
- **Nowak and Highfield, quoted in Frank 2012: 'The Price equation did not, however, prove as useful as [Price and Hamilton] had hoped. It turned out to be the mathematical equivalent of a tautology. . . . If the Price equation is used instead of an actual model, then the arguments hang in the air like a tantalizing mirage.'** — attacks BIO-T9. BIO-T9's failure mode when grouping is ill-defined.
- **ANIL / 'Rapid Learning or Feature Reuse? Towards Understanding the Effectiveness of MAML'** — attacks BIO-T12. BIO-T12 directly, and it is the canonical published demonstration that a signature mechanism can be inert.
- **Kennedy and De Jong on long-term learning in Soar** — attacks BIO-T13. BIO-T13 directly, in a wholly different substrate.
- **SkillFlow on library growth degrading performance without retrieval** — attacks BIO-T13. BIO-T13 jointly with BIO-T4 and BIO-T6: an unbounded store is not merely useless but actively harmful once retrieval cannot keep the candidate set precise.
- **Darwin Godel Machine, the authors' own objective-hacking incident** — attacks BIO-T15. BIO-T15 in its sharpest form.

### Sources that could not be verified

Recorded so the absence is auditable. Nothing below is quoted, and no number or wording is
attributed to any of it. An honest unreached source is worth more than a plausible reconstruction,
because a fabrication here would propagate into published claims.

| source | row | what was tried |
|---|---|---|
| Price 1970, *Nature* 227:520-521; Price 1972, *Ann. Hum. Genet.* 35:485-490 | BIO-T9 | three mirrors; one returned a 24,559-byte HTML error page with no PDF text layer, two returned 196-byte stubs. Frank 2012 (arXiv, fetched) is used as the verified restatement and is graded as such. |
| Kac 1947, *Bull. AMS* 53:1002-1010 | BIO-T11 | the AMS PDF URL returned a 5,907-byte Cloudflare bot-challenge interstitial. Two independently fetched monographs state the identity under Kac's name. |
| Weinreich, Delaney, DePristo & Hartl, *Science* 312:111-114, 2006 | BIO-T7 | Europe PMC DOI query returned the record with no PMCID and not in EPMC; a Harvard DASH bitstream returned 2,117 bytes. Blount et al. 2008 (PMC, fetched) owns the row instead. |
| Dwork et al., *Science* 349(6248):636-638, 2015 (reusable holdout) | BIO-T15 | an MIT DSpace bitstream URL returned an HTML landing page. The STOC 2015 companion (arXiv, fetched) is the theorem-grade primary used. |
| Taylor et al. 2016, *Artificial Life* 22(3):408-423; Banzhaf et al. 2016, *Theory Biosci.* 135:131-161 | BIO-T3 | two institutional repositories returned HTML error pages; the arXiv identifier tried for Banzhaf resolved to an unrelated paper and was discarded. Named as context only. |
| Steiner 1972, *Group Process and Productivity*; Diehl & Stroebe 1987, *JPSP* 53(3):497-509 | BIO-T8 | no open text located for the book; the article sits behind an APA paywall with no author-hosted copy found. Named as context only. |
| Blackwell 1953; Cover & Thomas Thm 2.8.1; Kaufman et al. 2012 *TKDD* 6(4) | BIO-T4, T5, T15 | not fetched. Each is named as the canonical reference for a statement that is separately verified from another fetched source. |

### Two corrections this pass produced

1. **BIO-T2 is pigeonhole, not Poincare recurrence.** The row's antecedent is a finite *deterministic*
   biosphere, so the faithful statement is that a deterministic map on a finite set is eventually
   periodic. Poincare recurrence needs a measure-preserving transformation on a finite-measure space,
   a different assumption set, and concludes only that almost every point returns near itself. On a
   finite set the pigeonhole argument needs no measure theory and yields the stronger conclusion.
   Citing Poincare here would overstate the machinery and understate the result.

2. **The 'tautology' line about the Price equation is not Frank's.** It is Frank 2012 quoting Nowak
   and Highfield, critics he goes on to answer. It is recorded as theirs. It remains the sharpest
   published statement of BIO-T9's failure mode, because an identity holds for any partition and so
   carries no evidence that a grouping is real.

### Cross-row dependency, recorded rather than filed as a gap

BIO-T5 says *useful* socially acquired information is bounded by what crossed the channel. The data
processing inequality bounds mutual information, not usefulness, and a bounded recipient can acquire
information and be made worse off. That step is owned by BIO-T4's parent, Rogers' paradox, together
with the two skill-library negatives. It is a dependency between rows, not a residue for ORION.

BIO-T1 and BIO-T15 are likewise one condition read in two directions: T1 is the prospective
structural precondition on the write graph, T15 the retrospective consequence when it is violated.
BIO-T2 and BIO-T3 are near-duplicate ceilings differing only in which constraint binds first,
finiteness of the state space or the support of the generator. Both facts are stated here rather
than papered over with separately manufactured parents.

### Where ORION may genuinely add something, stated conservatively

Only one row carries a residue that is not owned, BIO-T6's crossover locus, and even there the
residue is empirical rather than a theorem. Everything else this capsule contributes beyond the
parents is **protocol and study design, not mathematics**, and must be reported that way:

- the non-interference obligation of section 3 as a *checkable precondition on the kernel write
  graph*, asserted before the run and hashed with the checker, rather than a post-hoc leakage audit;
- the constitution `C` held outside every genome and write set, which is what the Darwin Godel
  Machine incident shows is load-bearing;
- the CONTINUED / RESET / matched-parent design with exact inherited-object knockouts, which
  *supplies* the identifying variation Imai et al. prove observation alone cannot;
- the partial transfer operator returning `CANNOT_TRANSLATE` or `CANNOT_VERIFY`, an engineering
  contract on top of institution-theoretic preservation.

None of these is a theorem. Claiming any of them as one would be the defect this appendix exists
to prevent.
