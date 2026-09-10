# RV-A corrections

Corrections are recorded here with the original text retained visibly. A silent
rewrite would leave no way to tell a corrected number from one that was always
right.

---

## C1 (2026-09-10) — compute share was 4.7%, is 2.13%

**Found by:** review from the team lead, against the study's own receipts.

**What was wrong.** Three places stated the compute share as **4.7%**:
`RESULT.md` line 65, `RESULT.md` line 120, and `CORE.md` line 116. The receipts
give:

```
L1        cpu_hours = 0.0236825
GS-R2     cpu_hours = 1.113682
share  0.0236825 / 1.113682 = 0.021265  ->  2.13%
reduction 1.113682 / 0.0236825 = 47.03x
```

The **47× compute reduction was transposed into a percentage.** The study's own
per-CPU-hour figure proves it independently: the hold-count ratio divided by the
compute share must equal the per-CPU-hour ratio, and 2.2101 / 0.021265 = 103.93,
which is the 104× already reported. At a 4.7% share the campaign's CPU-hours
would have to be 0.5039, not 1.1137, and the per-CPU-hour ratio would be ~47×.

**Original text, retained.**

> RESULT.md:65 — "i.e. **4.7%** of the campaign's compute. Per CPU-hour the
> ratio is **104×**."
>
> RESULT.md:120 — "the absolute hold count rises 2.21× over the whole campaign
> at 4.7% of its cost."
>
> CORE.md:116 — "**2.21× the absolute hold count of the entire campaign, at 4.7%
> of its compute** (104× per CPU-hour)."

**Direction of the error.** It **understated** the result. 2.13% is better than
4.7%, so nothing downstream was inflated and no conclusion changes.

**What carries the uncorrectable original.** The PR #293 title and the squash
merge commit `bebe864c9f96fd7a82944d66738fa8cd2b674e5c` on `main` both say
"4.7% of the compute". Commit messages and merged PR titles cannot be amended
after the fact, so they stand with the wrong figure and this record is the
correction of record for them.

**Defect-class check, not just the reported instance.** Fixing only the number
that was reported would leave the class unchecked, so every quantitative claim
in the study's prose was re-derived from the receipts:
`results/RVA_NUMBER_AUDIT.json`, produced by `hpc/rva_numaudit.py`.

| | |
|---|---|
| checks | 17 |
| failing | **1** (this one) |
| no-alarm case asserted | 16 |

The 16 that pass include the hold ratio 2.21×, the per-CPU-hour ratio 104×, both
parent ratios (1.36× and 4.92×), the lever-package ratio 3.82×, the null ratio
5.44×, the gate odds 27.7×, the tier cost ratio 4.60, the `allocation_score`
cost 8.04 T0-units, the halving saving 4.8 T0-units, and every rate and fraction
quoted. So the transposition was a single isolated slip, not a systematic one.
