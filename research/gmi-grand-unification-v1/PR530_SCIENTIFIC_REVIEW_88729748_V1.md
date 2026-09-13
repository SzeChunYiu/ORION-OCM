# PR 530 scientific review — pinned findings and repair register

Date: 2026-09-13. Scientific correctness only; no empirical reruns.
Primary reviewed head: 88729748789913017968924f6c669dbb130a3819.
Addendum reviewed delta: bc4dc228bc38bf293c6b5927ff60598b98b11e47.
[PR 530](https://github.com/SzeChunYiu/ORION-OCM/pull/530) is moving; these
claims concern those commits, not every future version. The addendum changes
only Z5 lineage scoring and its guards; the original regions below persist.

## Authority and executable scope

[B6 scorer at 88729748](https://github.com/SzeChunYiu/ORION-OCM/blob/88729748789913017968924f6c669dbb130a3819/research/machine-intelligence-morphogenesis-v1/gmi_microscope/b6_adjudicate.py)
claims to score the frozen D1a--D5 predictions exactly.
Its named B6 freeze, developmental runner and experimental receipt set are
not tracked at that reviewed head. The authoritative historical freeze
was recovered and inspected at full commit
5378c2b7f91f8fbc567764a2ee0c5ff6e256e814, path
research/machine-intelligence-morphogenesis-v1/GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md.
An abbreviation of that SHA resolves differently on another checkout;
the full object identity matters. Import/bind the authority before adjudication,
or explicitly document a versioned successor; filename claims are insufficient.

The historical experiment charges source development to the previous generation
and retains a disclosed leaky intervention. It can support a conditional
marginal target-search comparison. It cannot alone establish lower complete
lifetime acquisition cost, leakage-free transfer or a general developmental law.
Those are original scope boundaries, not newly introduced PR regressions.

## Findings requiring scientific or scoring correction

**R1 — positive B6 terminal bypasses D1a.** Scorer lines 337--343 permit
OBSERVED when D1a fails on two seeds but D1b holds. The frozen terminal
requires both D1a and D1b. A separate all-three-seed kill condition does not
license a positive when D1a fails on two; later parent-subtraction prose
does not state such permission either. Finite SAME witness:
CONTINUED=(2,2,2), RESET=(1,1,4), TWIN=(3,3,3).
The scorer returns D1a=FAILED, D1b=HELD, complete=true, OBSERVED.
Repair: derive the terminal truth table from a bound authority, require every
load-bearing positive premise, and retain unresolved cases explicitly.

**R2 — D2a interchanges two quantifiers.** Lines 129--137 take a majority of
per-seed conjunctions; the freeze requires a conjunction of two majorities.
Let earlier CONTINUED seeds be {0,1} and memory-carrier seeds {1,2}.
Both frozen predicates pass, but their intersection has size one and the
scorer reports FAILED. Repair: tally the predicates separately, then conjoin
their three-valued aggregate judgments; do not require coincident seeds.

**R3 — partial RESET spread can create a false failure.** Lines 187--195
compute D3a's spread from available non-null RESET values before all three
are known. RESET values 100,101 yield spread 1; two DISJ CONTINUED/TWIN
differences of 10 produce FAILED. Completing RESET with 200 yields spread
100 and HELD for the same already-read comparisons.
Repair: defer final comparisons until the spread-defining register is known,
or certify the verdict over every admitted completion. Missing data are not
a fixed small spread; an early positive may be safe under monotone widening,
whereas the demonstrated early negative is not.

**R4 — absent identity evidence is treated as duplicate identity.** Lines
48--51 hash absent seed fingerprints as an empty list; lines 250--260
then group missing target and fingerprints as a shared computation.
Distinct SAME/TWIN and CROSS/TWIN files lacking those fields, with different
B_morph values 1 and 2, are counted as one experiment using hash
4f53cda18c2baa0c and target=null.
Repair: validate experiment identity/provenance before deduplication. Unknown
identity must remain unknown; known equality and a missing record are different.

**R5 — interval survivors do not establish measured coexistence.** RV377210
freeze line 231 and X3 conflate an unresolved interval frontier with a
zero-width mixed frontier. Take XOR costs (88,[1,3],[1,3]) and NN costs
(312,[2,4],[2,4]); other candidates can have larger costs.
At timings XOR=(1,1), NN=(2,2), only XOR survives. At XOR=(3,3),
NN=(2,2), both survive. Both worlds fit the same interval evidence.
Repair supplied by EFI-1--3: report possible/necessary membership and
the set of feasible family-support patterns, retaining underidentification.

**R6 — the named neural-only timing falsifier is unreachable.** RV377210
freeze lines 238--243 admits neural-only as a falsifier while fixing
opcode costs XOR=88, lookup=136, sumNN=312 and oldNN=472.
XOR is the unique strict opcode minimum; it survives every valid timing
world under the registered three-coordinate Pareto rule. Direct enumeration
of 6,561 timing worlds retains XOR throughout, including 3,609 mixed fronts.
One-coordinate superiority does not establish exclusion of all rivals.
Repair supplied by EFI-2/4: design feasible discriminating timing predictions,
with explicit transport assumptions, rather than a structurally excluded event.

**R7 — the recorded pre-data chronology is false on available timestamps.**
The RV377210 freeze says it was registered before the other lane's V4
timing existed. On 2026-09-13 UTC:
- [V4 run 34749100254](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34749100254),
  source d6147f95e48b2e4e4afc2c3bd1dee8551527c2fc, job 103702229052,
  executed the committed V4 schedule at 09:13:48--09:13:53.
- Its artifact 10315471553, grand-gmi-parity3-point-v4, was created at 09:13:54.
- [Registration commit d83d789f](https://github.com/SzeChunYiu/ORION-OCM/commit/d83d789fa655d14526bc0cdcf0e34ef043a45cfe)
  has both author and committer time 09:23:06.
This proves artifact existence preceded that commit; it does not prove
the author inspected results. Repair: retain exact chronology, seek an
authenticated earlier specification if one exists, distinguish independently
supported outcome blindness from pre-data registration, and use a future
run for fresh prospective testing. Do not backdate or rewrite a freeze.

**R8 — Z5 universal founder claim drops unknown founders (bc4dc228 addendum).**
[New scorer](https://github.com/SzeChunYiu/ORION-OCM/blob/bc4dc228bc38bf293c6b5927ff60598b98b11e47/research/machine-intelligence-morphogenesis-v1/gmi_microscope/b6_adjudicate.py)
skips every recovered DENSE receipt without a known dense_root_carrier.
With 24 distinct arm receipt files all reporting a DENSE recovery, only
one warm arm carrying origin=["seed",0] and seed_carriers_raw=["TABLE"],
and 17 other warm-arm files lacking DENSE origins (plus six RESET files),
it returns complete=true, Z5=HELD, n_distinct_recoveries=1. The missing
warm-arm provenance is a universal-positive evidence gap even when cold
RESET arms are excluded from the claim.
Repair: enumerate applicable recoveries before testing provenance, retain
unknown roots in the denominator, and require every applicable root to be
known and non-DENSE before HELD. A known DENSE founder can falsify early.
Specify whether the quantifier concerns first recovered machines per arm
or every recovered machine; first-only receipts certify only the former.

## Reproduction and integration boundaries

The finite logic witnesses ran on laptop billy, never the Mac. R8 and the EFI
unit use CPython 3.12 explicitly. R1--R4 were reproduced against 88729748;
the intervening bc4dc228 delta leaves those logic expressions unchanged.
Scratch records are under work/pr530-science-review-0e2a1f, including
findings.json, findings-current-88729748.json and findings-z5-bc4dc228.json.
Their compact inputs and expected distinctions above are the portable
regression specifications; scratch files are not immutable empirical receipts.
The committed EFI checker/tests independently retain R5/R6 as exact controls.
R1--R4/R7/R8 remain explicit repair tasks for the B6/registration owner;
this module does not silently change the PR's frozen experiment.
