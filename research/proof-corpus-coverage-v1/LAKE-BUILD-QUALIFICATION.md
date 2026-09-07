# Authored offline Lake build qualification

Read first: this establishes one small two-package build under the existing offline evaluator profile.
It does not build any of the four corpus assignments, reconstruct a proof, learn a method, or qualify
the actual acquired corpus/plugin closure. The registered production acquisition clock was not started.

## Result and records

`AUTHORED_LAKE_BUILD_PASS`: Lean/Lake4.33.1 built `Authored` and `Fixture` from an authored
root package and one exact Git-pinned dependency. The root source, manifest, toolchain file and
dependency source/Git metadata remained unchanged. Both package configuration caches and module
outputs were written to separate owned artifact mounts.

Raw root on billy-laptop:
`/home/billy/orion-director-work/20260907/lake-build-qualification-v1`.

- `01-red/`: eight missing-implementation tests failed.
- `02-green/`: the eight fixture/contract tests passed.
- `03-prepare/`: authored source, setup Git process records, source/runtime inventories, ELF metadata,
  exact file mounts, proposed profile, limits, review and initial source snapshots.
- `04-run/`: actual profile preparation refused before dispatch; no Lake process was started.
- `04-diagnosis.json`: exactly12 inventory schema differences, historical `kind=link` versus
  current material `type=symlink`; all18,129 runtime paths and file identities otherwise agreed.
- `05-profile/`: additive corrected inventory/profile; historical attempt retained unchanged.
- `06-run/`: complete successful profile/resource receipts and raw streams/samples.
- `06-assessment.json`: actual four required artifact identities and positive fixture outcome.
- `07-final-tests/`:14 portable controls passed, zero skips. Extra controls exercise nonzero/bool
  return codes, missing evidence and each incomplete-cleanup condition; native source is unchanged.
- `08-custody/`: current source/raw/output bindings, measured cost scopes and retained source copies.

## Faithful working layout

The exact invoked target was:

```text
/lean/bin/lake --dir /workspace --no-cache --keep-toolchain --rehash --verbose build +Fixture:olean
```

The source workspace and complete existing Lean distribution were read-only inventoried materials.
`.lake/packages/authored` held an actual detached Git HEAD matching the lock revision. The authored
Git URL was `https://example.invalid/authored`; no source fetch occurred. There were no dependency
overrides, source thinning, default `FinalCheck`, custom tactics, plugins, initializers or neural code
in the authored fixture. Trusted pinned compiler/runtime implementations remain explicit assumptions.

| Writable guest | Separate artifact directory |
|---|---|
| `/work` | scratch and empty HOME |
| `/workspace/.lake/config` | compiled configs at indices0 and1 |
| `/workspace/.lake/build` | root module artifacts |
| `/workspace/.lake/packages/authored/.lake/build` | dependency module artifacts |
| `/workspace/.lake/cache` | owned cache |

The whole `.lake` remained read-only. This protects its package sources, manifest-related state and
automatic `package-overrides.json` path. Source/lock/Git and the runtime inventories passed the
profile's pre/post custody checks. The fixture assessor separately compared the original source
inventory and required nonempty regular `.olean` and generated `.c` outputs for both modules.

Lake's verbose trace shows two Lean module compilations, each with `-o`, `-i`, `-c` and
`--setup`. Generated C is an actual output; this fixture did **not** require a native C compile,
link or generated-plugin load. The29 bound executable/library mounts include7 permitted executables:
Lake, Lean, leanir, clang, ld.lld, llvm-ar and Git. Permission is not evidence that each executed.

The new ELF metadata closure reuses the exact existing runtime and loader/library identities where
available, while binding additional Git/compiler dependencies explicitly. The runtime was inventoried,
not copied. Runtime manifest SHA256:
`93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894`.

## Enforcement and costs

The unchanged profile uses network namespace isolation plus AppArmor `deny network`, individual
executable/library permissions and non-executable writable artifacts. Lake's `--offline` is not a
build control; `--no-cache` plus actual profile denial is the applicable route here.
Existing separately qualified resource controls establish denied network/undeclared execution and
allowed-versus-denied plugin behavior; they were not rerun or represented as new Lake-specific probes.
A future package requiring a generated native plugin needs separately bound immutable admission.

The authored envelope was2GiB memory+swap,2CPU,64processes,90seconds and2GiB owned output.
This smaller fixture preflight was explicitly separated from the production24GiB headroom gate.

| Scope | Actual measurement |
|---|---:|
| Metadata/fixture preparation process |1.097901895s |
| First refused profile process |3.534163143s |
| Successful profile process |7.295236720s |
| Successful profile through cleanup, nested |7.259615958s |
| Controlled workload through cleanup, nested |0.713115788s |
| Aggregate controlled descendant CPU |0.618353705s |
| Aggregate cgroup memory high-water |205,385,728bytes |

Do not add nested times. The figures exclude interactive analysis, the correction/diagnostic command
wall time and unrelated development; they are not a complete lifetime cost or a speedup comparison.
The memory high-water is a cgroup measurement, not RSS; the receipt reports RSS unavailable.
The controlled process returned0, was reaped, had no remaining group/controller members, and its
controllers and AppArmor profile were removed. Raw stderr was empty.

## Reuse boundary

`create_fixture(new_root)` creates new authored sources/Git metadata and inventory;
`make_profile(data, exact_files, exact_materials, bwrap_record, aa_exec_record)` constructs the
mount/command plan. An externally reviewed, hash-bound code-audit record is still required.
The unchanged `resource_boot.py -I -S -B` source-loaded entry is the dispatcher.
`assess(data, receipt)` is a local fixture assertion, not an issuer-authentication or portable
receipt-verification API; the raw profile receipt remains the evidence authority.

For the real rows, retain their locked targets and deadline, bind every acquired dependency and
actual build configuration/import closure, and review reachable tactics/FFI/network helpers.
This authored success does not discharge those remaining source-specific obligations.
