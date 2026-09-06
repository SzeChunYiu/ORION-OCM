# Actual G1 applicability: no eligible zero-incident block

At the original restore.max3.01 pre-solve snapshot, both exact WARRANTED and
EXPLORATORY kernels have 78 atoms and 146 nonzero entries. Neither contains a
zero-incident atom. Their intersection is empty; the decoder's eligible solve
dimension remains 78. This snapshot does not justify integrating the zero-incident
compact route from PR99 into the G1 vessel.

Scope: one historical snapshot and its actual current revocation. This is neither
a claim that other compression is impossible nor a performance comparison.
No spectator atoms, new revision family, model inference, synthesis, executable
operator or SV solve was invoked. No new routing implementation was built.

Read RESULT.json for exact task/config/revocation/seed, global-work counts and
resource scope; kernels.json and atoms.json retain the exact inspected values.
Source commit is 1509d23217a43e4024b442f66b242316bc877e55.
The target is QUERY_OPENED event 385, after reducing events 1–384, with pre-solve
state expectation d83d7ac9a171e4ea123b5dfc213d8cc82f34cde3469b852a57d3bd78bf3d5705.
This N=78 field is not the later N=86 profiling snapshot.

The original per-atom warranted, exploratory and background outputs/identities
remain required; global uniform seed is 1/78. Current warrant measurability adds
no eligible block because there are no zero-incident candidates. No new theory
or general nonzero-incident reconstruction theorem was claimed.

Global inspection work was charged: 502 ledger rows and 429 event hashes checked,
384 reducer applications, 385 expectation checks, two dense kernels with 12,168
cells materialized/inspected, 78 atom metadata records, and two checks of 180
frozen source files. The 77 support/closure reconstruction calls' supplied input
sizes are reported as input-size sums, not actual visited-node counts.
The single inspection used 0.593391 s descriptive wall and 0.587254 s self user
CPU; raw launch/exit records remain. These are not candidate/baseline timings.

An initial inspector incorrectly assumed one-based outer ledger rows and stopped
before reducer/kernel work. first-inspector/ preserves its exact code/error/exit1.
The correction adopted the frozen LedgerStore.entries() verifier, without editing
core source or records. The corrected launch exited0; its PID190266 was reaped.
All original source/input hashes remained unchanged.

Reconstruction uses already published raw data, not another model download:
../clia-reuse-study-result-20260906/raw/model-less-raw.tar.gz, SHA256
3ffdecf1200cc1bfe192478ce48b341eb8618bf8be0e2051a5d8a6429bc198a5.
Extract its v3/run/source/ into a NEW scratch source/ directory, and the five
PLAN.inputs files under v3/run/ into scratch input/ with the same relative paths.
Copy PLAN.json and inspect_field.py to that new scratch root; do not copy existing
RESULT/kernels/atoms outputs because writes are create-only. Verify every PLAN
input hash and all input/F0.source_files hashes. Use the supported Python recorded
in corrected-launch.json with scratch as cwd, never an unrelated system3.8.
The source/input archive contains everything needed; model binaries are unused.
Historical absolute paths remain custody metadata, not instructions to overwrite.

Ownership: #72 applicability / #70 representation; supports #50/#62 only as bounded
infrastructure evidence. Classification: SUPPORTING / NEGATIVE_RESULT for this
decoder premise. Next mechanism work must address actual nonzero-incident data
and full-output requirements under the existing owner, not extend this toy panel.
