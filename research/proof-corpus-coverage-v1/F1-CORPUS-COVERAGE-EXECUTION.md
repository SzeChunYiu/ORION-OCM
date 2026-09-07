# F1 real-corpus coverage — prospective execution

2026-09-07; companion to [DESIGN](F1-CORPUS-COVERAGE-DESIGN.md).
This is a preparation specification, not an executable or a completed run.
All future acquisition, compilation and tests belong on billy-laptop. No source
checkout, dependency acquisition, build, export or row selection occurred here.

## Source and toolchain freeze

Use the existing verified bare corpus:
`/home/billy/orion-director-work/20260907/proof-corpus-source-aa2d8b3.git`.
Create an isolated evaluator checkout at commit
`aa2d8b34692b16c70f699536de0d8e75b9a3e9ef`; never alter that source or lockfile.
Reverify raw commit/tree/blob identities using `/usr/bin/git` and source receipts.
Resolve all nine exact lockfile revisions listed in [READINESS](F1-CORPUS-READINESS.md),
including Mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`.
Do not follow `inputRev=main/master`, update dependencies or substitute old caches.

The existing Lean 4.33.1 release is at
`/home/billy/orion-director-work/20260906/f0-development-runtime-v4/lean-4.33.1-linux/`.
Its adjacent runtime-manifest SHA256 is
`93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894`;
compiler commit is `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`.
Rebind the actual Lean/Lake binaries, release libraries and build dependencies.
This release cache contains Init/Lean/Lake/Std, not matching Mathlib artifacts.
The existing Lean 4.14.0 Mathlib checkout is incompatible and remains untouched.

After the authored 47-control successor is integrated, bind its exact exporter,
fresh-environment checker, source/build provenance and isolated runtime receipt.
Do not use a mutable development executable merely because its filename matches.
The evaluator exporter load path and declaration-association adapter need their
own source-bound qualification before the first real row.

## Prospective operating envelope

These are conservative commissioning constraints set before assignment, not
measured optima or evidence that all four rows can finish on this host.

| Item | Registered setting |
|---|---|
| Assigned rows | 4; no replacements or within-run retries |
| Aggregate memory / memory+swap | 20 GiB / 20 GiB for all descendant build jobs |
| Aggregate CPU / processes | 2 CPU equivalents / 128 PIDs |
| Initial MemAvailable | at least 24 GiB; otherwise no dispatch |
| Initial work-volume free space | at least 224 GiB |
| Disk monitor stop conditions | free space below 80 GiB or owned new bytes above 128 GiB |
| Disk monitor interval | 1 second; retain observations and overshoot |
| Per-file write bound | 8 GiB inherited RLIMIT_FSIZE |
| Full source packet maximum | 512 MiB per row; reject overflow without filtering |
| Sum of row packet inputs | at most 1 GiB |
| Whole dispatch deadline | 43,200 s (12 h), including acquisition and custody work |
| Acquisition deadline | 3,600 s total |
| Per-row build / export | 7,200 s / 900 s |
| Per-row prepare / final check | 900 s / 600 s |
| Termination / forced reap | TERM, 5 s grace, KILL, at most 10 s reap wait |

Per-stage deadlines are ceilings, subordinate to the whole deadline. Cleanup and
final evidence sealing continue after dispatch stops and their costs remain
visible. Output streams are spooled to owned files; no unbounded RAM capture.
Disk monitoring is an early-stop guard, **not a hard aggregate filesystem quota**.
Its headroom, polling/kill delay and maximum overshoot need a controlled fixture.
If that protection cannot be commissioned safely, refuse dispatch; do not assert
an enforced 128 GiB quota. A real project quota may be a separately bound successor.

The inspected host has 32,520,568 kB MemTotal and had 301,561,298,944 bytes free.
It uses hybrid cgroups: memory, CPU and PIDs are **v1** controllers, while cgroup2
is mounted separately at `/sys/fs/cgroup/unified`. The ordinary SSH user cannot
write the existing memory/CPU controller files. Prepare a scoped controller or
systemd service with verified hierarchy, memory+swap, CPU and PID enforcement;
retain read-back limits, descendant membership, failure counters and cleanup.
Do not pretend a per-process RLIMIT_AS bounds an entire Lake process tree.
Controller initialization failure records CANNOT_CHECK at RESOURCE_SETUP for
all four already assigned rows; no fallback unbounded build or silent reassignment.

## Two execution profiles

1. Acquisition profile: exact pinned source/tooling fetches only, into a new
   owned directory; record remote URLs, commits, archive bytes, failures and cost.
   Verify every resolved revision before handing files to an offline build.
2. Evaluator build/export profile: fresh namespace with no outbound network,
   credentials, agent sockets, user caches or undeclared host files. Mount exact
   source/dependencies read-only and only declared build/output directories writable.
   If Lake needs writable package-local artifact paths, provide separately owned
   artifact mounts; do not make pinned source mutable. Bind actual setup records,
   native plugins, shared libraries, scripts and executable closure.

Qualify network denial, unexpected executable/plugin refusal, source immutability,
resource exhaustion, killed-grandchild cleanup and evidence retention on harmless
authored controls first. Compilation can execute tactics or `run_cmd`; inspect
the loaded closure and prohibit neural computation/model calls, not just network.
An unclassified required dispatch is a distinct BUILD_POLICY CANNOT_CHECK.
No online teacher/retrieval exception, npm install, implicit cache download or
upstream wrapper's unsandboxed fallback is permitted during build/export.
The source-free native checking profile is separate and cannot stand in for this
new evaluator profile. No whole-host neural-absence claim follows from either.

## Minimal faithful build route

After assignment and controller/profile qualification, invoke one Lake process
at a time for each required wrapper module; do not invoke the default FinalCheck.
Prospective argv, with the exact binary and module substituted by the registrar:

```text
LEAN_NUM_THREADS=2 <pinned-lake> --no-cache --rehash build +Theorems.Thm_<key>:olean
```

Preserve the package's original Lean options and exact dependencies. Do not use
`--old`, `--update`, imports thinning, altered proofs or reduced checking options.
Record actual concurrent jobs: the environment variable is a scheduling request;
the independently enforced CPU/memory group is the aggregate resource boundary.
Verified completed artifacts may be reused across assigned rows, with their source,
toolchain/options/dependency identities and warm/cold distinction recorded.
A shared failed prerequisite can block later rows explicitly without rerunning it;
those rows remain assigned and identify the exact upstream failed artifact.

`+Module:olean` is **not C-free** in this Lean/Lake version. The source-grounded
route still fetches leanArts and checks `.olean`, `.ilean`, generated `.c` and,
where applicable, private/server/IR artifacts. Do not delete C while an active
build depends on it or imply a selective target necessarily avoids all Mathlib.
Of 29,511 existing solution import records, 19,389 directly import root Mathlib;
all import P2M.Util, whose inspected header imports Lean. This observation uses
retained import metadata only and does not choose or inspect solution proofs.

## Required records and stop semantics

Create one immutable run directory with the frozen complete population/order,
four assignments, policy, toolchain/dependency/build/runtime manifests and source
snapshots. Each row records declared stages before dispatch and stores actual
argv/environment/mounts, setup/import metadata, raw stdout/stderr, exit/signal,
PID/group cleanup, resource controller observations and output identities.
Bind exact independently registered target/universes and reference proof identity;
retain full source export only in evaluator records, never the checker mount set.

Record wall/CPU/peak RSS where measured, group peak memory separately, bytes
acquired/built/exported/stored, cold dependency cost, reused artifact validation,
parsing/preparation/replay/checking and cleanup. Do not add overlapping nested
timers as if disjoint. Keep cumulative episode cost and stage scopes explicit.
Report unknown upstream AI proof-acquisition cost; no end-to-end lifetime claim.

Timeout, memory/disk/PID/controller refusal, process interruption and incomplete
checking are CANNOT_CHECK at the reached stage. A definite kernel type rejection
is REJECTED. Unreached dependent stages are NOT_RUN with an explicit cause, not
zero-cost successes. Preserve failed partial artifacts and all assigned rows.
Future continuation starts from the frozen cursor under a new create-only record;
a revival binds its changed mechanism and retains prior failure/cost evidence.

## Read-only source observations supporting this plan

Inspected pinned metadata, existing import records and installed Lake source;
no withheld solution bodies, route files or FinalCheck source were opened.
In the Lean distribution's `src/lean/lake/`:

- `Lake/CLI/Help.lean:120–161`: module/facet syntax and leanArts outputs.
- `Lake/Build/Module.lean:1120–1137`: olean fetch depends on leanArts.
- `Lake/Build/Module.lean:812–821`: C and other required artifact checks.
- `Lake/Build/Module.lean:635–647`: setup includes transitive imports/plugins/options.
- `Lake/Build/Actions.lean:37–64`: compiler outputs/setup/environment;
  `84–99`: postponed IR-to-C path still emits C.

Corpus README:71–80 reports full-build 153 GB peak and 67 GB artifacts plus
220 GB C, not our reproduced measurements; 98–101 discloses AI-produced source.
Full campaign build is neither scheduled nor justified by this four-row design.
