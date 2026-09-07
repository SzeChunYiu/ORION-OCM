# Resource and offline-profile qualification

Current source authority: [exit-code successor](resource-exitcode-records/CORE.md),
qualified on 23 source files with 12/12 profile cases and 65/65 focused controls.
The original 19-source and [prior 22-source](RESOURCE-SUCCESSOR.md) qualifications
remain historical; neither receipt authorizes the changed current runner bytes.

**AUTHORED_RESOURCE_PROFILE_CONTROLS_PASSED: 12/12.**
The same frozen source also passed 42 focused controls on billy-laptop.
This is current-host infrastructure evidence, not a corpus build, proof study,
semantic closure, acquisition qualification, neural-absence proof or OCM novelty.

Retained evidence index: [INDEX](resource-records/INDEX.json) and
[complete seal](resource-records/SEAL.json). The two deterministic archives retain
380 files / 9,583,009 raw bytes in 172,893 compressed bytes; all 12 record files
total 252,560 bytes. Member maps were independently read back against every byte.
Nine host executable/library inputs are hash/size-bound but not copied; authored
fixture binaries/plugins are retained. This is not a standalone archived OS.

## Exact authority

Raw run:
`/home/billy/orion-director-work/20260907/proof-corpus-resource-qualification-20260907-v1/`.

- SOURCE_FREEZE.json SHA256:
  `3d202b0982b94882d0f8a53003e226b6ac6d0e020459f97f85fa2b8dd94157db`.
- 19 owned Python source/test files, 51,318 bytes. Each workload ran the frozen
  resource_boot.py as a trusted file entry under Python3.11.14 with -I -S.
- RESULT.json SHA256:
  `6988ddca77c2b04fd9f4adb7ca7e8671e6817af7d1dc3de55ca7f32bdb5e6e38`.
- REGISTRATION.json fixes all 12 cases before dispatch; cases/* retain host
  process records, policy, exact mounts/input audit, resource samples and raw
  stdout/stderr, assessments, post-custody checks and cleanup.
- The entire authored matrix took 3.687245 s wall inside its recorder.42 focused
  tests reported 1.64 s; outer process durations are retained separately. These
  timers overlap nested work and must not be added as independent lifecycle cost.
- Post-run documentation is outside the 19-file executable freeze. Generated
  cache files, if retained, are artifacts, never source authority.

## Observed controls

| Authored control | Observed outcome |
|---|---|
| Registered envelope/no-alarm | 20 GiB memory+swap,2 CPU equivalents,128 PIDs read back; command runs under enforce profile |
| Source immutability | write refused with EROFS |
| Network | socket refused with EACCES in offline namespace |
| Unknown executable | execution refused with EACCES |
| Unknown executable file mapping | mapping refused with EACCES |
| Native plugin positive | actual dlopen + function returned 17 |
| Native plugin negative | actual dlopen refused for unregistered mapping path |
| Aggregate CPU | two workers;6/6 CFS periods throttled,175,356,393 ns group CPU |
| Aggregate memory+swap | two 40 MiB allocations hit 64 MiB combined maximum; 165 memsw failures, one OOM kill |
| Aggregate PIDs | fork refused at group ceiling; pids.events max=1 |
| Detached descendant | separately sessioned child removed/reaped with namespace |
| Spool stop | 100,000-byte sampled threshold;4,102,980-byte observed overshoot |
| Wall deadline | RESOURCE_STOP/WALL_DEADLINE; partial output retained |
| Per-file write bound | stdout exactly65,536 bytes, bwrap return153; COMMAND_FAILED retained without claiming exact signal from exit code alone |
| Catchable host interruption | INTERRUPTED receipt, partial output, empty/reaped descendants |

All 12 registered case assessments passed; some cases establish multiple related
observations in the table. Every final controller membership was empty, every
child was reaped, every owned controller removed and every owned policy unloaded.
The no-alarm envelope began with 28,599,660,544 bytes MemAvailable and
300,427,972,608 bytes free, above its registered 24 GiB/224 GiB requirements.
The stress controls used deliberately smaller limits; the 20 GiB case is a
readback/no-alarm qualification with an authored 3 s timing envelope, not a
20 GiB exhaustion experiment or qualification of a full-length corpus run.

Disk enforcement is a sampled stop, not a hard quota. The spool control took
0.074584 s from detected stop through cleanup; scanner/polling/kill delay and final
receipt writes prevent a zero-overshoot claim. Group memory includes charged
memory/page cache and is not process RSS or aggregate host RSS. Supervisor,
setup and source-custody work stay outside workload cgroups.

## Failure and review history retained

External development root:
`/home/billy/orion-director-work/20260907/proof-corpus-coverage-resource-dev-20260907/`.

- failure-pidfd-missing: the first timeout could not signal through absent Python
  wrappers. Its incomplete-cleanup receipt remains; the eventually empty owned
  groups were removed. Qualified Linux x86_64 pidfd calls repaired the mechanism.
- profile-initial-v1: installed bwrap rejected --clearenv. The preserved successor
  uses an empty subprocess environment and explicit registered --setenv values.
- authored-matrix-v1: earlier seven-case engineering evidence is historical; its
  source capture is explicitly post-run, not the final frozen qualification.
- The final source also repairs output-mount/evidence overlap, unreadable scans,
  final-scan failure/handler restoration, policy retention during incomplete
  cleanup, host write aliases and stale matching-header Python caches.
- Authored fixture source/build/readelf records, source-only helper installation
  and protected predecessor helper bytes remain with development evidence.
- Independent review retained actual failure probes and 24 passing repair controls;
  its scope is trusted file entry/current host, not arbitrary host mutation.

See RESOURCE-PROFILE.md for the API/trust boundary and RESOURCE-INTEGRATION.md
for the remaining acquisition and actual evaluator-material gates.
