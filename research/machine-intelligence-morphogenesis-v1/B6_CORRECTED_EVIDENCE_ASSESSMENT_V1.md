# B6 corrected evidence assessment V1

**Result: incomplete evidence; no D-table verdict changes on the available raw data.**
Assessment date: 2026-09-13. This is an adjudication replay and custody record,
not new empirical search, training, or a genotype-validation rerun.
The source-level correction is [B6_ADJUDICATION_CORRECTION_V1.md](B6_ADJUDICATION_CORRECTION_V1.md).

## Data and authority

The input source was the extracted, non-Git lane
`/home/billy/gmi-work/lanes/b6dev-billy/research/machine-intelligence-morphogenesis-v1/microscopes/results/`.
A stable copy was made on laptop billy at **2026-09-13 10:46:11–10:46:12 UTC**:

`/home/billy/ocm-verify/work/b6-corrected-adjudication/snapshot-20260913T104611Z`.

The snapshot contains **24 JSON files, totaling 16,467,840 bytes: 9 arm receipts, 11 source receipts,
2 saved adjudication/validation outputs, and 2 saved control reports**.
These are not 24 completed arms. The registered driver requires 24 physical arm files;
DISJ/RESET reuses CROSS/RESET, yielding 27 analysis labels. Fifteen physical arm
files and seventeen analysis labels were absent from this snapshot.
This assessment concerns this named lane and time, not every host or later receipt.

The original D registration is commit
`5378c2b7f91f8fbc567764a2ee0c5ff6e256e814`.
The historical scorer is pinned to imported main
`9f35356ed8e07d4b64c01431925c8278a198f288`.
The lane's driver, development module, and old adjudicator exactly match that commit.
Its local freeze has the same first 179 lines and lacks the later Z appendices;
authority for those appendices comes from the pinned Git record, not that local copy.
Z1–Z4 were registered after seven observed arms, Z5 after nine. Observations
already in hand are retrospective inputs, not outcome-blind tests of those predictions.

The 20 arm/source internal receipt digests all match the source's canonical
JSON hashing rule. All seven warm-arm source digest references match the copied
billy source receipts. Eleven corresponding old-host source files have identical
non-timing scientific content; their differences are host, receipt digest,
elapsed time, and four history timing fields. This consistency does not establish
independent replication or authenticate the historical execution environment.
Hashes establish byte identity and internal consistency, not external attestation.

## Replay and changes

Both scorers ran with CPython 3.12 on laptop billy, against links to snapshot
arm copies in separate `historical/` and `corrected/` directories.
No live source, raw receipt, frozen output, or search process was modified.
Every original input hash was rechecked after replay and witness lookup.

| Quantity | Historical scorer / saved output | Corrected scorer |
|---|---|---|
| D terminal | ADJUDICATION_INCOMPLETE__UNITS_MISSING | Same |
| D1a, D1b, D1s, D2a–D2d, D3a, D3b, D4 | PENDING_MORE_UNITS | Same |
| D5 | HELD | Same |
| Z1 | HELD from two recorded hits | Same; campaign incomplete |
| Z2, Z3, Z5 | PENDING_MORE_UNITS | Same |
| Receipt files / proven duplicate computation | 9 / 1 pair | Same |
| Distinct experiment count | 8 | Unresolved; provisional count after proven deduplication = 8 |

The historical replay reproduces the **saved old adjudication bytes exactly**.
The corrected provisional count removes the proven CROSS/TWIN S0 ≡ DISJ/TWIN S0
duplicate, and retains the documented RESET shared-file alias.
Its exact distinct count is withheld because two RESET records lack seed fingerprints.
This reports an identity-certification limitation, not evidence of extra duplicates
or withdrawal of any measured arm result. The targets of those RESET records differ.

The same three distinct recorded first DENSE recoveries retain founder carriers
PROGRAM, KVSTORE, and TABLE; none has unknown or conflicting founder metadata.
The corrected Z5 representation combines the proven twin alias and separates a
statement about recorded first recoveries from the frozen universal statement
about every recovered candidate. The available first-recovery records cannot
certify that universal statement.

## What the recovery records actually support

All nine available arms used 20,000 search evaluations. The three distinct
positive DENSE records are:

| Recorded first recovery | Target | Search placement | Verification cost | Sum |
|---|---|---:|---:|---:|
| SAME/CONTINUED S0; PROGRAM founder 39 | E_smooth3 | 18,595 | 19,648 | 38,243 |
| SAME/CONTINUED S1; KVSTORE founder 38 | E_smooth3 | 3,827 | 3,500 | 7,327 |
| CROSS/TWIN S0 ≡ DISJ/TWIN S0; TABLE founder 20 | E_sym5 | 18,630 | 1,306 | 19,936 |

Each record reports `carrier_atrophied=DENSE` and `min_over_six=0.8542`.
SAME/RESET S0 and SAME/TWIN S0 report no such recovery in their search window.
There are therefore **two** reported recoveries on E_smooth3 and **one**
distinct recovery on E_sym5. PR #540 at
`9e47d4109aa786fc39fe4cd9bc642c14c167c211` incorrectly locates all three
on E_smooth3 in §4 of its reachability-scope note.

Search placement 3,827 for SAME/CONTINUED S1 is a correctly identified replay
target; its reported search-plus-verification burden is 7,327.
“Recovered within 20,000 search evaluations” must not be rewritten as
“complete recovery cost at most 20,000”: SAME/CONTINUED S0 already costs 38,243.
Source acquisition is also excluded from these target-stage sums by the original
instrument. They are not complete lifetime costs.

The same target search function receives different initial populations, with
CONTINUED/TWIN matched in size and carrier histogram. The observed differences
are finite-seed, finite-window recovery outcomes. They do not identify the full
reachable Pareto frontier, establish zero cold-start reachability, estimate a
population success probability, or measure the abstract DU-1 theorem.
The theoretical correction is developed separately in the reachability-evidence
correction; no packet verdict changes follow from this replay.

## Witness availability and next decisive measurement

The first-DENSE summaries omit raw and atrophied genotypes, full control results,
and the rule-40 margin. The source verifier computes these quantities, but its
class-specific recorder discards them. The three raw fingerprints remain in
`trace_compact`. A recursive search over every saved genotype/fingerprint pair
in all 24 snapshot JSON files found **663 unique persisted fingerprints** and
no genotype matching any of these three first-DENSE fingerprints.
This scoped search does not assert that no copy exists outside this snapshot.

Consequently this assessment verifies recorded reports, not independently
re-exhibited admissible DENSE witnesses. A separately registered deterministic
replay retaining the SAME/CONTINUED S1 genotype and full verifier output is a
concrete next measurement. It should preserve the old receipts, bind the source
archive and search code, and charge all costs. No such replay was run here.
Neither a single witness nor a completed three-seed campaign would establish
unrestricted family coverage or global theory completion.

## Reproduction bindings

All paths below are relative to the snapshot directory above. The manifest binds
each of the 24 original filenames, lengths, hashes, and source modification times.

| Artifact | SHA-256 |
|---|---|
| `manifest.json` | `be8a549b0562561f48f1d47f1918609aa48157dd35149c4e79afd451d4f49fe2` |
| `corrected_b6_adjudicate.py` | `590b999cfbe89aa4bc391fd00d575aafa90d2d2a694b5748abd4f6844da498eb` |
| `historical_b6_adjudicate.py` | `1bb863dd0f77460824930f8316e32d4ad11d913caf6a23b38e103b9dac150419` |
| `corrected/STAGE_B6_DEV_ADJUDICATION_V2_billy.json` | `53eac49de90f2c74bb1c978e8d470426560ebe8c3e7849b8c613bf8b9f9c6196` |
| `historical/STAGE_B6_DEV_ADJUDICATION_billy.json` | `f07bb3755c362f3b2dadf883293573617c87cf70d15301bedd158995811ebc2b` |
| `evidence_validation.json` | `b5ddf45e8674e5d55df8c4af7bae3bba0523fe71f9a2b9ab9309843134784f42` |
| `saved_witness_search.json` | `b34be704147207d38208e1cef6ed62f481c45226a5aabb1fed390cf7509cc174` |

The selected adjudication inputs are now preserved in the portable
[evidence packet](evidence/b6-corrected-20260913/README.md): nine exact arm files,
five referenced source receipts, authority documents, the exact corrected source,
and both old/new outputs. Its 14 raw inputs total 15,951,708 bytes.
Two independent searches found no raw STAGE_B6_DEV JSON paths in locally reachable
Git history before this packet; unfetched remote objects were outside that search.

Portable replay matches all JSON except the directory prefixes of two explicit
identity-unknown file locators; the frozen output bytes remain unchanged.
An independent copy with one appended input newline was rejected before scoring.
[REPLAY_VALIDATION.json](evidence/b6-corrected-20260913/REPLAY_VALIDATION.json)
records the successful real-data replay and that integrity control.
The packet MANIFEST.json SHA-256 is
`a5dc56295fc3cc3438e6e26ef7717ea99774de7f27b5e4ac1600103a28520a3a`.
The original full snapshot remains the custody source for additional historical
control reports; this packet licenses scorer replay, not missing-witness replay.
