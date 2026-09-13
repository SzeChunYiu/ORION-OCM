# B6 S1 retrospective witness recovery protocol V1

Prepared 2026-09-13. Purpose: retain and independently recheck one missing
SAME/CONTINUED S1 candidate. This is retrospective recovery, not a prospective
prediction, an independent population replication, or frontier exhaustion.
The existing B6 custody packet and all historical outputs remain unchanged.

## Authority and strongest matched method

The parent is the original B6 experiment itself: its unmodified B1 search,
warm-population selection and six-intervention verifier at
commit 5378c2b7f91f8fbc567764a2ee0c5ff6e256e814. Capture is instrumentation,
not a new acquisition or morphogenesis mechanism. Matching this registered
instrument is the relevant comparison; later intervention versions are not
silently substituted. Core method and result authority remain separate.

RECOVERY_BINDINGS_V1.json binds the driver, original D freeze, all 12 modules
in the recursively inspected relative-import closure, the package initializer,
and the two packet receipts used for population reconstruction. All 13 Python
module files match the extracted historical lane byte-for-byte at preparation.
The newer 9f35356e ecology adds a seventh intervention, and its morphgen changes
generator guards; that revision is unsuitable for replaying the six-check cost.

The historical driver log records a CPython 3.11 executable path. Its historical
patch version and binary digest were not recorded. That path currently runs
3.11.14. Prefer it on laptop billy and record its present version/binary digest.
No claim of an authenticated historical execution environment follows.

## Exact recording failure

b1.search retains every standard-theta-crossing raw genotype in its in-memory
trace (b1.py lines 95--98). It records only the founder index as origin; it does
not persist individual mutation choices, intermediate archives or RNG states.
Crossover uses a second parent but retains only the primary parent's origin.
Founder38 therefore identifies a primary-lineage root, not complete ancestry
or proof that no DENSE ancestor contributed.
b6_development.first_of_class calls verify_candidate, then copies only a short
summary into its successful return (lines 218--221 at the pinned commit).
This discards the raw genotype, atrophied genotype, six per-control capabilities,
rule-40 margins and other returned verification fields.
run_arm then serializes trace_compact without genotypes (lines 272--273).
Final-best genotypes retain later archive winners, not every earlier witness.

The saved target row is trace index 2156, search evaluation 3827, raw fingerprint
f88fb0cbce639d7a578b9e254ae13b777a025df719dad0461e7a5133b59eb9dd,
founder ["seed",38]. The class scan reports 464 candidates and 3500 verification
evaluations, hence its reported sum is 7327. No matching saved genotype was
found in the custody packet's 24-file snapshot search.

The compact trace does not identify subthreshold archive insertions or the
full mutation/RNG trajectory. Founder 38 alone cannot reconstruct descendant
2156. Recreating the search requires evaluating its intervening candidates.
No record-supported evaluation-free reconstruction has been identified.

## Input reconstruction and identity gates

The target receipt records the ordered 61 seed fingerprints, capabilities and
carrier labels. Every genotype is present in its bound E_smooth1 S1 source
archive. Preparation reconstructs this exact order and binds the serialized
population; runtime rechecks all canonical fingerprints before search.
The original matching TWIN source is not needed to regenerate these already
recorded choices. Its historical acquisition cost remains disclosed.

Use only source-pinned modules and target specification E_smooth3. A short
128-evaluation prefix is a low-cost divergence check; compare every available
compact trace row including evaluation index, capability, descriptor, size,
origin and fingerprint. A mismatch refutes historical prefix identity.
A matching prefix does not prove identity of the unseen continuation or of the
historical environment. Record either outcome without deleting observations.

Then run the unmodified search through the registered recovery placement 3827,
with raw trace persistence enabled. The evaluation-count argument only bounds
the original loop; it does not change its proposals, archive rules or RNG draws.
This is a separately declared bounded retrospective run. If no admissible
witness appears, report that result and diagnose before extending the horizon.
Do not tune a candidate, threshold, seed or intervention to force a match.

## Capture mechanism and direct validation

TraceCapture adds JSONL persistence to the existing trace.append interface.
VerifierCapture calls each original evaluator/verifier/pruner exactly once,
returns its original value, and stores the successful raw genotype, full
verdict, atrophied genotype, complete atrophy information and actual evaluation
outputs. It restores the instrumented functions on exit. It draws no randomness
and does not alter a predicate or decision. Added storage, copying and timing
overhead are measured as replay instrumentation, not claimed to be free.
Total timers span run-function entry through receipt construction; interpreter
startup and final receipt writing remain outside those reported subtotals.

The historical class scan first filters RAW carrier DENSE, then asks whether
the atrophied carrier is DENSE and the controls pass. Thus "first" means first
under this particular raw prefilter; it is not a census of every graph that
could become DENSE after atrophy. Greedy atrophy also does not establish
globally minimal structure or a population-level causal mechanism.

After capture, launch verify_witness.py in a fresh process. It directly runs
all six controls and five probe targets on both raw and atrophied genotypes:
22 additional ecology calls. It checks genotype fingerprints, raw capabilities,
atrophied minimum, rule-36 threshold, rule-40 margin and distinct served answers.
Errors cannot masquerade as distinct probe answers. This independently composes
the checks and reexecutes them, while sharing the pinned primitive evaluator;
it is not an independent VM implementation. Retain all returned traces.

Do not mix this bar with later leak-free/control families. The historical
extra_unseen_feedback condition exposes half its scored unseen inputs, as the
freeze already discloses. Any current-bar assessment requires a separately
named protocol and additional costs, with neither result replacing the other.

## Cost and scheduling estimate

Historical S1 search: 20,000 evaluations, 518,124 charged proposal tries,
5028.4 seconds; verification of both scans: 390.2 seconds.
Search checkpoint 5000 took 1299.0 seconds. Linear timing extrapolation gives
about 962--994 seconds for search through 3827, not a guaranteed runtime.
Adding the entire historical verification duration gives about 22.5--23.1
minutes as a planning estimate. A full 20,000 replay would be about 90.3 minutes.
CPU contention, canonicalization and instrumentation can change these times.

The original first-any scan separately charged 352 verification evaluations.
The 7327 class-specific sum excludes that scan, all search after 3827,
extractor calibration, historical source acquisition and physical/controller
costs. The actual full target execution therefore charged at least
20000+3500+352=23852 search/verification evaluations, plus calibration.
Source E_smooth1 and the matching E_twin1 each used 20,000 evaluations,
with reported durations 2220.0 and 1873.8 seconds. They are reused inputs,
not newly free discoveries. Do not sum evaluations as if all calls cost equal
CPU work: record wall time, CPU time, proposal tries and calls separately.

Run a single process on laptop billy, after the integration gates permit it.
Preparation and focused capture tests perform no search. The explicit
--run-search switch is required to execute a replay. Old receipts are never
overwritten; each preparation, run and verification destination must be new.

## Commands and stop condition

1. prepare_recovery.py --repository REPO --packet B6_PACKET --output NEW_PREPARED
2. recover_witness.py --prepared NEW_PREPARED --output NEW_PREFIX --evaluations 128 --run-search
3. recover_witness.py --prepared NEW_PREPARED --output NEW_RECOVERY --evaluations 3827 --run-search
4. verify_witness.py --prepared NEW_PREPARED --witness NEW_RECOVERY/witness.json --output NEW_VERIFICATION.json

Use the recorded available Python 3.11 interpreter for steps 2--4.
Charge the short-prefix run too; it is additional work, not subtracted by reuse.
Stop once a captured witness passes the fresh-process checks. A different
fingerprint is a corrected historical identity, not by itself a failure of
witness existence. If verification fails, retain it, attribute the failing
stage and attempt a matched repair before making an admissibility claim.
