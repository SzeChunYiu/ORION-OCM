# Initial run and correction checkpoint

## Native run actually observed

GitHub Actions run `34263102842`, job `102185696663`, succeeded. The job was associated with PR161 head `a25b39c88ca004fca290dff9b8b10f71f404757d`, but checkout was the test merge `8fed51538b5993c0d8bcae1cc58e2719fadbae04` with base `e1ea10429dd2490488e07b9739428d0ea3b6b414`. It must not be described as a pure head checkout. The revised workflow now explicitly checks out the PR head and records `checkout-sha.txt`.

The observed initial result was:

```json
{"grammar_programs":341,"distinct_targets":206,"excluded_training_validation_targets":4,"exposed_transfer_targets":202,"kernel_parent_equal_rows":202,"lifecycle_observations":14,"learned_fragments":[["inc","square"]],"protected_holdout":false,"terminal":"NATIVE_KERNEL_PARENT_EQUIVALENT__ARCHITECTURE_BENEFIT_UNESTABLISHED"}
```

This complete through-length-four grammar is a 206-target population, NOT the earlier R0B 142-target population. Do not transplant counts, rates or oracle bounds between them. The two training and two validation identities are excluded from the 202 paired queries. The native generator was actually persisted and loaded after restart before these queries. Liveness observations cover three support withdrawals, reinstatements, associated restarts, and snapshot restart.

Initial normal and optimized Python 3.11.14 runs each passed 26 tests. Artifact `10070685919` contains native JSON and logs; its ZIP SHA256 is `c721c00f00be02a1a074abd9a380f269c5b7c1f427b3c7e33cd294a789fc1746`. Artifact existence does not establish architecture benefit.

## Retained RED to GREEN correction

After that green run, an additional local check supplied exact rational strings in a manually constructed certificate. `verify` accepted them, but `path_bound` used the unnormalized prices/rate and raised TypeError. The additional case reproduced one error in the existing 26-test suite. The helper now normalizes those inputs consistently and the normal/optimized local runs pass again. The case remains inside `test_exact_numeric_validation`; this is an implementation correction, not a changed theorem or new performance result. The previous code remains in Git history at the head above.

Read the successor exact-head Actions artifact before attributing the corrected-source run. Do not infer success from this checkpoint. Next work remains the full persistent matched parent and concrete relative-cost/semantic bridge in README G1/G2. No production or protected-evaluation authorization is added.
