# Native development evidence

This is an exposed, assistant-authored engineering development record. It supports a
reusable allowed-environment boundary; it establishes no learned method, held-out F1
reconstruction, FLT result, scaling result or OCM novelty. Final isolated commissioning
is a separate qualification and is not certified by these development calls.

## Parents and reviewed source

Lean 4.33.1 supplies fresh kernel environments, declaration checking and `Environment.replay`.
Its recorded githash is `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`.
`leanprover/lean4export@15f6055e299ad5b89345e533cc2192f4cc00f659` supplies the
NDJSON format, expression interning, serializer and parser.
`leanprover/comparator@3927ad383f208ae977c340a91c48ac9b497d2097` supplies the full
`ConstantInfo` comparison instances and the kernel-primitive comparison precedent.
These are absorbed parent mechanisms, not new OCM theorem-checking algorithms.
[Parent custody](parents/SOURCE.json), SHA256
`9ebca45283f7462f267f26adcac4924ca6daea10ffd2de22312ad108f1cf58b9`, binds their retained files.

The v4 handoff below binds all 12 native modules and identifies the generic executable
as SHA256 `1cf7eca5b692a2783fb95b7256b9836f2c0ab080b33463e86eba0cacfed19fe4`.
A read-only review rehashed those modules and found all equal to the handoff.
The final commissioning must independently bind its own executable, inputs and process boundary.

## Corrections and their evidence

**Parent normalization.** Initial preparation refused `Nat.beq.match_1`, then
`_private.Init.Prelude.0.Nat.pred_le_pred.match_1_1`. The two retained comparisons report
full parent-record equality and type/value alpha equality, while exact type equality is false.
The diffs show binder hygiene names and, in the second comparison, implicit/default annotations.
The annotation-only control also failed under the overly strict comparison.
[Types.lean](OCMEnvironment/Types.lean) now uses the parent's full-record `BEq`, with its
explicit alpha-interning normalization version; it does not promise source binder-interface equality.
Declaration names, ordered universe parameters, bodies and other declaration fields remain compared.
Raw packet hashes remain independent custody identities. `Config.restorePolicy` rejects another
normalization version; candidate insertion uses the registered target expression and checks the
actual stored theorem's type, value and ordered universes afterward.

**Checked-map export.** `rich-cases-v1-defined-prepare` exited zero and printed `PREPARED`,
but stderr contains exporter panics such as “Constant Eq not found in environment.”
Its permitted packet contains only the metadata header. The cold check returned
`CANNOT_CHECK` at registration (`UNKNOWN_OR_AMBIGUOUS_NAME Eq`): the earlier preparation
claim was not usable. Source inspection attributes this to the parent exporter's frontend
`Environment.find?` lookup on an environment reconstructed from the checked kernel map.
[CheckedExport](parents/checked-export/CheckedExport.lean) mechanically preserves the parent
body while changing exactly three environment annotations to `Kernel.Environment`, within a
separate namespace. The parent files stay unchanged. The transformation was independently
reconstructed and compared byte-for-byte; [ADAPTATION.json](parents/checked-export/ADAPTATION.json)
binds adapter SHA256 `10664601321cc22b93975a496d6bab12370a6d6228d6f51e67b3f2c1aee78bdc`
and parent SHA256 `1c60d571dc24bfb99e7cbb218d8d489919bbc871238f6db9c76248521fbea998`.
[Write.lean](OCMEnvironment/Write.lean) also reparses output and requires full checked membership
and record identity before `PREPARED`; target expression, name and universe-list roundtrips are checked.

**Axiom registry and cold restore.** Review-led corrections in
[Prepare.lean](OCMEnvironment/Prepare.lean), [Registry.lean](OCMEnvironment/Registry.lean) and
[Main.lean](OCMEnvironment/Main.lean) require independently registered full axiom headers and
reached kernel-primitive identities. A policy name alone is insufficient authority.
Preparation validates the full allowed axiom set, then persists only authorized axioms reached by
the selected environment. The original policy remains bound in preparation inputs.
The v4 matrix confirms missing registry coverage refuses, changed axiom headers and unallowed
opaque support refuse, an authorized opaque route reports `Fixture.evidence`, and an unused
independently registered allowlist entry permits cold checking with an empty actual axiom list.
These are current controls, not a claimed empirical red-to-green history of forged admission.
[Check.lean](OCMEnvironment/Check.lean) repeats the closure audit on the actual inserted theorem.

**Resource-control correction.** `resource-diagnostic-run` exited one because its test assertion
expected exhaustion, while the recorded native result was `KERNEL_PASS`. That attempt did not
reproduce a resource-misclassification bug and must not be counted as such evidence.
The replacement [KernelTests](fixtures/KernelTests.lean) uses 2,000 typed identity applications,
checks their valid baseline, and then checks a constrained execution. Its recorded result is
`CANNOT_CHECK / kernel_resource / DETERMINISTIC_TIMEOUT`.
The v4 matrix separately records the same candidate packet passing under the ordinary envelope
and returning that terminal under the constrained envelope. Source classification also maps
memory, recursion and interruption exceptions to `CANNOT_CHECK`; those branches are not all
claimed experimentally exercised here. A policy refusal does not assert theorem unprovability.

## Final development controls

Six native unit executables recorded exit zero, empty stderr and 45 reported controls:
8 dependency, 7 kernel, 8 normalization, 7 outcome, 10 packet and 5 registry controls.
The v4 matrix contains 29 prepare calls and 19 check calls, including expected refusals.
Read-only inspection verified all 48 referenced process-record hashes, recorded exit codes,
empty stderr, and parsed stdout equality with the matrix's recorded results.
This does not upgrade these direct development launches to final isolated commissioning.

Positive fixtures cover composition, polymorphism, definitions, opaque values, mutual and
nested inductives, projections, numeric/string literals and quotients. Negative fixtures cover
target/alias exclusion, changed target/universes, malformed candidate transport, absent or
changed primitive/axiom identities, unsafe/partial declarations and damaged families.
Changing the withheld proof while retaining the registered statement also passes independently.
Composition check 4 mutates registration's normalization version; it is a native development
control and is explicitly excluded from a candidate-only isolated matrix.
These finite controls do not rule out every semantically equivalent route or prove completeness.

## Raw evidence index

All external paths below are on `billy-laptop`; SHA256 values identify the exact retained files.
Sibling `process.json`, `stdout.txt` and `stderr.txt` preserve the development launch records.
No native process, build or test was rerun to write this document.

| Evidence | Exact external file | SHA256 |
|---|---|---|
| v4 source/outcome handoff | [NATIVE_HANDOFF.json](/home/billy/orion-director-work/20260907/proof-environment-development/environment-controls-v4/NATIVE_HANDOFF.json) | `39d6ad412bb78e59abb252a3045a564be42655f2789119a9b19ed5643fafec51` |
| v4 complete matrix | [DEVELOPMENT_CASES.json](/home/billy/orion-director-work/20260907/proof-environment-development/environment-controls-v4/DEVELOPMENT_CASES.json) | `f832f7a725d90ad095013af2e345ac375bcfba46b6a45bbcf598515b306447bd` |
| first identity refusal | [result.json](/home/billy/orion-director-work/20260907/proof-environment-development/composition-prepared-1/result.json) | `dc513dfc21be2875547fa4c05e15b4d9cbe468f334f752dd8cbcc9625f6e81b2` |
| second identity refusal | [result.json](/home/billy/orion-director-work/20260907/proof-environment-development/composition-prepared-2/result.json) | `3d9bcad74c57e013030c41b5a75956292526b33d96f5383a8c18e9c80b0ebd9b` |
| alpha comparison 1 | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/compare-real-1/stdout.txt) | `e0393867b46194aba53f22a6e4e729e148ea709f9a79bbf125aec00c380b6d89` |
| alpha comparison 2 | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/compare-real-2/stdout.txt) | `ee9aa50f1dd5c690f098d91ee9fa602f39d776bba4debd5f8e83c8a23f2cdf4d` |
| binder-name diff | [type-diff.txt](/home/billy/orion-director-work/20260907/proof-environment-development/compare-real-1/type-diff.txt) | `37d4855c61510dbea7f62fdb41885afb5384cc7f9378dd6f7a55adafeba20070` |
| binder-annotation type diff | [type-diff.txt](/home/billy/orion-director-work/20260907/proof-environment-development/compare-real-2/type-diff.txt) | `c3cff3ca8276ad212830527a3b82d1c16e2224d95862c17bfa1b455a2a65f6ad` |
| binder-annotation value diff | [value-diff.txt](/home/billy/orion-director-work/20260907/proof-environment-development/compare-real-2/value-diff.txt) | `7fcb4a11eb7e1f32f328eb4da43dd43e290089dbceca38b4d6b3a7a864a6a7fa` |
| annotation control refusal | [stderr.txt](/home/billy/orion-director-work/20260907/proof-environment-development/annotation-red-1/stderr.txt) | `0828d32c5bfdc7c1c54d48652e5db06f6dc5ff8be9c0a2f10bd8720b2d1289e2` |
| exporter panic | [stderr.txt](/home/billy/orion-director-work/20260907/proof-environment-development/rich-cases-v1-defined-prepare/stderr.txt) | `8d7e4c16a133f39360a5c90c5020c470b38cb172207f2991c11bbc07e327b4e1` |
| unusable earlier PREPARED | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/rich-cases-v1-defined-prepare/stdout.txt) | `e4edd58057bb4fe81a1b7c19cc5b0a43b2b317969dd2108a119e7d92d6ad9ee6` |
| header-only permitted packet | [permitted.ndjson](/home/billy/orion-director-work/20260907/proof-environment-development/rich-cases-v1/defined/prepared/permitted.ndjson) | `c2bccb21f1ddc32cc5b098cfc347b6d4be68e9d1daea0ccca5f07ea3e5bd7cbf` |
| cold refusal of earlier export | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/rich-cases-v1-defined-check/stdout.txt) | `6c405da9f1d8fcf3fe95b7c9e9e0da3ae73b05f6f6450dc5e3d8c7a2a51eea08` |
| resource false-start result | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/resource-diagnostic-run/stdout.txt) | `5bd9d7b79845af11671694c0015b3d5000491cf97c19891250b13ee8f141e198` |
| resource false-start assertion | [stderr.txt](/home/billy/orion-director-work/20260907/proof-environment-development/resource-diagnostic-run/stderr.txt) | `1105749680266d7d95ff132a4ed9b79bf64425ec2ff41fea8a0d179f8c0a87d7` |
| resource false-start process | [process.json](/home/billy/orion-director-work/20260907/proof-environment-development/resource-diagnostic-run/process.json) | `27eb6fb3b41da6e6d697c1201fb908b1f206caafbe326059dcbbf1197dd477f1` |
| actual resource timeout | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/resource-real-green/stdout.txt) | `a25e3d8dee828aa7bcbaad22f9e7595818f79ff2b70b9ba1cbf9533649aac077` |
| dependency controls | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/final-development-dependency_tests/stdout.txt) | `6081050c7494b89b3bd44cd79ce15c3ff07d5b11928a7e3fc03b99105723c47c` |
| kernel controls | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/final-development-kernel_tests/stdout.txt) | `a25e3d8dee828aa7bcbaad22f9e7595818f79ff2b70b9ba1cbf9533649aac077` |
| normalization controls | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/final-development-normalization_tests/stdout.txt) | `ec3dd24c45e063ef6e11dc875b50e1059bded579db960d6241a420c5601ae89f` |
| outcome controls | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/final-development-outcome_tests/stdout.txt) | `556a7c65a3fdbd701c40e45949f99bd793d4c4f0f18b8be52e67e04321a60ca2` |
| packet controls | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/final-development-packet_tests/stdout.txt) | `ba3ef1ead97fa116f82abfc94765f01aaea3a3680b7270ad61aecb223bd500ae` |
| registry controls | [stdout.txt](/home/billy/orion-director-work/20260907/proof-environment-development/final-development-registry_tests/stdout.txt) | `7d68e1958dd467abfab234b4d4f5d438beffed370c8be42f90499b5ad17e06fd` |
